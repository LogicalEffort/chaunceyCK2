from langchain.agents import create_agent
from langchain_ollama import ChatOllama
from chaunceyck2.agent_tools import *
from chaunceyck2.constants import MODEL, SYSTEM_PROMPT


def build_agent():
    llm = ChatOllama(
        model=MODEL,
        temperature=0,
        # Deep agents ship a long built-in system prompt; Ollama's default context
        # window is too small and silently truncates it. Raise it.
        num_ctx=16384,
    )
    return create_agent(
        model=llm,
        tools=[run_sql],
        system_prompt=SYSTEM_PROMPT,
    )
#ask an agent a question via console
def ask(agent, question: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": question}]})
    return result["messages"][-1].content
