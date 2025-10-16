from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from langchain_huggingface import HuggingFaceEmbeddings

model_name = "BAAI/bge-large-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

client = QdrantClient(host="localhost", port=6333)

# Create a collection
def create_collection():
    if "documents" not in [c.name for c in client.get_collections().collections]:
        client.create_collection(
            collection_name="documents",
            vectors_config=VectorParams(size=1024, distance=Distance.DOT)
        )

# Upload documents to collection
def ingest_docs(docs, collection_name="documents"):
    points = [
        {
            "id": i,
            "vector": embeddings.embed_query(doc.page_content),
            "payload": doc.metadata
        }
        for i, doc in enumerate(docs)
    ]
    client.upsert(collection_name=collection_name, points=points)

# Search Qdrant collection
def vector_search(query, collection_name="documents", limit=5):
    query_vector = embeddings.embed_query(query)
    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=limit
    )
    return results