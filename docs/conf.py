# pylint: disable=all
"""Configuration file for the Sphinx documentation builder."""
import sys
from pathlib import Path

import sphinx.application

# Path setup
DOCS = Path(__file__).parent
SRC = DOCS.parent.joinpath("src")
sys.path.append(str(SRC))

# Project information
project = "maya-tools"
author = "Fabien Taxil"
copyright = f"2022, {author}"

# General configuration
extensions = ["myst_parser"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Options for HTML output
html_theme = "sphinx_material"
html_static_path = ["_static"]


def setup(app: sphinx.application.Sphinx) -> None:
    """Plugin entry point."""
