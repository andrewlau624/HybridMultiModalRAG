import os
import datetime
import whisper
import pytesseract
from PIL import Image
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from qdrant_utils import ingest_docs
from neo4j_utils import ingest_to_neo4j, add_domain_tags
from tag_utils import generate_tags_from_text

# Directory to save all text files
DOCUMENTS_DIR = "./uploaded_files"
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

def save_text_file(text, original_name):
    base_name = os.path.splitext(original_name)[0]
    txt_path = os.path.join(DOCUMENTS_DIR, f"{base_name}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    return txt_path

def process(file):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)

    # Convert file to text
    if file.type.startswith("image"):
        text = pytesseract.image_to_string(Image.open(file))
    elif file.type.startswith("audio"):
        tmp_path = os.path.join(DOCUMENTS_DIR, f"temp_{file.name}")
        with open(tmp_path, "wb") as f:
            f.write(file.read())
        model = whisper.load_model("base")
        text = model.transcribe(tmp_path)["text"]
        os.remove(tmp_path)
    elif file.type == "application/pdf":
        tmp_path = os.path.join(DOCUMENTS_DIR, f"temp_{file.name}")
        with open(tmp_path, "wb") as f:
            f.write(file.read())
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        text = "\n\n".join([d.page_content for d in docs])
        os.remove(tmp_path)
    else:
        text = file.read().decode("utf-8")

    # Save as text file
    txt_path = save_text_file(text, file.name)

    # Create langchain Document
    document = Document(
        page_content=text,
        metadata={
            "source": txt_path,
            "type": "text/plain",
            "length": len(text),
            "processed_at": datetime.datetime.now().isoformat()
        }
    )

    # Split document into chunks
    documents = splitter.split_documents([document])

    # Upload to Qdrant and Neo4j
    ingest_docs(documents)
    ingest_to_neo4j(documents)

    # Generate tags from first few chunks
    combined_text = " ".join([d.page_content for d in documents[:3]])
    tags = generate_tags_from_text(combined_text)

    # Add domain tags to first document
    from neo4j_utils import driver
    with driver.session() as session:
        add_domain_tags(session, txt_path, tags)

    return [documents, "File Uploaded!"]
