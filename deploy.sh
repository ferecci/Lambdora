#!/bin/bash

set -e

echo "Deploying Lambdora Web REPL..."

if [ ! -f "index.html" ]; then
    echo "Error: Please run this script from the web/ directory"
    exit 1
fi

echo "Building Lambdora bundle..."
python3 build_lambdora.py

if [ ! -f "lambdora_bundle.py" ]; then
    echo "Error: Failed to create lambdora_bundle.py"
    exit 1
fi

echo "Bundle created successfully"

if [ -d ".git" ]; then
    echo "Git repository detected"
    
    if [ -n "$(git status --porcelain)" ]; then
        echo "Committing changes..."
        git add .
        git commit -m "Update web REPL bundle"
        
        echo "Pushing to remote..."
        git push
        
        echo "Deployment complete!"
        echo ""
        echo "If you have GitHub Pages enabled, your REPL should be available at:"
        echo "https://yourusername.github.io/lambdora/"
    else
        echo "No changes to commit"
    fi
else
    echo "Not a git repository - bundle ready for manual deployment"
    echo ""
    echo "To deploy:"
    echo "1. Upload the contents of this directory to your web server"
    echo "2. Or enable GitHub Pages in your repository settings"
fi

echo ""
echo "Lambdora Web REPL is ready!"
echo "Files to deploy:"
ls -la *.html *.css *.js *.py *.json 2>/dev/null || true 