"""The core reasoning engine of Opus 6.0."""

import anthropic

MODEL = "claude-opus-4-6"


class Brain:
    """Multi-pass reasoning engine with self-critique."""

    def __init__(self, client: anthropic.Anthropic):
        self.client = client

    def think(self, prompt: str, context: str = "") -> str:
        """Single reasoning pass."""
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system="You are the reasoning core of Opus 6.0, an advanced AI system. "
            "Think deeply and carefully. Show your reasoning step by step.",
            messages=[
                {
                    "role": "user",
                    "content": f"{f'Context: {context}' if context else ''}\n\n{prompt}".strip(),
                }
            ],
        )
        return response.content[0].text

    def critique(self, question: str, answer: str) -> dict:
        """Score and critique an answer. Returns score (1-10) and feedback."""
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=4000,
            system=(
                "You are a ruthless critic. Score the answer 1-10 and explain flaws. "
                "Respond in this exact format:\n"
                "SCORE: <number>\nFEEDBACK: <your critique>"
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nAnswer: {answer}\n\nCritique this answer.",
                }
            ],
        )
        text = response.content[0].text
        score = 5
        feedback = text
        for line in text.split("\n"):
            if line.startswith("SCORE:"):
                try:
                    score = int(line.split(":")[1].strip().split("/")[0].split(".")[0])
                except ValueError:
                    pass
            if line.startswith("FEEDBACK:"):
                feedback = line.split(":", 1)[1].strip()
        return {"score": score, "feedback": feedback}

    def reason(self, prompt: str, context: str = "", quality_threshold: int = 7, max_iterations: int = 3) -> dict:
        """
        Deep reasoning with self-critique loop.
        Keeps refining until quality threshold is met or max iterations reached.
        """
        iterations = []
        current_answer = ""

        for i in range(max_iterations):
            # Build prompt with previous feedback if available
            full_prompt = prompt
            if current_answer and iterations:
                last = iterations[-1]
                full_prompt = (
                    f"Original question: {prompt}\n\n"
                    f"Your previous answer scored {last['score']}/10.\n"
                    f"Critique: {last['feedback']}\n\n"
                    f"Previous answer:\n{current_answer}\n\n"
                    f"Write an improved answer addressing the critique."
                )

            current_answer = self.think(full_prompt, context)
            critique = self.critique(prompt, current_answer)

            iterations.append({
                "iteration": i + 1,
                "answer": current_answer,
                "score": critique["score"],
                "feedback": critique["feedback"],
            })

            if critique["score"] >= quality_threshold:
                break

        return {
            "answer": current_answer,
            "final_score": iterations[-1]["score"],
            "iterations": len(iterations),
            "history": iterations,
        }
