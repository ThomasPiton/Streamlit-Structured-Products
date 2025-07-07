# config_module.py
import streamlit as st

def save_simulation(name, config, result):
    """
    Save the simulation parameters and results in Streamlit session state.
    """
    if 'saved_sims' not in st.session_state:
        st.session_state['saved_sims'] = {}
    st.session_state['saved_sims'][name] = {'config': config, 'result': result}

def load_simulation(name):
    """
    Retrieve a saved simulation by name.
    """
    return st.session_state['saved_sims'].get(name, None)
