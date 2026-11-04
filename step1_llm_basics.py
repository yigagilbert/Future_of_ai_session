"""
STEP 1: Talking to an LLM through an API
========================================
What you learn:
  - An LLM is a function: text in -> text out.
  - System instructions shape *how* it answers.
  - Temperature controls creativity vs. consistency.
  - Tokens are what you are billed (or rate-limited) on.
  - The model has no memory: "chat" means re-sending the history.

Run:  python step1_llm_basics.py
"""

from google.genai import types

from fellowship_assistant.config import MODEL, get_client

client = get_client()

# --- 1. The simplest possible call -------------------------------------------
response = client.models.generate_content(
    model=MODEL,
    contents="In two sentences, what is a large language model?",
)
print("1) Simple call:\n", response.text, "\n")

# --- 2. A system instruction gives the model a role ---------------------------
config = types.GenerateContentConfig(
    system_instruction=(
        "You are a friendly assistant for a Christian student fellowship at "
        "Makerere University. Explain things simply, like a senior student "
        "talking to a first-year. Keep answers under 100 words."
    ),
    temperature=0.7,  # 0 = predictable, ~1+ = more creative
)
response = client.models.generate_content(
    model=MODEL,
    contents="Explain the meaning of John 3:16.",
    config=config,
)
print("2) With a system instruction:\n", response.text, "\n")

# --- 3. Tokens: what you pay for ---------------------------------------------
usage = response.usage_metadata
print(
    f"3) Tokens used: prompt={usage.prompt_token_count}, "
    f"answer={usage.candidates_token_count}, total={usage.total_token_count}\n"
)

# --- 4. Multi-turn chat: the SDK re-sends the history for us ------------------
chat = client.chats.create(model=MODEL, config=config)
print("4) Chat:")
for question in [
    "Give me one verse about courage.",
    "Why did you choose that one?",  # only makes sense with the history
]:
    reply = chat.send_message(question)
    print(f"   You: {question}\n   AI:  {reply.text}\n")

# --- 5. The limitation that motivates Step 2 ---------------------------------
response = client.models.generate_content(
    model=MODEL,
    contents="Translate 'God is love' into Luganda, and tell me today's verse of the day.",
)
print("5) Asking for things it cannot know or do reliably:\n", response.text)
print(
    "\n   -> The model may guess. It has no live data and no specialised tools.\n"
    "      In Step 2 we give it tools."
)
