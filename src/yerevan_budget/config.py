"""Project-wide constants: paths, source pages, HTTP settings."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PAGES_DIR = RAW_DIR / "pages"            # HTML of the site pages
FILES_DIR = RAW_DIR / "files"            # downloaded documents (<doc_id>.<ext>)
EXTRACTED_DIR = RAW_DIR / "extracted"    # content of rar / zip archives (<doc_id>/...)
INSTITUTIONS_DIR = RAW_DIR / "institutions"  # optional: archives of municipal institutions
INTERIM_DIR = DATA_DIR / "interim"       # extracted text and tables of every file (json.gz cache)
CATALOG_DIR = DATA_DIR / "catalog"       # small JSON manifests (committed to git)
TRANSLATIONS_DIR = DATA_DIR / "translations"  # hy -> en / ru dictionaries (committed to git)
SQL_DIR = ROOT / "sql"
DUCKDB_PATH = DATA_DIR / "yerevan_budget.duckdb"
RELEASE_DIR = DATA_DIR / "release"       # packed data snapshots (not in git)

# GitHub repository whose releases carry the data snapshots (override: env YEREVAN_BUDGET_REPO)
GITHUB_REPO = "opendataam/arm-yerevan-budget"

BASE_URL = "https://www.yerevan.am"
LANG = "hy"  # the documents are published only in the Armenian version of the site

# The "Finance" section (https://www.yerevan.am/hy/finance/) and its sub pages.
#   group "core"         – documents of the city budget (parsed into the database)
#   group "institutions" – financial documents of municipal institutions and companies
#                          (catalogued; downloaded only on request, not parsed)
#   group "link"         – pages that only link elsewhere
PAGES: dict[str, dict] = {
    "finance": {"group": "core", "title_en": "Finance (current documents)"},
    "archive-documents-of-2018": {"group": "core", "year": 2018, "title_en": "Archive documents of 2018"},
    "archive-documents-of-2019": {"group": "core", "year": 2019, "title_en": "Archive documents of 2019"},
    "archive-documents-of-2020": {"group": "core", "year": 2020, "title_en": "Archive documents of 2020"},
    "archive-documents-of-2021": {"group": "core", "year": 2021, "title_en": "Archive documents of 2021"},
    "archive-documents-of-2022": {"group": "core", "year": 2022, "title_en": "Archive documents of 2022"},
    "finance-archive-documents-of-2023": {"group": "core", "year": 2023, "title_en": "Archive documents of 2023"},
    "finance-archive-documents-of-2024": {"group": "core", "year": 2024, "title_en": "Archive documents of 2024"},
    "finance-archive-documents-of-2025": {"group": "core", "year": 2025, "title_en": "Archive documents of 2025"},
    "byowje-bolori-hamar": {"group": "core", "title_en": "Budget for everyone"},
    "finance-docs": {"group": "institutions",
                     "title_en": "Annual financial documents of state and community non-commercial organisations"},
    "finance-other-docs": {"group": "institutions",
                           "title_en": "Annual financial documents of community closed joint-stock companies"},
    "interactive-budget": {"group": "link", "title_en": "Interactive budget"},
}

# File types that are treated as documents when linked from a page
DOC_EXTENSIONS = ("pdf", "rar", "zip", "7z", "xls", "xlsx", "doc", "docx")

USER_AGENT = "yerevan-budget-collector/0.1 (open data research; python-requests)"
HTTP_TIMEOUT = 300
HTTP_RETRIES = 4
HTTP_DELAY = 1.0  # seconds between requests (be polite)
