import streamlit as st
import streamlit.components.v1 as components

# Configure the Streamlit page to take up the whole screen
st.set_page_config(page_title="The Abandoned Wing", layout="wide", initial_sidebar_state="collapsed")

# Read the HTML, CSS, and JS files
with open("index.html", "r", encoding="utf-8") as f:
    html_code = f.read()
with open("style.css", "r", encoding="utf-8") as f:
    css_code = f.read()
with open("game.js", "r", encoding="utf-8") as f:
    js_code = f.read()

# Inline the CSS and JS into the HTML so Streamlit's iframe can load them without routing issues
final_html = html_code.replace(
    '<link rel="stylesheet" href="style.css">',
    f'<style>\n{css_code}\n</style>'
).replace(
    '<script src="game.js"></script>',
    f'<script>\n{js_code}\n</script>'
)

# Render the game inside Streamlit
# Note: Height is set high to simulate full screen. 
components.html(final_html, height=850, scrolling=False)