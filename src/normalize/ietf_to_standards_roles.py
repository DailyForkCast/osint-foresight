import argparse
from ..utils.io import main_stub

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    args = ap.parse_args()
    main_stub(args.country, "standards_roles.tsv")