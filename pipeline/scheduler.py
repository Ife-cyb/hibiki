import time
import schedule
from loguru import logger

# Import pipeline steps
from fetcher import load_kaggle_dataset, fetch_anilist_data
from cleaner import merge_and_clean
from embedder import embed_and_store

def run_pipeline():
    logger.info("Starting scheduled Hibiki data pipeline run...")
    start_time = time.time()
    
    # Step 1: Load Kaggle Dataset
    try:
        logger.info("Step 1: Loading Kaggle Dataset...")
        kaggle_df = load_kaggle_dataset('./data')
        logger.success(f"Successfully loaded Kaggle dataset with {len(kaggle_df)} records.")
    except Exception as e:
        logger.error(f"Pipeline failed at Step 1 (Kaggle Dataset): {e}")
        return

    # Step 2: Fetch AniList Data
    try:
        logger.info("Step 2: Fetching AniList Data...")
        anilist_list = fetch_anilist_data(page=1, per_page=50)
        logger.success(f"Successfully fetched {len(anilist_list)} records from AniList.")
    except Exception as e:
        logger.error(f"Pipeline failed at Step 2 (AniList Fetch): {e}")
        return

    # Step 3: Merge and Clean
    try:
        logger.info("Step 3: Merging and Cleaning Data...")
        cleaned_df = merge_and_clean(kaggle_df, anilist_list)
        total_processed = len(cleaned_df)
        logger.success(f"Successfully merged data. Total valid records: {total_processed}.")
    except Exception as e:
        logger.error(f"Pipeline failed at Step 3 (Merge and Clean): {e}")
        return

    # Step 4: Embed and Store in ChromaDB
    try:
        logger.info("Step 4: Embedding and Storing Data...")
        new_records = embed_and_store(cleaned_df)
        # If embed_and_store doesn't return an int directly, fallback to descriptive text.
        if new_records is None:
            new_records = "check logs for exact count"
        logger.success("Successfully completed embedding step.")
    except Exception as e:
        logger.error(f"Pipeline failed at Step 4 (Embed and Store): {e}")
        return

    # Final Summary Log
    elapsed_time = time.time() - start_time
    logger.info(
        f"\n{'='*40}\n"
        f"PIPELINE RUN SUMMARY\n"
        f"{'='*40}\n"
        f"Total Records Processed : {total_processed}\n"
        f"New Records Added       : {new_records}\n"
        f"Time Elapsed            : {elapsed_time:.2f} seconds\n"
        f"{'='*40}"
    )

if __name__ == "__main__":
    # 1. Run immediately on startup
    logger.info("Initializing Hibiki ETL Pipeline...")
    run_pipeline()
    
    # 2. Schedule for every Sunday at 2:00 AM
    schedule.every().sunday.at("02:00").do(run_pipeline)
    
    logger.info("Pipeline scheduler is active. Waiting for next run (Sundays at 02:00 AM)...")
    
    # 3. Endless execution loop
    while True:
        schedule.run_pending()
        time.sleep(60)
