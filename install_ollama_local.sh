#!/bin/bash
set -e

echo "Installing Ollama locally..."

# Create bin directory if it doesn't exist
mkdir -p ~/bin

# Download and extract Ollama
echo "Downloading Ollama..."
curl -L https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz

echo "Extracting Ollama..."
tar -xzf ollama-linux-amd64.tgz

# Move to bin directory
echo "Installing Ollama to ~/bin..."
mv ollama ~/bin/

# Add to PATH
echo "Adding Ollama to PATH..."
echo 'export PATH="$PATH:~/bin"' >> ~/.bashrc

# Clean up
rm ollama-linux-amd64.tgz

echo "Ollama installed successfully!"
echo "Please run: source ~/.bashrc"
echo "Then test with: ollama --version"
