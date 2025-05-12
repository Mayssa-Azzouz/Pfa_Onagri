# config.py
COLORS = {
    "primary": "#2E8B57",        # Vert principal (Sea Green)
    "dark": "#1A5D1A",           # Vert foncé (Forest Green)
    "light": "#90EE90",          # Vert clair (Light Green)
    "accent": "#32CD32",         # Vert accent (Lime Green)
    "background": "#F5F5F5",     # Fond gris clair
    "text_dark": "#1A3A1A",      # Texte foncé
    "text_light": "#FFFFFF"      # Texte clair
}

NAVBAR_STYLE = f"""
<style>
    /* Navbar verte */
    .main-nav {{
        background-color: {COLORS['dark']} !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .nav-item:hover {{
        background-color: {COLORS['primary']} !important;
    }}
    .nav-item.active {{
        background-color: {COLORS['accent']} !important;
        color: {COLORS['text_dark']} !important;
    }}
    
    /* Sidebar verte */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['dark']} !important;
    }}
    .sidebar .sidebar-content {{
        background: linear-gradient(180deg, {COLORS['dark']}, {COLORS['primary']}) !important;
    }}
</style>
"""

SIDEBAR_HEADER_STYLE = f"""
<div style="
    background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
    color: {COLORS['text_light']};
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 30px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
">
"""