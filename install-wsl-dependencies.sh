#!/bin/bash
# AI Sakhi - Install WSL Dependencies for Diagram Generation

echo "======================================================================"
echo "AI Sakhi - Installing WSL Dependencies"
echo "======================================================================"
echo ""
echo "This script will install:"
echo "  - python3-pip"
echo "  - graphviz"
echo "  - diagrams Python library"
echo ""
echo "You will be prompted for your sudo password."
echo ""

# Update package list
echo "Updating package list..."
sudo apt-get update

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to update package list"
    exit 1
fi

# Install pip3 and graphviz
echo ""
echo "Installing python3-pip and graphviz..."
sudo apt-get install -y python3-pip graphviz

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install packages"
    exit 1
fi

# Install diagrams library
echo ""
echo "Installing diagrams Python library..."
pip3 install diagrams

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install diagrams library"
    exit 1
fi

# Verify installation
echo ""
echo "======================================================================"
echo "Verifying installation..."
echo "======================================================================"
echo ""

echo -n "Python version: "
python3 --version

echo -n "pip3 version: "
pip3 --version

echo -n "Graphviz (dot): "
which dot

echo -n "Diagrams library: "
python3 -c "import diagrams; print('Installed successfully')" 2>&1

echo ""
echo "======================================================================"
echo "✅ Installation complete!"
echo "======================================================================"
echo ""
echo "You can now generate diagrams by running:"
echo "  python3 generate_ai_sakhi_diagram.py"
echo ""
