#!/bin/bash

# Package Railway worker deployment

echo "📦 Packaging Railway worker deployment..."

# Create deployment directory
mkdir -p railway_deployment
cd railway_deployment

# Copy essential files
echo "Copying worker files..."
cp ../railway_worker.py .
cp ../railway.json .
cp ../Procfile .
cp ../requirements.txt .

# Copy curriculum directory
echo "Copying curriculum files..."
cp -r ../curriculum .

# Create archive
echo "Creating archive..."
cd ..
tar -czf railway_worker_deployment.tar.gz railway_deployment/

# Cleanup
rm -rf railway_deployment

echo "✅ Package created: railway_worker_deployment.tar.gz"
echo ""
echo "📋 Next steps:"
echo "1. Download railway_worker_deployment.tar.gz"
echo "2. Extract on your local machine"
echo "3. Push to GitHub repository"
echo "4. Deploy to Railway from GitHub"
echo ""
echo "Or use Railway CLI:"
echo "  railway up"
