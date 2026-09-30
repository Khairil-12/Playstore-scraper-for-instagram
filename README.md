# Instagram Play Store Scraper & Cleaner

This repository contains an automated pipeline to extract and clean Instagram app reviews from the Google Play Store. It was built to generate a high-quality dataset of critical user reviews for text processing and sentiment analysis.

## Features

- **Automated Scraper (`python/instagram_scraper.py`):** Fetches 15,000 recent reviews using `google-play-scraper` with built-in pagination and rate-limit handling.
- **Data Cleaner (`python/clean_reviews.py`):** Processes raw data to produce a clean dataset of ~3,000 meaningful critical reviews (1-3 stars) by removing emoji-only reviews, spam, and extremely short comments.
- **Interactive Pipeline (`notebook/instagram_scraper.ipynb`):** A complete Jupyter Notebook containing the end-to-end process from metadata fetching to data export and validation.
- **Detailed Specs (`documentation/PRD.md`):** Complete Product Requirements Document defining architecture, data schema, and cleaning rules.

## Project Structure

```
├── documentation/
│   └── PRD.md                  # Architecture, rules, and metrics
├── notebook/
│   └── instagram_scraper.ipynb # End-to-end Jupyter Notebook
├── python/
│   ├── clean_reviews.py        # Cleaning and filtering logic
│   └── instagram_scraper.py    # Raw scraping script
└── README.md
```
*(Note: Large raw and cleaned CSV datasets are intentionally excluded from version control.)*

## Requirements & Usage

1. **Install dependencies:**
   ```bash
   pip install google-play-scraper pandas
   ```

2. **Scrape raw data (15,000 reviews):**
   ```bash
   python python/instagram_scraper.py
   ```
   *Generates `instagram_reviews_raw_15000.csv`*

3. **Clean data (~3,000 critical reviews):**
   ```bash
   python python/clean_reviews.py
   ```
   *Generates `instagram_reviews_cleaned_3000.csv`*
