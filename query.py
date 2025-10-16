import os

from dotenv import load_dotenv
from openai import OpenAI
from neo4j_utils import semantic_search
from qdrant_utils import vector_search

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def fetch_query(query):
    qdrant_results = vector_search(query)
    neo4j_results = semantic_search(query)

    qdrant_texts = "\n\n".join(load_qdrant_txt(qdrant_results.points))
    neo4j_texts = "\n\n".join(load_neo4j_txt(neo4j_results))

    prompt = f"""
You are an intelligent retrieval agent in a Hybrid RAG system combining:
1. Vector Search (Qdrant) — retrieves semantically similar content chunks.
2. Graph Search (Neo4j) — retrieves documents and entities via knowledge graph tags.

Your task:
- Combine and interpret the following search results.
- Identify the most relevant and non-redundant information.
- Provide a concise, factual, and well-structured answer to the user query.
- If the results conflict, prioritize the Neo4j knowledge graph for factual consistency.
- If no strong matches exist, state that clearly.

User Query:
{query}

Vector Search Results (Qdrant):
{qdrant_texts}

Graph Search Results (Neo4j):
{neo4j_texts}

Your output should be:
1. A short paragraph answering the query.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content

def load_qdrant_txt(points, max_chars=2000):
    texts = []
    seen_sources = set()

    for p in points:
        payload = p.payload
        source = payload.get("source")
        ftype = payload.get("type", "text/plain")

        if ftype != "text/plain" or not source or source in seen_sources:
            continue

        seen_sources.add(source)
        try:
            with open(source, "r", encoding="utf-8") as f:
                texts.append(f.read()[:max_chars])
        except Exception as e:
            texts.append(f"[Unable to load {source}: {e}]")

    return texts

def load_neo4j_txt(results, max_chars=2000):
    texts = []
    seen_sources = set()

    for r in results:
        source = r.get("source")
        ftype = r.get("type", "text/plain")

        if ftype != "text/plain" or not source or source in seen_sources:
            continue

        seen_sources.add(source)

        try:
            with open(source, "r", encoding="utf-8") as f:
                texts.append(f.read()[:max_chars])
        except Exception as e:
            texts.append(f"[Unable to load {source}: {e}]")

    return texts