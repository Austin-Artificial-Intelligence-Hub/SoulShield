#!/bin/bash

# Build Lambda layer with dependencies
echo "Building Lambda layer..."

cd lambda/layer

# Create python directory for Lambda layer
mkdir -p python

# Install dependencies
pip install -r requirements.txt -t python/

echo "Layer built successfully!"
