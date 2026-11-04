"""
STEP 4: From chatbot to agent
=============================
What you learn:
  - A chatbot answers a question. An agent pursues a GOAL.
  - The agent loop:  think -> act (call a tool) -> observe (read result) -> repeat
    until the goal is done. The model decides which tools to use, in what order.
  - Guardrails matter: a step limit, clear instructions, and a human who checks the result.

This is the same loop as Step 3. What changes is the job we give it: an open-ended
goal that needs several tools in sequence, plus a system prompt that makes the
model plan, check its work and finish deliberately.

Run:  python step4_agent.py
      python step4_agent.py "Prepare a short devotional on patience, with a Luganda summary"
"""

import asyncio
import sys

from google.genai import types
from mcp import ClientSession
from mcp.client.stdio import stdio_client

from fellowship_assistant.config import MODEL, get_client
from step3_mcp_client import SERVER, call_mcp_tool, mcp_tools_to_gemini

MAX_STEPS = 10  # guardrail: never loop forever (and protect your free-tier quota)

AGENT_INSTRUCTIONS = """
You are the Fellowship Assistant, an agent that prepares material for a
Christian student fellowship at Makerere University.

How you work:
1. Start by writing a short numbered PLAN of the steps you will take.
2. Use tools for every Bible quote and every translation. Never invent scripture
   or translations from memory.
3. After each tool result, check it. If a tool returns an error, adapt
   (e.g. try another reference) instead of giving up.
4. When the goal is achieved, save the result with save_devotional, then reply
   with a short summary that starts with "DONE:".

Write for university students: warm, practical, about 250 words.
"""

DEFAULT_GOAL = (
    "Prepare this Friday's fellowship devotional on the theme 'faith over fear'. "
    "Use two Bible passages, write a short reflection and one discussion question, "
    "include a one-sentence Luganda translation of the key message, and save it."
)


async def run_agent(goal: str) -> str:
    client = get_client()

    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = mcp_tools_to_gemini((await session.list_tools()).tools)

            config = types.GenerateContentConfig(
                system_instruction=AGENT_INSTRUCTIONS,
                tools=[tools],
            )
            contents = [types.Content(role="user", parts=[types.Part(text=goal)])]

            for step in range(1, MAX_STEPS + 1):
                response = await client.aio.models.generate_content(
                    model=MODEL, contents=contents, config=config
                )
                contents.append(response.candidates[0].content)

                # THINK: show any reasoning/plan text the model wrote this turn
                thought = "".join(p.text or "" for p in response.candidates[0].content.parts)
                if thought.strip():
                    print(f"\n[step {step}] THINK:\n{thought.strip()}")

                # Finished? (no more tool requests)
                if not response.function_calls:
                    return thought

                # ACT + OBSERVE
                parts = []
                for call in response.function_calls:
                    args = dict(call.args)
                    preview = {k: (v[:60] + "...") if isinstance(v, str) and len(v) > 60 else v for k, v in args.items()}
                    print(f"[step {step}] ACT:     {call.name}({preview})")
                    result = await call_mcp_tool(session, call.name, args)
                    print(f"[step {step}] OBSERVE: {result[:120]}")
                    parts.append(types.Part.from_function_response(name=call.name, response={"result": result}))
                contents.append(types.Content(role="user", parts=parts))

            return f"Stopped after {MAX_STEPS} steps without finishing (guardrail hit)."


if __name__ == "__main__":
    goal = " ".join(sys.argv[1:]) or DEFAULT_GOAL
    print(f"GOAL: {goal}")
    final = asyncio.run(run_agent(goal))
    print("\n" + "=" * 60 + "\nFINAL ANSWER:\n" + final)
