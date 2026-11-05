"""
STEP 3a: Turning our tools into an MCP server
=============================================
What you learn:
  - In Step 2 the tools were locked inside one script, wired to one model.
  - MCP (Model Context Protocol) is an open standard for exposing tools
    (and data) to *any* AI app: Claude Desktop, VS Code, Cursor, Gemini CLI,
    or your own client.
  - Think of it as "USB-C for AI tools": build the tool once, plug it in anywhere.
    Plug this server into Claude Desktop and Claude can suddenly speak Luganda.

Each @mcp.tool() below wraps a function from speak_uganda/tools.py.
The SDK reads the type hints + docstring and generates the JSON schema,
the same kind of schema we wrote by hand in Step 2.

Run (normally an MCP client starts this for you):
    python step3_mcp_server.py

Inspect it in a browser with the official MCP Inspector (needs Node.js):
    npx @modelcontextprotocol/inspector python step3_mcp_server.py
"""

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

from speak_uganda import tools

load_dotenv()  # so SUNBIRD_API_KEY works however the server is launched

mcp = MCPServer(
    name="speak-uganda",
    instructions="Tools for learning Ugandan languages: weather, Sunbird AI translation and text-to-speech, saving phrasebooks.",
)

LANGS = "ISO 639-3 codes: lug=Luganda, ach=Acholi, teo=Ateso, lgg=Lugbara, nyn=Runyankole, swa=Swahili, eng=English."


@mcp.tool()
def get_weather(city: str, days: int = 3) -> str:
    """Get the weather forecast for a town or city in Uganda (1-7 days)."""
    return tools.get_weather(city, days)


@mcp.tool(description=f"Translate text with Sunbird AI. {LANGS}")
def translate_text(text: str, target_language: str, source_language: str = "eng") -> str:
    return tools.translate_text(text, target_language, source_language)


@mcp.tool(description=f"Speak text aloud with Sunbird AI text-to-speech and save the audio file. "
                      f"The text must already be in that language. {LANGS}")
def speak_text(text: str, language: str = "lug") -> str:
    return tools.speak_text(text, language)


@mcp.tool()
def save_phrasebook(title: str, content: str) -> str:
    """Save a finished phrasebook or lesson (Markdown) to a file."""
    return tools.save_phrasebook(title, content)


if __name__ == "__main__":
    mcp.run()  # speaks MCP over stdin/stdout
