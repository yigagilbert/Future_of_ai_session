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

from speak_uganda.config import MODEL, get_client

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
        "You are 'Speak Uganda', a cheerful language buddy for university students "
        "at Makerere. You love Uganda's languages and cultures. Keep answers under 100 words."
    ),
    temperature=0.7,  # 0 = predictable, ~1+ = more creative
)
response = client.models.generate_content(
    model=MODEL,
    contents="How many languages are spoken in Uganda, and which are the biggest?",
    config=config,
)
print("2) With a system instruction:\n", response.text, "\n")

# --- 3. Tokens: what you pay for ---------------------------------------------
usage = response.usage_metadata
# gemini-2.5-flash "thinks" before answering; those hidden tokens are billed as output too
print(
    f"3) Tokens used: prompt={usage.prompt_token_count}, thinking={usage.thoughts_token_count or 0}, "
    f"answer={usage.candidates_token_count}, total={usage.total_token_count}\n"
)

# --- 4. Multi-turn chat: the SDK re-sends the history for us ------------------
chat = client.chats.create(model=MODEL, config=config)
print("4) Chat:")
for question in [
    "I'm visiting Gulu next week. Which language is spoken there?",
    "Teach me how to greet someone in it.",  # only makes sense with the history
]:
    reply = chat.send_message(question)
    print(f"   You: {question}\n   AI:  {reply.text}\n")

# --- 5. The limitation that motivates Step 2 ---------------------------------
response = client.models.generate_content(
    model=MODEL,
    contents="What's the weather in Gulu tomorrow? And say 'Congratulations on your wedding' in Acholi, out loud please.",
)
print("5) Asking for things it cannot know or do:\n", response.text)
print(
    "\n   -> It has no live weather, may guess the Acholi, and cannot speak.\n"
    "      In Step 2 we give it tools."
)
