#!/usr/bin/env python3
"""
LUNA: Chief Executive Multi-Agent System Entry Point.
"""
import sys
import asyncio

def main():
    try:
        from luna.cli.console import run_cli
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        print("\nSession ended.")
        sys.exit(0)

if __name__ == "__main__":
    main()
