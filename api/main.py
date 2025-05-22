from flask import Flask, jsonify, request, redirect
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
        if not firebase_admin.get_app(name=app_name_to_use): # Verifica se o app nomeado existe antes de tentar inicializar
             firebase_admin.initialize_app(name=app_name_to_use) # Isso pode dar erro se já foi inicializado sem nome ou com outro nome
        app.logger.info(f"Firebase Admin SDK já estava inicializado com o app: {app_name_to_use}.")
        FB_ADMIN_INITIALIZED = True
    
    if FB_ADMIN_INITIALIZED:
        if not db_admin: # Só pega o client se db_admin ainda não foi setado
            app_name_to_use = list(firebase_admin._apps.keys())[0] # Pega o nome do primeiro app inicializado
            db_admin = admin_firestore.client(app=firebase_admin.get_app(name=app_name_to_use))
            app.logger.info(f"Cliente Firestore Admin obtido para o app: {app_name_to_use}.")
    else:
         app.logger.warning("Credenciais do Firebase Admin não configuradas corretamente e nenhuma app existente encontrada.")

except Exception as e_fb_admin_main:
    app.logger.error(f"Erro GERAL ao inicializar Firebase Admin SDK em main.py: {e_fb_admin_main}", exc_info=True)


LOTTERY_CONFIG = {
    "megasena": {
        "nome_exibicao": "Mega-Sena", "min": 1, "max": 60, "count": 6, "count_apostadas": 6,
        "color": "#209869", "processed_json_name": "megasena_processed_results.json",
        "count_sorteadas": 6, "preco_aposta_base": 5.0,
        "rateio_sena_key": "rateio_principal_valor", 
        "rateio_quina_key": "rateio_quina_valor",   
        "rateio_quadra_key": "rateio_quadra_valor"  
    },
    "lotofacil": {
        "nome_exibicao": "Lotofácil", "min": 1, "max": 25, "count": 15, "count_apostadas": 15,
        "color": "#930089", "processed_json_name": "lotofacil_processed_results.json",
        "count_sorteadas": 15, "preco_aposta_base": 3.0
    },
    "lotomania": {
        "nome_exibicao": "Lotomania", "min": 0, "max": 99, "count_apostadas": 50,
        "count_sorteadas": 20, "color": "#f78100",
        "processed_json_name": "lotomania_processed_results.json", "preco_aposta_base": 3.0
    },
    "quina": {
        "nome_exibicao": "Quina", "min": 1, "max": 80, "count": 5, "count_apostadas": 5,
        "color": "#260085", "processed_json_name": "quina_processed_results.json",
        "count_sorteadas": 5, "preco_aposta_base": 2.50
    }
}
TAXA_SERVICO_JOGO_MISTERIOSO = 1.50 # Exemplo de taxa de serviço

PLATFORM_STATS_DOC_REF = None
FICTITIOUS_WINNERS_COL_REF = None
MYSTERY_GAMES_COLLECTION = 'mystery_games' # Nome da coleção para jogos misteriosos

if FB_ADMIN_INITIALIZED and db_admin:
    PLATFORM_STATS_DOC_REF = db_admin.collection('platform_statistics').document('global_metrics')
    FICTITIOUS_WINNERS_COL_REF = db_admin.collection('fictitious_top_winners')
else:
    app.logger.warning("db_admin não está configurado. Algumas funcionalidades do Firestore estarão desabilitadas.")


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
    global FB_ADMIN_INITIALIZED, db_admin # Garante acesso às globais
    if not FB_ADMIN_INITIALIZED or not db_admin:
        app.logger.error(f"Firebase Admin não inicializado. Não é possível buscar URL do Blob para {lottery_key}.")
        return None
    config = LOTTERY_CONFIG.get(lottery_key)
    if not config: 
        app.logger.error(f"Configuração não encontrada para {lottery_key}")
        return None
    
    app.logger.info(f"Buscando URL do Blob no Firestore para {lottery_key.upper()}...")
    try:
        doc_ref = db_admin.collection('lottery_data_source_urls').document(lottery_key)
        doc = doc_ref.get()
        if not doc.exists: 
            app.logger.error(f"URL do Blob não encontrado no Firestore para {lottery_key}.")
            return None
        data_source_info = doc.to_dict()
        blob_url = data_source_info.get('blob_url')
        if not blob_url: 
            app.logger.error(f"Campo 'blob_url' não encontrado no Firestore para {lottery_key}.")
            return None
        
        app.logger.info(f"Carregando dados de {lottery_key.upper()} do Vercel Blob: {blob_url}")
        response = requests.get(blob_url, timeout=20)
        response.raise_for_status() # Levanta um erro para status HTTP 4xx/5xx
        data = response.json()
        app.logger.info(f"Sucesso ao carregar {lottery_key.upper()} ({len(data) if isinstance(data, list) else 'N/A'} registros) do Vercel Blob")
        return data
    except firebase_exceptions.FirebaseError as fb_err: 
        app.logger.error(f"Erro do Firebase ao buscar URL para {lottery_key}: {fb_err}")
    except requests.exceptions.RequestException as e: 
        app.logger.error(f"Erro de requisição ao buscar JSON do Blob {(blob_url if 'blob_url' in locals() else 'URL_DESCONHECIDO')}: {e}")
    except Exception as e_gen: 
        app.logger.error(f"Erro genérico ao carregar dados de {(blob_url if 'blob_url' in locals() else 'URL_DESCONHECIDO')}: {e_gen}", exc_info=True)
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
    res = 1
    for i in range(k): res = res * (n - i) // (i + 1)
    return res

def get_or_create_platform_stats_from_firestore():
    if not PLATFORM_STATS_DOC_REF: # PLATFORM_STATS_DOC_REF é definido globalmente
        app.logger.warning("Firestore não disponível para get_or_create_platform_stats_from_firestore.")
        # Retorna dados mockados se o Firestore não estiver disponível
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
            # Converte timestamp do Firestore para datetime se necessário
            if 'last_fictitious_winner_update_timestamp' in data and not isinstance(data['last_fictitious_winner_update_timestamp'], datetime):
                 # Se não for datetime, assume que é um timestamp do Firestore e converte ou usa um valor padrão
                 ts_val = data['last_fictitious_winner_update_timestamp']
                 if hasattr(ts_val, 'seconds'): # Checa se é um Timestamp do Firestore
                     data['last_fictitious_winner_update_timestamp'] = datetime.fromtimestamp(ts_val.seconds, tz=timezone.utc)
                 else: # Fallback se não for reconhecido
                     data['last_fictitious_winner_update_timestamp'] = datetime.now(timezone.utc) - timedelta(hours=2) 
            return data
        else:
            # Cria o documento se ele não existir
            initial_stats = {
                "total_generated_games": 30000,
                "total_fictitious_prizes_awarded": 150,
                "total_fictitious_prize_value_bruto": 200000.0,
                "last_fictitious_winner_update_timestamp": admin_firestore.SERVER_TIMESTAMP # Usa o timestamp do servidor para a primeira criação
            }
            PLATFORM_STATS_DOC_REF.set(initial_stats)
            app.logger.info("Documento de estatísticas da plataforma inicializado no Firestore.")
            initial_stats_for_return = initial_stats.copy()
            initial_stats_for_return['last_fictitious_winner_update_timestamp'] = datetime.now(timezone.utc) # Para retorno imediato
            return initial_stats_for_return
    except firebase_exceptions.FirebaseError as e:
        app.logger.error(f"Erro ao acessar estatísticas no Firestore: {e}")
        # Retorna dados mockados em caso de erro
        return { 
            "total_generated_games": 35000, "total_fictitious_prizes_awarded": 400,
            "total_fictitious_prize_value_bruto": 150000.0,
            "last_fictitious_winner_update_timestamp": datetime.now(timezone.utc) - timedelta(hours=2)
        }

def _simulate_fictitious_win(current_stats_dict):
    global db_admin # Garante acesso à variável global
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

        if not is_new_winner: # Tenta atualizar um ganhador existente
            # Busca um ganhador aleatório para atualizar (limitado para performance)
            # Uma forma mais eficiente seria buscar o mais antigo ou menos premiado, mas isso é mais complexo
            existing_winners_query = FICTITIOUS_WINNERS_COL_REF.order_by("last_win_date", direction=admin_firestore.Query.ASCENDING).limit(1).stream() 
            existing_winners_list = [doc for doc in existing_winners_query]
            if existing_winners_list:
                winner_doc_to_update = random.choice(existing_winners_list) # Pega um dos mais antigos
                winner_doc_ref = winner_doc_to_update.reference
                winner_data_fs = winner_doc_to_update.to_dict()
                
                winner_data_to_set["nick"] = winner_data_fs.get("nick", f"{winner_nick_base} #{random.randint(100,999)}")
                winner_data_to_set["total_prize_value_bruto"] = winner_data_fs.get("total_prize_value_bruto", 0) + prize_value
                winner_data_to_set["number_of_wins"] = winner_data_fs.get("number_of_wins", 0) + 1
                winner_data_to_set["last_win_lottery"] = chosen_lottery
                winner_data_to_set["last_win_date"] = admin_firestore.SERVER_TIMESTAMP
                app.logger.info(f"Atualizando ganhador fictício existente: {winner_data_to_set['nick']}")
            else:
                is_new_winner = True # Se não encontrou nenhum para atualizar, cria um novo

        if is_new_winner:
            winner_data_to_set = {
                "nick": f"{winner_nick_base} #{random.randint(1000,9999)}",
                "total_prize_value_bruto": prize_value,
                "last_win_lottery": chosen_lottery,
                "last_win_date": admin_firestore.SERVER_TIMESTAMP,
                "number_of_wins": 1
            }
            winner_doc_ref = FICTITIOUS_WINNERS_COL_REF.document() # Cria novo documento
            app.logger.info(f"Criando novo ganhador fictício: {winner_data_to_set['nick']}")

        if winner_doc_ref: # Se um documento foi selecionado ou criado
            winner_doc_ref.set(winner_data_to_set, merge=True) # merge=True é útil se atualizando

        # Atualiza as estatísticas da plataforma
        prizes_awarded = current_stats_dict.get("total_fictitious_prizes_awarded", 0) + 1
        prize_value_total = current_stats_dict.get("total_fictitious_prize_value_bruto", 0) + prize_value
        
        PLATFORM_STATS_DOC_REF.update({
            "total_fictitious_prizes_awarded": prizes_awarded,
            "total_fictitious_prize_value_bruto": prize_value_total,
            "last_fictitious_winner_update_timestamp": admin_firestore.SERVER_TIMESTAMP
        })
        app.logger.info("Estatísticas da plataforma atualizadas com ganho fictício.")
        # Atualiza o dicionário local para retorno imediato
        current_stats_dict["total_fictitious_prizes_awarded"] = prizes_awarded
        current_stats_dict["total_fictitious_prize_value_bruto"] = prize_value_total
        current_stats_dict["last_fictitious_winner_update_timestamp"] = datetime.now(timezone.utc) # Para retorno imediato

    except firebase_exceptions.FirebaseError as e:
        app.logger.error(f"Erro ao simular ganho fictício no Firestore: {e}")
    except Exception as e_gen_fict:
        app.logger.error(f"Erro genérico ao simular ganho fictício: {e_gen_fict}", exc_info=True)
    
    return current_stats_dict

# --- ROTAS EXISTENTES ---
@app.route('/')
def api_base_root():
    return jsonify({"message": "API Loto Genius Python (api/main.py).", "note": "Endpoints em /api/..." })

@app.route('/api/') # Adicionando uma rota para /api/ para corresponder ao Vercel
def api_home_vercel():
    return jsonify({"message": "API Loto Genius Python (api/main.py).", "note": "Endpoints em /api/main/..."})


@app.route('/api/main/')
def api_main_home():
    return jsonify({"mensagem": "API Loto Genius AI Refatorada!", "versao": "4.8.0 - Jogo Misterioso"})

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
    if random.random() < 0.15: # 15% de chance em cada chamada para simular um ganho
        should_simulate_win = True
    else:
        last_update_obj = current_stats.get("last_fictitious_winner_update_timestamp")
        if last_update_obj and isinstance(last_update_obj, datetime):
             if (datetime.now(timezone.utc) - last_update_obj) > timedelta(minutes=10): 
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
            win_date_obj = winner_data.get("last_win_date")
            date_str = "Data N/A"
            if isinstance(win_date_obj, datetime):
                date_str = win_date_obj.strftime("%d/%m/%Y")
            elif hasattr(win_date_obj, 'seconds'): # Checa se é um Timestamp do Firestore não convertido
                date_str = datetime.fromtimestamp(win_date_obj.seconds, tz=timezone.utc).strftime("%d/%m/%Y")
            
            winners_list.append({
                "nick": winner_data.get("nick", "Anônimo da Sorte"),
                "prize_total": format_currency(winner_data.get("total_prize_value_bruto", 0)),
                "lottery": LOTTERY_CONFIG.get(winner_data.get("last_win_lottery", ""), {}).get("nome_exibicao", "Diversas"),
                "date": date_str
            })
        
        # Se a lista estiver vazia e o Firestore estiver disponível, tenta popular alguns ganhadores iniciais
        if not winners_list and FICTITIOUS_WINNERS_COL_REF: 
            app.logger.info("Lista de Top Winners vazia, adicionando alguns ganhadores iniciais...")
            initial_stats_dict = get_or_create_platform_stats_from_firestore() # Pega/cria estatísticas atuais
            for _ in range(random.randint(3,5)): # Adiciona 3 a 5 ganhadores
                initial_stats_dict = _simulate_fictitious_win(initial_stats_dict) # Simula e atualiza estatísticas
            
            # Tenta buscar novamente após popular
            winners_query_retry = FICTITIOUS_WINNERS_COL_REF.order_by("total_prize_value_bruto", direction=admin_firestore.Query.DESCENDING).limit(10).stream()
            for winner_doc_retry in winners_query_retry: # Repete a lógica de formatação
                winner_data_retry = winner_doc_retry.to_dict()
                win_date_obj_retry = winner_data_retry.get("last_win_date")
                date_str_retry = "Data N/A"
                if isinstance(win_date_obj_retry, datetime): date_str_retry = win_date_obj_retry.strftime("%d/%m/%Y")
                elif hasattr(win_date_obj_retry, 'seconds'): date_str_retry = datetime.fromtimestamp(win_date_obj_retry.seconds, tz=timezone.utc).strftime("%d/%m/%Y")
                winners_list.append({
                    "nick": winner_data_retry.get("nick"),
                    "prize_total": format_currency(winner_data_retry.get("total_prize_value_bruto")),
                    "lottery": LOTTERY_CONFIG.get(winner_data_retry.get("last_win_lottery", ""), {}).get("nome_exibicao", "Diversas"),
                    "date": date_str_retry
                })
        
        return jsonify(winners_list)
    except firebase_exceptions.FirebaseError as e:
        app.logger.error(f"Erro ao buscar top winners do Firestore: {e}")
        return jsonify({"error": "Não foi possível buscar os top winners"}), 500
    except Exception as e_gen_tw:
        app.logger.error(f"Erro genérico ao buscar top winners: {e_gen_tw}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar top winners"}), 500

@app.route('/api/main/resultados/<lottery_name>', methods=['GET'])
def get_resultados_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results = load_processed_lottery_data(lottery_name_lower)
    if not all_results: return jsonify({"aviso": f"Dados para {lottery_name.upper()} indisponíveis no momento."}), 404
    if not isinstance(all_results, list) or not all_results:
        return jsonify({"erro": f"Formato de dados inesperado para {lottery_name.upper()}."}), 500
    latest_result = all_results[0] # Assume que o primeiro é o mais recente
    return jsonify({
        "ultimo_concurso": latest_result.get("concurso"),
        "data": latest_result.get("data"),
        "numeros": latest_result.get("numeros"),
        "ganhadores_principal_contagem": latest_result.get("ganhadores_principal_contagem"),
        "cidades_ganhadoras_principal": latest_result.get("cidades_ganhadoras_principal"),
        "rateio_principal_valor": latest_result.get("rateio_principal_valor"), # Mantém como string
        "fonte": f"Dados Processados - {lottery_name.upper()} (Vercel Blob)"
    })

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
        except ValueError: pass # Ignora números que não podem ser convertidos para int
    
    if not todos_numeros: return jsonify({"data": [], "mensagem": "Nenhum número válido nos dados."}), 200
    
    contagem = Counter(todos_numeros)
    frequencia_ordenada = sorted(contagem.items(), key=lambda item: (-item[1], item[0])) # Ordena por frequência (desc) e depois por número (asc)
    frequencia_formatada = [{"numero": str(num).zfill(2), "frequencia": freq} for num, freq in frequencia_ordenada]
    return jsonify({"data": frequencia_formatada, "total_sorteios_analisados": len(all_results)})

@app.route('/api/main/stats/pares-frequentes/<lottery_name>', methods=['GET'])
def get_pares_frequentes(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
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
                # Garante que temos o número esperado de dezenas para a loteria
                if len(numeros_int_list) == numeros_por_sorteio: 
                     for par in combinations(numeros_int_list, 2): # Gera pares
                        todos_os_itens_combinacao.append(tuple(par)) # Adiciona como tupla para ser "hashable" no Counter
            except ValueError:
                # app.logger.warning(f"Erro ao converter números para int no sorteio: {s.get('concurso')}, números: {numeros_str_list}")
                continue # Pula este sorteio se houver erro de conversão

    if not todos_os_itens_combinacao: return jsonify({"data": [], "mensagem": "Não foi possível gerar pares."}), 200
    
    contagem_itens = Counter(todos_os_itens_combinacao)
    itens_ordenados = sorted(contagem_itens.items(), key=lambda item: (-item[1], item[0])) # Ordena por frequência (desc) e depois pelo par (asc)
    itens_formatados = [{"par": [str(n).zfill(2) for n in item_numeros], "frequencia": freq} for item_numeros, freq in itens_ordenados]
    return jsonify({"data": itens_formatados[:30]}) # Retorna os top 30


@app.route('/api/main/stats/cidades-premiadas/<lottery_name>', methods=['GET'])
def get_cidades_premiadas(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    if not isinstance(all_results, list): return jsonify({"data": [], "mensagem": "Formato de dados de resultados inválido."}), 500

    contagem_cidades = Counter()
    total_premios_contabilizados = 0
    for sorteio in all_results:
        cidades = sorteio.get("cidades_ganhadoras_principal", [])
        if isinstance(cidades, list): # Garante que 'cidades' é uma lista
            # Filtra cidades vazias, não especificadas, ou traços
            cidades_validas = [c.strip() for c in cidades if c and isinstance(c, str) and c.strip().lower() not in ["", "não especificada", "-", "nao especificada"]]
            if cidades_validas:
                contagem_cidades.update(cidades_validas)
                # Usa o número de ganhadores se disponível, senão o número de cidades válidas como aproximação
                total_premios_contabilizados += sorteio.get("ganhadores_principal_contagem", len(cidades_validas)) 
    
    cidades_ordenadas = sorted(contagem_cidades.items(), key=lambda item: (-item[1], item[0])) # Ordena por frequência (desc) e nome da cidade (asc)
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
        rateio_bruto_str = sorteio.get("rateio_principal_valor", "0.0") # Vem como string "R$ X.XXX,XX"
        rateio_float = parse_currency_to_float(rateio_bruto_str) # Converte para float
        
        num_ganhadores_no_sorteio = sorteio.get("ganhadores_principal_contagem", 0)
        
        if rateio_float > 0 and isinstance(cidades, list) and cidades and num_ganhadores_no_sorteio > 0:
            cidades_validas = [c.strip() for c in cidades if c and isinstance(c, str) and c.strip().lower() not in ["", "não especificada", "-", "nao especificada"]]
            # Distribui o prêmio entre as cidades únicas listadas, proporcionalmente às suas ocorrências no sorteio
            # Se uma cidade aparece X vezes e há Y cidades na lista, ela recebe X/Y do prêmio total.
            # Se 'num_ganhadores_no_sorteio' é mais preciso, usamos ele para dividir o prêmio.
            # Esta lógica assume que cada 'cidade' na lista representa um ganhador.
            for cidade_unica in set(cidades_validas): # Para cada cidade única
                ocorrencias_cidade_no_sorteio = cidades_validas.count(cidade_unica)
                # O valor do prêmio para esta cidade neste sorteio é o rateio por ganhador * número de ganhadores nesta cidade
                soma_premios_cidade[cidade_unica] += rateio_float * ocorrencias_cidade_no_sorteio
                
    cidades_ordenadas = sorted(soma_premios_cidade.items(), key=lambda item: (-item[1], item[0]))
    cidades_formatadas = [{"cidade_uf": cid, "total_ganho_principal_formatado": format_currency(val), "total_ganho_principal_float": val} for cid, val in cidades_ordenadas]
    return jsonify({"data": cidades_formatadas[:30]})

@app.route('/api/main/jogo-manual/probabilidade', methods=['POST'])
def calcular_probabilidade_jogo():
    data = request.get_json()
    if not data or 'lottery_type' not in data or 'numeros_usuario' not in data: 
        return jsonify({"erro": "Dados incompletos."}), 400
    
    lottery_type = data['lottery_type'].lower()
    numeros_usuario_str_list = data['numeros_usuario']
    
    if lottery_type not in LOTTERY_CONFIG: 
        return jsonify({"erro": f"Loteria '{data['lottery_type']}' não configurada."}), 404
    
    config = LOTTERY_CONFIG[lottery_type]
    nome_loteria = config.get('nome_exibicao', lottery_type.capitalize())
    universo_total = config['max'] - config['min'] + 1
    num_sorteados_premio_max = config.get('count_sorteadas', config.get('count')) # Quantos são sorteados para prêmio máximo
    num_marcados_volante_config = config.get('count_apostadas', config.get('count')) # Quantos o usuário marca no volante padrão

    if not isinstance(numeros_usuario_str_list, list): 
        return jsonify({"erro": "Formato 'numeros_usuario' inválido, esperado uma lista."}), 400
    
    numeros_usuario = []
    try:
        for n_str in numeros_usuario_str_list:
            num = int(n_str)
            if not (config['min'] <= num <= config['max']): 
                return jsonify({"erro": f"Número {num} fora do range ({config['min']}-{config['max']}) para {nome_loteria}."}), 400
            numeros_usuario.append(num)
    except ValueError: 
        return jsonify({"erro": "Números do usuário devem ser inteiros."}), 400
    
    if len(set(numeros_usuario)) != len(numeros_usuario): 
        return jsonify({"erro": "Números do usuário contêm duplicatas."}), 400
    
    # Para Lotomania, o cálculo é um pouco diferente se o usuário fornece exatamente 50 números
    # Para outras loterias, o cálculo da probabilidade do prêmio máximo depende de quantos números o usuário jogou
    # A pergunta aqui é: "Qual a probabilidade de acertar o prêmio máximo com ESTE jogo específico?"
    
    num_marcados_pelo_usuario = len(numeros_usuario)

    prob_dec = 0.0
    prob_txt = "Não aplicável para esta configuração."

    if lottery_type == "lotomania":
        # Lotomania: prêmio máximo com 20 acertos (ou 0 acertos), aposta padrão de 50 números.
        if num_marcados_pelo_usuario == 50:
            # Probabilidade de 20 acertos (prêmio máximo)
            # Combinações de 20 números sorteados em um universo de 100. O usuário escolhe 50.
            # Combinações (k números certos entre os N marcados) * Combinações(M-k certos entre os Q-N não marcados) / Combinações(M certos entre Q no universo)
            # Aqui, queremos a chance de acertar todos os 20 (k=20) dentre os 50 marcados (N=50), com M=20 sorteados no universo Q=100.
            # Chance de 20 acertos: C(50,20) * C(100-50, 20-20) / C(100,20) = C(50,20) / C(100,20) -- ISSO ESTÁ ERRADO.
            # Chance de acertar 20 com um jogo de 50 é 1 / C(100,20) se as 20 dezenas sorteadas estiverem entre as 50 escolhidas.
            # A probabilidade de acertar as 20 dezenas sorteadas, tendo escolhido 50, é C(50,20) * C(50,0) / C(100,20). Não.
            # É simplesmente 1 / C(100,20) se as suas 50 escolhidas INCLUEM as 20 sorteadas.
            # A probabilidade de acertar os 20 números sorteados em 20 é 1 em C(100, 20)
            # Se o usuário joga 50 numeros, a chance de acertar os 20 é C(50,20) / C(100,20). Não, é 1 / (C(100,50)/C(80,30))
            # A probabilidade de fazer 20 pontos na Lotomania é 1 / 11.372.635 (C(100,20))
            combinacoes_totais = combinations_count(universo_total, num_sorteados_premio_max) # C(100, 20)
            if combinacoes_totais > 0:
                prob_dec = 1 / combinacoes_totais
                val_inv = round(combinacoes_totais)
                prob_txt = f"1 em {val_inv:,}".replace(',', '.')
            else:
                prob_txt = "Cálculo de combinações resultou em zero."
            descricao_prob = f"Probabilidade de acertar os {num_sorteados_premio_max} números (prêmio máximo) com uma aposta padrão."
        else:
            prob_txt = f"Para {nome_loteria}, o cálculo de probabilidade do prêmio máximo (20 acertos) é baseado em uma aposta padrão de 50 números."
            descricao_prob = f"O jogo fornecido com {num_marcados_pelo_usuario} números não corresponde à aposta padrão de 50 números para este cálculo."

    else: # Outras loterias (Mega, Quina, Lotofácil)
        # Quantos números o usuário pode marcar no volante (count_apostadas)
        # Quantos números são sorteados para o prêmio máximo (count_sorteadas)
        # Quantos o usuário realmente marcou (num_marcados_pelo_usuario)

        # Se o usuário marcou o número exato de dezenas sorteadas para o prêmio máximo
        if num_marcados_pelo_usuario == num_sorteados_premio_max:
            combinacoes_totais = combinations_count(universo_total, num_sorteados_premio_max)
            if combinacoes_totais > 0:
                prob_dec = 1 / combinacoes_totais
                prob_txt = f"1 em {int(combinacoes_totais):,}".replace(',', '.')
            else:
                prob_txt = "Cálculo de combinações resultou em zero."
            descricao_prob = f"Probabilidade de acertar o prêmio máximo ({num_sorteados_premio_max} acertos) com um jogo simples de {num_marcados_pelo_usuario} números."
        
        # Se o usuário marcou MAIS números do que o mínimo para a aposta (ex: 7 números na Mega)
        # E esse número de marcados é o que a loteria permite para essa aposta específica
        elif num_marcados_pelo_usuario > num_sorteados_premio_max and num_marcados_pelo_usuario <= config.get('max_numeros_aposta', num_marcados_volante_config) : # Adicionar 'max_numeros_aposta' no config se tiver
            # Chance de acertar 'num_sorteados_premio_max' ao escolher 'num_marcados_pelo_usuario'
            # é C(num_marcados_pelo_usuario, num_sorteados_premio_max) / C(universo_total, num_sorteados_premio_max)
            combinacoes_favoraveis = combinations_count(num_marcados_pelo_usuario, num_sorteados_premio_max)
            combinacoes_totais_universo = combinations_count(universo_total, num_sorteados_premio_max)

            if combinacoes_totais_universo > 0 and combinacoes_favoraveis > 0:
                prob_dec = combinacoes_favoraveis / combinacoes_totais_universo
                if prob_dec > 0 :
                    val_inv = round(1 / prob_dec)
                    prob_txt = f"1 em {val_inv:,}".replace(',', '.') if val_inv != float('inf') else "Praticamente certo (verifique)"
                else:
                    prob_txt = "Probabilidade muito baixa ou zero."
            else:
                prob_txt = "Cálculo de probabilidade indisponível para esta configuração de jogo."
            descricao_prob = f"Probabilidade de acertar o prêmio máximo ({num_sorteados_premio_max} acertos) com um jogo de {num_marcados_pelo_usuario} números."
        else:
            return jsonify({"erro": f"Para {nome_loteria}, você deve fornecer um número de dezenas compatível com as regras da loteria (ex: {num_marcados_volante_config} ou outras apostas múltiplas permitidas)."}), 400


    return jsonify({
        "loteria": nome_loteria, 
        "jogo_usuario": sorted(numeros_usuario), 
        "probabilidade_decimal": prob_dec, 
        "probabilidade_texto": prob_txt,
        "descricao": descricao_prob
    })

# Função auxiliar para gerar jogo aleatório - Certifique-se que está definida ou importe-a
def gerar_jogo_ia_aleatorio_rapido(lottery_name):
    config = LOTTERY_CONFIG.get(lottery_name)
    if not config: 
        app.logger.error(f"Configuração de loteria não encontrada para '{lottery_name}' em gerar_jogo_ia_aleatorio_rapido.")
        return {"jogo": [], "estrategia_usada": "Erro: Loteria não configurada"}
    
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    min_num, max_num = config["min"], config["max"]
    
    if (max_num - min_num + 1) < numeros_a_gerar: 
        app.logger.error(f"Erro Aleatório Rápido para {lottery_name}: range ({min_num}-{max_num}) insuficiente para gerar {numeros_a_gerar} números.")
        return {"jogo": [], "estrategia_usada": f"Erro Config (range {max_num - min_num + 1} < {numeros_a_gerar})"}
    
    try:
        jogo_final = sorted(random.sample(range(min_num, max_num + 1), numeros_a_gerar))
    except ValueError as e_sample: # Exceção se a população for menor que o tamanho da amostra
        app.logger.error(f"Erro no random.sample para {lottery_name} (range {min_num}-{max_num}, gerar {numeros_a_gerar}): {e_sample}")
        return {"jogo": [], "estrategia_usada": "Erro Interno na Geração Aleatória (sample)"}

    if len(jogo_final) != numeros_a_gerar: # Salvaguarda adicional, embora random.sample deva garantir isso
        app.logger.error(f"Falha crítica no Aleatório Rápido para {lottery_name}. Esperado {numeros_a_gerar}, obtido {len(jogo_final)}.")
        return {"jogo": [], "estrategia_usada": "Erro Interno na Geração Aleatória (contagem)"}
        
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório Otimizado"
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
        # Tenta gerar um jogo totalmente aleatório como fallback extremo
        try:
            jogo_fallback_extremo = sorted(random.sample(range(config["min"], config["max"] + 1), expected_count))
            app.logger.info(f"Fallback extremo para /gerar_jogo {lottery_name} gerou: {jogo_fallback_extremo}")
            return jsonify({"jogo": jogo_fallback_extremo, "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório (Fallback Crítico)", "aviso": "Usado fallback crítico."})
        except Exception as e_fallback:
            app.logger.error(f"Falha no fallback extremo para /gerar_jogo {lottery_name}: {e_fallback}")
            return jsonify({"erro": f"Não foi possível gerar jogo para {lottery_name} mesmo com fallback.", "detalhes": resultado_geracao.get("estrategia_usada", "Falha interna na geração")}), 500

    if resultado_geracao.get("jogo") and PLATFORM_STATS_DOC_REF: # PLATFORM_STATS_DOC_REF precisa estar definido
        try:
            PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats:
            app.logger.error(f"Erro ao incrementar total_generated_games (aleatório): {e_stats}")
    return jsonify(resultado_geracao)

# ... (Restante das suas funções de estratégia get_hot_numbers_strategy, get_cold_numbers_strategy, etc.)
# ... (Certifique-se que elas também usam 'app.logger' e lidam com erros de contagem de números)

# Exemplo de como adaptar uma função de estratégia existente:
def get_hot_numbers_strategy(all_results, num_concursos_analisar, num_numeros_gerar, lottery_min, lottery_max, lottery_name_for_log=""):
    if not all_results: 
        app.logger.warning(f"HotNumbers para {lottery_name_for_log}: Sem resultados históricos, usando aleatório.")
        return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    recent_results = all_results[:num_concursos_analisar]
    if not recent_results: # Se num_concursos_analisar for maior que o disponível, usa todos.
        recent_results = all_results
        if not recent_results: # Ainda sem resultados (lista vazia)
             app.logger.warning(f"HotNumbers para {lottery_name_for_log}: Lista de resultados recentes vazia, usando aleatório.")
             return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    all_drawn_numbers_in_slice_raw = [num_str for result in recent_results if "numeros" in result and isinstance(result["numeros"], list) for num_str in result["numeros"]]
    all_drawn_numbers_in_slice = []
    for n_str in all_drawn_numbers_in_slice_raw:
        try: all_drawn_numbers_in_slice.append(int(n_str))
        except ValueError: pass

    if not all_drawn_numbers_in_slice: 
        app.logger.warning(f"HotNumbers para {lottery_name_for_log}: Nenhum número válido na fatia de resultados, usando aleatório.")
        return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    number_counts = Counter(all_drawn_numbers_in_slice)
    # Pega os 'num_numeros_gerar' mais frequentes. Se houver empate na frequência, a ordenação secundária por número garante consistência.
    hot_numbers_sorted_by_freq = sorted(number_counts.items(), key=lambda item: (-item[1], item[0])) 
    
    generated_game = [num for num, count in hot_numbers_sorted_by_freq[:num_numeros_gerar]] 
    
    # Se não houver números suficientes unicamente pela frequência (ex: todos com mesma baixa frequência)
    if len(generated_game) < num_numeros_gerar:
        app.logger.info(f"HotNumbers para {lottery_name_for_log}: Completando com números aleatórios pois a frequência não gerou o suficiente.")
        possible_numbers_pool = list(range(lottery_min, lottery_max + 1))
        complementar_needed = num_numeros_gerar - len(generated_game)
        
        # Garante que os números complementares não estão já no jogo gerado
        pool_complementar = [num for num in possible_numbers_pool if num not in generated_game]
        random.shuffle(pool_complementar)
        generated_game.extend(pool_complementar[:complementar_needed])
        generated_game = list(set(generated_game)) # Remove duplicatas se houver sobreposição (improvável aqui)

    # Garantia final de contagem (se a lógica acima ainda falhar por algum motivo extremo)
    if len(generated_game) != num_numeros_gerar:
        app.logger.warning(f"HotNumbers para {lottery_name_for_log}: Contagem final incorreta ({len(generated_game)} de {num_numeros_gerar}). Recorrendo a aleatório para ajustar/completar.")
        if len(generated_game) > num_numeros_gerar:
            return sorted(random.sample(generated_game, num_numeros_gerar)) # Pega uma amostra
        else: # len < num_numeros_gerar
            # Preenche o restante com números completamente aleatórios que ainda não estão no jogo
            current_game_set = set(generated_game)
            possible_fillers = [n for n in range(lottery_min, lottery_max + 1) if n not in current_game_set]
            random.shuffle(possible_fillers)
            needed_to_fill = num_numeros_gerar - len(generated_game)
            generated_game.extend(possible_fillers[:needed_to_fill])
            # Se, mesmo assim, a contagem estiver errada (ex: range muito pequeno e tudo já usado), fallback final
            if len(generated_game) != num_numeros_gerar:
                 app.logger.error(f"HotNumbers para {lottery_name_for_log}: Falha crítica no ajuste de contagem. Usando aleatório total.")
                 return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))

    return sorted(generated_game)


@app.route('/api/main/gerar_jogo/numeros_quentes/<lottery_name>', methods=['GET'])
def gerar_jogo_numeros_quentes_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404
    
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: # Se não conseguiu carregar dados históricos, usa aleatório como fallback
        app.logger.warning(f"Números Quentes para {lottery_name}: Dados históricos indisponíveis. Usando fallback aleatório.")
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({
            "jogo": fallback_result.get("jogo", []), 
            "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Quentes (Fallback Aleatório - Sem Histórico)",
            "aviso": "Dados históricos indisponíveis, palpite gerado aleatoriamente."
        }), 200 # Retorna 200 com aviso

    try:
        num_concursos_analisar = int(request.args.get('num_concursos_analisar', 20))
        if num_concursos_analisar <= 0: num_concursos_analisar = 20
        # Limita a análise ao número de resultados disponíveis se for menor que o solicitado
        num_concursos_analisar = min(num_concursos_analisar, len(all_results) if all_results else 20)
    except ValueError: 
        num_concursos_analisar = min(20, len(all_results) if all_results else 20)
    
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    lottery_min, lottery_max = config["min"], config["max"]
    
    jogo_final = get_hot_numbers_strategy(all_results, num_concursos_analisar, numeros_a_gerar, lottery_min, lottery_max, lottery_name_lower)
    
    if not jogo_final or len(jogo_final) != numeros_a_gerar:
        app.logger.warning(f"Números Quentes API para {lottery_name}: Jogo final não corresponde. Esperado: {numeros_a_gerar}, Obtido: {len(jogo_final)}. Usando fallback aleatório.")
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({
            "jogo": fallback_result.get("jogo", []), 
            "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Quentes (Fallback Aleatório Interno)", 
            "aviso": "Estratégia Quente não produziu resultado esperado, usando fallback aleatório."
        }), 200
    
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Quentes ({num_concursos_analisar} últimos concursos)"
    if PLATFORM_STATS_DOC_REF:
        try: PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats: app.logger.error(f"Erro ao incrementar total_generated_games (quentes): {e_stats}")
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

# ... (Adapte get_cold_numbers_strategy de forma similar a get_hot_numbers_strategy) ...
def get_cold_numbers_strategy(all_results, num_concursos_analisar, num_numeros_gerar, lottery_min, lottery_max, lottery_name_for_log=""):
    if not all_results:
        app.logger.warning(f"ColdNumbers para {lottery_name_for_log}: Sem resultados históricos, usando aleatório.")
        return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))

    recent_results_slice = all_results[:num_concursos_analisar]
    if not recent_results_slice:
        app.logger.warning(f"ColdNumbers para {lottery_name_for_log}: Fatia de resultados recentes vazia, usando aleatório.")
        return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    drawn_numbers_in_slice_raw = [num_str for result in recent_results_slice if "numeros" in result and isinstance(result["numeros"], list) for num_str in result["numeros"]]
    drawn_numbers_in_slice = []
    for n_str in drawn_numbers_in_slice_raw:
        try: drawn_numbers_in_slice.append(int(n_str))
        except ValueError: pass

    frequency_counts = Counter(drawn_numbers_in_slice)
    all_possible_numbers_in_range = list(range(lottery_min, lottery_max + 1))
    
    # Cria uma lista de todos os números possíveis com suas frequências (0 se não apareceram)
    cold_numbers_candidates = [{'numero': num, 'frequencia': frequency_counts.get(num, 0)} for num in all_possible_numbers_in_range]
    # Ordena por frequência (ascendente) e depois por número (ascendente) para desempate
    cold_numbers_candidates_sorted = sorted(cold_numbers_candidates, key=lambda x: (x['frequencia'], x['numero']))
    
    final_cold_selection = [candidate['numero'] for candidate in cold_numbers_candidates_sorted[:num_numeros_gerar]]
    
    # Garantia de contagem, similar à estratégia HotNumbers
    if len(final_cold_selection) < num_numeros_gerar:
        app.logger.info(f"ColdNumbers para {lottery_name_for_log}: Completando com números aleatórios (menos frequentes não foram suficientes).")
        # Pega números que não foram selecionados e os embaralha
        remaining_possible = [num['numero'] for num in cold_numbers_candidates_sorted[num_numeros_gerar:]]
        random.shuffle(remaining_possible)
        final_cold_selection.extend(remaining_possible[:num_numeros_gerar - len(final_cold_selection)])
        final_cold_selection = list(set(final_cold_selection)) # Garante unicidade

    if len(final_cold_selection) != num_numeros_gerar:
        app.logger.warning(f"ColdNumbers para {lottery_name_for_log}: Contagem final incorreta ({len(final_cold_selection)} de {num_numeros_gerar}). Recorrendo a aleatório para ajustar.")
        if len(final_cold_selection) > num_numeros_gerar:
            return sorted(random.sample(final_cold_selection, num_numeros_gerar))
        else:
            current_selection_set = set(final_cold_selection)
            possible_fillers = [n for n in all_possible_numbers_in_range if n not in current_selection_set]
            random.shuffle(possible_fillers)
            needed_to_fill = num_numeros_gerar - len(final_cold_selection)
            final_cold_selection.extend(possible_fillers[:needed_to_fill])
            if len(final_cold_selection) != num_numeros_gerar:
                app.logger.error(f"ColdNumbers para {lottery_name_for_log}: Falha crítica no ajuste de contagem. Usando aleatório total.")
                return sorted(random.sample(all_possible_numbers_in_range, num_numeros_gerar))
                
    return sorted(final_cold_selection)


@app.route('/api/main/gerar_jogo/numeros_frios/<lottery_name>', methods=['GET'])
def gerar_jogo_numeros_frios_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404

    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: # Fallback se dados históricos não disponíveis
        app.logger.warning(f"Números Frios para {lottery_name}: Dados históricos indisponíveis. Usando fallback aleatório.")
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({
            "jogo": fallback_result.get("jogo", []), 
            "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Frios (Fallback Aleatório - Sem Histórico)",
            "aviso": "Dados históricos indisponíveis, palpite gerado aleatoriamente."
        }), 200

    try:
        num_concursos_analisar = int(request.args.get('num_concursos_analisar', 20))
        if num_concursos_analisar <= 0: num_concursos_analisar = 20
        num_concursos_analisar = min(num_concursos_analisar, len(all_results) if all_results else 20)
    except ValueError: 
        num_concursos_analisar = min(20, len(all_results) if all_results else 20)
    
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    lottery_min, lottery_max = config["min"], config["max"]
    
    jogo_final = get_cold_numbers_strategy(all_results, num_concursos_analisar, numeros_a_gerar, lottery_min, lottery_max, lottery_name_lower)
    
    if not jogo_final or len(jogo_final) != numeros_a_gerar:
        app.logger.warning(f"Números Frios API para {lottery_name}: Jogo final não corresponde. Esperado: {numeros_a_gerar}, Obtido: {len(jogo_final)}. Usando fallback aleatório.")
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({
            "jogo": fallback_result.get("jogo", []), 
            "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Frios (Fallback Aleatório Interno)", 
            "aviso": "Estratégia Fria não produziu resultado esperado, usando fallback aleatório."
        }), 200
    
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Frios ({num_concursos_analisar} últimos concursos)"
    if PLATFORM_STATS_DOC_REF:
        try: PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats: app.logger.error(f"Erro ao incrementar total_generated_games (frios): {e_stats}")
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

# ... (Adapte gerar_numeros_baseados_em_data_simples de forma similar) ...
def gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_numeros_gerar, min_val, max_val, lottery_name_for_log=""):
    app.logger.info(f"Gerando palpite esotérico simples com data: {data_nascimento_str} para {lottery_name_for_log} ({num_numeros_gerar} números entre {min_val}-{max_val})")
    numeros_base = set()
    soma_total_digitos = 0
    
    if data_nascimento_str and isinstance(data_nascimento_str, str):
        for digito in data_nascimento_str:
            if digito.isdigit(): 
                soma_total_digitos += int(digito)
    
    # Redução numerológica
    app.logger.info(f"Soma inicial dos dígitos para {lottery_name_for_log}: {soma_total_digitos}")
    soma_reduzida = soma_total_digitos
    while soma_reduzida > 9 and soma_reduzida not in [11, 22, 33]: # Mantém números mestres se desejar, ou remove
        soma_anterior_temp = soma_reduzida
        soma_reduzida = sum(int(d) for d in str(soma_reduzida))
        app.logger.info(f"Redução numerológica para {lottery_name_for_log}: {soma_anterior_temp} -> {soma_reduzida}")
    
    if soma_reduzida > 0 and min_val <= soma_reduzida <= max_val:
        numeros_base.add(soma_reduzida)
        app.logger.info(f"Número base da numerologia para {lottery_name_for_log}: {soma_reduzida}")

    # Tenta adicionar variações da data se ainda precisar de números
    if data_nascimento_str and isinstance(data_nascimento_str, str) and len(numeros_base) < num_numeros_gerar :
        dia = int(data_nascimento_str[0:2]) if len(data_nascimento_str) >= 2 else 0
        mes = int(data_nascimento_str[2:4]) if len(data_nascimento_str) >= 4 else 0
        # ano_curto = int(data_nascimento_str[6:8]) if len(data_nascimento_str) == 8 else 0 # Ex: 90

        if min_val <= dia <= max_val and dia not in numeros_base: numeros_base.add(dia)
        if len(numeros_base) < num_numeros_gerar and min_val <= mes <= max_val and mes not in numeros_base: numeros_base.add(mes)
        # if len(numeros_base) < num_numeros_gerar and min_val <= ano_curto <= max_val and ano_curto not in numeros_base : numeros_base.add(ano_curto)
    
    palpite_final_list = list(numeros_base)
    
    # Completa com números aleatórios se necessário
    if len(palpite_final_list) < num_numeros_gerar:
        app.logger.info(f"Esotérico para {lottery_name_for_log}: Completando com números aleatórios.")
        pool_complementar = [n for n in range(min_val, max_val + 1) if n not in palpite_final_list]
        random.shuffle(pool_complementar)
        necessarios = num_numeros_gerar - len(palpite_final_list)
        palpite_final_list.extend(pool_complementar[:necessarios])
    
    # Garante a contagem exata e unicidade
    final_game_set = set(palpite_final_list)
    if len(final_game_set) > num_numeros_gerar:
        final_result = sorted(random.sample(list(final_game_set), num_numeros_gerar))
    elif len(final_game_set) < num_numeros_gerar: # Ainda faltam (improvável se pool_complementar foi bem feito)
        app.logger.error(f"Esotérico para {lottery_name_for_log}: Falha crítica ao completar. Usando fallback aleatório total.")
        return sorted(random.sample(range(min_val, max_val + 1), num_numeros_gerar))
    else:
        final_result = sorted(list(final_game_set))

    app.logger.info(f"Palpite esotérico simples gerado para {lottery_name_for_log}: {final_result}")
    return final_result


def verificar_historico_combinacao(lottery_name_lower, combinacao_palpite_int_list):
    app.logger.info(f"[verificar_historico] Verificando {combinacao_palpite_int_list} para {lottery_name_lower}")
    todos_resultados = load_processed_lottery_data(lottery_name_lower)
    if not todos_resultados: 
        app.logger.warning(f"[verificar_historico] Histórico não carregado para {lottery_name_lower}")
        return 0, 0.0, "Histórico indisponível"
    
    ocorrencias = 0
    valor_total_ganho = 0.0
    concursos_premiados_info = [] # Lista para armazenar info dos concursos premiados

    palpite_ordenado = sorted(combinacao_palpite_int_list) # Garante que o palpite está ordenado

    for sorteio in todos_resultados:
        numeros_sorteados_str = sorteio.get("numeros")
        if numeros_sorteados_str and isinstance(numeros_sorteados_str, list):
            try:
                numeros_sorteados_int = sorted([int(n_str) for n_str in numeros_sorteados_str]) # Ordena para comparação
                if numeros_sorteados_int == palpite_ordenado: # Compara listas ordenadas
                    ocorrencias += 1
                    rateio_str = sorteio.get("rateio_principal_valor", "0.0")
                    valor_ganho_neste_sorteio = parse_currency_to_float(rateio_str)
                    valor_total_ganho += valor_ganho_neste_sorteio
                    concursos_premiados_info.append({
                        "concurso": sorteio.get("concurso"),
                        "data": sorteio.get("data"),
                        "valor_premio_formatado": format_currency(valor_ganho_neste_sorteio)
                    })
            except (ValueError, TypeError) as e_conv: 
                # app.logger.warning(f"[verificar_historico] Erro ao processar números do sorteio {sorteio.get('concurso')}: {e_conv}")
                continue 
    
    app.logger.info(f"[verificar_historico] Palpite {palpite_ordenado} para {lottery_name_lower}: {ocorrencias} ocorrências, R${valor_total_ganho:.2f} ganhos. Detalhes: {concursos_premiados_info}")
    return ocorrencias, valor_total_ganho, concursos_premiados_info


@app.route('/api/main/palpite-esoterico/<lottery_name>', methods=['POST'])
def gerar_palpite_esoterico_route(lottery_name):
    app.logger.info(f"Endpoint /api/main/palpite-esoterico/{lottery_name} acessado. JSON: {request.get_json(silent=True)}")
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: 
        app.logger.warning(f"Loteria não config para palpite esotérico: {lottery_name}")
        return jsonify({"erro": "Loteria não configurada."}), 404
    
    dados_usuario = request.get_json()
    if not dados_usuario: 
        app.logger.warning("Dados não fornecidos para palpite esotérico.")
        return jsonify({"erro": "Dados da requisição não fornecidos."}), 400
    
    data_nascimento_str = dados_usuario.get("data_nascimento") # Espera DDMMAAAA
    if not data_nascimento_str or not re.match(r"^\d{8}$", data_nascimento_str): 
        app.logger.warning(f"'data_nascimento' inválida ou não fornecida: {data_nascimento_str}")
        return jsonify({"erro": "Parâmetro 'data_nascimento' (DDMMAAAA) inválido ou não fornecido."}), 400
    
    num_a_gerar = config.get("count_apostadas", config.get("count", config.get("count_sorteadas")))
    min_val, max_val = config["min"], config["max"]
    
    app.logger.info(f"Gerando palpite esotérico para {lottery_name} com data {data_nascimento_str}")
    palpite_gerado_int_list = gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_a_gerar, min_val, max_val, lottery_name_lower)
    metodo_usado = f"Baseado em Numerologia (data: {data_nascimento_str[0:2]}/{data_nascimento_str[2:4]}/{data_nascimento_str[4:8]})"
    
    if not palpite_gerado_int_list or len(palpite_gerado_int_list) != num_a_gerar:
        app.logger.error(f"Falha ao gerar palpite esotérico: {palpite_gerado_int_list}, esperado: {num_a_gerar}. Usando fallback aleatório.")
        palpite_gerado_int_list = sorted(random.sample(range(min_val, max_val + 1), num_a_gerar)) 
        metodo_usado = "Aleatório (fallback pós-falha esotérica)"
        app.logger.info(f"Fallback palpite aleatório para esotérico: {palpite_gerado_int_list}")
    
    ocorrencias, valor_ganho, detalhes_premiacao = verificar_historico_combinacao(lottery_name_lower, palpite_gerado_int_list)
    
    response_data = {
        "loteria": config["nome_exibicao"], 
        "palpite_gerado": palpite_gerado_int_list, # Lista de inteiros
        "parametros_usados": {"data_nascimento_input": data_nascimento_str},
        "metodo_geracao": metodo_usado,
        "historico_desta_combinacao": {
            "combinacao_verificada": palpite_gerado_int_list, 
            "ja_foi_premiada_faixa_principal": ocorrencias > 0,
            "vezes_premiada_faixa_principal": ocorrencias,
            "valor_total_ganho_faixa_principal_formatado": format_currency(valor_ganho),
            "valor_total_ganho_faixa_principal_float": valor_ganho,
            "detalhes_concursos_premiados": detalhes_premiacao if isinstance(detalhes_premiacao, list) else "N/A"
        }
    }
    app.logger.info(f"Retornando palpite esotérico para {lottery_name}: {response_data}")
    if PLATFORM_STATS_DOC_REF: # PLATFORM_STATS_DOC_REF precisa estar definido
        try: PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats: app.logger.error(f"Erro ao incrementar total_generated_games (esotérico): {e_stats}")
    return jsonify(response_data), 200


# ... (Adapte _generate_logical_hunch de forma similar, garantindo contagem correta e logging) ...
def _generate_logical_hunch(lottery_name, all_results, config):
    app.logger.info(f"Gerando palpite lógico para {lottery_name}")
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    min_val, max_val = config["min"], config["max"]
    
    jogo_final_set = set() 
    
    # 1. Evitar números do último sorteio (se disponível)
    numeros_ultimo_sorteio = set()
    if all_results and len(all_results) > 0:
        try:
            numeros_ultimo_sorteio = set(int(n_str) for n_str in all_results[0].get("numeros", []))
        except ValueError:
            app.logger.warning(f"Palpite Lógico para {lottery_name}: Não foi possível converter números do último sorteio para int.")
    
    # 2. Pegar alguns dos mais frequentes (que não saíram no último)
    if all_results:
        todos_numeros_raw_lg = [num_str for sorteio in all_results for num_str in sorteio.get("numeros", [])]
        todos_numeros_int_lg = []
        for n_str_lg in todos_numeros_raw_lg:
            try: todos_numeros_int_lg.append(int(n_str_lg))
            except ValueError: pass

        if todos_numeros_int_lg:
            contagem_lg = Counter(todos_numeros_int_lg)
            frequencia_ordenada_lg = sorted(contagem_lg.items(), key=lambda item: (-item[1], item[0])) 
            
            num_frequentes_a_pegar = math.ceil(numeros_a_gerar * 0.4) # Ex: 40%
            for num_freq_val, _ in frequencia_ordenada_lg:
                if len(jogo_final_set) < num_frequentes_a_pegar:
                    if int(num_freq_val) not in numeros_ultimo_sorteio: # Condição importante
                        jogo_final_set.add(int(num_freq_val))
                else:
                    break
    
    # 3. Completar com números aleatórios (que não saíram no último e não estão já no set)
    pool_aleatorio_logico = [n for n in range(min_val, max_val + 1) if n not in numeros_ultimo_sorteio and n not in jogo_final_set]
    random.shuffle(pool_aleatorio_logico)

    idx_pool_lg = 0
    while len(jogo_final_set) < numeros_a_gerar and idx_pool_lg < len(pool_aleatorio_logico):
        jogo_final_set.add(pool_aleatorio_logico[idx_pool_lg])
        idx_pool_lg += 1

    # Garantia de contagem
    jogo_final_list_lg = list(jogo_final_set)
    if len(jogo_final_list_lg) < numeros_a_gerar:
        app.logger.warning(f"Palpite Lógico para {lottery_name}: Faltaram números ({len(jogo_final_list_lg)} de {numeros_a_gerar}). Completando totalmente aleatório o restante (sem restrições).")
        pool_geral_restante_lg = [n for n in range(min_val, max_val + 1) if n not in jogo_final_list_lg]
        random.shuffle(pool_geral_restante_lg)
        necessarios_lg = numeros_a_gerar - len(jogo_final_list_lg)
        jogo_final_list_lg.extend(pool_geral_restante_lg[:necessarios_lg])

    if len(jogo_final_list_lg) > numeros_a_gerar: # Se por acaso passou (ex: lógica inicial pegou mais)
        jogo_final_list_lg = random.sample(jogo_final_list_lg, numeros_a_gerar)
    
    # Fallback final se ainda houver problema de contagem (muito improvável)
    if len(jogo_final_list_lg) != numeros_a_gerar:
        app.logger.error(f"Palpite Lógico para {lottery_name}: Falha crítica ao gerar contagem correta. Gerando totalmente aleatório.")
        return sorted(list(random.sample(range(min_val, max_val + 1), numeros_a_gerar)))

    return sorted(jogo_final_list_lg)


@app.route('/api/main/gerar_jogo/logico/<lottery_name>', methods=['GET'])
def gerar_jogo_logico_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config:
        return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404

    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    # Mesmo se houver erro nos dados históricos, tentamos gerar um palpite lógico (que pode acabar sendo aleatório)
    if error_response and status_code != 503 : # Se o erro não for indisponibilidade temporária do Blob
         app.logger.warning(f"Palpite Lógico para {lottery_name}: Erro ao buscar dados históricos ({status_code}). Estratégia pode ser comprometida.")
         # Não retorna erro aqui, deixa _generate_logical_hunch lidar com all_results = None

    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    jogo_final = _generate_logical_hunch(lottery_name_lower, all_results, config) # all_results pode ser None

    if not jogo_final or len(jogo_final) != numeros_a_gerar:
        app.logger.error(f"API /gerar_jogo/logico: Falha ao gerar jogo para {lottery_name}. Usando fallback aleatório geral.")
        resultado_fallback = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower) # Fallback mais robusto
        return jsonify({
            "jogo": resultado_fallback.get("jogo", []),
            "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Palpite Lógico (Fallback Aleatório Crítico)",
            "aviso": "Falha na estratégia lógica, usando palpite aleatório."
        }), 200 # Retorna 200 com aviso e fallback

    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Palpite Lógico Inteligente"
    if PLATFORM_STATS_DOC_REF:
        try: PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats_update: app.logger.error(f"Erro ao incrementar total_generated_games para palpite lógico: {e_stats_update}")
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})


def determinar_faixa_premio_main(lottery_type, acertos):
    config_loteria = LOTTERY_CONFIG.get(lottery_type)
    if not config_loteria: return "Desconhecida", False
    
    # Lógica para determinar faixas e se foi premiado
    # Adapte conforme as regras de cada loteria e os dados que você tem
    premiado = False
    faixa = f"{acertos} Acertos"

    if lottery_type == "megasena":
        if acertos == 6: faixa, premiado = "Sena", True
        elif acertos == 5: faixa, premiado = "Quina", True
        elif acertos == 4: faixa, premiado = "Quadra", True
    elif lottery_type == "lotofacil":
        if acertos == 15: faixa, premiado = "15 Pontos", True
        elif acertos == 14: faixa, premiado = "14 Pontos", True
        elif acertos == 13: faixa, premiado = "13 Pontos", True
        elif acertos == 12: faixa, premiado = "12 Pontos", True
        elif acertos == 11: faixa, premiado = "11 Pontos", True
    elif lottery_type == "quina":
        if acertos == 5: faixa, premiado = "Quina", True
        elif acertos == 4: faixa, premiado = "Quadra", True
        elif acertos == 3: faixa, premiado = "Terno", True
        elif acertos == 2: faixa, premiado = "Duque", True # Algumas faixas podem não ter prêmio monetário relevante
    elif lottery_type == "lotomania":
        if acertos == 20: faixa, premiado = "20 Pontos", True
        elif acertos == 19: faixa, premiado = "19 Pontos", True
        elif acertos == 18: faixa, premiado = "18 Pontos", True
        elif acertos == 17: faixa, premiado = "17 Pontos", True
        elif acertos == 16: faixa, premiado = "16 Pontos", True
        elif acertos == 15: faixa, premiado = "15 Pontos", True
        elif acertos == 0: faixa, premiado = "0 Acertos (Especial)", True # Prêmio para 0 acertos
        
    return faixa, premiado


@app.route('/api/main/verificar-jogo-passado', methods=['POST']) # Endpoint unificado
def verificar_jogo_passado_api():
    data = request.get_json()
    if not data or 'lottery' not in data or 'concurso' not in data or 'numeros_usuario' not in data:
        return jsonify({"erro": "Dados incompletos: lottery, concurso e numeros_usuario são obrigatórios."}), 400

    lottery_type_req = data['lottery'].lower()
    if lottery_type_req not in LOTTERY_CONFIG:
        return jsonify({"erro": f"Loteria '{data['lottery']}' não configurada ou inválida."}), 404
    
    config_req = LOTTERY_CONFIG[lottery_type_req]
    nome_exibicao_req = config_req.get("nome_exibicao", lottery_type_req.capitalize())
    expected_numbers_count = config_req.get("count_apostadas", config_req.get("count"))
    min_num_req, max_num_req = config_req.get("min"), config_req.get("max")

    try:
        concurso_solicitado = int(data['concurso'])
        numeros_usuario_input = data['numeros_usuario']
        if not isinstance(numeros_usuario_input, list) or len(numeros_usuario_input) != expected_numbers_count:
             return jsonify({"erro": f"A lista 'numeros_usuario' para {nome_exibicao_req} deve conter {expected_numbers_count} dezenas."}), 400
        
        numeros_usuario = [int(n) for n in numeros_usuario_input] 
        for num_usr in numeros_usuario: 
            if not (min_num_req <= num_usr <= max_num_req):
                return jsonify({"erro": f"Número inválido {num_usr} para {nome_exibicao_req}. Deve ser entre {min_num_req} e {max_num_req}."}), 400
        if len(set(numeros_usuario)) != expected_numbers_count: # Checa duplicatas e contagem de uma vez
            return jsonify({"erro": f"Os números do usuário para {nome_exibicao_req} não devem conter duplicatas e devem ser {expected_numbers_count}."}), 400

    except (ValueError, TypeError) :
        return jsonify({"erro": "Concurso deve ser um inteiro e números do usuário devem ser uma lista de inteiros válidos."}), 400

    all_lottery_results = load_processed_lottery_data(lottery_type_req)
    if not all_lottery_results:
        return jsonify({"erro": f"Dados históricos da {nome_exibicao_req} indisponíveis no momento."}), 503

    sorteio_encontrado_req = None
    for sorteio_hist_req in all_lottery_results:
        # Comparar concurso como string para evitar problemas de tipo int vs str
        if str(sorteio_hist_req.get("concurso")) == str(concurso_solicitado):
            sorteio_encontrado_req = sorteio_hist_req
            break
    
    if not sorteio_encontrado_req:
        return jsonify({"erro": f"Concurso {concurso_solicitado} da {nome_exibicao_req} não encontrado na base de dados."}), 404

    numeros_sorteados_oficial_str_req = sorteio_encontrado_req.get("numeros", [])
    if not numeros_sorteados_oficial_str_req or not isinstance(numeros_sorteados_oficial_str_req, list) :
         return jsonify({"erro": f"Números sorteados não encontrados ou em formato inválido para o concurso {concurso_solicitado} de {nome_exibicao_req}."}), 500
    
    try:
        numeros_sorteados_oficial_req = [int(n) for n in numeros_sorteados_oficial_str_req]
    except ValueError:
        return jsonify({"erro": f"Erro ao processar números sorteados para o concurso {concurso_solicitado} de {nome_exibicao_req}."}), 500

    acertos_req = len(set(numeros_usuario) & set(numeros_sorteados_oficial_req))
    
    faixa_premio_txt_req, premiado_flag_req = determinar_faixa_premio_main(lottery_type_req, acertos_req)
    
    # Lógica para buscar valor do prêmio (exemplo para Mega-Sena, precisa adaptar para outras)
    valor_premio_real = 0.0
    aviso_premio_req = None
    if premiado_flag_req:
        if lottery_type_req == "megasena":
            if acertos_req == 6: key_rateio = config_req.get("rateio_sena_key")
            elif acertos_req == 5: key_rateio = config_req.get("rateio_quina_key")
            elif acertos_req == 4: key_rateio = config_req.get("rateio_quadra_key")
            else: key_rateio = None
            
            if key_rateio and sorteio_encontrado_req.get(key_rateio) is not None:
                valor_premio_real = parse_currency_to_float(sorteio_encontrado_req.get(key_rateio))
            elif key_rateio: # Se a chave existe mas o valor não, informa que não está disponível
                 aviso_premio_req = f"Valor do prêmio da {faixa_premio_txt_req} não disponível na base de dados para este concurso."
        # TODO: Adicionar lógica de busca de rateio para Lotofácil, Quina, Lotomania
        # Exemplo:
        # elif lottery_type_req == "lotofacil":
        #     if acertos_req == 15: key_rateio = "rateio_15_acertos_valor" # Supondo que essa chave existe nos seus dados
        #     # ... outras faixas ...
        #     if key_rateio and sorteio_encontrado_req.get(key_rateio) is not None: ...

    return jsonify({
        "loteria_nome_exibicao": nome_exibicao_req,
        "concurso_verificado": concurso_solicitado,
        "data_sorteio_verificado": sorteio_encontrado_req.get("data", "N/A"),
        "jogo_usuario": sorted(numeros_usuario),
        "numeros_sorteados": sorted(numeros_sorteados_oficial_req),
        "acertos": acertos_req,
        "premiado": premiado_flag_req,
        "faixa_premio": faixa_premio_txt_req,
        "valor_premio_bruto_estimado": valor_premio_real, # Valor numérico
        "valor_premio_formatado_estimado": format_currency(valor_premio_real) if premiado_flag_req and valor_premio_real > 0 else ("Não aplicável" if not aviso_premio_req and premiado_flag_req else "R$ 0,00"),
        "aviso": aviso_premio_req
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
    # Adapte verificar_jogos_salvos_batch_main para ser chamado aqui se necessário
    # result = verificar_jogos_salvos_batch_main() 
    # Por enquanto, vamos simular um sucesso
    result = {"status": "success", "message": "Verificação em lote (simulada) concluída com sucesso."}
    app.logger.info(result["message"])
    if result.get("status") == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Para desenvolvimento local, debug=True é útil. Para produção, debug=False.
    # Vercel ignora app.run, então isso é principalmente para testes locais.
    app.run(host='0.0.0.0', port=port, debug=True)