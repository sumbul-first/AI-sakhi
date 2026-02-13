# Generate AI Sakhi Architecture Diagrams

## Quick Start

Choose one of the following methods to generate PNG architecture diagrams:

### Method 1: Using WSL (Recommended for Windows)

**Double-click**: `generate-diagrams-wsl.bat`

This will:
1. Install dependencies in WSL Ubuntu-22.04 (requires sudo password)
2. Generate architecture diagrams
3. Save PNG files to `generated-diagrams/` folder

**First-time setup**: You'll be prompted for your sudo password to install packages.

---

### Method 2: Using Docker (No WSL Setup Required)

**Double-click**: `generate-diagrams-docker.bat`

This will:
1. Use Docker to create a temporary container
2. Install dependencies inside the container
3. Generate architecture diagrams
4. Save PNG files to `generated-diagrams/` folder

**Requirements**: Docker Desktop must be running.

---

### Method 3: Manual WSL Commands

Open WSL terminal and run:

```bash
# One-time setup (install dependencies)
sudo apt-get update
sudo apt-get install -y python3-pip graphviz
pip3 install diagrams

# Generate diagrams (run anytime)
python3 generate_ai_sakhi_diagram.py
```

---

### Method 4: Manual Docker Command

Open PowerShell and run:

```powershell
docker run --rm -v ${PWD}:/app -w /app python:3.10-slim bash -c "apt-get update && apt-get install -y graphviz && pip install diagrams && python generate_ai_sakhi_diagram.py"
```

---

## What Gets Generated

After running any of the above methods, you'll have:

1. **Full Architecture Diagram**
   - File: `generated-diagrams/ai_sakhi_architecture.png`
   - Shows complete system with all components
   - Includes: Frontend, Backend, AWS Services, Storage, Monitoring

2. **Simplified Architecture Diagram**
   - File: `generated-diagrams/ai_sakhi_architecture_simplified.png`
   - High-level overview
   - Easier to understand for presentations

## Viewing Diagrams

### On Windows
- **File Explorer**: Navigate to `generated-diagrams\` and double-click PNG files
- **VS Code**: Right-click PNG → "Open Preview"
- **Browser**: Drag and drop PNG into browser window

### In Git
After generation, commit the diagrams:

```bash
git add generated-diagrams/
git commit -m "Add architecture diagrams"
```

## Troubleshooting

### WSL Method Issues

**Problem**: "sudo: command not found"
- **Solution**: Your WSL installation may be corrupted. Reinstall:
  ```powershell
  wsl --unregister Ubuntu-22.04
  wsl --install -d Ubuntu-22.04
  ```

**Problem**: "Permission denied"
- **Solution**: Make sure you enter your sudo password when prompted

**Problem**: "pip3: command not found" after installation
- **Solution**: Use `python3 -m pip install diagrams` instead

### Docker Method Issues

**Problem**: "Docker is not running"
- **Solution**: Start Docker Desktop and wait for it to fully start

**Problem**: "Cannot connect to Docker daemon"
- **Solution**: Restart Docker Desktop

**Problem**: Takes too long on first run
- **Explanation**: Docker needs to download the Python image (~100MB) on first run
- **Solution**: Be patient, subsequent runs will be much faster

### General Issues

**Problem**: "generate_ai_sakhi_diagram.py not found"
- **Solution**: Make sure you're running the command from the project root directory

**Problem**: "No module named 'diagrams'"
- **Solution**: Dependencies not installed. Run the installation steps again

**Problem**: Generated diagrams are empty or corrupted
- **Solution**: Delete `generated-diagrams/` folder and regenerate

## Alternative: Use Existing Mermaid Diagrams

If you don't want to generate PNG diagrams, comprehensive Mermaid diagrams are already available in:

- **File**: `ai-sakhi-architecture-diagram.md`
- **Renders automatically** on GitHub/GitLab
- **Includes**: Multiple diagram types (architecture, flows, data models, etc.)

## System Requirements

### WSL Method
- Windows 10/11 with WSL 2
- Ubuntu-22.04 distribution installed
- ~100MB disk space for dependencies

### Docker Method
- Docker Desktop installed and running
- ~200MB disk space for Docker image (one-time download)

## Estimated Time

- **First-time setup**: 2-3 minutes (installing dependencies)
- **Diagram generation**: 10-15 seconds
- **Subsequent runs**: 10-15 seconds (dependencies already installed)

## Files Created

```
generated-diagrams/
├── ai_sakhi_architecture.png              (~500KB)
└── ai_sakhi_architecture_simplified.png   (~200KB)
```

## Need Help?

See detailed documentation:
- **WSL Setup**: `WSL-DIAGRAM-SETUP.md`
- **Diagram Guide**: `DIAGRAM-GENERATION-GUIDE.md`
- **MCP Report**: `aws-diagram-mcp-setup-report.md`
- **Architecture Summary**: `AI-SAKHI-ARCHITECTURE-SUMMARY.md`

## Summary

**Easiest Method**: Double-click `generate-diagrams-docker.bat` (if Docker is running)

**Best for Development**: Use WSL method (one-time setup, then fast)

**No Installation**: Use existing Mermaid diagrams in `ai-sakhi-architecture-diagram.md`
