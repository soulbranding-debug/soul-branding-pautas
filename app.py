import streamlit as st
import requests
import json
from datetime import datetime

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
            
            for pref in ['models/gemini-2.5-flash', 'models/gemini-1.5-flash', 'models/gemini-1.5-pro']:
                if pref in modelos_disponiveis:
                    modelo_escolhido = pref
                    break
                    
            st.success(f"✅ Conectado ao Google! Modelo: {modelo_escolhido}")

            # 2. LIMPEZA EXTREMA E FILTRO DE COLUNAS
            file_contents_raw = uploaded_file.read().decode("utf-8")
            
            try:
                trello_data = json.loads(file_contents_raw)
                
                # Filtrar as listas: IGNORAR Backlog e Concluídos
                listas_validas = {}
                for l in trello_data.get("lists", []):
                    nome_lista = l.get("name", "").lower()
                    if not l.get("closed", False) and "backlog" not in nome_lista and "concluído" not in nome_lista and "concluido" not in nome_lista:
                        listas_validas[l["id"]] = l["name"]

                membros = {m["id"]: m.get("fullName", "Desconhecido") for m in trello_data.get("members", [])}
                
                cards = []
                for c in trello_data.get("cards", []):
                    if not c.get("closed", False) and c.get("idList") in listas_validas:
                        nomes_responsaveis = [membros.get(m_id, "Desconhecido") for m_id in c.get("idMembers", [])]
                        
                        cards.append({
                            "nome_card": c.get("name"),
                            "prazo": c.get("due"),
                            "coluna_atual": listas_validas[c.get("idList")],
                            "responsaveis": nomes_responsaveis,
                            "etiquetas": [lbl.get("name") for lbl in c.get("labels", []) if lbl.get("name")]
                        })
                        
                trello_resumido = {
                    "cards_em_andamento": cards
                }
                file_contents = json.dumps(trello_resumido, ensure_ascii=False)
                
            except Exception as e:
                st.warning("Não foi possível filtrar o JSON perfeitamente, a tentar com o ficheiro original...")
                file_contents = file_contents_raw

            # 3. PEDIDO À INTELIGÊNCIA ARTIFICIAL COM REGRA ESTRITA DE ALERTAS
            data_hoje = datetime.now().strftime("%d/%m/%Y")
            
            prompt = f"""
            Hoje é dia {data_hoje}. Atuas como o assistente de operações da agência Soul Branding. 
            Com base no conhecimento do manual da agência (equipa, reuniões, responsabilidades por cliente, fluxo do Trello) 
            e nos dados extraídos dos cards do Trello fornecidos abaixo, por favor gera com precisão:

            1. Calendário visual para o mês atual ({data_hoje}): 
               - Posiciona as demandas em aberto pelo prazo de entrega.
               - Inclui os lembretes das recorrências mensais de cada pessoa do time.
            2. Roteiro atualizado da equipa: 
               - Agrupa por pessoa (Mateus, Zilli, Taís, Henrique, Bruno, Vitória, Luan, Arthur).
               - O que eles têm a fazer hoje e nos próximos dias com base nos prazos.
            3. Lista de alertas para a reunião de pauta: 
               - REGRA ESTRITA: Analisar EXCLUSIVAMENTE os cards que estão nas colunas individuais de cada pessoa do time OU na coluna de "Revisão". Não incluir alertas de outras colunas.
               - Destacar cards com prazo vencido nestas colunas (comparando com {data_hoje}).
               - Destacar cards que estão sem status, sem responsável ou travados nestas colunas específicas.

            Aqui estão os DADOS RESUMIDOS E FILTRADOS do Trello:
            {file_contents}
            """

            with st.spinner('A estruturar o calendário e roteiros do time...'):
                
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
