# api/main.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import os
import json
from collections import Counter
from itertools import combinations
import math
import re
import logging
import firebase_admin
from firebase_admin import credentials, firestore as admin_firestore
import requests
from datetime import datetime 

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.INFO)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# --- INICIALIZAÇÃO DO FIREBASE ADMIN ---
FB_ADMIN_INITIALIZED = False
db_admin = None
try:
    SERVICE_ACCOUNT_KEY_PATH_MAIN = os.path.join(APP_ROOT, "serviceAccountKey.json")
    if os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON') and not firebase_admin._apps:
        service_account_json_str = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        service_account_info = json.loads(service_account_json_str)
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred, name='lotoGeniusApiAppVercel')
        app.logger.info("Firebase Admin SDK inicializado para main.py via variável de ambiente Vercel.")
        FB_ADMIN_INITIALIZED = True
    elif os.path.exists(SERVICE_ACCOUNT_KEY_PATH_MAIN) and not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH_MAIN)
        firebase_admin.initialize_app(cred, name='lotoGeniusApiAppFileLocal')
        app.logger.info("Firebase Admin SDK inicializado para main.py via arquivo local.")
        FB_ADMIN_INITIALIZED = True
    elif firebase_admin._apps: 
        app.logger.info("Firebase Admin SDK já estava inicializado.")
        FB_ADMIN_INITIALIZED = True
    
    if FB_ADMIN_INITIALIZED and not db_admin :
        if firebase_admin._apps:
            app_name_to_use = list(firebase_admin._apps.keys())[0]
            db_admin = admin_firestore.client(app=firebase_admin.get_app(name=app_name_to_use))
        else:
            app.logger.warning("Nenhum app Firebase Admin encontrado após tentativas de inicialização.")
            FB_ADMIN_INITIALIZED = False

    if not FB_ADMIN_INITIALIZED:
         app.logger.warning("Credenciais do Firebase Admin não configuradas corretamente. Funcionalidades dependentes do Firestore Admin podem não funcionar.")

except Exception as e_fb_admin_main:
    app.logger.error(f"Erro GERAL ao inicializar Firebase Admin SDK em main.py: {e_fb_admin_main}")

LOTTERY_CONFIG = {
    "megasena": {
        "nome_exibicao": "Mega-Sena", "min": 1, "max": 60, "count": 6, "count_apostadas": 6,
        "color": "#209869", "processed_json_name": "megasena_processed_results.json",
        "count_sorteadas": 6,
        "rateio_sena_key": "rateio_principal_valor",
        "rateio_quina_key": "rateio_quina_valor",
        "rateio_quadra_key": "rateio_quadra_valor"
    },
    "lotofacil": {
        "nome_exibicao": "Lotofácil", "min": 1, "max": 25, "count": 15, "count_apostadas": 15,
        "color": "#930089", "processed_json_name": "lotofacil_processed_results.json",
        "count_sorteadas": 15
    },
    "lotomania": {
        "nome_exibicao": "Lotomania", "min": 0, "max": 99, "count_apostadas": 50,
        "count_sorteadas": 20, "color": "#f78100",
        "processed_json_name": "lotomania_processed_results.json"
    },
    "quina": {
        "nome_exibicao": "Quina", "min": 1, "max": 80, "count": 5, "count_apostadas": 5,
        "color": "#260085", "processed_json_name": "quina_processed_results.json",
        "count_sorteadas": 5
    }
}

platform_stats_data = {
    "jogos_gerados_total": random.randint(20000, 33000),
    "jogos_premiados_estimativa": random.randint(300, 800),
    "valor_premios_estimativa_bruto": random.uniform(100000, 380000)
}

def format_currency(value):
    if isinstance(value, (int, float)): return f"R$ {value:_.2f}".replace('.', ',').replace('_', '.')
    return "R$ 0,00"

def is_na_custom(value):
    if value is None: return True
    if isinstance(value, float) and math.isnan(value): return True
    if isinstance(value, str): return value.strip().lower() in ['', 'nan', '-']
    return False

def parse_currency_to_float(currency_str):
    if is_na_custom(currency_str): return 0.0
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
    config = LOTTERY_CONFIG.get(lottery_key)
    if not config: app.logger.error(f"Configuração não encontrada para {lottery_key}"); return None
    
    app.logger.info(f"Buscando URL do Blob no Firestore para {lottery_key.upper()}...")
    try:
        doc_ref = db_admin.collection('lottery_data_source_urls').document(lottery_key)
        doc = doc_ref.get()
        if not doc.exists: app.logger.error(f"URL do Blob não encontrado no Firestore para {lottery_key}."); return None
        data_source_info = doc.to_dict(); blob_url = data_source_info.get('blob_url')
        if not blob_url: app.logger.error(f"Campo 'blob_url' não encontrado no Firestore para {lottery_key}."); return None
        
        app.logger.info(f"Carregando dados de {lottery_key.upper()} do Vercel Blob: {blob_url}")
        response = requests.get(blob_url, timeout=20); response.raise_for_status()
        data = response.json()
        app.logger.info(f"Sucesso ao carregar {lottery_key.upper()} ({len(data) if isinstance(data, list) else 'N/A'} registros) do Vercel Blob")
        return data
    except firebase_admin.exceptions.FirebaseError as fb_err: app.logger.error(f"Erro do Firebase ao buscar URL para {lottery_key}: {fb_err}")
    except requests.exceptions.RequestException as e: app.logger.error(f"Erro de requisição ao buscar JSON do Blob {blob_url if 'blob_url' in locals() else 'URL_DESCONHECIDO'}: {e}")
    except Exception as e_gen: app.logger.error(f"Erro genérico ao carregar dados de {blob_url if 'blob_url' in locals() else 'URL_DESCONHECIDO'}: {e_gen}")
    return None

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
    return jsonify({"mensagem": "API Loto Genius AI Refatorada!", "versao": "4.5.1 - Backend Review"})

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
    if not isinstance(all_results, list) or not all_results:
        return jsonify({"erro": f"Formato de dados inesperado para {lottery_name.upper()}."}), 500
    latest_result = all_results[0]
    return jsonify({"ultimo_concurso": latest_result.get("concurso"),"data": latest_result.get("data"),"numeros": latest_result.get("numeros"),"ganhadores_principal_contagem": latest_result.get("ganhadores_principal_contagem"),"cidades_ganhadoras_principal": latest_result.get("cidades_ganhadoras_principal"),"rateio_principal_valor": latest_result.get("rateio_principal_valor"),"fonte": f"Dados Processados - {lottery_name.upper()} (Vercel Blob)"})

@app.route('/api/main/stats/frequencia/<lottery_name>', methods=['GET'])
def get_frequencia_numeros(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    if not isinstance(all_results, list): return jsonify({"data": [], "mensagem": "Formato de dados de resultados inválido."}), 500
    todos_numeros = [num for sorteio in all_results if "numeros" in sorteio and isinstance(sorteio["numeros"], list) for num in sorteio["numeros"]]
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
    if not isinstance(all_results, list): return jsonify({"data": [], "mensagem": "Formato de dados de resultados inválido."}), 500
    numeros_por_sorteio = config.get("count_sorteadas", config.get("count"))
    todos_os_itens_combinacao = [tuple(par) for s in all_results if s.get("numeros") and isinstance(s["numeros"], list) and len(s["numeros"]) == numeros_por_sorteio for par in combinations(sorted(s["numeros"]), 2)]
    if not todos_os_itens_combinacao: return jsonify({"data": [], "mensagem": "Não foi possível gerar pares."}), 200
    contagem_itens = Counter(todos_os_itens_combinacao); itens_ordenados = sorted(contagem_itens.items(), key=lambda item: (-item[1], item[0]))
    itens_formatados = [{"par": [str(n).zfill(2) for n in item_numeros], "frequencia": freq} for item_numeros, freq in itens_ordenados]
    return jsonify({"data": itens_formatados[:30]})

@app.route('/api/main/stats/cidades-premiadas/<lottery_name>', methods=['GET'])
def get_cidades_premiadas(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    if not isinstance(all_results, list): return jsonify({"data": [], "mensagem": "Formato de dados de resultados inválido."}), 500
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
    if not isinstance(all_results, list): return jsonify({"data": [], "mensagem": "Formato de dados de resultados inválido."}), 500
    soma_premios_cidade = Counter()
    for sorteio in all_results:
        cidades = sorteio.get("cidades_ganhadoras_principal", [])
        rateio_bruto = sorteio.get("rateio_principal_valor", 0.0)
        rateio = parse_currency_to_float(rateio_bruto) 
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
            if not (config['min'] <= num <= config['max']): return jsonify({"erro": f"Número {num} fora do range ({config['min']}-{config['max']})."}), 400
            numeros_usuario.append(num)
    except ValueError: return jsonify({"erro": "Números devem ser inteiros."}), 400
    if len(set(numeros_usuario)) != len(numeros_usuario): return jsonify({"erro": "Números repetidos."}), 400
    if len(numeros_usuario) != num_marcados_volante_config:
        return jsonify({"erro": f"Para {nome_loteria}, você deve fornecer {num_marcados_volante_config} números."}), 400
    prob_dec = 0; prob_txt = "Não aplicável."
    if lottery_type == "lotomania":
        if len(numeros_usuario) == 50 and num_sorteados_premio_max == 20: # Para 20 acertos
            comb_fav = combinations_count(num_marcados_volante_config, num_sorteados_premio_max) # Combinações de 50 escolhe 20
            comb_tot = combinations_count(universo_total, num_sorteados_premio_max) # Combinações de 100 escolhe 20
            if comb_tot > 0 and comb_fav > 0 : # comb_fav deve ser 1 aqui na verdade
                prob_dec = 1 / comb_tot # A probabilidade de acertar OS 20 é 1 / C(100,20)
                val_inv = round(comb_tot)
                prob_txt = f"1 em {val_inv:,}".replace(',', '.') if val_inv != float('inf') else "1 em infinito"
            else: prob_txt = "Combinações inválidas."
        else: prob_txt = "Lotomania (20 acertos) requer jogo de 50 números para este cálculo simplificado."
    else:
        if len(numeros_usuario) == num_sorteados_premio_max: # Jogo simples, ex: 6 na Mega
            comb_tot = combinations_count(universo_total, num_sorteados_premio_max)
            if comb_tot > 0: prob_dec = 1 / comb_tot; prob_txt = f"1 em {int(comb_tot):,}".replace(',', '.')
            else: prob_txt = "Combinações resultou em zero."
        else: # Jogos com mais dezenas que o sorteio (ex: 7 na Mega)
            combinacoes_possiveis_com_numeros_marcados = combinations_count(len(numeros_usuario), num_sorteados_premio_max)
            combinacoes_totais_no_universo = combinations_count(universo_total, num_sorteados_premio_max)
            if combinacoes_totais_no_universo > 0 and combinacoes_possiveis_com_numeros_marcados > 0:
                prob_dec = combinacoes_possiveis_com_numeros_marcados / combinacoes_totais_no_universo
                val_inv = round(1 / prob_dec) if prob_dec > 0 else float('inf')
                prob_txt = f"1 em {val_inv:,}".replace(',', '.') if val_inv != float('inf') else "1 em infinito"
            else: prob_txt = "Cálculo de probabilidade indisponível para esta configuração."
    return jsonify({"loteria": nome_loteria, "jogo_usuario": sorted(numeros_usuario), "probabilidade_decimal": prob_dec, "probabilidade_texto": prob_txt, "descricao": f"Probabilidade de acertar o prêmio máximo ({num_sorteados_premio_max} acertos) com um jogo de {len(numeros_usuario)} números."})

def gerar_jogo_ia_aleatorio_rapido(lottery_name):
    config = LOTTERY_CONFIG.get(lottery_name)
    if not config: return {"jogo": [], "estrategia_usada": "Erro: Loteria não configurada"}
    
    numeros_a_gerar = config.get("count_apostadas", config.get("count")) # REVISAR: Pega a quantidade certa
    min_num, max_num = config["min"], config["max"]

    if (max_num - min_num + 1) < numeros_a_gerar: return {"jogo": [], "estrategia_usada": "Erro de Configuração (range insuficiente)"}
    
    # REVISAR: Garantir que 'num_numeros_gerar' seja respeitado
    if (max_num - min_num + 1) < numeros_a_gerar:
        app.logger.error(f"Erro de Configuração para {lottery_name}: range insuficiente ({max_num - min_num + 1}) para gerar {numeros_a_gerar} números.")
        return {"jogo": [], "estrategia_usada": f"Erro de Configuração (range {max_num - min_num + 1} insuficiente para {numeros_a_gerar} números)"}

    jogo_final = sorted(random.sample(range(min_num, max_num + 1), numeros_a_gerar))
    
    if len(jogo_final) != numeros_a_gerar:
        app.logger.error(f"Falha ao gerar {numeros_a_gerar} números para {lottery_name} no aleatório rápido. Obtido: {len(jogo_final)}")
        # Este caso não deveria acontecer com random.sample se o range for suficiente
        return {"jogo": [], "estrategia_usada": "Erro interno na geração aleatória"}

    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório Rápido"
    return {"jogo": jogo_final, "estrategia_usada": estrategia_aplicada}

@app.route('/api/main/gerar_jogo/<lottery_name>', methods=['GET'])
def gerar_jogo_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    if lottery_name_lower not in LOTTERY_CONFIG: return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404
    
    resultado_geracao = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
    
    config = LOTTERY_CONFIG[lottery_name_lower]
    expected_count = config.get("count_apostadas", config.get("count"))

    if not resultado_geracao.get("jogo") or len(resultado_geracao.get("jogo")) != expected_count :
        app.logger.error(f"API /gerar_jogo: Falha ao gerar jogo para {lottery_name}. Esperado: {expected_count}, Recebido: {len(resultado_geracao.get('jogo', []))}. Detalhes: {resultado_geracao.get('estrategia_usada', 'Falha interna')}")
        return jsonify({"erro": f"Não foi possível gerar jogo para {lottery_name}.", "detalhes": resultado_geracao.get("estrategia_usada", "Falha interna na geração")}), 500
    
    if resultado_geracao.get("jogo"): platform_stats_data["jogos_gerados_total"] += 1
    return jsonify(resultado_geracao)

def get_hot_numbers_strategy(all_results, num_concursos_analisar, num_numeros_gerar, lottery_min, lottery_max, lottery_name_for_log=""):
    # REVISAR: Garantir que 'num_numeros_gerar' seja respeitado
    if not all_results: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    recent_results = all_results[:num_concursos_analisar]
    if not recent_results:
        recent_results = all_results if len(all_results) > 0 else []
        if not recent_results: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    all_drawn_numbers_in_slice = [num for result in recent_results if "numeros" in result and isinstance(result["numeros"], list) for num in result["numeros"]]
    if not all_drawn_numbers_in_slice: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    number_counts = Counter(all_drawn_numbers_in_slice)
    hot_numbers_sorted_by_freq = sorted(number_counts.items(), key=lambda item: (-item[1], item[0]))
    
    generated_game = [num for num, count in hot_numbers_sorted_by_freq[:num_numeros_gerar]] # Pega os N mais frequentes
    
    if len(generated_game) < num_numeros_gerar:
        possible_numbers = list(range(lottery_min, lottery_max + 1))
        complementar_needed = num_numeros_gerar - len(generated_game)
        pool_complementar = [num for num in possible_numbers if num not in generated_game]
        random.shuffle(pool_complementar)
        
        generated_game.extend(pool_complementar[:complementar_needed])

    # Salvaguarda final para garantir a contagem, se a lógica acima falhar
    if len(generated_game) != num_numeros_gerar:
        app.logger.warning(f"HotNumbers: Contagem incorreta ({len(generated_game)} de {num_numeros_gerar}) para {lottery_name_for_log}. Recorrendo a aleatório para completar/ajustar.")
        # Se tem mais, corta. Se tem menos, preenche com aleatórios (evitando duplicatas se possível)
        if len(generated_game) > num_numeros_gerar:
            generated_game = sorted(random.sample(generated_game, num_numeros_gerar))
        else: # len < num_numeros_gerar
            current_game_set = set(generated_game)
            possible_fillers = [n for n in range(lottery_min, lottery_max + 1) if n not in current_game_set]
            random.shuffle(possible_fillers)
            needed_to_fill = num_numeros_gerar - len(generated_game)
            generated_game.extend(possible_fillers[:needed_to_fill])
        # Última checagem, se ainda não bate, usa o fallback geral
        if len(generated_game) != num_numeros_gerar:
             return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))


    return sorted(generated_game)

@app.route('/api/main/gerar_jogo/numeros_quentes/<lottery_name>', methods=['GET'])
def gerar_jogo_numeros_quentes_api(lottery_name):
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
        app.logger.warning(f"Números Quentes: Jogo final não corresponde à contagem esperada para {lottery_name}. Esperado: {numeros_a_gerar}, Obtido: {len(jogo_final)}. Usando fallback.")
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({"jogo": fallback_result.get("jogo", []), "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Quentes (Fallback Aleatório)", "aviso": "Estratégia não produziu resultado esperado, usando fallback."}), 200
    
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Quentes ({num_concursos_analisar} concursos)"
    if jogo_final: platform_stats_data["jogos_gerados_total"] += 1
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

def get_cold_numbers_strategy(all_results, num_concursos_analisar, num_numeros_gerar, lottery_min, lottery_max, lottery_name_for_log=""):
    # REVISAR: Garantir que 'num_numeros_gerar' seja respeitado
    if not all_results: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    recent_results_slice = all_results[:num_concursos_analisar]
    if not recent_results_slice:
        recent_results_slice = all_results if len(all_results) > 0 else []
        if not recent_results_slice: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    drawn_numbers_in_slice = [num for result in recent_results_slice if "numeros" in result and isinstance(result["numeros"], list) for num in result["numeros"]]
    frequency_counts = Counter(drawn_numbers_in_slice); all_possible_numbers = list(range(lottery_min, lottery_max + 1))
    cold_numbers_candidates = sorted([{'numero': num, 'frequencia': frequency_counts.get(num, 0)} for num in all_possible_numbers], key=lambda x: (x['frequencia'], x['numero']))
    
    final_cold_selection = [candidate['numero'] for candidate in cold_numbers_candidates[:num_numeros_gerar]] # Pega os N menos frequentes
    
    if len(final_cold_selection) < num_numeros_gerar:
        remaining_possible = [num for num in all_possible_numbers if num not in final_cold_selection]; random.shuffle(remaining_possible)
        final_cold_selection.extend(remaining_possible[:num_numeros_gerar - len(final_cold_selection)])
    
    final_game = sorted(final_cold_selection)

    if len(final_game) != num_numeros_gerar: 
        app.logger.warning(f"ColdNumbers: Contagem incorreta ({len(final_game)} de {num_numeros_gerar}) para {lottery_name_for_log}. Usando fallback aleatório.")
        return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    return final_game

@app.route('/api/main/gerar_jogo/numeros_frios/<lottery_name>', methods=['GET'])
def gerar_jogo_numeros_frios_api(lottery_name):
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
        app.logger.warning(f"Números Frios: Jogo final não corresponde à contagem esperada para {lottery_name}. Esperado: {numeros_a_gerar}, Obtido: {len(jogo_final)}. Usando fallback.")
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({"jogo": fallback_result.get("jogo", []), "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Frios (Fallback Aleatório)", "aviso": "Estratégia não produziu resultado esperado, usando fallback."}), 200
    
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Frios ({num_concursos_analisar} concursos)"
    if jogo_final: platform_stats_data["jogos_gerados_total"] += 1
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

def gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_numeros, min_val, max_val):
    # REVISAR: Garantir que 'num_numeros' seja respeitado
    app.logger.info(f"Gerando palpite esotérico simples com data: {data_nascimento_str} para {num_numeros} números entre {min_val}-{max_val}")
    numeros_base = set(); soma_total_digitos = 0
    if data_nascimento_str and isinstance(data_nascimento_str, str):
        for digito in data_nascimento_str:
            if digito.isdigit(): soma_total_digitos += int(digito)
    app.logger.info(f"Soma inicial dos dígitos: {soma_total_digitos}")
    while soma_total_digitos > 9: soma_anterior = soma_total_digitos; soma_total_digitos = sum(int(d) for d in str(soma_total_digitos)); app.logger.info(f"Redução numerológica: {soma_anterior} -> {soma_total_digitos}")
    if soma_total_digitos > 0 and min_val <= soma_total_digitos <= max_val: numeros_base.add(soma_total_digitos); app.logger.info(f"Número base da numerologia: {soma_total_digitos}")
    
    palpite_final = list(numeros_base); 
    tentativas_aleatorias = 0; 
    max_tentativas_por_numero = 50 # Aumentar tentativas para preenchimento

    while len(palpite_final) < num_numeros and tentativas_aleatorias < (num_numeros * max_tentativas_por_numero) :
        num_aleatorio = random.randint(min_val, max_val)
        if num_aleatorio not in palpite_final: palpite_final.append(num_aleatorio)
        tentativas_aleatorias += 1
    
    if len(palpite_final) < num_numeros:
        app.logger.warning(f"Esotérico: Não foi possível gerar {num_numeros} únicos com a estratégia inicial. Completando aleatoriamente..."); 
        elementos_possiveis = [n for n in range(min_val, max_val + 1) if n not in palpite_final]; 
        random.shuffle(elementos_possiveis)
        necessarios = num_numeros - len(palpite_final)
        palpite_final.extend(elementos_possiveis[:necessarios])
    
    # Garante a quantidade exata, mesmo que a lógica acima falhe (improvável)
    if len(palpite_final) != num_numeros:
        app.logger.error(f"Esotérico: Falha crítica ao ajustar contagem. Esperado {num_numeros}, obtido {len(palpite_final)}. Usando fallback aleatório total.")
        return sorted(random.sample(range(min_val, max_val + 1), num_numeros))

    final_result = sorted(palpite_final)
    app.logger.info(f"Palpite esotérico simples gerado: {final_result}")
    return final_result

def verificar_historico_combinacao(lottery_name_lower, combinacao_palpite):
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
def gerar_palpite_esoterico_route(lottery_name):
    app.logger.info(f"Endpoint /api/main/palpite-esoterico/{lottery_name} acessado. JSON: {request.get_json(silent=True)}")
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
        app.logger.error(f"Falha ao gerar palpite esotérico: {palpite_gerado}, esperado: {num_a_gerar}. Usando fallback.")
        palpite_gerado = sorted(random.sample(range(min_val, max_val + 1), num_a_gerar)) # Fallback
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

def determinar_faixa_premio_main(lottery_type, acertos):
    config_loteria = LOTTERY_CONFIG.get(lottery_type)
    if not config_loteria: return "Desconhecida", False
    
    if lottery_type == "megasena":
        if acertos == 6: return "Sena", True
        if acertos == 5: return "Quina", True
        if acertos == 4: return "Quadra", True
    elif lottery_type == "lotofacil":
        if acertos == 15: return "15 Pontos", True
        if acertos == 14: return "14 Pontos", True
        if acertos == 13: return "13 Pontos", True
        if acertos == 12: return "12 Pontos", True
        if acertos == 11: return "11 Pontos", True
    elif lottery_type == "quina":
        if acertos == 5: return "Quina", True
        if acertos == 4: return "Quadra", True
        if acertos == 3: return "Terno", True
        if acertos == 2: return "Duque", True
    elif lottery_type == "lotomania":
        if acertos == 20: return "20 Pontos", True
        if acertos == 19: return "19 Pontos", True
        if acertos == 18: return "18 Pontos", True
        if acertos == 17: return "17 Pontos", True
        if acertos == 16: return "16 Pontos", True
        if acertos == 15: return "15 Pontos", True
        if acertos == 0: return "0 Acertos", True 
        
    return f"{acertos} Acertos", False

def verificar_jogos_salvos_batch_main():
    global FB_ADMIN_INITIALIZED, db_admin
    if not FB_ADMIN_INITIALIZED or not db_admin:
        app.logger.error("Firebase Admin não inicializado em main.py. Abortando verificação de jogos.")
        return {"status": "error", "message": "Firebase Admin não inicializado."}

    app.logger.info("Iniciando verificação em lote de jogos salvos (via main.py)...")
    try:
        latest_official_results = {}
        for lottery_key_loop in LOTTERY_CONFIG.keys():
            data = load_processed_lottery_data(lottery_key_loop)
            if data and isinstance(data, list) and len(data) > 0:
                latest_official_results[lottery_key_loop] = data[0]
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

            concurso_atual_oficial_str = latest_result_for_lottery.get('concurso')
            if concurso_atual_oficial_str is None:
                app.logger.warning(f"Concurso atual oficial não encontrado para {lottery_type}. Pulando jogo {game_id}.")
                continue
            
            try:
                concurso_atual_oficial = int(concurso_atual_oficial_str)
            except ValueError:
                app.logger.warning(f"Valor de concurso inválido '{concurso_atual_oficial_str}' para {lottery_type}. Pulando jogo {game_id}.")
                continue

            ultimo_concurso_verificado_doc = game_data.get('ultimoConcursoVerificado')
            
            if ultimo_concurso_verificado_doc == concurso_atual_oficial and game_data.get('isPremiado') is not None:
                 continue

            official_numbers_str = latest_result_for_lottery.get('numeros')
            if not official_numbers_str or not isinstance(official_numbers_str, list):
                app.logger.warning(f"Números oficiais não encontrados ou em formato inválido para {lottery_type} concurso {concurso_atual_oficial}. Pulando jogo {game_id}.")
                continue
            
            official_numbers = [int(n) for n in official_numbers_str if isinstance(n, (int, str)) and str(n).isdigit()]

            hits = 0
            hit_numbers_list = []
            if official_numbers and isinstance(user_numbers, list):
                for num_val in user_numbers:
                    try:
                        if int(num_val) in official_numbers:
                            hits += 1
                            hit_numbers_list.append(int(num_val))
                    except (ValueError, TypeError):
                        app.logger.warning(f"Valor não numérico em user_numbers para jogo {game_id}: {num_val}")
                        continue
            
            faixa_premio_str, is_premiado_flag = determinar_faixa_premio_main(lottery_type, hits)
            
            notificacao_deve_ser_pendente = False
            if is_premiado_flag:
                if not game_data.get('isPremiado') or game_data.get('notificacaoPendente', False):
                    notificacao_deve_ser_pendente = True

            update_data = {
                'ultimoConcursoVerificado': concurso_atual_oficial,
                'dataUltimaVerificacao': admin_firestore.SERVER_TIMESTAMP,
                'acertos': hits,
                'numerosAcertados': sorted(hit_numbers_list),
                'isPremiado': is_premiado_flag,
                'faixaPremio': faixa_premio_str,
                'notificacaoPendente': notificacao_deve_ser_pendente
            }
            
            user_games_ref.document(game_id).update(update_data)
            jogos_atualizados_count += 1
            if is_premiado_flag and notificacao_deve_ser_pendente: 
                novos_premios_identificados_count +=1
                app.logger.info(f"Jogo PREMIADO E NOTIFICAÇÃO PENDENTE! ID: {game_id}, Loteria: {lottery_type}, Acertos: {hits}, Faixa: {faixa_premio_str}")
        
        msg = f"Verificação em lote concluída. {jogos_atualizados_count} jogos verificados/atualizados. {novos_premios_identificados_count} prêmios marcados para notificação."
        app.logger.info(msg)
        return {"status": "success", "message": msg}

    except Exception as e:
        app.logger.error(f"Erro durante a verificação em lote de jogos salvos (main.py): {e}", exc_info=True)
        return {"status": "error", "message": f"Erro interno durante a verificação: {str(e)}"}

@app.route('/api/main/verificar-jogo-passado/megasena', methods=['POST'])
def verificar_jogo_passado_megasena_api():
    data = request.get_json()
    if not data or 'concurso' not in data or 'numeros_usuario' not in data:
        return jsonify({"erro": "Dados incompletos: concurso e numeros_usuario são obrigatórios."}), 400

    try:
        concurso_solicitado = int(data['concurso'])
        numeros_usuario_input = data['numeros_usuario']
        if not isinstance(numeros_usuario_input, list) or len(numeros_usuario_input) != 6:
             return jsonify({"erro": "A lista 'numeros_usuario' deve conter 6 dezenas."}), 400
        numeros_usuario = [int(n) for n in numeros_usuario_input] 
        for num_usr in numeros_usuario: 
            if not (1 <= num_usr <= 60):
                return jsonify({"erro": f"Número inválido {num_usr} para Mega-Sena. Deve ser entre 1 e 60."}), 400
        if len(set(numeros_usuario)) != 6: 
            return jsonify({"erro": "Os números do usuário para Mega-Sena não devem conter duplicatas."}), 400

    except ValueError:
        return jsonify({"erro": "Concurso deve ser um inteiro e números do usuário devem ser inteiros válidos."}), 400
    except TypeError:
        return jsonify({"erro": "Formato de 'numeros_usuario' inválido, esperado uma lista de números."}), 400

    all_mega_results = load_processed_lottery_data("megasena")
    if not all_mega_results:
        return jsonify({"erro": "Dados históricos da Mega-Sena indisponíveis no momento."}), 503

    sorteio_encontrado = None
    for sorteio_hist in all_mega_results:
        if sorteio_hist.get("concurso") == concurso_solicitado:
            sorteio_encontrado = sorteio_hist
            break
    
    if not sorteio_encontrado:
        return jsonify({"erro": f"Concurso {concurso_solicitado} da Mega-Sena não encontrado na base de dados."}), 404

    numeros_sorteados_oficial_str = sorteio_encontrado.get("numeros", [])
    if not numeros_sorteados_oficial_str or not isinstance(numeros_sorteados_oficial_str, list) :
         return jsonify({"erro": f"Números sorteados não encontrados ou em formato inválido para o concurso {concurso_solicitado}."}), 500
    
    try:
        numeros_sorteados_oficial = [int(n) for n in numeros_sorteados_oficial_str]
    except ValueError:
        return jsonify({"erro": f"Erro ao processar números sorteados para o concurso {concurso_solicitado}."}), 500

    acertos = len(set(numeros_usuario) & set(numeros_sorteados_oficial))
    
    faixa_premio_txt = "Não Premiado"
    valor_premio = 0.0
    premiado_flag = False
    aviso_premio = None
    
    lottery_config_ms = LOTTERY_CONFIG.get("megasena", {})

    if acertos == 6:
        faixa_premio_txt = "Sena"
        rateio_key = lottery_config_ms.get("rateio_sena_key", "rateio_principal_valor") # Fallback para chave antiga se a nova não existir
        valor_premio_str = sorteio_encontrado.get(rateio_key)
        valor_premio = parse_currency_to_float(valor_premio_str) if valor_premio_str is not None else 0.0
        premiado_flag = True
    elif acertos == 5:
        faixa_premio_txt = "Quina"
        rateio_key = lottery_config_ms.get("rateio_quina_key")
        if rateio_key and sorteio_encontrado.get(rateio_key) is not None:
            valor_premio = parse_currency_to_float(sorteio_encontrado.get(rateio_key))
        else:
            aviso_premio = "Valor do prêmio da Quina não disponível para este concurso na base de dados."
        premiado_flag = True 
    elif acertos == 4:
        faixa_premio_txt = "Quadra"
        rateio_key = lottery_config_ms.get("rateio_quadra_key")
        if rateio_key and sorteio_encontrado.get(rateio_key) is not None:
            valor_premio = parse_currency_to_float(sorteio_encontrado.get(rateio_key))
        else:
            aviso_premio = "Valor do prêmio da Quadra não disponível para este concurso na base de dados."
        premiado_flag = True

    return jsonify({
        "loteria": "Mega-Sena",
        "concurso_verificado": concurso_solicitado,
        "jogo_usuario": sorted(numeros_usuario),
        "numeros_sorteados": sorted(numeros_sorteados_oficial),
        "acertos": acertos,
        "premiado": premiado_flag,
        "faixa_premio": faixa_premio_txt,
        "valor_premio_bruto": valor_premio, # Já é float
        "valor_premio_formatado": format_currency(valor_premio) if premiado_flag and valor_premio > 0 else ("Não aplicável" if not aviso_premio and premiado_flag else "R$ 0,00"),
        "aviso": aviso_premio
    }), 200

@app.route('/api/internal/run-verification', methods=['POST'])
def trigger_game_verification_endpoint():
    INTERNAL_API_KEY = os.environ.get("INTERNAL_CRON_SECRET")
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)