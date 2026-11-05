# 🎤 Facilitator guide

**Session:** Godly Geeks Movement · Sat 7 Nov 2026 · 9:00–11:00 AM EAT · Online
**Project:** Speak Uganda, an AI language buddy that talks
**Presenting from:** `notebooks/workshop.ipynb` in Google Colab, plus the slide deck

## Run-of-show (120 min)

| Time | Min | Segment | Notebook section | Notes |
|---|---|---|---|---|
| 9:00 | 10 | Welcome, prayer, Acts 2 hook | Title cell | Pentecost: "each one heard their own language". God cares about every language, and so can our tech |
| 9:10 | 10 | **Show the finished agent first** | Jump to Step 4, run it, **play the audio** | "By 11 AM you'll understand every line of this." |
| 9:20 | 5 | Setup: everyone gets a Gemini key | Setup cells | Share the Colab link in chat *before* this slide |
| 9:25 | 15 | **Step 1: LLM basics** | Step 1 | End on the "limitation" cell: no weather, guessed Acholi, no voice |
| 9:40 | 20 | **Step 2: Tool calling** | Step 2 | Play "Webale nnyo". Pause on `print(r.function_calls)`: the model *asks*, it doesn't *do* |
| 10:00 | 5 | ☕ Break / Q&A | | |
| 10:05 | 20 | **Step 3: MCP** | Step 3 | Point out the client has zero tool code. "USB-C for AI tools." Optional: Claude Desktop speaking Luganda |
| 10:25 | 15 | **Step 4: Agents** | Step 4 | Read the THINK/ACT/OBSERVE trace aloud, play every phrase, take a goal from the audience |
| 10:40 | 10 | Careers, Sunbird AI, Ugandan-language AI, how to keep learning | Wrap-up | |
| 10:50 | 10 | Q&A, challenges, closing prayer | Wrap-up | Share the GitHub link |

## Pre-session checklist

**Two days before**
- [ ] The "Open in Colab" badge in the README opens the notebook
- [ ] Run the whole notebook top to bottom in Colab with **your** keys
- [ ] **Listen to every audio clip.** Check which languages have a voice (`lug`, `ach`, `teo`, `lgg`, `nyn`…) and adjust demo goals if one doesn't
- [ ] Ask an Acholi speaker to sanity-check the demo phrases if you can
- [ ] Check the Gemini model name still works (`gemini-2.5-flash`) and the free-tier limits: https://ai.google.dev/gemini-api/docs/rate-limits
- [ ] Screen-record the full agent run **with sound** (backup if the API or the network fails)
- [ ] Send the organisers the Colab link + "create a Gemini key beforehand" instructions to share

**Morning of**
- [ ] Fresh Colab runtime, run setup + one `speak_text` call to **warm up the voice model**
- [ ] **Share your computer audio** in the meeting (Zoom: *Share sound*; Meet: share a Chrome tab with audio)
- [ ] **Second Gemini API key** ready (different Google account) in case you hit a quota
- [ ] Browser zoom ~125%, notifications off, close other tabs
- [ ] Phone hotspot ready as backup internet

## If things go wrong

| Problem | Do this |
|---|---|
| `429` rate limit mid-demo | Client retries automatically. If it persists, switch to the backup key (`os.environ["GEMINI_API_KEY"]=...` then re-create `client`) |
| Audience can't hear audio | Re-share with sound enabled; or download the clip and play it from your phone near the mic |
| Speech is slow (cold start) | Talk through what's happening: a 3-billion-parameter voice model is waking up |
| A language has no voice | Great teaching moment: the agent sees the error and adapts. Switch the goal to Luganda |
| Model gives an odd answer | LLMs are non-deterministic; this is why we use tools and guardrails |
| Network dies | Play the screen recording of that step |

## Analogies that land

- **LLM** = a very well-read intern who has never left the library
- **Tools** = giving the intern a phone, and now a *voice*
- **MCP** = a standard phone socket, so any intern in any office can use the same phone lines
- **Agent** = giving the intern a *goal* ("get me ready for Gulu") instead of step-by-step instructions
