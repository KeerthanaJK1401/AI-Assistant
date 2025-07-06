import os
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_to_txt, sanitize_filename

# Load API key from .env
load_dotenv()

# Define the output schema
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

# Set up the LLM (OpenRouter with Mistral)
llm = ChatOpenAI(
    model="mistralai/mistral-7b-instruct",
    temperature=0,
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
)

# Define output parser
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

# Prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an intelligent AI research assistant. Your job is to perform in-depth research and produce detailed, well-written paragraph summaries (at least 200–300 words) in clear English.

Use search and Wikipedia tools as needed. Then return the result as structured JSON matching this format:
{format_instructions}

The summary should read like a small informative article — avoid bullets and be as descriptive as possible.
""",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

# Tools
tools = [search_tool, wiki_tool]

# Create the agent
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)

# Agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# Run the agent
def run_research(query: str) -> str:
    try:
        response = agent_executor.invoke({"query": query})
        raw_output = response["output"].strip("`").strip()
        structured = parser.parse(raw_output)

        filename = f"{structured.topic.lower().replace(' ', '_')}.txt"
        save_to_txt(structured, filename)
        return filename
    except Exception as e:
        print("❌ Error:", e)
        return ""

if __name__ == "__main__":
    query = input("🔍 Hello! What topic would you like me to research today?\n> ")
    run_research(query)
