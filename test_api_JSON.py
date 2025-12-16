import requests
import json

# --- CONFIGURATION ---
URL = "https://ted-rag-assignment-ruby.vercel.app/api/prompt"

# Extended Test Cases (2 per category)
test_cases = [
    # TYPE 1: Precise Fact Retrieval [cite: 13]
    {
        "category": "1. Precise Fact Retrieval",
        "question": "Find a TED talk that discusses overcoming fear or anxiety. Provide the title and speaker."
    },
    {
        "category": "1. Precise Fact Retrieval",
        "question": "Who gave the talk titled 'The power of vulnerability'? Provide the speaker name and the year it was filmed."
    },

    # TYPE 2: Multi-Result Topic Listing [cite: 17]
    {
        "category": "2. Multi-Result Topic Listing",
        "question": "Which TED talk focuses on education or learning? Return a list of exactly 3 talk titles."
    },
    {
        "category": "2. Multi-Result Topic Listing",
        "question": "List exactly 3 TED talks that discuss Artificial Intelligence or robots."
    },

    # TYPE 3: Key Idea Summary Extraction [cite: 22]
    {
        "category": "3. Key Idea Summary",
        "question": "Find a TED talk where the speaker talks about technology improving people's lives. Provide the title and a short summary of the key idea."
    },
    {
        "category": "3. Key Idea Summary",
        "question": "Provide a summary of the main idea in the talk 'How great leaders inspire action'."
    },

    # TYPE 4: Recommendation with Justification [cite: 26]
    {
        "category": "4. Recommendation",
        "question": "I'm looking for a TED talk about climate change and what individuals can do in their daily lives. Which talk would you recommend?"
    },
    {
        "category": "4. Recommendation",
        "question": "I am an introvert and feel out of place in social situations. Recommend a relevant talk and explain why it fits my situation."
    }
]

# Run Tests
for i, case in enumerate(test_cases):
    print(f"--- TEST {i+1} ({case['category']}) ---")
    
    # Construct Payload
    payload = {"question": case["question"]}
    
    # Print Request
    print("REQUEST:")
    print(json.dumps(payload, indent=4))
    
    try:
        # Send Request
        response = requests.post(URL, json=payload)
        
        # Print Response
        print("\nRESPONSE:")
        if response.status_code == 200:
            # Parse and re-dump to ensure strict JSON formatting in output
            data = response.json()
            print(json.dumps(data, indent=4))
        else:
            print(f"Error Code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Connection Error: {e}")
        
    print("\n" + "="*50 + "\n")