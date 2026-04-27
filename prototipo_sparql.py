import streamlit as st
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd




import os
from google import genai



model_id ='gemini-2.5-flash'
# Configura a variável de ambiente APENAS para esta sessão do Jupyter
os.environ["GEMINI_API_KEY"] = SUA_CHAVE

GEMINI_API_KEY = SUA_CHAVE

# Configura o cliente da API.
# Assume que GEMINI_API_KEY está definida nas variáveis de ambiente.
try:
    client = genai.Client()
except Exception as e:
    print(f"Erro ao inicializar o cliente: {e}")
    print("Certifique-se de que a variável de ambiente GEMINI_API_KEY esteja configurada.")
    exit()




import json
from typing import Dict, List, Tuple

file_ontology = open("json/ontologia.json", "r")
ontology = file_ontology.read()

file_common_queries = open("json/consultas.json", "r")
examples = file_common_queries.read()

file_autores = open("json/qid_autores.json", "r")
autores = file_autores.read()

file_artigos = open("json/qid_tipos_publicacao.json", "r")
artigos = file_artigos.read()



def create_gemini_prompt(user_input: str) -> str:
    """
    Cria a instrução de sistema e a consulta do usuário para o LLM.
    """
    # 1. Instrução do Sistema (Contexto e Regras)

    SYSTEM_PROMPT_DYNAMIC_SPARQL = f"""
    **FORMATO DE RESPOSTA OBRIGATÓRIO:**
        ```json
        {{
          "reasoning": "Sua análise aqui",
          "SPARQL": "SELECT ... FROM ... WHERE ..."
        }}
        ```

    **ATENÇÃO: VOCÊ DEVE RETORNAR EXATAMENTE ESSE FORMATO JSON COM AS CHAVES "reasoning" E "SPARQL"**
    **NÃO RETORNE: {{"query": "..."}}, {{"description": "..."}}, ou {{"result": "..."}}**
    **APENAS: {{"reasoning": "...", "sql": "..."}} - NADA MAIS!**

    Você é um Engenheiro de Dados Sênior especializado em Wikidata e SPARQL.
    Sua tarefa é converter uma solicitação em SPARQL executável. Use ESTRITAMENTE os contextos fornecidos.

    **PRIORIDADE CRÍTICA**: Use os EXEMPLOS DE REFERÊNCIA como base principal para gerar SPARQL. 
    Adapte os padrões existentes em vez de criar consultas do zero sempre que possível. 
    Se um exemplo for 80% similar à consulta atual, modifique-o ao invés de criar SPARQL completamente novo.
   

    ## 1. MAPEAMENTO DE AUTORES e QID (Onde encontrar os autores):
    <qid_autores>
    {autores}
    </qid_autores>

    ## 2. MAPEAMENTO DE Publicações e QID (Onde encontrar o tipo de publicação):
    <db_schema>
    {artigos}
    </db_schema>

    ## 3. EXEMPLOS DE REFERÊNCIA (PRIORIZE ESTES PADRÕES):
    <examples>
    {examples}
    </examples>

    ## 4. Estruturas e Relacionamentos do dominio:
    <ontology>
    {ontology}
    </ontology>
   
    ## SOLICITAÇÃO DO USUÁRIO:
    "{user_input}"

    ## INSTRUÇÕES CRÍTICAS - LEIA COM ATENÇÃO:

    **ERROS COMUNS (O QUE NÃO FAZER):**
    - NÃO retorne {{"query": "..."}}, {{"description": "..."}}, ou {{"result": "..."}}
    - NÃO retorne explicações em markdown ou tabelas HTML
    - NÃO invente dados ou estruturas inexistentes
    - RETORNE APENAS JSON com EXATAMENTE 2 chaves: "reasoning" e "sparql"
    - Se a consulta for impossível, retorne: {{"reasoning": "Consulta impossível: [motivo]", "sparql": "-- Erro: [motivo]"}}

    **FLUXO CORRETO (O QUE FAZER):**
    1. Gere SPARQL válido para Wikidata.
    2. Retorne EXATAMENTE: {{"reasoning": "...", "sparql": "..."}}"""
    
    
    return SYSTEM_PROMPT_DYNAMIC_SPARQL


from typing import Dict, Any, Optional
import requests
import json
import logging
from abc import ABC, abstractmethod


def generate(system_prompt: str, user_prompt: str, temperature: float = 0.0, force_json: bool = False) -> Dict[str, Any]:
        
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY não configurada! Falha ao chamar Gemini.")
        return {}

    # URL para o modelo Gemini 2.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        
    payload = {
            "contents": [{
                "parts": [{"text": user_prompt}]
            }],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": temperature
            }
    }

    try:
            print("Enviando request para Gemini API")
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "candidates" in data and len(data["candidates"]) > 0:
                text_content = data['candidates'][0]['content']['parts'][0]['text']
                return json.loads(text_content)
            else:
                print(f"Gemini retornou resposta vazia ou bloqueada por segurança: {data}")
                return {}
    except Exception as e:
            print(f"Erro na API Gemini: {e}")
    return {}


def normalizar_para_string(dado):
    if isinstance(dado, bytes):
        # Se for bytes, decodifica para string usando UTF-8
        return dado.decode('utf-8')
    elif isinstance(dado, str):
        # Se já for string (unicode), retorna como está
        return dado
    else:
        # Opcional: tentar converter outros tipos (ex: números) para string
        return str(dado)


st.image("imagem.png")
st.title("Consulta acadêmica no Wikidata")

# Input for query
author_name = st.text_input("**Ingresse sua consulta**", "")

if st.button("Consultar"):
    # 1. Set up SPARQL endpoint (Scholarly)
    sparql = SPARQLWrapper("https://query-scholarly.wikidata.org/sparql")

    # 2. Define query (Example: Find papers by author)
    #query = """SELECT ?Artigo ?ArtigoLabel WHERE {
    #            ?Artigo wdt:P50 wd:Q17489997.
    #            SERVICE wikibase:label { bd:serviceParam wikibase:language '[AUTO_LANGUAGE],en'. }
    #        }
    #        """
    query = author_name


    prompt_gerado = create_gemini_prompt(query)
    rpta_gerado = generate(prompt_gerado, query)
    print(rpta_gerado)
    print("\n" + "#"*70 + "\n")

    sparql_consulta = normalizar_para_string(rpta_gerado['SPARQL'])
    
    print(sparql_consulta)
            
    sparql.setQuery(sparql_consulta)
    sparql.setReturnFormat(JSON)

    # 3. Execute query and parse results
    results = sparql.query().convert()
    results_df = pd.json_normalize(results['results']['bindings'])
    #print(results_df.columns)
    
    # 4. Display in Streamlit
    if not results_df.empty:
       # st.dataframe(results_df[['ArtigoLabel.value', 'Artigo.value']])
        st.dataframe(results_df.filter(like='.value'))
    else:
        st.write("No results found.")
