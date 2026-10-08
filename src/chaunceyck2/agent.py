from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from chaunceyck2.agent_tools import *
from chaunceyck2.constants import MODEL, SYSTEM_PROMPT


def build_agent():
    llm = ChatOllama(
        model=MODEL,
        temperature=0,
        num_ctx=16384,
    )
    return create_agent(
        model=llm,
        tools=[search_wiki],
        system_prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver()
    )
#ask an agent a question via console
def ask(agent, question: str, thread_id: str = "console") -> str:
    config = {"configurable": {"thread_id": thread_id}}
    result = agent.invoke({"messages": [{"role": "user", "content": question}]}, config)
    return result["messages"][-1].content

