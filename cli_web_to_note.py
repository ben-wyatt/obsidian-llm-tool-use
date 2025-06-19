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
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()

    url = args.url
    note_name = args.note_name

    if args.verbose:
        print(f"Verbose mode enabled.")

    print(f"Fetching content from: {url}")
    content = extract_main_content(url)


    if content:
        # Add the URL as a property in the note
        extra_properties = {"source_url": url}

        obsidify_text(content, note_name, ignore_token_limit=True, extra_properties=extra_properties, verbose=args.verbose)
        print(f"Note created: {note_name}.md")
    else:
        print("Failed to extract content from the URL.")

if __name__ == "__main__":
    main() 