import os
from dotenv import load_dotenv
import weaviate

load_dotenv()

# Connect to Weaviate using the older API that's compatible
client = weaviate.Client(
    url="http://localhost:8080",
    additional_headers={
        "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
    }
)

def create_schema():
    class_name = "CompanyData"
    if not client.schema.exists(class_name):
        class_obj = {
            "class": class_name,
            "properties": [
                {"name": "content", "dataType": ["text"]},
                {"name": "source", "dataType": ["text"]},
                {"name": "filename", "dataType": ["text"]}
            ],
            "vectorizer": "text2vec-openai"
        }
        client.schema.create_class(class_obj)

def insert_document_chunks(chunks, filename):
    for chunk in chunks:
        client.data_object.create(
            data_object={
                "content": chunk,
                "source": "upload",
                "filename": filename
            },
            class_name="CompanyData"
        )

def semantic_search(query, top_k=5):
    result = client.query.get("CompanyData", ["content", "filename"]).with_near_text({
        "concepts": [query]
    }).with_limit(top_k).do()
    
    return [{"content": obj["content"], "filename": obj["filename"]} for obj in result["data"]["Get"]["CompanyData"]]
