import argparse, json
from pathlib import Path
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--country", required=True)
parser.add_argument("--query-file", required=False)
parser.add_argument("--out", required=True)
args = parser.parse_args()

outdir = Path(args.out)
outdir.mkdir(parents=True, exist_ok=True)
outfile = outdir / f"crossref_stub_{args.country.upper()}_{datetime.utcnow().date()}.jsonl"
outfile.write_text(json.dumps({"note": "stub pull", "country": args.country}) + "\n", encoding="utf-8")
print(f"Wrote {outfile}")