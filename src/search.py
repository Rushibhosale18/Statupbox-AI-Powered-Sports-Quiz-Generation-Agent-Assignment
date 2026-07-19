"""
Web search module.
Uses DuckDuckGo to fetch live sports news and recent results,
providing the 'fresh context' half of the RAG pipeline.
"""

from duckduckgo_search import DDGS


def get_live_news_context(sport_name):
    """
    Searches the live web for recent news, results, and events for a sport.

    Args:
        sport_name: Name of the sport (e.g. "Cricket", "Football").

    Returns:
        A formatted string containing the top 3 search result snippets,
        or a fallback message if the search fails.
    """
    search_query = (
        f"{sport_name} latest tournament results news 2026"
    )
    retrieved_texts = []

    print(f"[INFO] Searching web for: '{search_query}'...")

    try:
        ddgs = DDGS()
        results = ddgs.text(search_query, max_results=3)
        if not results:
            print("[INFO] Empty results from default search, trying bing backend...")
            results = ddgs.text(search_query, backend="bing", max_results=3)

        if results:
            for index, r in enumerate(results, start=1):
                title = r.get("title", "No Title")
                snippet = r.get("body", "No snippet available.")
                source = r.get("href", "")
                retrieved_texts.append(
                    f"Web Source {index}: {title}\n"
                    f"Snippet: {snippet}\n"
                    f"URL: {source}"
                )

    except Exception as e:
        print(f"[ERROR] Web search failed: {e}")
        return (
            "No recent web search results available. "
            "The quiz will rely solely on historical data from the knowledge base."
        )

    if not retrieved_texts:
        return "No relevant web results found for this sport."

    return "\n\n".join(retrieved_texts)
