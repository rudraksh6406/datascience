"""Opus 6.0 — The main orchestrator."""

import anthropic

from .agents import AgentPool
from .brain import Brain
from .memory import Memory
from .planner import Planner


class Opus6:
    """
    Opus 6.0: an AI agent that plans, reasons, self-critiques, and remembers.

    Pipeline:
        1. Recall relevant memories
        2. Plan the approach (for complex tasks)
        3. Execute each step with specialist agents
        4. Self-critique and refine
        5. Store learnings in memory
    """

    def __init__(self, api_key: str | None = None, quality_threshold: int = 7):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self.brain = Brain(self.client)
        self.planner = Planner(self.client)
        self.agents = AgentPool(self.client)
        self.memory = Memory()
        self.quality_threshold = quality_threshold

    def _build_context(self, prompt: str) -> str:
        """Build context from memory."""
        memories = self.memory.search(prompt, limit=3)
        if not memories:
            return ""
        lines = ["Relevant memories:"]
        for m in memories:
            lines.append(f"  - [{m['created'][:10]}] {m['content'][:200]}")
        return "\n".join(lines)

    def _is_complex(self, prompt: str) -> bool:
        """Heuristic: does this need multi-step planning?"""
        complex_signals = ["build", "create", "implement", "design", "refactor", "debug", "analyze", "compare"]
        word_count = len(prompt.split())
        has_signal = any(s in prompt.lower() for s in complex_signals)
        return word_count > 20 or has_signal

    def run(self, prompt: str, verbose: bool = False) -> dict:
        """
        Run Opus 6.0 on a prompt.

        Returns dict with: answer, score, iterations, plan (if complex).
        """
        context = self._build_context(prompt)

        # Simple questions: reason directly with self-critique
        if not self._is_complex(prompt):
            result = self.brain.reason(
                prompt, context=context, quality_threshold=self.quality_threshold
            )
            self.memory.store(
                f"Q: {prompt[:100]}\nA: {result['answer'][:200]}",
                tags=["qa"],
            )
            return {
                "answer": result["answer"],
                "score": result["final_score"],
                "iterations": result["iterations"],
                "plan": None,
            }

        # Complex tasks: plan → execute → critique
        plan = self.planner.plan(prompt, context)

        if verbose:
            print(f"\n📋 Plan ({len(plan)} steps):")
            for step in plan:
                print(f"  {step['step']}. [{step['type']}] {step['description']}")

        # Execute each step with the appropriate specialist
        step_results = []
        accumulated_context = context

        for step in plan:
            specialist = self.agents.route(step.get("type", "think"))
            step_prompt = (
                f"You are executing step {step['step']} of a plan.\n"
                f"Overall goal: {prompt}\n"
                f"This step: {step['description']}\n"
                f"Previous results:\n{accumulated_context}"
            )

            result = self.agents.invoke(specialist, step_prompt)
            step_results.append({
                "step": step["step"],
                "description": step["description"],
                "specialist": specialist,
                "result": result,
            })
            accumulated_context += f"\n\nStep {step['step']} result:\n{result[:500]}"

            if verbose:
                print(f"  ✅ Step {step['step']} done ({specialist})")

        # Synthesize final answer
        synthesis_prompt = (
            f"Original task: {prompt}\n\n"
            f"Step results:\n"
            + "\n\n".join(
                f"--- Step {r['step']}: {r['description']} ---\n{r['result']}"
                for r in step_results
            )
            + "\n\nSynthesize these results into a final, coherent answer."
        )

        final = self.brain.reason(
            synthesis_prompt,
            quality_threshold=self.quality_threshold,
        )

        # Remember
        self.memory.store(
            f"Task: {prompt[:100]}\nPlan: {len(plan)} steps\nScore: {final['final_score']}/10",
            tags=["task", "complex"],
        )

        return {
            "answer": final["answer"],
            "score": final["final_score"],
            "iterations": final["iterations"],
            "plan": plan,
            "steps": step_results,
        }
