"""
Logo Display Utility - Alternative Version with GitHub URL Fallback
Handles MIVA logo display with multiple fallback strategies
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
            # Streamlit Cloud deployment path (update with your repo name)
            Path("/mount/src/mind-platform/assets") / logo_filename,
            # Alternative Streamlit Cloud path
            Path("/app/assets") / logo_filename,
            # Relative to this file (utils/logo_handler.py)
            Path(__file__).parent.parent / "assets" / logo_filename,
            # Relative to current working directory
            Path.cwd() / "assets" / logo_filename,
            # Direct path from root
            Path("assets") / logo_filename,
        ]
        
        # Return first path that exists
        for path in possible_paths:
            if path.exists():
                return str(path)
        
        return None
    except Exception:
        return None


def get_github_logo_url(dark_mode=True, github_user="MivasPrince", repo_name="Mind-platform", branch="main"):
    """
    Get direct URL to logo on GitHub (fallback method)
    
    Args:
        dark_mode: True for dark theme, False for light theme
        github_user: Your GitHub username
        repo_name: Your repository name
        branch: Branch name (usually 'main' or 'master')
        
    Returns:
        URL string to logo on GitHub
    """
    logo_filename = "miva_logo_dark.png" if dark_mode else "miva_logo_light.png"
    return f"https://raw.githubusercontent.com/{github_user}/{repo_name}/{branch}/assets/{logo_filename}"


def display_logo(location="sidebar", width=200, use_github_fallback=True):
    """
    Display MIVA logo in specified location
    First tries local file, then falls back to GitHub URL if enabled
    
    Args:
        location: "sidebar", "main", or "login"
        width: Logo width in pixels
        use_github_fallback: If True, uses GitHub raw URL when local file not found
    """
    try:
        # Try local file first
        logo_path = get_logo_path(dark_mode=True)
        
        if logo_path and os.path.exists(logo_path):
            # Local file found
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
        
        elif use_github_fallback:
            # Local file not found, try GitHub URL
            github_url = get_github_logo_url(dark_mode=True)
            
            if location == "sidebar":
                st.sidebar.image(github_url, width=width)
            elif location == "main":
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(github_url, width=width)
            elif location == "login":
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(github_url, width=width)
        
        # If both methods fail, silently do nothing
    except Exception as e:
        # Uncomment for debugging:
        # if location == "sidebar":
        #     st.sidebar.caption(f"Logo error: {str(e)}")
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
