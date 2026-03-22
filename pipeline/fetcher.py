import os
import pandas as pd
from loguru import logger
import kaggle
from dotenv import load_dotenv

load_dotenv()

def load_kaggle_dataset(download_dir='./data') -> pd.DataFrame:
    """
    Downloads the MyAnimeList dataset from Kaggle, loads the specific 
    animes.csv file, and performs basic cleaning and filtering.
    """
    dataset_name = "marlesson/myanimelist-dataset-animes-profiles-reviews"
    csv_filename = "animes.csv"
    csv_filepath = os.path.join(download_dir, csv_filename)

    # Note: Requires Kaggle API credentials either in the environment 
    # (KAGGLE_USERNAME, KAGGLE_KEY) or inside ~/.kaggle/kaggle.json

    if not os.path.exists(csv_filepath):
        logger.info(f"Downloading dataset '{dataset_name}' to '{download_dir}'...")
        try:
            kaggle.api.dataset_download_files(dataset_name, path=download_dir, unzip=True)
            logger.success("Download and extraction complete.")
        except Exception as e:
            logger.error(f"Failed to download dataset from Kaggle: {e}")
            raise
    else:
        logger.info(f"Dataset already found at '{csv_filepath}'. Skipping download.")

    logger.info("Loading animes.csv into pandas DataFrame...")
    try:
        df = pd.read_csv(csv_filepath)
    except FileNotFoundError:
        logger.error(f"File not found: {csv_filepath}")
        raise
    
    logger.info(f"Raw DataFrame loaded with {len(df)} rows.")

    # Select only required columns (handling capitalization based on typical dataset schemas)
    required_cols = ['title', 'synopsis', 'genre', 'score', 'episodes', 'type', 'img_url']
    
    # Check what columns we actually have, just in case 'img_url' is named 'image_url' natively
    if 'img_url' in df.columns and 'image_url' not in df.columns:
        df = df.rename(columns={'img_url': 'image_url'})
        
    actual_cols = ['title', 'synopsis', 'genre', 'score', 'episodes', 'type', 'image_url']
    
    missing_cols = [col for col in required_cols if col not in df.columns and col != 'img_url']
    if missing_cols:
        logger.warning(f"Missing expected columns in dataset: {missing_cols}")

    # Keep only target columns, ignore those that truly aren't there
    keep_cols = [col for col in actual_cols if col in df.columns]
    df = df[keep_cols]

    logger.info("Filtering out empty or short synopses...")
    
    # Drop rows where synopsis is entirely null
    initial_count = len(df)
    df = df.dropna(subset=['synopsis'])
    
    # Ensure they are strings, then drop those less than 50 characters
    df['synopsis'] = df['synopsis'].astype(str)
    df = df[df['synopsis'].str.len() >= 50]
    
    final_count = len(df)
    logger.success(f"Cleaning complete! Dropped {initial_count - final_count} invalid rows.")
    logger.info(f"Final dataset ready with {final_count} curated anime entries.")
    
    return df

if __name__ == "__main__":
    df = load_kaggle_dataset()
    logger.info(f"Sample data:\n{df.head(2)}")

import time
import requests

def fetch_anilist_data(page=1, per_page=50) -> list:
    """
    Fetches anime data from the AniList GraphQL API directly, automatically 
    paginating until all requested records are retrieved. 
    Maintains a standard 1-second rate limit between calls.
    Returns data normalized to match the Kaggle DataFrame schema.
    """
    url = os.getenv("ANILIST_API_URL", "https://graphql.anilist.co")
    
    query = '''
    query ($page: Int, $perPage: Int) {
      Page (page: $page, perPage: $perPage) {
        pageInfo {
          total
          currentPage
          lastPage
          hasNextPage
          perPage
        }
        media (type: ANIME, sort: POPULARITY_DESC) {
          id
          title {
            romaji
            english
          }
          description
          genres
          averageScore
          episodes
          format
          coverImage {
            large
          }
        }
      }
    }
    '''
    
    normalized_data = []
    has_next_page = True
    current_page = page

    logger.info("Starting AniList API fetch...")

    while has_next_page:
        variables = {
            'page': current_page,
            'perPage': per_page
        }

        try:
            response = requests.post(url, json={'query': query, 'variables': variables})
            
            if response.status_code == 429:
                logger.warning(f"Rate limited on page {current_page}. Waiting 5 seconds before retrying...")
                time.sleep(5)
                continue
                
            response.raise_for_status()
            data = response.json()
            
            page_info = data['data']['Page']['pageInfo']
            media_list = data['data']['Page']['media']
            
            for anime in media_list:
                # Fallback title: English first, then Romaji if English is null
                title = anime['title']['english'] if anime['title']['english'] else anime['title']['romaji']
                
                # Normalize genre list to a comma-separated string (Kaggle format typical representation)
                genre_str = ", ".join(anime['genres']) if anime.get('genres') else ""
                
                # Cleanup HTML tags commonly returned by AniList descriptions
                desc = anime['description'] or ""
                if desc:
                    desc = desc.replace("<br>", "\n").replace("<i>", "").replace("</i>", "")
                
                normalized_data.append({
                    'title': title,
                    'synopsis': desc,
                    'genre': genre_str,
                    'score': anime['averageScore'],
                    'episodes': anime['episodes'] or 0,
                    'type': anime['format'] or "Unknown",
                    'image_url': anime['coverImage']['large'] if anime.get('coverImage') else ""
                })

            logger.info(f"Fetched page {current_page}/{page_info['lastPage']} ({len(media_list)} items).")
            
            has_next_page = page_info['hasNextPage']
            current_page += 1
            
            # Rate limiting buffer
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error on page {current_page}: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error parsing AniList API on page {current_page}: {e}")
            break
            
    logger.success(f"AniList fetch complete. Retrieved {len(normalized_data)} normalized anime records.")
    return normalized_data
