from fastapi import FastAPI, UploadFile, Path
from .utils.file import save_to_disk
from .db.collections.files import files_collection, FileSchema
from .queue.q import q
from .queue.workers import process_file
from bson import ObjectId
from pydantic import BaseModel
from .rag.chat_context import prepare_context
from .rag.graph import create_chat_graph

app = FastAPI()


class ChatInput(BaseModel):
    file_id: str
    query: str

@app.get("/")
def hello():
    return {"status": "healthy!"}


@app.get("/{id}")
async def get_file_by_id(id: str = Path(..., description="ID of the file")):
    db_file = await files_collection.find_one({"_id": ObjectId(id)})

    return {
        "_id": str(db_file["_id"]),
        "name": db_file["name"],
        "status": db_file["status"],
        "result": db_file["result"] if "result" in db_file else None,
    }


@app.post("/upload")
async def upload_file(file: UploadFile):

    db_file = await files_collection.insert_one(
        document=FileSchema(name=file.filename, status="saving")
    )

    file_path = f"/mnt/uploads/{str(db_file.inserted_id)}/{file.filename}"
    await save_to_disk(file=await file.read(), path=file_path)

    # Push to Queue
    q.enqueue(process_file, str(db_file.inserted_id), file_path)

    # MongoDB Save
    await files_collection.update_one(
        {"_id": db_file.inserted_id}, {"$set": {"status": "queued"}}
    )
    return {"file_id": str(db_file.inserted_id)}


@app.post("/chat")
async def chat_with_file(input: ChatInput):
    # 1. Prepare initial state
    print("📥 /chat endpoint called")
    state = prepare_context(file_id=input.file_id, user_query=input.query)

    # 2. Create and run LangGraph
    app_graph = create_chat_graph(checkpointer=None)
    final_state = app_graph.invoke(state)

    return {"response": final_state["messages"][-1].content}
