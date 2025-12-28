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
    Tries multiple possible locations for logo files
    
    Args:
        dark_mode: True for dark theme, False for light theme
        
    Returns:
        Path to logo file or None if not found
    """
    try:
        logo_filename = "miva_logo_dark.png" if dark_mode else "miva_logo_light.png"
        
        # Try multiple possible locations
        possible_paths = [
            # Streamlit Cloud deployment path (CONFIRMED WORKING)
            Path("/mount/src/mind-platform/assets") / logo_filename,
            # Direct path from root
            Path("assets") / logo_filename,
            # Relative to current working directory
            Path.cwd() / "assets" / logo_filename,
            # Relative to this file (utils/logo_handler.py)
            Path(__file__).parent.parent / "assets" / logo_filename,
        ]
        
        # Return first path that exists (skip paths with permission errors)
        for path in possible_paths:
            try:
                if path.exists():
                    return str(path)
            except (PermissionError, OSError):
                # Skip paths that can't be accessed
                continue
        
        return None
    except Exception:
        return None


def display_logo(location="sidebar", width=200):
    """
    Display MIVA logo in specified location
    Fails silently if logo files don't exist
    
    Args:
        location: "sidebar", "main", or "login"
        width: Logo width in pixels
    """
    try:
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
        # If no logo file exists, do nothing (fail silently)
    except Exception as e:
        # Silently fail - don't break the app if logo doesn't exist
        # Uncomment below for debugging:
        # st.sidebar.caption(f"Logo not found: {str(e)}")
        pass


def get_logo_base64():
    """
    Get logo as base64 string for CSS embedding
    Useful for adding logo to headers or backgrounds
    
    Returns:
        Base64 encoded string or None if logo not found
    """
    try:
        import base64
        
        logo_path = get_logo_path(dark_mode=True)
        
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                data = f.read()
                return base64.b64encode(data).decode()
        
        return None
    except Exception:
        return None
