"""
ChromaDB operations module.
Handles initializing the persistent vector database, populating it with
historical sports facts, and querying it with semantic search.
"""

import os
import json
import chromadb
from chromadb.utils import embedding_functions

from src.config import CHROMA_DB_PATH, DATA_FILE_PATH


def get_chroma_client():
    """Initializes and returns a persistent ChromaDB client saving to disk."""
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)


def _get_embedding_function():
    """Returns the default sentence-transformer embedding function."""
    return embedding_functions.DefaultEmbeddingFunction()


def setup_and_populate_db(json_file_path=None):
    """
    Reads the offline JSON facts, creates a ChromaDB collection, and populates it.
    Idempotent: skips insertion if the collection already contains data.

    Args:
        json_file_path: Path to the sports_facts.json file.
                        Defaults to DATA_FILE_PATH from config.

    Returns:
        The ChromaDB collection object.
    """
    if json_file_path is None:
        json_file_path = DATA_FILE_PATH

    client = get_chroma_client()
    embedding_fn = _get_embedding_function()

    # Get or create the collection
    collection = client.get_or_create_collection(
        name="sports_history",
        embedding_function=embedding_fn,
    )

    # Skip if already populated
    if collection.count() > 0:
        print(f"[INFO] Database already populated with {collection.count()} facts.")
        return collection

    # Validate data file exists
    if not os.path.exists(json_file_path):
        print(f"[ERROR] Data file not found at {json_file_path}")
        return collection

    # Load facts from JSON
    with open(json_file_path, "r", encoding="utf-8") as f:
        facts_list = json.load(f)

    documents = []
    metadata_list = []
    ids = []

    for idx, item in enumerate(facts_list):
        documents.append(item["fact"])
        # Metadata enables filtered queries by sport
        metadata_list.append({"sport": item["sport"]})
        ids.append(f"fact_{idx}")

    # Bulk insert into ChromaDB
    collection.add(
        documents=documents,
        metadatas=metadata_list,
        ids=ids,
    )
    print(f"[SUCCESS] Successfully vectorized and stored {len(documents)} facts.")
    return collection


def query_historic_facts(sport, query_text, n_results=3):
    """
    Searches ChromaDB for historic documents related to a specific sport.

    Args:
        sport:      The sport category to filter on (e.g. "Cricket").
        query_text: The semantic search query string.
        n_results:  Number of results to return.

    Returns:
        A list of matching document strings.
    """
    client = get_chroma_client()
    embedding_fn = _get_embedding_function()

    collection = client.get_or_create_collection(
        name="sports_history",
        embedding_function=embedding_fn,
    )

    if collection.count() == 0:
        print("[WARNING] ChromaDB collection is empty. Run setup_and_populate_db() first.")
        return []

    # Semantic query with metadata filter
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results,
        where={"sport": sport},
    )

    return results.get("documents", [[]])[0]
