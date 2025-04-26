"""All the read/write operations for markdown files in the vault."""
import os
from dotenv import load_dotenv

load_dotenv()
raw_path = os.getenv('VAULT_PATH', '.')
VAULT_PATH = os.path.expanduser(raw_path)


def get_notes_list()-> list[str]:
    """Get a list of all markdown file names in the vault."""
    notes_list = []
    for root, _, files in os.walk(VAULT_PATH):
        for file in files:
            if file.endswith('.md'):
                notes_list.append(file[:-3])  # Remove the '.md' extension
    return notes_list

def get_note_content(note_name: str) -> str:
    """Get the content of a markdown note by its name."""
    note_path = os.path.join(VAULT_PATH, note_name + '.md')
    if not os.path.exists(note_path):
        raise FileNotFoundError(f"Note '{note_name}' does not exist in the vault.")
    
    with open(note_path, 'r', encoding='utf-8') as file:
        return file.read()


def create_note(note_name: str, content: str = "") -> None:
    """Create a new markdown note with the given name and content."""
    note_path = os.path.join(VAULT_PATH, note_name + '.md')
    with open(note_path, 'w', encoding='utf-8') as file:
        file.write(content)


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

