import datetime

from neo4j import GraphDatabase

from tag_utils import generate_tags_from_text

URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password123")

driver = GraphDatabase.driver(URI, auth=AUTH)

# Create document node with basic metadata
def create_document_node(session, metadata):
    query = """
    MERGE (d:Document {source: $source})
    SET d.type = coalesce($type, 'unknown'),
        d.length = coalesce($length, 0),
        d.processed_at = datetime(coalesce($processed_at, datetime()))
    RETURN d
    """

    safe_metadata = {
        "source": metadata.get("source", "unknown"),
        "type": metadata.get("type", "text/plain"),
        "length": metadata.get("length", 0),
        "processed_at": metadata.get("processed_at", datetime.datetime.now().isoformat())
    }

    session.run(query, safe_metadata)

# Upload documents to neo4j
def ingest_to_neo4j(documents):
    with driver.session() as session:
        for doc in documents:
            metadata = doc.metadata
            create_document_node(session, metadata)

# Create a tag node
def create_tag_node(session, tag):
    query = """
    MERGE (t:Tag {name: $tag})
    RETURN t
    """
    session.run(query, {"tag": tag})

# Create a connection between document and tag
def connect_doc_to_tag(session, doc_source, tag):
    query = """
    MATCH (d:Document {source: $doc_source})
    MATCH (t:Tag {name: $tag})
    MERGE (d)-[:HAS_TAG]->(t)
    """
    session.run(query, {"doc_source": doc_source, "tag": tag})

# For each tag, create a tag and connect it to the corresponding document
def add_domain_tags(session, doc_source, tags):
    for tag in tags:
        create_tag_node(session, tag)
        connect_doc_to_tag(session, doc_source, tag)


def search_documents_by_tag(session, tag):
    query = """
    MATCH (d:Document)-[:HAS_TAG]->(t:Tag)
    WHERE toLower(t.name) CONTAINS toLower($tag)
    RETURN d.source AS source,
           d.type AS type,
           d.length AS length,
           d.processed_at AS processed_at,
           collect(DISTINCT t.name) AS tags
    """
    result = session.run(query, {"tag": tag})
    return [record.data() for record in result]

def semantic_search(query):
    tags = generate_tags_from_text(query, usage="query")

    if not tags:
        return []

    all_results = []
    seen_sources = set()

    with driver.session() as session:
        for tag in tags:
            results = search_documents_by_tag(session, tag)
            for record in results:
                src = record["source"]
                if src not in seen_sources: # Avoid duplicate documents
                    seen_sources.add(src)
                    record["matched_tag"] = tag
                    all_results.append(record)
    return all_results
