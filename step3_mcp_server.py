"""
STEP 3a: Turning our tools into an MCP server
=============================================
What you learn:
  - In Step 2 the tools were locked inside one script, wired to one model.
  - MCP (Model Context Protocol) is an open standard for exposing tools
    (and data) to *any* AI app: Claude Desktop, VS Code, Cursor, Gemini CLI,
    or your own client.
  - Think of it as "USB-C for AI tools": build the tool once, plug it in anywhere.

Each @mcp.tool() below wraps a function from fellowship_assistant/tools.py.
The SDK reads the type hints + docstring and generates the JSON schema,
the same kind of schema we wrote by hand in Step 2.

Run (normally an MCP client starts this for you):
    python step3_mcp_server.py

Inspect it in a browser with the official MCP Inspector (needs Node.js):
    npx @modelcontextprotocol/inspector python step3_mcp_server.py
"""

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

from fellowship_assistant import tools

load_dotenv()  # so SUNBIRD_API_KEY works however the server is launched

mcp = MCPServer(
    name="fellowship-assistant",
    instructions="Tools for a Christian student fellowship: Bible lookup, Sunbird AI translation, saving devotionals.",
)


@mcp.tool()
def get_bible_verse(reference: str, translation: str = "web") -> str:
    """Look up a Bible passage by reference, e.g. "John 3:16" or "Psalm 23". translation: "web" or "kjv"."""
    return tools.get_bible_verse(reference, translation)


@mcp.tool()
def get_random_verse() -> str:
    """Get one random Bible verse. Useful as a 'verse of the day'."""
    return tools.get_random_verse()


@mcp.tool()
def translate_text(text: str, target_language: str, source_language: str = "eng") -> str:
    """Translate text using Sunbird AI. Languages are ISO 639-3 codes, e.g.
    lug=Luganda, ach=Acholi, teo=Ateso, lgg=Lugbara, nyn=Runyankole, swa=Swahili, eng=English."""
    return tools.translate_text(text, target_language, source_language)


@mcp.tool()
def save_devotional(title: str, content: str) -> str:
    """Save a finished devotional (Markdown) to a file for sharing with the fellowship."""
    return tools.save_devotional(title, content)


if __name__ == "__main__":
    mcp.run()  # speaks MCP over stdin/stdout
