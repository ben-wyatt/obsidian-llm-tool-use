import ollama as ollama
from dotenv import load_dotenv
from dspy import Prediction
import re
import argparse
from tools.md_files import create_note, get_notes_list

# Load environment variables from .env file
load_dotenv()

with open('small_sys_prompt.txt', 'r') as file:
    SYS_PROMPT = file.read()


def test_ollama(prompt:str =SYS_PROMPT):
    print("Hello from obsidian-llm-tool-use!")
    try:
        client = ollama.start_ollama()
        print("Ollama client initialized successfully.")
        stream = client.chat.completions.create(
            model="qwen2.5:7b-instruct-q4_K_M",
            messages=[
                {"role": "system", "content": prompt},
                # {"role": "user", "content": "Make a todo list with 5 things to do today."}
            ],
            stream=True,
            max_tokens=2000,
        )

        print("Response from Ollama:")
        generated_text = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                generated_text += content
                print(content, end="", flush=True)
        print()  # Add a newline at the end
        
        return generated_text

    except RuntimeError as e:
        print(f"Error initializing Ollama client: {e}")
    

def test_sys_prompt():

    #list of notes
    note_list = get_notes_list()
    note_list_str = "\n".join([f"- {note}" for note in note_list])

    #the note context
    with open('grpo_context.txt', 'r') as file:
        grpo_context = file.read()

    with open('chatgpt_sys_prompt.md', 'r') as file:
        sys_prompt = file.read()\
            .replace("!!CONTEXT!!", grpo_context)\
            .replace("!!NOTE_LIST!!", note_list_str)
        

    # print(20*"=","SYSTEM PROMPT",20*"=","\n",sys_prompt,"\n",20*"=")
    result = test_ollama(sys_prompt)
    create_note("GRPO",result)
    

def test_evals():
    """Test evaluations for the note generation module."""
    from dspy_modules.note_gen import links_exist


    note_list = ['A','B','Hello','Reinforcement Learning']
    print(f"notes: {note_list}")
    assert not links_exist("This is a note with links to [[Reinforcement Learning]] and [[D]].", note_list)
    assert links_exist("This note has no links.", note_list)
    assert not links_exist("This note has a link to [[NonExistentNote]].", note_list)
    assert links_exist("This note has a link to [[Reinforcement Learning#hello there]].", note_list)
    assert links_exist("This note has links to [[Reinforcement Learning|RL]] ", note_list)
    assert links_exist("This note has a link to [[Reinforcement Learning|RL]] and [[A#B]] and [[B#A|Hello]].", note_list)
    
    print("All tests passed!")

def test_evals_2():
    """Use the evaluate_note"""
    from dspy_modules.note_gen import evaluate_note
    print("testing dspoy_modules.note_gen.evaluate_note using sample_note.md")
    note_list = ['A','B','Hello','Reinforcement Learning']
    with open('sample_note.md', 'r') as file:
        note_content = file.read()
    result = evaluate_note(note_content,note_list,verbose=True)
    print(f"Evaluation result: {result:.2f} (pass rate)")
    return result

def test_dpsy():
    from dspy_modules import run
    
    pred: Prediction = run.test_dspy()
    print("DSPy prediction completions:", pred.completions)
    
    # Extract the note content from the nested structure
    if hasattr(pred, '_store') and 'obs_note' in pred._store:
        nested_pred = pred._store['obs_note']
        if hasattr(nested_pred, 'obs_note'):
            note_content = nested_pred.obs_note
            
            # Save the note to a file
            note_name = "SQLite_for_Note_Data"
            create_note(note_name, note_content)
            print(f"Note saved as '{note_name}.md'")
        else:
            print(f"Error: Nested prediction doesn't have obs_note attribute")
    else:
        print(f"Error: Could not find obs_note in prediction structure")
    
    return pred

def generate_note_from_topic(topic: str, related_notes: list = None):
    """
    Generate a note on a specific user-provided topic.
    
    Args:
        topic: The topic to generate a note about
        related_notes: Optional list of related note filenames. If None, all notes will be used.
        
    Returns:
        The generated prediction
    """
    from dspy_modules import run
    
    # If no related notes are provided, use all notes in the vault
    if related_notes is None:
        related_notes = get_notes_list()
        
    # Generate a clean filename from the topic
    note_name = re.sub(r'[^\w\s]', '', topic).strip()
    if not note_name:
        note_name = "Generated_Note"
    
    # Generate the note content using DSPy
    print(f"Generating note about: {topic}")
    print(f"Using related notes: {related_notes}")
    
    # Call the DSPy module with the topic as context
    pred = run.generate_note_from_topic(topic=topic, note_list=related_notes)
    
    # Extract the note content from the prediction
    if hasattr(pred, 'obs_note'):
        # Direct access to obs_note field
        note_content = pred.obs_note.obs_note
        
        # Save the note to a file
        create_note(note_name, note_content)
        print(f"Note saved as '{note_name}.md'")
    else:
        print(f"Error: Could not find obs_note in prediction structure")
    
    return pred


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Generate Obsidian notes using LLMs')
    parser.add_argument('--topic', type=str, help='Topic to generate a note about')
    parser.add_argument('--test', action='store_true', help='Run the test_dpsy function')
    
    args = parser.parse_args()
    
    client = ollama.start_ollama()
    note_list = get_notes_list()
    
    if args.topic:
        # Generate a note on the specified topic
        generate_note_from_topic(args.topic, note_list)
    elif args.test:
        # Run the test function
        test_dpsy()
    else:
        # If no arguments provided, show a simple interactive prompt
        topic = input("Enter a topic for your note: ")
        
        # Generate the note - note is already saved inside generate_note_from_topic
        pred = generate_note_from_topic(topic, note_list)
        print("Note generation complete.")

    
    print("Done!")


