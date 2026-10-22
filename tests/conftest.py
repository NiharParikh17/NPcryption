"""
Shared pytest configuration and fixtures for NPcryption tests.
"""
import sys
import os

# Ensure the src directory is on sys.path so npcryption
# can be found even without an editable install.
_SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
