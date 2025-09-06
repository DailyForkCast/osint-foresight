import argparse, json
from pathlib import Path
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("--country", required=True)
parser.add_argument("--years", default="2015-2025")
parser.add_argument("--out", required=True)
args = parser.parse_args()

outdir = Path(args.out)
outdir.mkdir(parents=True, exist_ok=True)
outfile = outdir / f"openaire_stub_{args.country.upper()}_{datetime.utcnow().date()}.jsonl"

with outfile.open("w", encoding="utf-8") as f:
    f.write(json.dumps({"note": "stub pull", "country": args.country, "years": args.years}) + "\n")

print(f"Wrote {outfile}")