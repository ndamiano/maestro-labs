"""Shared lab code. Importing it puts maestro's src on sys.path, so `from lib import ...` is the
only bootstrap a lab script needs."""
from lib.paths import bootstrap

bootstrap()
