#!/usr/bin/env python3
"""
Logged Octave shell wrapper.
Runs an interactive Octave session with logging of all inputs and outputs.
"""

import sys
import os
import subprocess
import datetime
import select
import time
from pathlib import Path


def ensure_log_dir():
    """Ensure the logs directory exists."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    return log_dir / "txt.log"


def format_timestamp():
    """Generate a timestamp string in the format [YYYY-MM-DD HH:MM:SS]."""
    return datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def log_message(log_file, direction, message):
    """
    Log a message to the log file.
    
    Args:
        log_file: Path to the log file
        direction: Either 'IN' or 'OUT'
        message: The message content to log
    """
    with open(log_file, 'a', encoding='utf-8') as f:
        timestamp = format_timestamp()
        f.write(f"{timestamp} [{direction}] {message}\n")


def run_octave_logged():
    """
    Run an interactive Octave shell with logging.
    
    Every user input is logged as [TIMESTAMP] [IN] ...
    Every Octave output is logged as [TIMESTAMP] [OUT] ...
    """
    log_file = ensure_log_dir()
    
    print("Starting logged Octave shell...")
    print(f"Logs will be written to: {log_file}")
    print("Type 'quit' or 'exit' to exit Octave.")
    print("-" * 60)
    
    try:
        # Start Octave process in interactive mode
        process = subprocess.Popen(
            ['octave', '--interactive', '--quiet'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Give Octave a moment to start
        time.sleep(0.5)
        
        while True:
            # Display prompt
            sys.stdout.write("octave> ")
            sys.stdout.flush()
            
            # Read user input
            try:
                user_input = input()
            except EOFError:
                print("\nExiting...")
                break
            
            # Log the input
            log_message(log_file, "IN", user_input)
            
            # Check for exit commands
            if user_input.strip() in ['quit', 'exit', 'quit()', 'exit()']:
                process.stdin.write(user_input + "\n")
                process.stdin.flush()
                break
            
            # Send input to Octave
            process.stdin.write(user_input + "\n")
            process.stdin.flush()
            
            # Read and display output
            output_lines = []
            time.sleep(0.2)  # Give Octave time to process
            
            # Try to read available output
            while True:
                ready, _, _ = select.select([process.stdout], [], [], 0.1)
                if not ready:
                    break
                    
                line = process.stdout.readline()
                if not line:
                    break
                    
                # Display to user
                print(line, end='')
                output_lines.append(line.rstrip('\n'))
            
            # Log all output
            for line in output_lines:
                if line.strip():  # Only log non-empty lines
                    log_message(log_file, "OUT", line)
            
            # Check if process has terminated
            if process.poll() is not None:
                break
        
        # Clean up
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=2)
            
    except FileNotFoundError:
        print("\nError: Octave is not installed or not in PATH.")
        print("Please install GNU Octave to use this tool.")
        print("  Ubuntu/Debian: sudo apt-get install octave")
        print("  macOS: brew install octave")
        return 1
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        if 'process' in locals() and process.poll() is None:
            process.terminate()
            process.wait(timeout=2)
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    print("\nLogged Octave session ended.")
    print(f"Logs saved to: {log_file}")
    return 0


if __name__ == "__main__":
    sys.exit(run_octave_logged())
