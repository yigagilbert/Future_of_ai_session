# ✝️ Godly Geeks: Build an AI Fellowship Assistant

**LLM Development · API Integration · MCP Servers · Agentic AI**

Workshop materials from the **CoCIS Christian Fellowship, Makerere University** session on **7 November 2026**, facilitated by **Yiga Gilbert** (Software Engineer, Sunbird AI).

<a href="https://colab.research.google.com/github/yigagilbert/Future_of_ai_session/blob/main/notebooks/workshop.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

We build **one project in four steps**. Each step adds one idea from the theme:

| Step | Theme | What we build | File |
|---|---|---|---|
| 1 | **LLM development** | Call Gemini through its API: prompts, system instructions, temperature, tokens, chat | [`step1_llm_basics.py`](step1_llm_basics.py) |
| 2 | **API integration** | Give the model tools: a Bible API and Sunbird AI translation (function calling) | [`step2_tool_calling.py`](step2_tool_calling.py) |
| 3 | **MCP servers** | Package the tools as an MCP server so *any* AI app can use them | [`step3_mcp_server.py`](step3_mcp_server.py), [`step3_mcp_client.py`](step3_mcp_client.py) |
| 4 | **Agentic AI** | Give it a goal ("prepare Friday's devotional") and let it plan and act | [`step4_agent.py`](step4_agent.py) |

```
                       ┌──────────────────────────── Step 4: agent loop ─────────────────────────┐
                       │                                                                          │
   You ──goal──▶  Gemini (Step 1)  ◀──tool calls (Step 2)──▶  MCP client  ◀──MCP (Step 3)──▶  MCP server
                                                                                                  ├─▶ bible-api.com
                                                                                                  ├─▶ Sunbird AI (Luganda, Acholi, …)
                                                                                                  └─▶ save_devotional → output/*.md
```

---

## 🚀 Option A: Run in Google Colab (easiest, nothing to install)

1. Click the **Open in Colab** badge above.
2. Get a free Gemini API key at **https://aistudio.google.com/apikey**.
3. In Colab, open the 🔑 **Secrets** panel (left sidebar), add `GEMINI_API_KEY`, and enable notebook access.
4. *(Optional)* Add `SUNBIRD_API_KEY` for translation into Ugandan languages: **https://api.sunbird.ai**
5. Run the cells from top to bottom.

## 💻 Option B: Run on your own computer

Requires **Python 3.10+**.

```bash
git clone https://github.com/yigagilbert/Future_of_ai_session.git
cd Future_of_ai_session

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # Windows: copy .env.example .env
# then open .env and paste your GEMINI_API_KEY (and optionally SUNBIRD_API_KEY)
```

Run each step from the project folder:

```bash
python step1_llm_basics.py
python step2_tool_calling.py
python step3_mcp_client.py         # starts step3_mcp_server.py for you
python step4_agent.py
python step4_agent.py "Prepare a short devotional on patience, with a Luganda summary"
```

Devotionals the agent saves appear in `output/`.

---

## 🔌 Use the MCP server in other AI apps

This is the point of MCP: the server you built in Step 3 works with any MCP-compatible app. Use **absolute paths** in the configs below.

**Claude Desktop**: *Settings → Developer → Edit Config* (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "fellowship-assistant": {
      "command": "/full/path/to/Future_of_ai_session/.venv/bin/python",
      "args": ["/full/path/to/Future_of_ai_session/step3_mcp_server.py"],
      "env": { "SUNBIRD_API_KEY": "your-key-here" }
    }
  }
}
```

**VS Code (GitHub Copilot agent mode)**: create `.vscode/mcp.json`:

```json
{
  "servers": {
    "fellowship-assistant": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["${workspaceFolder}/step3_mcp_server.py"]
    }
  }
}
```

**MCP Inspector** (a browser UI for testing servers, needs Node.js):

```bash
npx @modelcontextprotocol/inspector python step3_mcp_server.py
```

---

## 📁 Project structure

```
Future_of_ai_session/
├── notebooks/workshop.ipynb      # the live-session notebook (self-contained, Colab-ready)
├── fellowship_assistant/
│   ├── tools.py                  # plain Python tools: Bible API, Sunbird translate, save file
│   └── config.py                 # loads .env, creates the Gemini client (with retries)
├── step1_llm_basics.py
├── step2_tool_calling.py
├── step3_mcp_server.py
├── step3_mcp_client.py
├── step4_agent.py
├── docs/exercises.md             # take-home challenges
└── docs/facilitator-guide.md     # run-of-show and backup plan for presenters
```

## 🧠 Key ideas in one table

| Concept | One-liner |
|---|---|
| **LLM** | Text in → text out, through an API. No memory, no live data. |
| **Tool calling** | The model *asks* for a function; *your code* runs it and returns the result. |
| **MCP** | An open standard so any AI app can discover and use your tools ("USB-C for AI tools"). |
| **Agent** | A loop of think → act → observe until a goal is met, with guardrails (step limits, human review). |

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `429 RESOURCE_EXHAUSTED` | You hit the free-tier rate limit. The client retries automatically; otherwise wait a minute. Limits are listed at https://ai.google.dev/gemini-api/docs/rate-limits |
| `404 model not found` | Google renamed or retired the model. Set `GEMINI_MODEL` in `.env` (or `MODEL` in the notebook) to a current one from https://ai.google.dev/gemini-api/docs/models |
| Translation says `SUNBIRD_API_KEY is not set` | Add the key to `.env` / Colab secrets. Everything else works without it. |
| `ModuleNotFoundError: mcp.server.fastmcp` in other tutorials | Those tutorials use MCP SDK v1. This repo uses v2, where `FastMCP` became `MCPServer`. |

## 📚 Learn more

- Gemini API docs: https://ai.google.dev/gemini-api/docs
- Function calling: https://ai.google.dev/gemini-api/docs/function-calling
- Model Context Protocol: https://modelcontextprotocol.io
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Sunbird AI API (Ugandan languages): https://api.sunbird.ai/docs
- Bible API used here: https://bible-api.com

## 🙏 Credits

Built for the **Godly Geeks Movement**, CoCIS Christian Fellowship, Makerere University.
Bible text: World English Bible (public domain) and KJV via bible-api.com. Translation: Sunbird AI.

> *"Whatever you do, work at it with all your heart, as working for the Lord."* (Colossians 3:23)

License: [MIT](LICENSE)
