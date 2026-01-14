import streamlit as st
import extra_streamlit_components as stx
from modules.database import supabase
from time import sleep
import datetime

# O @st.cache_resource garante que o gerenciador seja carregado uma única vez
@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()

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

# checa se há sessão válida no cookie
def verificar_sessao_cookie():
    cookie_manager = get_manager()
    
    token = cookie_manager.get(cookie="sb_token")
    
    if token and st.session_state.user is None:
        try:
            # Pergunta pro Supabase: "Esse token ainda vale?"
            res = supabase.auth.get_user(token)
            if res and res.user:
                st.session_state.user = res.user
                return True
        except Exception as e:
            # Se o token for inválido/expirado, apaga ele
            print(f"Token inválido: {e}")
            cookie_manager.delete("sb_token")
            return False
    return False

def render_login():
    configurar_estilo_login()
    cookie_manager = get_manager()
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
                    
                    # salva o cookie com validade de 30 dias
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

def logout():
    # Remove do banco (opcional), remove do state e remove do cookie
    supabase.auth.sign_out()
    st.session_state.user = None
    
    cookie_manager = get_manager()
    cookie_manager.delete("sb_token")
    
    sleep(0.5) # Dá tempo do cookie ser deletado
    st.rerun()