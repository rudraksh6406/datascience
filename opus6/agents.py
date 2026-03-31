"""Specialist sub-agents for Opus 6.0."""

import anthropic

MODEL = "claude-opus-4-6"

SPECIALISTS = {
    "coder": (
        "You are an elite software engineer. Write clean, correct, production-quality code. "
        "Include only what's needed — no fluff, no over-engineering."
    ),
    "researcher": (
        "You are a research specialist. Analyze information thoroughly, cite your reasoning, "
        "identify gaps in knowledge, and present balanced conclusions."
    ),
    "writer": (
        "You are a world-class writer. Be clear, concise, and compelling. "
        "Match the tone to the audience. Every word should earn its place."
    ),
    "debugger": (
        "You are a debugging expert. Analyze errors systematically: "
        "reproduce, isolate, identify root cause, fix, verify. Show your reasoning."
    ),
    "architect": (
        "You are a systems architect. Design for simplicity, scalability, and maintainability. "
        "Consider trade-offs explicitly. Prefer boring technology that works."
    ),
}


class AgentPool:
    """Pool of specialist sub-agents."""

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def invoke(self, specialist: str, prompt: str, context: str = "") -> str:
        """Invoke a specialist agent."""
        system = SPECIALISTS.get(specialist)
        if not system:
            available = ", ".join(SPECIALISTS.keys())
            raise ValueError(f"Unknown specialist '{specialist}'. Available: {available}")

        response = self.client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": f"{f'Context: {context}' if context else ''}\n\n{prompt}".strip(),
                }
            ],
        )
        return response.content[0].text

    def route(self, task_type: str) -> str:
        """Map a task type to the best specialist."""
        mapping = {
            "think": "researcher",
            "search": "researcher",
            "code": "coder",
            "write": "writer",
            "verify": "debugger",
            "debug": "debugger",
            "design": "architect",
        }
        return mapping.get(task_type, "researcher")
