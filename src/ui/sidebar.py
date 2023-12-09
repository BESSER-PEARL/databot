import streamlit_antd_components as sac

from src.app.app import get_app


def sidebar_menu():
    page = sac.menu([
        sac.MenuItem('Playground', icon='robot'),
        sac.MenuItem('Admin', icon='person'),
        sac.MenuItem('Settings', icon='gear'),
        sac.MenuItem('About DataBot', icon='info-circle'),
    ], open_all=True)
    return page


def admin_menu():
    app = get_app()
    page = sac.menu([
        sac.MenuItem(type='divider'),
        sac.MenuItem('Manage project', icon='sliders', disabled=not app.projects),
        sac.MenuItem('All projects', icon='folder2-open', disabled=not app.projects),
        sac.MenuItem('New project', icon='plus-circle'),
    ], open_all=True, index=0 if app.projects else 2)
    return page
