import sys
import os

# Add the directory of the script to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
from web_to_note import extract_main_content, obsidify_text
from tools.md_files import get_notes_list

def main():
    parser = argparse.ArgumentParser(description="Generate a markdown note from a URL.")
    parser.add_argument("url", type=str, help="The URL to extract content from.")
    parser.add_argument("note_name", type=str, help="The name of the markdown note to create.")
    args = parser.parse_args()

    url = args.url
    note_name = args.note_name

    print(f"Fetching content from: {url}")
    content = extract_main_content(url)

    # Fetch the list of existing notes
    notes_list = get_notes_list()

    if content:
        # Token estimation
        token_count = len(content) / 3.5
        if token_count > 20000:
            print(f"Aborting: The content exceeds the token limit (10,000 tokens). Estimated tokens: {token_count:.2f}")
            sys.exit(1)
        # Add the URL as a property in the note
        extra_properties = {"source_url": url}

        obsidify_text(content, note_name, auto_allow=True, extra_properties=extra_properties)
        print(f"Note created: {note_name}.md")
    else:
        print("Failed to extract content from the URL.")

if __name__ == "__main__":
    main() 