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
      python step4_agent.py "I'm going to Mbarara for exams. Teach me 3 Runyankole phrases to encourage my friends."
"""

import asyncio
import sys

from google.genai import types
from mcp import ClientSession
from mcp.client.stdio import stdio_client

from speak_uganda.config import MODEL, get_client
from step3_mcp_client import SERVER, call_mcp_tool, mcp_tools_to_gemini

MAX_STEPS = 15  # guardrail: never loop forever (and protect your free-tier quota)

AGENT_INSTRUCTIONS = """
You are Speak Uganda, an agent that prepares short, practical language lessons
for university students travelling around Uganda.

How you work:
1. Start by writing a short numbered PLAN of the steps you will take.
2. Check the weather for the destination and let it shape your tips
   (e.g. rain means a phrase about umbrellas or shelter).
3. Choose useful phrases for the situation. Use translate_text for EVERY phrase.
   Never write a Ugandan-language translation from memory.
4. Use speak_text on each translated phrase, in the same language, so the
   student can hear it. If a tool returns an error, adapt (skip the audio,
   or say so) instead of giving up.
5. End the phrasebook with a short blessing for the journey, also translated.
6. Save everything with save_phrasebook (phrases, translations, audio file
   paths, weather tip), then reply with a short summary that starts with "DONE:".

Be warm and encouraging. Keep the phrasebook short.
"""

DEFAULT_GOAL = (
    "I'm a Makerere student travelling to Gulu this weekend for a friend's wedding. "
    "Check the weather, teach me 4 useful Acholi phrases for the trip and the wedding, "
    "let me hear each one, and save a phrasebook."
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
    print("\nAudio files are in output/audio/ and the phrasebook in output/.")
