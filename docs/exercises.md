# 🏋️ Take-home challenges

Pick one, build it, and share a screenshot or GitHub link with the fellowship.

## 🟢 Beginner

1. **Change the personality.** Edit the system instruction in Step 1 so the assistant answers like a youth pastor, a lecturer or a poet. Compare answers at `temperature=0` and `temperature=1.5`.
2. **Hymn of the day.** Add a tool `get_hymn_of_the_day()` that returns a random hymn from a Python list. Register it in Step 2 *and* in the MCP server.

## 🟡 Intermediate

3. **Weather-aware announcements.** Add a tool that gets Kampala's weather from [Open-Meteo](https://open-meteo.com) (free, no key) so the agent can say "carry an umbrella to fellowship".
4. **Plug your server into a real app.** Connect `step3_mcp_server.py` to Claude Desktop, VS Code or the MCP Inspector (see the README) and use the tools from there.
5. **More languages.** Ask the agent for a devotional summary in Acholi (`ach`), Ateso (`teo`), Lugbara (`lgg`) and Runyankole (`nyn`). Ask a speaker of each language to rate the result.

## 🔴 Advanced

6. **Weekly announcement agent.** Build an agent that takes the week's events (as text) and drafts the fellowship WhatsApp announcement in English and Luganda, then saves it.
7. **Human in the loop.** Change `step4_agent.py` so it asks you to type `y` before it calls `save_devotional`. Why is this an important guardrail for agents that *act* (send emails, make payments)?
8. **Remote MCP server.** Run the server with `mcp.run(transport="streamable-http")` and connect to it over HTTP instead of stdio. Where could you deploy it?

## 💭 Reflection

- Where could an agent like this cause harm (wrong scripture, wrong translation, false confidence)? How did we reduce that risk?
- What tasks in your church, fellowship or community could AI help with *responsibly*?
