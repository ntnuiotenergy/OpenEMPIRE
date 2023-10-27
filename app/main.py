import streamlit as st
from pathlib import Path

from app.modules.utils import get_active_results

from app.modules.input import input
from app.modules.output import output

st.set_page_config(layout="wide")

st.title("OpenEMPIRE")

st.markdown(
    """
Use this app to analyze results from Empire runs. 

Select the input button to see inputs from the available model runs. Select the output button to see the results.

The app searches for results from the working directory, but you can also provide an absolute path in the sidebar to results located elsewhere.
"""
)

result_folder = Path.cwd() / "Results"
other_results = st.sidebar.text_input("Absolute path to other folder with results:")

if other_results:
    other_results = Path(other_results)
    if not other_results.exists():
        raise ValueError("Cannot find the results folder specified")

    active_results = get_active_results([result_folder, other_results])

else:
    active_results = get_active_results([result_folder])



if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Input'

with st.sidebar:
    st.session_state['current_page'] = st.radio("Navigate to", ['Input', 'Output'])

if st.session_state['current_page'] == 'Input':
    input(active_results)
elif st.session_state['current_page'] == 'Output':
    output(active_results)