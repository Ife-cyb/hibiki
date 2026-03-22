import os
from dotenv import load_dotenv
from loguru import logger
from sentence_transformers import SentenceTransformer
import chromadb

# Load environment variables
load_dotenv()

def embed_and_store(df):
    """
    Embeds rich text representations of anime and stores them in ChromaDB 
    along with associated metadata for semantic search. Incremental update.
    """
    logger.info("Loading sentence-transformers model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    db_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    logger.info(f"Connecting to ChromaDB at {db_path}...")
    client = chromadb.PersistentClient(path=db_path)
    
    collection = client.get_or_create_collection(name="hibiki_anime")
    
    # Check for existing IDs to support incremental updates
    existing_data = collection.get(include=[])
    existing_ids = set(existing_data['ids'])
    
    df_new = df[~df['anime_id'].isin(existing_ids)]
    new_records = len(df_new)
    
    if new_records == 0:
        logger.info("All records already exist in ChromaDB. Nothing to do.")
        return 0
        
    logger.info(f"Found {new_records} new records to embed and store (Skipped {len(df) - new_records} existing).")
    
    batch_size = 64
    total_stored = 0
    
    for i in range(0, new_records, batch_size):
        batch = df_new.iloc[i:i + batch_size]
        
        texts_to_embed = batch['rich_text'].tolist()
        ids = batch['anime_id'].tolist()
        
        # Prepare metadata (ensure pure types for ChromaDB)
        metadatas = []
        for _, row in batch.iterrows():
            metadatas.append({
                "title": str(row.get('title', '')),
                "score": float(row.get('score', 0.0)),
                "image_url": str(row.get('image_url', '')),
                "synopsis": str(row.get('synopsis', '')),
                "genre": str(row.get('genre', '')),
                "type": str(row.get('type', '')),
                "episodes": int(row.get('episodes', 0))
            })
            
        logger.info(f"Encoding batch {i//batch_size + 1}/{(new_records + batch_size - 1)//batch_size}...")
        embeddings = model.encode(texts_to_embed, batch_size=batch_size, show_progress_bar=False).tolist()
        
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=texts_to_embed,
            metadatas=metadatas
        )
        
        total_stored += len(ids)
        logger.info(f"Stored {total_stored}/{new_records} records.")
        
    logger.success(f"Finished embedding and storing {total_stored} records to 'hibiki_anime' collection.")
    return total_stored
