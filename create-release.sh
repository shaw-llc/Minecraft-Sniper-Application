#!/bin/bash

# OpenMC Username Sniper Release Script
# This script creates a new release tag and pushes it to GitHub,
# which triggers the GitHub Actions workflow to build and publish the release.

# Ensure script exits on error
set -e

# Configuration
VERSION="1.0.0"
RELEASE_BRANCH="main"
REPO_URL="https://github.com/yourusername/OpenMC-Username-Sniper.git"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}OpenMC Username Sniper Release Script${NC}"
echo -e "Creating release version ${GREEN}v$VERSION${NC}"

# Check if we're on the correct branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "$RELEASE_BRANCH" ]; then
    echo -e "${RED}Error: You must be on the $RELEASE_BRANCH branch to create a release.${NC}"
    echo -e "Current branch: $CURRENT_BRANCH"
    echo -e "Please switch to the $RELEASE_BRANCH branch and try again."
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}Error: You have uncommitted changes.${NC}"
    echo -e "Please commit or stash your changes before creating a release."
    exit 1
fi

# Pull latest changes
echo -e "Pulling latest changes from $RELEASE_BRANCH..."
git pull origin $RELEASE_BRANCH

# Update version in package.json
echo -e "Updating version in package.json to $VERSION..."
# This uses sed to replace the version field in package.json
sed -i '' 's/"version": ".*"/"version": "'$VERSION'"/' package.json

# Commit version change
echo -e "Committing version change..."
git add package.json
git commit -m "chore: bump version to $VERSION for release"

# Create release tag
echo -e "Creating release tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION"

# Push changes and tag
echo -e "Pushing changes and tag to remote repository..."
git push origin $RELEASE_BRANCH
git push origin "v$VERSION"

echo -e "${GREEN}Release v$VERSION has been created and pushed to GitHub.${NC}"
echo -e "GitHub Actions will now build and publish the release packages."
echo -e "You can monitor the build progress at:"
echo -e "${YELLOW}https://github.com/yourusername/OpenMC-Username-Sniper/actions${NC}"
echo -e ""
echo -e "Once the build is complete, you can find the release at:"
echo -e "${YELLOW}https://github.com/yourusername/OpenMC-Username-Sniper/releases/tag/v$VERSION${NC}"
echo -e ""
echo -e "Don't forget to update the release notes on GitHub with the contents of RELEASE_NOTES.md" 