"""
STEP 2: Giving the LLM tools (API integration / function calling)
=================================================================
What you learn:
  - The model cannot call APIs itself. It *asks* us to call a function.
  - We describe each tool with a name, a description and a JSON schema.
  - Our code runs the tool and sends the result back.
  - The model then writes the final answer using real data.

        You ──question──▶ Gemini
        Gemini ──"please call get_weather('Gulu')"──▶ Your code
        Your code ──calls Open-Meteo / Sunbird AI──▶ result
        Your code ──result──▶ Gemini ──final answer──▶ You

Run:  python step2_tool_calling.py
"""

from google.genai import types

from speak_uganda.config import MODEL, get_client
from speak_uganda.tools import ALL_TOOLS

client = get_client()

# --- 1. Describe the tools to the model --------------------------------------
# This JSON schema is the "contract". Keep an eye on it: MCP (Step 3) uses
# exactly the same idea.
LANG = "ISO 639-3 code: lug=Luganda, ach=Acholi, teo=Ateso, lgg=Lugbara, nyn=Runyankole, swa=Swahili, eng=English"

tool_declarations = [
    types.FunctionDeclaration(
        name="get_weather",
        description="Get the weather forecast for a town or city in Uganda.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "e.g. Gulu, Jinja, Mbarara"},
                "days": {"type": "integer", "description": "1 to 7 days, default 3"},
            },
            "required": ["city"],
        },
    ),
    types.FunctionDeclaration(
        name="translate_text",
        description="Translate English text into a Ugandan language using Sunbird AI.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "target_language": {"type": "string", "description": LANG},
            },
            "required": ["text", "target_language"],
        },
    ),
    types.FunctionDeclaration(
        name="speak_text",
        description="Speak text aloud in a Ugandan language (Sunbird AI text-to-speech). Saves an audio file.",
        parameters_json_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text already in the target language"},
                "language": {"type": "string", "description": LANG},
            },
            "required": ["text", "language"],
        },
    ),
]

config = types.GenerateContentConfig(
    tools=[types.Tool(function_declarations=tool_declarations)],
    system_instruction=(
        "You are Speak Uganda, a language buddy. Always use tools for weather, translations "
        "and speech; never guess them. To speak a phrase, translate it first, then speak the translation."
    ),
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
        "Will it rain in Gulu this weekend?",
        "How do I say 'Thank you very much' in Luganda? Let me hear it.",
    ]:
        print(f"\nYou: {q}")
        print(f"AI:  {ask(q)}")

    # Bonus: the SDK can run this loop for you. Pass plain Python functions;
    # it reads their type hints and docstrings to build the schema.
    print("\n--- Same thing, with automatic function calling ---")
    from speak_uganda.tools import get_weather

    auto = client.models.generate_content(
        model=MODEL,
        contents="Compare the weather in Jinja and Mbarara for tomorrow.",
        config=types.GenerateContentConfig(tools=[get_weather]),
    )
    print(auto.text)
