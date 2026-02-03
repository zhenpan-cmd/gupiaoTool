#!/usr/bin/env python3
"""
System Health Check for OpenClaw Assistant
Verifies all core functionalities are working properly
"""

import sys
import os
import subprocess
import importlib.util
from datetime import datetime

def check_python_environment():
    """Check Python environment and key dependencies"""
    print("🔍 Checking Python environment...")
    
    # Check Python version
    python_version = sys.version
    print(f"  ✓ Python version: {python_version.split()[0]}")
    
    # Check key libraries
    libraries = [
        'pandas',
        'numpy', 
        'requests',
        'akshare',
        'easyquotation'
    ]
    
    for lib in libraries:
        try:
            importlib.import_module(lib)
            print(f"  ✓ {lib} available")
        except ImportError:
            print(f"  ⚠ {lib} not available")
    
    print()

def check_workspace_files():
    """Check essential workspace files"""
    print("📁 Checking workspace files...")
    
    essential_files = [
        'AGENTS.md',
        'SOUL.md', 
        'USER.md',
        'IDENTITY.md',
        'MEMORY.md',
        'TOOLS.md'
    ]
    
    for file in essential_files:
        if os.path.exists(file):
            print(f"  ✓ {file} exists")
        else:
            print(f"  ⚠ {file} missing")
    
    # Check memory directory
    if os.path.exists('memory'):
        print(f"  ✓ memory/ directory exists")
    else:
        print(f"  ⚠ memory/ directory missing")
    
    print()

def check_git_config():
    """Check Git configuration"""
    print("📦 Checking Git configuration...")
    
    try:
        result = subprocess.run(['git', 'config', '--global', 'user.name'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            print(f"  ✓ Git username configured: {result.stdout.strip()}")
        else:
            print(f"  ⚠ Git username not configured")
    except:
        print(f"  ⚠ Git not accessible")
    
    try:
        result = subprocess.run(['git', 'status'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✓ Git repository accessible")
        else:
            print(f"  ⚠ Not in Git repository")
    except:
        print(f"  ⚠ Git not accessible")
    
    print()

def check_memory_maintenance():
    """Check memory maintenance status"""
    print("🧠 Checking memory maintenance...")
    
    # Check if today's memory file exists
    today = datetime.now().strftime('%Y-%m-%d')
    today_file = f'memory/{today}.md'
    
    if os.path.exists(today_file):
        print(f"  ✓ Today's memory file exists: {today_file}")
    else:
        print(f"  ⚠ Today's memory file missing: {today_file}")
    
    # Check if MEMORY.md exists
    if os.path.exists('MEMORY.md'):
        print(f"  ✓ Long-term memory file exists")
    else:
        print(f"  ⚠ Long-term memory file missing")
    
    print()

def check_tools_availability():
    """Check tool availability"""
    print("🛠️  Checking tool availability...")
    
    tools = [
        ('python3', '--version'),
        ('git', '--version'), 
        ('pip', '--version'),
    ]
    
    for tool, arg in tools:
        try:
            result = subprocess.run([tool, arg], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_line = result.stdout.strip().split('\n')[0]
                print(f"  ✓ {tool}: {version_line}")
            else:
                print(f"  ⚠ {tool} failed with code {result.returncode}")
        except FileNotFoundError:
            print(f"  ⚠ {tool} not found")
        except Exception as e:
            print(f"  ⚠ {tool} error: {e}")
    
    print()

def check_essential_directories():
    """Check essential directories"""
    print("📂 Checking essential directories...")
    
    dirs = [
        'memory',
        '.git'
    ]
    
    for dir_name in dirs:
        if os.path.exists(dir_name) and os.path.isdir(dir_name):
            print(f"  ✓ {dir_name}/ exists")
        else:
            print(f"  ⚠ {dir_name}/ missing or not a directory")
    
    print()

def run_complete_check():
    """Run complete system health check"""
    print("🏥 Running Complete System Health Check")
    print("="*50)
    print(f"Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_python_environment()
    check_workspace_files()
    check_git_config()
    check_memory_maintenance()
    check_tools_availability()
    check_essential_directories()
    
    print("🎉 System health check completed!")
    print()
    print("💡 Remember: Run this check regularly to ensure system integrity.")
    print("📝 Update your memory files to keep track of system changes.")

if __name__ == "__main__":
    run_complete_check()