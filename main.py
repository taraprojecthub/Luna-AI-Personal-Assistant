#!/usr/bin/env python3
"""
LUNA: Chief Executive Multi-Agent System Entry Point.
"""
import sys
import asyncio

# Ensure UTF-8 output encoding across Windows terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def main():
    try:
        from luna.cli.console import run_cli
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        print("\nSession ended.")
        sys.exit(0)

if __name__ == "__main__":
    main()
