
## Implemented Features
- basic io: read, write, list notes
- text_to_note: paste some raw text in, get an LLM-generated note. uses azure gpt-4.1-mini
- web_to_note: URL list -> grab body text -> llm -> note
- LLMs: Ollama (qwen) and azure/gpt-4.1-mini


## Bugs


## Intended Features
- obsidian search with tags
- internet search
- multi-hop rag?
- track token usage
- more accurate token estimates (use DSPy completions data)
- append note: continue a note with new context


## Chat Features
- interface
- summarize selection
- expand selection with web search
- create new note

## List of Actionable Items
- implement DSPy `GenerateSearchQuery` to search internet for relevant information. Flow becomes "Make me a note on Path Integrals" -> fully formed note
- gather training data for generate_note(); or other ways to get better insight from transcripts
- organize thoughts: fix this readme, review Obsidian note with thoughts on the project
- more advanced DSPy flows: grab extra research, identify possible new note topics
- advanced note-connections: note aliases, fuzzy-match note names like "Stablecoin Future" and "Future of Stablecoins". "Dwarkesh Podcast" with "Dwarkesh Patel Podcast"
  - might require 
- daily note integration






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


As a more complex example: "make a new note about GRPO.". It calls o3 to do some internet research on GRPO, then it searches for files by keywords, and reformats the GPT answer into a proper Obsidian note.

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
- stood up as MCP server? yes I actually like this idea a lot. could mean I can get it working on the phone.

OpenAI sometimes hides their hyperlinks behind special tokens like `oai_citation_attribution`. Is there anyway for me to still get those hyperlinks?

At first, lets just use DSPy. I just wrote a bunch of evaluations that check to see if a note is well formatted. Following [this tutorial](https://youtu.be/Hf6u4SDSFcg?si=KXiLvmisYm88lzkP&t=728)

One possible source of context -> note: I take notes on media that I watch. Then get transcript of the video/podcast. 



## Gathering Data

To use DSPy, we need examples of the task being done properly.

For each sample we need:
- a list of existing obsidian notes (for the model to possibly link to based on awareness)
- context: some text-based digital artifact, like a blog post, a meeting transcript, podcast transcript
- a note derived from that context. Formatted in obsidian markdown. With links to other existing obsidian notes.


I'm thinking that the best data-gathering strat is finding examples for context, running them through o3 for a first pass, then finish up by checking the frontmatter and whatever. Along the way save some of the unfinished ones so I can verify the verifier.
