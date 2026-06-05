import streamlit as st
import requests
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
                
                # CONEXÃO DIRETA À PROVA DE ERROS (Bypass da biblioteca)
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                
                # Enviar para o Google
                response = requests.post(url, headers=headers, json=data)
                response_json = response.json()
                
                # Mostrar o resultado
                if response.status_code == 200:
                    resposta_texto = response_json['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("### 📋 O Seu Relatório está Pronto:")
                    st.markdown(resposta_texto)
                else:
                    erro_msg = response_json.get('error', {}).get('message', 'Erro desconhecido')
                    st.error(f"Erro no servidor do Google: {erro_msg}")
                
        except Exception as e:
            st.error(f"Ocorreu um erro no site: {e}")
    else:
        st.warning("Por favor, faça primeiro o upload do ficheiro JSON.")
