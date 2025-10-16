# HybridMultiModalRAG

AI-powered **Multimodal Retrieval-Augmented Generation (RAG)** system for enterprise knowledge graphs.  
Supports ingestion of **text, PDF, images, audio**, builds a **Neo4j knowledge graph**, and enables **hybrid search** using both keyword and vector retrieval.

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/andrewlau624/HybridMultiModalRAG
cd HybridMultiModalRAG
```
### **2. Install Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### **3. Configure Environment Variables**
Create a .env file in the root directory:
```ini
OPENAI_API_KEY=sk-<your-openai-key>
```

Get your OpenAI API key from https://platform.openai.com/api-keys

### **4. Run Databases with Docker**
Qdrant (Vector Database)
```bash
docker run -p 6333:6333 qdrant/qdrant
```

Maps local port 6333 to Qdrant API.

Access API at: http://localhost:6333.

Neo4j (Knowledge Graph)

```bash
docker run -d \
  --name neo4j \
  --restart=always \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  -v $HOME/neo4j/data:/data \
  neo4j:latest
```

Access Neo4j Browser at: http://localhost:7474

Bolt protocol port for Python: 7687

Tip: Start Qdrant first, then Neo4j.

### **5. Running the Streamlit App**
```bash
streamlit run app.py
```

### **6. Upload Files and Run Query**

#### Upload Files
- Click the **“Browse files”** button in the Streamlit app.  
- Supported file types:
  - **Text:** `.txt`, `.pdf`
  - **Images:** `.jpg`, `.png`
  - **Audio:** `.mp3`

The system will process each file:  
- **Text/PDF:** extract content  
- **Images:** OCR / captioning  
- **Audio:** transcription  

#### Enter a Query
- Type a natural language query in the input box.  
- Example queries:
  - `"Summarize the document"`  
  - `"List all entities mentioned in the PDF"`  
  - `"Show connections between John Smith and projects"`  

#### Run Query
- Press the **“Run Query”** button.  
- The system performs a **hybrid search**:
  - Keyword matching in the knowledge graph  
  - Semantic vector search via Qdrant  
- Results are displayed in the app:
  - Summarized answers  
