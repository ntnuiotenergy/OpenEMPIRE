from pathlib import Path

import streamlit as st

from app.modules.input import input
from app.modules.output import output
from app.modules.utils import get_active_results


def app():
    
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

    st.sidebar.markdown(f"Current results:  {active_results}")

    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Output"

    with st.sidebar:
        st.session_state["current_page"] = st.radio("Navigate to", ["Output", "Input"])

    if st.session_state["current_page"] == "Input":
        input(active_results)
        # st.markdown("Currently disabled")

    elif st.session_state["current_page"] == "Output":
        output(active_results)


if __name__ == "__main__":
    st.set_page_config(layout="wide")

    import streamlit_authenticator as stauth
    import yaml
    from yaml.loader import SafeLoader

    with open("config/app.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        # config["authenticator"],
    )

    name, authenticatied, username = authenticator.login("Login", "main")
    
    if authenticatied:
        # st.write(f"Welcome *{name}*")
        app()
        authenticator.logout("Logout", "main")
    elif authenticatied is False:
        st.error("Username/password is incorrect")
    elif authenticatied is None:
        st.warning("Please enter your username and password")
