"""
STEP 3b: Connecting Gemini to our MCP server
============================================
What you learn:
  - An MCP *client* starts (or connects to) an MCP *server*.
  - It asks the server "what tools do you have?" (list_tools).
  - It passes those tools to the LLM, and when the LLM requests one,
    it forwards the call to the server (call_tool).
  - This client contains no tool code: swap the server and it gets new abilities.

        Gemini ◀──▶ MCP client (this file) ◀──MCP──▶ MCP server (step3_mcp_server.py)
                                                        └──▶ bible-api.com, Sunbird AI

Run:  python step3_mcp_client.py
"""

import asyncio
import os
import sys

from google.genai import types
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from fellowship_assistant.config import MODEL, get_client

# The client launches the server as a subprocess. By default MCP passes only a
# minimal environment, so we hand over ours (it contains SUNBIRD_API_KEY).
SERVER = StdioServerParameters(
    command=sys.executable,
    args=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "step3_mcp_server.py")],
    env=dict(os.environ),
)


def mcp_tools_to_gemini(mcp_tools) -> types.Tool:
    """MCP tools already carry a JSON schema, so converting them is one line each."""
    return types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name=t.name,
                description=t.description or "",
                parameters_json_schema=t.input_schema,
            )
            for t in mcp_tools
        ]
    )


async def call_mcp_tool(session: ClientSession, name: str, args: dict) -> str:
    result = await session.call_tool(name, args)
    return "\n".join(c.text for c in result.content if getattr(c, "text", None))


async def ask(session: ClientSession, gemini_tool: types.Tool, question: str) -> str:
    client = get_client()
    config = types.GenerateContentConfig(tools=[gemini_tool])
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]

    while True:
        response = await client.aio.models.generate_content(model=MODEL, contents=contents, config=config)
        if not response.function_calls:
            return response.text

        contents.append(response.candidates[0].content)
        parts = []
        for call in response.function_calls:
            print(f"   [mcp] {call.name}({dict(call.args)})")
            result = await call_mcp_tool(session, call.name, dict(call.args))
            parts.append(types.Part.from_function_response(name=call.name, response={"result": result}))
        contents.append(types.Content(role="user", parts=parts))


async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            listed = await session.list_tools()
            print("Tools discovered from the MCP server:")
            for t in listed.tools:
                print(f"  - {t.name}: {(t.description or '').splitlines()[0]}")

            gemini_tool = mcp_tools_to_gemini(listed.tools)
            question = "Give me a verse of the day and explain it in two sentences."
            print(f"\nYou: {question}")
            print(f"AI:  {await ask(session, gemini_tool, question)}")


if __name__ == "__main__":
    asyncio.run(main())
