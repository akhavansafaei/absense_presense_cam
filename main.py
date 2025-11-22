#!/usr/bin/env python3
"""
Webcam Attendance System
A simple face recognition-based attendance monitoring system.
"""

import sys
from ui import CLIInterface


def main():
    """Main entry point for the application."""
    try:
        print("\n" + "="*70)
        print(" "*15 + "WEBCAM ATTENDANCE SYSTEM")
        print(" "*20 + "Initializing...")
        print("="*70)

        # Initialize and run the CLI interface
        cli = CLIInterface()
        cli.run()

    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
