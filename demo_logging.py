#!/usr/bin/env python3
"""
Demo script to simulate logged Octave behavior.
This creates sample log entries to demonstrate the logging format.
"""

import sys
import time
from run_octave_logged import ensure_log_dir, log_message


def demo_logging():
    """Create sample log entries to demonstrate the system."""
    print("=" * 60)
    print("Demo: Creating sample Octave log entries")
    print("=" * 60)
    print()
    
    log_file = ensure_log_dir()
    print(f"Log file: {log_file.absolute()}")
    print()
    
    # Sample Octave session
    demo_commands = [
        ("IN", "x = 5"),
        ("OUT", "x = 5"),
        ("IN", "y = x * 2"),
        ("OUT", "y = 10"),
        ("IN", "A = [1 2 3; 4 5 6; 7 8 9]"),
        ("OUT", "A ="),
        ("OUT", "   1   2   3"),
        ("OUT", "   4   5   6"),
        ("OUT", "   7   8   9"),
        ("IN", "det(A)"),
        ("OUT", "ans = 0"),
        ("IN", "% Calculate eigenvalues"),
        ("OUT", ""),
        ("IN", "eig(A)"),
        ("OUT", "ans ="),
        ("OUT", "  16.1168"),
        ("OUT", "  -1.1168"),
        ("OUT", "   0.0000"),
        ("IN", "% Three-body problem initial conditions"),
        ("OUT", ""),
        ("IN", "m1 = 1.0; m2 = 1.0; m3 = 1.0;"),
        ("OUT", ""),
        ("IN", "G = 6.67430e-11"),
        ("OUT", "G = 6.6743e-11"),
        ("IN", "disp('Numerical integration required for general solution')"),
        ("OUT", "Numerical integration required for general solution"),
    ]
    
    print("Creating log entries...")
    for i, (direction, message) in enumerate(demo_commands, 1):
        log_message(log_file, direction, message)
        print(f"  [{i}/{len(demo_commands)}] Logged: {direction} - {message[:50]}...")
        time.sleep(0.05)  # Small delay for timestamps
    
    print()
    print("✓ Demo log entries created successfully!")
    print()
    print("To view the logs:")
    print("  1. Run: python3 log_server.py")
    print("  2. Open: http://localhost:8000/")
    print()
    print("Or view directly:")
    print(f"  cat {log_file}")
    print()
    
    # Display a sample of the log
    print("=" * 60)
    print("Sample log output:")
    print("=" * 60)
    with open(log_file, 'r') as f:
        lines = f.readlines()
        for line in lines[:5]:
            print(line.rstrip())
    print("  ...")
    print(f"  ({len(lines)} total lines)")
    print("=" * 60)


if __name__ == "__main__":
    try:
        demo_logging()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
