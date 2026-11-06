"""Tests of the data snapshot helpers (no network)."""

import io
import tarfile

import pytest

from yerevan_budget import release


def test_asset_urls(monkeypatch):
    monkeypatch.setenv("YEREVAN_BUDGET_REPO", "org/repo")
    assert release.asset_url("SHA256SUMS") == "https://github.com/org/repo/releases/latest/download/SHA256SUMS"
    assert (release.asset_url("yerevan_budget.duckdb.xz", "data-2026-11-06")
            == "https://github.com/org/repo/releases/download/data-2026-11-06/yerevan_budget.duckdb.xz")


def test_parse_sums():
    text = "abc123  yerevan_budget.duckdb.xz\nDEF456 *yerevan_budget-raw.tar.xz\n\n"
    assert release.parse_sums(text) == {"yerevan_budget.duckdb.xz": "abc123", "yerevan_budget-raw.tar.xz": "def456"}


def _tar(*names: str) -> tarfile.TarFile:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as t:
        for name in names:
            info = tarfile.TarInfo(name)
            info.size = 1
            t.addfile(info, io.BytesIO(b"x"))
    buf.seek(0)
    return tarfile.open(fileobj=buf, mode="r")


def test_safe_members_selects_prefix():
    t = _tar("raw/files/a.pdf", "catalog/documents.json", "rawish/b")
    assert [m.name for m in release.safe_members(t, "raw")] == ["raw/files/a.pdf"]
    assert [m.name for m in release.safe_members(t, "catalog")] == ["catalog/documents.json"]


def test_safe_members_rejects_traversal():
    with pytest.raises(ValueError):
        release.safe_members(_tar("raw/../../etc/passwd"), "raw")


def test_institutions_not_packed():
    assert release._skip_institutions(tarfile.TarInfo("raw/institutions/x.rar")) is None
    info = tarfile.TarInfo("raw/files/x.pdf")
    assert release._skip_institutions(info) is info
