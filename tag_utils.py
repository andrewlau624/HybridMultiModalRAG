import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

class TagsModel(BaseModel):
    tags: List[str]

def generate_tags_from_text(text: str, usage="domain") -> list[str]:
    domainPrompt = f"""
    You are an expert knowledge graph curator for a Neo4j database.

    Analyze the following text and generate between 3 and 10 short, descriptive tags (1–3 words each).
    Include a mix of:
      - **Broad tags**: general topics or domains (e.g., "Machine Learning", "Healthcare")
      - **Specific tags**: precise concepts, entities, or techniques (e.g., "Reinforcement Learning", "Neural Decoding")

    Tags should be relevant, unique, and suitable as node labels for connecting related documents in a graph database.

    Text:
    {text}
    
    Return only a JSON list of strings.
    """

    queryPrompt = f"""
    You are an expert semantic search assistant curating tags for Neo4j knowledge graph queries.

    The user has entered the following natural language query.  
    Your task is to extract **3–10 relevant search tags** (1–3 words each) representing both broad and specific concepts implied by the query.

    Tags should:
      • Reflect both general domains and precise subtopics.
      • Be suitable for matching Tag nodes in Neo4j.
      • Avoid stopwords, punctuation, or irrelevant words.
      • Be formatted as clean title-case strings (e.g., "Climate Change", "Graph Neural Networks").

    Query:
    Return only a JSON list of strings.
    {text}
    
    Return only a JSON list of strings.
    """

    response = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": domainPrompt if usage == "domain" else queryPrompt}],
        temperature=0.3,
        response_format=TagsModel
    )

    output = response.choices[0].message

    if output.refusal:
        return []
    return output.parsed.tags

