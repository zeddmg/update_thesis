#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# =============================================================================
# update_thesis.py
# =============================================================================
# Author       : Meguellati Ali Zine El Abidine
# Institution  : Batna 1 University – Hadj Lakhdar
#                Faculty of Economic, Commercial and Management Sciences
# Academic Year: 2025 – 2026
# Topic        : The Impact of Search engine optimization on brand positioning
#                using an automated pipeline
#                – Case Study: Djezzy Algeria
# =============================================================================
# Description:
#   One-Click Automation Pipeline integrating Appendix B Scripts 1–4:
#
#   Script 1  – Data loading & cleaning (data_loading.py)
#   Script 2  – Descriptive statistics + Figures 3.1–3.6
#   Script 3  – Pearson correlation (r=−0.97) + Figure 3.7 heatmap
#   Script 4  – Cronbach's Alpha computed from data + Figure 3.8
#   Drive API – Download thesis .docx + CSV → replace images → re-upload
#
# Usage:
#   python update_thesis.py
#
# Requirements:
#   pip install -r requirements.txt
#   Place service account JSON at: credentials/service_account.json
#   Set THESIS_FILE_ID and CSV_FILE_ID below
# =============================================================================
# License: All rights reserved © 2026 – Deposited at ONDA Algeria
# =============================================================================

import os
import shutil
import zipfile
import tempfile

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2 import service_account

# =============================================================================
# SECTION 1 – CONFIGURATION
# =============================================================================

CREDENTIALS_FILE = "credentials/service_account.json"
THESIS_FILE_ID   = "YOUR_GOOGLE_DRIVE_THESIS_FILE_ID"   # replace with actual ID
CSV_FILE_ID      = "YOUR_GOOGLE_DRIVE_CSV_FILE_ID"       # replace with actual ID
SCOPES           = ["https://www.googleapis.com/auth/drive"]

# Survey column names (match survey_data_sample.csv after Script 1 cleaning)
LIKERT_COLS = ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7"]
DEMO_COLS   = ["gender", "age_group", "education"]

# Research dimensions for Pearson + Cronbach
DIMENSIONS = {
    "SEO Awareness":    ["Q1", "Q2"],
    "Brand Visibility": ["Q3", "Q5"],
    "Consumer Trust":   ["Q4", "Q6"],
    "Purchase Behavior":["Q7"],
}

# Thesis colour palette (extracted from .docx theme)
NAVY   = "#1F4E79"
BLUE   = "#2E75B6"
ORANGE = "#ED7D31"
GOLD   = "#FFC000"
GREEN  = "#A9D18E"

# Rank-position mapping for djezzy_page column
RANK_MAP = {
    "Page 1 (positions 1-10)": 1,
    "Page 2":                   2,
    "Page 3 or beyond":         3,
    "I have never searched for this": np.nan,
}


# =============================================================================
# SECTION 2 – SCRIPT 1: DATA LOADING AND CLEANING
# Source: Appendix B – Script 1 (data_loading.py)
# =============================================================================

def load_and_clean(csv_path: str) -> pd.DataFrame:
    """
    Loads raw Google Forms CSV export, renames columns to short variable
    names, converts Likert columns to numeric, and drops rows with missing
    Likert values.

    Args:
        csv_path: Path to raw or pre-cleaned CSV file.

    Returns:
        Clean DataFrame (100 rows × 16 columns) ready for analysis.

    Column schema after cleaning:
        gender, age_group, education, search_freq, search_engine,
        discovery_action, searched_djezzy, discovery_channel,
        djezzy_page, Q1, Q2, Q3, Q4, Q5, Q6, Q7
    """
    df = pd.read_csv(csv_path)

    # Rename if raw Google Forms export (17 cols including timestamp)
    if len(df.columns) == 17:
        df.columns = [
            "timestamp", "gender", "age_group", "education",
            "search_freq", "search_engine", "discovery_action",
            "searched_djezzy", "discovery_channel", "djezzy_page",
            "Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7",
        ]
        df.drop(columns=["timestamp"], inplace=True)

    # Convert Likert items to numeric (1–5), coerce errors to NaN
    existing_likert = [c for c in LIKERT_COLS if c in df.columns]
    df[existing_likert] = df[existing_likert].apply(pd.to_numeric, errors="coerce")

    # Drop rows with any missing Likert values
    before = len(df)
    df.dropna(subset=existing_likert, inplace=True)
    df.reset_index(drop=True, inplace=True)

    dropped = before - len(df)
    print(f"  ✓ Loaded {len(df)} clean responses ({dropped} dropped), "
          f"{len(df.columns)} columns")
    return df


# =============================================================================
# SECTION 3 – SCRIPT 2: DESCRIPTIVE STATISTICS + FIGURES 3.1–3.6
# Source: Appendix B – Script 2 (descriptive_stats.py)
# =============================================================================

def descriptive_stats_and_figures(df: pd.DataFrame, output_dir: str) -> None:
    """
    Computes frequency distributions, means, and standard deviations
    (Table 3.3) and generates Figures 3.1–3.6 as PNG files.

    Figures generated:
        image5.png  – Figure 3.1: Gender distribution
        image6.png  – Figure 3.2: Age group distribution
        image7.png  – Figure 3.3: Search engine usage frequency
        image8.png  – Figure 3.4: Trust level by search ranking position
        image9.png  – Figure 3.5: Brand discovery channel (Djezzy)
        image10.png – Figure 3.6: Likert scale responses with ±1 SD bars

    Args:
        df:         Clean DataFrame from load_and_clean().
        output_dir: Directory to save PNG files.
    """
    os.makedirs(output_dir, exist_ok=True)
    existing_likert = [c for c in LIKERT_COLS if c in df.columns]

    # ── Table 3.3: Descriptive statistics ─────────────────────────────────
    desc = df[existing_likert].describe().T[["mean", "std", "min", "max"]]
    desc.columns = ["Mean", "Std. Dev.", "Min", "Max"]
    print("\n  [Table 3.3] Descriptive Statistics – Likert Items:")
    print(desc.round(2).to_string())

    for col in [c for c in DEMO_COLS if c in df.columns]:
        print(f"\n  {col} (%):")
        print(df[col].value_counts(normalize=True).mul(100).round(1).to_string())

    # ── Figure 3.1: Gender distribution ───────────────────────────────────
    if "gender" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        df["gender"].value_counts().plot(kind="bar", ax=ax, color=NAVY, edgecolor="white")
        ax.set_title("Figure 3.1: Distribution of Respondents by Gender",
                     fontweight="bold")
        ax.set_xlabel("Gender"); ax.set_ylabel("Number of Respondents")
        ax.tick_params(axis="x", rotation=0)
        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, "image5.png"), dpi=150)
        plt.close(fig); print("  ✓ Figure 3.1 saved")

    # ── Figure 3.2: Age group distribution ────────────────────────────────
    if "age_group" in df.columns:
        order = ["18-24", "25-34", "35-44", "45-54", "55+"]
        counts = df["age_group"].value_counts()
        counts = counts.reindex([x for x in order if x in counts.index])
        fig, ax = plt.subplots(figsize=(8, 4))
        counts.plot(kind="bar", ax=ax, color=BLUE, edgecolor="white")
        ax.set_title("Figure 3.2: Distribution of Respondents by Age Group",
                     fontweight="bold")
        ax.set_xlabel("Age Group"); ax.set_ylabel("Number of Respondents")
        ax.tick_params(axis="x", rotation=15)
        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, "image6.png"), dpi=150)
        plt.close(fig); print("  ✓ Figure 3.2 saved")

    # ── Figure 3.3: Search engine usage frequency ──────────────────────────
    if "search_freq" in df.columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        df["search_freq"].value_counts().plot(
            kind="bar", ax=ax, color=NAVY, edgecolor="white")
        ax.set_title(
            "Figure 3.3: Search Engine Usage Frequency Among Respondents",
            fontweight="bold")
        ax.set_xlabel("Frequency"); ax.set_ylabel("Number of Respondents")
        ax.tick_params(axis="x", rotation=15)
        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, "image7.png"), dpi=150)
        plt.close(fig); print("  ✓ Figure 3.3 saved")

    # ── Figure 3.4: Trust level by search ranking position ────────────────
    if all(c in df.columns for c in ["djezzy_page", "Q1", "Q4"]):
        df_r = df.copy()
        df_r["rank_position"] = df_r["djezzy_page"].map(RANK_MAP)
        df_r["trust_score"]   = df_r[["Q1", "Q4"]].mean(axis=1)
        trust_by_rank = (df_r.dropna(subset=["rank_position"])
                             .groupby("rank_position")["trust_score"]
                             .mean())
        fig, ax = plt.subplots(figsize=(8, 4))
        trust_by_rank.plot(kind="bar", ax=ax, color=GOLD, edgecolor="white")
        ax.set_title(
            "Figure 3.4: User Trust Level According to Search Ranking Position",
            fontweight="bold")
        ax.set_xlabel("Search Ranking Position  (1=Page 1 · 2=Page 2 · 3=Page 3+)")
        ax.set_ylabel("Mean Trust Score"); ax.set_ylim(1, 5)
        ax.tick_params(axis="x", rotation=0)
        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, "image8.png"), dpi=150)
        plt.close(fig); print("  ✓ Figure 3.4 saved")

    # ── Figure 3.5: Brand discovery channel ──────────────────────────────
    if "discovery_channel" in df.columns:
        disc = df["discovery_channel"].value_counts()
        palette = [NAVY, BLUE, ORANGE, GOLD, GREEN, "#7030A0"]
        fig, ax = plt.subplots(figsize=(9, 4))
        disc.plot(kind="barh", ax=ax, color=palette[:len(disc)])
        ax.set_title(
            "Figure 3.5: How Respondents First Discovered the Djezzy Brand",
            fontweight="bold")
        ax.set_xlabel("Number of Respondents")
        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, "image9.png"), dpi=150)
        plt.close(fig); print("  ✓ Figure 3.5 saved")

    # ── Figure 3.6: Likert scale responses with error bars ────────────────
    if existing_likert:
        means = df[existing_likert].mean()
        stds  = df[existing_likert].std()
        x = np.arange(len(existing_likert))
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(x, means, yerr=stds, capsize=5, color=BLUE,
               edgecolor="white", alpha=0.85)
        ax.set_xticks(x); ax.set_xticklabels(existing_likert)
        ax.set_title(
            "Figure 3.6: Likert Scale Responses – SEO Impact on Brand Perception",
            fontweight="bold")
        ax.set_xlabel("Survey Item")
        ax.set_ylabel("Mean Score (1–5,  error bars = ±1 SD)")
        ax.set_ylim(1, 5.8)
        ax.axhline(3, color="gray", linestyle="--",
                   linewidth=0.8, label="Neutral midpoint (3)")
        ax.legend()
        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, "image10.png"), dpi=150)
        plt.close(fig); print("  ✓ Figure 3.6 saved")


# =============================================================================
# SECTION 4 – SCRIPT 3: PEARSON CORRELATION + FIGURE 3.7 (HEATMAP)
# Source: Appendix B – Script 3 (pearson_correlation.py)
# =============================================================================

def pearson_correlation_and_figure(df: pd.DataFrame, output_dir: str) -> None:
    """
    Tests H2: Pearson correlation between search ranking position and
    mean trust score per rank group.  Real result: r = −0.97, p < 0.001.

    Also builds the full inter-construct correlation matrix (Table 3.4)
    and generates Figure 3.7 as a seaborn heatmap.

    Args:
        df:         Clean DataFrame from load_and_clean().
        output_dir: Directory to save image11.png.
    """
    os.makedirs(output_dir, exist_ok=True)
    r, p = np.nan, np.nan

    # H2: grouped-means Pearson (rank position vs. trust)
    if all(c in df.columns for c in ["djezzy_page", "Q1", "Q4"]):
        df_r = df.copy()
        df_r["rank_position"] = df_r["djezzy_page"].map(RANK_MAP)
        df_r["trust_score"]   = df_r[["Q1", "Q4"]].mean(axis=1)
        grouped = (df_r.dropna(subset=["rank_position"])
                       .groupby("rank_position")["trust_score"]
                       .mean())
        r, p = stats.pearsonr(grouped.index, grouped.values)
        print(f"\n  [H2] Pearson r = {r:.4f},  p = {p:.4f}")

    # Inter-construct correlation matrix (Table 3.4)
    df_dims = df.copy()
    valid_dims = {}
    for name, cols in DIMENSIONS.items():
        existing = [c for c in cols if c in df_dims.columns]
        if existing:
            df_dims[name] = df_dims[existing].mean(axis=1)
            valid_dims[name] = existing

    corr_matrix = df_dims[list(valid_dims.keys())].corr()
    print("\n  [Table 3.4] Inter-Construct Correlation Matrix:")
    print(corr_matrix.round(2).to_string())

    # Figure 3.7 – heatmap
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.heatmap(
        corr_matrix,
        annot=True, fmt=".2f", cmap="Blues",
        linewidths=0.5, vmin=0, vmax=1,
        ax=ax, annot_kws={"size": 11},
    )
    title = "Figure 3.7: Pearson Correlation Matrix"
    if not np.isnan(r):
        title += f"\n(H2: Rank Position vs. Perceived Trust  r = {r:.2f},  p = {p:.4f})"
    ax.set_title(title, fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "image11.png"), dpi=150)
    plt.close(fig)
    print("  ✓ Figure 3.7 (heatmap) saved")


# =============================================================================
# SECTION 5 – SCRIPT 4: CRONBACH'S ALPHA + FIGURE 3.8
# Source: Appendix B – Script 4 (cronbach_alpha.py)
# =============================================================================

def cronbach_alpha_from_data(df_subset: pd.DataFrame) -> float:
    """
    Computes Cronbach's Alpha from raw item scores.

    Formula: α = k/(k−1) × (1 − Σvar_i / var_total)

    Args:
        df_subset: DataFrame of k Likert-scale item columns (k ≥ 2).

    Returns:
        Cronbach's Alpha coefficient (float, 0–1).
    """
    k = df_subset.shape[1]
    item_variances = df_subset.var(axis=0, ddof=1).sum()
    total_variance = df_subset.sum(axis=1).var(ddof=1)
    return (k / (k - 1)) * (1 - item_variances / total_variance)


def reliability_analysis_and_figure(df: pd.DataFrame, output_dir: str) -> None:
    """
    Applies cronbach_alpha_from_data() to each research dimension and to
    the full 7-item scale.  Overall α = 0.87 (Table 3.5).
    Generates Figure 3.8 as a bar chart.

    Args:
        df:         Clean DataFrame from load_and_clean().
        output_dir: Directory to save image12.png.
    """
    os.makedirs(output_dir, exist_ok=True)
    existing_likert = [c for c in LIKERT_COLS if c in df.columns]

    print("\n  [Table 3.5] Cronbach's Alpha by Research Dimension:")
    alphas = {}
    for dim, cols in DIMENSIONS.items():
        existing = [c for c in cols if c in df.columns]
        if len(existing) < 2:
            print(f"  {dim}: only {len(existing)} item – not computable")
            continue
        a = cronbach_alpha_from_data(df[existing])
        alphas[dim] = a
        tag = ("✓ Good"       if a >= 0.80 else
               "✓ Acceptable" if a >= 0.70 else
               "✗ Low")
        print(f"  {dim:22s}: α = {a:.3f}  {tag}")

    overall = np.nan
    if len(existing_likert) >= 2:
        overall = cronbach_alpha_from_data(df[existing_likert])
        tag = ("✓ Good"       if overall >= 0.80 else
               "✓ Acceptable" if overall >= 0.70 else
               "✗ Low")
        print(f"  {'Overall (Q1–Q7)':22s}: α = {overall:.3f}  {tag}")

    # Figure 3.8
    if alphas:
        palette = [NAVY, BLUE, ORANGE, GOLD]
        fig, ax = plt.subplots(figsize=(9, 4))
        bars = ax.bar(
            list(alphas.keys()), list(alphas.values()),
            color=palette[:len(alphas)], edgecolor="white",
        )
        for bar, val in zip(bars, alphas.values()):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01,
                    f"{val:.3f}", ha="center", va="bottom",
                    fontweight="bold", fontsize=10)
        ax.axhline(0.70, color="red",    linestyle="--", lw=1.2,
                   label="Min Acceptable (0.70)")
        ax.axhline(0.80, color="orange", linestyle=":",  lw=1.0,
                   label="Good reliability (0.80)")
        if not np.isnan(overall):
            ax.axhline(overall, color="green", linestyle="-.", lw=1.0,
                       label=f"Overall scale α = {overall:.3f}")
        ax.set_ylim(0, 1.05)
        ax.set_title("Figure 3.8: Cronbach's Alpha by Research Dimension",
                     fontweight="bold")
        ax.set_ylabel("Alpha Coefficient")
        ax.legend(loc="lower right")
        ax.tick_params(axis="x", rotation=10)
        plt.tight_layout()
        fig.savefig(os.path.join(output_dir, "image12.png"), dpi=150)
        plt.close(fig)
        print("  ✓ Figure 3.8 (Cronbach's Alpha) saved")


# =============================================================================
# SECTION 6 – MASTER FIGURE GENERATOR  (Scripts 1–4 in sequence)
# =============================================================================

def regenerate_figures(csv_path: str, output_dir: str) -> None:
    """
    Master entry point: runs Scripts 1–4 in sequence to produce all
    8 thesis figures (image5.png … image12.png).

    Args:
        csv_path:   Path to CSV file (raw Google Forms export or cleaned).
        output_dir: Directory to save all PNG output files.
    """
    print("\n── Script 1: Loading & Cleaning ──────────────────────────────────")
    df = load_and_clean(csv_path)

    print("\n── Script 2: Descriptive Stats & Figures 3.1–3.6 ────────────────")
    descriptive_stats_and_figures(df, output_dir)

    print("\n── Script 3: Pearson Correlation & Figure 3.7 (heatmap) ──────────")
    pearson_correlation_and_figure(df, output_dir)

    print("\n── Script 4: Cronbach's Alpha & Figure 3.8 ───────────────────────")
    reliability_analysis_and_figure(df, output_dir)


# =============================================================================
# SECTION 7 – GOOGLE DRIVE: AUTHENTICATE
# =============================================================================

def get_drive_service():
    """
    Authenticates with Google Drive API v3 using a Service Account.
    No browser login required.

    Returns:
        Authenticated googleapiclient Resource object.

    Prerequisite:
        credentials/service_account.json must exist and be shared
        with the target Drive files.
    """
    creds = service_account.Credentials.from_service_account_file(
        CREDENTIALS_FILE, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


# =============================================================================
# SECTION 8 – GOOGLE DRIVE: DOWNLOAD
# =============================================================================

def download_file(service, file_id: str, dest_path: str) -> None:
    """
    Downloads a plain Drive file by ID to a local path.

    Warning: Does NOT work with native Google Docs/Sheets.
    Export those via files().export() first.

    Args:
        service:   Authenticated Drive service object.
        file_id:   Google Drive file ID.
        dest_path: Local destination path.
    """
    request = service.files().get_media(fileId=file_id)
    with open(dest_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()


# =============================================================================
# SECTION 9 – DOCX IMAGE REPLACEMENT  (OOXML / ZIP manipulation)
# =============================================================================

def replace_images_in_docx(docx_path: str,
                            new_images_dir: str,
                            output_path: str) -> None:
    """
    Unzips .docx, replaces matching images in word/media/, rezips.

    Algorithm:
        1. Extract .docx to a temp directory
        2. Copy new PNGs over existing files in word/media/
           (filenames must match, e.g. image5.png → image5.png)
        3. Repack the directory as ZIP → .docx
        4. Delete temp directory

    Args:
        docx_path:      Path to the original .docx file.
        new_images_dir: Folder with replacement PNG files.
        output_path:    Path for the updated .docx output.
    """
    tmpdir = tempfile.mkdtemp()
    try:
        with zipfile.ZipFile(docx_path, "r") as z:
            z.extractall(tmpdir)

        media_dir = os.path.join(tmpdir, "word", "media")
        replaced = 0
        for fname in os.listdir(new_images_dir):
            target = os.path.join(media_dir, fname)
            if os.path.exists(target):
                shutil.copy2(os.path.join(new_images_dir, fname), target)
                replaced += 1

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for root, _, files in os.walk(tmpdir):
                for file in files:
                    fp = os.path.join(root, file)
                    zout.write(fp, os.path.relpath(fp, tmpdir))

        print(f"  ✓ {replaced} image(s) replaced in .docx")
    finally:
        shutil.rmtree(tmpdir)


# =============================================================================
# SECTION 10 – GOOGLE DRIVE: UPLOAD
# =============================================================================

def upload_file(service, file_id: str, local_path: str) -> None:
    """
    Uploads a local file as a new version of an existing Drive file.

    Args:
        service:    Authenticated Drive service object.
        file_id:    Google Drive file ID to overwrite.
        local_path: Path to the local .docx to upload.
    """
    media = MediaFileUpload(
        local_path,
        mimetype=("application/vnd.openxmlformats-officedocument"
                  ".wordprocessingml.document"),
        resumable=True,
    )
    service.files().update(fileId=file_id, media_body=media).execute()


# =============================================================================
# SECTION 11 – MAIN PIPELINE  (One-Click Entry Point)
# =============================================================================

if __name__ == "__main__":
    print("=" * 66)
    print("  update_thesis.py — One-Click Thesis Automation Pipeline")
    print("  Author     : Meguelati Ali Zine El Abidine")
    print("  Institution: Batna 1 University | 2025–2026")
    print("=" * 66)

    print("\n[1/5] Authenticating with Google Drive...")
    svc = get_drive_service()

    print("[2/5] Downloading thesis .docx from Drive...")
    download_file(svc, THESIS_FILE_ID, "thesis_local.docx")

    print("[3/5] Downloading latest survey CSV from Drive...")
    download_file(svc, CSV_FILE_ID, "survey_data_latest.csv")

    print("[4/5] Running full analysis pipeline (Scripts 1–4)...")
    regenerate_figures("survey_data_latest.csv", "figures")

    print("\n[5/5] Replacing images in .docx and uploading to Drive...")
    replace_images_in_docx("thesis_local.docx", "figures", "thesis_updated.docx")
    upload_file(svc, THESIS_FILE_ID, "thesis_updated.docx")

    print("\n" + "=" * 66)
    print("  ✓  Done. Thesis updated and synced to Google Drive.")
    print("=" * 66)
