from dspy import LM, configure
import os
from dspy_modules.note_gen import NoteGenerator
from tools.md_files import get_notes_list, create_note
from dotenv import load_dotenv
import re

load_dotenv()


api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = 'azure/gpt-4.1-mini'
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2048*16))

if not api_key:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set.")
if not api_base:
    raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set.")
if not deployment_name:
    raise ValueError("AZURE_OPENAI_DEPLOYMENT environment variable is not set.")


lm = LM(
    model=deployment_name,
    api_key=api_key,
    api_base=api_base,
    api_version="2023-03-15-preview",
    max_tokens=MAX_TOKENS
)

configure(lm=lm)


def assert_note_name_is_valid(filename: str) -> None:
    """ 
    Check if a filename is compatible with Obsidian vault requirements.
    
    Returns True if:
      - It does not include OS-level forbidden characters
      - It does not include Obsidian-reserved link/anchor characters
      - It is not a Windows reserved name (e.g., CON, PRN, AUX, NUL, COM1–COM9, LPT1–LPT9)
      - It does not end with a space or dot on Windows
    """
    # Forbidden by Windows: < > : " / \\ | ? * and control characters 0–31
    os_forbidden = r'[<>:"/\\|?*\x00-\x1F]'
    # macOS also forbids ':', but it's already in os_forbidden
    # Obsidian link/anchor conflicts: [ ] # ^
    obsidian_forbidden = r'[\[\]#^]'
    # Windows reserved basenames (case-insensitive)
    reserved_windows = {
        'CON','PRN','AUX','NUL',
        *(f'COM{i}' for i in range(1,10)),
        *(f'LPT{i}' for i in range(1,10))
    }
    # Check OS-level forbidden
    if re.search(os_forbidden, filename):
        raise ValueError(f"Filename '{filename}' contains OS-level forbidden characters.")
    # Check Obsidian-specific forbidden
    if re.search(obsidian_forbidden, filename):
        raise ValueError(f"Filename '{filename}' contains Obsidian-specific forbidden characters.")
    # Check reserved Windows names
    name_root = filename.split('.')[0].upper()
    if name_root in reserved_windows:
        raise ValueError(f"Filename '{filename}' is a Windows reserved name.")
    # On Windows, filenames cannot end with space or dot
    if filename.endswith(' ') or filename.endswith('.'):
        raise ValueError(f"Filename '{filename}' cannot end with a space or dot.")



def obsidify_text(long_text: str,
                  note_name: str, 
                  verbose: bool = False, 
                  ignore_token_limit: bool = False, 
                  extra_properties: dict = None, 
                  insert_links: bool = True,
                  prompt_with_note_list: bool = False):
    """
    Takes a long text, formats it into Obsidian markdown using DSPy LM, 
    incorporates links to existing notes, and saves it to the vault.

    Args:
        long_text (str): The input text to format.
        note_name (str): The name of the new note to create.
        verbose (bool): Whether to print verbose output.
        ignore_token_limit (bool): Whether to automatically allow the LLM call without user confirmation.
    """
    assert_note_name_is_valid(note_name+".md")
    # Token estimation
    note_list = get_notes_list()
    long_text_tokens = len(long_text) / 3.5
    note_list_tokens = len("".join(note_list)) / 3.5
    total_tokens = long_text_tokens + note_list_tokens

    if verbose:
        print(f"Estimated tokens for long_text: {long_text_tokens:.2f}")
        print(f"Estimated tokens for note_list: {note_list_tokens:.2f}")
        print(f"Total estimated tokens: {total_tokens:.2f}")
        print(f"DSPy max generation tokens: {MAX_TOKENS}")

    # Require user confirmation if auto_allow is False
    if not ignore_token_limit:
        while True:
            user_input = input(f"The estimated token usage is {total_tokens:.2f} tokens. Proceed with the LLM call? (y/n/print): ")
            if user_input.lower() == 'y':
                break
            elif user_input.lower() == 'n':
                print("LLM call aborted by the user.")
                return
            elif user_input.lower() == 'print':
                print("\nFull text:")
                print(long_text)
            else:
                print("Invalid input. Please enter 'y', 'n', or 'print'.")

    note_generator = NoteGenerator()
    if prompt_with_note_list:
        response = note_generator(context=long_text, note_list=note_list)
    else:
        response = note_generator(context=long_text,note_list=[])
    reasoning = response.reasoning
    obsidian_note = response.obs_note

    if verbose: 
        print(f"\n\nReasoning:\n\n{reasoning}")
        print(f"\n\nObsidian note:\n\n{obsidian_note}\n\n")
        print(f"Generated token estimate: {len(obsidian_note+reasoning)/3.5:.2f}")

    if insert_links:
        obsidian_note = insert_links_to_existing_notes(obsidian_note, note_list)
    model_tag = deployment_name.replace('.', '_') #obsidian tags don't support dots 
    create_note(note_name, obsidian_note, extra_tags=[model_tag], extra_properties=extra_properties)
    print(f"Note '{note_name}' created successfully in the vault.")


def insert_links_to_existing_notes(long_text: str, note_list: list[str]) -> str:
    """
    Takes a long text and a list of existing notes, and inserts links to the existing notes into the text.
    Ensures that notes already enclosed in [[ ]] are not modified.
    """
    for note in note_list:
        # Use regex to check if the note is already enclosed in [[ ]]
        pattern = rf"(?<!\[\[){re.escape(note)}(?!\]\])"
        long_text = re.sub(pattern, f"[[{note}]]", long_text)
    return long_text





if __name__ == "__main__":
    sample_text = """
    This is a sample long text that will be converted into Obsidian markdown format.
    It should include links to existing notes where relevant.
    """

    possible_notes = [
        "Machine Learning Basics",
        "Introduction to Neural Networks",
        "Understanding Gradient Descent",
        "Applications of AI in Healthcare",
        "Ethics in Artificial Intelligence"
    ]
    for note in possible_notes:
        obsidify_text(note, note,verbose=True)




