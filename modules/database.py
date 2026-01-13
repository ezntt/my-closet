import streamlit as st
from supabase import create_client, Client
import datetime

@st.cache_resource  # evita reconexões desnecessárias
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = init_connection()

# bucket no supabase
def upload_imagem(file, user_id):
    try:

        user_path = str(user_id)
        
        # limpa nome do arquivo
        file_ext = file.name.split('.')[-1]
        timestamp = datetime.datetime.now().timestamp()
        file_name = f"{user_path}/{timestamp}.{file_ext}"
        
        file_bytes = file.getvalue()
        
        # Upload
        res = supabase.storage.from_("fotos-roupas").upload(
            path=file_name,
            file=file_bytes,
            file_options={"content-type": file.type}
        )
        
        return supabase.storage.from_("fotos-roupas").get_public_url(file_name)
        
    except Exception as e:
        st.error(f"Erro detalhado no upload: {e}")
        return None

def salvar_roupa(dados):
    return supabase.table("roupas").insert(dados).execute()

def buscar_roupas_usuario():
    return supabase.table("roupas").select("*").order("created_at", desc=True).execute()

def registrar_emprestimo(id_roupa, nome_pessoa, data_dev, obs):
    dados = {
        "status": "Emprestado",
        "emprestado_para": nome_pessoa,
        "observacoes": obs,
        "data_devolucao": data_dev.isoformat() if data_dev else None
    }
    return supabase.table("roupas").update(dados).eq("id", id_roupa).execute()

def registrar_devolucao(id_roupa):
    dados = {
        "status": "Disponível",
        "emprestado_para": None,
        "data_devolucao": None,
        "observacoes": None
    }
    return supabase.table("roupas").update(dados).eq("id", id_roupa).execute()

def excluir_roupa(id_roupa):
    return supabase.table("roupas").delete().eq("id", id_roupa).execute()