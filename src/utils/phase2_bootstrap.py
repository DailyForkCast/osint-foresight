import argparse, csv, os, sys
from datetime import date

HEADERS = {
    "domain_maturity.tsv": ["domain_id","domain","maturity_band","rationale","key_signals","confidence_LMH","notes"],
    "facilities.tsv": ["facility","type","location","access_mode","relevance","notes"],
    "sanctions_hits.csv": ["list_name","entity_name","country","link","last_check","notes"],
}

SEED_ROWS = {
    "domain_maturity.tsv": [{"domain_id":"D0","domain":"(seed)","maturity_band":"","rationale":"","key_signals":"","confidence_LMH":"","notes":"no_data_yet=true"}],
    "facilities.tsv": [{"facility":"(seed)","type":"","location":"","access_mode":"","relevance":"","notes":"no_data_yet=true"}],
    "sanctions_hits.csv": [{"list_name":"(seed)","entity_name":"","country":"","link":"","last_check":str(date.today()),"notes":"no_data_yet=true (non-US persons policy applies)"}],
}

def ensure_file(path, headers, seed=True):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Decide delimiter by extension
        delim = '\t' if path.endswith('.tsv') else ','
        with open(path, 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=headers, delimiter=delim)
            w.writeheader()
            if seed:
                # Write a single seed row (empty fields filled by DictWriter)
                for row in SEED_ROWS[os.path.basename(path)]:
                    w.writerow(row)
        return True
    return False

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--country", required=True, help="ISO2 code, e.g., AT")
    p.add_argument("--no-seed", action="store_true", help="Create headers only")
    args = p.parse_args()

    base = os.path.join("data","processed",f"country={args.country}")
    created = []
    for fname in ("domain_maturity.tsv","facilities.tsv","sanctions_hits.csv"):
        path = os.path.join(base, fname)
        if ensure_file(path, HEADERS[fname], seed=not args.no_seed):
            created.append(path)
    print("Created:" if created else "All present:")
    for c in created:
        print(" - ", c)