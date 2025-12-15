"""
Legacy entrypoint (kept for backwards compatibility).

Run:
  python "DS5 Quickchats RL.py"

This delegates to the maintained script:
  DS5QuickchatsRL.py
"""

from DS5QuickchatsRL import main


if __name__ == "__main__":
    raise SystemExit(main())

