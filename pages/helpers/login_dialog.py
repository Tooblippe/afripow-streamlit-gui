import streamlit as st


@st.dialog("Login")
def login_dialog():
    st.write(f"Username:", key="username")
    un = st.text_input(f"Username...{st.session_state.get('logged_in',False)}", key="uninput")
    st.write("Password:", key="password")
    pw = st.text_input("password", key="pwinput")
    if st.button("Login", key="btnloginqw"):
        if pw == 'abc':
            st.session_state['logged_in'] = True
        else:
            st.session_state['logged_in'] = False

        st.rerun()
