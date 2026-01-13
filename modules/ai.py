import streamlit as st
from google import genai
from PIL import Image

def analisar_imagem(image_file):
    """
    Retorna lista na ordem: 
    [Categoria, Cor, Marca, Nome, Ocasiao, Estacao, Tecido, Estilo]
    """
    try:
        client = genai.Client(api_key=st.secrets["gemini"]["api_key"])
        
        gemini_model = "gemini-flash-latest"
        
        img = Image.open(image_file)
        
        prompt = """
        Você é um especialista em catalogação de moda. Analise esta imagem.
        Extraia os dados técnicos e responda APENAS com os valores separados por vírgula, na ordem exata abaixo.
        Se não souber, chute o mais provável baseada na imagem.
        
        1. Categoria (Ex: Camiseta, Calça, Vestido, Casaco, Tênis, Acessório, Saia, Shorts, Blusa)
        2. Cor Principal (Ex: Preto, Azul Marinho, Bege, Estampado)
        3. Marca (Se visível, senão 'Genérica')
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
            # Precisamos de pelo menos 8 campos agora
            if len(partes) >= 8:
                return [p.strip() for p in partes]
            else:
                st.warning(f"IA retornou menos dados que o necessário: {len(partes)} campos encontrados.")
                return None
        else:
            st.error("IA retornou resposta vazia.")
            return None
            
    except Exception as e:
        st.error(f"Erro na comunicação com a IA: {str(e)}")
        return None