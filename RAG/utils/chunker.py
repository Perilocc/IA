import json


def chunk_text(text, chunk_size=1200, overlap=150):
    text = (text or "").strip()

    if not text:
        return []

    if chunk_size <= 0:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = max(end - overlap, start + 1)

    return chunks


def chunk_documents(data):

    chunks=[]
    ids=[]
    metadatas=[]

    for module,records in data.items():
        for rec in records:
            text=json.dumps(
                rec,
                ensure_ascii=False
            )

            chunks.append(text)

            ids.append(
                f"{module}_{rec['id']}"
            )

            metadatas.append({
                "module":module,
                "record_id":str(
                    rec["id"]
                )
            })

    return chunks,ids,metadatas