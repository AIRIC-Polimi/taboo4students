from dotenv import load_dotenv
from openai import AzureOpenAI
import json
import numpy as np
from pathlib import Path
import os


def main():
    # Config
    load_dotenv()

    repo_folder = Path(__file__).parent.parent
    path_db = os.environ.get("PATH_DB", str(repo_folder / "data" / "level4_data" / "hints_db.json"))
    path_hints = os.environ.get("PATH_HINTS", str(repo_folder / "data" / "level4_data" / "hints.txt"))
    client = AzureOpenAI()

    # Read hints
    with open(path_hints, "r", encoding="utf-8") as f:
        hints = [line.strip() for line in f if line.strip()]

    # Create the vector_store
    vector_store: dict[str, list[float]] = {}

    # Add the hints to the vector_store
    for i, hint in enumerate(hints):
        response = client.embeddings.create(input=hint, model="text-embedding-3-large")
        print(f"Adding hint {i} to db...")
        vector_store[hint] = response.data[0].embedding
        print(f"DONE: Added hint {i} to db...")

    # Save vector_store as json file
    with open(path_db, "w", encoding="utf-8") as f:
        json.dump(vector_store, f)

    # Reload vector_store
    with open(path_db, "r", encoding="utf-8") as f:
        vector_store = json.load(f)

    # Define similarity search function
    def custom_similarity_search(
        query: str, client: AzureOpenAI, vector_store: dict[str, list[float]], k: int = 1
    ) -> list[str]:
        # Get the embedding for the query
        result = client.embeddings.create(input=query, model="text-embedding-3-large")
        query_embedding = result.data[0].embedding
        # Calculate the cosine similarity
        similarities = []
        for hint, embedding in vector_store.items():
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities.append((hint, similarity))
        # Get the top k hints
        top_k_hints = sorted(similarities, key=lambda x: x[1], reverse=True)[:k]
        # Return the hints
        return [hint for hint, _ in top_k_hints]

    # Test the vector_store
    query = "medico"
    results = custom_similarity_search(query, client, vector_store, k=3)
    print(f"Testing the vector store with a similarity search for the word '{query}'")
    print("\n🔎 Top matches for query:")
    for i, doc in enumerate(results):
        print(f"{i}. {doc}")


if __name__ == "__main__":
    main()
