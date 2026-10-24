#!/usr/bin/env python3
"""
LUNA: Chief Executive Multi-Agent System Entry Point.
Supports both Interactive Terminal CLI and Web Dashboard.
"""
import sys
import argparse
import asyncio

# Ensure UTF-8 output encoding across Windows terminals
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def parse_args():
    parser = argparse.ArgumentParser(description="LUNA Chief Executive Multi-Agent System")
    parser.add_argument("--web", action="store_true", help="Launch the Executive Web Dashboard & WebSocket Server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address for Web Server (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port for Web Server (default: 8000)")
    return parser.parse_args()

def run_web(host: str, port: int):
    import uvicorn
    print(f"\n✦ LUNA Executive Web Server starting at http://{host}:{port}")
    print("Press Ctrl+C to terminate the server.\n")
    uvicorn.run("luna.api.server:app", host=host, port=port, reload=False, log_level="info")

def main():
    args = parse_args()
    try:
        if args.web:
            run_web(args.host, args.port)
        else:
            from luna.cli.console import run_cli
            asyncio.run(run_cli())
    except KeyboardInterrupt:
        print("\nSession ended.")
        sys.exit(0)

if __name__ == "__main__":
    main()
