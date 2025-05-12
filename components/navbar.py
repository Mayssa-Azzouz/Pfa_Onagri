import streamlit as st
from streamlit import query_params

def render_navbar(current_page: str = None):
    """Navbar responsive avec gestion d'état par URL"""
    COLORS = {
        "sky_blue": "#00B4D8",
        "vivid_orange": "#F8961E",
        "dark_blue": "#1A1A2E"
    }
    
    # Récupération de la page active depuis les query params si non spécifiée
    if current_page is None:
        current_page = query_params().get("page", "Accueil")

    st.markdown(f"""
    <style>
        /* Main responsive navbar */
        .main-nav {{
            position: fixed;
            top: 0;
            left: 0;
            height: 60px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-around;
            background-color: {COLORS['dark_blue']};
            padding: 0 10px;
            z-index: 1002;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        /* When sidebar is open */
        [data-testid="stSidebar"][aria-expanded="true"] ~ div .main-nav {{
            width: calc(100% - 300px);
            margin-left: 300px;
        }}

        .nav-item {{
            color: white !important;
            padding: 8px 20px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            margin: 0 5px;
            font-size: 15px;
        }}

        .nav-item:hover {{
            background-color: {COLORS['sky_blue']};
            transform: translateY(-2px);
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        .nav-item.active {{
            background-color: {COLORS['vivid_orange']};
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            font-weight: 600;
        }}

        /* Push content down */
        .block-container {{
            padding-top: 80px;
        }}

        /* Mobile responsive */
        @media (max-width: 768px) {{
            .main-nav {{
                height: auto;
                flex-wrap: wrap;
                padding: 10px;
            }}
            .nav-item {{
                margin: 5px;
                font-size: 14px;
                padding: 6px 12px;
            }}
            [data-testid="stSidebar"][aria-expanded="true"] ~ div .main-nav {{
                width: 100%;
                margin-left: 0;
            }}
            .block-container {{
                padding-top: 120px;
            }}
        }}
    </style>

    <nav class="main-nav" aria-label="Main navigation">
        <a href="/?page=Accueil" class="nav-item {'active' if current_page == 'Accueil' else ''}" aria-current="{'page' if current_page == 'Accueil' else 'false'}">🏠 Accueil</a>
        <a href="/Themes_ODD?page=Thèmes ODD" class="nav-item {'active' if current_page == 'Thèmes ODD' else ''}" aria-current="{'page' if current_page == 'Thèmes ODD' else 'false'}">🌍 Thèmes ODD</a>
        <a href="/Climat?page=Climat" class="nav-item {'active' if current_page == 'Climat' else ''}" aria-current="{'page' if current_page == 'Climat' else 'false'}">🌡️ Climat</a>
        <a href="/Donnees?page=Données" class="nav-item {'active' if current_page == 'Données' else ''}" aria-current="{'page' if current_page == 'Données' else 'false'}">📊 Données</a>
        <a href="/A_propos?page=À propos" class="nav-item {'active' if current_page == 'À propos' else ''}" aria-current="{'page' if current_page == 'À propos' else 'false'}">ℹ️ À propos</a>
    </nav>
    """, unsafe_allow_html=True)