# api/main.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import os
import json
from collections import Counter
from itertools import combinations
import math
import pandas as pd
import re
import logging
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore
import requests # Para buscar do Blob

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.INFO)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- INICIALIZAÇÃO DO FIREBASE ADMIN ---
FB_ADMIN_INITIALIZED = False
db_admin = None
try:
    SERVICE_ACCOUNT_KEY_PATH_MAIN = os.path.join(APP_ROOT, "serviceAccountKey.json")
    # Tenta primeiro carregar do arquivo local (útil para desenvolvimento se o arquivo estiver presente)
    if os.path.exists(SERVICE_ACCOUNT_KEY_PATH_MAIN) and not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH_MAIN)
        firebase_admin.initialize_app(cred, name='lotoGeniusApiAppFile')
        app.logger.info("Firebase Admin SDK inicializado para main.py via arquivo local.")
        FB_ADMIN_INITIALIZED = True
    # Senão, tenta carregar de variáveis de ambiente (prioridade para Vercel)
    elif os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON') and not firebase_admin._apps:
        service_account_json_str = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        service_account_info = json.loads(service_account_json_str)
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred, name='lotoGeniusApiAppEnv')
        app.logger.info("Firebase Admin SDK inicializado para main.py via variável de ambiente.")
        FB_ADMIN_INITIALIZED = True
    
    if FB_ADMIN_INITIALIZED: # Se alguma inicialização teve sucesso
         # Garante que estamos pegando a instância correta do app Firebase inicializado
        app_name_to_use = list(firebase_admin._apps.keys())[0]
        db_admin = admin_firestore.client(app=firebase_admin.get_app(name=app_name_to_use))
    else:
        app.logger.warning("Credenciais do Firebase Admin não encontradas (nem arquivo, nem ENV VAR). Funcionalidades dependentes do Firestore Admin não funcionarão.")

except Exception as e_fb_admin_main:
    app.logger.error(f"Erro GERAL ao inicializar Firebase Admin SDK em main.py: {e_fb_admin_main}")


LOTTERY_CONFIG = {
    "megasena": {"nome_exibicao": "Mega-Sena", "min": 1, "max": 60, "count": 6, "count_apostadas": 6, "color": "#209869", "processed_json_name": "megasena_processed_results.json", "count_sorteadas": 6},
    "lotofacil": {"nome_exibicao": "Lotofácil", "min": 1, "max": 25, "count": 15, "count_apostadas": 15, "color": "#930089", "processed_json_name": "lotofacil_processed_results.json", "count_sorteadas": 15},
    "lotomania": {"nome_exibicao": "Lotomania", "min": 0, "max": 99, "count_apostadas": 50, "count_sorteadas": 20, "color": "#f78100", "processed_json_name": "lotomania_processed_results.json"},
    "quina": {"nome_exibicao": "Quina", "min": 1, "max": 80, "count": 5, "count_apostadas": 5, "color": "#260085", "processed_json_name": "quina_processed_results.json", "count_sorteadas": 5}
}

platform_stats_data = {
    "jogos_gerados_total": random.randint(20000, 33000),
    "jogos_premiados_estimativa": random.randint(300, 800),
    "valor_premios_estimativa_bruto": random.uniform(100000, 380000)
}

def format_currency(value):
    if isinstance(value, (int, float)): return f"R$ {value:_.2f}".replace('.', ',').replace('_', '.')
    return "R$ 0,00"

def parse_currency_to_float(currency_str):
    if pd.isna(currency_str): return 0.0
    if not isinstance(currency_str, str): currency_str = str(currency_str)
    cleaned_str = currency_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
    if not cleaned_str or cleaned_str == '-': return 0.0
    try: return float(cleaned_str)
    except ValueError: app.logger.warning(f"Não foi possível converter '{currency_str}' para float."); return 0.0

def load_processed_lottery_data(lottery_key):
    global FB_ADMIN_INITIALIZED, db_admin
    
    if not FB_ADMIN_INITIALIZED or not db_admin:
        app.logger.error(f"Firebase Admin não inicializado. Não é possível buscar URL do Blob para {lottery_key}.")
        return None

    app.logger.info(f"Buscando URL do Blob no Firestore para {lottery_key.upper()}...")
    try:
        doc_ref = db_admin.collection('lottery_data_source_urls').document(lottery_key)
        doc = doc_ref.get()
        
        if not doc.exists:
            app.logger.error(f"URL do Blob não encontrado no Firestore para {lottery_key}.")
            return None
        
        data_source_info = doc.to_dict()
        blob_url = data_source_info.get('blob_url') # Este é o URL completo com hash
        
        if not blob_url:
            app.logger.error(f"Campo 'blob_url' não encontrado no documento do Firestore para {lottery_key}.")
            return None

        app.logger.info(f"Carregando dados de {lottery_key.upper()} do Vercel Blob (via Firestore URL): {blob_url}")
        response = requests.get(blob_url, timeout=20) 
        response.raise_for_status()
        data = response.json()
        app.logger.info(f"Sucesso ao carregar {lottery_key.upper()} ({len(data)} registros) do Vercel Blob")
        return data
        
    except firebase_admin.exceptions.FirebaseError as fb_err:
        app.logger.error(f"Erro do Firebase ao buscar URL do Blob para {lottery_key}: {fb_err}")
    except requests.exceptions.HTTPError as http_err:
        app.logger.error(f"Erro HTTP ao buscar JSON do Vercel Blob {blob_url if 'blob_url' in locals() else 'URL_DESCONHECIDO'}: {http_err}. Status: {http_err.response.status_code if hasattr(http_err, 'response') and http_err.response is not None else 'N/A'}")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Erro de requisição ao buscar JSON do Vercel Blob {blob_url if 'blob_url' in locals() else 'URL_DESCONHECIDO'}: {e}")
    except json.JSONDecodeError as e_json:
        app.logger.error(f"Erro ao decodificar JSON de {blob_url if 'blob_url' in locals() else 'URL_DESCONHECIDO'}: {e_json}")
    except Exception as e_gen:
        app.logger.error(f"Erro genérico ao carregar dados de {blob_url if 'blob_url' in locals() else 'URL_DESCONHECIDO'}: {e_gen}")
    return None

# --- O resto do seu main.py continua aqui (endpoints de stats, geradores, verificação, etc.) ---
# Eles usarão a função load_processed_lottery_data atualizada.

# Exemplo de como get_data_for_stats usaria a nova função:
def get_data_for_stats(lottery_name_lower):
    if lottery_name_lower not in LOTTERY_CONFIG:
        return None, {"erro": f"Loteria '{lottery_name_lower}' não configurada."}, 404
    all_results = load_processed_lottery_data(lottery_name_lower)
    if not all_results:
        return None, {"erro": f"Dados de {lottery_name_lower.upper()} indisponíveis no momento (falha ao buscar do Blob)."}, 503
    return all_results, None, None

def combinations_count(n, k):
    if k < 0 or k > n: return 0
    if k == 0 or k == n: return 1
    if k > n // 2: k = n - k
    res = 1;
    for i in range(k): res = res * (n - i) // (i + 1)
    return res

@app.route('/')
def api_base_root():
    return jsonify({"message": "API Loto Genius Python (api/main.py).", "note": "Endpoints em /api/main/..." })

@app.route('/api/main/')
def api_main_home():
    return jsonify({"mensagem": "API Loto Genius AI Refatorada!", "versao": "4.3.6 - Blob Firestore URLs"})

@app.route('/api/main/platform-stats', methods=['GET'])
def get_platform_stats():
    platform_stats_data["jogos_gerados_total"] += random.randint(1, 7)
    if random.random() < 0.03:
        platform_stats_data["jogos_premiados_estimativa"] += random.randint(1,2)
        platform_stats_data["valor_premios_estimativa_bruto"] += random.uniform(1000, 15000)
    return jsonify({
        "jogos_gerados_total": platform_stats_data["jogos_gerados_total"],
        "jogos_premiados_estimativa": platform_stats_data["jogos_premiados_estimativa"],
        "valor_premios_estimativa_formatado": format_currency(platform_stats_data["valor_premios_estimativa_bruto"])
    })

@app.route('/api/main/recent-winning-pools', methods=['GET'])
def get_recent_winning_pools():
    pools = [{"name": "Bolão Astral da Fortuna", "lottery": "Mega-Sena", "prize": format_currency(random.uniform(200000, 700000)), "date": "25/12/2025"}, {"name": "Grupo Estrela Guia", "lottery": "Lotofácil", "prize": format_currency(random.uniform(7000, 20000)), "date": "10/11/2025"}]
    return jsonify(random.sample(pools, k=min(len(pools), random.randint(1,2))))

@app.route('/api/main/top-winners', methods=['GET'])
def get_top_winners():
    winners = [{"nick": "Vidente Premiado", "prize_total": format_currency(random.uniform(280000, 1300000))}, {"nick": "Numerólogo da Sorte", "prize_total": format_currency(random.uniform(190000, 800000))}]
    random.shuffle(winners)
    return jsonify(winners[:random.randint(1,len(winners))])

@app.route('/api/main/resultados/<lottery_name>', methods=['GET'])
def get_resultados_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results = load_processed_lottery_data(lottery_name_lower)
    if not all_results: return jsonify({"aviso": f"Dados para {lottery_name.upper()} indisponíveis no momento."}), 404
    latest_result = all_results[0]
    return jsonify({"ultimo_concurso": latest_result.get("concurso"),"data": latest_result.get("data"),"numeros": latest_result.get("numeros"),"ganhadores_principal_contagem": latest_result.get("ganhadores_principal_contagem"),"cidades_ganhadoras_principal": latest_result.get("cidades_ganhadoras_principal"),"rateio_principal_valor": latest_result.get("rateio_principal_valor"),"fonte": f"Dados Processados - {lottery_name.upper()} (Vercel Blob)"})

@app.route('/api/main/stats/frequencia/<lottery_name>', methods=['GET'])
def get_frequencia_numeros(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    todos_numeros = [num for sorteio in all_results if "numeros" in sorteio for num in sorteio["numeros"]]
    if not todos_numeros: return jsonify({"data": [], "mensagem": "Nenhum número nos dados."}), 200
    contagem = Counter(todos_numeros); frequencia_ordenada = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))
    frequencia_formatada = [{"numero": str(num).zfill(2), "frequencia": freq} for num, freq in frequencia_ordenada]
    return jsonify({"data": frequencia_formatada, "total_sorteios_analisados": len(all_results)})

@app.route('/api/main/stats/pares-frequentes/<lottery_name>', methods=['GET'])
def get_pares_frequentes(lottery_name):
    lottery_name_lower = lottery_name.lower(); config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": "Loteria não configurada."}), 404
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    numeros_por_sorteio = config.get("count_sorteadas", config.get("count"))
    todos_os_itens_combinacao = [tuple(par) for s in all_results if s.get("numeros") and len(s["numeros"]) == numeros_por_sorteio for par in combinations(sorted(s["numeros"]), 2)]
    if not todos_os_itens_combinacao: return jsonify({"data": [], "mensagem": "Não foi possível gerar pares."}), 200
    contagem_itens = Counter(todos_os_itens_combinacao); itens_ordenados = sorted(contagem_itens.items(), key=lambda item: (-item[1], item[0]))
    itens_formatados = [{"par": [str(n).zfill(2) for n in item_numeros], "frequencia": freq} for item_numeros, freq in itens_ordenados]
    return jsonify({"data": itens_formatados[:30]})

@app.route('/api/main/stats/cidades-premiadas/<lottery_name>', methods=['GET'])
def get_cidades_premiadas(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    contagem_cidades = Counter(); total_premios_contabilizados = 0
    for sorteio in all_results:
        cidades = sorteio.get("cidades_ganhadoras_principal", [])
        if isinstance(cidades, list):
            cidades_validas = [c for c in cidades if c and isinstance(c, str) and c.lower().strip() != "não especificada" and c.strip() != "-"]
            if cidades_validas:
                contagem_cidades.update(cidades_validas)
                total_premios_contabilizados += sorteio.get("ganhadores_principal_contagem", len(cidades_validas))
    cidades_ordenadas = sorted(contagem_cidades.items(), key=lambda item: (-item[1], item[0]))
    cidades_formatadas = [{"cidade_uf": cidade, "premios_principais": freq} for cidade, freq in cidades_ordenadas]
    return jsonify({"data": cidades_formatadas[:30], "total_premios_analisados": total_premios_contabilizados})

@app.route('/api/main/stats/maiores-premios-cidade/<lottery_name>', methods=['GET'])
def get_maiores_premios_cidade(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    soma_premios_cidade = Counter()
    for sorteio in all_results:
        cidades = sorteio.get("cidades_ganhadoras_principal", [])
        rateio_bruto = sorteio.get("rateio_principal_valor", 0.0)
        rateio = parse_currency_to_float(rateio_bruto) if isinstance(rateio_bruto, str) else float(rateio_bruto)
        num_ganhadores_no_sorteio = sorteio.get("ganhadores_principal_contagem", 0)
        if rateio > 0 and cidades and num_ganhadores_no_sorteio > 0:
            cidades_validas = [c for c in cidades if c and isinstance(c, str) and c.lower().strip() != "não especificada" and c.strip() != "-"]
            for cidade_unica in set(cidades_validas):
                ocorrencias_cidade_no_sorteio = cidades_validas.count(cidade_unica)
                soma_premios_cidade[cidade_unica] += rateio * ocorrencias_cidade_no_sorteio
    cidades_ordenadas = sorted(soma_premios_cidade.items(), key=lambda item: (-item[1], item[0]))
    cidades_formatadas = [{"cidade_uf": cid, "total_ganho_principal_formatado": format_currency(val), "total_ganho_principal_float": val} for cid, val in cidades_ordenadas]
    return jsonify({"data": cidades_formatadas[:30]})

@app.route('/api/main/jogo-manual/probabilidade', methods=['POST'])
def calcular_probabilidade_jogo():
    data = request.get_json();
    if not data or 'lottery_type' not in data or 'numeros_usuario' not in data: return jsonify({"erro": "Dados incompletos."}), 400
    lottery_type = data['lottery_type'].lower()
    numeros_usuario_str_list = data['numeros_usuario']
    if lottery_type not in LOTTERY_CONFIG: return jsonify({"erro": f"Loteria '{data['lottery_type']}' não configurada."}), 404
    config = LOTTERY_CONFIG[lottery_type]; nome_loteria = config.get('nome_exibicao', lottery_type.capitalize())
    universo_total = config['max'] - config['min'] + 1
    num_sorteados_premio_max = config.get('count_sorteadas', config.get('count'))
    num_marcados_volante_config = config.get('count_apostadas', config.get('count'))
    if not isinstance(numeros_usuario_str_list, list): return jsonify({"erro": "Formato 'numeros_usuario' inválido."}), 400
    numeros_usuario = []
    try:
        for n_str in numeros_usuario_str_list:
            num = int(n_str)
            if not (config['min'] <= num <= config['max']): return jsonify({"erro": f"Número {num} fora do range."}), 400
            numeros_usuario.append(num)
    except ValueError: return jsonify({"erro": "Números devem ser inteiros."}), 400
    if len(set(numeros_usuario)) != len(numeros_usuario): return jsonify({"erro": "Números repetidos."}), 400
    if len(numeros_usuario) != num_marcados_volante_config:
        return jsonify({"erro": f"Para {nome_loteria}, você deve fornecer {num_marcados_volante_config} números."}), 400
    prob_dec = 0; prob_txt = "Não aplicável."
    if lottery_type == "lotomania":
        if len(numeros_usuario) == 50 and num_sorteados_premio_max == 20:
            comb_fav = combinations_count(num_marcados_volante_config, num_sorteados_premio_max)
            comb_tot = combinations_count(universo_total, num_sorteados_premio_max)
            if comb_tot > 0 and comb_fav > 0 :
                prob_dec = comb_fav / comb_tot
                val_inv = round(comb_tot / comb_fav) if comb_fav > 0 else float('inf')
                prob_txt = f"1 em {val_inv:,}".replace(',', '.') if val_inv != float('inf') else "1 em infinito"
            else: prob_txt = "Combinações inválidas."
        else: prob_txt = "Lotomania (20 acertos) requer jogo de 50 números."
    else:
        if len(numeros_usuario) == num_sorteados_premio_max:
            comb_tot = combinations_count(universo_total, num_sorteados_premio_max)
            if comb_tot > 0: prob_dec = 1 / comb_tot; prob_txt = f"1 em {int(comb_tot):,}".replace(',', '.')
            else: prob_txt = "Combinações resultou em zero."
        else:
            combinacoes_possiveis_com_numeros_marcados = combinations_count(len(numeros_usuario), num_sorteados_premio_max)
            combinacoes_totais_no_universo = combinations_count(universo_total, num_sorteados_premio_max)
            if combinacoes_totais_no_universo > 0 and combinacoes_possiveis_com_numeros_marcados > 0:
                prob_dec = combinacoes_possiveis_com_numeros_marcados / combinacoes_totais_no_universo
                val_inv = round(1 / prob_dec) if prob_dec > 0 else float('inf')
                prob_txt = f"1 em {val_inv:,}".replace(',', '.') if val_inv != float('inf') else "1 em infinito"
            else: prob_txt = "Cálculo de probabilidade indisponível para esta configuração."
    return jsonify({"loteria": nome_loteria, "jogo_usuario": sorted(numeros_usuario), "probabilidade_decimal": prob_dec, "probabilidade_texto": prob_txt, "descricao": f"Probabilidade de acertar o prêmio máximo ({num_sorteados_premio_max} acertos) com um jogo de {len(numeros_usuario)} números."})

def gerar_jogo_ia_aleatorio_rapido(lottery_name): #... (como antes) ...
    config = LOTTERY_CONFIG.get(lottery_name)
    if not config: return {"jogo": [], "estrategia_usada": "Erro: Loteria não configurada"}
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    min_num, max_num = config["min"], config["max"]
    if (max_num - min_num + 1) < numeros_a_gerar: return {"jogo": [], "estrategia_usada": "Erro de Configuração (range insuficiente)"}
    jogo_final = sorted(random.sample(range(min_num, max_num + 1), numeros_a_gerar))
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório Rápido"
    return {"jogo": jogo_final, "estrategia_usada": estrategia_aplicada}

@app.route('/api/main/gerar_jogo/<lottery_name>', methods=['GET'])
def gerar_jogo_api(lottery_name): #... (como antes) ...
    lottery_name_lower = lottery_name.lower()
    if lottery_name_lower not in LOTTERY_CONFIG: return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404
    resultado_geracao = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
    if not resultado_geracao.get("jogo") or len(resultado_geracao.get("jogo")) == 0:
        return jsonify({"erro": f"Não foi possível gerar jogo para {lottery_name}.", "detalhes": resultado_geracao.get("estrategia_usada", "Falha interna")}), 500
    if resultado_geracao.get("jogo"): platform_stats_data["jogos_gerados_total"] += 1
    return jsonify(resultado_geracao)

def get_hot_numbers_strategy(all_results, num_concursos_analisar, num_numeros_gerar, lottery_min, lottery_max, lottery_name_for_log=""): #... (como antes) ...
    if not all_results: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    recent_results = all_results[:num_concursos_analisar]
    if not recent_results:
        recent_results = all_results if len(all_results) > 0 else []
        if not recent_results: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    all_drawn_numbers_in_slice = [num for result in recent_results if "numeros" in result and isinstance(result["numeros"], list) for num in result["numeros"]]
    if not all_drawn_numbers_in_slice: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    number_counts = Counter(all_drawn_numbers_in_slice)
    hot_numbers_sorted_by_freq = sorted(number_counts.items(), key=lambda item: (-item[1], item[0]))
    generated_game = [num for num, count in hot_numbers_sorted_by_freq[:num_numeros_gerar]]
    if len(generated_game) < num_numeros_gerar:
        possible_numbers = list(range(lottery_min, lottery_max + 1))
        random.shuffle(possible_numbers)
        for num in possible_numbers:
            if len(generated_game) == num_numeros_gerar: break
            if num not in generated_game: generated_game.append(num)
    return sorted(generated_game)

@app.route('/api/main/gerar_jogo/numeros_quentes/<lottery_name>', methods=['GET'])
def gerar_jogo_numeros_quentes_api(lottery_name): #... (como antes) ...
    lottery_name_lower = lottery_name.lower(); config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    if not all_results: return jsonify({"erro": f"Dados históricos para {lottery_name.upper()} indisponíveis."}), 500
    try:
        num_concursos_analisar = int(request.args.get('num_concursos_analisar', 20))
        if num_concursos_analisar <= 0 or num_concursos_analisar > len(all_results):
            num_concursos_analisar = min(20, len(all_results)) if len(all_results) > 0 else 1
    except ValueError: num_concursos_analisar = min(20, len(all_results)) if len(all_results) > 0 else 1
    numeros_a_gerar = config.get("count_apostadas", config.get("count")); lottery_min = config["min"]; lottery_max = config["max"]
    jogo_final = get_hot_numbers_strategy(all_results, num_concursos_analisar, numeros_a_gerar, lottery_min, lottery_max, lottery_name_lower)
    if not jogo_final or len(jogo_final) != numeros_a_gerar:
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({"jogo": fallback_result.get("jogo", []), "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Quentes (Fallback Aleatório)", "aviso": "Estratégia não produziu resultado, usando fallback."}), 200
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Quentes ({num_concursos_analisar} concursos)"
    if jogo_final: platform_stats_data["jogos_gerados_total"] += 1
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

def get_cold_numbers_strategy(all_results, num_concursos_analisar, num_numeros_gerar, lottery_min, lottery_max, lottery_name_for_log=""): #... (como antes) ...
    if not all_results: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    recent_results_slice = all_results[:num_concursos_analisar]
    if not recent_results_slice:
        recent_results_slice = all_results if len(all_results) > 0 else []
        if not recent_results_slice: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    drawn_numbers_in_slice = [num for result in recent_results_slice if "numeros" in result and isinstance(result["numeros"], list) for num in result["numeros"]]
    frequency_counts = Counter(drawn_numbers_in_slice); all_possible_numbers = list(range(lottery_min, lottery_max + 1))
    cold_numbers_candidates = sorted([{'numero': num, 'frequencia': frequency_counts.get(num, 0)} for num in all_possible_numbers], key=lambda x: (x['frequencia'], x['numero']))
    final_cold_selection = [candidate['numero'] for candidate in cold_numbers_candidates[:num_numeros_gerar]]
    if len(final_cold_selection) < num_numeros_gerar:
        remaining_possible = [num for num in all_possible_numbers if num not in final_cold_selection]; random.shuffle(remaining_possible)
        final_cold_selection.extend(remaining_possible[:num_numeros_gerar - len(final_cold_selection)])
    final_game = sorted(final_cold_selection)
    if len(final_game) != num_numeros_gerar: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    return final_game

@app.route('/api/main/gerar_jogo/numeros_frios/<lottery_name>', methods=['GET'])
def gerar_jogo_numeros_frios_api(lottery_name): #... (como antes) ...
    lottery_name_lower = lottery_name.lower(); config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    if not all_results: return jsonify({"erro": f"Dados históricos para {lottery_name.upper()} indisponíveis."}), 500
    try:
        num_concursos_analisar = int(request.args.get('num_concursos_analisar', 20))
        if num_concursos_analisar <= 0 or num_concursos_analisar > len(all_results):
            num_concursos_analisar = min(20, len(all_results)) if len(all_results) > 0 else 1
    except ValueError: num_concursos_analisar = min(20, len(all_results)) if len(all_results) > 0 else 1
    numeros_a_gerar = config.get("count_apostadas", config.get("count")); lottery_min = config["min"]; lottery_max = config["max"]
    jogo_final = get_cold_numbers_strategy(all_results, num_concursos_analisar, numeros_a_gerar, lottery_min, lottery_max, lottery_name_lower)
    if not jogo_final or len(jogo_final) != numeros_a_gerar:
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({"jogo": fallback_result.get("jogo", []), "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Frios (Fallback Aleatório)", "aviso": "Estratégia não produziu resultado, usando fallback."}), 200
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Frios ({num_concursos_analisar} concursos)"
    if jogo_final: platform_stats_data["jogos_gerados_total"] += 1
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

def gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_numeros, min_val, max_val): #... (como antes) ...
    app.logger.info(f"Gerando palpite esotérico simples com data: {data_nascimento_str} para {num_numeros} números entre {min_val}-{max_val}")
    numeros_base = set(); soma_total_digitos = 0
    if data_nascimento_str and isinstance(data_nascimento_str, str):
        for digito in data_nascimento_str:
            if digito.isdigit(): soma_total_digitos += int(digito)
    app.logger.info(f"Soma inicial dos dígitos: {soma_total_digitos}")
    while soma_total_digitos > 9: soma_anterior = soma_total_digitos; soma_total_digitos = sum(int(d) for d in str(soma_total_digitos)); app.logger.info(f"Redução numerológica: {soma_anterior} -> {soma_total_digitos}")
    if soma_total_digitos > 0 and min_val <= soma_total_digitos <= max_val: numeros_base.add(soma_total_digitos); app.logger.info(f"Número base da numerologia: {soma_total_digitos}")
    palpite_final = list(numeros_base); tentativas_aleatorias = 0; max_tentativas = num_numeros * 20
    while len(palpite_final) < num_numeros and tentativas_aleatorias < max_tentativas:
        num_aleatorio = random.randint(min_val, max_val)
        if num_aleatorio not in palpite_final: palpite_final.append(num_aleatorio)
        tentativas_aleatorias += 1
    if len(palpite_final) < num_numeros:
        app.logger.warning(f"Não foi possível gerar {num_numeros} únicos. Preenchendo..."); elementos_possiveis = [n for n in range(min_val, max_val + 1) if n not in palpite_final]; random.shuffle(elementos_possiveis)
        necessarios = num_numeros - len(palpite_final); palpite_final.extend(elementos_possiveis[:necessarios])
    final_result = sorted(palpite_final)[:num_numeros]; app.logger.info(f"Palpite esotérico simples gerado: {final_result}")
    return final_result

def verificar_historico_combinacao(lottery_name_lower, combinacao_palpite): #... (como antes) ...
    app.logger.info(f"[verificar_historico] Verificando {combinacao_palpite} para {lottery_name_lower}")
    todos_resultados = load_processed_lottery_data(lottery_name_lower)
    if not todos_resultados: app.logger.warning(f"[verificar_historico] Histórico não carregado para {lottery_name_lower}"); return 0, 0.0
    ocorrencias = 0; valor_total_ganho = 0.0
    try: palpite_formatado = sorted([int(n) for n in combinacao_palpite])
    except (ValueError, TypeError) as e: app.logger.error(f"[verificar_historico] Erro ao formatar palpite: {combinacao_palpite}, Erro: {e}"); return 0, 0.0
    for sorteio in todos_resultados:
        numeros_sorteados = sorteio.get("numeros")
        if numeros_sorteados and isinstance(numeros_sorteados, list):
            try:
                numeros_sorteados_formatados = sorted([int(n) for n in numeros_sorteados])
                if numeros_sorteados_formatados == palpite_formatado:
                    ocorrencias += 1
                    valor_total_ganho += float(sorteio.get("rateio_principal_valor", 0.0))
            except (ValueError, TypeError): continue 
    app.logger.info(f"[verificar_historico] Palpite {palpite_formatado} para {lottery_name_lower}: {ocorrencias} ocorrências, R${valor_total_ganho:.2f} ganhos.")
    return ocorrencias, valor_total_ganho

@app.route('/api/main/palpite-esoterico/<lottery_name>', methods=['POST'])
def gerar_palpite_esoterico_route(lottery_name): #... (como antes) ...
    app.logger.info(f"Endpoint /api/main/palpite-esoterico/{lottery_name} acessado. Path: {request.path}. JSON: {request.get_json(silent=True)}")
    lottery_name_lower = lottery_name.lower(); config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: app.logger.warning(f"Loteria não config para palpite esotérico: {lottery_name}"); return jsonify({"erro": "Loteria não configurada."}), 404
    dados_usuario = request.get_json()
    if not dados_usuario: app.logger.warning("Dados não fornecidos para palpite esotérico."); return jsonify({"erro": "Dados da requisição não fornecidos."}), 400
    data_nascimento_str = dados_usuario.get("data_nascimento")
    if not data_nascimento_str: app.logger.warning("'data_nascimento' não fornecida."); return jsonify({"erro": "Parâmetro 'data_nascimento' não fornecido."}), 400
    num_a_gerar = config.get("count_apostadas", config.get("count", config.get("count_sorteadas")))
    min_val = config["min"]; max_val = config["max"]
    app.logger.info(f"Gerando palpite esotérico para {lottery_name} com data {data_nascimento_str}")
    palpite_gerado = gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_a_gerar, min_val, max_val)
    metodo_usado = f"Baseado em Dados Esotéricos (data_nasc: {data_nascimento_str}) - Simples"
    if not palpite_gerado or len(palpite_gerado) != num_a_gerar:
        app.logger.error(f"Falha ao gerar palpite esotérico: {palpite_gerado}, esperado: {num_a_gerar}")
        palpite_gerado = sorted(random.sample(range(min_val, max_val + 1), num_a_gerar))
        metodo_usado = "Aleatório (fallback pós-falha esotérica)"; app.logger.info(f"Fallback palpite aleatório: {palpite_gerado}")
    ocorrencias, valor_ganho = verificar_historico_combinacao(lottery_name_lower, palpite_gerado)
    response_data = {
        "loteria": config["nome_exibicao"], "palpite_gerado": palpite_gerado,
        "parametros_usados": {"data_nascimento_input": data_nascimento_str},
        "metodo_geracao": metodo_usado,
        "historico_desta_combinacao": {
            "combinacao_verificada": palpite_gerado, "ja_foi_premiada_faixa_principal": ocorrencias > 0,
            "vezes_premiada_faixa_principal": ocorrencias,
            "valor_total_ganho_faixa_principal_formatado": format_currency(valor_ganho),
            "valor_total_ganho_faixa_principal_float": valor_ganho
        }}
    app.logger.info(f"Retornando palpite esotérico para {lottery_name}: {response_data}")
    return jsonify(response_data), 200

# --- LÓGICA DE VERIFICAÇÃO DE JOGOS ---
def determinar_faixa_premio_main(lottery_type, acertos):
    config_loteria = LOTTERY_CONFIG.get(lottery_type)
    if not config_loteria: return "Desconhecida", False
    
    # Regras de premiação específicas para cada loteria
    # Estas são simplificações e precisam ser ajustadas com as regras oficiais.
    if lottery_type == "megasena":
        if acertos == 6: return "Sena (Prêmio Máximo)", True
        if acertos == 5: return "Quina", True
        if acertos == 4: return "Quadra", True
    elif lottery_type == "lotofacil":
        if acertos == 15: return "15 Pontos (Prêmio Máximo)", True
        if acertos == 14: return "14 Pontos", True
        if acertos == 13: return "13 Pontos", True
        if acertos == 12: return "12 Pontos", True
        if acertos == 11: return "11 Pontos", True
    elif lottery_type == "quina":
        if acertos == 5: return "Quina (Prêmio Máximo)", True
        if acertos == 4: return "Quadra", True
        if acertos == 3: return "Terno", True
        if acertos == 2: return "Duque", True
    elif lottery_type == "lotomania":
        # Lotomania tem várias faixas, incluindo 0 acertos
        if acertos == 20: return "20 Pontos (Prêmio Máximo)", True
        if acertos == 19: return "19 Pontos", True
        if acertos == 18: return "18 Pontos", True
        if acertos == 17: return "17 Pontos", True
        if acertos == 16: return "16 Pontos", True
        if acertos == 15: return "15 Pontos", True
        if acertos == 0: return "0 Acertos (Premiado!)", True # Prêmio para quem não acerta nenhum
        
    return f"{acertos} Acertos", False # Default se não se encaixar ou não for premiado

def verificar_jogos_salvos_batch_main():
    global FB_ADMIN_INITIALIZED, db_admin
    if not FB_ADMIN_INITIALIZED or not db_admin:
        app.logger.error("Firebase Admin não inicializado em main.py. Abortando verificação de jogos.")
        return {"status": "error", "message": "Firebase Admin não inicializado."}

    app.logger.info("Iniciando verificação em lote de jogos salvos...")
    try:
        latest_official_results = {}
        for lottery_key_loop in LOTTERY_CONFIG.keys():
            data = load_processed_lottery_data(lottery_key_loop)
            if data and isinstance(data, list) and len(data) > 0:
                latest_official_results[lottery_key_loop] = data[0] # Pega o concurso mais recente
            else:
                app.logger.warning(f"Não foi possível carregar dados recentes para {lottery_key_loop} do Blob.")
        
        if not latest_official_results:
            app.logger.warning("Nenhum resultado oficial carregado do Blob para verificação. Abortando.")
            return {"status": "warning", "message": "Nenhum resultado oficial carregado do Blob."}

        user_games_ref = db_admin.collection('userGames')
        docs_stream = user_games_ref.stream()

        jogos_atualizados_count = 0
        novos_premios_identificados_count = 0

        for doc in docs_stream:
            game_data = doc.to_dict()
            game_id = doc.id
            lottery_type = game_data.get('lottery')
            user_numbers = game_data.get('game')

            if not lottery_type or not user_numbers or lottery_type not in LOTTERY_CONFIG:
                app.logger.warning(f"Jogo {game_id} com dados incompletos ou loteria desconhecida. Pulando.")
                continue

            latest_result_for_lottery = latest_official_results.get(lottery_type)
            if not latest_result_for_lottery:
                app.logger.warning(f"Sem resultado recente para {lottery_type} para o jogo {game_id}. Pulando.")
                continue 

            concurso_atual_oficial = latest_result_for_lottery.get('concurso')
            
            # Se já foi verificado contra este concurso E já tem um status de premiação definido, não reverificar
            if game_data.get('ultimoConcursoVerificado') == concurso_atual_oficial and game_data.get('isPremiado') is not None:
                 continue

            official_numbers = latest_result_for_lottery.get('numeros')
            hits = 0
            hit_numbers_list = []
            if official_numbers and isinstance(user_numbers, list):
                for num_val in user_numbers:
                    try:
                        if int(num_val) in official_numbers: # Garante que ambos são int para comparação
                            hits += 1
                            hit_numbers_list.append(int(num_val))
                    except (ValueError, TypeError):
                        app.logger.warning(f"Valor não numérico em user_numbers para jogo {game_id}: {num_val}")
                        continue
            
            faixa_premio_str, is_premiado_flag = determinar_faixa_premio_main(lottery_type, hits)

            update_data = {
                'ultimoConcursoVerificado': concurso_atual_oficial,
                'dataUltimaVerificacao': admin_firestore.SERVER_TIMESTAMP,
                'acertos': hits,
                'numerosAcertados': sorted(hit_numbers_list), # Salva os números acertados
                'isPremiado': is_premiado_flag,
                'faixaPremio': faixa_premio_str,
                # Marca notificaçãoPendente se é um novo prêmio OU se era um prêmio antigo não notificado
                'notificacaoPendente': True if is_premiado_flag and (game_data.get('isPremiado') == False or game_data.get('notificacaoPendente') == True or game_data.get('isPremiado') is None) else False
            }
            
            user_games_ref.document(game_id).update(update_data)
            jogos_atualizados_count += 1
            if is_premiado_flag and update_data['notificacaoPendente']: 
                novos_premios_identificados_count +=1
                app.logger.info(f"Jogo PREMIADO E NOTIFICAÇÃO PENDENTE! ID: {game_id}, Loteria: {lottery_type}, Acertos: {hits}, Faixa: {faixa_premio_str}")
        
        msg = f"Verificação em lote concluída. {jogos_atualizados_count} jogos verificados/atualizados. {novos_premios_identificados_count} prêmios marcados para notificação."
        app.logger.info(msg)
        return {"status": "success", "message": msg}

    except Exception as e:
        app.logger.error(f"Erro durante a verificação em lote de jogos salvos (main.py): {e}", exc_info=True)
        return {"status": "error", "message": f"Erro interno durante a verificação: {str(e)}"}


@app.route('/api/internal/run-verification', methods=['POST'])
def trigger_game_verification_endpoint():
    INTERNAL_API_KEY = os.environ.get("INTERNAL_CRON_SECRET") # Deve ser configurado na Vercel
    if not INTERNAL_API_KEY:
        app.logger.error("INTERNAL_CRON_SECRET não configurado nas variáveis de ambiente da Vercel.")
        return jsonify({"error": "Configuração interna do servidor ausente."}), 500

    request_api_key = request.headers.get('X-Internal-Api-Key')
    if request_api_key != INTERNAL_API_KEY:
        app.logger.warning("Tentativa de acesso não autorizado ao endpoint de verificação de jogos.")
        return jsonify({"error": "Não autorizado"}), 403
    
    app.logger.info("Disparando verificação de jogos salvos manualmente via endpoint.")
    result = verificar_jogos_salvos_batch_main()
    if result.get("status") == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 500

# Remover o app.run() para produção na Vercel
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)