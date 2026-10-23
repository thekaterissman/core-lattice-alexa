# Talk to Core Lattice through Alexa+ (Simulated Experience)

**Amazon Developer Hackathon 2026 — "Build, Ship, Shape" · Alexa+ track**

A web app that simulates an Alexa+ conversation with **Core Lattice** — a
proprietary conversational AI architecture built by independent developer
**Kate Rissman**. You talk (type or speak) to the engine; it routes your intent,
remembers your session, plans, explains itself, and answers honestly when it
can't verify something instead of inventing an answer.

## Why a simulation?

The official hackathon rules expressly allow a **simulated Alexa+ experience**
in a web app, exempt from the Alexa runtime-technology-hook requirement. This
project takes that alternate path. The full simulation source is in this
repository — the conversational engine, the server, and the interface — so
judges can run exactly what the demo video shows. No mockups: the app works.

## Run it

Zero dependencies — Python 3 standard library only.

```bash
python3 app.py              # serves http://127.0.0.1:8080
python3 app.py --port 9000  # custom port
```

Open the URL in a browser. Tap the mic or type. (Voice in/out uses the
browser's Web Speech API — Chrome gives the best result; typing always works.)

Endpoints:

- `GET  /api/health` → `{"status": "ok", ...}`
- `POST /api/chat` with `{"utterance": "...", "session_id": "..."}` → reply with intent, text, and suggestion chips

## What the demo does

- **Conversation with memory** — greets you, learns your name ("my name is…"),
  recalls it later in the session ("what's my name?")
- **Guided demo** — say "run the demo" for a 3-part walkthrough of the engine
- **Planning** — say "plan my hackathon week" and the engine builds a structured
  step plan from your goal
- **Self-knowledge** — ask "who built you", "what is Core Lattice?", or
  "what can you do?" and it explains the architecture and its own limits
- **Honest uncertainty** — off-script questions get a plain answer about what
  the scaffold can and can't do, never a fabricated fact

## How it's built

| File | What it is |
|---|---|
| `app.py` | Stdlib-only HTTP server. Serves `./static`, exposes `/api/chat` |
| `core_lattice.py` | The Core Lattice scaffold engine: intent router, session memory, demo flows |
| `static/index.html` | Alexa-style interface: status ring, chat, suggestion chips |
| `static/app.js` | Chat client; Web Speech API voice in/out |
| `static/styles.css` | Dark Alexa-blue theme, responsive |

## AI tools used in building this project

- **Muse (Meta)** — AI pair-programming assistant used to help write, debug,
  and smoke-test the engine, server, and interface code, and to draft this
  documentation.
- **Core Lattice (the author's own architecture)** — the conversational engine
  at the center of the demo is Kate Rissman's proprietary system; this repo
  contains a scaffold of it built for the hackathon.
- **Web Speech API (browser-native)** — speech recognition and synthesis for
  the voice layer; not an external AI service.

## The story

An independent developer built her own AI architecture — now you can talk to
it through Alexa. One builder, no team, no funding: the engine was designed for
her own real work (including litigating her own civil case as a pro se
plaintiff), and this simulation layer was built around it in October 2026 for
this hackathon.

## License

MIT — see `LICENSE`.
