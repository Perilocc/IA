from datetime import datetime
from hashlib import sha1
from io import BytesIO
from pathlib import Path

from docx import Document
from fastapi import HTTPException, UploadFile
from pypdf import PdfReader

from RAG.core.chroma import collection
from RAG.core.logging_config import logger
from RAG.services.ollama_service import check_ollama_health, get_embeddings
from RAG.utils.chunker import chunk_text


def _safe_filename(filename: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in Path(filename).stem).strip("_") or "documento"


def _decode_text(content: bytes) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="ignore")


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages).strip()


def _extract_docx_text(content: bytes) -> str:
    document = Document(BytesIO(content))
    paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs).strip()


def _extract_text_from_file(content: bytes, filename: str) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf_text(content)
    if suffix == ".docx":
        return _extract_docx_text(content)
    if suffix == ".txt":
        return _decode_text(content)

    raise HTTPException(status_code=415, detail=f"Formato não suportado: {suffix or 'arquivo sem extensão'}")


async def index_uploaded_documents(files: list[UploadFile]):
    if not files:
        raise HTTPException(status_code=400, detail="Envie ao menos um arquivo")

    if not await check_ollama_health():
        raise HTTPException(status_code=503, detail="Ollama indisponível")

    chunks = []
    ids = []
    metadatas = []
    processed_files = 0

    for upload in files:
        content = await upload.read()

        if not content:
            logger.warning("Arquivo vazio ignorado: %s", upload.filename)
            continue

        text = _extract_text_from_file(content, upload.filename or "documento")

        if not text.strip():
            logger.warning("Sem texto extraível em %s", upload.filename)
            continue

        file_hash = sha1(content).hexdigest()[:16]
        filename = upload.filename or "documento"
        file_slug = _safe_filename(filename)
        doc_chunks = chunk_text(text)

        for index, chunk in enumerate(doc_chunks):
            chunks.append(chunk)
            ids.append(f"doc_{file_hash}_{index}")
            metadatas.append({
                "module": "documents",
                "record_id": f"{file_slug}_{index}",
                "filename": filename,
                "file_type": Path(filename).suffix.lower().lstrip("."),
                "file_hash": file_hash,
            })

        processed_files += 1

    if not chunks:
        raise HTTPException(status_code=400, detail="Nenhum texto pôde ser extraído dos arquivos enviados")

    existing = collection.get(ids=ids)
    if existing.get("ids"):
        collection.delete(ids=existing["ids"])

    embeddings = await get_embeddings(chunks)

    collection.upsert(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas,
    )

    logger.info("Indexados %s chunks de %s arquivo(s)", len(chunks), processed_files)

    return {
        "status": "success",
        "indexed": len(chunks),
        "files": processed_files,
        "message": "Documentos indexados com sucesso",
        "last_sync": datetime.now().isoformat(),
    }