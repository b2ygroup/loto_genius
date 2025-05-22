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
from firebase_admin import credentials, firestore as admin_firestore, exceptions as firebase_exceptions
import requests
from datetime import datetime, timedelta, timezone

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.INFO)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

FB_ADMIN_INITIALIZED = False
db_admin = None
try:
    SERVICE_ACCOUNT_KEY_PATH_MAIN = os.path.join(APP_ROOT, "serviceAccountKey.json")
    if os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON') and not firebase_admin._apps:
        service_account_json_str = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        service_account_info = json.loads(service_account_json_str)
        cred = credentials.Certificate(service_account_info)
        firebase_admin.initialize_app(cred, name='lotoGeniusApiAppVercelMainPyFull') 
        app.logger.info("Firebase Admin SDK inicializado para main.py via Vercel ENV.")
        FB_ADMIN_INITIALIZED = True
    elif os.path.exists(SERVICE_ACCOUNT_KEY_PATH_MAIN) and not firebase_admin._apps:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH_MAIN)
        firebase_admin.initialize_app(cred, name='lotoGeniusApiAppFileLocalMainPyFull') 
        app.logger.info("Firebase Admin SDK inicializado para main.py via arquivo local.")
        FB_ADMIN_INITIALIZED = True
    elif firebase_admin._apps:
        app_name_to_use = list(firebase_admin._apps.keys())[0]
        if not firebase_admin.get_app(name=app_name_to_use):
             firebase_admin.initialize_app(name=app_name_to_use)
        app.logger.info(f"Firebase Admin SDK já estava inicializado com o app: {app_name_to_use}.")
        FB_ADMIN_INITIALIZED = True
    
    if FB_ADMIN_INITIALIZED:
        if not db_admin:
            app_name_to_use = list(firebase_admin._apps.keys())[0]
            db_admin = admin_firestore.client(app=firebase_admin.get_app(name=app_name_to_use))
    else:
         app.logger.warning("Credenciais do Firebase Admin não configuradas corretamente.")

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

PLATFORM_STATS_DOC_REF = None
FICTITIOUS_WINNERS_COL_REF = None
if FB_ADMIN_INITIALIZED and db_admin:
    PLATFORM_STATS_DOC_REF = db_admin.collection('platform_statistics').document('global_metrics')
    FICTITIOUS_WINNERS_COL_REF = db_admin.collection('fictitious_top_winners')

FICTITIOUS_NICKS = [
    "Mestre dos Números", "Rainha da Sorte", "Profeta da Fortuna", "Ás da Loteria", 
    "Imperador dos Palpites", "Dama da Premiação", "Oráculo Milionário", "Gênio da Quina",
    "Estrela da Mega", "Visionário da Lotofácil", "Sábio das Dezenas", "Apostador Lendário",
    "Bruxo dos Bolões", "Ninja dos Números", "Explorador da Sorte", "Arquiteto da Fortuna",
    "Decifrador de Códigos", "Guardião dos Prêmios", "Peregrino da Prosperidade"
]

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
    except ValueError: return 0.0

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
    except firebase_exceptions.FirebaseError as fb_err: app.logger.error(f"Erro do Firebase ao buscar URL para {lottery_key}: {fb_err}")
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

def get_or_create_platform_stats_from_firestore():
    if not PLATFORM_STATS_DOC_REF:
        app.logger.warning("Firestore não disponível para get_or_create_platform_stats_from_firestore.")
        return {
            "total_generated_games": random.randint(35000, 45000),
            "total_fictitious_prizes_awarded": random.randint(400, 900),
            "total_fictitious_prize_value_bruto": random.uniform(150000, 500000),
            "last_fictitious_winner_update_timestamp": datetime.now(timezone.utc) - timedelta(hours=2)
        }
    try:
        doc = PLATFORM_STATS_DOC_REF.get()
        if doc.exists:
            data = doc.to_dict()
            if 'last_fictitious_winner_update_timestamp' in data and not isinstance(data['last_fictitious_winner_update_timestamp'], datetime):
                 data['last_fictitious_winner_update_timestamp'] = datetime.now(timezone.utc) - timedelta(hours=2) 
            return data
        else:
            initial_stats = {
                "total_generated_games": 30000,
                "total_fictitious_prizes_awarded": 150,
                "total_fictitious_prize_value_bruto": 200000.0,
                "last_fictitious_winner_update_timestamp": admin_firestore.SERVER_TIMESTAMP 
            }
            PLATFORM_STATS_DOC_REF.set(initial_stats)
            app.logger.info("Documento de estatísticas da plataforma inicializado no Firestore.")
            initial_stats_for_return = initial_stats.copy()
            initial_stats_for_return['last_fictitious_winner_update_timestamp'] = datetime.now(timezone.utc)
            return initial_stats_for_return
    except firebase_exceptions.FirebaseError as e:
        app.logger.error(f"Erro ao acessar estatísticas no Firestore: {e}")
        return { 
            "total_generated_games": 35000, "total_fictitious_prizes_awarded": 400,
            "total_fictitious_prize_value_bruto": 150000.0,
            "last_fictitious_winner_update_timestamp": datetime.now(timezone.utc) - timedelta(hours=2)
        }

def _simulate_fictitious_win(current_stats_dict):
    if not FICTITIOUS_WINNERS_COL_REF or not PLATFORM_STATS_DOC_REF or not db_admin:
        app.logger.warning("Firestore não disponível para simular ganho fictício.")
        return current_stats_dict

    try:
        is_new_winner = random.random() < 0.70 
        winner_nick_base = random.choice(FICTITIOUS_NICKS)
        chosen_lottery = random.choice(list(LOTTERY_CONFIG.keys()))
        prize_value = random.uniform(50.0, 50000.0) 
        if random.random() < 0.05: # 5% de chance de um prêmio maior
            prize_value = random.uniform(50001.0, 750000.0)

        winner_doc_ref = None
        winner_data_to_set = {}

        if not is_new_winner:
            existing_winners_query = FICTITIOUS_WINNERS_COL_REF.order_by("last_win_date", direction=admin_firestore.Query.ASCENDING).limit(1).stream() 
            existing_winners_list = [doc for doc in existing_winners_query]
            if existing_winners_list:
                winner_doc_to_update = random.choice(existing_winners_list)
                winner_doc_ref = winner_doc_to_update.reference
                winner_data_fs = winner_doc_to_update.to_dict()
                
                winner_data_to_set["nick"] = winner_data_fs.get("nick", f"{winner_nick_base} #{random.randint(100,999)}")
                winner_data_to_set["total_prize_value_bruto"] = winner_data_fs.get("total_prize_value_bruto", 0) + prize_value
                winner_data_to_set["number_of_wins"] = winner_data_fs.get("number_of_wins", 0) + 1
                winner_data_to_set["last_win_lottery"] = chosen_lottery
                winner_data_to_set["last_win_date"] = admin_firestore.SERVER_TIMESTAMP
                app.logger.info(f"Atualizando ganhador fictício existente: {winner_data_to_set['nick']}")
            else:
                is_new_winner = True

        if is_new_winner:
            winner_data_to_set = {
                "nick": f"{winner_nick_base} #{random.randint(1000,9999)}", # Maior range para nicks
                "total_prize_value_bruto": prize_value,
                "last_win_lottery": chosen_lottery,
                "last_win_date": admin_firestore.SERVER_TIMESTAMP,
                "number_of_wins": 1
            }
            winner_doc_ref = FICTITIOUS_WINNERS_COL_REF.document() 
            app.logger.info(f"Criando novo ganhador fictício: {winner_data_to_set['nick']}")

        if winner_doc_ref:
            winner_doc_ref.set(winner_data_to_set, merge=True)

        prizes_awarded = current_stats_dict.get("total_fictitious_prizes_awarded", 0) + 1
        prize_value_total = current_stats_dict.get("total_fictitious_prize_value_bruto", 0) + prize_value
        
        PLATFORM_STATS_DOC_REF.update({
            "total_fictitious_prizes_awarded": prizes_awarded,
            "total_fictitious_prize_value_bruto": prize_value_total,
            "last_fictitious_winner_update_timestamp": admin_firestore.SERVER_TIMESTAMP
        })
        app.logger.info("Estatísticas da plataforma atualizadas com ganho fictício.")
        current_stats_dict["total_fictitious_prizes_awarded"] = prizes_awarded
        current_stats_dict["total_fictitious_prize_value_bruto"] = prize_value_total
        current_stats_dict["last_fictitious_winner_update_timestamp"] = datetime.now(timezone.utc) 

    except firebase_exceptions.FirebaseError as e:
        app.logger.error(f"Erro ao simular ganho fictício no Firestore: {e}")
    
    return current_stats_dict

@app.route('/')
def api_base_root():
    return jsonify({"message": "API Loto Genius Python (api/main.py).", "note": "Endpoints em /api/main/..." })

@app.route('/api/main/')
def api_main_home():
    return jsonify({"mensagem": "API Loto Genius AI Refatorada!", "versao": "4.7.0 - Ganhadores Fictícios e Palpite Lógico"})

@app.route('/api/main/platform-stats', methods=['GET'])
def get_platform_stats_persistent():
    if not FB_ADMIN_INITIALIZED or not PLATFORM_STATS_DOC_REF:
        app.logger.warning("Firestore não inicializado, usando estatísticas em memória para /platform-stats.")
        in_memory_platform_stats = { 
            "jogos_gerados_total": random.randint(35000, 45000),
            "jogos_premiados_total": random.randint(400, 900),
            "valor_premios_total_formatado": format_currency(random.uniform(150000, 500000)),
        }
        in_memory_platform_stats["jogos_gerados_total"] += random.randint(1, 7)
        return jsonify(in_memory_platform_stats)

    current_stats = get_or_create_platform_stats_from_firestore()
    
    new_total_generated_games = current_stats.get("total_generated_games", 0) + random.randint(1, 7)
    try:
        PLATFORM_STATS_DOC_REF.update({"total_generated_games": new_total_generated_games})
        current_stats["total_generated_games"] = new_total_generated_games 
    except firebase_exceptions.FirebaseError as e:
        app.logger.error(f"Erro ao atualizar total_generated_games no Firestore: {e}")

    should_simulate_win = False
    # Aumenta a chance ou frequência para mais dinamismo se desejado
    if random.random() < 0.15: # 15% de chance em cada chamada para simular um ganho
        should_simulate_win = True
    else:
        last_update_obj = current_stats.get("last_fictitious_winner_update_timestamp")
        if last_update_obj and isinstance(last_update_obj, datetime):
             if (datetime.now(timezone.utc) - last_update_obj) > timedelta(minutes=10): # Reduzido para a cada 10 minutos
                should_simulate_win = True
    
    if should_simulate_win:
        current_stats = _simulate_fictitious_win(current_stats)

    return jsonify({
        "jogos_gerados_total": current_stats.get("total_generated_games"),
        "jogos_premiados_total": current_stats.get("total_fictitious_prizes_awarded"),
        "valor_premios_total_formatado": format_currency(current_stats.get("total_fictitious_prize_value_bruto")),
    })

@app.route('/api/main/top-winners', methods=['GET'])
def get_top_winners_persistent():
    if not FB_ADMIN_INITIALIZED or not FICTITIOUS_WINNERS_COL_REF:
        app.logger.warning("Firestore não inicializado, usando ganhadores fallback para /top-winners.")
        winners_fallback = [{"nick": "Sortudo Virtual #777", "prize_total": format_currency(random.uniform(100000, 500000)), "lottery": "Mega-Sena", "date": "21/05/2025"}]
        return jsonify(winners_fallback)

    try:
        winners_query = FICTITIOUS_WINNERS_COL_REF.order_by("total_prize_value_bruto", direction=admin_firestore.Query.DESCENDING).limit(10).stream()
        winners_list = []
        for winner_doc in winners_query:
            winner_data = winner_doc.to_dict()
            win_date = winner_data.get("last_win_date")
            date_str = ""
            if isinstance(win_date, datetime):
                date_str = win_date.strftime("%d/%m/%Y")
            elif hasattr(win_date, 'seconds'): # Checa se é um Timestamp do Firestore não convertido
                date_str = datetime.fromtimestamp(win_date.seconds, tz=timezone.utc).strftime("%d/%m/%Y")
            else:
                date_str = "Data N/A"
            
            winners_list.append({
                "nick": winner_data.get("nick", "Anônimo da Sorte"),
                "prize_total": format_currency(winner_data.get("total_prize_value_bruto", 0)),
                "lottery": LOTTERY_CONFIG.get(winner_data.get("last_win_lottery", ""), {}).get("nome_exibicao", "Diversas"),
                "date": date_str
            })
        
        if not winners_list and FICTITIOUS_WINNERS_COL_REF:
            app.logger.info("Lista de Top Winners vazia, adicionando alguns ganhadores iniciais...")
            initial_stats_dict = get_or_create_platform_stats_from_firestore()
            for _ in range(random.randint(3,5)): 
                initial_stats_dict = _simulate_fictitious_win(initial_stats_dict) 
            
            winners_query = FICTITIOUS_WINNERS_COL_REF.order_by("total_prize_value_bruto", direction=admin_firestore.Query.DESCENDING).limit(10).stream()
            for winner_doc in winners_query:
                winner_data = winner_doc.to_dict()
                win_date = winner_data.get("last_win_date")
                date_str = ""
                if isinstance(win_date, datetime):
                    date_str = win_date.strftime("%d/%m/%Y")
                elif hasattr(win_date, 'seconds'):
                    date_str = datetime.fromtimestamp(win_date.seconds, tz=timezone.utc).strftime("%d/%m/%Y")
                else:
                    date_str = "Data N/A"
                winners_list.append({
                    "nick": winner_data.get("nick"),
                    "prize_total": format_currency(winner_data.get("total_prize_value_bruto")),
                    "lottery": LOTTERY_CONFIG.get(winner_data.get("last_win_lottery", ""), {}).get("nome_exibicao", "Diversas"),
                    "date": date_str
                })
        
        return jsonify(winners_list)
    except firebase_exceptions.FirebaseError as e:
        app.logger.error(f"Erro ao buscar top winners do Firestore: {e}")
        return jsonify({"error": "Não foi possível buscar os top winners"}), 500
    except Exception as e_gen:
        app.logger.error(f"Erro genérico ao buscar top winners: {e_gen}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar top winners"}), 500


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
    todos_numeros_raw = [num_str for sorteio in all_results if "numeros" in sorteio and isinstance(sorteio["numeros"], list) for num_str in sorteio["numeros"]]
    todos_numeros = []
    for num_str in todos_numeros_raw: 
        try: todos_numeros.append(int(num_str))
        except ValueError: pass 
    if not todos_numeros: return jsonify({"data": [], "mensagem": "Nenhum número válido nos dados."}), 200
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
    
    todos_os_itens_combinacao = []
    for s in all_results:
        numeros_str_list = s.get("numeros")
        if numeros_str_list and isinstance(numeros_str_list, list):
            try:
                numeros_int_list = sorted([int(n_str) for n_str in numeros_str_list])
                if len(numeros_int_list) == numeros_por_sorteio: 
                     for par in combinations(numeros_int_list, 2):
                        todos_os_itens_combinacao.append(tuple(par))
            except ValueError:
                continue 

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
        if len(numeros_usuario) == 50 and num_sorteados_premio_max == 20:
            comb_tot = combinations_count(universo_total, num_sorteados_premio_max) 
            if comb_tot > 0 :
                prob_dec = 1 / comb_tot 
                val_inv = round(comb_tot)
                prob_txt = f"1 em {val_inv:,}".replace(',', '.') if val_inv != float('inf') else "1 em infinito"
            else: prob_txt = "Combinações inválidas."
        else: prob_txt = "Lotomania (20 acertos) requer jogo de 50 números para este cálculo."
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

def gerar_jogo_ia_aleatorio_rapido(lottery_name):
    config = LOTTERY_CONFIG.get(lottery_name)
    if not config: return {"jogo": [], "estrategia_usada": "Erro: Loteria não configurada"}
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    min_num, max_num = config["min"], config["max"]
    if (max_num - min_num + 1) < numeros_a_gerar: 
        app.logger.error(f"Erro Aleatório Rápido para {lottery_name}: range insuficiente para gerar {numeros_a_gerar} números.")
        return {"jogo": [], "estrategia_usada": f"Erro Config (range {max_num - min_num + 1} < {numeros_a_gerar})"}
    
    # !!! REVISAR ESTA LÓGICA DE CONTAGEM DE NÚMEROS !!!
    # random.sample DEVE retornar a quantidade correta se o range for suficiente.
    jogo_final = sorted(random.sample(range(min_num, max_num + 1), numeros_a_gerar))
    
    if len(jogo_final) != numeros_a_gerar: # Salvaguarda
        app.logger.error(f"Falha crítica no Aleatório Rápido para {lottery_name}. Esperado {numeros_a_gerar}, obtido {len(jogo_final)}.")
        return {"jogo": [], "estrategia_usada": "Erro Interno na Geração Aleatória"}
        
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório Otimizado" # Nome mais chamativo
    return {"jogo": jogo_final, "estrategia_usada": estrategia_aplicada}

@app.route('/api/main/gerar_jogo/<lottery_name>', methods=['GET'])
def gerar_jogo_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404
    
    resultado_geracao = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
    expected_count = config.get("count_apostadas", config.get("count"))

    if not resultado_geracao.get("jogo") or len(resultado_geracao.get("jogo")) != expected_count :
        app.logger.error(f"API /gerar_jogo: Falha ao gerar jogo para {lottery_name}. Esperado: {expected_count}, Recebido: {len(resultado_geracao.get('jogo', []))}. Detalhes: {resultado_geracao.get('estrategia_usada', 'Falha interna')}")
        return jsonify({"erro": f"Não foi possível gerar jogo para {lottery_name}.", "detalhes": resultado_geracao.get("estrategia_usada", "Falha interna na geração")}), 500
    
    if resultado_geracao.get("jogo") and PLATFORM_STATS_DOC_REF:
        try:
            PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats:
            app.logger.error(f"Erro ao incrementar total_generated_games (aleatório): {e_stats}")
    return jsonify(resultado_geracao)

def get_hot_numbers_strategy(all_results, num_concursos_analisar, num_numeros_gerar, lottery_min, lottery_max, lottery_name_for_log=""):
    # !!! REVISAR ESTA LÓGICA DE CONTAGEM DE NÚMEROS !!!
    if not all_results: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    recent_results = all_results[:num_concursos_analisar]
    if not recent_results:
        recent_results = all_results if len(all_results) > 0 else []
        if not recent_results: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    all_drawn_numbers_in_slice_raw = [num_str for result in recent_results if "numeros" in result and isinstance(result["numeros"], list) for num_str in result["numeros"]]
    all_drawn_numbers_in_slice = []
    for n_str in all_drawn_numbers_in_slice_raw:
        try: all_drawn_numbers_in_slice.append(int(n_str))
        except ValueError: pass

    if not all_drawn_numbers_in_slice: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    number_counts = Counter(all_drawn_numbers_in_slice)
    hot_numbers_sorted_by_freq = sorted(number_counts.items(), key=lambda item: (-item[1], item[0]))
    
    generated_game = [num for num, count in hot_numbers_sorted_by_freq[:num_numeros_gerar]] 
    
    if len(generated_game) < num_numeros_gerar:
        possible_numbers = list(range(lottery_min, lottery_max + 1))
        complementar_needed = num_numeros_gerar - len(generated_game)
        pool_complementar = [num for num in possible_numbers if num not in generated_game]
        random.shuffle(pool_complementar)
        generated_game.extend(pool_complementar[:complementar_needed])

    if len(generated_game) != num_numeros_gerar:
        app.logger.warning(f"HotNumbers: Contagem incorreta ({len(generated_game)} de {num_numeros_gerar}) para {lottery_name_for_log}. Recorrendo a aleatório para completar/ajustar.")
        if len(generated_game) > num_numeros_gerar:
            generated_game = sorted(random.sample(generated_game, num_numeros_gerar))
        else: 
            current_game_set = set(generated_game)
            possible_fillers = [n for n in range(lottery_min, lottery_max + 1) if n not in current_game_set]
            random.shuffle(possible_fillers)
            needed_to_fill = num_numeros_gerar - len(generated_game)
            generated_game.extend(possible_fillers[:needed_to_fill])
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
    if jogo_final and PLATFORM_STATS_DOC_REF:
        try:
            PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats:
            app.logger.error(f"Erro ao incrementar total_generated_games (quentes): {e_stats}")
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

def get_cold_numbers_strategy(all_results, num_concursos_analisar, num_numeros_gerar, lottery_min, lottery_max, lottery_name_for_log=""):
    # !!! REVISAR ESTA LÓGICA DE CONTAGEM DE NÚMEROS !!!
    if not all_results: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    recent_results_slice = all_results[:num_concursos_analisar]
    if not recent_results_slice:
        recent_results_slice = all_results if len(all_results) > 0 else []
        if not recent_results_slice: return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    drawn_numbers_in_slice_raw = [num_str for result in recent_results_slice if "numeros" in result and isinstance(result["numeros"], list) for num_str in result["numeros"]]
    drawn_numbers_in_slice = []
    for n_str in drawn_numbers_in_slice_raw:
        try: drawn_numbers_in_slice.append(int(n_str))
        except ValueError: pass

    frequency_counts = Counter(drawn_numbers_in_slice); all_possible_numbers = list(range(lottery_min, lottery_max + 1))
    cold_numbers_candidates = sorted([{'numero': num, 'frequencia': frequency_counts.get(num, 0)} for num in all_possible_numbers], key=lambda x: (x['frequencia'], x['numero']))
    
    final_cold_selection = [candidate['numero'] for candidate in cold_numbers_candidates[:num_numeros_gerar]]
    
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
    if jogo_final and PLATFORM_STATS_DOC_REF:
        try:
            PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats:
            app.logger.error(f"Erro ao incrementar total_generated_games (frios): {e_stats}")
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

def gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_numeros, min_val, max_val):
    # !!! REVISAR ESTA LÓGICA DE CONTAGEM DE NÚMEROS !!!
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
    max_tentativas_preenchimento = num_numeros * 50 

    while len(palpite_final) < num_numeros and tentativas_aleatorias < max_tentativas_preenchimento :
        num_aleatorio = random.randint(min_val, max_val)
        if num_aleatorio not in palpite_final: palpite_final.append(num_aleatorio)
        tentativas_aleatorias += 1
    
    if len(palpite_final) < num_numeros:
        app.logger.warning(f"Esotérico: Não foi possível gerar {num_numeros} únicos com a estratégia inicial. Completando aleatoriamente..."); 
        elementos_possiveis = [n for n in range(min_val, max_val + 1) if n not in palpite_final]; 
        random.shuffle(elementos_possiveis)
        necessarios = num_numeros - len(palpite_final)
        palpite_final.extend(elementos_possiveis[:necessarios])
        palpite_final = list(set(palpite_final)) # Garante unicidade após extend
    
    # Garante a quantidade exata, mesmo que a lógica acima falhe (improvável)
    if len(palpite_final) > num_numeros:
        palpite_final = random.sample(palpite_final, num_numeros)
    elif len(palpite_final) < num_numeros: # Ainda faltam números
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
        numeros_sorteados_str = sorteio.get("numeros")
        if numeros_sorteados_str and isinstance(numeros_sorteados_str, list):
            try:
                numeros_sorteados_formatados = sorted([int(n) for n in numeros_sorteados_str])
                if numeros_sorteados_formatados == palpite_formatado:
                    ocorrencias += 1
                    # Usa parse_currency_to_float para converter o valor do rateio
                    valor_total_ganho += parse_currency_to_float(sorteio.get("rateio_principal_valor", "0.0"))
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
    if palpite_gerado and PLATFORM_STATS_DOC_REF:
        try:
            PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats:
            app.logger.error(f"Erro ao incrementar total_generated_games (esotérico): {e_stats}")
    return jsonify(response_data), 200

def _generate_logical_hunch(lottery_name, all_results, config):
    # !!! REVISAR ESTA LÓGICA DE CONTAGEM DE NÚMEROS !!!
    app.logger.info(f"Gerando palpite lógico para {lottery_name}")
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    min_val = config["min"]
    max_val = config["max"]
    
    jogo_final_set = set() # Usar set para evitar duplicatas iniciais
    
    numeros_ultimo_sorteio = set()
    if all_results and len(all_results) > 0:
        try:
            numeros_ultimo_sorteio = set(int(n) for n in all_results[0].get("numeros", []))
        except ValueError:
            app.logger.warning(f"Palpite Lógico: Não foi possível converter números do último sorteio para int.")
    
    if all_results:
        todos_numeros_raw = [num_str for sorteio in all_results for num_str in sorteio.get("numeros", [])]
        todos_numeros_int = []
        for n_str in todos_numeros_raw:
            try: todos_numeros_int.append(int(n_str))
            except ValueError: pass

        if todos_numeros_int:
            contagem = Counter(todos_numeros_int)
            frequencia_ordenada = sorted(contagem.items(), key=lambda item: (-item[1], item[0])) 
            
            num_frequentes_a_pegar = math.ceil(numeros_a_gerar * 0.4) # 40% dos mais frequentes
            for num_freq, _ in frequencia_ordenada:
                if len(jogo_final_set) < num_frequentes_a_pegar:
                    if int(num_freq) not in numeros_ultimo_sorteio:
                        jogo_final_set.add(int(num_freq))
                else:
                    break
    
    tentativas_preenchimento = 0
    max_tentativas = numeros_a_gerar * 50 # Limite de tentativas para preenchimento
    pool_aleatorio_inicial = [n for n in range(min_val, max_val + 1) if n not in numeros_ultimo_sorteio and n not in jogo_final_set]
    random.shuffle(pool_aleatorio_inicial)

    idx_pool = 0
    while len(jogo_final_set) < numeros_a_gerar and idx_pool < len(pool_aleatorio_inicial):
        jogo_final_set.add(pool_aleatorio_inicial[idx_pool])
        idx_pool += 1
        tentativas_preenchimento +=1 # Conta como tentativa
        if tentativas_preenchimento > max_tentativas: break

    if len(jogo_final_set) < numeros_a_gerar:
        app.logger.warning(f"Palpite Lógico: Faltaram números ({len(jogo_final_set)} de {numeros_a_gerar}) para {lottery_name}. Completando totalmente aleatório o restante.")
        numeros_restantes_necessarios = numeros_a_gerar - len(jogo_final_set)
        pool_geral_restante = [n for n in range(min_val, max_val + 1) if n not in jogo_final_set] # Não precisa checar ultimo sorteio aqui, pois já estamos em fallback
        random.shuffle(pool_geral_restante)
        jogo_final_set.update(pool_geral_restante[:numeros_restantes_necessarios])

    jogo_final_list = list(jogo_final_set)
    # Garante a contagem correta final, se algo deu muito errado
    if len(jogo_final_list) > numeros_a_gerar:
        jogo_final_list = random.sample(jogo_final_list, numeros_a_gerar)
    elif len(jogo_final_list) < numeros_a_gerar:
        app.logger.error(f"Palpite Lógico: Falha crítica ao gerar contagem correta para {lottery_name}. Gerando totalmente aleatório para completar.")
        # Completa com números totalmente aleatórios, garantindo unicidade com o que já tem
        pool_complementar_final = [n for n in range(min_val, max_val + 1) if n not in jogo_final_list]
        random.shuffle(pool_complementar_final)
        necessarios_final = numeros_a_gerar - len(jogo_final_list)
        jogo_final_list.extend(pool_complementar_final[:necessarios_final])
        # Se mesmo assim falhar (range muito pequeno e números já usados), recorre ao sample direto
        if len(jogo_final_list) != numeros_a_gerar:
            return sorted(list(random.sample(range(min_val, max_val + 1), numeros_a_gerar)))


    return sorted(jogo_final_list)

@app.route('/api/main/gerar_jogo/logico/<lottery_name>', methods=['GET'])
def gerar_jogo_logico_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config:
        return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404

    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response:
        app.logger.warning(f"Dados históricos indisponíveis para palpite lógico de {lottery_name}. Gerando aleatório.")
        resultado_fallback = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        resultado_fallback["estrategia_usada"] = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Lógico (Fallback Aleatório - Sem Histórico)"
        return jsonify(resultado_fallback), 200

    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    jogo_final = _generate_logical_hunch(lottery_name_lower, all_results, config)

    if not jogo_final or len(jogo_final) != numeros_a_gerar:
        app.logger.error(f"API /gerar_jogo/logico: Falha ao gerar jogo para {lottery_name}. Usando fallback aleatório.")
        resultado_fallback = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        resultado_fallback["estrategia_usada"] = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Lógico (Fallback Aleatório Crítico)"
        return jsonify(resultado_fallback)

    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Palpite Lógico Inteligente"
    if jogo_final and PLATFORM_STATS_DOC_REF:
        try:
            PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats_update:
            app.logger.error(f"Erro ao incrementar total_generated_games para palpite lógico: {e_stats_update}")
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

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
        rateio_key = lottery_config_ms.get("rateio_sena_key", "rateio_principal_valor") 
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
        "valor_premio_bruto": valor_premio,
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