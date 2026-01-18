import streamlit as st
from modules.auth import render_login, logout, verificar_sessao_cookie
from modules.ui import render_aba_cadastro, render_aba_closet, render_aba_stylist

# configuração da página
st.set_page_config(page_title="My Closet", page_icon="👕", layout="centered")

# inicializa sessão
if 'user' not in st.session_state:
    st.session_state.user = None

def main():
    # tenta recuperar sessão via cookie
    if not st.session_state.user:
        verificar_sessao_cookie()

    # caso continue sem usuário
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

        st.title("My Closet")
        
        # 3 abas principais
        closet, cadastro, stylist = st.tabs(["Acervo", "Cadastrar", "Stylist"])
        
        with closet:
            render_aba_closet()
        
        with cadastro:
            render_aba_cadastro(st.session_state.user.id)
            
        with stylist:
            render_aba_stylist()

if __name__ == "__main__":
    main()