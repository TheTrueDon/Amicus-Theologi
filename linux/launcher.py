"""Linux entry point. Uses the proven local controller shared with Windows.

For a built DEB this executable includes Python and all required packages.
The user never has to install Python or run a shell to launch Amicus.
"""
from pathlib import Path
import sys

if not getattr(sys, 'frozen', False):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from windows.launcher import main

if __name__ == '__main__':
    sys.exit(main())
