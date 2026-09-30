# PRD: Instagram Play Store Review & Rating Scraper

## 1. Overview

Project untuk scraping data rating dan review aplikasi Instagram dari Google Play Store, kemudian melakukan data cleaning untuk mendapatkan dataset review kritik yang bermakna. Data digunakan sebagai dataset untuk keperluan analisis teks pada mata kuliah Pemrosesan Teks (Semester 5).

## 2. Problem Statement

Dibutuhkan dataset review kritik pengguna Instagram dari Google Play Store dalam jumlah ~3000 review bersih untuk text processing dan analisis sentimen. Data mentah perlu di-scrape dalam jumlah besar (15,000) karena mayoritas review positif/tidak bermakna, sehingga setelah cleaning hanya ~3000 review kritik berkualitas yang tersisa.

## 3. Goals

- Scrape 15,000 review dan rating Instagram dari Google Play Store
- Menyimpan data mentah terstruktur dalam format CSV (dirty data)
- Melakukan data cleaning: filter review kritik (score 1-3), hapus emoji-only, spam, dan review terlalu pendek
- Menghasilkan ~3,000 review kritik bersih dan bermakna (clean data)
- Proses scraping berjalan stabil tanpa terkena rate limit

## 4. Non-Goals

- Tidak melakukan analisis sentimen (scope project lain)
- Tidak scraping dari app store lain (Apple App Store, dll)
- Tidak membuat UI/dashboard
- Tidak melakukan real-time monitoring review

## 5. Target Application

| Field | Value |
|-------|-------|
| App Name | Instagram |
| Package ID | `com.instagram.android` |
| Store | Google Play Store |
| Raw Review Count | 15,000 |
| Clean Review Count | ~3,000 |
| Language | English (`en`) |
| Country | United States (`us`) |

## 6. Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.7+ |
| Scraping Library | `google-play-scraper` |
| Data Processing | `pandas` |
| Regex | `re` (stdlib) |
| Output Format | CSV (`.csv`) |
| Documentation | Jupyter Notebook (`.ipynb`) |

## 7. Data Schema

Output CSV (raw & clean) berisi kolom-kolom berikut:

| Column | Type | Description |
|--------|------|-------------|
| `reviewId` | string | Unique identifier tiap review |
| `userName` | string | Nama display user yang memberi review |
| `score` | int (1-5) | Star rating dari user |
| `thumbsUpCount` | int | Jumlah like/helpful votes pada review |
| `reviewCreatedVersion` | string | Versi app saat review ditulis |
| `at` | datetime | Timestamp review diposting |
| `content` | string | Isi teks review |

## 8. Architecture & Flow

```
[Start]
   |
   v
[Fetch App Metadata] --> title, avg rating, total ratings
   |
   v
[Scrape 15,000 Reviews] --> paginated batch (200/batch), Sort.NEWEST
   |
   v
[Export Raw CSV] --> instagram_reviews_raw_15000.csv (dirty data)
   |
   v
[Data Cleaning Pipeline]
   |-- Filter score 1-3 only (critical reviews)
   |-- Remove emoji-only reviews
   |-- Remove too short (< 3 words or < 12 chars after emoji strip)
   |-- Remove spam (repeated chars 5+, < 40% alpha)
   |-- Normalize whitespace
   |
   v
[Trim to ~3,000 reviews]
   |
   v
[Export Clean CSV] --> instagram_reviews_cleaned_3000.csv (clean data)
   |
   v
[Validation] --> row count, score dist, null check, sample preview
```

## 9. Data Cleaning Rules

| Rule | Criteria | Purpose |
|------|----------|---------|
| Score filter | score <= 3 | Hanya review kritik/negatif |
| Emoji-only filter | < 12 chars after emoji removal | Hapus review tanpa teks bermakna |
| Word count filter | < 3 words after emoji removal | Hapus review terlalu pendek |
| Alpha ratio filter | < 40% alphabetic characters | Hapus spam simbol/angka |
| Spam filter | Karakter berulang 5+ kali | Hapus "aaaaaaa", "!!!!!!" dst |
| Whitespace normalize | Collapse multiple spaces | Bersihkan formatting |

## 10. Implementation Plan

### Phase 1: Setup Environment
- Install Python 3.7+
- Install dependencies: `pip install google-play-scraper pandas`

### Phase 2: Scraping (`python/instagram_scraper.py`)
- Fetch app metadata (title, rating, total reviews)
- Scrape 15,000 reviews dengan paginated batches (200/batch)
- Rate limit handling dengan sleep 0.5s antar batch
- Error handling dengan retry + backoff 2s
- Export ke `instagram_reviews_raw_15000.csv`

### Phase 3: Data Cleaning (`python/clean_reviews.py`)
- Load raw CSV
- Deduplicate by reviewId
- Filter score 1-3
- Apply quality filters (emoji, length, spam, alpha ratio)
- Clean text (normalize whitespace)
- Trim to 3,000 rows
- Export ke `instagram_reviews_cleaned_3000.csv`

### Phase 4: Documentation (`notebook/instagram_scraper.ipynb`)
- Notebook berisi seluruh pipeline dari scraping hingga cleaning
- Step-by-step dengan markdown explanation
- Validation & preview di akhir

## 11. Configuration Parameters

```python
# Scraper config
APP_ID = 'com.instagram.android'
TARGET_COUNT = 15000
LANG = 'en'
COUNTRY = 'us'
BATCH_SIZE = 200
SLEEP_BETWEEN_BATCHES = 0.5
SLEEP_ON_ERROR = 2
SORT_ORDER = Sort.NEWEST

# Cleaning config
TARGET_CLEAN = 3000
MIN_WORDS = 3
MIN_CLEAN_CHARS = 12
```

## 12. Error Handling Strategy

| Scenario | Handling |
|----------|----------|
| Rate limit / IP block | Increase `time.sleep()` delay, retry |
| Connection timeout | Catch exception, sleep 2s, continue loop |
| Empty response (no more reviews) | Break loop, export data yang sudah terkumpul |
| Missing fields (e.g. `reviewCreatedVersion`) | Pandas handle sebagai `NaN` |
| Batch fetch error | Log error, sleep, retry batch yang sama |
| Clean data < 3,000 | Relax filter thresholds atau increase raw scrape count |

## 13. Output Files

| File | Type | Rows | Description |
|------|------|------|-------------|
| `instagram_reviews_raw_15000.csv` | Dirty data | 15,000 | Semua review mentah dari Play Store |
| `instagram_reviews_cleaned_3000.csv` | Clean data | ~3,000 | Review kritik bersih dan bermakna |

## 14. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Google rate limiting | Scraping gagal/lambat | Batch kecil (200), sleep antar batch |
| IP blocking | Scraping berhenti total | Ganti network, tingkatkan delay |
| API structure berubah | Library tidak berfungsi | Update `google-play-scraper` ke versi terbaru |
| Clean count < 3,000 | Dataset kurang | Tingkatkan raw count atau relax filter |
| Review tanpa app version | Data incomplete | Handle sebagai NaN, kolom tetap ada |

## 15. Success Criteria

- [x] Script scraping berjalan tanpa error fatal
- [x] Raw CSV berisi 15,000 row review
- [x] Semua 7 kolom data schema tersedia
- [x] Data cleaning menghasilkan ~3,000 review kritik
- [x] Clean data: score 1-3, content bermakna, tidak spam
- [x] Execution time < 2 menit untuk 15,000 review scraping
- [x] Notebook dokumentasi lengkap dengan step-by-step

## 16. Project Structure

```
P2/
├── documentation/
│   ├── play_store_scraping_documentation.md
│   └── PRD.md
├── python/
│   ├── instagram_scraper.py
│   └── clean_reviews.py
├── notebook/
│   └── instagram_scraper.ipynb
├── instagram_reviews_raw_15000.csv        (dirty data - 15,000 rows)
└── instagram_reviews_cleaned_3000.csv     (clean data - ~3,000 rows)
```

## 17. Actual Results

| Metric | Value |
|--------|-------|
| Raw reviews scraped | 15,000 |
| Scraping time | ~78.5s |
| Critical reviews (score 1-3) | 3,920 |
| After quality filter | 3,161 |
| Final clean dataset | 3,000 |
| Score 1 in clean data | 2,369 |
| Score 2 in clean data | 313 |
| Score 3 in clean data | 318 |
| Empty content in clean data | 0 |

## 18. References

- [google-play-scraper PyPI](https://pypi.org/project/google-play-scraper/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- Internal: `documentation/play_store_scraping_documentation.md`
