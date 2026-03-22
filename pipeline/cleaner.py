import pandas as pd
import uuid
from loguru import logger

def merge_and_clean(kaggle_df, anilist_list):
    """
    Transforms and merges Kaggle and AniList datasets into a unified format.
    Ensures data quality, unique IDs, and structured rich text for embeddings.
    """
    logger.info("Starting merge and clean process...")
    
    # 1. Convert AniList list to DataFrame
    anilist_df = pd.DataFrame(anilist_list)
    
    # Make sure 'genre' column is consistent (fetcher used 'genre', but we asked for genres)
    if 'genre' in anilist_df.columns and 'genre' not in kaggle_df.columns:
        # Assuming kaggle_df has 'genres' instead, or vice versa. 
        # But instructions said fetcher created matching schema to Kaggle.
        pass
    
    # 2. Merge both DataFrames
    merged_df = pd.concat([kaggle_df, anilist_df], ignore_index=True)
    initial_count = len(merged_df)
    logger.info(f"Total records before deduplication: {initial_count}")
    
    # Deduplicate by title (case-insensitive)
    merged_df['title'] = merged_df['title'].fillna('')
    merged_df['title_lower'] = merged_df['title'].str.lower()
    merged_df = merged_df.drop_duplicates(subset=['title_lower'], keep='first')
    merged_df = merged_df.drop(columns=['title_lower'])
    
    dedup_count = len(merged_df)
    logger.info(f"Total records after deduplication: {dedup_count} (removed {initial_count - dedup_count})")
    
    # 3. Create 'rich_text' column
    # Safely fill NaNs for text columns before concatenation
    merged_df['genre'] = merged_df.get('genre', pd.Series([''] * len(merged_df))).fillna('')
    merged_df['synopsis'] = merged_df.get('synopsis', pd.Series([''] * len(merged_df))).fillna('')
    
    merged_df['rich_text'] = (
        "Title: " + merged_df['title'] + 
        ". Genres: " + merged_df['genre'] + 
        ". " + merged_df['synopsis']
    )
    
    # 4. Normalize scores to a 0-1 range (Min-Max scaling)
    merged_df['score'] = pd.to_numeric(merged_df.get('score', 0), errors='coerce').fillna(0)
    min_score = merged_df['score'].min()
    max_score = merged_df['score'].max()
    if max_score > min_score:
        merged_df['score'] = (merged_df['score'] - min_score) / (max_score - min_score)
    else:
        merged_df['score'] = 0.0
        
    # 5. Remove any anime with missing rich_text or image_url
    merged_df['image_url'] = merged_df.get('image_url', pd.Series([''] * len(merged_df))).fillna('')
    
    # We consider empty strings as "missing" as well
    valid_mask = (merged_df['image_url'].str.strip() != '') & (merged_df['rich_text'].str.strip() != '')
    merged_df = merged_df[valid_mask]
    
    clean_count = len(merged_df)
    logger.info(f"Records remaining after cleaning missing text/images: {clean_count}")
    
    # 6. Add unique 'anime_id'
    merged_df['anime_id'] = [str(uuid.uuid4()) for _ in range(len(merged_df))]
    
    logger.success(f"Successfully cleaned and merged data. Final count: {clean_count}")
    return merged_df
