"""
Quick and dirty script for directly pasting text into a note.
Copy the results from a ChatGPT response and paste it into this script.
It's not working correctly, I think because Raycast gets rid of newlines.
"""

import sys
import os

# Add the directory of the script to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
from text_to_note import paste_text_to_note

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
    paste_text_to_note(text, note_name, verbose=args.verbose)

if __name__ == "__main__":
    main()
