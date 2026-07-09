from pathlib import Path

# -----------------------------
# Project Root
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# Data Directories
# -----------------------------
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"

# -----------------------------
# Database
# -----------------------------
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "nifty100.db"

# -----------------------------
# Other Directories
# -----------------------------
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"
DOCS_DIR = BASE_DIR / "docs"

# -----------------------------
# Supported File Types
# -----------------------------
SUPPORTED_FILES = [".xlsx"]

# -----------------------------
# Ensure Required Directories Exist
# -----------------------------
for folder in [
    PROCESSED_DATA_DIR,
    OUTPUT_DIR,
    DATABASE_DIR,
    LOG_DIR,
    REPORT_DIR,
]:
    folder.mkdir(parents=True, exist_ok=True)
