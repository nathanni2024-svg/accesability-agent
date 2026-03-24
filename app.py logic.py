import datetime

def save_research_to_file(query, content):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"research_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Deep Research: {query}\n")
        f.write(f"Generated on: {timestamp}\n\n")
        f.write(content)
    
    return filename
