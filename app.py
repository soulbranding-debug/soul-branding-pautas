import streamlit as st
import google.generativeai as genai
import json

# Configuração visual do site
st.set_page_config(page_title="Soul Branding - Gerador de Pautas", page_icon="⚡")

st.title("⚡ Soul Branding - Gerador de Pautas e Roteiros")
st.write("Faça o upload do ficheiro JSON diário do Trello para gerar o calendário, roteiros e alertas automáticos.")

# Caixa para colocar a Chave da API
api_key = st.text_input("Insira a sua Chave de API do Google Gemini:", type="password")

# Botão de upload do ficheiro
uploaded_file = st.file_uploader("Escolha o ficheiro JSON do Trello (.json)", type="json")

if st.button("Gerar Relatório da Soul Branding"):
    if not api_key:
        st.warning("Por favor, insira a chave da API do Gemini acima.")
    elif uploaded_file is not None:
        try:
            # Configurar a Inteligência Artificial
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash-latest')
            # Ler o ficheiro do Trello
            file_contents = uploaded_file.read().decode("utf-8")

            # Instrução (Prompt) que será enviada à IA
            prompt = f"""
            Atuas como o assistente de operações da agência Soul Branding. 
            Com base no conhecimento sobre a estrutura de clientes, equipa (Mateus, Zilli, Taís, Henrique, Bruno, Vitória, Luan, Arthur) 
            e no ficheiro JSON do Trello de hoje fornecido abaixo, por favor gera com precisão:
            1. Calendário visual do mês atual com as demandas posicionadas pelo prazo.
            2. Roteiro atualizado de cada pessoa do time.
            3. Lista de alertas com cards vencidos, sem status ou sem responsável para a reunião.

            Aqui estão os dados do Trello de hoje:
            {file_contents}
            """

            with st.spinner('A analisar milhares de cards e a gerar o relatório... (Isto pode demorar cerca de 20 a 40 segundos)'):
                response = model.generate_content(prompt)
                st.markdown("### 📋 O Seu Relatório está Pronto:")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar: {e}")
    else:
        st.warning("Por favor, faça primeiro o upload do ficheiro JSON.")
