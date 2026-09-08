import sys
from pathlib import Path

# The tool lives outside the repo and imports it: the harness under test is maestro's own runner,
# tools and turn log, not a copy of them.
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path.home() / "Documents" / "ai-agent-test" / "src"))
