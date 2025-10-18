#!/bin/bash
# PostgreSQL USASpending Database Restore

# 1. Create database
createdb -U postgres usaspending

# 2. Restore structure
pg_restore -U postgres -d usaspending -s F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/toc.dat

# 3. Restore data (selective)
for table in vendor contract award; do
    echo "Restoring $table..."
    pg_restore -U postgres -d usaspending -t $table -a F:/DECOMPRESSED_DATA/osint_data/OSINT_DATA/USAspending/usaspending-db_20250906/toc.dat
done
