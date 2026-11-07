# 🇺🇬 Speak Uganda: build an AI language buddy that talks

**LLM Development · API Integration · MCP Servers · Agentic AI**

Workshop materials from the **Godly Geeks Movement** session of the **CoCIS Christian Fellowship, Makerere University**, on **7 November 2026**, facilitated by **Yiga Gilbert** (Software Engineer, Sunbird AI).

<a href="https://colab.research.google.com/github/yigagilbert/Future_of_ai_session/blob/main/notebooks/workshop.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

We build **one project in four steps**. By the end, an AI agent checks the weather in Gulu, teaches you Acholi phrases for a friend's wedding and **says them out loud** in a Ugandan voice.

| Step | Theme | What we build | File |
|---|---|---|---|
| 1 | **LLM development** | Call Gemini through its API: prompts, system instructions, temperature, tokens, chat | [`step1_llm_basics.py`](step1_llm_basics.py) |
| 2 | **API integration** | Give the model tools: weather, Sunbird AI translation and text-to-speech | [`step2_tool_calling.py`](step2_tool_calling.py) |
| 3 | **MCP servers** | Package the tools as an MCP server so *any* AI app can use them | [`step3_mcp_server.py`](step3_mcp_server.py), [`step3_mcp_client.py`](step3_mcp_client.py) |
| 4 | **Agentic AI** | Give it a goal ("I'm going to Gulu…") and let it plan and act | [`step4_agent.py`](step4_agent.py) |

```
                    ┌───────────────────────── Step 4: agent loop ─────────────────────────┐
                    │                                                                       │
 You ──goal──▶  Gemini (Step 1)  ◀──tool calls (Step 2)──▶  MCP client  ◀──MCP (Step 3)──▶  speak-uganda server
                                                                                              ├─▶ get_weather     → Open-Meteo (free)
                                                                                              ├─▶ translate_text  → Sunbird AI
                                                                                              ├─▶ speak_text      → Sunbird AI text-to-speech 🔊
                                                                                              └─▶ save_phrasebook → output/*.md
```

---

## 🔑 Keys you need

| Key | Needed for | Get it |
|---|---|---|
| `GEMINI_API_KEY` | Everything (the LLM) | Free: https://aistudio.google.com/apikey |
| `SUNBIRD_API_KEY` | Translation and speech in Ugandan languages | https://api.sunbird.ai (sign up, then create a key) |

Without a Sunbird key, everything still runs: weather works, and the translation and speech tools return a clear "key not set" message, which the agent works around.

## 🚀 Option A: Run in Google Colab (easiest, nothing to install)

1. Click the **Open in Colab** badge above.
2. Open the 🔑 **Secrets** panel in the left sidebar, add `GEMINI_API_KEY` (and `SUNBIRD_API_KEY`), and enable notebook access.
3. Run the cells from top to bottom. Audio players appear under the cells that speak.

## 💻 Option B: Run on your own computer

Requires **Python 3.10+**.

```bash
git clone https://github.com/yigagilbert/Future_of_ai_session.git
cd Future_of_ai_session

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # Windows: copy .env.example .env
# then open .env and paste your keys
```

Run each step from the project folder:

```bash
python step1_llm_basics.py
python step2_tool_calling.py
python step3_mcp_client.py         # starts step3_mcp_server.py for you
python step4_agent.py
python step4_agent.py "I'm going to Mbarara for exams. Teach me 3 Runyankole phrases to encourage my friends."
```

Audio files are saved in `output/audio/` and phrasebooks in `output/`.

---

## 🔌 Use the MCP server in other AI apps

This is the point of MCP: the server you built in Step 3 works with any MCP-compatible app. Plug it into Claude Desktop and Claude can check Ugandan weather, translate and **speak Luganda**. Use **absolute paths** in the configs below.

**Claude Desktop**: *Settings → Developer → Edit Config* (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "speak-uganda": {
      "command": "/full/path/to/Future_of_ai_session/.venv/bin/python",
      "args": ["/full/path/to/Future_of_ai_session/step3_mcp_server.py"],
      "env": {
        "SUNBIRD_API_KEY": "your-key-here",
        "OUTPUT_DIR": "/full/path/to/Future_of_ai_session/output"
      }
    }
  }
}
```

**VS Code (GitHub Copilot agent mode)**: create `.vscode/mcp.json`:

```json
{
  "servers": {
    "speak-uganda": {
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
├── notebooks/workshop.ipynb      # the live-session notebook (Colab-ready)
├── speak_uganda/
│   ├── tools.py                  # plain Python tools: weather, Sunbird translate + speech, save file
│   └── config.py                 # loads .env, creates the Gemini client (with retries)
├── step1_llm_basics.py
├── step2_tool_calling.py
├── step3_mcp_server.py
├── step3_mcp_client.py
├── step4_agent.py
└── docs/exercises.md             # take-home challenges
```

## 🧠 Key ideas in one table

| Concept | One-liner |
|---|---|
| **LLM** | Text in → text out, through an API. No memory, no live data. |
| **Tool calling** | The model *asks* for a function; *your code* runs it and returns the result. |
| **MCP** | An open standard so any AI app can discover and use your tools ("USB-C for AI tools"). |
| **Agent** | A loop of think → act → observe until a goal is met, with guardrails (step limits, human review). |

## 💭 Tokens and "thinking"

LLMs read and write in **tokens**, pieces of words. Tokens are what you pay for, and what free-tier rate limits count.

In Step 1 you print the token count of one answer. In one run of the workshop it came out like this:

```
prompt: 51 | thinking: 437 | answer: 118 | total: 606
```

Why isn't the total 51 + 118 = 169? Because `gemini-2.5-flash` is a **thinking model**: before it answers, it reasons privately in tokens you never see. Those **thinking tokens** are reported separately as `thoughts_token_count`, and they are **billed as output tokens**. Here they were about three-quarters of the total.

| Field (`response.usage_metadata`) | What it counts |
|---|---|
| `prompt_token_count` | Your question plus the system instruction |
| `thoughts_token_count` | Hidden reasoning before the answer |
| `candidates_token_count` | The answer you see |
| `total_token_count` | All of the above |

Thinking makes answers better on hard problems (planning, code, multi-step agents), but it costs tokens and time. For simple questions you can switch it off. On 2.5 Flash, a budget of 0 disables it:

```python
config = types.GenerateContentConfig(
    thinking_config=types.ThinkingConfig(thinking_budget=0),   # no thinking
)
```

The amount of thinking varies from run to run, so your numbers will differ. The notebook's Step 1 has both cells, so you can compare the totals yourself.

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `429 RESOURCE_EXHAUSTED` | You hit Gemini's free-tier rate limit. The client retries automatically; otherwise wait a minute. Limits: https://ai.google.dev/gemini-api/docs/rate-limits |
| `404 model not found` | Google renamed or retired the model. Set `GEMINI_MODEL` in `.env` (or `MODEL` in the notebook) to a current one from https://ai.google.dev/gemini-api/docs/models |
| `SUNBIRD_API_KEY is not set` | Add the key to `.env` / Colab secrets. |
| Speech is slow the first time | The voice model warms up on first use. Later calls are faster. |
| A language has no voice | `speak_text` returns Sunbird's error and the agent skips the audio. Translation still works. |
| Weather fails | Free weather services rate-limit shared machines like Colab. The tool tries Open-Meteo, then MET Norway, then wttr.in, and if all fail it returns each service's error. |
| Translation or speech fails or is slow | The first Sunbird call can take a minute while the model wakes up; the tools retry 3 times. Run the notebook's health-check cell to see the real error.  means the key is wrong. |
| `ModuleNotFoundError: mcp.server.fastmcp` in other tutorials | Those tutorials use MCP SDK v1. This repo uses v2, where `FastMCP` became `MCPServer`. |

## 📚 Learn more

- Gemini API docs: https://ai.google.dev/gemini-api/docs
- Function calling: https://ai.google.dev/gemini-api/docs/function-calling
- Model Context Protocol: https://modelcontextprotocol.io
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Sunbird AI API (Ugandan languages): https://api.sunbird.ai/docs
- Open-Meteo weather API: https://open-meteo.com

## 🙏 Credits

Built for the **Godly Geeks Movement**, CoCIS Christian Fellowship, Makerere University.
Translation and speech: Sunbird AI. Weather: Open-Meteo, MET Norway and wttr.in.

> *"Each one heard their own language being spoken."* (Acts 2:6)

License: [MIT](LICENSE)
