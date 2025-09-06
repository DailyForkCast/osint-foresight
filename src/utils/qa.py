from pathlib import Path
from .io import SCHEMAS

class SchemaError(Exception):
    pass

def validate_headers(path: Path, expected: list[str]) -> None:
    # Lightweight header check (read first line only)
    with path.open("r", encoding="utf-8") as f:
        first = f.readline().strip().replace("\ufeff", "")
    delim = "\t" if path.suffix == ".tsv" else ","
    got = first.split(delim)
    if got != expected:
        raise SchemaError(f"Header mismatch in {path.name}.\nExpected: {expected}\nGot:      {got}")