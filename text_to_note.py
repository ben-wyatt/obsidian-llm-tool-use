import dspy
from dspy import Signature, InputField, OutputField, ChainOfThought
import os
from dspy_modules.note_gen import NoteGenerator
from tools.md_files import get_notes_list, create_note
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = 'azure/gpt-4.1-mini'


if not api_key:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set.")
if not api_base:
    raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set.")
if not deployment_name:
    raise ValueError("AZURE_OPENAI_DEPLOYMENT environment variable is not set.")


lm = dspy.LM(
    model=deployment_name,
    api_key=api_key,
    api_base=api_base,
    api_version="2023-03-15-preview" 
)

dspy.configure(lm=lm)


def obsidify_text(long_text: str, note_name: str, verbose: bool = False, auto_allow: bool = False, extra_properties: dict = None):
    """
    Takes a long text, formats it into Obsidian markdown using DSPy LM, 
    incorporates links to existing notes, and saves it to the vault.

    Args:
        long_text (str): The input text to format.
        note_name (str): The name of the new note to create.
        verbose (bool): Whether to print verbose output.
        auto_allow (bool): Whether to automatically allow the LLM call without user confirmation.
    """

    # Token estimation
    long_text_tokens = len(long_text) / 3.5
    note_list_tokens = len("".join(get_notes_list())) / 3.5
    total_tokens = long_text_tokens + note_list_tokens

    if verbose:
        print(f"Estimated tokens for long_text: {long_text_tokens:.2f}")
        print(f"Estimated tokens for note_list: {note_list_tokens:.2f}")
        print(f"Total estimated tokens: {total_tokens:.2f}")

    # Require user confirmation if auto_allow is False
    if not auto_allow:
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
    response = note_generator(context=long_text, note_list=get_notes_list())
    obsidian_note = response.obs_note
    if verbose:
        print(f"Response: {response}")

    create_note(note_name, obsidian_note, extra_tags=[deployment_name], extra_properties=extra_properties)
    print(f"Note '{note_name}' created successfully in the vault.")


#paste a list of links -> scrapes the text -> obsidify_text





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




