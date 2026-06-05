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
            # 1. VALIDAR A CHAVE E O MODELO
            st.info("🔍 A verificar acessos...")
            url_models = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            resp_models = requests.get(url_models)
            
            if resp_models.status_code != 200:
                st.error("Erro ao validar a chave da API. Verifique se a copiou corretamente.")
                st.stop()
                
            modelos_disponiveis = [m['name'] for m in resp_models.json().get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
            modelo_escolhido = modelos_disponiveis[0]
            
            # Tenta pegar o melhor modelo disponível
            for pref in ['models/gemini-2.5-flash', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro']:
                if pref in modelos_disponiveis:
                    modelo_escolhido = pref
                    break
                    
            st.success(f"✅ Conectado ao Google! Modelo: {modelo_escolhido}")

            # 2. LIMPEZA EXTREMA DO TRELLO (Reduz o ficheiro em 99%)
            file_contents_raw = uploaded_file.read().decode("utf-8")
            
            try:
                trello_data = json.loads(file_contents_raw)
                
                # Extrair apenas o que é essencial para a Pauta
                listas = [{"id": l["id"], "nome": l["name"]} for l in trello_data.get("lists", []) if not l.get("closed", False)]
                membros = [{"id": m["id"], "nome": m.get("fullName", "Desconhecido")} for m in trello_data.get("members", [])]
                
                cards = []
                for c in trello_data.get("cards", []):
                    if not c.get("closed", False):
                        cards.append({
                            "nome_card": c.get("name"),
                            "prazo": c.get("due"),
                            "id_lista": c.get("idList"),
                            "id_responsaveis": c.get("idMembers"),
                            "etiquetas": [lbl.get("name") for lbl in c.get("labels", []) if lbl.get("name")]
                        })
                        
                # Monta um novo ficheiro minúsculo
                trello_resumido = {
                    "listas_do_quadro": listas,
                    "membros_da_equipa": membros,
                    "cards_ativos": cards
                }
                file_contents = json.dumps(trello_resumido, ensure_ascii=False)
                
            except Exception as e:
                st.warning("Não foi possível fazer a limpeza extrema, a tentar enviar o ficheiro original...")
                file_contents = file_contents_raw

            # 3. PEDIDO À INTELIGÊNCIA ARTIFICIAL
            prompt = f"""
            Atuas como o assistente de operações da agência Soul Branding. 
            Com base no conhecimento sobre a estrutura de clientes, equipa (Mateus, Zilli, Taís, Henrique, Bruno, Vitória, Luan, Arthur) 
            e nos dados extraídos do Trello de hoje fornecido abaixo, por favor gera com precisão:
            1. Calendário visual do mês atual com as demandas posicionadas pelo prazo.
            2. Roteiro atualizado de cada pessoa do time.
            3. Lista de alertas com cards vencidos, sem status ou sem responsável para a reunião.

            Aqui estão os DADOS RESUMIDOS do Trello de hoje:
            {file_contents}
            """

            with st.spinner('A processar e formatar o seu relatório da Soul Branding...'):
                
                modelo_url = modelo_escolhido.replace('models/', '')
                url_gen = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_url}:generateContent?key={api_key}"
                headers = {'Content-Type': 'application/json'}
                data = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                
                response = requests.post(url_gen, headers=headers, json=data)
                response_json = response.json()
                
                # 4. MOSTRAR RESULTADO
                if response.status_code == 200:
                    resposta_texto = response_json['candidates'][0]['content']['parts'][0]['text']
                    st.markdown("### 📋 O Seu Relatório está Pronto:")
                    st.markdown(resposta_texto)
                else:
                    erro_msg = response_json.get('error', {}).get('message', 'Erro desconhecido')
                    st.error(f"Erro do Google: {erro_msg}")
                
        except Exception as e:
            st.error(f"Ocorreu um erro no site: {e}")
    else:
        st.warning("Por favor, anexe o ficheiro JSON do Trello antes de gerar.")
