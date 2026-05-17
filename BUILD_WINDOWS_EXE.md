# How to Build a Windows Executable for SwimScore

This guide shows you how to convert your Flask application into a Windows `.exe` file.

## Prerequisites

You need to be on a **Windows machine** (or use a Windows VM/cloud instance) since you're building a Windows-only executable.

## Step-by-Step Instructions

### 1. Install PyInstaller

Open Command Prompt or PowerShell and install PyInstaller:

```bash
pip install pyinstaller
```

### 2. Ensure All Dependencies Are Installed

Make sure all your project dependencies are installed:

```bash
pip install -r requirements.txt
```

### 3. Build the Executable

From the project root directory (`/workspace`), run one of these commands:

**Option A - Simple one-liner:**
```bash
pyinstaller --onefile --windowed --name SwimScore --add-data "swimapp/templates;swimapp\templates" --add-data "swimapp/static;swimapp\static" --add-data "instance;instance" --hidden-import flask --hidden-import flask_sqlalchemy --hidden-import flask_login --hidden-import werkzeug.security --hidden-import jinja2 run.py
```

**Option B - Using the spec file (recommended):**
```bash
pyinstaller swimscore.spec
```

### 4. Find Your Executable

After the build completes, you'll find your executable at:
- `dist/SwimScore.exe` (single file version)
- `dist/SwimScore/` (folder with all files if using spec file)

### 5. Test the Executable

Run `SwimScore.exe` on a Windows machine. It will:
- Start the Flask server automatically
- Open your default web browser to `http://127.0.0.1:5000`
- The app will run locally without needing Python installed

## Important Notes

### Database Location
The SQLite database (`swim.db`) will be created in the same directory as the executable when first run. User data will persist between runs.

### Console Output
- If you want to see debug logs, change `console=False` to `console=True` in the spec file
- For a production release, keep it as `console=False` for a cleaner experience

### Firewall
When users first run the executable, Windows Firewall may prompt them to allow network access. This is normal since the Flask server needs to listen on port 5000.

### Building on Non-Windows Systems
If you're currently on Linux/Mac but need a Windows executable, you have these options:
1. Use a Windows VM (VirtualBox, VMware)
2. Use Wine (may have limitations)
3. Use a CI/CD service like GitHub Actions with Windows runners
4. Use a cloud Windows instance

## Troubleshooting

### Missing Modules Error
If you get "ModuleNotFoundError" when running the exe, add the missing module to the `hiddenimports` list in the spec file.

### Static Files Not Loading
Ensure the `--add-data` paths are correct. On Windows, use semicolon (`;`) as the separator in the command line.

### App Crashes on Startup
Try running with `console=True` to see error messages in the console window.

## Distribution

To distribute your app:
1. Zip the entire `dist/SwimScore/` folder (if using spec file)
2. Or just share the single `dist/SwimScore.exe` file (if using --onefile)
3. Users don't need Python installed - just run the .exe!

## Rebuilding After Code Changes

Any time you modify your Python code, templates, or static files:
1. Delete the `build` and `dist` folders
2. Run the pyinstaller command again
