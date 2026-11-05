# 🏋️ Take-home challenges

Pick one, build it, and share a screenshot, an audio clip or a GitHub link with the fellowship.

## 🟢 Beginner

1. **Change the personality.** Edit the system instruction in Step 1 so the buddy talks like a radio DJ, a strict teacher or a proud grandmother. Compare answers at `temperature=0` and `temperature=1.5`.
2. **Proverb of the day.** Add a tool `get_proverb()` that returns a random English proverb from a Python list. Register it in Step 2 *and* in the MCP server, then ask the agent to translate it and speak it.

## 🟡 Intermediate

3. **Speech-to-text: check my pronunciation.** Sunbird also does speech-to-text (`POST /tasks/audio/transcriptions`, see https://api.sunbird.ai/docs). Add a `transcribe_audio(path)` tool, record yourself saying a phrase, and let the agent tell you how close you were.
4. **Plug your server into a real app.** Connect `step3_mcp_server.py` to Claude Desktop, VS Code or the MCP Inspector (see the README) and get Claude to speak Luganda.
5. **Language tour.** Ask the agent for the same phrase in Luganda (`lug`), Acholi (`ach`), Ateso (`teo`), Lugbara (`lgg`) and Runyankole (`nyn`). Ask a speaker of each language to rate the translation *and* the voice.

## 🔴 Advanced

6. **Language of the week.** Build an agent for the fellowship WhatsApp group: every Monday it picks a language, one useful phrase and one Bible verse, translates both, and produces an audio clip.
7. **Human in the loop.** Change `step4_agent.py` so it shows you each translation and asks you to type `y` before it generates speech or saves anything. Why is this an important guardrail for agents that *act*?
8. **Remote MCP server.** Run the server with `mcp.run(transport="streamable-http")` and connect to it over HTTP instead of stdio. Where could you deploy it so your whole class can use it?

## 💭 Reflection

- A fluent-sounding translation can still be wrong. How did we reduce that risk, and what else could we do?
- Most AI works best in English. Why does building for Ugandan languages matter, and who benefits?
- What could a talking language buddy do for your church, family or community?
