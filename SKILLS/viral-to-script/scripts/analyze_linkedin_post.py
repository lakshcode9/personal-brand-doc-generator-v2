"""
LinkedIn Post Analyzer script.
Extracts structure and hooks from LinkedIn posts.
"""
import sys
import io
import json

# Fix terminal encoding issues on Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def analyze_post(content):
    """
    Simulates structural analysis of a LinkedIn post.
    In a real scenario, this helps feed the LLM prompt.
    """
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    if not lines:
        return {}
        
    analysis = {
        "hook": lines[0],
        "line_count": len(lines),
        "structure": "List" if any(l.startswith(("-", "•", "1.", "✅")) for l in lines) else "Narrative",
        "raw_text": content
    }
    return analysis

if __name__ == "__main__":
    test_content = "I dropped out of college.\nNow I build AI agents.\nHere is how I did it:\n1. Learned Python\n2. Built RAG\n3. Scaled."
    print(json.dumps(analyze_post(test_content), indent=2))
