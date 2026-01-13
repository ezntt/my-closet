import streamlit as st
from modules.database import supabase
from time import sleep

def render_login():
    st.markdown("## 🔐 Acesso ao Acervo")
    
    # Formulário simples centralizado
    with st.container(border=True):
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Entrar", type="primary", use_container_width=True):
                try:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.success("Entrando...")
                    sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

        with c2:
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