import streamlit as st
from google import genai
from PIL import Image
import json

gemini_model = "gemini-flash-latest"

def get_client():
    return genai.Client(api_key=st.secrets["gemini"]["api_key"])

# retorna lista na ordem: categoria, cor, marca, nome curto, ocasiao, estacao, tecido, estilo
def analisar_imagem(image_file):
    try:
        client = get_client()
        
        
        img = Image.open(image_file)
        
        prompt = """
        Você é um especialista em catalogação de moda. Analise esta imagem.
        Extraia os dados técnicos e responda APENAS com os valores separados por vírgula, na ordem exata abaixo.
        Se não souber, chute o mais provável baseada na imagem.
        
        1. Categoria (Ex: Camiseta, Calça, Vestido, Casaco, Tênis, Acessório, Saia, Shorts, Blusa)
        2. Cor Principal (Ex: Preto, Azul Marinho, Bege, Estampado)
        3. Marca (Se visível, senão 'Desconhecida')
        4. Nome Curto Sugerido (Ex: Camiseta Preta Básica)
        5. Ocasião (Escolha uma: Casual, Trabalho, Festa, Esporte, Formal)
        6. Estação Ideal (Escolha uma: Verão, Inverno, Meia-Estação, Todas)
        7. Tecido/Material (Ex: Algodão, Jeans, Couro, Poliéster, Lã, Sintético)
        8. Estilo (Ex: Básico, Vintage, Streetwear, Elegante, Esportivo)

        Exemplo de resposta:
        Tênis, Branco, Nike, Tênis Air Force, Casual, Todas, Couro, Streetwear
        """
        
        response = client.models.generate_content(
            model=gemini_model,
            contents=[img, prompt]
        )
        
        if response.text:
            partes = response.text.split(',')
            if len(partes) >= 8:
                return [p.strip() for p in partes]
            else:
                st.warning(f"A IA retornou menos dados que o necessário: {len(partes)} campos encontrados.\nTente novamente.")
                return None
        else:
            st.error("IA retornou resposta vazia.\nTente novamente.")
            return None
            
    except Exception as e:
        st.error(f"Erro na comunicação com a IA: {str(e)}.\nTente novamente.")
        return None

# NOVA FUNÇÃO: Gera sugestões de looks baseados nas roupas do usuário
def sugerir_looks(lista_roupas, ocasiao_escolhida):
    try:
        client = get_client()

        # Prepara o inventário para a IA ler (ID é crucial para recuperarmos a foto depois)
        texto_inventario = ""
        for item in lista_roupas:
            texto_inventario += f"- ID: {item['id']} | Nome: {item['nome']} | Categoria: {item['categoria']} | Cor: {item['cor']} | Estilo: {item.get('estilo', '')}\n"
            
        prompt = f"""
        Você é um Personal Stylist. Analise o inventário abaixo e crie 3 sugestões de looks para a ocasião: "{ocasiao_escolhida}".
        
        INVENTÁRIO:
        {texto_inventario}
        
        REGRAS:
        1. Use apenas os IDs listados.
        2. Combine peças superiores, inferiores e calçados/acessórios de forma harmônica.
        3. Responda ESTRITAMENTE um JSON puro, sem crases ```json, no seguinte formato:
        
        [
            {{
                "nome_look": "Nome Criativo",
                "ids_pecas": [1, 5, 9],
                "explicacao": "Por que funciona..."
            }},
            ...
        ]
        """
        
        response = client.models.generate_content(
            model=gemini_model,
            contents=prompt
        )
        
        # Limpeza básica caso a IA mande markdown
        texto_limpo = response.text.replace("```json", "").replace("```", "").strip()
        
        return json.loads(texto_limpo)
        
    except Exception as e:
        st.error(f"Erro ao gerar looks: {e}")
        return []