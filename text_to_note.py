import dspy
from dspy import Signature, InputField, OutputField, ChainOfThought
import os
from dspy_modules.note_gen import NoteGenerator
from tools.md_files import get_notes_list, create_note
from dotenv import load_dotenv


load_dotenv()


api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment_name = 'gpt-4.1-mini'


if not api_key:
    raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set.")
if not api_base:
    raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set.")
if not deployment_name:
    raise ValueError("AZURE_OPENAI_DEPLOYMENT environment variable is not set.")


lm = dspy.LM(
    model=f"azure/{deployment_name}",
    api_key=api_key,
    api_base=api_base,
    api_version="2023-03-15-preview" 
)

dspy.configure(lm=lm)


def obsidify_text(long_text: str, note_name: str,verbose: bool = False):
    """
    Takes a long text, formats it into Obsidian markdown using DSPy LM, 
    incorporates links to existing notes, and saves it to the vault.

    Args:
        long_text (str): The input text to format.
        note_name (str): The name of the new note to create.
    """


    note_generator = NoteGenerator()
    response = note_generator(context=long_text, note_list=get_notes_list())
    obsidian_note = response.obs_note
    if verbose:
        print(f"Response: {response}")

    create_note(note_name, obsidian_note)
    print(f"Note '{note_name}' created successfully in the vault.")


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
        obsidify_text(note, note)



