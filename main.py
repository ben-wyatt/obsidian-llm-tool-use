import ollama as ollama


def test_ollama():
    print("Hello from obsidian-llm-tool-use!")
    try:
        client = ollama.get_ollama_client()
        print("Ollama client initialized successfully.")
        stream = client.chat.completions.create(
            model="qwen2.5:7b-instruct-q4_K_M",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how can I use Ollama with Python?"}
            ],
            stream=True
        )

        print("Response from Ollama:")
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()  # Add a newline at the end



    except RuntimeError as e:
        print(f"Error initializing Ollama client: {e}")
    






if __name__ == "__main__":
    test_ollama()
