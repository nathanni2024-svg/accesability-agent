import os
import argparse
from tavily import TavilyClient

def deep_research(query, max_iterations=2):
    """
    Advanced research logic that can be called by the Main App.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key or api_key == "your_tavily_api_key_here":
        return "Error: TAVILY_API_KEY is missing. You need to provide a real API key."

    try:
        client = TavilyClient(api_key=api_key)
        
        # Perform an 'Advanced' search which includes AI-powered summaries
        search_result = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True
        )
    except Exception as e:
        return f"Tavily API Search Error: {str(e)}"

    # Building the structured response
    report = [f"### 🔎 Research Results for: {query}"]
    report.append(f"\n**Executive Summary:**\n{search_result.get('answer', 'Summary unavailable.')}")
    
    report.append("\n**Key Sources Found:**")
    for res in search_result.get('results', []):
        # We truncate the content to 1000 chars to save AI tokens
        snippet = res['content'][:1000] + "..." if len(res['content']) > 1000 else res['content']
        report.append(f"- **[{res['title']}]({res['url']})**")
        report.append(f"  > {snippet}\n")

    return "\n".join(report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, required=True)
    args = parser.parse_args()
    print(deep_research(args.query))