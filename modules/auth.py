import streamlit as st
from modules.database import supabase
from time import sleep

def configurar_estilo_login():
    st.markdown("""
        <style>
            .block-container { padding-top: 2rem; }
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Centraliza o container de login */
            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                background: white;
                padding: 2rem;
            }
        </style>
    """, unsafe_allow_html=True)

def render_login():
    configurar_estilo_login()
    st.markdown("## Login")

    with st.container(border=True):
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        
        login, cadastro = st.columns(2)

        with login:
            if st.button("Entrar", type="primary", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.success("Entrando...")
                    sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

        with cadastro:
            with st.expander("Cadastrar"):
                nome_completo = st.text_input("Nome Completo")
                if st.button("Criar Conta", use_container_width=True):
                    try:
                        res = supabase.auth.sign_up({
                            "email": email, 
                            "password": password,
                            "options": {"data": {"full_name": nome_completo}}
                        })
                        st.session_state.user = res.user
                        st.success("Conta criada!")
                        sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

def logout():
    supabase.auth.sign_out()
    st.session_state.user = None
    st.rerun()