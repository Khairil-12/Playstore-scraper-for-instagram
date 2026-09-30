import time
import pandas as pd
from google_play_scraper import app, reviews, Sort

# ── Configuration ─────────────────────────────────────────────
APP_ID = 'com.instagram.android'
TARGET_COUNT = 15000
LANG = 'en'
COUNTRY = 'us'
BATCH_SIZE = 200
SLEEP_BETWEEN_BATCHES = 0.5
SLEEP_ON_ERROR = 2
OUTPUT_FILE = 'instagram_reviews_raw_15000.csv'

DESIRED_COLUMNS = [
    'reviewId', 'userName', 'score',
    'thumbsUpCount', 'reviewCreatedVersion', 'at', 'content'
]


def fetch_app_metadata():
    """Fetch and print Instagram app metadata."""
    print(f"[*] Fetching metadata for: {APP_ID}")
    try:
        info = app(APP_ID, lang=LANG, country=COUNTRY)
        print(f"    App Title       : {info.get('title')}")
        print(f"    Average Rating  : {info.get('score', 0):.2f} / 5.0")
        print(f"    Total Ratings   : {info.get('ratings')}")
        print(f"    Total Reviews   : {info.get('reviews')}")
        return info
    except Exception as e:
        print(f"[!] Could not fetch metadata: {e}")
        return None


def fetch_reviews():
    """Scrape 15000 reviews with paginated batches."""
    all_reviews = []
    token = None
    start = time.time()

    print(f"\n[*] Scraping {TARGET_COUNT} reviews...")

    while len(all_reviews) < TARGET_COUNT:
        remaining = TARGET_COUNT - len(all_reviews)
        count = min(BATCH_SIZE, remaining)

        try:
            batch, token = reviews(
                APP_ID,
                lang=LANG,
                country=COUNTRY,
                sort=Sort.NEWEST,
                count=count,
                continuation_token=token
            )

            if not batch:
                print("[*] No more reviews available.")
                break

            all_reviews.extend(batch)
            if len(all_reviews) % 1000 == 0 or len(all_reviews) >= TARGET_COUNT:
                print(f"    Progress: {len(all_reviews)} / {TARGET_COUNT}")

            if not token:
                print("[*] Reached end of available reviews.")
                break

            time.sleep(SLEEP_BETWEEN_BATCHES)

        except Exception as e:
            print(f"[!] Batch error: {e}")
            time.sleep(SLEEP_ON_ERROR)
            continue

    elapsed = time.time() - start
    print(f"\n[+] Scraped {len(all_reviews)} reviews in {elapsed:.1f}s")
    return all_reviews


def export_csv(raw_reviews):
    """Convert to DataFrame, select columns, export CSV."""
    df = pd.DataFrame(raw_reviews)
    cols = [c for c in DESIRED_COLUMNS if c in df.columns]
    df_out = df[cols] if cols else df
    df_out.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    print(f"[+] Exported '{OUTPUT_FILE}' ({len(df_out)} rows, {len(df_out.columns)} cols)")
    return df_out


def validate(df):
    """Basic validation on output."""
    print("\n[*] Validation:")
    print(f"    Rows       : {len(df)}")
    print(f"    Columns    : {list(df.columns)}")
    print(f"    Score range: {df['score'].min()} - {df['score'].max()}")
    print(f"    Score dist :")
    print(df['score'].value_counts().sort_index().to_string())
    print(f"    Null counts:")
    print(df.isnull().sum().to_string())


def main():
    fetch_app_metadata()
    raw = fetch_reviews()
    if not raw:
        print("[!] No reviews collected. Exiting.")
        return
    df = export_csv(raw)
    validate(df)


if __name__ == '__main__':
    main()
