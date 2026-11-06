"""Command line interface: ``python -m yerevan_budget <command>``."""

from __future__ import annotations

import argparse
import logging
import sys


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="yerevan-budget", description=__doc__)
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("catalog", help="crawl the Finance pages of yerevan.am -> data/catalog/{pages,documents}.json")

    f = sub.add_parser("fetch", help="download the documents (and unpack the archives) -> data/raw")
    f.add_argument("--force", action="store_true", help="download again documents that are already on disk")
    f.add_argument("--institutions", action="store_true",
                   help="also download the ≈10 GB of archives of municipal institutions (not parsed)")

    e = sub.add_parser("extract", help="extract text and tables of every file -> data/interim/*.json.gz")
    e.add_argument("--force", action="store_true", help="re-extract files that are already cached")
    e.add_argument("--doc", action="append", help="only this doc_id (repeatable)")

    b = sub.add_parser("build", help="(re)build the DuckDB database from data/raw, data/interim and data/translations")
    b.add_argument("--db", help="output path (default data/yerevan_budget.duckdb)")

    t = sub.add_parser("translations", help="write names without a translation to data/translations/pending/")
    t.add_argument("--merge", action="store_true", help="merge the filled files from data/translations/pending")

    sub.add_parser("docs", help="regenerate docs/data_dictionary.md and docs/*/inventory.md from the database")

    a = sub.add_parser("all", help="catalog + fetch + extract + build + docs")
    a.add_argument("--force", action="store_true")

    r = sub.add_parser("release", help="pack the data snapshot and publish it as a GitHub release (needs gh)")
    r.add_argument("--tag", help="release tag (default data-<collection date>)")
    r.add_argument("--pack-only", action="store_true", help="only create the assets in data/release/<tag>")

    dl = sub.add_parser("download", help="download a data snapshot from GitHub releases into data/")
    dl.add_argument("--tag", default="latest", help="release tag (default: latest)")
    dl.add_argument("--part", action="append", choices=["db", "parquet", "raw"], help="what to download (default: db)")
    dl.add_argument("--with-catalog", action="store_true", help="with raw: also overwrite data/catalog from the snapshot")

    args = p.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    for noisy in ("pdfminer", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    if args.cmd in ("release", "download"):
        from . import release

        if args.cmd == "release":
            release.pack(args.tag) if args.pack_only else release.publish(args.tag)
        else:
            release.download(args.tag, tuple(args.part or ["db"]), args.with_catalog)
        return 0
    if args.cmd == "translations":
        from . import translations

        translations.merge_pending() if args.merge else translations.write_pending()
        return 0

    force = getattr(args, "force", False)
    if args.cmd in ("catalog", "all"):
        from . import catalog

        catalog.crawl()
    if args.cmd in ("fetch", "all"):
        from . import fetch

        fetch.download(force=force if args.cmd == "fetch" else False, institutions=getattr(args, "institutions", False))
    if args.cmd in ("extract", "all"):
        from . import extract

        extract.run(force=force, only=tuple(getattr(args, "doc", None) or ()))
    if args.cmd in ("build", "all"):
        from . import build

        build.build(getattr(args, "db", None))
    if args.cmd in ("docs", "all"):
        from . import docs

        docs.write_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
