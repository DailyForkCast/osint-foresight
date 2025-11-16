# Eurostat COMEXT Bulk Download - Step-by-Step Guide

**Date**: 2025-10-30
**Purpose**: Get the COMPLETE ds-056120 dataset (not the API sample)

---

## The Problem

The Eurostat website has TWO ways to access data:
1. **API endpoints** (what you accidentally used) - Returns tiny samples (18K records)
2. **Bulk download files** (what you need) - Contains complete datasets (10M+ records)

---

## Step-by-Step Instructions

### Step 1: Go to the Bulk Download Portal

**URL**: https://ec.europa.eu/eurostat/databrowser/bulk?lang=en&selectedTab=fileComext

**What you should see**:
- A page titled "Bulk Download" or "Eurost Bulk Download Facility"
- Tabs at the top: "Tables", "fileComext", etc.
- Click the "**fileComext**" tab

### Step 2: Find the Dataset

**Look for these characteristics**:

- **Folder/Section**: "External trade by HS/CN classification"
- **Dataset code**: Contains "056120" or similar
- **File name patterns** to look for:
  - `comext_monthly_*.7z` or `comext_monthly_*.zip`
  - `full_*.tsv.gz` or `full_*.csv.gz`
  - Any file with "CN8" or "HS" in the name

- **File size indicators**: Should show MB or GB, not KB
  - Look for files showing: "1.5 GB", "800 MB", etc.
  - Avoid files showing: "110 KB", "250 KB", etc.

### Step 3: Alternative - Use FTP/Direct Links

If the web interface is confusing, try the FTP server:

**FTP Access**:
```
ftp://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=comext
```

Or direct bulk files page:
```
https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&file=comext
```

**What to download**:
- Look for files dated 2024 or 2025 (recent)
- File names like:
  - `NC_XXXXXXXX.dat` (large .dat files)
  - `comext_products.txt` (product reference)
  - Compressed archives (.7z, .gz, .zip)

### Step 4: Verify Before Downloading

**Before you click download, check**:
- ✅ File size is AT LEAST 500 MB (preferably 1-2 GB)
- ✅ File name includes "full", "complete", or "monthly"
- ✅ Not an XML or JSON file (those are usually metadata)
- ❌ NOT from a URL containing "/api/"
- ❌ NOT a "sample" or "preview" file

### Step 5: Download Location

Save to:
```
F:\OSINT_Data\Trade_Facilities\eurostat_comext_bulk\
```

---

## Alternative: Easy Comext for Targeted Queries

If you can't find the bulk download, use the Easy Comext interface for custom exports:

**URL**: https://ec.europa.eu/eurostat/comext/newxtweb/

**Steps**:
1. Select "Reporter": All EU27 countries (or select specific ones)
2. Select "Partner": China (CN), Hong Kong (HK)
3. Select "Product":
   - CN8 code: 8542 (semiconductors)
   - CN8 code: 8541 (semiconductor devices)
   - CN8 code: 2846 (rare earths)
   - (Or select all products if available)
4. Select "Period": 2000-2024, Monthly
5. Click "Export" → CSV format
6. Wait for generation (may take several minutes for large queries)
7. Download the CSV file

**Advantages**:
- Can get exactly what you need (China trade only)
- No need to process entire 10M record dataset
- Still free, no API key needed

**Disadvantages**:
- May be limited to 1M rows per query
- Requires multiple queries for all products
- Manual process (not automated)

---

## Troubleshooting

### Issue: Can't find ds-056120 on bulk download page

**Solution**:
- The dataset code may be embedded in a larger file
- Look for "Monthly detailed data" or "CN8 classification"
- Download ANY large (>500MB) trade file - they often contain the same data with different organization

### Issue: All files seem to be samples

**Solution**:
- Eurostat may have changed their interface
- Try the FTP access method instead
- Or use Easy Comext to generate custom exports

### Issue: File downloads are very slow

**Solution**:
- These are large files (1-2 GB) and may take 10-30 minutes
- Use a download manager if possible
- Ensure stable internet connection
- Don't use Wi-Fi if you can avoid it

---

## Verification After Download

Once downloaded, verify you have the right file:

```bash
# Check file size (should be >500 MB)
ls -lh your_downloaded_file.gz

# Count lines (should be millions, not thousands)
gunzip -c your_file.gz | wc -l

# Expected: 10,000,000+ lines (10 million)
# If you see: <100,000 lines, it's NOT the bulk download
```

---

## Next Steps After Successful Download

1. **Move file** to: `F:\OSINT_Data\Trade_Facilities\eurostat_comext_bulk\`

2. **Filter for China**:
   ```bash
   python scripts/filter_eurostat_bulk_china.py
   ```

3. **Load into master database**:
   ```bash
   python scripts/load_eurostat_into_master.py
   ```

4. **Analysis ready**: Query EU-China trade from master database

---

## Summary: What Makes This Confusing

**The Eurostat interface mixes**:
- API endpoints (for developers, limited data)
- Bulk downloads (for researchers, complete data)
- Interactive tools (for casual users, manual queries)

**Key distinction**:
- If the URL contains `/api/`, it's the API (limited)
- If the URL contains `/bulk/` or shows file sizes, it's correct
- If you're clicking "Download" on a giant file list, you're in the right place

---

## Contact

If still stuck after following this guide:
- Email Eurostat help desk: estat-user-support@ec.europa.eu
- Reference: "Looking for ds-056120 complete monthly data in CN8 format"
- They should be able to provide direct link to the correct file

---

**End of Guide**

**Status**: Awaiting user to download the correct bulk file
**Current file**: F:/ds-056120$defaultview_linear.csv.gz (18K records, INCORRECT)
**Target**: 10M+ record bulk download
