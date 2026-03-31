# Djezzy SEO Thesis — Automation Pipeline

> **The Impact Search Engine Optimization (SEO) on Brand Positioning : Using an Automated Analytical Pipeline — Case Study: Djezzy Algeria**
> Licence Dissertation · Batna 1 University – Hadj Lakhdar  
> Faculty of Economic, Commercial and Management Sciences  
> **Author:** Meguelati Ali Zine El Abidine
---

## Overview

This repository contains the complete automation pipeline developed as part of the dissertation. It connects every stage of the research workflow:
For Permission requests PLEASE CONTACT ME AT : zineelabidine.meguellati@gmail.com

```
Google Forms Survey
       │
       ▼
Google Sheets  ◄──── createDjezzyForm.gs  (Apps Script)
       │
       ▼
sheets_reader.py  ──► data/survey_data_latest.csv
       │
       ▼
update_thesis.py  ──► Scripts 1–4 ──► 8 PNG figures
       │
       ▼
Google Drive  (thesis .docx updated automatically)
```

**Key results from the 100-respondent survey:**
- Pearson r = **−0.97** between search ranking position and perceived credibility
- Cronbach's Alpha = **0.87** (overall 7-item scale)
- **0%** of respondents cited Google as their primary brand discovery channel → central diagnostic finding

---

## Project Structure

```
djezzy-seo-thesis/
│
├── update_thesis.py          # Main one-click pipeline (Scripts 1–4 + Drive API)
├── requirements.txt          # Python dependencies
├── .gitignore
├── README.md
│
├── scripts/
│   ├── createDjezzyForm.gs   # Google Apps Script — creates the survey form
│   └── sheets_reader.py      # Reads live responses from Google Sheets → CSV
│
├── credentials/              # NOT committed — see Setup
│   └── service_account.json  # Google Cloud service account key
│
├── data/                     # NOT committed (survey_data_latest.csv goes here)
│   └── .gitkeep
│
└── figures/                  # Generated automatically — NOT committed
    └── .gitkeep
```

---

## Scripts

### `update_thesis.py` — Main Pipeline

One-click automation that integrates all four Appendix B analysis scripts:

| Section | Function | Description |
|---|---|---|
| Script 1 | `load_and_clean()` | Load raw CSV, rename columns, drop missing values |
| Script 2 | `descriptive_stats_and_figures()` | Table 3.3 + Figures 3.1–3.6 |
| Script 3 | `pearson_correlation_and_figure()` | Pearson r + heatmap Figure 3.7 |
| Script 4 | `cronbach_alpha_from_data()` + `reliability_analysis_and_figure()` | Cronbach α + Figure 3.8 |
| Drive | `download_file()` / `replace_images_in_docx()` / `upload_file()` | Full Drive sync |

**Run:**
```bash
python update_thesis.py
```

---

### `scripts/createDjezzyForm.gs` — Google Apps Script

Creates the complete bilingual (English/Arabic) survey form with 16 questions across 4 sections and automatically links it to a Google Sheets spreadsheet for response collection.

**Usage:**
1. Open [Google Apps Script](https://script.google.com)
2. Create a new project and paste the script
3. Run `createForm()` — **once only**
4. Check **View → Logs** for the form URL, share URL, and Sheet ID

**Sections:**
- **Section A** — Personal Information (gender, age, education)
- **Section B** — Internet & Search Engine Usage
- **Section C** — Djezzy Algeria & Digital Discovery
- **Section D** — SEO & Brand Perception (7-item Likert scale, 1–5)

---

### `scripts/sheets_reader.py` — Google Sheets Reader

Reads live survey responses directly from the linked Google Sheets spreadsheet, renames columns to match the analysis pipeline, and exports a clean CSV.

**Run:**
```bash
# Export CSV only
python scripts/sheets_reader.py

# Export CSV and immediately regenerate all figures
python scripts/sheets_reader.py --run-pipeline
```

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/djezzy-seo-thesis.git
cd djezzy-seo-thesis
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up Google Cloud credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or use existing)
3. Enable **Google Drive API** and **Google Sheets API**
4. Create a **Service Account** → Download the JSON key
5. Place the JSON file at `credentials/service_account.json`
6. Share your thesis `.docx` and survey CSV on Google Drive with the service account email

### 4. Configure file IDs

Edit the top of `update_thesis.py`:
```python
THESIS_FILE_ID = "your_drive_thesis_file_id"
CSV_FILE_ID    = "your_drive_csv_file_id"
```

Edit the top of `scripts/sheets_reader.py`:
```python
SHEET_ID = "your_google_sheets_spreadsheet_id"
```

> **Finding a Drive file ID:** Open the file in Google Drive → the ID is the long string in the URL between `/d/` and `/edit`.

---

## How to Get File IDs

| What | Where to find it |
|---|---|
| Drive file ID | `https://drive.google.com/file/d/`**`THIS_PART`**`/view` |
| Sheets spreadsheet ID | `https://docs.google.com/spreadsheets/d/`**`THIS_PART`**`/edit` |
| Apps Script log | View → Logs after running `createForm()` |

---

## Figures Generated

| File | Figure | Description |
|---|---|---|
| `image5.png` | Figure 3.1 | Distribution of Respondents by Gender |
| `image6.png` | Figure 3.2 | Distribution of Respondents by Age Group |
| `image7.png` | Figure 3.3 | Search Engine Usage Frequency |
| `image8.png` | Figure 3.4 | Trust Level by Search Ranking Position |
| `image9.png` | Figure 3.5 | Brand Discovery Channel — Djezzy |
| `image10.png` | Figure 3.6 | Likert Scale Responses (±1 SD) |
| `image11.png` | Figure 3.7 | Pearson Correlation Heatmap (r = −0.97) |
| `image12.png` | Figure 3.8 | Cronbach's Alpha by Dimension (α = 0.87) |

---

## Research Context

**Central question:** Does SEO measurably affect how Algerian users perceive and position Djezzy Algeria?

**Three hypotheses tested:**
- **H1** — Higher Google ranking is associated with higher perceived brand visibility ✓
- **H2** — Users who find Djezzy at higher positions trust the brand more ✓ (r = −0.97)
- **H3** — SEO practices have a measurable positive effect on brand perception ✓ (α = 0.87)

**Key diagnostic finding:** 8% of respondents cited Google as their primary discovery channel for Djezzy (word of mouth: 38%, social media: 31%) — suggesting Djezzy's organic search presence does not yet translate into brand discovery despite high trust correlation with rank position.

---

## License

All rights reserved © 2026 — Meguelati Ali Zine El Abidine  
Deposited at **ONDA** (National Office of Copyright and Related Rights), Algeria.

Academic use only. Not for commercial redistribution.

---

## Citation

```
Meguellati, A. Z. E. (2026). The Impact Search Engine Optimization (SEO) on Brand Positioning : Using an Automated Analytical Pipeline [Licence dissertation].
Batna 1 University – Hadj Lakhdar, Faculty of Economic,
Commercial and Management Sciences.
```
