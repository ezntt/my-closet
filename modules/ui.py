import streamlit as st
import pandas as pd
import unicodedata
from modules.database import salvar_roupa, atualizar_roupa, excluir_roupa, upload_imagem, buscar_roupas_usuario, registrar_emprestimo, registrar_devolucao
from modules.ai import analisar_imagem, sugerir_looks
from modules.config import CATEGORIAS, CORES, OCASIOES, ESTACOES, TECIDOS, ESTILOS
from time import sleep

# normalização de texto
def normalizar_texto(texto):
    if not texto: return ""
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII').lower()

# estilos css
def configurar_estilo():
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-bottom: 5rem;
            }
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            
            [data-testid="stVerticalBlockBorderWrapper"] {
                border-radius: 12px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                border: 1px solid #eee;
                background-color: white;
                padding: 10px;
                margin-bottom: 10px;
            }
            
            /* efeito hover na imagem */
            .img-hover:hover {
                opacity: 0.9;
                transform: scale(1.02);
                transition: all 0.2s ease-in-out;
                cursor: zoom-in;
            }
            
            button { border-radius: 8px !important; height: 3em !important; }
            input, select, textarea { border-radius: 8px !important; }
            
            h1 { font-size: 1.8rem !important; }
            h2 { font-size: 1.5rem !important; }
            h3 { font-size: 1.2rem !important; }
        </style>
    """, unsafe_allow_html=True)

# modais do sistema
@st.dialog("Registrar Empréstimo")
def modal_emprestimo(id_roupa, nome_peca):
    st.write(f"Emprestando: **{nome_peca}**")
    para_quem = st.text_input("Para quem?", placeholder="Ex: João")
    data_dev = st.date_input("Previsão de Devolução", value=None)
    obs = st.text_area("Observação", placeholder="Ex: Cuidado com a mancha")
    
    if st.button("Confirmar", type="primary", use_container_width=True):
        if para_quem:
            registrar_emprestimo(id_roupa, para_quem, data_dev, obs)
            st.success("Registrado!")
            sleep(0.5)
            st.rerun()
        else:
            st.warning("Informe o nome da pessoa.")

@st.dialog("Editar Peça")
def modal_editar(item):
    st.write(f"Editando: **{item['nome']}**")
    nova_foto = st.file_uploader("Trocar Foto", type=['jpg', 'png', 'jpeg'])
    
    if nova_foto:
        st.info("Nova foto selecionada.")
    elif item.get('imagem_url'):
        st.markdown(f"""
            <img src="{item['imagem_url']}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px;">
        """, unsafe_allow_html=True)

    nome = st.text_input("Nome da Peça", value=item['nome'])
    
    col1, col2 = st.columns(2)
    
    def get_index(lista, valor):
        try: return lista.index(valor)
        except: return 0

    with col1:
        cat = st.selectbox("Categoria", CATEGORIAS, index=get_index(CATEGORIAS, item.get('categoria')))
        cor = st.text_input("Cor", value=item.get('cor', '')) 
        marca = st.text_input("Marca", value=item.get('marca', ''))
        tecido = st.text_input("Tecido", value=item.get('tecido', ''))

    with col2:
        ocasiao = st.selectbox("Ocasião", OCASIOES, index=get_index(OCASIOES, item.get('ocasiao')))
        estacao = st.selectbox("Estação", ESTACOES, index=get_index(ESTACOES, item.get('estacao')))
        estilo = st.selectbox("Estilo", ESTILOS, index=get_index(ESTILOS, item.get('estilo')))

    if st.button("Salvar Alterações", type="primary", use_container_width=True):
        with st.spinner("Atualizando..."):
            dados = {
                "nome": nome, "categoria": cat, "cor": cor, "marca": marca,
                "ocasiao": ocasiao, "estacao": estacao, "tecido": tecido, "estilo": estilo
            }
            if nova_foto:
                url = upload_imagem(nova_foto, item['user_id'])
                if url: dados['imagem_url'] = url
            
            atualizar_roupa(item['id'], dados)
            st.success("Atualizado!")
            sleep(0.5)
            st.rerun()

@st.dialog("Confirmar Exclusão")
def modal_excluir(id_roupa, nome_peca):
    st.warning(f"Excluir **{nome_peca}**?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancelar", use_container_width=True): st.rerun()
    with col2:
        if st.button("Sim, Excluir", type="primary", use_container_width=True):
            excluir_roupa(id_roupa)
            st.success("Excluído.")
            sleep(0.5)
            st.rerun()

# aba de cadastro
def render_aba_cadastro(user_id):
    configurar_estilo()
    st.subheader("Nova Peça")
    
    foto_camera = st.camera_input("Tirar foto")
    uploaded_file_galeria = st.file_uploader("Ou galeria", type=['jpg', 'png', 'jpeg'])
    uploaded_file = foto_camera if foto_camera else uploaded_file_galeria
    
    if 'form' not in st.session_state:
        st.session_state.form = {
            "nome": "", "cat": "", "cor": "", "marca": "", 
            "ocasiao": "", "estacao": "Todas", "tecido": "", "estilo": ""
        }

    # processamento de imagem via ia
    if uploaded_file and st.button("✨ Preencher com IA", use_container_width=True):
        with st.spinner("A Stylist está analisando..."):
            uploaded_file.seek(0)
            dados_ia = analisar_imagem(uploaded_file)
            if dados_ia and len(dados_ia) >= 8:
                st.session_state.form['cat'] = dados_ia[0]
                st.session_state.form['cor'] = dados_ia[1]
                st.session_state.form['marca'] = dados_ia[2]
                st.session_state.form['nome'] = dados_ia[3]
                st.session_state.form['ocasiao'] = dados_ia[4]
                st.session_state.form['estacao'] = dados_ia[5]
                st.session_state.form['tecido'] = dados_ia[6]
                st.session_state.form['estilo'] = dados_ia[7]
                st.success("Dados preenchidos!")
            else:
                st.warning("Preencha manualmente.")

    with st.container(border=True):
        nome = st.text_input("Nome", value=st.session_state.form['nome'])
        col1, col2 = st.columns(2)
        
        def get_index(lista, valor):
            try: return lista.index(valor)
            except: return 0

        with col1:
            cat = st.selectbox("Categoria", CATEGORIAS, index=get_index(CATEGORIAS, st.session_state.form['cat']))
            cor = st.text_input("Cor", value=st.session_state.form['cor'])
            marca = st.text_input("Marca", value=st.session_state.form['marca'])
            tecido = st.text_input("Tecido", value=st.session_state.form['tecido'])

        with col2:
            ocasiao = st.selectbox("Ocasião", OCASIOES, index=get_index(OCASIOES, st.session_state.form['ocasiao']))
            estacao = st.selectbox("Estação", ESTACOES, index=get_index(ESTACOES, st.session_state.form['estacao']))
            estilo = st.selectbox("Estilo", ESTILOS, index=get_index(ESTILOS, st.session_state.form['estilo']))

    if st.button("Salvar no Guarda-Roupa", type="primary", use_container_width=True):
        if nome:
            with st.spinner("Salvando..."):
                url_img = None
                if uploaded_file:
                    uploaded_file.seek(0)
                    url_img = upload_imagem(uploaded_file, user_id)
                
                dados = {
                    "nome": nome, "categoria": cat, "cor": cor, "marca": marca,
                    "ocasiao": ocasiao, "estacao": estacao, "tecido": tecido, "estilo": estilo,
                    "user_id": user_id, "imagem_url": url_img
                }
                salvar_roupa(dados)
                st.success("Salvo!")
                st.session_state.form = {
                    "nome": "", "cat": "Camiseta", "cor": "", "marca": "", 
                    "ocasiao": "Casual", "estacao": "Todas", "tecido": "Algodão", "estilo": "Básico"
                }
                sleep(1)
                st.rerun()
        else:
            st.error("Nome obrigatório.")

# aba de acervo
def render_aba_closet():
    configurar_estilo()
    st.subheader("Meu Acervo")
    
    resp = buscar_roupas_usuario()
    roupas = resp.data
    
    if not roupas:
        st.info("Nenhuma roupa cadastrada.")
        return

    # filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        pesquisa = st.text_input("🔎 Pesquisar", placeholder="Ex: calça preta").strip()
    with col_f2:
        filtro_status = st.selectbox("Status", ["Todos", "Disponível", "Emprestado"])

    # filtragem de itens
    if pesquisa:
        termo_busca = normalizar_texto(pesquisa)
        roupas = [
            r for r in roupas 
            if termo_busca in normalizar_texto(r['nome']) or 
               termo_busca in normalizar_texto(r['categoria']) or 
               termo_busca in normalizar_texto(r['cor']) or 
               termo_busca in normalizar_texto(r['marca'])
        ]
    
    if filtro_status != "Todos":
        roupas = [r for r in roupas if r['status'] == filtro_status]

    # grid de roupas
    cols = st.columns(2)
    
    for index, item in enumerate(roupas):
        with cols[index % 2]:
            with st.container(border=True):
                # imagem com link expansível
                if item.get('imagem_url'):
                    st.markdown(f"""
                        <a href="{item['imagem_url']}" target="_blank" title="Clique para ampliar">
                            <div class="img-hover" style="height: 150px; overflow: hidden; border-radius: 8px; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; margin-bottom: 8px;">
                                <img src="{item['imagem_url']}" style="width: 100%; height: 100%; object-fit: cover;">
                            </div>
                        </a>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div style="height: 50px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-bottom: 8px; color: #aaa;">
                            Sem Foto
                        </div>
                    """, unsafe_allow_html=True)
                
                # detalhes
                st.markdown(f"**{item['nome']}**")
                st.caption(f"{item['categoria']} • {item['cor']}")
                
                # status
                if item['status'] == 'Disponível':
                    st.markdown(":green[Disponível]")
                else:
                    st.markdown(f":red[Emprestado] para {item.get('emprestado_para')}")

                # botões de ação
                with st.popover("⚙️ Opções", use_container_width=True):
                    if item['status'] == 'Disponível':
                        if st.button("Emprestar", key=f"emp_{item['id']}", use_container_width=True):
                            modal_emprestimo(item['id'], item['nome'])
                    else:
                        if st.button("Devolver", key=f"dev_{item['id']}", type="primary", use_container_width=True):
                            registrar_devolucao(item['id'])
                            st.rerun()

                    if st.button("Editar", key=f"edt_{item['id']}", use_container_width=True):
                        modal_editar(item)
                    
                    st.divider()
                    if st.button("Excluir", key=f"exc_{item['id']}", type="primary", use_container_width=True):
                        modal_excluir(item['id'], item['nome'])

# aba personal stylist
def render_aba_stylist():
    configurar_estilo()
    st.markdown("## 🤖 AI Personal Stylist")
    st.caption("Escolha a ocasião e deixe a IA montar seus looks com o que você já tem.")
    
    resp = buscar_roupas_usuario()
    todas_roupas = resp.data
    disponiveis = [r for r in todas_roupas if r['status'] == 'Disponível']
    
    if len(disponiveis) < 2:
        st.warning("Cadastre pelo menos 2 peças disponíveis para usar o Stylist.")
        return
    
    opcoes_stylist = OCASIOES + ["Dia Frio", "Dia Quente", "Encontro Romântico"]
    ocasiao = st.selectbox("Qual a ocasião?", opcoes_stylist)       
    
    if st.button("✨ Gerar Looks com IA", type="primary", use_container_width=True):
        with st.spinner("A Stylist está no closet escolhendo as peças..."):
            sugestoes = sugerir_looks(disponiveis, ocasiao)
            if sugestoes:
                st.session_state['looks_gerados'] = sugestoes
            else:
                st.error("A IA não conseguiu montar looks agora.")

    if 'looks_gerados' in st.session_state:
        st.divider()
        for i, look in enumerate(st.session_state['looks_gerados']):
            with st.container(border=True):
                st.markdown(f"### Look {i+1}: {look.get('nome_look', 'Sugestão')}")
                
                explicacao = look.get('explicacao', '')
                st.markdown(f"**Dica da Stylist:**\n_{explicacao}_")
                
                st.divider()
                st.caption("Peças utilizadas:")
                
                ids = look.get('ids_pecas', [])
                pecas_do_look = [p for p in disponiveis if p['id'] in ids]
                
                if pecas_do_look:
                    cols_look = st.columns(len(pecas_do_look))
                    for idx, peca in enumerate(pecas_do_look):
                        with cols_look[idx]:
                            if peca.get('imagem_url'):
                                # imagem com link expansível
                                st.markdown(f"""
                                    <a href="{peca['imagem_url']}" target="_blank" title="Clique para ampliar">
                                        <div class="img-hover" style="height: 80px; overflow: hidden; border-radius: 8px; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa;">
                                            <img src="{peca['imagem_url']}" style="width: 100%; height: 100%; object-fit: cover;">
                                        </div>
                                    </a>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("🖼️")
                            st.caption(peca['nome'], help=f"{peca['marca']} - {peca['cor']}")