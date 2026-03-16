# How to Run AI Sakhi Application Locally

This guide provides step-by-step instructions to run the AI Sakhi application on your local machine and view it in your browser.

## Prerequisites Check

Before starting, verify you have:
- ✅ Python 3.8 or higher installed
- ✅ Git repository cloned
- ✅ Terminal/PowerShell access

## Step-by-Step Instructions

### Step 1: Open Terminal in Project Directory

1. Open PowerShell or Command Prompt
2. Navigate to the project directory:
   ```powershell
   cd C:\Users\sumbul\kiro-hackathon\SakhiSathi
   ```

3. Verify you're in the correct directory:
   ```powershell
   Get-Location
   ```
   
   You should see: `C:\Users\sumbul\kiro-hackathon\SakhiSathi`

### Step 2: Activate Python Virtual Environment

The project uses a virtual environment to manage dependencies.

**Option A: If virtual environment exists (ai-sakhi-env)**
```powershell
.\ai-sakhi-env\Scripts\Activate.ps1
```

**Option B: If you see an error, create a new virtual environment**
```powershell
# Create virtual environment
python -m venv ai-sakhi-env

# Activate it
.\ai-sakhi-env\Scripts\Activate.ps1

ai-sakhi-env\Scripts\activate
```

**Verify activation:**
You should see `(ai-sakhi-env)` at the beginning of your command prompt.

### Step 3: Install Required Dependencies

Install all Python packages needed by the application:

```powershell
pip install -r requirements.txt
```

**If requirements.txt doesn't exist, install manually:**
```powershell
pip install flask flask-babel boto3 python-dotenv
```

This will install:
- Flask (web framework)
- Flask-Babel (multi-language support)
- boto3 (AWS SDK - for mock mode)
- python-dotenv (environment variables)

### Step 4: Verify Application File

Check that the main application file exists:

```powershell
Test-Path app_integrated.py
```

Should return: `True`

### Step 5: Start the Application

Run the Flask application:

```powershell
python app_integrated.py
```

**What you should see:**
```
 * Serving Flask app 'app_integrated'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:8080
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
```

**Important:** Leave this terminal window open. The application is now running!

### Step 6: Open Application in Browser

1. Open your web browser (Chrome, Firefox, Edge, etc.)
2. Go to one of these URLs:
   - `http://localhost:8080`
   - `http://127.0.0.1:8080`

3. You should see the AI Sakhi home page with:
   - AI Sakhi logo (mother-daughter design)
   - Welcome message
   - Language selector
   - Five health module buttons:
     - 🌸 Puberty Education
     - 🛡️ Safety & Mental Support
     - 🩸 Menstrual Shopping Guide
     - 🤰 Pregnancy Guidance
     - 🏛️ Government Resources

### Step 7: Test the Application

Try these features:

#### Test 1: Home Page
- ✅ Logo displays correctly
- ✅ Navigation menu works
- ✅ Language selector is visible

#### Test 2: Health Modules
Click each module button to verify:
- ✅ Puberty Education module loads
- ✅ Safety & Mental Support module loads
- ✅ Menstrual Shopping Guide module loads
- ✅ Pregnancy Guidance module loads
- ✅ Government Resources module loads

#### Test 3: Language Switching
- Click the language selector
- Try switching between languages
- Verify content updates

#### Test 4: Emergency Contacts
- Navigate to Safety & Mental Support
- Check that emergency helpline numbers display

### Step 8: View Application Logs

In the terminal where the app is running, you'll see:
- HTTP requests (GET, POST)
- Status codes (200, 404, etc.)
- Any errors or warnings

Example output:
```
127.0.0.1 - - [08/Mar/2026 10:30:15] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [08/Mar/2026 10:30:16] "GET /static/css/style.css HTTP/1.1" 200 -
127.0.0.1 - - [08/Mar/2026 10:30:20] "GET /modules/puberty HTTP/1.1" 200 -
```

### Step 9: Stop the Application

When you're done testing:

1. Go to the terminal where the app is running
2. Press `Ctrl + C`
3. The application will stop

You should see:
```
^C
Keyboard interrupt received, exiting.
```

## Troubleshooting

### Issue 1: "python: command not found"

**Solution:**
```powershell
# Check if Python is installed
python --version

# If not found, try:
py --version

# Or install Python from: https://www.python.org/downloads/
```

### Issue 2: "Cannot activate virtual environment"

**Error:** `Activate.ps1 cannot be loaded because running scripts is disabled`

**Solution:**
```powershell
# Run PowerShell as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try activating again
.\ai-sakhi-env\Scripts\Activate.ps1
```

### Issue 3: "Port 8080 is already in use"

**Error:** `OSError: [Errno 98] Address already in use`

**Solution A: Stop the existing process**
```powershell
# Find process using port 8080
netstat -ano | findstr :8080

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

**Solution B: Use a different port**
Edit `app_integrated.py` and change:
```python
app.run(host='0.0.0.0', port=8080, debug=True)
```
to:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

Then access at: `http://localhost:5000`

### Issue 4: "Module not found" errors

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```powershell
# Make sure virtual environment is activated
.\ai-sakhi-env\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 5: "Template not found" errors

**Error:** `jinja2.exceptions.TemplateNotFound: index.html`

**Solution:**
```powershell
# Verify templates directory exists
Test-Path templates

# If missing, check project structure
Get-ChildItem -Directory
```

### Issue 6: Browser shows "This site can't be reached"

**Possible causes:**
1. Application not running (check terminal)
2. Wrong URL (use http://localhost:8080)
3. Firewall blocking (temporarily disable)

**Solution:**
```powershell
# Verify app is running
# You should see "Running on http://127.0.0.1:8080" in terminal

# Try alternative URL
http://127.0.0.1:8080
```

### Issue 7: Page loads but looks broken (no styling)

**Cause:** Static files not loading

**Solution:**
```powershell
# Verify static directory exists
Test-Path static

# Check browser console (F12) for errors
# Look for 404 errors on CSS/JS files
```

## Quick Reference Commands

### Start Application (Quick)
```powershell
cd C:\Users\sumbul\kiro-hackathon\SakhiSathi
.\ai-sakhi-env\Scripts\Activate.ps1
python app_integrated.py
```

### Stop Application
```
Ctrl + C
```

### Restart Application
```powershell
# Stop with Ctrl + C, then:
python app_integrated.py
```

### Check if Running
```powershell
netstat -ano | findstr :8080
```

### View Logs in Real-Time
The logs appear automatically in the terminal where you ran `python app_integrated.py`

## Application URLs

Once running, access these pages:

| Page | URL |
|------|-----|
| Home | http://localhost:8080/ |
| Puberty Education | http://localhost:8080/modules/puberty |
| Safety & Mental Support | http://localhost:8080/modules/safety |
| Menstrual Guide | http://localhost:8080/modules/menstrual |
| Pregnancy Guidance | http://localhost:8080/modules/pregnancy |
| Government Resources | http://localhost:8080/modules/government |
| Emergency Contacts | http://localhost:8080/api/emergency-contacts |
| Health Check | http://localhost:8080/health |
| Statistics | http://localhost:8080/api/stats |

## Development Tips

### Auto-Reload on Code Changes

The application runs in debug mode, which means:
- ✅ Automatic reload when you save code changes
- ✅ Detailed error messages in browser
- ✅ Interactive debugger

### View Application Structure

```powershell
# See all files
Get-ChildItem -Recurse -File | Select-Object FullName

# See just Python files
Get-ChildItem -Recurse -Filter "*.py" | Select-Object Name
```

### Check Application Health

```powershell
# Using PowerShell
Invoke-WebRequest -Uri http://localhost:8080/health

# Or open in browser
http://localhost:8080/health
```

Should return:
```json
{
  "status": "healthy",
  "components": {
    "content_manager": "operational",
    "session_manager": "operational",
    ...
  }
}
```

## Running in Background (Optional)

If you want to run the app in background:

### Option 1: Using PowerShell Job
```powershell
Start-Job -ScriptBlock { 
    cd C:\Users\sumbul\kiro-hackathon\SakhiSathi
    .\ai-sakhi-env\Scripts\Activate.ps1
    python app_integrated.py
}

# Check job status
Get-Job

# Stop job
Stop-Job -Id 1
```

### Option 2: Using Start-Process
```powershell
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd C:\Users\sumbul\kiro-hackathon\SakhiSathi; .\ai-sakhi-env\Scripts\Activate.ps1; python app_integrated.py"
```

## Next Steps

After successfully running the application:

1. **Test all features** - Go through each module
2. **Check logs** - Monitor terminal for any errors
3. **Test on mobile** - Access from phone using your computer's IP
4. **Review documentation** - Read module-specific docs
5. **Deploy to AWS** - Follow CloudFormation deployment guide

## Support

If you encounter issues not covered here:

1. Check `APPLICATION_TEST_REPORT.md` for known issues
2. Review error messages in terminal
3. Check browser console (F12 → Console tab)
4. Verify all dependencies are installed
5. Ensure virtual environment is activated

---

**Quick Start Summary:**
```powershell
cd C:\Users\sumbul\kiro-hackathon\SakhiSathi
.\ai-sakhi-env\Scripts\Activate.ps1
python app_integrated.py
# Open browser to http://localhost:8080
```

**That's it! Your AI Sakhi application should now be running locally.** 🎉
