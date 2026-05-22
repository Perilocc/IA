import json

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