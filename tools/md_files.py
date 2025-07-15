"""All the read/write operations for markdown files in the vault."""
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
raw_path = os.getenv('VAULT_PATH', '.')
VAULT_PATH = os.path.expanduser(raw_path)
TOOL_VERSION = os.getenv('TOOL_VERSION')

def get_notes_list() -> list[str]:
    """Get a list of all markdown file paths in the vault, relative to the vault root."""
    notes_list = []
    for root, _, files in os.walk(VAULT_PATH):
        # Skip the .obsidian folder and its subfolders
        if ".obsidian" in root.split(os.sep) or 'Excalidraw' in root.split(os.sep):
            continue
        for file in files:
            if file.endswith('.md'):
                # Construct the relative path and remove the '.md' extension
                relative_path = os.path.relpath(os.path.join(root, file), VAULT_PATH)
                notes_list.append(relative_path[:-3])  # Remove the '.md' extension
    return notes_list

def get_note_content(note_name: str) -> str:
    """
    Get the content of a note by its name.

    This function retrieves the content of a markdown note from the vault based on its name.
    The note content may include references to other notes, which are formatted using 
    double brackets, e.g., [[Referenced Note Name]]. These references are used to link 
    notes together within the vault.

    Args:
        note_name (str): The name of the note (without the '.md' extension).

    Returns:
        str: The content of the note as a string.

    Raises:
        FileNotFoundError: If the specified note does not exist in the vault.
    """
    note_path = os.path.join(VAULT_PATH, note_name + '.md')
    if not os.path.exists(note_path):
        raise FileNotFoundError(f"Note '{note_name}' does not exist in the vault.")
    
    with open(note_path, 'r', encoding='utf-8') as file:
        return file.read()


def create_note(note_name: str, content: str = "", extra_tags: list[str] = None, extra_properties: dict = None) -> None:
    """Create a new markdown note with the given name and content, allowing extra tags and properties."""
    # Generate YAML frontmatter
    yaml_frontmatter = {
        "created": datetime.now().strftime('%Y-%m-%d'),
        "tags": ["llm-generated",] + (extra_tags if extra_tags else []),
        "tool_version": TOOL_VERSION
    }

    # Add extra properties if provided
    if extra_properties:
        yaml_frontmatter.update(extra_properties)

    # Convert frontmatter to YAML string
    yaml_frontmatter_str = "---\n" + "\n".join(
        f"{key}: {value if not isinstance(value, list) else '\n  - '.join([''] + value)}"
        for key, value in yaml_frontmatter.items()
    ) + "\n---\n"

    # Prepend the YAML frontmatter to the content
    full_content = f"{yaml_frontmatter_str}\n{content}"

    note_path = os.path.join(VAULT_PATH, note_name + '.md')
    with open(note_path, 'w', encoding='utf-8') as file:
        file.write(full_content)



def reindex_notes():
    """
    Reindex all notes in the vault for semantic search.

    This function retrieves the content of all markdown notes in the vault, 
    generates embeddings for each note using a SentenceTransformer model, 
    and stores the embeddings in a FAISS index for efficient similarity search. 
    Additionally, it saves the metadata (note names) associated with the embeddings.

    Steps:
    1. Retrieve the list of all notes in the vault using `get_notes_list`.
    2. Read the content of each note using `get_note_content` and prepend the note name.
    3. Generate embeddings for the note content using the "all-MiniLM-L6-v2" model.
    4. Create a FAISS index and add the embeddings to it.
    5. Save the FAISS index to a file for later use.
    6. Save the metadata (note names) to a pickle file.

    Raises:
        FileNotFoundError: If the FAISS index or metadata file cannot be written to the specified path.

    Outputs:
        - FAISS index file: "data/faiss/notes_index.faiss"
        - Metadata file: "data/faiss/notes_meta.pkl"
    """
    from sentence_transformers import SentenceTransformer
    import faiss
    import pickle
    from tools.md_files import get_notes_list, get_note_content

    # Load the SentenceTransformer model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Retrieve the list of notes and their content
    notes_list = get_notes_list()
    note_content = []
    for note in notes_list:
        content = get_note_content(note)
        content = note + '\n\n' + content
        note_content.append(content)

    # Generate embeddings for the notes
    embeddings = model.encode(note_content, convert_to_numpy=True)

    # Create a FAISS index and add the embeddings
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Save the FAISS index to a file
    faiss.write_index(index, "data/faiss/notes_index.faiss")

    # Save the metadata (note names) to a pickle file
    with open("data/faiss/notes_meta.pkl", "wb") as f:
        pickle.dump(notes_list, f)

def search_notes(query: str, top_k: int = 5):
    """
    Search for the most relevant notes based on a query.

    This function uses a precomputed FAISS index and a SentenceTransformer model
    to find the top-k most relevant notes in the vault. The notes are ranked
    based on their semantic similarity to the query.

    Args:
        query (str): The search query to find relevant notes.
        top_k (int): The number of top results to return. Defaults to 5.

    Returns:
        list: A list of note names corresponding to the top-k search results.
    """
    from sentence_transformers import SentenceTransformer
    import faiss
    import pickle
    model = SentenceTransformer("all-MiniLM-L6-v2")

    index = faiss.read_index('data/faiss/notes_index.faiss')
    with open("data/faiss/notes_meta.pkl", "rb") as f:
        notes_list = pickle.load(f)
    query_vec = model.encode([query],convert_to_numpy=True)
    result = index.search(query_vec, top_k)
    D,I = index.search(query_vec, top_k)
    return [notes_list[idx] for idx in I[0]]


if __name__ == "__main__":
    print("Vault Path:", VAULT_PATH)
    notes = get_notes_list()
    print(f"Found {len(notes)} markdown files in the vault:")
    for note in notes:
        print(note)
    
    # Example of reading an existing note
    try:
        if notes:
            sample_note = notes[0]
            print(f"\nReading content of '{sample_note}':")
            content = get_note_content(sample_note)
            print(f"Content preview: {content[:100]}...")
        else:
            print("No existing notes to read.")
    except FileNotFoundError as e:
        print(f"Error: {e}")

    # Example of creating a new note
    test_note_name = "test_note"
    test_content = "# Test Note\n\nThis is a test note created programmatically."
    print(f"\nCreating new note '{test_note_name}'...")
    create_note(test_note_name, test_content)
    print(f"Note '{test_note_name}' created successfully.")

    # Verify the new note exists and read its content
    print(f"\nVerifying note '{test_note_name}':")
    try:
        content = get_note_content(test_note_name)
        print(f"Content: {content}")
    except FileNotFoundError as e:
        print(f"Error: {e}")

