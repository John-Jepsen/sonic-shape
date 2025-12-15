"""
EveryNoise scraping utilities.

Parses the public EveryNoise genre map to extract genre names, positions, and
preview URLs for downstream enrichment.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Dict, List, Optional

import requests

STYLE_RE = re.compile(
    r"color:\s*(?P<color>#[0-9a-fA-F]{6});\s*top:\s*(?P<top>[\d.]+)px;\s*left:\s*(?P<left>[\d.]+)px;\s*font-size:\s*(?P<font>[\d.]+)%",
    re.IGNORECASE,
)


def _parse_style(style: str) -> Dict[str, float | str]:
    m = STYLE_RE.search(style)
    if not m:
        return {}
    return {
        "color": m.group("color"),
        "top_px": float(m.group("top")),
        "left_px": float(m.group("left")),
        "font_size_pct": float(m.group("font")),
    }


class _GenreDivParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.records: List[Dict[str, object]] = []
        self.current: Optional[Dict[str, object]] = None

    def handle_starttag(self, tag, attrs):
        if tag != "div":
            return
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        if "genre" in cls:
            self.current = attrs_dict

    def handle_data(self, data):
        if self.current and data.strip():
            self.current["name"] = data.strip()
            style_meta = _parse_style(self.current.get("style", ""))
            self.current.update(style_meta)
            self.records.append(self.current)
            self.current = None


def parse_everynoise_html(html: str) -> List[Dict[str, object]]:
    """
    Parse EveryNoise genre map HTML and return a list of genre records.
    """
    parser = _GenreDivParser()
    parser.feed(html)
    return parser.records


def fetch_everynoise(url: str = "https://everynoise.com/engenremap.html", timeout: int = 60) -> List[Dict[str, object]]:
    """
    Fetch and parse the EveryNoise map.
    """
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return parse_everynoise_html(resp.text)

