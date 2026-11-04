"""
STEP 2: Giving the LLM tools (API integration / function calling)
=================================================================
What you learn:
  - The model cannot call APIs itself. It *asks* us to call a function.
  - We describe each tool with a name, a description and a JSON schema.
  - Our code runs the tool and sends the result back.
  - The model then writes the final answer using real data.

        You ──question──▶ Gemini
        Gemini ──"please call get_bible_verse('Psalm 23:1')"──▶ Your code
        Your code ──calls bible-api.com──▶ result
        Your code ──result──▶ Gemini ──final answer──▶ You

Run:  python step2_tool_calling.py
"""

from google.genai import types

from fellowship_assistant.config import MODEL, get_client
from fellowship_assistant.tools import ALL_TOOLS

client = get_client()

# --- 1. Describe the tools to the model --------------------------------------
# This JSON schema is the "contract". Keep an eye on it: MCP (Step 3) uses
# exactly the same idea.
tool_declarations = [
    types.FunctionDeclaration(
        name="get_bible_verse",
        description="Look up a Bible passage by reference, e.g. 'John 3:16' or 'Psalm 23'.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "reference": {"type": "string", "description": "Bible reference"},
                "translation": {
                    "type": "string",
                    "enum": ["web", "kjv"],
                    "description": "web (default) or kjv",
                },
            },
            "required": ["reference"],
        },
    ),
    types.FunctionDeclaration(
        name="translate_text",
        description="Translate text into a Ugandan/African language using Sunbird AI.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "target_language": {
                    "type": "string",
                    "description": "ISO 639-3 code, e.g. lug=Luganda, ach=Acholi, nyn=Runyankole",
                },
            },
            "required": ["text", "target_language"],
        },
    ),
]

config = types.GenerateContentConfig(
    tools=[types.Tool(function_declarations=tool_declarations)],
    system_instruction="You help a student fellowship. Always use tools for Bible text and translations; never guess them.",
)


# --- 2. The tool-calling loop -------------------------------------------------
def ask(question: str) -> str:
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]

    while True:
        response = client.models.generate_content(model=MODEL, contents=contents, config=config)

        if not response.function_calls:  # no tool requested -> final answer
            return response.text

        # Keep the model's turn (it contains the tool request) in the history
        contents.append(response.candidates[0].content)

        # Run every tool the model asked for and send the results back
        result_parts = []
        for call in response.function_calls:
            print(f"   [tool] {call.name}({dict(call.args)})")
            result = ALL_TOOLS[call.name](**call.args)
            print(f"   [tool] -> {result[:100]}")
            result_parts.append(
                types.Part.from_function_response(name=call.name, response={"result": result})
            )
        contents.append(types.Content(role="user", parts=result_parts))


if __name__ == "__main__":
    for q in [
        "What does Psalm 23:1 say? Explain it in one sentence.",
        "Translate 'God is love' into Luganda.",
    ]:
        print(f"\nYou: {q}")
        print(f"AI:  {ask(q)}")

    # Bonus: the SDK can run this loop for you. Pass plain Python functions;
    # it reads their type hints and docstrings to build the schema.
    print("\n--- Same thing, with automatic function calling ---")
    from fellowship_assistant.tools import get_bible_verse, translate_text

    auto = client.models.generate_content(
        model=MODEL,
        contents="Quote Romans 8:28 in KJV.",
        config=types.GenerateContentConfig(tools=[get_bible_verse, translate_text]),
    )
    print(auto.text)
