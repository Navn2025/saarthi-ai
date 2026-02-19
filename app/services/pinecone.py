from pinecone import Pinecone,ServerlessSpec

from app.core.config import PINECONE_API_KEY
from app.services.embedding import get_embedding

pc=Pinecone(api_key=PINECONE_API_KEY)

index_name="prashikshan-question"

if not pc.has_index(index_name):
     pc.create_index(
        name=index_name,
        dimension=1024,   # must match embedding model
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
     
index=pc.Index(index_name)

def upsert_embeddings(text: str, record_id: str,student_id:str=None):
    try:
        vector = get_embedding(text)

        index.upsert(
            vectors=[ 
                {
                    "id": record_id,
                    "values": vector,
                    "metadata": {
                        "text": text,
                        "student_id": student_id
                    }
                }
            ]
        )
        return True
    except Exception as e:
        print(f"Error upserting embeddings: {str(e)}")
        return False
  


def query_embeddings(query_text, top_k=5, student_id=None):
    try:
        vector = get_embedding(query_text)

        results = index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True,
            filter={
                "student_id": student_id
            }
        )
        return results
    except Exception as e:
        print(f"Error querying embeddings: {str(e)}")
        return None