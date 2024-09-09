#!/bin/bash

# Variables (customize as needed)
GITHUB_USERNAME="mexmarv"
REPO_NAME="honeypot"
REPO_DESC="Leran Servers on subnet, and then simulate them."
BRANCH="main"

# Check if Git is initialized, otherwise initialize it
if [ ! -d ".git" ]; then
    echo "Initializing Git repository..."
    git init
fi

# Add all files to the repository
echo "Adding files to the repository..."
git add .

# Commit the files
echo "Committing files..."
git commit -m "Initial commit for honeypot project"

# Create a new repository on GitHub using GitHub CLI (gh)
echo "Creating repository on GitHub..."
gh repo create "$REPO_NAME" --public --description "$REPO_DESC" --source=. --remote=origin --push

# Set branch name and push to GitHub
echo "Pushing to GitHub..."
git branch -M "$BRANCH"
git push -u origin "$BRANCH"

echo "Successfully pushed the repository to GitHub!"
