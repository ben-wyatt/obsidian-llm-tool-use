import os
import requests
from bs4 import BeautifulSoup
from tools.md_files import create_note
from text_to_note import obsidify_text

def extract_main_content(url: str) -> str:
    """Fetch and extract the main content from a URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract main content (e.g., paragraphs)
        paragraphs = soup.find_all('p')
        main_content = '\n'.join(p.get_text() for p in paragraphs)
        return main_content.strip()
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return ""

def generate_single_note_from_urls(urls: list[str], note_name: str) -> None:
    """Generate a single markdown note from a list of URLs."""
    combined_content = ""
    for url in urls:
        print(f"Processing URL: {url}")
        content = extract_main_content(url)
        if content:
            combined_content += f"# Content from {url}\n\n{content}\n\n"
        else:
            print(f"Failed to extract content from {url}")

    if combined_content:
        obsidify_text(combined_content, note_name)
        print(f"Combined note created: {note_name}.md")
    else:
        print("No content extracted from the provided URLs.")

if __name__ == "__main__":
    # Example usage
    urls = [
        "http://www.incompleteideas.net/IncIdeas/BitterLesson.html",
        "https://en.wikipedia.org/wiki/Richard_S._Sutton",
        "http://incompleteideas.net/IncIdeas/KeytoAI.html",
        'http://incompleteideas.net/rlai.cs.ualberta.ca/RLAI/richsprinciples.html'
    ]
    generate_single_note_from_urls(urls, "Rich Sutton_GPT") 