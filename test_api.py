import requests
import json

# --- CONFIGURATION ---
URL = "https://ted-rag-assignment-ruby.vercel.app/api/prompt" 

test_cases = [
    {
        "type": "1. Precise Fact Retrieval",
        "goal": "Locate a specific entity/fact",
        "question": "Find a TED talk that discusses overcoming fear or anxiety. Provide the title and speaker."
    },
    {
        "type": "2. Multi-Result Topic Listing",
        "goal": "List exactly 3 titles",
        "question": "Which TED talk focuses on education or learning? Return a list of exactly 3 talk titles."
    },
    {
        "type": "3. Key Idea Summary",
        "goal": "Summarize a key idea",
        "question": "Find a TED talk where the speaker talks about technology improving people's lives. Provide the title and a short summary of the key idea."
    },
    {
        "type": "4. Recommendation",
        "goal": "Recommend with justification",
        "question": "I'm looking for a TED talk about climate change and what individuals can do in their daily lives. Which talk would you recommend?"
    }
]

print(f"🚀 Starting Test Suite on: {URL}\n")

for test in test_cases:
    print("="*60)
    print(f"🧪 TEST TYPE: {test['type']}")
    print(f"🎯 GOAL: {test['goal']}")
    print(f"❓ QUESTION: \"{test['question']}\"")
    print("-" * 60)

    try:
        # Send Request
        response = requests.post(URL, json={"question": test['question']})
        
        # Check Status
        if response.status_code == 200:
            data = response.json()
            
            # 1. Print Technical Status
            print(f"✅ STATUS: 200 OK")
            
            # 2. Print The AI's Answer
            print("\n🤖 AI RESPONSE:")
            print(data['response'])
            
            # 3. Print Validation Data (Sources)
            print("\n📚 SOURCE EVIDENCE:")
            if data.get('context'):
                # Print just the first source to prove it retrieved something
                first_source = data['context'][0]
                print(f"   [Source 1] Title: {first_source.get('title', 'N/A')}")
                print(f"   [Source 1] Score: {first_source.get('score', 'N/A')}")
                print(f"   (Total Sources Retrieved: {len(data['context'])})")
            else:
                print("   ⚠️ WARNING: No context chunks returned!")

        else:
            print(f"❌ ERROR: Status Code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
    
    print("\n") # Spacing between tests

print("="*60)
print("🏁 Test Suite Completed.")