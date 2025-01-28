#!/bin/bash

# Get version from pyproject.toml
VERSION=$(python3 -c "import tomli; print(tomli.load(open('pyproject.toml', 'rb'))['project']['version'])")

# Build the package
python3 -m build

# Create GitHub release
gh release create v${VERSION} ./dist/* \
  --title "Release v${VERSION}" \
  --generate-notes
