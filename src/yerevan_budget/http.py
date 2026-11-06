"""Small polite HTTP client with retries, rate limiting and streamed downloads."""

from __future__ import annotations

import logging
import time
from pathlib import Path

import requests

from . import config

log = logging.getLogger(__name__)


class Client:
    """Wrapper around ``requests.Session`` with a pause between requests and retries."""

    def __init__(self, delay: float = config.HTTP_DELAY) -> None:
        self.session = requests.Session()
        self.session.headers["User-Agent"] = config.USER_AGENT
        self.delay = delay
        self._last = 0.0

    def _wait(self) -> None:
        wait = self.delay - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)

    def _request(self, method: str, url: str, stream: bool = False) -> requests.Response:
        last_exc: Exception | None = None
        for attempt in range(1, config.HTTP_RETRIES + 1):
            self._wait()
            try:
                r = self.session.request(method, url, timeout=config.HTTP_TIMEOUT, stream=stream, allow_redirects=True)
                self._last = time.monotonic()
                if r.status_code >= 500:
                    raise requests.HTTPError(f"HTTP {r.status_code}", response=r)
                r.raise_for_status()
                return r
            except requests.RequestException as exc:  # network error, 4xx or 5xx
                last_exc = exc
                self._last = time.monotonic()
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if status is not None and 400 <= status < 500:
                    break  # a missing file does not appear on retry
                backoff = 5 * attempt
                log.warning("%s %s failed (%s), retry %d in %ds", method, url, exc, attempt, backoff)
                time.sleep(backoff)
        raise RuntimeError(f"{method} {url} failed") from last_exc

    def get(self, url: str) -> requests.Response:
        return self._request("GET", url)

    def head(self, url: str) -> requests.Response:
        return self._request("HEAD", url)

    def download(self, url: str, dst: Path) -> int:
        """Stream ``url`` to ``dst`` (via a ``.part`` file); returns the size in bytes."""
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_name(dst.name + ".part")
        with self._request("GET", url, stream=True) as r, open(tmp, "wb") as f:
            f.writelines(r.iter_content(1 << 20))
        tmp.replace(dst)
        return dst.stat().st_size
