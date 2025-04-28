---
aliases:
  - "DSPy Example"
created: 2025-04-28
tags:
  - knowledge-base
  - dspy
---

# DSPy – Passing All Formatting Checks

Here are some links:

[[A]] [[B]]  [[Reinforcement Learning#hey!|whatever]]



## Overview
DSPy is a *declarative* framework that turns each LLM interaction into a typed module and then compiles the whole graph with automatic prompt- or demo-optimization.

### Key Features
- **Module graph**: compose reasoning steps as Python objects.  
- **Optimizers**: `BootstrapFewShot`, `ReActFeedback`, lightweight fine-tuning.  
- **Back-end agnostic**: works with local Ollama, llama-cpp, or hosted APIs.  
For more, see the project’s GitHub page:  
[stanfordnlp/dspy-ai](https://github.com/stanfordnlp/dspy-ai)

## Code Example
```python
import dspy, requests

class OllamaLM(dspy.LM):
    def _call(self, prompt, stop):
        r = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": "qwen2.5:7b-instruct-q4_K_M",
                  "messages": [{"role": "user", "content": prompt}],
                  "stream": False},
            timeout=60,
        )
        return r.json()["choices"][0]["message"]["content"]

dspy.settings.configure(lm=OllamaLM())

class Explain(dspy.Signature):
    topic: str
    answer: str

explain = dspy.ChainOfThought(Explain)
print(explain(topic="DSPy").answer)