import requests
import json

API_KEY = "fe9d2ce62a5ef406bb796c402f9cc3458e6aeba4"
url = "https://api.indiankanoon.org/search/"

headers = {
    "Authorization": f"Token {API_KEY}",
    "Accept": "application/json"
}

test_queries = [
    "IPC 302 murder",
    "article 21 constitution india",
    "dowry harassment 498A",
    "right to privacy judgement",
    "stalking"
]

print(f"=== TESTING INDIAN KANOON API WITH CORRECTED KEY 'docs' ===\n")

for query in test_queries:
    print(f"Testing Query: '{query}'")
    try:
        # Using data= for POST form-encoded payload
        response = requests.post(url, data={"formInput": query}, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Verified correct key is 'docs', not 'results'
            docs = data.get("docs", [])
            print(f"  Status: 200 OK")
            print(f"  Results Found: {len(docs)}")
            if docs:
                print(f"  Top Title: {docs[0].get('title')}")
        else:
            print(f"  Status: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"  Exception: {str(e)}")
    print("-" * 40)