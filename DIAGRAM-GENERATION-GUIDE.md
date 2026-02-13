# AI Sakhi - Diagram Generation Guide

## Quick Start: Generate Architecture Diagrams

This guide provides step-by-step instructions for generating AWS architecture diagrams for the AI Sakhi application.

## Prerequisites

### Option 1: Using WSL (Windows Subsystem for Linux) - Recommended

1. **Verify WSL is installed**:
   ```bash
   wsl --list --verbose
   ```

2. **Install required packages in WSL**:
   ```bash
   # Update package list
   sudo apt-get update
   
   # Install Python 3 and pip
   sudo apt-get install -y python3 python3-pip
   
   # Install Graphviz (required for diagram generation)
   sudo apt-get install -y graphviz
   
   # Install Python diagrams library
   pip3 install diagrams
   ```

### Option 2: Using Linux/macOS

1. **Install Graphviz**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install graphviz
   
   # macOS
   brew install graphviz
   ```

2. **Install Python diagrams library**:
   ```bash
   pip3 install diagrams
   ```

### Option 3: Using Docker

No installation required - Docker will handle everything.

## Generate Diagrams

### Method 1: Using the Python Script (WSL/Linux/macOS)

1. **Navigate to project directory**:
   ```bash
   # In WSL, Windows paths are mounted under /mnt/
   cd /mnt/c/path/to/your/project
   
   # Or on Linux/macOS
   cd /path/to/your/project
   ```

2. **Run the diagram generation script**:
   ```bash
   python3 generate_ai_sakhi_diagram.py
   ```

3. **View generated diagrams**:
   ```bash
   ls -lh generated-diagrams/
   ```
   
   Output files:
   - `ai_sakhi_architecture.png` - Full architecture diagram
   - `ai_sakhi_architecture_simplified.png` - Simplified version

### Method 2: Using Docker

1. **Create a Dockerfile** (already provided in project):
   ```dockerfile
   FROM python:3.10-slim
   
   RUN apt-get update && \
       apt-get install -y graphviz && \
       pip install diagrams && \
       rm -rf /var/lib/apt/lists/*
   
   WORKDIR /app
   COPY generate_ai_sakhi_diagram.py .
   
   CMD ["python", "generate_ai_sakhi_diagram.py"]
   ```

2. **Build and run**:
   ```bash
   # Build Docker image
   docker build -t ai-sakhi-diagram .
   
   # Run container and generate diagrams
   docker run -v $(pwd)/generated-diagrams:/app/generated-diagrams ai-sakhi-diagram
   ```

### Method 3: Using MCP Server (When Windows Support is Fixed)

Once the MCP server Windows compatibility issue is resolved:

```python
# This will work in future versions
from kiro import mcp_tools

result = mcp_tools.generate_diagram(
    code=diagram_code,
    filename="ai-sakhi-architecture",
    workspace_dir="."
)
```

## Diagram Types Available

### 1. Full Architecture Diagram
**File**: `ai_sakhi_architecture.png`

Shows complete system architecture including:
- User layer
- Frontend components (Flask, Voice UI, Language Selector)
- API Gateway and Load Balancing
- Core application services
- Health education modules
- AWS AI/ML services (Transcribe, Polly, Translate, Bedrock)
- Data storage (S3, DynamoDB, RDS)
- Monitoring (CloudWatch, CloudTrail)
- External integrations

### 2. Simplified Architecture Diagram
**File**: `ai_sakhi_architecture_simplified.png`

Shows high-level overview:
- User interaction
- Frontend layer
- Backend services
- AWS services
- Storage layer
- Monitoring

### 3. Mermaid Diagrams (Already Available)
**File**: `ai-sakhi-architecture-diagram.md`

Contains multiple Mermaid diagrams that render automatically on GitHub/GitLab:
- Main architecture diagram
- Voice processing flow
- Emergency response flow
- Data model relationships
- AWS services integration map
- Deployment architecture
- Security architecture
- Performance & scalability

## Troubleshooting

### Issue: "Command not found: python3"
**Solution**: Install Python 3
```bash
sudo apt-get install python3 python3-pip
```

### Issue: "ModuleNotFoundError: No module named 'diagrams'"
**Solution**: Install diagrams library
```bash
pip3 install diagrams
```

### Issue: "Graphviz not found"
**Solution**: Install Graphviz
```bash
# Ubuntu/Debian
sudo apt-get install graphviz

# macOS
brew install graphviz
```

### Issue: "Permission denied" when running script
**Solution**: Make script executable
```bash
chmod +x generate_ai_sakhi_diagram.py
```

### Issue: "Cannot write to generated-diagrams directory"
**Solution**: Create directory with proper permissions
```bash
mkdir -p generated-diagrams
chmod 755 generated-diagrams
```

### Issue: MCP Server Windows Error
**Error**: `AttributeError: module 'signal' has no attribute 'SIGALRM'`

**Explanation**: The MCP diagram server uses Unix-specific signals that are not available on Windows.

**Solutions**:
1. Use WSL (recommended)
2. Use Docker
3. Use the standalone Python script
4. Use Mermaid diagrams (already available)

## Viewing Diagrams

### On Windows
1. **File Explorer**: Navigate to `generated-diagrams/` folder and double-click PNG files
2. **VS Code**: Right-click PNG file → "Open Preview"
3. **Browser**: Drag and drop PNG file into browser window

### On Linux/macOS
```bash
# Using default image viewer
xdg-open generated-diagrams/ai_sakhi_architecture.png  # Linux
open generated-diagrams/ai_sakhi_architecture.png      # macOS

# Using specific viewer
eog generated-diagrams/ai_sakhi_architecture.png       # GNOME
feh generated-diagrams/ai_sakhi_architecture.png       # Lightweight
```

### On GitHub/GitLab
Mermaid diagrams in `ai-sakhi-architecture-diagram.md` render automatically when viewing the file.

## Customizing Diagrams

### Modify Diagram Layout

Edit `generate_ai_sakhi_diagram.py` and change the `direction` parameter:

```python
with Diagram(
    "AI Sakhi Architecture",
    show=False,
    direction="TB",  # Options: TB (top-bottom), LR (left-right), BT, RL
    filename=output_path
):
```

### Change Output Format

Modify the `outformat` parameter:

```python
with Diagram(
    "AI Sakhi Architecture",
    show=False,
    outformat="png"  # Options: png, jpg, svg, pdf, dot
):
```

### Add Custom Components

```python
# Import additional AWS services
from diagrams.aws.analytics import Kinesis
from diagrams.aws.security import WAF

# Add to diagram
kinesis = Kinesis("Data Streaming")
waf = WAF("Web Application Firewall")
```

### Customize Colors and Styles

```python
# Use Edge for custom styling
user >> Edge(color="blue", style="bold", label="HTTPS") >> api_gateway
```

## Best Practices

1. **Version Control**: Commit generated diagrams to Git for documentation
2. **Automation**: Add diagram generation to CI/CD pipeline
3. **Documentation**: Keep diagrams in sync with code changes
4. **Multiple Views**: Generate both detailed and simplified versions
5. **Export Formats**: Generate PNG for documentation, SVG for presentations
6. **Regular Updates**: Regenerate diagrams when architecture changes

## Additional Resources

### Official Documentation
- **Python Diagrams**: https://diagrams.mingrammer.com/
- **Graphviz**: https://graphviz.org/
- **Mermaid**: https://mermaid.js.org/

### Example Diagrams
- AWS Architecture: https://diagrams.mingrammer.com/docs/getting-started/examples
- Kubernetes: https://diagrams.mingrammer.com/docs/nodes/k8s
- On-Premises: https://diagrams.mingrammer.com/docs/nodes/onprem

### AI Sakhi Documentation
- Architecture Overview: `AI-SAKHI-ARCHITECTURE-SUMMARY.md`
- Mermaid Diagrams: `ai-sakhi-architecture-diagram.md`
- MCP Setup Report: `aws-diagram-mcp-setup-report.md`
- Design Document: `.kiro/specs/sakhi-saathi-ai/design.md`

## Quick Reference Commands

```bash
# Install dependencies (WSL/Linux)
sudo apt-get update && sudo apt-get install -y python3 python3-pip graphviz
pip3 install diagrams

# Generate diagrams
python3 generate_ai_sakhi_diagram.py

# View diagrams
ls -lh generated-diagrams/

# Open diagram (Linux)
xdg-open generated-diagrams/ai_sakhi_architecture.png

# Open diagram (macOS)
open generated-diagrams/ai_sakhi_architecture.png

# Docker method
docker build -t ai-sakhi-diagram .
docker run -v $(pwd)/generated-diagrams:/app/generated-diagrams ai-sakhi-diagram
```

## Summary

You now have multiple options for generating AWS architecture diagrams:

1. ✅ **WSL/Linux/macOS**: Use `generate_ai_sakhi_diagram.py` script
2. ✅ **Docker**: Containerized diagram generation
3. ✅ **Mermaid**: Already available in `ai-sakhi-architecture-diagram.md`
4. ⏳ **MCP Server**: Will work once Windows compatibility is fixed

Choose the method that works best for your environment and workflow!
