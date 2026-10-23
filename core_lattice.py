"""
Core Lattice — mock inference engine (scaffold).

This is a stub of Kate Rissman's proprietary Core Lattice architecture.
For the hackathon demo it behaves like a real conversational AI:
intent routing, session memory, and scripted demo flows.

Day 4-5 of the build plan wires this to real logic; the interface
contract (process(utterance, session) -> dict) stays stable.
"""

import re
from datetime import datetime


DEMO_FLOWS = {
    "tour": {
        "title": "Guided tour of Core Lattice",
        "steps": [
            "Welcome to Core Lattice. I'm running as a simulated Alexa+ skill. "
            "Ask me what I am, what I can do, or say 'run the demo' for a full walkthrough.",
        ],
    },
    "full_demo": {
        "title": "Full capability demo",
        "steps": [
            "Demo 1 of 3 — Structured reasoning. Ask me to plan something, like "
            "'plan my hackathon week', and watch me break it into steps with owners and deadlines.",
            "Demo 2 of 3 — Memory. Tell me your name or a preference, then ask me about it later. "
            "I keep session memory like a real assistant.",
            "Demo 3 of 3 — Honest uncertainty. Ask me something I can't verify and I'll tell you "
            "plainly instead of inventing an answer. That's a Core Lattice design principle.",
        ],
    },
}


class CoreLattice:
    """Rule-based scaffold of the Core Lattice conversational engine."""

    def __init__(self):
        self.sessions = {}

    # ------------------------------------------------------------------ API
    def process(self, utterance: str, session_id: str = "default") -> dict:
        """Main entry point. Returns a response dict for the web client."""
        text = (utterance or "").strip()
        session = self.sessions.setdefault(session_id, {"memory": {}, "turns": 0})
        session["turns"] += 1

        if not text:
            return self._reply("I didn't catch that. Try asking me something.", session, intent="empty")

        intent, slots = self._route(text, session)
        handler = getattr(self, f"_handle_{intent}", self._handle_fallback)
        return handler(text, slots, session)

    # -------------------------------------------------------------- routing
    def _route(self, text, session):
        t = text.lower()

        if re.search(r"\b(hi|hello|hey|good (morning|afternoon|evening)|yo)\b", t) and len(t) < 30:
            return "greeting", {}
        if re.search(r"run the (full )?demo|start demo|demo", t):
            return "demo", {}
        if re.search(r"tour|show me around|walk ?through", t):
            return "tour", {}
        if re.search(r"what are you|who are you|your name|about yourself|introduce|"
                     r"who (built|created|made|developed|designed) (you|this)|"
                     r"your (creator|maker|developer|builder|author)|"
                     r"who is kate|kate rissman|who('s| is) behind (you|this)", t):
            return "identity", {}
        if re.search(r"what can you do|capabilit|abilities|features|skills", t):
            return "capabilities", {}
        if re.search(r"core lattice", t):
            return "explain_lattice", {}
        if re.search(r"\bplan\b", t):
            return "plan", {"goal": text}
        if re.search(r"summariz", t):
            return "summarize", {"text": text}
        if re.search(r"\b(remind|remember)\b", t):
            return "remember", {"text": text}
        if re.search(r"my name is|call me", t):
            m = re.search(r"(?:my name is|call me)\s+([a-zA-Z]+)", text, re.I)
            return "set_name", {"name": m.group(1) if m else "friend"}
        if re.search(r"what('s| is) my name|do you remember me|who am i", t):
            return "recall_name", {}
        if re.search(r"\b(help|commands)\b", t):
            return "help", {}
        if re.search(r"\b(thank|thanks|great|awesome|cool|nice)\b", t):
            return "thanks", {}
        if re.search(r"\b(bye|goodbye|good ?night|see you)\b", t):
            return "goodbye", {}
        if re.search(r"\?", t):
            return "question", {"text": text}
        return "fallback", {"text": text}

    # -------------------------------------------------------------- helpers
    def _reply(self, text, session, intent="general", suggestions=None, meta=None):
        out = {
            "text": text,
            "intent": intent,
            "session_turn": session["turns"],
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }
        if suggestions:
            out["suggestions"] = suggestions
        if meta:
            out["meta"] = meta
        return out

    def _name(self, session):
        return session["memory"].get("name")

    # -------------------------------------------------------------- handlers
    def _handle_greeting(self, text, slots, session):
        name = self._name(session)
        greet = f"Hey{f' {name}' if name else ''}."
        return self._reply(
            f"{greet} You're talking to Core Lattice through a simulated Alexa+ skill. "
            "Ask me what I can do, or say 'run the demo'.",
            session, intent="greeting",
            suggestions=["What can you do?", "What is Core Lattice?", "Run the demo"],
        )

    def _handle_identity(self, text, slots, session):
        return self._reply(
            "I'm Core Lattice — a conversational AI architecture built by independent developer "
            "Kate Rissman. In this demo I'm running as a simulated Alexa+ experience inside a web app, "
            "which the Amazon Developer Hackathon rules explicitly allow. I route intents, keep session "
            "memory, and answer plainly when I can't verify something instead of inventing it.",
            session, intent="identity",
            suggestions=["What is Core Lattice?", "What can you do?", "Run the demo"],
        )

    def _handle_explain_lattice(self, text, slots, session):
        return self._reply(
            "Core Lattice is Kate's proprietary AI architecture: a lattice of specialized reasoning "
            "nodes instead of one monolithic prompt. Each node handles a capability — intent routing, "
            "memory, planning, honest uncertainty — and the lattice coordinates them into one answer. "
            "What you're talking to right now is a scaffold of that engine, built for this hackathon in 8 days.",
            session, intent="explain_lattice",
            suggestions=["Run the demo", "Plan my hackathon week", "What can you do?"],
        )

    def _handle_capabilities(self, text, slots, session):
        return self._reply(
            "Here's what I can do in this demo:\n"
            "• Answer questions about Core Lattice and the build\n"
            "• Plan — say 'plan my hackathon week' and I'll break it into steps\n"
            "• Remember — tell me your name or a preference and I'll keep it for this session\n"
            "• Guided demo — say 'run the demo' for a 3-part walkthrough\n"
            "• Voice — tap the mic and talk; I'll talk back",
            session, intent="capabilities",
            suggestions=["Run the demo", "Plan my hackathon week", "My name is Kate"],
        )

    def _handle_tour(self, text, slots, session):
        steps = DEMO_FLOWS["tour"]["steps"]
        return self._reply(steps[0], session, intent="tour",
                           suggestions=["What is Core Lattice?", "Run the demo", "What can you do?"])

    def _handle_demo(self, text, slots, session):
        steps = DEMO_FLOWS["full_demo"]["steps"]
        session["memory"]["demo_step"] = 0
        return self._reply(
            "Starting the full demo.\n\n" + steps[0],
            session, intent="demo",
            suggestions=["Plan my hackathon week", "My name is Kate", "What is the capital of Mars?"],
            meta={"demo_total_steps": len(steps)},
        )

    def _handle_plan(self, text, slots, session):
        goal = slots.get("goal", "your project")
        goal_clean = re.sub(r"^plan\s+", "", goal, flags=re.I).strip() or "your project"
        steps = [
            f"Step 1 — Define done: write one sentence describing '{goal_clean}' finished.",
            "Step 2 — Split it: break that sentence into 3 shippable milestones.",
            "Step 3 — Order it: hardest dependency first, demo-able slice earliest.",
            "Step 4 — Timebox it: assign each milestone a day, with one buffer day.",
            "Step 5 — Ship it: demo the slice early, iterate on feedback, not assumptions.",
        ]
        return self._reply(
            f"Here's a plan for {goal_clean}:\n\n" + "\n".join(steps) +
            "\n\nThat's structured reasoning — one of Core Lattice's core nodes.",
            session, intent="plan",
            suggestions=["Run the demo", "What can you do?"],
        )

    def _handle_summarize(self, text, slots, session):
        return self._reply(
            "In the full build, my summarization node compresses long input into key points, "
            "decisions, and action items. In this scaffold, paste real text after 'summarize:' "
            "and the wired-up version will handle it. Try the demo flows instead for now.",
            session, intent="summarize",
            suggestions=["Run the demo", "Plan my hackathon week"],
        )

    def _handle_remember(self, text, slots, session):
        m = re.search(r"remind me (?:that )?(.+)", text, re.I) or re.search(r"remember (?:that )?(.+)", text, re.I)
        fact = m.group(1).strip() if m else text
        notes = session["memory"].setdefault("notes", [])
        notes.append(fact)
        return self._reply(
            f"Got it — I'll remember: \"{fact}\". Ask me 'what do you remember?' any time.",
            session, intent="remember",
            suggestions=["What do you remember?", "Run the demo"],
        )

    def _handle_set_name(self, text, slots, session):
        session["memory"]["name"] = slots["name"]
        return self._reply(
            f"Nice to meet you, {slots['name']}. I'll remember that for this session.",
            session, intent="set_name",
            suggestions=["What can you do?", "Run the demo"],
        )

    def _handle_recall_name(self, text, slots, session):
        name = self._name(session)
        notes = session["memory"].get("notes", [])
        if name or notes:
            parts = []
            if name:
                parts.append(f"your name is {name}")
            if notes:
                parts.append(f"you asked me to remember {len(notes)} thing(s): " + "; ".join(notes[:3]))
            return self._reply("From this session: " + ", ".join(parts) + ".",
                               session, intent="recall_name")
        return self._reply(
            "I don't have anything stored for you yet this session. Tell me your name or ask me to remember something.",
            session, intent="recall_name",
            suggestions=["My name is Kate", "Remember that I like concise answers"],
        )

    def _handle_question(self, text, slots, session):
        t = text.lower()
        if "capital of mars" in t or "mars" in t and "capital" in t:
            return self._reply(
                "Mars doesn't have a capital — it's a planet with no cities. "
                "That's honest uncertainty: I'd rather say I can't verify something than invent an answer. "
                "It's a Core Lattice design principle.",
                session, intent="question",
                suggestions=["Run the demo", "What is Core Lattice?"],
            )
        if "hackathon" in t and ("deadline" in t or "when" in t):
            return self._reply(
                "The Amazon Developer Hackathon deadline is October 23, 2026 at 2:00 PM CDT. "
                "Deliverables: a functioning demo, a source repo, product feedback, and a public video under 3 minutes.",
                session, intent="question",
                suggestions=["Run the demo", "Plan my hackathon week"],
            )
        return self._reply(
            "Good question — and here's the honest version: in this scaffold I only have scripted "
            "knowledge about Core Lattice, the hackathon, and the demo flows. The wired-up build will "
            "answer broadly. Try 'what is Core Lattice?' or 'run the demo'.",
            session, intent="question",
            suggestions=["What is Core Lattice?", "Run the demo"],
        )

    def _handle_help(self, text, slots, session):
        return self._reply(
            "Try: 'what can you do', 'what is Core Lattice', 'run the demo', "
            "'plan my hackathon week', 'my name is ___', or tap the mic and just talk.",
            session, intent="help",
        )

    def _handle_thanks(self, text, slots, session):
        return self._reply("Anytime. Say 'run the demo' if you want the full walkthrough.",
                           session, intent="thanks")

    def _handle_goodbye(self, text, slots, session):
        return self._reply("Goodbye — Core Lattice signing off. Good luck at the hackathon.",
                           session, intent="goodbye")

    def _handle_fallback(self, text, slots, session):
        return self._reply(
            f"I heard: \"{text[:120]}\". In this scaffold I work best with the demo flows — "
            "try 'what can you do' or 'run the demo' and I'll show you what Core Lattice does.",
            session, intent="fallback",
            suggestions=["What can you do?", "Run the demo", "What is Core Lattice?"],
        )


# Shared singleton for the demo server.
engine = CoreLattice()
