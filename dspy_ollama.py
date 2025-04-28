"""I'm really not sure how I should do this implementation..."""
import requests, dspy_modules, pathlib

class OllamaLM(dspy_modules.LM):
    def __init__(self, model="qwen2.5:7b-instruct-q4_K_M", url="http://localhost:11434/api/chat"):
        super().__init__(max_tokens=2048)           # you can pass temp, top_p, etc.
        self.model, self.url = model, url

    def _call(self, prompt, stop):
        payload = {"model": self.model,
                   "messages": [{"role": "user", "content": prompt}],
                   "stream": False}
        r = requests.post(self.url, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    
dspy_modules.settings.configure(lm=OllamaLM())


class MakeNote(dspy_modules.Module):
    class Sig(dspy_modules.Signature):
        """Transform raw context & note list into a markdown Obsidian note
        with [[links]] and #tags."""
        context: str
        note_list: str
        markdown_note: str
    
    def forward(self, context, note_list):
        lm = dspy_modules.LM()
        prompt = f"""
You are an Obsidian note-writer.  Use [[double brackets]] to link to existing
notes from the list below if relevant.  Return *only* markdown.

-- Existing notes --
{note_list}

-- New context --
{context}

Generate the new note:
"""
        return {"markdown_note": lm(prompt)}
    
from dspy_modules.assertions import LMAssertion

class NoteCompliance(LMAssertion):
    def check(self, markdown_note):
        # must have at least one H1 and end with newline
        return markdown_note.startswith("# ") and markdown_note.endswith("\n")