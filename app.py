import streamlit as st
import streamlit.components.v1 as components
import re

st.set_page_config(page_title="The Abandoned Wing", layout="wide", initial_sidebar_state="collapsed")

# Read the files
with open("index.html", "r", encoding="utf-8") as f:
    html_code = f.read()
with open("style.css", "r", encoding="utf-8") as f:
    css_code = f.read()
with open("game.js", "r", encoding="utf-8") as f:
    js_code = f.read()

# Use regex to replace the tags to avoid exact-string-match failures
html_with_css = re.sub(
    r'<link[^>]*rel="stylesheet"[^>]*href="style\.css"[^>]*>', 
    f'<style>\n{css_code}\n</style>', 
    html_code
)

final_html = re.sub(
    r'<script[^>]*src="game\.js"[^>]*></script>', 
    f'<script>\n{js_code}\n</script>', 
    html_with_css
)

# Render the game
components.html(final_html, height=850, scrolling=False)
