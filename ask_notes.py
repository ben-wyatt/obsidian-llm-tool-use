from dotenv import load_dotenv
import os
import argparse
load_dotenv()
os.environ["VAULT_PATH"]="~/Obsidian/Notes Vault"

import dspy
from dspy.primitives.prediction import Prediction

from tools.md_files import search_notes,get_note_content

os.environ["VAULT_PATH"]="~/Obsidian/Notes Vault"

azure_lm = dspy.LM(
    model=f"azure/gpt-4.1",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2023-03-15-preview"
)
dspy.configure(lm=azure_lm)



class NoteResearcher(dspy.Signature):
    """Read through notes to answer a question"""
    question: str = dspy.InputField(description="The question that needs to be answered.")
    answer: str = dspy.OutputField(description="The answer to the question.")

agent = dspy.ReAct(
    NoteResearcher,
    tools=[search_notes,get_note_content]
)

def ask_notes(question: str) -> Prediction:
    """
    Ask a question and retrieve a prediction based on the content of the Obsidian Vault.

    Args:
        question (str): The question that needs to be answered.

    Returns:
        Prediction: An object containing the attributes `trajectory`, `reasoning`, and `answer`.
    """
    return agent(question=question)

def main():
    parser = argparse.ArgumentParser(description="Ask a question and retrieve a prediction based on the content of the Obsidian Vault.")
    parser.add_argument("question", type=str, help="The question that needs to be answered.")
    args = parser.parse_args()
    result = ask_notes(question=args.question)
    
    print("\n\n===========-TRAJECTORY-============\n\n")
    for step_key, step_value in result.trajectory.items():
        if "observation" in step_key and len(step_value) > 300:
            step_value = step_value[:300] + "..."
        print(f"{step_key}: {step_value}\n")  
    
    print("\n\n===========-REASONING-============\n\n")
    print(result.reasoning)
    print("\n\n===========-ANSWER-============\n\n")
    print(result.answer)


if __name__ == "__main__":
    main()