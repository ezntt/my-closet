import streamlit as st
import extra_streamlit_components as stx
from modules.database import supabase
from time import sleep
import datetime

# gerenciador de cookies
def get_manager(key="init"):
    return stx.CookieManager(key=key)

def configurar_estilo_login():
    st.markdown("""
        <style>
            .block-container { padding-top: 2rem; }
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            div[data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 12px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                background: white;
                padding: 2rem;
            }
        </style>
    """, unsafe_allow_html=True)

# verificação de sessão ativa
def verificar_sessao_cookie():
    try:
        cookie_manager = get_manager(key="cookie_check")
        token = cookie_manager.get(cookie="sb_token")
        
        if token and st.session_state.user is None:
            # valida token no supabase
            res = supabase.auth.get_user(token)
            if res and res.user:
                st.session_state.user = res.user
                return True
    except Exception as e:
        print(f"Sessão não restaurada: {e}")
        return False
    
    return False

# renderiza tela de login
def render_login():
    configurar_estilo_login()
    cookie_manager = get_manager(key="cookie_login")

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
                    
                    # salva token (30 dias)
                    if res.session:
                        token = res.session.access_token
                        cookie_manager.set("sb_token", token, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))
                    
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
                        if res.session:
                             cookie_manager.set("sb_token", res.session.access_token, expires_at=datetime.datetime.now() + datetime.timedelta(days=30))

                        st.success("Conta criada!")
                        sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro: {e}")

# encerra sessão
def logout():
    try:
        cookie_manager = get_manager(key="cookie_logout")
        cookie_manager.delete("sb_token")
    except:
        pass
        
    supabase.auth.sign_out()
    st.session_state.user = None
    
    sleep(0.5)
    st.rerun()