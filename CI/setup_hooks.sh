#!/bin/bash

# Define the top-level directory of the repository and the Git directory
REPO_TOPLEVEL=$(git rev-parse --show-toplevel)
GIT_DIR=$(git rev-parse --git-dir)

# Define the source and target directories for the hooks
REPO_HOOKS_DIR="$REPO_TOPLEVEL/git_hooks"
GIT_HOOKS_DIR="$GIT_DIR/hooks"

# Ensure the commands run successfully before proceeding
if [ -z "$REPO_HOOKS_DIR" ] || [ -z "$GIT_HOOKS_DIR" ]; then
    echo "Error: Could not determine repository or hooks directory."
    exit 1
fi

# Link each script from the git_hooks directory to the .git/hooks directory and make them executable
for hook in "$REPO_HOOKS_DIR"/*; do
    if [ -f "$hook" ]; then
        hook_name=$(basename "$hook")
        ln -sf "$hook" "$GIT_HOOKS_DIR/$hook_name"  # Force symlink creation
        chmod +x "$GIT_HOOKS_DIR/$hook_name"  # Make the script executable
        echo "Linked and set executable: $hook_name"
    else
        echo "Skipping non-file item: $hook"
    fi
done

echo "Git hooks set up successfully."