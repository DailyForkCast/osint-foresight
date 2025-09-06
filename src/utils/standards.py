from pathlib import Path
import yaml

DEF_MAP = {
    # fallback if file not present
    "detnet": "Edge Comms & Spectrum",
    "mls": "Cyber/Secure Comms",
    "cbor": "AI/HPC/Data",
}

MAP_PATH = Path("taxonomies/mappings/standards_map.yaml")

def wg_sector_map() -> dict:
    if MAP_PATH.exists():
        data = yaml.safe_load(MAP_PATH.read_text(encoding="utf-8")) or []
        out = {}
        for row in data:
            acr = str(row.get("acronym","")) .strip().lower()
            if acr:
                out[acr] = row.get("sector","")
        return out or DEF_MAP
    return DEF_MAP