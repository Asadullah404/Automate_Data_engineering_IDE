import PyInstaller.__main__
import os
import shutil
import sys

def aggressive_build():
    # 1. CLEANING PHASE: Wipe old build files to prevent cache corruption
    print("Step 1: Cleaning workspace...")
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f" -> Removing {folder}...")
            shutil.rmtree(folder, ignore_errors=True)
    
    # 2. DEFINITIONS
    entry_point = 'workflow_ide.py'
    name = 'AutomateFlow_PRO'
    
    # 3. BUILD PARAMETERS
    params = [
        entry_point,
        f'--name={name}',
        '--onefile',        # Single EXE
        '--windowed',       # No console
        '--noconfirm',      # Overwrite
        '--clean',          # Clean cache
        '--noupx',          # CRITICAL: Fixes sqlite3.dll decompression error
        
        # Explicitly include data folders
        '--add-data', f'Config{os.pathsep}Config',
        '--add-data', f'Custom_Scripts{os.pathsep}Custom_Scripts',
        
        # Ensure standard libraries are bundled correctly
        '--collect-all', 'pandas',
        '--collect-all', 'sqlite3',
    ]
    
    print(f"\nStep 2: Starting Aggressive Build for '{name}'...")
    print(" -> UPX: Disabled (Stability over compression)")
    print(" -> Mode: Single Executable\n")
    
    try:
        PyInstaller.__main__.run(params)
        print(f"\n✅ SUCCESS! Your fixed executable is at: dist/{name}.exe")
    except Exception as e:
        print(f"\n❌ Build failed: {e}")

if __name__ == '__main__':
    aggressive_build()

