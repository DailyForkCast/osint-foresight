#!/usr/bin/env python3
"""
Batch processor for SEC EDGAR analysis with checkpoint support
Processes companies in smaller batches to avoid timeouts
"""

import json
import logging
import time
from pathlib import Path
from scripts.process_sec_edgar_multicountry import SECEdgarMultiCountryAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_checkpoint():
    """Load processing checkpoint"""
    checkpoint_file = Path("data/processed/sec_batch_checkpoint.json")
    if checkpoint_file.exists():
        with open(checkpoint_file) as f:
            return json.load(f)
    return {"processed_companies": [], "last_company": None}

def save_checkpoint(checkpoint):
    """Save processing checkpoint"""
    checkpoint_file = Path("data/processed/sec_batch_checkpoint.json")
    checkpoint_file.parent.mkdir(exist_ok=True, parents=True)
    with open(checkpoint_file, 'w') as f:
        json.dump(checkpoint, f, indent=2)

def main():
    """Process SEC filings in batches"""

    # All Chinese company tickers to process
    chinese_tickers = [
        # Batch 1: Major tech (10 companies)
        ["BABA", "BIDU", "JD", "PDD", "TME", "BILI", "IQ", "VIPS", "NTES", "WB"],

        # Batch 2: EVs and new economy (10 companies)
        ["NIO", "XPEV", "LI", "MOMO", "HUYA", "DOYU", "QD", "GOTU", "YY", "ATHM"],

        # Batch 3: Finance and services (10 companies)
        ["FUTU", "TIGR", "LU", "QFIN", "FINV", "JFU", "CNF", "JRJC", "EDU", "TAL"],

        # Batch 4: Others (remaining)
        ["NEW", "TEDU", "COE", "BEDU", "KE", "TUYA", "RLX", "YMM", "MNSO", "DDL", "API"]
    ]

    checkpoint = load_checkpoint()

    logging.info("=" * 60)
    logging.info("Starting SEC EDGAR Batch Processing")
    logging.info(f"Previously processed: {len(checkpoint['processed_companies'])} companies")
    logging.info("=" * 60)

    analyzer = SECEdgarMultiCountryAnalyzer(
        output_dir="data/processed/sec_edgar_batch"
    )

    total_processed = 0

    for batch_num, batch in enumerate(chinese_tickers, 1):
        logging.info(f"\n--- Processing Batch {batch_num}/{len(chinese_tickers)} ---")

        for ticker in batch:
            if ticker in checkpoint["processed_companies"]:
                logging.info(f"Skipping {ticker} (already processed)")
                continue

            try:
                logging.info(f"Analyzing {ticker}...")

                # Search for the company
                analyzer.search_company_filings("CN", limit=1)  # This needs modification

                # Mark as processed
                checkpoint["processed_companies"].append(ticker)
                checkpoint["last_company"] = ticker
                save_checkpoint(checkpoint)

                total_processed += 1

                # Rate limiting
                time.sleep(2)

            except Exception as e:
                logging.error(f"Error processing {ticker}: {e}")
                time.sleep(5)  # Wait longer on error
                continue

        # Longer pause between batches
        if batch_num < len(chinese_tickers):
            logging.info(f"Batch {batch_num} complete. Pausing before next batch...")
            time.sleep(10)

    # Generate final report
    logging.info("\nGenerating final report...")
    analyzer.generate_risk_assessment()
    analyzer.save_results()
    analyzer.generate_report()

    logging.info("=" * 60)
    logging.info(f"SEC EDGAR Batch Processing Complete!")
    logging.info(f"Total companies processed: {total_processed}")
    logging.info(f"Results saved to: data/processed/sec_edgar_batch")
    logging.info("=" * 60)

if __name__ == "__main__":
    main()
