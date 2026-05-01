#!/usr/bin/env python3
"""Simple Timer Application"""

import time
import sys
import argparse
from datetime import datetime, timedelta
import platform
import os

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def format_time(seconds):
    """Format seconds into HH:MM:SS format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def ring_bell():
    """Ring the system bell."""
    print('\a', end='', flush=True)
    for _ in range(3):
        time.sleep(0.3)
        print('\a', end='', flush=True)

def run_timer(total_seconds, show_time=False):
    """Run the timer countdown."""
    start_time = time.time()
    end_time = start_time + total_seconds

    print(f"⏱️  Timer started for {format_time(total_seconds)}")
    if show_time:
        print(f"   Will finish at: {(datetime.now() + timedelta(seconds=total_seconds)).strftime('%H:%M:%S')}")
    print()

    try:
        while True:
            now = time.time()
            remaining = end_time - now

            if remaining <= 0:
                clear_screen()
                print("=" * 40)
                print("       ⏰ TIME'S UP! ⏰")
                print("=" * 40)
                ring_bell()
                break

            # Update display every 0.1 seconds
            sys.stdout.write(f"\r⏱️  Time remaining: {format_time(int(remaining))}")
            sys.stdout.flush()
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\n⛔ Timer cancelled")
        return False

    return True

def main():
    parser = argparse.ArgumentParser(
        description='Simple Timer Application',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python timer.py 5m          # Set a 5-minute timer
  python timer.py 30s         # Set a 30-second timer
  python timer.py 1h 30m      # Set a 1 hour 30 minute timer
  python timer.py 300         # Set a 300-second timer
  python timer.py 5m --time   # Show finish time
        '''
    )

    parser.add_argument(
        'duration',
        nargs='*',
        help='Timer duration (e.g., 5m, 30s, 1h 30m, or seconds as integer)'
    )
    parser.add_argument(
        '--time', '-t',
        action='store_true',
        help='Show the finish time'
    )

    args = parser.parse_args()

    if not args.duration:
        parser.print_help()
        print("\n❌ Error: Please specify a duration")
        sys.exit(1)

    # Parse duration
    total_seconds = 0

    try:
        # If single argument that's a number, treat as seconds
        if len(args.duration) == 1 and args.duration[0].isdigit():
            total_seconds = int(args.duration[0])
        else:
            # Parse time units (e.g., 5m, 30s, 1h)
            for part in args.duration:
                if part.endswith('h') or part.endswith('hour'):
                    total_seconds += int(part.rstrip('hour')) * 3600
                elif part.endswith('m') or part.endswith('min'):
                    total_seconds += int(part.rstrip('min')) * 60
                elif part.endswith('s') or part.endswith('sec'):
                    total_seconds += int(part.rstrip('sec'))
                elif part.isdigit():
                    total_seconds += int(part)
                else:
                    raise ValueError(f"Invalid time format: {part}")

        if total_seconds <= 0:
            print("❌ Error: Duration must be greater than 0")
            sys.exit(1)

        success = run_timer(total_seconds, args.time)
        sys.exit(0 if success else 1)

    except (ValueError, IndexError) as e:
        print(f"❌ Error: {e}")
        print("\nUsage examples:")
        print("  python timer.py 5m          # 5 minutes")
        print("  python timer.py 30s         # 30 seconds")
        print("  python timer.py 1h 30m      # 1 hour 30 minutes")
        print("  python timer.py 300         # 300 seconds")
        sys.exit(1)

if __name__ == '__main__':
    main()
