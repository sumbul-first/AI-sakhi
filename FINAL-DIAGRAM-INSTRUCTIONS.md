# Final Step: Generate AI Sakhi Architecture Diagram

## Current Status ✅

I've successfully installed most dependencies in your WSL environment:
- ✅ Python 3.10.6 (already installed)
- ✅ pip3 (just installed)
- ✅ diagrams Python library (just installed)
- ❌ Graphviz system package (requires sudo - needs your password)

## One Command to Complete Setup

Open PowerShell or Command Prompt and run:

```powershell
wsl -d Ubuntu-22.04 bash -c "sudo apt-get update && sudo apt-get install -y graphviz"
```

**You will be prompted for your sudo password** - this is normal and required.

## Then Generate Diagrams

After installing graphviz, run:

```powershell
wsl -d Ubuntu-22.04 bash -c "cd /mnt/c/Users/sumbul/kiro-hackathon/SakhiSathi && /usr/bin/python3 generate_ai_sakhi_diagram.py"
```

## Or Use the Batch File

I've created `install-and-generate.bat` that does both steps. Just double-click it and enter your sudo password when prompted.

## What You'll Get

After running the commands above, you'll have:

```
generated-diagrams/
├── ai_sakhi_architecture.png              (Full architecture diagram)
└── ai_sakhi_architecture_simplified.png   (Simplified diagram)
```

## Why Sudo is Required

The `graphviz` package contains system-level executables (`dot`, `neato`, etc.) that need to be installed in system directories. This is a one-time setup - once installed, future diagram generations won't need sudo.

## Alternative: Use Docker (No Sudo Required)

If you prefer not to use sudo, you can use Docker instead:

```powershell
docker run --rm -v ${PWD}:/app -w /app python:3.10-slim bash -c "apt-get update && apt-get install -y graphviz && pip install diagrams && python generate_ai_sakhi_diagram.py"
```

This requires Docker Desktop to be running but doesn't need sudo.

## Summary

**What's Done:**
- ✅ pip3 installed in WSL
- ✅ diagrams library installed in WSL
- ✅ All Python dependencies ready

**What's Needed:**
- ⏳ Install graphviz (one command with sudo)
- ⏳ Run diagram generation script

**Estimated Time:**
- Graphviz installation: 30 seconds
- Diagram generation: 10 seconds
- **Total: Less than 1 minute**

## Quick Commands Reference

```powershell
# Install graphviz (one-time, requires sudo password)
wsl -d Ubuntu-22.04 bash -c "sudo apt-get install -y graphviz"

# Generate diagrams (run anytime after graphviz is installed)
wsl -d Ubuntu-22.04 bash -c "cd /mnt/c/Users/sumbul/kiro-hackathon/SakhiSathi && /usr/bin/python3 generate_ai_sakhi_diagram.py"

# Or use the all-in-one batch file
# Double-click: install-and-generate.bat
```

## Verification

After installation, verify everything works:

```powershell
wsl -d Ubuntu-22.04 bash -c "which dot && /usr/bin/python3 -c 'import diagrams; print(\"Ready to generate diagrams!\")'"
```

Expected output:
```
/usr/bin/dot
Ready to generate diagrams!
```

## Next Steps

1. Run the graphviz installation command (requires sudo password)
2. Run the diagram generation command
3. View the generated PNG files in `generated-diagrams/` folder
4. Commit to Git: `git add generated-diagrams/`

You're almost there - just one sudo command away from having beautiful architecture diagrams!
