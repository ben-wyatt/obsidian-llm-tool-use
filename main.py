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
            stream=True
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
    





if __name__ == "__main__":
    # test_ollama()
    test_sys_prompt() 
    print("Done!")
