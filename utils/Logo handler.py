"""
Logo Display Utility
Handles MIVA logo display for dark/light modes
"""

import streamlit as st
import os
from pathlib import Path


def get_logo_path(dark_mode=True):
    """
    Get the path to the appropriate logo based on theme
    
    Args:
        dark_mode: True for dark theme, False for light theme
        
    Returns:
        Path to logo file or None if not found
    """
    assets_dir = Path(__file__).parent.parent / "assets"
    
    if dark_mode:
        logo_file = assets_dir / "miva_logo_dark.png"
    else:
        logo_file = assets_dir / "miva_logo_light.png"
    
    if logo_file.exists():
        return str(logo_file)
    
    return None


def display_logo(location="sidebar", width=200):
    """
    Display MIVA logo in specified location
    
    Args:
        location: "sidebar", "main", or "login"
        width: Logo width in pixels
    """
    # Currently using dark mode theme
    logo_path = get_logo_path(dark_mode=True)
    
    if logo_path and os.path.exists(logo_path):
        if location == "sidebar":
            st.sidebar.image(logo_path, width=width)
        elif location == "main":
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo_path, width=width)
        elif location == "login":
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo_path, width=width)
    else:
        # Fallback to text logo if image not found
        if location == "sidebar":
            st.sidebar.markdown("### 🎓 MIVA")
        else:
            st.markdown("# 🎓 MIVA")


def get_logo_base64():
    """
    Get logo as base64 string for CSS embedding
    Useful for adding logo to headers or backgrounds
    """
    import base64
    
    logo_path = get_logo_path(dark_mode=True)
    
    if logo_path and os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode()
    
    return None
