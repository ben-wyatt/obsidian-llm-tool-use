import sys
import os

# Add the directory of the script to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
from web_to_note import extract_main_content, obsidify_text, generate_single_note_from_urls
from tools.brave_search import get_web_links

def main():
    parser = argparse.ArgumentParser(description="Generate a markdown note from a URL.")
    parser.add_argument("url_or_query", type=str, help="The URL or query to extract content from.")
    parser.add_argument("note_name", type=str, help="The name of the markdown note to create.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    args = parser.parse_args()

    url_or_query = args.url_or_query
    note_name = args.note_name

    if args.verbose:
        print(f"Verbose mode enabled.")

    urls = None
    url = None

    #identify if the url_or_query is a url or a query
    if url_or_query.startswith("http"):
        url = url_or_query
        if args.verbose:
            print(f"single url identified")
    else:
        urls = get_web_links(url_or_query, count=5)
        if args.verbose:
            print(f"multiple urls identified")

    


    if urls:
        extra_properties = {"source_url": urls}
        generate_single_note_from_urls(urls, note_name, insert_links=True, verbose=args.verbose)
    elif url:
        print(f"Fetching content from: {url}")
        extra_properties = {"source_url": url}
        content = extract_main_content(url)
        obsidify_text(content, note_name, ignore_token_limit=True, insert_links=True, extra_properties=extra_properties, verbose=args.verbose)
    else:
        print("No content found.")
    print(f"Note created: {note_name}.md")

if __name__ == "__main__":
    main() 