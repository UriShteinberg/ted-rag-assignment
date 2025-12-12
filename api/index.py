from flask import Flask, request, jsonify
from openai import OpenAI
from pinecone import Pinecone
import os

app = Flask(__name__)

# --- CONFIGURATION ---
# [cite_start]The assignment requires specific model names [cite: 33, 34]
EMBEDDING_MODEL = "RPRTHPB-text-embedding-3-small"
CHAT_MODEL = "RPRTHPB-gpt-5-mini"

# Hyperparameters (Must match what you used in Ingest)
STATS = {
    "chunk_size": 1000,
    "overlap_ratio": 0.1,
    "top_k": 15
}

# [cite_start]Strict System Prompt from Assignment [cite: 48-52]
SYSTEM_PROMPT = """You are a TED Talk assistant that answers questions strictly and 
only based on the TED dataset context provided to you (metadata 
and transcript passages). You must not use any external 
knowledge, the open internet, or information that is not explicitly 
contained in the retrieved context. If the answer cannot be 
determined from the provided context, respond: "I don't know 
based on the provided TED data." Always explain your answer 
using the given context, quoting or paraphrasing the relevant 
transcript or metadata when helpful."""

def get_clients():
    # Connect to University Platform
    client = OpenAI(
        api_key=os.environ.get("LLMOD_API_KEY"), 
        base_url="https://api.llmod.ai" 
    )
    # Connect to Pinecone
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    index = pc.Index("ted-rag")
    return client, index

@app.route('/api/stats', methods=['GET'])
def stats():
    # [cite_start]Returns the configuration as strict JSON [cite: 90-96]
    return jsonify(STATS)

@app.route('/api/prompt', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get("question", "")
        
        client, index = get_clients()

        # 1. Embed the Question
        # We need to vector-search the user's question to find relevant talks
        q_embedding = client.embeddings.create(
            input=[question], 
            model=EMBEDDING_MODEL
        ).data[0].embedding
        
        # 2. Search Pinecone
        # [cite_start]We retrieve the top 5 most similar chunks [cite: 44]
        results = index.query(
            vector=q_embedding, 
            top_k=STATS["top_k"], 
            include_metadata=True
        )
        
        # 3. Build Context for the AI
        context_list = []
        context_text = ""
        
        for match in results['matches']:
            meta = match['metadata']
            
            # [cite_start]Format strictly for the output JSON [cite: 72-78]
            context_list.append({
                "talk_id": meta.get('talk_id', "N/A"),
                "title": meta.get('title', "N/A"),
                "chunk": meta.get('chunk', ""),
                "score": match['score']
            })
            
            # Append to the string the AI actually reads
            context_text += f"---\nTitle: {meta.get('title')}\nSpeaker: {meta.get('speaker')}\nContent: {meta.get('chunk')}\n"

        # 4. Construct Final Prompt
        final_user_message = f"Context:\n{context_text}\n\nQuestion: {question}"
        
        # 5. Call Chat Model
        completion = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": final_user_message}
            ]
        )
        
        response_text = completion.choices[0].message.content

        # [cite_start]6. Return Strict JSON Response [cite: 69-85]
        return jsonify({
            "response": response_text,
            "context": context_list,
            "Augmented_prompt": {
                "System": SYSTEM_PROMPT,
                "User": final_user_message
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# This allows you to run the server locally for testing
if __name__ == "__main__":
    app.run(debug=True, port=3000)