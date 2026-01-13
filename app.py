import streamlit as st
from modules.auth import render_login, logout
from modules.ui import render_aba_cadastro, render_aba_acervo, render_aba_stylist

st.set_page_config(page_title="My Closet", page_icon="👕", layout="centered")

if 'user' not in st.session_state:
    st.session_state.user = None

def main():
    if not st.session_state.user:
        render_login()
    else:
        user_meta = st.session_state.user.user_metadata
        nome_display = user_meta.get('full_name', st.session_state.user.email)
        
        with st.sidebar:
            st.write(f"👤 **{nome_display}**")
            st.divider()
            if st.button("Sair"):
                logout()

        st.title("Meu Guarda-Roupa")
        
        # AGORA COM 3 ABAS
        closet, cadastro, stylist = st.tabs(["Acervo", "Cadastrar", "Stylist"])
        
        with closet:
            render_aba_acervo()
        
        with cadastro:
            render_aba_cadastro(st.session_state.user.id)
            
        with stylist:
            render_aba_stylist()

if __name__ == "__main__":
    main()