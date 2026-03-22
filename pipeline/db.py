import os
import sys
from dotenv import load_dotenv
from loguru import logger
from sentence_transformers import SentenceTransformer
import chromadb

load_dotenv()

# Cache model and collection globally so FastAPIs don't reload them on every single request
_model = None
_collection = None

def get_model():
    global _model
    if _model is None:
        logger.info("Loading sentence-transformers model 'all-MiniLM-L6-v2'...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_collection():
    global _collection
    if _collection is None:
        # 1) Check for Railway environment to utilize persistent volumes
        if os.environ.get("RAILWAY_ENVIRONMENT"):
            # IMPORTANT: In the Railway Dashboard, you must attach a volume
            # mounted at /data so the ChromaDB database survives container redeployments!
            db_path = "/data/chroma_db"
            # Override env variable so other modules like embedder.py use the correct path
            os.environ["CHROMA_DB_PATH"] = db_path
        else:
            db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
            
        logger.info(f"Connecting to ChromaDB search collection at {db_path}...")
        client = chromadb.PersistentClient(path=db_path)
        _collection = client.get_or_create_collection(name="hibiki_anime")
        
        # 2) Fallback pre-population mechanism on first deployment 
        if _collection.count() == 0:
            logger.warning("ChromaDB is empty! Pre-populating with minimum 50 records so app isn't blank...")
            try:
                import pandas as pd
                # Safely ensure local imports work regardless of execution context
                sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
                try:
                    from pipeline.fetcher import fetch_anilist_data
                    from pipeline.cleaner import merge_and_clean
                    from pipeline.embedder import embed_and_store
                except ModuleNotFoundError:
                    # Fallback if running directly inside pipeline/ folder
                    from fetcher import fetch_anilist_data
                    from cleaner import merge_and_clean
                    from embedder import embed_and_store

                # Fetch 50 initial fallback records directly from AniList 
                anilist_data = fetch_anilist_data(page=1, per_page=50)
                
                # Mock an empty Kaggle DataFrame to satisfy the merge_and_clean function signature
                empty_kaggle = pd.DataFrame(columns=["title", "synopsis", "genre", "score", "image_url", "type", "episodes"])
                
                # Process the data identically to normal pipeline
                cleaned_df = merge_and_clean(empty_kaggle, anilist_data)
                
                logger.info(f"Embedding and storing {len(cleaned_df)} fallback records...")
                embed_and_store(cleaned_df)
                
                logger.success("Fallback pre-population sequence complete. DB is now hydrated via fallback.")
                
            except Exception as e:
                logger.error(f"Failed to execute database pre-population: {e}")

    return _collection

def search_anime(query: str, n_results: int = 6) -> list:
    """
    Search function intended for API consumption.
    Embeds the user query, does a vector search in ChromaDB, and returns normalized results.
    """
    try:
        model = get_model()
        collection = get_collection()

        logger.info(f"Performing semantic search for: '{query}'")
        
        # 1. Embed query
        query_embedding = model.encode(query).tolist()

        # 2. Query ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        formatted_results = []
        if not results['ids'] or not results['ids'][0]:
            logger.warning("No results found in ChromaDB collection.")
            return formatted_results

        metadatas = results['metadatas'][0]
        distances = results['distances'][0]

        # 3. Format output
        for anime_id, meta, dist in zip(results['ids'][0], metadatas, distances):
            # Convert ChromaDB distance into a rough 0-100% match score 
            # (Works reasonably well mapping typical L2/Cosine distances from SentenceTransformers)
            # Normalizing so it caps properly between 0-100
            match_percentage = min(100.0, max(0.0, (1.0 - (dist / 2.0)) * 100.0))

            formatted_results.append({
                "anime_id": anime_id,
                "title": meta.get("title", "Unknown"),
                "synopsis": meta.get("synopsis", ""),
                "image_url": meta.get("image_url", ""),
                "score": round(float(meta.get("score", 0.0)), 2),
                "match_percentage": round(match_percentage, 1)
            })

        logger.success(f"Returned {len(formatted_results)} results for query '{query}'")
        return formatted_results

    except Exception as e:
        logger.error(f"Error executing search_anime: {e}")
        return []
