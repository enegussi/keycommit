import os, sys
# Add the project root (…/keycommit) to sys.path so "app" can be imported
# Example: if this file is /Users/you/Desktop/keycommit/tests/conftest.py
# then project_root becomes /Users/you/Desktop/keycommit
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
