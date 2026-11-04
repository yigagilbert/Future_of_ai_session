# 🎤 Facilitator guide

**Session:** Godly Geeks Movement · Sat 7 Nov 2026 · 9:00–11:00 AM EAT · Online
**Presenting from:** `notebooks/workshop.ipynb` in Google Colab

## Run-of-show (120 min)

| Time | Min | Segment | Notebook section | Notes |
|---|---|---|---|---|
| 9:00 | 10 | Welcome, prayer, devotional hook | Title cell | Exodus 31:3 → skill is a gift; tech as stewardship |
| 9:10 | 10 | **Show the finished agent first** | Jump to Step 4, run it | "By 11 AM you'll understand every line of this." |
| 9:20 | 5 | Setup: everyone gets a Gemini key | Setup cells | Share the Colab link in chat *before* this slide |
| 9:25 | 15 | **Step 1: LLM basics** | Step 1 | End on the "limitation" cell: it guesses Luganda |
| 9:40 | 20 | **Step 2: Tool calling** | Step 2 | Pause on `print(r.function_calls)`: the model *asks*, it doesn't *do* |
| 10:00 | 5 | ☕ Break / Q&A | | |
| 10:05 | 20 | **Step 3: MCP** | Step 3 | Point out the client has zero tool code. "USB-C for AI tools." Optional: show the same server in Claude Desktop or the Inspector |
| 10:25 | 15 | **Step 4: Agents** | Step 4 | Read the THINK/ACT/OBSERVE trace aloud. Discuss guardrails (MAX_STEPS, human review) |
| 10:40 | 10 | Careers, Sunbird AI, Ugandan-language AI, how to keep learning | Wrap-up | |
| 10:50 | 10 | Q&A, challenges, closing prayer | Wrap-up | Share the GitHub link |

## Pre-session checklist

**Two days before**
- [ ] Repo is public on GitHub; the "Open in Colab" badge opens the notebook
- [ ] Run the whole notebook top to bottom in Colab with **your** keys
- [ ] Check the Gemini model name still works (`gemini-2.5-flash`) and the free-tier limits: https://ai.google.dev/gemini-api/docs/rate-limits
- [ ] Sunbird API key works (`translate_text("God is love", "lug")`)
- [ ] Screen-record each step working (backup if the API or the network fails)
- [ ] Send the organisers the Colab link + "create a Gemini key beforehand" instructions to share

**Morning of**
- [ ] Fresh Colab runtime, run the setup cells, keep the tab open
- [ ] **Second Gemini API key** ready (different Google account) in case you hit a quota
- [ ] Browser zoom ~125%, notifications off, close other tabs
- [ ] Phone hotspot ready as backup internet
- [ ] Test screen sharing on the meeting platform

## If things go wrong

| Problem | Do this |
|---|---|
| `429` rate limit mid-demo | Client retries automatically. If it persists, switch to the backup key (`os.environ["GEMINI_API_KEY"]=...` then re-create `client`) |
| Model gives an odd answer | Great teaching moment: LLMs are non-deterministic; this is why we use tools and guardrails |
| Sunbird API slow (cold start) | Talk through what's happening; the timeout is 120 s. Or skip translation; every other tool still works |
| Network dies | Play the screen recording of that step |
| Students stuck on keys | Tell them to follow along by watching; the repo has everything for later |

## Analogies that land

- **LLM** = a very well-read intern who has never been outside the library
- **Tools** = giving the intern a phone to call people who know things
- **MCP** = a standard phone socket, so any intern in any office can use the same phone lines
- **Agent** = giving the intern a *goal* ("organise Friday's fellowship") instead of step-by-step instructions
