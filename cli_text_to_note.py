"""
Use this for "obsifiying" text.
"""

import sys
import os

# Add the directory of the script to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
from text_to_note import obsidify_text

def main():
    parser = argparse.ArgumentParser(description="Generate a markdown note from text input.")
    parser.add_argument("text", type=str, help="The text to process and convert into a note.")
    parser.add_argument("note_name", type=str, help="The name of the markdown note to create.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()

    text = args.text
    note_name = args.note_name

    if args.verbose:
        print(f"Verbose mode enabled.")
        print(f"Processing text: {text}")

    # Process the text and generate the note
    content = obsidify_text(text, note_name, verbose=args.verbose, ignore_token_limit=True, insert_links=True)
    if content:
        print(f"Note created: {note_name}.md")
    else:
        print("Failed to process the text.")

if __name__ == "__main__":
    main()
