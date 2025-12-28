"""
Logo Diagnostic Page
Temporary debugging page to test logo display
"""

import streamlit as st
import sys
from pathlib import Path
import os

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(page_title="Logo Test", page_icon="🔍", layout="wide")

st.title("🔍 Logo Display Diagnostics")
st.markdown("---")

# Test 1: Check current working directory
st.header("1. Current Working Directory")
cwd = os.getcwd()
st.code(cwd)
st.success(f"✓ Working from: {cwd}")

# Test 2: Check if assets folder exists
st.header("2. Assets Folder Check")
possible_asset_paths = [
    Path(cwd) / "assets",
    Path(__file__).parent.parent / "assets",
    Path("assets"),
    Path("/mount/src/mind-platform/assets"),
    Path("/app/assets"),
]

for asset_path in possible_asset_paths:
    exists = asset_path.exists()
    if exists:
        st.success(f"✓ FOUND: {asset_path}")
        # List contents
        try:
            contents = list(asset_path.iterdir())
            st.write(f"   Contents: {[f.name for f in contents]}")
        except Exception as e:
            st.write(f"   Could not list contents: {e}")
    else:
        st.warning(f"✗ Not found: {asset_path}")

# Test 3: Look for logo files specifically
st.header("3. Logo Files Search")
logo_names = ["miva_logo_dark.png", "miva_logo_light.png"]

for logo_name in logo_names:
    st.subheader(f"Looking for: {logo_name}")
    found = False
    
    for asset_path in possible_asset_paths:
        logo_path = asset_path / logo_name
        if logo_path.exists():
            st.success(f"✓ FOUND: {logo_path}")
            st.write(f"   File size: {logo_path.stat().st_size} bytes")
            found = True
            
            # Try to display it
            try:
                st.image(str(logo_path), width=200, caption=f"Successfully loaded: {logo_name}")
            except Exception as e:
                st.error(f"   Error displaying: {e}")
    
    if not found:
        st.error(f"✗ {logo_name} NOT FOUND in any location")

# Test 4: Try logo handler
st.header("4. Logo Handler Test")
try:
    from utils.logo_handler import display_logo, get_logo_path
    st.success("✓ Logo handler imported successfully")
    
    # Get path
    logo_path = get_logo_path(dark_mode=True)
    if logo_path:
        st.success(f"✓ Logo path resolved: {logo_path}")
        st.write(f"   File exists: {os.path.exists(logo_path)}")
    else:
        st.error("✗ Logo path is None - logo not found by handler")
    
    # Try to display
    st.subheader("Attempting to display logo via handler:")
    display_logo("main", width=200)
    
except Exception as e:
    st.error(f"✗ Error with logo handler: {e}")
    import traceback
    st.code(traceback.format_exc())

# Test 5: Python path
st.header("5. Python Path")
st.write("sys.path entries:")
for i, path in enumerate(sys.path):
    st.code(f"{i}: {path}")

# Test 6: File structure
st.header("6. Repository Structure")
try:
    repo_root = Path(__file__).parent.parent
    st.write(f"Repository root: {repo_root}")
    
    # List top-level directories
    st.write("Top-level contents:")
    for item in sorted(repo_root.iterdir()):
        if item.is_dir():
            st.write(f"📁 {item.name}/")
        else:
            st.write(f"📄 {item.name}")
except Exception as e:
    st.error(f"Error exploring structure: {e}")

st.markdown("---")
st.info("💡 **Instructions:** Once you see where the logo files are (or aren't), you can fix the path in logo_handler.py")
