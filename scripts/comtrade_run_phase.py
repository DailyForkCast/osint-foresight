"""
UN Comtrade Phase Runner
Quick script to run specific phases or resume from checkpoint
"""

import sys
from comtrade_collector_automated import ComtradeCollector


def main():
    if len(sys.argv) < 2:
        print("Usage: python comtrade_run_phase.py [phase_number|all|resume]")
        print()
        print("Options:")
        print("  1      - Run Phase 1 only (Core Technologies)")
        print("  2      - Run Phase 2 only (Strategic Expansion)")
        print("  3a     - Run Phase 3A only (Remaining Codes - Recent)")
        print("  3b     - Run Phase 3B only (Historical Data)")
        print("  all    - Run all phases in sequence")
        print("  resume - Resume from checkpoint")
        print()
        print("Examples:")
        print("  python comtrade_run_phase.py 1")
        print("  python comtrade_run_phase.py all")
        print("  python comtrade_run_phase.py resume")
        sys.exit(1)

    phase = sys.argv[1].lower()
    collector = ComtradeCollector()

    try:
        collector._connect_db()

        if phase == '1':
            print("Starting Phase 1: Core Technologies")
            print("This will take approximately 6-8 hours")
            print()
            collector.run_phase_1()

        elif phase == '2':
            print("Starting Phase 2: Strategic Expansion")
            print("This will take approximately 4-6 hours")
            print()
            collector.run_phase_2()

        elif phase == '3a':
            print("Starting Phase 3A: Remaining Codes (Recent Years)")
            print("This will take approximately 3-4 hours")
            print()
            collector.run_phase_3_recent()

        elif phase == '3b':
            print("Starting Phase 3B: Historical Data")
            print("This will take approximately 6-10 hours")
            print()
            collector.run_phase_3_historical()

        elif phase == 'all':
            print("Starting All Phases")
            print("Total time: 16-24 hours (will run over multiple days)")
            print()
            collector.run_all_phases()

        elif phase == 'resume':
            print("Resuming from checkpoint...")
            current_phase = collector.checkpoint.get('current_phase', 1)
            completed = len(collector.checkpoint.get('completed_requests', []))
            print(f"Current phase: {current_phase}")
            print(f"Completed requests: {completed:,}")
            print()
            collector.run_all_phases()

        else:
            print(f"Unknown phase: {phase}")
            sys.exit(1)

        collector._print_final_summary()

    except KeyboardInterrupt:
        print("\nCollection interrupted. Progress saved to checkpoint.")
        collector._save_checkpoint()
    except Exception as e:
        print(f"Error: {e}")
        collector._save_checkpoint()
        raise
    finally:
        if collector.db_conn:
            collector.db_conn.close()


if __name__ == '__main__':
    main()
