import streamlit as st
from modules.auth import render_login, logout
from modules.ui import render_aba_cadastro, render_aba_acervo

st.set_page_config(page_title="My Closet", page_icon="👕", layout="centered")

if 'user' not in st.session_state:
    st.session_state.user = None

def main():
    if not st.session_state.user:
        render_login()
    else:
        meta = st.session_state.user.user_metadata
        nome = meta.get('full_name', st.session_state.user.email)
        
        with st.sidebar:
            st.write(f"👤 **{nome}**")
            st.divider()
            if st.button("Sair"):
                logout()

        st.title("Meu Guarda-Roupa")
        
        t1, t2 = st.tabs(["Novo", "Guarda-Roupa"])
        
        with t1:
            render_aba_cadastro(st.session_state.user.id)
        with t2:
            render_aba_acervo()

if __name__ == "__main__":
    main()