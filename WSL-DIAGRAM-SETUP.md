# WSL Diagram Generation Setup - Manual Steps Required

## Current Status

Your WSL Ubuntu-22.04 environment has:
- ✅ Python 3.10.6 installed
- ❌ Graphviz not installed (requires sudo)
- ❌ pip3 not installed (requires sudo)
- ❌ diagrams library not installed

## Manual Installation Steps

Since the installation requires sudo password, please run these commands manually in your WSL terminal:

### Step 1: Open WSL Terminal

```powershell
# In PowerShell or Command Prompt
wsl -d Ubuntu-22.04
```

### Step 2: Install Required Packages

```bash
# Update package list
sudo apt-get update

# Install pip3 and graphviz
sudo apt-get install -y python3-pip graphviz

# Install diagrams library
pip3 install diagrams
```

### Step 3: Navigate to Project Directory

```bash
# Windows paths are mounted under /mnt/
cd /mnt/c/Users/YourUsername/path/to/ai-sakhi-project
```

### Step 4: Generate Diagrams

```bash
# Run the diagram generation script
python3 generate_ai_sakhi_diagram.py
```

### Step 5: View Generated Diagrams

```bash
# List generated files
ls -lh generated-diagrams/

# The diagrams will be available at:
# - generated-diagrams/ai_sakhi_architecture.png
# - generated-diagrams/ai_sakhi_architecture_simplified.png
```

## Alternative: One-Line Installation

If you prefer, you can run all installation commands at once:

```bash
sudo apt-get update && \
sudo apt-get install -y python3-pip graphviz && \
pip3 install diagrams && \
echo "Installation complete! Now run: python3 generate_ai_sakhi_diagram.py"
```

## Verification

After installation, verify everything is working:

```bash
# Check Python version
python3 --version
# Expected: Python 3.10.6

# Check graphviz
which dot
# Expected: /usr/bin/dot

# Check diagrams library
python3 -c "import diagrams; print('diagrams library installed successfully')"
# Expected: diagrams library installed successfully
```

## Troubleshooting

### Issue: "sudo: command not found"
This shouldn't happen on Ubuntu-22.04. If it does, your WSL installation may be corrupted.

**Solution**: Reinstall WSL Ubuntu:
```powershell
wsl --unregister Ubuntu-22.04
wsl --install -d Ubuntu-22.04
```

### Issue: "Permission denied"
**Solution**: Ensure you're running commands with sudo for system packages.

### Issue: "pip3: command not found" after installation
**Solution**: Use python3 -m pip instead:
```bash
python3 -m pip install diagrams
```

### Issue: Diagram generation fails with "Graphviz not found"
**Solution**: Verify graphviz installation:
```bash
sudo apt-get install --reinstall graphviz
```

## Expected Output

When you run `python3 generate_ai_sakhi_diagram.py`, you should see:

```
======================================================================
AI Sakhi Architecture Diagram Generator
======================================================================

Generating AI Sakhi Architecture Diagram...
Created output directory: generated-diagrams
✅ Diagram generated successfully: generated-diagrams/ai_sakhi_architecture.png

Generating Simplified Architecture Diagram...
✅ Simplified diagram generated: generated-diagrams/ai_sakhi_architecture_simplified.png

======================================================================
✅ All diagrams generated successfully!
======================================================================

Generated files:
  1. generated-diagrams/ai_sakhi_architecture.png
  2. generated-diagrams/ai_sakhi_architecture_simplified.png

You can now view these PNG files in your file explorer or image viewer.
```

## Viewing Diagrams on Windows

After generation, you can view the diagrams:

1. **File Explorer**: Navigate to `generated-diagrams\` folder and double-click PNG files
2. **VS Code**: Right-click PNG file → "Open Preview"
3. **Browser**: Drag and drop PNG file into browser window

## Next Steps

Once you've completed the manual installation:

1. ✅ Install dependencies (sudo apt-get install python3-pip graphviz)
2. ✅ Install diagrams library (pip3 install diagrams)
3. ✅ Run diagram generation script (python3 generate_ai_sakhi_diagram.py)
4. ✅ View generated PNG diagrams
5. ✅ Commit diagrams to Git repository

## Why Manual Installation is Required

The automated installation requires sudo password input, which cannot be provided programmatically for security reasons. This is a one-time setup - once installed, future diagram generations will work automatically.

## Alternative Solutions

If you prefer not to use WSL, you have these options:

1. **Use Mermaid Diagrams**: Already available in `ai-sakhi-architecture-diagram.md` - renders automatically on GitHub/GitLab
2. **Use Docker**: Run diagram generation in a container (no sudo required)
3. **Use Online Tools**: Copy diagram code to online Mermaid or Graphviz editors
4. **Use Linux VM**: If you have a Linux virtual machine

## Docker Alternative (No Sudo Required)

If you have Docker Desktop running, you can generate diagrams without WSL setup:

```powershell
# In PowerShell
docker run --rm -v ${PWD}:/app -w /app python:3.10-slim bash -c "apt-get update && apt-get install -y graphviz && pip install diagrams && python generate_ai_sakhi_diagram.py"
```

This will:
1. Pull Python 3.10 image
2. Install graphviz and diagrams
3. Generate diagrams
4. Save them to your current directory

## Summary

**Current Blocker**: WSL requires sudo password for package installation

**Solution**: Run the installation commands manually in WSL terminal (see Step 2 above)

**Time Required**: ~2-3 minutes for installation, ~10 seconds for diagram generation

**One-Time Setup**: Yes - once installed, future generations are automatic
