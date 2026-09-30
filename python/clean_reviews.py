import re
import pandas as pd

# ── Config ────────────────────────────────────────────────────
RAW_FILE = 'instagram_reviews_raw_15000.csv'
OUTPUT_FILE = 'instagram_reviews_cleaned_3000.csv'
TARGET_CLEAN = 3000

DESIRED_COLUMNS = [
    'reviewId', 'userName', 'score',
    'thumbsUpCount', 'reviewCreatedVersion', 'at', 'content'
]

MIN_WORDS = 3
MIN_CLEAN_CHARS = 12

EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U00002702-\U000027B0"
    "\U0000FE00-\U0000FE0F"
    "\U0000200D"
    "\U000023E9-\U000023F3"
    "\U0000231A-\U0000231B"
    "\U00002328"
    "\U000023CF"
    "\U000023F8-\U000023FA"
    "\U00002934-\U00002935"
    "\U000025AA-\U000025AB"
    "\U000025B6"
    "\U000025C0"
    "\U000025FB-\U000025FE"
    "\U00002600-\U000027BF"
    "\U00002B05-\U00002B07"
    "\U00002B1B-\U00002B1C"
    "\U00002B50"
    "\U00002B55"
    "\U00003030"
    "\U0000303D"
    "\U00003297"
    "\U00003299"
    "]+", flags=re.UNICODE
)

SPAM_RE = re.compile(r'(.)\1{4,}')


def strip_emojis(text):
    return EMOJI_RE.sub('', text)


def is_meaningful(text):
    """Return True if review is meaningful criticism, not junk."""
    if pd.isna(text):
        return False
    t = str(text).strip()
    if not t:
        return False

    no_emoji = strip_emojis(t).strip()
    if len(no_emoji) < MIN_CLEAN_CHARS:
        return False

    words = no_emoji.split()
    if len(words) < MIN_WORDS:
        return False

    alpha_chars = sum(1 for c in no_emoji if c.isalpha())
    if alpha_chars < len(no_emoji) * 0.4:
        return False

    if SPAM_RE.search(no_emoji):
        cleaned = SPAM_RE.sub('', no_emoji).strip()
        if len(cleaned) < MIN_CLEAN_CHARS:
            return False

    return True


def clean_text(text):
    t = str(text).strip()
    t = re.sub(r'\s+', ' ', t)
    return t.strip()


def main():
    print(f"[*] Loading {RAW_FILE}...")
    df = pd.read_csv(RAW_FILE, sep=';')
    print(f"    Raw rows: {len(df)}")

    cols = [c for c in DESIRED_COLUMNS if c in df.columns]
    df = df[cols].copy()

    df = df.drop_duplicates(subset='reviewId')
    print(f"    After dedup: {len(df)}")

    # Filter critical reviews (score 1-3)
    df_crit = df[df['score'] <= 3].copy()
    print(f"    Critical (score 1-3): {len(df_crit)}")

    # Quality filter
    mask = df_crit['content'].apply(is_meaningful)
    df_clean = df_crit[mask].copy()
    print(f"    After quality filter: {len(df_clean)}")

    # Clean text
    df_clean['content'] = df_clean['content'].apply(clean_text)
    df_clean = df_clean[df_clean['content'].str.len() > 0]
    print(f"    After text cleaning: {len(df_clean)}")

    # Trim to target
    if len(df_clean) >= TARGET_CLEAN:
        df_final = df_clean.head(TARGET_CLEAN)
        print(f"    Trimmed to target: {TARGET_CLEAN}")
    else:
        df_final = df_clean
        print(f"    [!] Only {len(df_final)} clean reviews (target was {TARGET_CLEAN})")

    df_final = df_final.reset_index(drop=True)

    df_final.to_csv(OUTPUT_FILE, index=False, sep=';', encoding='utf-8-sig')
    print(f"\n[+] Exported '{OUTPUT_FILE}' ({len(df_final)} rows)")

    # Validation
    print("\n[*] Validation:")
    print(f"    Rows    : {len(df_final)}")
    print(f"    Columns : {list(df_final.columns)}")
    print(f"    Score dist:")
    print(df_final['score'].value_counts().sort_index().to_string())
    print(f"    Null counts:")
    print(df_final.isnull().sum().to_string())
    empty_content = (df_final['content'].isna() | (df_final['content'] == '')).sum()
    print(f"    Empty content: {empty_content}")
    print(f"\n    Sample reviews:")
    for i, row in df_final.head(5).iterrows():
        print(f"    [{row['score']}] {str(row['content'])[:120]}")


if __name__ == '__main__':
    main()
