from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
import os
import base64
from langchain_cohere import CohereEmbeddings
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from google.genai import types
from google import genai

load_dotenv()

client = genai.Client(api_key="AIzaSyDcLwBQ25gk-YesXRfLYRIGhNTc1vkWtvM")


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def process_file(id: str, file_path: str):
    await files_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": {"status": "processing"}}
    )

    await files_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": {"status": "converting to images"}}
    )

    # Step 1: Convert the PDF to image
    pages = convert_from_path(file_path)
    images = []

    for i, page in enumerate(pages):
        image_save_path = "/mnt/uploads/images/{id}/image-{i}.jpg"
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        page.save(image_save_path, "JPEG")
        images.append(image_save_path)

    await files_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": {"status": "converting to images success"}}
    )

    extracted_texts = []

    embedder = CohereEmbeddings(model="embed-english-v3.0")

    vector_store = QdrantVectorStore.from_documents(
        documents=[],
        url="http://qdrant:6333",
        collection_name="PDF_CONTEXT",
        embedding=embedder
    )

    for i, image_path in enumerate(images):
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg",
                ),
                "Write Complete Detail of this Image",
            ],
        )

        print(f"Page {i + 1}:", response.text)

        await files_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"status": "processed", "result": response.text}},
        )

        text = response.text.strip()
        extracted_texts.append(text)

        # Create LangChain Document with metadata
        doc = Document(
            page_content=text,
            metadata={"file_id": str(id), "page_number": i}
        )

        vector_store.add_documents(documents=[doc])
        
        # rq worker --with-scheduler --url redis://valkey:6379
