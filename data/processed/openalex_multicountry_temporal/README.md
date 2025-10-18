# OpenAlex Multi-Country Temporal Analysis

## Overview

This directory contains the infrastructure and results for comprehensive analysis of China's research collaborations using the 422GB OpenAlex dataset across 60+ countries and 25 years (2000-2025).

## Directory Structure

```
openalex_multicountry_temporal/
├── by_country/           # Country-specific China collaborations
│   ├── US_china/        # US-China collaborations
│   ├── DE_china/        # Germany-China collaborations
│   └── [ALL_COUNTRIES]/ # Each country's partnerships
├── by_period/           # Temporal analysis
│   ├── pre_bri_baseline_2000_2012/
│   ├── bri_launch_2013_2016/
│   ├── expansion_2017_2019/
│   ├── trade_war_2020_2021/
│   └── decoupling_2022_2025/
├── by_technology/       # Technology-specific analysis
│   ├── artificial_intelligence/
│   ├── quantum_computing/
│   ├── semiconductors/
│   └── [ALL_TECH_AREAS]/
├── patterns/           # Collaboration pattern analysis
├── networks/           # Network analysis results
├── analysis/           # Comprehensive reports
└── verification/       # Data integrity verification
```

## Zero Fabrication Protocol

- Every finding traceable to specific JSONL line
- Complete verification hashes for all records
- Source file and line number documentation
- No interpolation or estimation of missing data

## Usage

### Run Full Analysis
```bash
python scripts/process_openalex_multicountry_temporal.py --resume-checkpoint
```

### Run Limited Test
```bash
python scripts/process_openalex_multicountry_temporal.py --max-files 10
```

### Generate Reports
```bash
python scripts/generate_openalex_strategic_intelligence_report.py
```

## Output Files

- `collaborations_TIMESTAMP.json` - Detailed collaboration records
- `analysis_TIMESTAMP.json` - Statistical analysis
- `EXECUTIVE_BRIEFING.md` - Strategic intelligence summary
- `processing_checkpoint.json` - Resume point for large processing

## Data Verification

All results include verification section:
```json
{
  "verification": {
    "source_file": "works_part_00001.jsonl.gz",
    "line_number": 1247893,
    "extraction_command": "sed -n '1247893p' works_part_00001.jsonl | jq '.title'",
    "paper_hash": "a1b2c3d4e5f6..."
  }
}
```

## Requirements

- 32GB RAM minimum for streaming processing
- 422GB OpenAlex data at F:/OSINT_Backups/openalex/data/
- Python 3.8+ with json, gzip, pathlib, collections
