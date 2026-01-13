import streamlit as st
import pandas as pd
from modules.database import salvar_roupa, atualizar_roupa, excluir_roupa, upload_imagem, buscar_roupas_usuario, registrar_emprestimo, registrar_devolucao
from modules.ai import analisar_imagem
from time import sleep

# modal do empréstimo
@st.dialog("Registrar Empréstimo")
def modal_emprestimo(id_roupa, nome_peca):
    st.write(f"Emprestando: **{nome_peca}**")
    
    para_quem = st.text_input("Para quem?", placeholder="Ex: João")
    data_dev = st.date_input("Previsão de Devolução", value=None)
    obs = st.text_area("Observação", placeholder="Ex: Cuidado com a mancha")
    
    if st.button("Confirmar", type="primary"):
        if para_quem:
            registrar_emprestimo(id_roupa, para_quem, data_dev, obs)
            st.success("Registrado!")
            sleep(0.5)
            st.rerun()
        else:
            st.warning("Informe o nome da pessoa.")

# modal de edição (NOVO)
@st.dialog("Editar Peça")
def modal_editar(item):
    st.write(f"Editando: **{item['nome']}**")
    
    # upload de nova foto (opcional)
    nova_foto = st.file_uploader("Trocar Foto", type=['jpg', 'png', 'jpeg'])
    if nova_foto:
        st.info("Nova foto selecionada (será salva ao confirmar).")
    elif item.get('imagem_url'):
        st.image(item['imagem_url'], width=150, caption="Foto Atual")

    # campos preenchidos com valor atual
    nome = st.text_input("Nome da Peça", value=item['nome'])
    
    col1, col2 = st.columns(2)
    
    # mesmas listas do cadastro
    opt_cats = ["Camiseta", "Calça", "Vestido", "Casaco", "Tênis", "Acessório", "Saia", "Shorts", "Blusa"]
    opt_ocasiao = ["Casual", "Trabalho", "Festa", "Esporte", "Formal"]
    opt_estacao = ["Todas", "Verão", "Inverno", "Meia-Estação"]
    opt_estilo = ["Básico", "Vintage", "Streetwear", "Elegante", "Esportivo"]

    def get_index(lista, valor):
        try: return lista.index(valor)
        except: return 0

    with col1:
        cat = st.selectbox("Categoria", opt_cats, index=get_index(opt_cats, item.get('categoria')))
        cor = st.text_input("Cor", value=item.get('cor', ''))
        marca = st.text_input("Marca", value=item.get('marca', ''))
        tecido = st.text_input("Tecido", value=item.get('tecido', ''))

    with col2:
        ocasiao = st.selectbox("Ocasião", opt_ocasiao, index=get_index(opt_ocasiao, item.get('ocasiao')))
        estacao = st.selectbox("Estação", opt_estacao, index=get_index(opt_estacao, item.get('estacao')))
        estilo = st.selectbox("Estilo", opt_estilo, index=get_index(opt_estilo, item.get('estilo')))

    if st.button("Salvar Alterações", type="primary"):
        with st.spinner("Atualizando..."):
            dados = {
                "nome": nome, "categoria": cat, "cor": cor, "marca": marca,
                "ocasiao": ocasiao, "estacao": estacao, "tecido": tecido, "estilo": estilo
            }
            
            # se trocou a foto
            if nova_foto:
                url = upload_imagem(nova_foto, item['user_id'])
                if url:
                    dados['imagem_url'] = url
            
            atualizar_roupa(item['id'], dados)
            st.success("Peça atualizada!")
            sleep(0.5)
            st.rerun()

# modal de exclusão (NOVO)
@st.dialog("Confirmar Exclusão")
def modal_excluir(id_roupa, nome_peca):
    st.warning(f"Tem certeza que deseja excluir **{nome_peca}**?")
    st.caption("Esta ação não pode ser desfeita.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("Sim, Excluir", type="primary", use_container_width=True):
            excluir_roupa(id_roupa)
            st.success("Item excluído.")
            sleep(0.5)
            st.rerun()

# cadastro de peça
def render_aba_cadastro(user_id):
    st.subheader("Nova Peça")
    
    uploaded_file = st.file_uploader("Foto da Roupa (Uma IA preencherá os dados automaticamente)", type=['jpg', 'png', 'jpeg'])
    
    if 'form' not in st.session_state:
        st.session_state.form = {
            "nome": "", "cat": "", "cor": "", "marca": "", 
            "ocasiao": "", "estacao": "Todas", "tecido": "", "estilo": ""
        }

    # Botão IA
    if uploaded_file and st.button("Preencher dados com IA"):
        with st.spinner("Analisando (Gemini)..."):
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
                st.success("Dados identificados!")
            else:
                st.warning("IA não conseguiu identificar todos os campos.\nPreencha manualmente.")

    # form
    with st.container(border=True):
        nome = st.text_input("Nome da Peça", value=st.session_state.form['nome'])
        
        col1, col2 = st.columns(2)
        
        # opçoes de selectbox
        opt_cats = ["Camiseta", "Calça", "Vestido", "Casaco", "Tênis", "Acessório", "Saia", "Shorts", "Blusa"]
        opt_ocasiao = ["Casual", "Trabalho", "Festa", "Esporte", "Formal"]
        opt_estacao = ["Todas", "Verão", "Inverno", "Meia-Estação"]
        opt_estilo = ["Básico", "Vintage", "Streetwear", "Elegante", "Esportivo"]
        
        # Função auxiliar para evitar erro se a IA trouxer algo fora da lista
        def get_index(lista, valor):
            try: return lista.index(valor)
            except: return 0

        with col1:
            cat = st.selectbox("Categoria", opt_cats, index=get_index(opt_cats, st.session_state.form['cat']))
            cor = st.text_input("Cor", value=st.session_state.form['cor'])
            marca = st.text_input("Marca", value=st.session_state.form['marca'])
            tecido = st.text_input("Tecido", value=st.session_state.form['tecido'])

        with col2:
            ocasiao = st.selectbox("Ocasião", opt_ocasiao, index=get_index(opt_ocasiao, st.session_state.form['ocasiao']))
            estacao = st.selectbox("Estação", opt_estacao, index=get_index(opt_estacao, st.session_state.form['estacao']))
            estilo = st.selectbox("Estilo", opt_estilo, index=get_index(opt_estilo, st.session_state.form['estilo']))

    if st.button("Salvar no Guarda-Roupa", type="primary"):
        if nome:
            with st.spinner("Salvando..."):
                url_img = None
                if uploaded_file:
                    url_img = upload_imagem(uploaded_file, user_id)
                    if url_img is None:
                        st.warning("A imagem não pôde ser salva, mas os dados serão.")
                
                dados = {
                    "nome": nome, "categoria": cat, "cor": cor, "marca": marca,
                    "ocasiao": ocasiao, "estacao": estacao, "tecido": tecido, "estilo": estilo,
                    "user_id": user_id, "imagem_url": url_img
                }
                
                try:
                    salvar_roupa(dados)
                    st.success("Peça salva!")
                    # Reset
                    st.session_state.form = {
                        "nome": "", "cat": "Camiseta", "cor": "", "marca": "", 
                        "ocasiao": "Casual", "estacao": "Todas", "tecido": "Algodão", "estilo": "Básico"
                    }
                    sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {e}")
        else:
            st.error("O nome da peça é obrigatório.")

# acervo
def render_aba_acervo():
    st.subheader("Meu Acervo")
    
    resp = buscar_roupas_usuario()
    roupas = resp.data
    
    if not roupas:
        st.info("Nenhuma roupa cadastrada.")
        return

    # filtros
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        pesquisa = st.text_input("Pesquisar", placeholder="Nome, marca ou cor...")
    with col_f2:
        filtro_status = st.selectbox("Status", ["Todos", "Disponível", "Emprestado"])

    # lógica de filtro
    if pesquisa:
        roupas = [r for r in roupas if pesquisa.lower() in (r['nome']+r['cor']+r['marca']).lower()]
    if filtro_status != "Todos":
        roupas = [r for r in roupas if r['status'] == filtro_status]

    # organização por categoria
    categorias_existentes = list(set([r['categoria'] for r in roupas]))
    categorias_existentes.sort()

    for categoria in categorias_existentes:
        itens = [r for r in roupas if r['categoria'] == categoria]
        if not itens: continue

        st.markdown(f"### {categoria}")
        
        cols = st.columns(4)
        
        for index, item in enumerate(itens):
            with cols[index % 4]:
                with st.container(border=True):
                    # foto
                    if item.get('imagem_url'):
                        st.image(item['imagem_url'], use_container_width=True)
                    else:
                        st.markdown("<div style='height:120px; background:#f5f5f5; color:#999; display:flex; align-items:center; justify-content:center; border-radius:5px;'>Sem Imagem</div>", unsafe_allow_html=True)
                    
                    # detalhes
                    st.markdown(f"**{item['nome']}**")
                    st.caption(f"{item['marca']} • {item['cor']}")
                    
                    # status
                    if item['status'] == 'Disponível':
                        st.markdown(":green[Disponível]")
                    else:
                        st.markdown(f":red[Emprestado]")
                        st.caption(f"Para: {item.get('emprestado_para')}")

                    with st.popover("Ações", use_container_width=True):
                        
                        # Emprestar / Devolver
                        if item['status'] == 'Disponível':
                            if st.button("Emprestar", key=f"emp_{item['id']}", use_container_width=True):
                                modal_emprestimo(item['id'], item['nome'])
                        else:
                            if st.button("Receber Devolução", key=f"dev_{item['id']}", type="primary", use_container_width=True):
                                registrar_devolucao(item['id'])
                                st.rerun()

                        # Editar
                        if st.button("Editar", key=f"edt_{item['id']}", use_container_width=True):
                            modal_editar(item)

                        # Excluir (com confirmação segura)
                        st.divider()
                        if st.button("Excluir", key=f"exc_{item['id']}", type="primary", use_container_width=True):
                            modal_excluir(item['id'], item['nome'])