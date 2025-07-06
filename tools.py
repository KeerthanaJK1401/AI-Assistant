import re
from datetime import datetime
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool

# Sanitize filename
def sanitize_filename(title: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_]', '', title.lower().replace(" ", "_"))

# Save to text file (plain text format)
def save_to_txt(data, filename=None):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if not filename:
        filename = sanitize_filename(data.topic) + ".txt"

    formatted_text = (
        f"Title: {data.topic}\n\n"
        f"{data.summary}\n\n"
        f"Sources: {', '.join(data.sources)}\n"
        f"Tools Used: {', '.join(data.tools_used)}\n"
        f"Saved On: {timestamp}\n"
        f"{'-'*80}\n"
    )

    with open(filename, "w", encoding="utf-8") as f:
        f.write(formatted_text)

    print(f"✅ Research saved to file: {filename}")
    return f"Saved to {filename}"

# Tool for saving (optional if you want to expose it as a tool)
save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file.",
)

# Search tool using DuckDuckGo
search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information",
)

# Wikipedia tool with character limits
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=2000)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)
