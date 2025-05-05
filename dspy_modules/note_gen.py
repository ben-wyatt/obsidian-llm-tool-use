"""DSPy context -> note module
It should be able to:
- include a tags section at the beginning
- include [[]] links to existing notes within the text

"""

from typing import List
import dspy
from dspy import Signature, InputField, OutputField
import re

class GenerateNote(dspy.Signature):
    """Generates an Obsidian markdown note from context and list of existing notes."""
    context = InputField(desc="External knowledge context")
    note_list = InputField(desc="List of existing notes")
    obs_note = OutputField(desc="Generated Obsidian markdown note")



class GenerateSearchQuery(dspy.Signature):
    """Generates an Obsidian search query from context and list of existing notes. Details: https://help.obsidian.md/plugins/search"""
    context = InputField(desc="External knowledge context")
    tag_list = InputField(desc="List of all tags in the vault")
    obs_query = OutputField(desc="Generated Obsidian search query")


class NoteGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_note = dspy.ChainOfThought(GenerateNote)
    def forward(self,context: str, note_list: List[str]) -> str:
        obs_note = self.generate_note(context=context, note_list=note_list)
        return dspy.Prediction(obs_note=obs_note,context=context,note_list=note_list)

####################
#### Evaluation ####
####################



#### Properties/Metadata
import re, yaml, json, textwrap
from typing import List
from pathlib import Path

#YAML or JSON block right at the top (front matter)
def has_yaml_front_matter(note: str, verbose: bool = False) -> bool:
    result = bool(re.match(r"^---\s*\n", note))
    if verbose:
        print(f"  - Front matter check: {'Found' if result else 'Not found'}")
    return result

#Can we parse the properties cleanly?
def properties_parse_clean(note: str, verbose: bool = False) -> bool:
    m = re.match(r"^---\s*\n(.*?)\n---", note, re.DOTALL)
    if not m:
        if verbose:
            print("  - Properties parsing: Failed to find front matter block")
        return False
    block = m.group(1).strip()
    try:
        yaml.safe_load(block if block.startswith("{") else textwrap.dedent(block))
        if verbose:
            print("  - Properties parsing: Valid YAML/JSON")
        return True
    except yaml.YAMLError as e:
        if verbose:
            print(f"  - Properties parsing: Invalid YAML/JSON - {str(e)}")
        return False

#Does it include at least one 'tags' property (YAML list or string)?
def tags_property_present(note: str, verbose: bool = False) -> bool:
    m = re.match(r"^---\s*\n(.*?)\n---", note, re.DOTALL)
    if not m:
        if verbose:
            print("  - Tags property: No front matter found")
        return False
    props = yaml.safe_load(m.group(1))
    result = "tags" in props and bool(props["tags"])
    if verbose:
        if "tags" in props:
            print(f"  - Tags property: {'Present with values' if result else 'Present but empty'}")
        else:
            print("  - Tags property: Missing")
    return result

#Ensure any **required** properties (e.g. aliases, created) are present
REQUIRED = {"aliases", "created"}
def required_properties_present(note: str, verbose: bool = False) -> bool:
    m = re.match(r"^---\s*\n(.*?)\n---", note, re.DOTALL)
    if not m:
        if verbose:
            print("  - Required properties: No front matter found")
        return False
    props = yaml.safe_load(m.group(1))
    missing = REQUIRED - props.keys()
    result = REQUIRED.issubset(props.keys())
    if verbose:
        if result:
            print("  - Required properties: All present")
        else:
            print(f"  - Required properties: Missing {', '.join(missing)}")
    return result



#### Internal Links
# def links_exist(obs_note:str,note_list:List[str]) -> bool:
#     """Check if the note contains Obsidian links."""
#     #find every [[link]] in the note
#     links = re.findall(r'\[\[([^\]]+)\]\]', obs_note)    
#     # Process each link to handle aliases
#     for link in links:
#         # If link contains an alias (format: [[actual_note|display_text]])
#         if '|' in link:
#             actual_note = link.split('|')[0]
#             actual_note = actual_note.split('#')[0]  # Remove any fragment identifier
#             if actual_note not in note_list:
#                 return False
#         # Regular link without alias
#         elif link.split('#')[0] not in note_list:
#             return False
#     return True

WIKILINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")

#Your original, but now supports heading and block anchors
def links_exist(note: str, vault_files: List[str], verbose: bool = False) -> bool:
    links_found = WIKILINK_RE.findall(note)
    if verbose:
        print(f"  - Links check: Found {len(links_found)} wiki links")
    
    for raw in links_found:
        target = raw.split("|")[0]           # strip alias
        target = target.split("#")[0]        # strip heading or block
        if target not in vault_files:
            if verbose:
                print(f"  - Links check: '{target}' not found in vault")
            return False
    
    if verbose and links_found:
        print("  - Links check: All links resolve to existing files")
    return True

#Check that any [[note|Alias]] aliases resolve to real files
def aliases_resolve(note: str, vault_files: List[str], verbose: bool = False) -> bool:
    aliases_found = [raw for raw in WIKILINK_RE.findall(note) if "|" in raw]
    if verbose:
        print(f"  - Aliases check: Found {len(aliases_found)} aliased links")
    
    for raw in aliases_found:
        target = raw.split("|")[0]
        if target.split('#')[0] not in vault_files:
            if verbose:
                print(f"  - Aliases check: '{target}' not found in vault")
            return False
    
    if verbose and aliases_found:
        print("  - Aliases check: All aliased links resolve to existing files")
    return True



#### Markdown Structuring
#First non-blank line should be an H1 title
def has_title_heading(note: str, verbose: bool = False) -> bool:
    # Skip frontmatter if present
    content = note
    if note.startswith('---'):
        frontmatter_end = note.find('---', 3)
        if frontmatter_end != -1:
            content = note[frontmatter_end + 3:].strip()
    
    # Look for first non-empty line in content after frontmatter
    for line in content.splitlines():
        if line.strip():                       # first non-empty
            result = line.startswith("# ")
            if verbose:
                if result:
                    print("  - Title heading: Found H1 title")
                else:
                    print(f"  - Title heading: First content line is not H1: '{line[:40]}...'")
            return result
    if verbose:
        print("  - Title heading: Note appears empty")
    return False
#Prevent skipping H-levels (## followed by ####)
def heading_levels_monotonic(note: str, verbose: bool = False) -> bool:
    levels = [len(m.group(1)) for m in re.finditer(r"^(#{1,6})\s", note, re.MULTILINE)]
    if not levels:
        if verbose:
            print("  - Heading levels: No headings found")
        return True
    
    result = all(abs(a - b) <= 1 for a, b in zip(levels, levels[1:]))
    if verbose:
        if result:
            print("  - Heading levels: All heading levels properly sequential")
        else:
            problems = [(i, levels[i], levels[i+1]) 
                       for i in range(len(levels)-1) 
                       if abs(levels[i] - levels[i+1]) > 1]
            print(f"  - Heading levels: Found {len(problems)} heading level skip(s)")
    return result

#Make sure any triple-backtick code blocks close
def code_blocks_closed(note: str, verbose: bool = False) -> bool:
    count = note.count("```")
    result = count % 2 == 0
    if verbose:
        if result:
            print(f"  - Code blocks: Found {count//2} properly closed code blocks")
        else:
            print(f"  - Code blocks: Unclosed code block detected ({count} backtick markers)")
    return result

#Cosmetic: blank line after the front matter
def blank_line_after_front_matter(note: str, verbose: bool = False) -> bool:
    result = bool(re.match(r"^---\s*\n.*?\n---\s*\n\n", note, re.DOTALL))
    if verbose:
        if result:
            print("  - Front matter spacing: Blank line present after front matter")
        else:
            print("  - Front matter spacing: Missing blank line after front matter")
    return result


#### Collect all evaluations in a list
ALL_EVALS = [
    has_yaml_front_matter,
    properties_parse_clean,
    tags_property_present,
    required_properties_present,
    links_exist,
    aliases_resolve,
    has_title_heading,
    heading_levels_monotonic,
    code_blocks_closed,
    blank_line_after_front_matter,
]

def evaluate_note(note: str, vault_files: List[str], verbose=False) -> float:
    """Return a pass rate between 0 and 1 for the generated note."""
    passes = 0
    if verbose:
        print("Evaluating note quality:")
        
    for fn in ALL_EVALS:
        # Functions that need vault_files accept two args
        try:
            if fn.__code__.co_argcount == 2:  # Functions without verbose param
                ok = fn(note, verbose)
            elif fn.__code__.co_argcount == 3:  # Functions with vault_files and verbose
                ok = fn(note, vault_files, verbose)
            else:
                raise ValueError(f"Unexpected function signature for {fn.__name__}")
        except Exception as e:
            ok = False
            if verbose:
                test_name = fn.__name__
                print(f"{test_name}: ERROR - {str(e)}")
        passes += ok
        
        if verbose:
            test_name = fn.__name__
            result = "PASS" if ok else "FAIL"
            print(f"{test_name}: {result}")
            
    score = passes / len(ALL_EVALS)
    if verbose:
        print(f"Overall score: {score:.2f} ({passes}/{len(ALL_EVALS)} checks passed)")
    return score