import streamlit as st

pages = {
    "Simulation": [
        st.Page("pages/simulation.py", title="Simulation", icon=":material/monitoring:"),
    ],
    "Others": [
        st.Page("pages/about.py", title="About", icon=":material/info:"),
        st.Page("pages/faq.py", title="FAQ", icon=":material/help:"),
        st.Page("pages/contact.py", title="Contact", icon=":material/contacts_product:"),
    ],
}

# --- Render Navigation ---
pg = st.navigation(pages)

# --- Show Logo ---
st.logo("static/img/bank_logo.png", icon_image="static/img/bank_logo.png")

pg.run()
