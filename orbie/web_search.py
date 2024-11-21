import requests
from secret_vals import config

def search(query, num_results=config["search"]["num_results"]):
    url = config["search"]["API"]
    params = {
        "q": query,
        "format": "json"
    }
    response = requests.get(url, params=params, verify=False)
    response = response.json()
    # Response pattern: query: str, number_of_results: int, results: list of dict
    # Results pattern (All str): url, title, content, thumbnail, engine, parsed_url, template, engines, positions, score, category
    results = []
    # Get top 5 results
    for result in response["results"][:num_results]:
        results.append({
            "url": result["url"],
            "title": result["title"],
            "content": result["content"],
        })
    # Return stringified list with query
    return f"Query: {response['query']}\nResults: {results}"



