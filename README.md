# Opus 6.0

An enhanced AI agent built on top of Claude. Smarter. Better.

## What makes it "6.0"?

- **Deep Reasoning Engine** — thinks before it speaks, critiques its own answers, retries if not good enough
- **Persistent Memory** — remembers across conversations
- **Multi-Agent Orchestration** — spawns specialist sub-agents for complex tasks
- **Self-Improvement Loop** — scores its own outputs and iterates

## Quick Start

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key
python -m opus6 "your prompt here"
```

## Architecture

```
User Input
  │
  ▼
┌─────────────┐
│   Planner    │  ← breaks complex tasks into steps
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Reasoner    │  ← deep chain-of-thought with self-critique
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Executor    │  ← runs tools, code, searches
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   Critic     │  ← scores output, sends back if < threshold
└─────┬───────┘
      │
      ▼
   Response
```
