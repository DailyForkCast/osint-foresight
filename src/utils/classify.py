from __future__ import annotations
from collections import Counter
import re

# Build a simple keyword search across sectors (case-insensitive).
# keywords_map format: { sector: {"en": [..], "local": [..], "zh": [..]} }

def tokenize(text: str) -> list[str]:
    return re.findall(r"[\w\-\+/#\.]+", (text or "").lower())


def score_sectors(text: str, keywords_map: dict) -> tuple[list[str], dict[str, int]]:
    toks = tokenize(text)
    counts = {sector: 0 for sector in keywords_map.keys()}
    # naive: count substring matches for multiword kws, token matches otherwise
    tset = set(toks)
    for sector, langs in keywords_map.items():
        kws = []
        for lang in ("en","local","zh"):
            kws += (langs or {}).get(lang, [])
        for kw in kws:
            kw_l = kw.lower()
            if " " in kw_l or any(ch in kw_l for ch in ['*']):
                # wildcard/star — very loose: check containment sans star
                kw_pat = kw_l.replace('*','')
                if kw_pat and kw_pat in (text or "").lower():
                    counts[sector] += 1
            else:
                if kw_l in tset:
                    counts[sector] += 1
    # sectors by score
    ordered = [s for s,_ in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])) if counts[s] > 0]
    return ordered, counts


def primary_sector(text_blocks: list[str], keywords_map: dict) -> tuple[str, dict[str,int]]:
    text = " \n ".join([t for t in text_blocks if t])
    ordered, counts = score_sectors(text, keywords_map)
    return (ordered[0] if ordered else ""), counts


def bucket_intensity(n: int) -> int:
    # 0–3 buckets. Tune thresholds later if needed.
    if n <= 0: return 0
    if n <= 2: return 1
    if n <= 5: return 2
    return 3