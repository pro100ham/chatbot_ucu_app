import duckduckgo_search

def web_search(query: str, num_results: int = 5) -> str:
    from duckduckgo_search import DDGS

    allowed_sites = [
        "ucu.edu.ua",
        "lvbs.com.ua",
        "wiki.ucu.edu.ua",
        "er.ucu.edu.ua",
        "vstup.ucu.edu.ua"
    ]
    site_filter = " OR ".join([f"site:{site}" for site in allowed_sites])
    full_query = f"{site_filter} {query}"

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(full_query, max_results=num_results):
            results.append(f"{r['title']}\n{r['href']}\n{r['body']}\n")

    return "\n\n".join(results) if results else "Результатів не знайдено."

