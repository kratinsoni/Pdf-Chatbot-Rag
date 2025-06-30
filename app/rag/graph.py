# graph.py
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage
import os
from dotenv import load_dotenv

load_dotenv()

# Define LangGraph state schema with context


class State(TypedDict):
    messages: Annotated[list, add_messages]
    context: str  # Injected context from vector store

# Initialize LLM
llm = init_chat_model(model_provider="openai", model="gpt-4.1-mini")

# Chatbot node that uses context + user message


def chatbot(state: State):
    # Inject context as a system message
    context_message = SystemMessage(content=f"Relevant context:\n{state['context']}")
    message_history = [context_message] + state["messages"]

    response = llm.invoke(message_history)

    if len(response.tool_calls) > 1:
        raise ValueError("Too many tool calls. Expected at most one.")

    return {"messages": [response]}

# Build Graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# Expose graph


def create_chat_graph(checkpointer=None):
    return graph_builder.compile(checkpointer=checkpointer)
