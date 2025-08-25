#!/usr/bin/env python3
"""
Main entry point for Jakarta Maps Analyzer
Runs the pet market analysis for Jakarta
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.runners.main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error running analysis: {e}")
        sys.exit(1)