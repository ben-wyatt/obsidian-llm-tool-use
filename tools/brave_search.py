"""
brave_api.py
------------

Thin wrapper around Brave Search REST API.
Specs: https://api-dashboard.search.brave.com/app/documentation
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import requests
from requests import Response
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()


__all__ = ["BraveSearchAPI", "BraveAPIError"]


class BraveAPIError(RuntimeError):
    """Raised for non-successful HTTP responses from Brave Search."""


class BraveSearchAPI:
    _BASE = "https://api.search.brave.com/res/v1"  # root chosen per docs [oai_citation:0‡api-dashboard.search.brave.com](https://api-dashboard.search.brave.com/app/documentation?utm_source=chatgpt.com)
    _DEFAULT_HEADERS: Dict[str, str] = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "User-Agent": "brave-api-wrapper/0.1",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        timeout: float = 10.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        """
        Parameters
        ----------
        api_key
            Brave “Subscription Token” (falls back to env var *BRAVE_API_KEY*).
        api_version
            Optional YYYY-MM-DD version string; sets API-Version header. [oai_citation:1‡api-dashboard.search.brave.com](https://api-dashboard.search.brave.com/app/documentation/web-search/request-headers)
        timeout
            Seconds before timing-out any request.
        session
            Provide your own `requests.Session` for connection pooling.
        """
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "A Brave API key is required – pass api_key= or set BRAVE_API_KEY"
            )

        self.timeout = timeout
        self.session = session or requests.Session()

        # Compose static headers
        self._headers = self._DEFAULT_HEADERS | {
            "X-Subscription-Token": self.api_key
        }
        if api_version:
            self._headers["Api-Version"] = api_version

    # ---------- public helpers ---------- #

    def web_search(self, q: str, **params: Any) -> Dict[str, Any]:
        """
        Basic Web Search (returns multiple “result types” by default) [oai_citation:2‡api-dashboard.search.brave.com](https://api-dashboard.search.brave.com/app/documentation/web-search/query)
        Examples
        --------
        >>> client.web_search("pizza near bushwick", count=10, safesearch="moderate")
        """
        return self._get("/web/search", q=q, **params)

    def news_search(self, q: str, **params: Any) -> Dict[str, Any]:
        """News vertical (requires a plan that includes news). [oai_citation:3‡api-dashboard.search.brave.com](https://api-dashboard.search.brave.com/app/documentation/news-search?utm_source=chatgpt.com)"""
        return self._get("/news/search", q=q, **params)

    def image_search(self, q: str, **params: Any) -> Dict[str, Any]:
        """Image vertical (requires image search on your plan)."""
        return self._get("/image/search", q=q, **params)

    def video_search(self, q: str, **params: Any) -> Dict[str, Any]:
        """Video vertical."""
        return self._get("/video/search", q=q, **params)

    def summarizer(self, q: str, summary: bool = True, **params: Any) -> Dict[str, Any]:
        """
        One-shot helper that triggers summarizer generation by tacking on `summary=1`
        and then reads the `summarizer` key Brave returns. Requires Pro AI plan. [oai_citation:4‡api-dashboard.search.brave.com](https://api-dashboard.search.brave.com/app/documentation/summarizer-search?utm_source=chatgpt.com)
        """
        params.setdefault("summary", int(summary))
        return self.web_search(q, **params)

    # ---------- internal ---------- #

    def _get(self, endpoint: str, **params: Any) -> Dict[str, Any]:
        """Low-level GET with automatic retries on `Retry-After` headers."""
        url = f"{self._BASE}{endpoint}"
        while True:
            resp: Response = self.session.get(
                url, headers=self._headers, params=params, timeout=self.timeout
            )
            if resp.status_code == 429 and "Retry-After" in resp.headers:
                wait = int(resp.headers["Retry-After"])
                time.sleep(wait)
                continue
            if not resp.ok:
                raise BraveAPIError(f"{resp.status_code}: {resp.text}")
            return resp.json()
        

##Tools for ReAct Agent


def get_web_links(query: str, count: int = 5) -> list[str]:
    """
    Perform a web search using the BraveSearchAPI and return a list of URLs.

    Parameters
    ----------
    query : str
        The search query string.
    count : int, optional
        The number of search results to retrieve (default is 5).

    Returns
    -------
    list[str]
        A list of URLs from the search results.
    """
    client = BraveSearchAPI()
    results = client.web_search(query, count=count)
    return [url['url'] for url in results['web']['results']]



def extract_main_content(url: str) -> str:
    """Fetch and extract the main content from a URL. Converts youtube urls to transcripts."""
    try:
        #check if url is a youtube url
        if 'youtube.com' in url:
            yt_id = url.split("v=")[1].split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(yt_id)
            transcript_text = " ".join([t["text"] for t in transcript])
            return transcript_text
        elif 'youtu.be' in url:
            #example: https://youtu.be/LCEmiRjPEtQ?si=nsyR9_UGpmIITuOR -> LCEmiRjPEtQ
            yt_id = url.split("be/")[1].split("?")[0]
            transcript = YouTubeTranscriptApi.get_transcript(yt_id)
            transcript_text = " ".join([t["text"] for t in transcript])
            return transcript_text
        else:
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

if __name__ == "__main__":
    results = get_web_links("deep dish pizza", count=5)
    print(results)