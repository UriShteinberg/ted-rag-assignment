import pandas as pd
from pinecone import Pinecone
from openai import OpenAI
import time
import os

# --- 1. CONFIGURATION ---
# PASTE YOUR KEYS HERE FOR LOCAL RUNNING
LLMOD_API_KEY = os.environ.get("LLMOD_API_KEY")
LLMOD_BASE_URL = "https://api.llmod.ai" # Check your platform for the exact URL
PINECONE_KEY = os.environ.get("PINECONE_API_KEY")

# Constants
INDEX_NAME = "ted-rag"
EMBEDDING_MODEL = "RPRTHPB-text-embedding-3-small" # 
CHUNK_SIZE = 1000
OVERLAP = 100

# SAFETY LOCK: Only process 20 talks first to save your $5 budget! [cite: 36, 39]
LIMIT_TALKS = None  # Set to None only when ready for the full upload

# --- 2. SETUP CLIENTS ---
# We use base_url to point to the university platform instead of OpenAI directly
client = OpenAI(api_key=LLMOD_API_KEY, base_url=LLMOD_BASE_URL)
pc = Pinecone(api_key=PINECONE_KEY)
index = pc.Index(INDEX_NAME)

def get_embedding(text):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=EMBEDDING_MODEL).data[0].embedding

def chunk_text(text, chunk_size, overlap):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# --- 3. PROCESS DATA ---
print("Loading data...")
df = pd.read_csv('ted_talks_en.csv')

if LIMIT_TALKS:
    df = df.head(LIMIT_TALKS)
    print(f"⚠️ SAFETY MODE: Processing only {LIMIT_TALKS} talks.")

vectors = []
for i, row in df.iterrows():
    # New Line (Includes Date and Views for fact retrieval)
    context = f"Title: {row['title']}\nSpeaker: {row['speaker_1']}\nDate: {row['published_date']}\nViews: {row['views']}\nTopics: {row['topics']}\nTranscript: {row['transcript']}"
    
    chunks = chunk_text(context, CHUNK_SIZE, OVERLAP)
    
    for idx, chunk_text_content in enumerate(chunks):
        try:
            # Generate Embedding (This costs money!)
            vector_values = get_embedding(chunk_text_content)
            
            # Prepare Metadata
            metadata = {
                "talk_id": str(row['talk_id']),
                "title": str(row['title']),
                "chunk": chunk_text_content
            }
            
            vectors.append({
                "id": f"{row['talk_id']}_{idx}",
                "values": vector_values,
                "metadata": metadata
            })
        except Exception as e:
            print(f"Error on row {i}: {e}")

    # Upload in batches of 50
    if len(vectors) >= 50:
        index.upsert(vectors)
        vectors = []
        print(f"Uploaded batch... (at row {i})")

# Final upload
if vectors:
    index.upsert(vectors)
    print("Done!")