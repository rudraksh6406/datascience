"""Task planner — breaks complex problems into steps."""

import json

import anthropic

MODEL = "claude-opus-4-6"


class Planner:
    """Decomposes complex tasks into executable steps."""

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def plan(self, task: str, context: str = "") -> list[dict]:
        """
        Break a task into ordered steps.
        Returns list of {step, description, type} dicts.
        Type is one of: think, search, code, write, verify.
        """
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=(
                "You are a planning engine. Break the user's task into 2-7 concrete steps. "
                "Respond with a JSON array of objects, each with keys: "
                '"step" (int), "description" (string), "type" (one of: think, search, code, write, verify). '
                "Output ONLY the JSON array, no other text."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"{f'Context: {context}' if context else ''}\n\nTask: {task}".strip(),
                }
            ],
        )
        text = response.content[0].text.strip()
        # Extract JSON from response
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return [{"step": 1, "description": task, "type": "think"}]
