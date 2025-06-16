"""
Fix module imports for cx_Freeze build
"""

import os
import sys

def fix_build_imports():
    """Fix module import issues in the build directory"""
    
    build_dir = "build/exe.win-amd64-3.13"
    
    if not os.path.exists(build_dir):
        print("❌ Build directory not found!")
        return False
    
    # Create __init__.py files to make directories proper Python packages
    init_dirs = [
        build_dir,
        os.path.join(build_dir, "modules"),
        os.path.join(build_dir, "utils"),
        os.path.join(build_dir, "tests")
    ]
    
    for dir_path in init_dirs:
        if os.path.exists(dir_path):
            init_file = os.path.join(dir_path, "__init__.py")
            if not os.path.exists(init_file):
                with open(init_file, 'w', encoding='utf-8') as f:
                    f.write("# Package initialization\n")
                print(f"Created {init_file}")
    
    # Create a startup script that fixes the Python path
    startup_script = os.path.join(build_dir, "fix_paths.py")
    with open(startup_script, 'w', encoding='utf-8') as f:
        f.write("""
import sys
import os

# Add current directory and subdirectories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'modules'))
sys.path.insert(0, os.path.join(current_dir, 'utils'))
sys.path.insert(0, os.path.join(current_dir, 'tests'))

print("Python paths fixed for standalone execution")
""")
    
    print(f"✓ Created {startup_script}")
    
    # Update the main kitchen_app.py to include the path fix
    main_app = os.path.join(build_dir, "kitchen_app.py")
    if os.path.exists(main_app):
        # Read the current content
        with open(main_app, 'r') as f:
            content = f.read()
        
        # Add path fix at the beginning
        path_fix = """
# Fix Python paths for standalone execution
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'modules'))
sys.path.insert(0, os.path.join(current_dir, 'utils'))

"""
        
        # Only add if not already present
        if "Fix Python paths for standalone execution" not in content:
            with open(main_app, 'w', encoding='utf-8') as f:
                f.write(path_fix + content)
            print(f"Updated {main_app} with path fixes")
    
    print("\n🎉 Build import fixes completed!")
    return True

if __name__ == "__main__":
    fix_build_imports()
