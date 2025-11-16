"""
OpenAlex V4 - Concurrent Processing by Date Ranges
Implements USPTO NULL data methodology for capturing "uncertain" works
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime

# Configuration
OPENALEX_DATA = Path("F:/OSINT_Backups/openalex/data/works")
PROJECT_ROOT = Path("C:/Projects/OSINT - Foresight")

# Processing parameters
MAX_PER_TECH = 25000  # Increased from 10,000
STRICTNESS = "moderate"
NUM_CONCURRENT_PROCESSES = 4  # Run 4 parallel processes

def get_date_directories():
    """Get all date directories sorted chronologically"""
    date_dirs = sorted(OPENALEX_DATA.glob('updated_date=*'))
    print(f"Found {len(date_dirs)} date directories")
    print(f"Date range: {date_dirs[0].name} to {date_dirs[-1].name}")
    return date_dirs

def partition_directories(date_dirs, num_partitions):
    """Partition directories into chunks for concurrent processing"""
    chunk_size = len(date_dirs) // num_partitions
    partitions = []

    for i in range(num_partitions):
        start_idx = i * chunk_size
        if i == num_partitions - 1:
            # Last partition gets remaining directories
            end_idx = len(date_dirs)
        else:
            end_idx = (i + 1) * chunk_size

        partition_dirs = date_dirs[start_idx:end_idx]
        partitions.append({
            'id': i + 1,
            'start_date': partition_dirs[0].name,
            'end_date': partition_dirs[-1].name,
            'num_dirs': len(partition_dirs),
            'dirs': [str(d) for d in partition_dirs]
        })

    return partitions

def create_partition_config(partitions):
    """Save partition configuration"""
    config_file = PROJECT_ROOT / "config" / "openalex_concurrent_partitions.json"

    with open(config_file, 'w') as f:
        json.dump({
            'created': datetime.now().isoformat(),
            'num_partitions': len(partitions),
            'max_per_tech': MAX_PER_TECH,
            'strictness': STRICTNESS,
            'partitions': partitions
        }, f, indent=2)

    print(f"\n[OK] Partition configuration saved to: {config_file}")
    return config_file

def launch_concurrent_processes(partitions):
    """Launch concurrent OpenAlex processing for each partition"""

    processes = []

    for partition in partitions:
        partition_id = partition['id']
        start_date = partition['start_date']
        end_date = partition['end_date']

        # Create partition-specific script arguments
        # We'll need to modify the main script to accept date range filters

        log_file = PROJECT_ROOT / f"openalex_v4_partition_{partition_id}.log"

        # Command to run
        cmd = [
            "python",
            str(PROJECT_ROOT / "scripts" / "integrate_openalex_concurrent_worker.py"),
            "--partition-id", str(partition_id),
            "--start-date", start_date,
            "--end-date", end_date,
            "--max-per-tech", str(MAX_PER_TECH),
            "--strictness", STRICTNESS
        ]

        print(f"\n[Partition {partition_id}] Launching process:")
        print(f"  Date range: {start_date} to {end_date}")
        print(f"  Directories: {partition['num_dirs']}")
        print(f"  Log file: {log_file}")

        # Launch process in background
        with open(log_file, 'w') as log:
            process = subprocess.Popen(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=str(PROJECT_ROOT)
            )
            processes.append({
                'id': partition_id,
                'process': process,
                'log_file': log_file
            })

    return processes

def monitor_processes(processes):
    """Monitor concurrent processes"""
    import time

    print(f"\n{'=' * 80}")
    print(f"MONITORING {len(processes)} CONCURRENT PROCESSES")
    print(f"{'=' * 80}\n")

    while True:
        all_done = True

        for proc_info in processes:
            status = proc_info['process'].poll()
            if status is None:
                all_done = False
                print(f"[Partition {proc_info['id']}] Still running... (check {proc_info['log_file'].name})")
            else:
                if status == 0:
                    print(f"[Partition {proc_info['id']}] COMPLETED (exit code: {status})")
                else:
                    print(f"[Partition {proc_info['id']}] ERROR (exit code: {status})")

        if all_done:
            break

        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking again in 60 seconds...")
        time.sleep(60)

    print(f"\n{'=' * 80}")
    print("ALL CONCURRENT PROCESSES COMPLETE")
    print(f"{'=' * 80}\n")

if __name__ == '__main__':
    print(f"{'=' * 80}")
    print("OPENALEX V4 - CONCURRENT PROCESSING LAUNCHER")
    print(f"{'=' * 80}\n")

    # Get date directories
    date_dirs = get_date_directories()

    # Partition into chunks
    print(f"\nPartitioning into {NUM_CONCURRENT_PROCESSES} concurrent processes...")
    partitions = partition_directories(date_dirs, NUM_CONCURRENT_PROCESSES)

    print("\nPartition Summary:")
    for p in partitions:
        print(f"  Partition {p['id']}: {p['start_date']} to {p['end_date']} ({p['num_dirs']} dirs)")

    # Save configuration
    config_file = create_partition_config(partitions)

    # Ask for confirmation
    print(f"\n{'=' * 80}")
    print("CONFIGURATION:")
    print(f"{'=' * 80}")
    print(f"  Concurrent processes: {NUM_CONCURRENT_PROCESSES}")
    print(f"  Max works per technology: {MAX_PER_TECH:,}")
    print(f"  Validation strictness: {STRICTNESS}")
    print(f"  Total expected: ~{MAX_PER_TECH * 9:,} works per partition")
    print(f"  Combined total: ~{MAX_PER_TECH * 9 * NUM_CONCURRENT_PROCESSES:,} works")
    print()

    # Auto-launch (no interactive prompt needed)
    print("\n[AUTO-LAUNCH] Starting concurrent processing...")

    # Launch processes
    print(f"\n{'=' * 80}")
    print("LAUNCHING CONCURRENT PROCESSES")
    print(f"{'=' * 80}")

    processes = launch_concurrent_processes(partitions)

    # Monitor until complete
    monitor_processes(processes)

    print("\n[OK] All concurrent processes completed.")
    print(f"\nNext step: Merge results into master database")
