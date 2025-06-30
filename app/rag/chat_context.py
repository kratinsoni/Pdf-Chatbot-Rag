# utils/chat_context.py
from langchain_core.messages import HumanMessage
from .vectorstore import get_relevant_chunks


def prepare_context(file_id: str, user_query: str):
    context_chunks = get_relevant_chunks(file_id, user_query)
    context_text = "\n\n".join([doc.page_content for doc in context_chunks])
    
    print(f"Retrieved {len(context_chunks)} chunks for query: '{user_query}'")
    
    return {
        "messages": [HumanMessage(content=user_query)],
        "context": context_text
    }
