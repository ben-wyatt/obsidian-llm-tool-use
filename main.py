import ollama as ollama
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

with open('small_sys_prompt.txt', 'r') as file:
    SYS_PROMPT = file.read()





def test_ollama(prompt:str =SYS_PROMPT):
    print("Hello from obsidian-llm-tool-use!")
    try:
        client = ollama.get_ollama_client()
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
    from tools.md_files import get_notes_list, create_note
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

    note_list = ['A','B','Hello','Reinforcement Learning']
    with open('sample_note.md', 'r') as file:
        note_content = file.read()
    return evaluate_note(note_content,note_list,verbose=True)



if __name__ == "__main__":
    # test_ollama()
    # test_sys_prompt() 
    result = test_evals_2()
    print(f"Evaluation result: {result:.2f} (pass rate)")
    print("Done!")
