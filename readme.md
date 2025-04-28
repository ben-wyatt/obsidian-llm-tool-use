hello-world



## Implemented Features
- basic os: read, write, list notes
- single workflow template: add some document context and convert to obsidian note. links to previous notes.


## Bugs
- sometimes it just goes on and on and on. generating the same note over and over again. maybe have a limit to token length? This would have to be fixed either with slightly better prompting (DSPy!) or with training.

## Intended Features
- obsidian search with tags
- summarize selection
- expand selection
- Chat
- internet search
- multi-hop rag?


## List of Actionable Items
- write first system prompt: include the details on how obsidian works like [[]] and whatever. See how well it performs
- make a new test vault folder
- write first two tools: get list of .md files in Vault folder, create new file and write something in that file.
- build some examples: context, note list -> nicely formatted notes.



### Chat Interactions
- Version control
- summarize
- create new note
- write on note


I'll be using Qwen 2.5 7b through Ollama to start, since it scores very high on tool calling.

## Context -> Note Workflow
I don't really know how the `agent frameworks` handle their LLM flows. *Ideally* what this system does is this:
- user provides mission statement. example: "Here is a transcript from our last meeting: {transcript}. Can you reformat them and then create some actionable items for the team?"
- LLM thinks through an action plan: "OK I have to look for similar notes to the content described in here first, then I will identify any connections from this discussion to other notes. After that, I will reformat the transcription, including any note connections along the way."
  - in this scenario the likely connection notes would be notes on the people in the meeting or concept notes of things discussed in the meeting.
- it executes these one at a time. First it generates the tokens for "find_notes_list()" with some type of content filtering on it.
  - not sure how to do the content filtering but one way would be to do semantic search with a few keywords drawn by the LLM": `find_notes_list(semantic_keywords=['Fuel Team Meeting','Reinforcement Learning','Note Taking Features'])`
  - answer: use the [Search functionality](https://help.obsidian.md/plugins/search#Search+operators)
- then it identifies if any of them are actually important. moves forward
- it reformats the given context, the transcript, into obsidian markdown. It should be aware of all of the major Obsidian Markup Features
- 

As a more complex example: "make a new note about GRPO.". It calls GPT-o3 to do some internet research on GRPO, then it searches for files by keywords, and reformats the GPT answer into a proper Obsidian note.

### Obsidian Markup Features
**Double Brackets**: links to other notes. can point to non-existant notes.
**bracket-bang**:
[**tags**](https://help.obsidian.md/tags): using a `#` before a word. 
[**properties**](https://help.obsidian.md/properties): creating a section via 2x `---` and a keyword.
**callouts**: `[!whatever]`



## Meta Thoughts on the project
It's going to be a big pain in the ass if I want to implement this into Obsidian. There's a few ways I could do it:
- TypeScript shim to Python (?)
- Use other plugins: `Python Scripter` or `Python Lab`. run everything as a series of scripts (probably no good because I need UI elements as well)
- Persistant Python service and talk via HTTP using the local REST API

OpenAI sometimes hides their hyperlinks behind special tokens like `oai_citation_attribution`. Is there anyway for me to still get those hyperlinks?

At first, lets just use DSPy. I just wrote a bunch of evaluations that check to see if a note is well formatted. Following [this tutorial](https://youtu.be/Hf6u4SDSFcg?si=KXiLvmisYm88lzkP&t=728)