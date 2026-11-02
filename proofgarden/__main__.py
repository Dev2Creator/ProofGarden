"""Allow ``python -m proofgarden``."""

import sys

from .cli.main import main

if __name__ == "__main__":
    sys.exit(main())
