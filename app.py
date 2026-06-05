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
            # 1. MODO DETETIVE: Descobrir os modelos permitidos
            st.info("🔍 A verificar os acessos da sua chave no Google...")
            url_models = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            resp_models = requests.get(url_models)
            
            if resp_models.status_code != 200:
                st.error("Erro ao validar a chave da API. Verifique se não há espaços em branco.")
                st.stop()
                
            modelos_disponiveis = [m['name'] for m in resp_models.json().get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
            
            if not modelos_disponiveis:
                st.error("A sua chave não tem permissão para usar nenhum modelo de texto do Gemini.")
                st.stop()

            modelo_escolhido = modelos_disponiveis[0]
            preferencias = ['models/gemini-2.5-flash', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
            
            for pref in preferencias:
                if pref in modelos_disponiveis:
                    modelo_escolhido = pref
                    break
                    
            st.success(f"✅ Permissão garantida! O Google autorizou o uso do modelo: {modelo_escolhido}")

            # 2. LIMPEZA DO TRELLO (O Segredo para não estourar a quota grátis!)
            file_contents_raw = uploaded_file.read().decode("utf-8")
            
            try:
                trello_data = json.loads(file_contents_raw)
                # Remover o histórico de ações e plugins que não interessam e ocupam 90% do ficheiro
                if 'actions' in trello_data:
                    del trello_data['actions']
                if 'pluginData' in trello_data:
                    del trello_data['pluginData']
                # Converter de volta para texto (agora muito mais leve!)
                file_contents = json.dumps(trello_data)
            except:
                file_contents = file_contents_raw # Se falhar, tenta com o ficheiro original

            # Instrução (Prompt)
            prompt = f"""
            Atuas como o assistente de operações da agência Soul Branding. 
            Com base no conhecimento sobre a estrutura de clientes, equipa (Mateus, Zilli, Taís, Henrique, Bruno, Vitória, Luan, Arthur) 
            e no ficheiro JSON do Trello de hoje fornecido abaixo, por favor gera com precisão:
            1. Calendário visual do mês atual com as demandas posicionadas pelo prazo.
            2. Roteiro atualizado de cada pessoa do time.
            3. Lista de alertas com cards vencidos, sem status ou sem responsável para a reunião.

            Aqui estão os dados limpos do Trello de hoje:
            {file_contents}
            """

            with st.spinner('A analisar os cards da agência e a gerar o relatório... (Isto pode demorar até 1 minuto)'):
                
                # Enviar para o Google
                modelo_url = modelo_escolhido.replace('models/', '')
                url_gen = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_url}:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                
                response = requests.post(url_gen, headers=headers, json=data)
                response_json = response.json()
                
                # Mostrar o resultado
                if response.status_code == 200:
                    resposta_texto = response_json['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("### 📋 O Seu Relatório está Pronto:")
                    st.markdown(resposta_texto)
                else:
                    erro_msg = response_json.get('error', {}).get('message', 'Erro desconhecido')
                    st.error(f"Erro de Quota ou Limite no Google: {erro_msg}")
                
        except Exception as e:
            st.error(f"Ocorreu um erro interno no site: {e}")
    else:
        st.warning("Por favor, faça primeiro o upload do ficheiro JSON.")
