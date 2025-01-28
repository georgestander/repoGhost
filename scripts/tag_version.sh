#!/bin/bash

# Get the version from pyproject.toml
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

# Commit version change
git add pyproject.toml
git commit -m "Bump version to $VERSION"
git push origin main

# Delete existing tag locally and remotely
git tag -d "v$VERSION" 2>/dev/null || true
git push origin ":refs/tags/v$VERSION" 2>/dev/null || true

# Create and push git tag
git tag -a "v$VERSION" -m "Release version $VERSION"
git push origin "v$VERSION"

echo "Created and pushed tag v$VERSION"
echo "GitHub Actions will handle the release and PyPI upload"
