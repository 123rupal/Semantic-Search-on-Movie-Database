import pymongo
import requests
import creds

client=pymongo.MongoClient(creds.mongodb_serv)
db=client.sample_mflix
collection=db.movies

embedding_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"

def generate_embedding(text: str) -> list[float]:

  response = requests.post(
    embedding_url,
    headers={"Authorization": f"Bearer {creds.hf_token}"},
    json={"inputs": text})

  if response.status_code != 200:
    raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")

  return response.json()

'''for doc in collection.find({'plot':{"$exists": True}}).limit(50):
    doc['plot_embedding_hf'] = generate_embedding(doc['plot'])
    collection.replace_one({'_id': doc['_id']}, doc)'''

query="Imaginary characters from outer space at war."

res = collection.aggregate([
    {
        "$vectorSearch": {
            "queryVector": generate_embedding(query),
            "path": "plot_embedding_hf",
            "numCandidates": 100,
            "limit": 4,
            "index": "PlotSemanticSearch",
        }
    }
])

for d in res:
    print(f'Movie Name: {d["title"]},\nMovie Plot: {d["plot"]}\n')