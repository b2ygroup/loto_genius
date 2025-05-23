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
import pandas as pd

# Importação relativa para o verificador_jogos
from .verificador_jogos import verificar_jogos_salvos_batch, initialize_firebase_admin_verificador as init_fb_verificador_main
from .verificador_jogos import verificar_jogos_para_novo_resultado

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.INFO)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

FB_ADMIN_INITIALIZED = False
db_admin = None
firebase_app_main = None

try:
    MAIN_APP_NAME = 'lotoGeniusApiAppMainPy'
    if MAIN_APP_NAME not in firebase_admin._apps:
        SERVICE_ACCOUNT_KEY_PATH_MAIN = os.path.join(APP_ROOT, "serviceAccountKey.json")
        service_account_json_str_env = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        cred = None
        if service_account_json_str_env:
            service_account_info = json.loads(service_account_json_str_env)
            cred = credentials.Certificate(service_account_info)
            app.logger.info(f"Usando credenciais do Firebase via ENV VAR para {MAIN_APP_NAME}.")
        elif os.path.exists(SERVICE_ACCOUNT_KEY_PATH_MAIN):
            cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH_MAIN)
            app.logger.info(f"Usando credenciais do Firebase via arquivo local para {MAIN_APP_NAME}.")
        
        if cred:
            firebase_app_main = firebase_admin.initialize_app(cred, name=MAIN_APP_NAME)
            app.logger.info(f"Firebase Admin SDK inicializado para {MAIN_APP_NAME} (main.py).")
        else:
            app.logger.error(f"ERRO CRÍTICO [{MAIN_APP_NAME}]: Credenciais do Firebase não encontradas (ENV VAR ou local).")
            
    else: 
        firebase_app_main = firebase_admin.get_app(name=MAIN_APP_NAME)
        app.logger.info(f"Firebase Admin SDK ({MAIN_APP_NAME}) já estava inicializado (main.py). Reutilizando.")

    if firebase_app_main:
        db_admin = admin_firestore.client(app=firebase_app_main)
        FB_ADMIN_INITIALIZED = True
        app.logger.info(f"Cliente Firestore Admin obtido para {MAIN_APP_NAME} (main.py).")
        init_fb_verificador_main(app_name_suffix='VerifViaMain')
    else:
         app.logger.warning(f"Falha ao obter instância da app Firebase {MAIN_APP_NAME}. Cliente Firestore não será configurado.")

except Exception as e_fb_admin_main:
    app.logger.error(f"Erro GERAL ao inicializar Firebase Admin SDK em main.py para {MAIN_APP_NAME}: {e_fb_admin_main}", exc_info=True)

LOTTERY_CONFIG = {
    "megasena": {
        "nome_exibicao": "Mega-Sena", "min": 1, "max": 60, "count": 6, "count_apostadas": 6,
        "color": "#209869", "count_sorteadas": 6, "preco_aposta_base": 5.0,
        "modalidade_param_value": "Mega-Sena",
        "master_file_name_local": "Mega-Sena_Resultados.xlsx",
        "processed_json_name": "megasena_processed_results.json",
        "col_concurso": "Concurso", "col_data_sorteio": "Data do Sorteio",
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 6,
        "col_ganhadores_principal": "Ganhadores 6 acertos", "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 6 acertos", "rateio_sena_key": "rateio_principal_valor",
        "col_rateio_quina": "Rateio 5 acertos", "rateio_quina_key": "rateio_quina_valor",
        "col_rateio_quadra": "Rateio 4 acertos", "rateio_quadra_key": "rateio_quadra_valor"
    },
    "lotofacil": {
        "nome_exibicao": "Lotofácil", "min": 1, "max": 25, "count": 15, "count_apostadas": 15,
        "color": "#930089", "count_sorteadas": 15, "preco_aposta_base": 3.0,
        "modalidade_param_value": "Lotofácil",
        "master_file_name_local": "Lotofácil_Resultados.xlsx",
        "processed_json_name": "lotofacil_processed_results.json",
        "col_concurso": "Concurso", "col_data_sorteio": "Data Sorteio",
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 15,
        "col_ganhadores_principal": "Ganhadores 15 acertos", "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 15 acertos", "rateio_15_key": "rateio_principal_valor",
        "col_rateio_14": "Rateio 14 acertos", "rateio_14_key": "rateio_14_acertos_valor", # Exemplo de nome de coluna no XLSX
        "col_rateio_13": "Rateio 13 acertos", "rateio_13_key": "rateio_13_acertos_valor",
        "col_rateio_12": "Rateio 12 acertos", "rateio_12_key": "rateio_12_acertos_valor",
        "col_rateio_11": "Rateio 11 acertos", "rateio_11_key": "rateio_11_acertos_valor"
    },
    "lotomania": {
        "nome_exibicao": "Lotomania", "min": 0, "max": 99, "count_apostadas": 50,
        "count_sorteadas": 20, "color": "#f78100", "preco_aposta_base": 3.0,
        "modalidade_param_value": "Lotomania",
        "master_file_name_local": "Lotomania_Resultados.xlsx", 
        "processed_json_name": "lotomania_processed_results.json",
        "col_concurso": "Concurso", "col_data_sorteio": "Data Sorteio", 
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 20,
        "col_ganhadores_principal": "Ganhadores 20 acertos", "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 20 acertos", "rateio_20_key": "rateio_principal_valor",
        "col_rateio_0": "Rateio 0 acertos", "rateio_0_key": "rateio_0_acertos_valor" 
    },
    "quina": {
        "nome_exibicao": "Quina", "min": 1, "max": 80, "count": 5, "count_apostadas": 5,
        "color": "#260085", "count_sorteadas": 5, "preco_aposta_base": 2.50,
        "modalidade_param_value": "Quina",
        "master_file_name_local": "Quina_Resultados.xlsx",
        "processed_json_name": "quina_processed_results.json",
        "col_concurso": "Concurso", "col_data_sorteio": "Data Sorteio",
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 5,
        "col_ganhadores_principal": "Ganhadores 5 acertos", "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 5 acertos", "rateio_5_key": "rateio_principal_valor",
        "col_rateio_4": "Rateio 4 acertos", "rateio_4_key": "rateio_4_acertos_valor", 
        "col_rateio_3": "Rateio 3 acertos", "rateio_3_key": "rateio_3_acertos_valor",
        "col_rateio_2": "Rateio 2 acertos", "rateio_2_key": "rateio_2_acertos_valor"
    }
}
TAXA_SERVICO_JOGO_MISTERIOSO = 1.50

PLATFORM_STATS_DOC_REF = None
FICTITIOUS_WINNERS_COL_REF = None
MYSTERY_GAMES_COLLECTION = 'mystery_games'
VERCEL_TMP_DIR = '/tmp' 
DOWNLOAD_URL_BASE_CAIXA = "https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download"

if FB_ADMIN_INITIALIZED and db_admin:
    PLATFORM_STATS_DOC_REF = db_admin.collection('platform_statistics').document('global_metrics')
    FICTITIOUS_WINNERS_COL_REF = db_admin.collection('fictitious_top_winners')
else:
    app.logger.warning("db_admin não está configurado em main.py. PLATFORM_STATS_DOC_REF e FICTITIOUS_WINNERS_COL_REF serão None.")


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
        app.logger.error(f"Firebase Admin (db_admin) não inicializado em main.py. Não é possível buscar URL do Blob para {lottery_key}.")
        return None
    config = LOTTERY_CONFIG.get(lottery_key)
    if not config:
        app.logger.error(f"Configuração não encontrada para {lottery_key} em main.py")
        return None

    app.logger.info(f"Buscando URL do Blob no Firestore para {lottery_key.upper()} (via main.py)...")
    blob_url = None
    try:
        doc_ref = db_admin.collection('lottery_data_source_urls').document(lottery_key)
        doc = doc_ref.get()
        if not doc.exists:
            app.logger.error(f"URL do Blob não encontrado no Firestore para {lottery_key} (main.py).")
            return None
        data_source_info = doc.to_dict()
        blob_url = data_source_info.get('blob_url')
        if not blob_url:
            app.logger.error(f"Campo 'blob_url' não encontrado no Firestore para {lottery_key} (main.py).")
            return None

        app.logger.info(f"Carregando dados de {lottery_key.upper()} do Vercel Blob: {blob_url} (main.py)")
        response = requests.get(blob_url, timeout=20)
        response.raise_for_status()
        data = response.json()
        app.logger.info(f"Sucesso ao carregar {lottery_key.upper()} ({len(data) if isinstance(data, list) else 'N/A'} registros) do Vercel Blob (main.py)")
        return data
    except firebase_exceptions.FirebaseError as fb_err:
        app.logger.error(f"Erro do Firebase ao buscar URL para {lottery_key} (main.py): {fb_err}")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Erro de requisição ao buscar JSON do Blob {(blob_url if blob_url else 'URL_DESCONHECIDO')} (main.py): {e}")
    except Exception as e_gen:
        app.logger.error(f"Erro genérico ao carregar dados de {(blob_url if blob_url else 'URL_DESCONHECIDO')} (main.py): {e_gen}", exc_info=True)
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
    if not PLATFORM_STATS_DOC_REF or not db_admin:
        app.logger.warning("Firestore (PLATFORM_STATS_DOC_REF ou db_admin) não disponível para get_or_create_platform_stats_from_firestore (main.py).")
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
                 ts_val = data['last_fictitious_winner_update_timestamp']
                 if hasattr(ts_val, 'seconds'):
                     data['last_fictitious_winner_update_timestamp'] = datetime.fromtimestamp(ts_val.seconds, tz=timezone.utc)
                 else:
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
            app.logger.info("Documento de estatísticas da plataforma inicializado no Firestore (main.py).")
            initial_stats_for_return = initial_stats.copy()
            initial_stats_for_return['last_fictitious_winner_update_timestamp'] = datetime.now(timezone.utc)
            return initial_stats_for_return
    except firebase_exceptions.FirebaseError as e:
        app.logger.error(f"Erro ao acessar estatísticas no Firestore (main.py): {e}")
        return {
            "total_generated_games": 35000, "total_fictitious_prizes_awarded": 400,
            "total_fictitious_prize_value_bruto": 150000.0,
            "last_fictitious_winner_update_timestamp": datetime.now(timezone.utc) - timedelta(hours=2)
        }

def _simulate_fictitious_win(current_stats_dict):
    global db_admin
    if not FICTITIOUS_WINNERS_COL_REF or not PLATFORM_STATS_DOC_REF or not db_admin:
        app.logger.warning("Firestore (refs ou db_admin) não disponível para simular ganho fictício (main.py).")
        return current_stats_dict

    try:
        is_new_winner = random.random() < 0.70
        winner_nick_base = random.choice(FICTITIOUS_NICKS)
        chosen_lottery = random.choice(list(LOTTERY_CONFIG.keys()))
        prize_value = random.uniform(50.0, 50000.0)
        if random.random() < 0.05:
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
                app.logger.info(f"Atualizando ganhador fictício existente: {winner_data_to_set['nick']} (main.py)")
            else:
                is_new_winner = True

        if is_new_winner:
            winner_data_to_set = {
                "nick": f"{winner_nick_base} #{random.randint(1000,9999)}",
                "total_prize_value_bruto": prize_value,
                "last_win_lottery": chosen_lottery,
                "last_win_date": admin_firestore.SERVER_TIMESTAMP,
                "number_of_wins": 1
            }
            winner_doc_ref = FICTITIOUS_WINNERS_COL_REF.document()
            app.logger.info(f"Criando novo ganhador fictício: {winner_data_to_set['nick']} (main.py)")

        if winner_doc_ref:
            winner_doc_ref.set(winner_data_to_set, merge=True)

        prizes_awarded = current_stats_dict.get("total_fictitious_prizes_awarded", 0) + 1
        prize_value_total = current_stats_dict.get("total_fictitious_prize_value_bruto", 0) + prize_value

        PLATFORM_STATS_DOC_REF.update({
            "total_fictitious_prizes_awarded": prizes_awarded,
            "total_fictitious_prize_value_bruto": prize_value_total,
            "last_fictitious_winner_update_timestamp": admin_firestore.SERVER_TIMESTAMP
        })
        app.logger.info("Estatísticas da plataforma atualizadas com ganho fictício (main.py).")
        current_stats_dict["total_fictitious_prizes_awarded"] = prizes_awarded
        current_stats_dict["total_fictitious_prize_value_bruto"] = prize_value_total
        current_stats_dict["last_fictitious_winner_update_timestamp"] = datetime.now(timezone.utc)

    except firebase_exceptions.FirebaseError as e:
        app.logger.error(f"Erro ao simular ganho fictício no Firestore (main.py): {e}")
    except Exception as e_gen_fict:
        app.logger.error(f"Erro genérico ao simular ganho fictício (main.py): {e_gen_fict}", exc_info=True)

    return current_stats_dict

def parse_ganhadores_cidades_cron(cidade_uf_str, num_ganhadores_str):
    cidades_parsed = []
    try:
        num_ganhadores_cleaned = str(num_ganhadores_str).strip()
        if num_ganhadores_cleaned.lower() == 'nan': num_ganhadores = 0
        elif num_ganhadores_cleaned.isdigit(): num_ganhadores = int(num_ganhadores_cleaned)
        else: num_ganhadores = 0
    except ValueError: num_ganhadores = 0

    if num_ganhadores > 0 and isinstance(cidade_uf_str, str) and \
       cidade_uf_str.strip() and cidade_uf_str.strip() != "-" and \
       cidade_uf_str.lower() != 'nan':
        temp_str = re.sub(r'\s*\(\s*(\d+)\s*\)\s*', r'(\1)', cidade_uf_str)
        if ";" in temp_str: entries = [entry.strip() for entry in temp_str.split(';')]
        else: entries = [entry.strip() for entry in temp_str.split(',')]
        
        parsed_from_entries = []
        for entry in entries:
            if not entry: continue
            match_contagem = re.search(r'\((?P<contagem>\d+)\)$', entry)
            contagem_na_string = 1; cidade_limpa = entry
            if match_contagem:
                contagem_na_string = int(match_contagem.group("contagem"))
                cidade_limpa = re.sub(r'\s*\(\d+\)$', '', entry).strip()
            if cidade_limpa: parsed_from_entries.extend([cidade_limpa] * contagem_na_string)
        
        cidades_parsed = [c for c in parsed_from_entries if c]
        
        if num_ganhadores > 0:
            if not cidades_parsed: cidades_parsed = ["Não especificada"] * num_ganhadores
            elif len(cidades_parsed) < num_ganhadores:
                if len(cidades_parsed) == 1: cidades_parsed = [cidades_parsed[0]] * num_ganhadores
                else: cidades_parsed.extend(["Não especificada"] * (num_ganhadores - len(cidades_parsed)))
            elif len(cidades_parsed) > num_ganhadores: cidades_parsed = cidades_parsed[:num_ganhadores]
    elif num_ganhadores > 0: cidades_parsed = ["Não especificada"] * num_ganhadores
    return cidades_parsed, num_ganhadores


def baixar_arquivo_loteria_para_vercel(loteria_key_func, config_loteria_func):
    modalidade_valor = config_loteria_func.get("modalidade_param_value", config_loteria_func.get("nome_exibicao"))
    nome_arquivo_base = config_loteria_func.get("master_file_name_local")
    
    if not modalidade_valor or not nome_arquivo_base:
        app.logger.error(f"CRON ERRO [{loteria_key_func.upper()}]: Configuração de download incompleta (modalidade ou nome base).")
        return None

    caminho_completo_destino = os.path.join(VERCEL_TMP_DIR, nome_arquivo_base)
    
    params = {'modalidade': modalidade_valor}
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://loterias.caixa.gov.br/'
    })
    try:
        app.logger.info(f"CRON Baixando arquivo para {loteria_key_func.upper()} de {DOWNLOAD_URL_BASE_CAIXA} com params {params} para {caminho_completo_destino}...")
        response = session.get(DOWNLOAD_URL_BASE_CAIXA, params=params, stream=True, timeout=60, allow_redirects=True)
        response.raise_for_status()
        with open(caminho_completo_destino, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): f.write(chunk)
        app.logger.info(f"CRON SUCESSO [{loteria_key_func.upper()}]: Arquivo salvo em {caminho_completo_destino}")
        return caminho_completo_destino
    except requests.exceptions.RequestException as e:
        app.logger.error(f"CRON ERRO ao baixar para {loteria_key_func.upper()}: {e}")
    return None

def upload_json_to_vercel_blob_cron(pathname_in_blob, json_content_str, loteria_key_func):
    BLOB_ACCESS_TOKEN_CRON = os.environ.get("BLOB_READ_WRITE_TOKEN")
    if not BLOB_ACCESS_TOKEN_CRON:
        app.logger.error(f"CRON ERRO CRÍTICO [{loteria_key_func.upper()}]: BLOB_READ_WRITE_TOKEN não configurado.")
        return None
        
    upload_url = f"https://blob.vercel-storage.com/{pathname_in_blob}"
    headers = {
        "Authorization": f"Bearer {BLOB_ACCESS_TOKEN_CRON}",
        "Content-Type": "application/json; charset=utf-8",
        "x-api-version": "6" 
    }
    app.logger.info(f"CRON Fazendo upload de '{pathname_in_blob}' para Vercel Blob...")
    try:
        response = requests.put(upload_url, headers=headers, data=json_content_str.encode('utf-8'), timeout=30)
        response.raise_for_status()
        blob_data = response.json()
        blob_access_url = blob_data.get('url') 
        app.logger.info(f"CRON SUCESSO [{loteria_key_func.upper()}]: JSON enviado para Vercel Blob. URL: {blob_access_url}")
        return blob_access_url
    except requests.exceptions.HTTPError as http_err:
        app.logger.error(f"CRON ERRO HTTP ao enviar JSON para Vercel Blob ({loteria_key_func.upper()}): {http_err} - {http_err.response.text if http_err.response else ''}")
    except requests.exceptions.RequestException as e_blob:
        app.logger.error(f"CRON ERRO de requisição ao enviar JSON para Vercel Blob ({loteria_key_func.upper()}): {e_blob}")
    except Exception as e_gen_blob:
        app.logger.error(f"CRON Erro genérico ao enviar para Vercel Blob ({loteria_key_func.upper()}): {e_gen_blob}")
    return None

def processar_loteria_para_cron(loteria_key_func, config_loteria_func, tentar_download=True):
    global db_admin 
    if not db_admin:
        app.logger.error(f"CRON ERRO [{loteria_key_func.upper()}]: Cliente Firestore (db_admin) não está disponível.")
        return

    app.logger.info(f"CRON Iniciando processamento JSON para {loteria_key_func.upper()}")
    json_file_name_for_blob = config_loteria_func["processed_json_name"]
    df = None
    filepath_to_read = None

    if tentar_download:
        filepath_to_read = baixar_arquivo_loteria_para_vercel(loteria_key_func, config_loteria_func)
    
    if filepath_to_read and os.path.exists(filepath_to_read):
        try: 
            df = pd.read_excel(filepath_to_read, engine='openpyxl', dtype=str, na_values=['-'], keep_default_na=True)
            app.logger.info(f"CRON SUCESSO [{loteria_key_func.upper()}]: Arquivo {filepath_to_read} lido com pandas.")
        except Exception as e_read: 
            app.logger.error(f"CRON ERRO ao ler arquivo {filepath_to_read} para {loteria_key_func.upper()}: {e_read}")
            if os.path.exists(filepath_to_read) and VERCEL_TMP_DIR in filepath_to_read: os.remove(filepath_to_read)
            return
    elif tentar_download:
        app.logger.warning(f"CRON AVISO: Falha no download ou arquivo não encontrado para {loteria_key_func.upper()} após tentativa de download.")
        return
    else:
        app.logger.info(f"CRON [{loteria_key_func.upper()}]: Download não solicitado e nenhum arquivo encontrado.")
        return


    if df is None or df.empty: 
        app.logger.warning(f"CRON AVISO FINAL: DataFrame não carregado ou vazio para {loteria_key_func.upper()}.")
        if filepath_to_read and os.path.exists(filepath_to_read) and VERCEL_TMP_DIR in filepath_to_read: os.remove(filepath_to_read)
        return

    col_concurso = config_loteria_func["col_concurso"]
    col_data = config_loteria_func["col_data_sorteio"]
    cols_bolas_prefix = config_loteria_func["cols_bolas_prefix"]
    num_bolas_a_ler = config_loteria_func["num_bolas_no_arquivo"]
    col_ganhadores_principal = config_loteria_func.get("col_ganhadores_principal")
    col_cidade_uf_principal = config_loteria_func.get("col_cidade_uf_principal")
    col_rateio_principal = config_loteria_func.get("col_rateio_principal")
    
    col_rateio_quina_ms = config_loteria_func.get("col_rateio_quina")
    col_rateio_quadra_ms = config_loteria_func.get("col_rateio_quadra")

    results_list = []

    for index, row in df.iterrows():
        try:
            concurso_str = str(row.get(col_concurso, '')).strip()
            data_str = str(row.get(col_data, '')).strip()
            concurso_str_cleaned = concurso_str.replace(',', '')
            if pd.isna(concurso_str_cleaned) or not concurso_str_cleaned or concurso_str_cleaned.lower() == 'nan' or concurso_str_cleaned == '-': continue
            try: concurso_val = int(float(concurso_str_cleaned))
            except ValueError: continue
            if pd.isna(data_str) or not data_str or data_str.lower() == 'nan' or data_str == '-': continue
            data_formatada = data_str
            try: 
                dt_obj = pd.to_datetime(data_str, errors='coerce', dayfirst=True)
                data_formatada = dt_obj.strftime('%d/%m/%Y') if pd.notna(dt_obj) else data_str
            except Exception: pass
            
            dezenas_lidas = []
            for i in range(1, num_bolas_a_ler + 1):
                dezena_val_str = str(row.get(f'{cols_bolas_prefix}{i}', '')).strip()
                if dezena_val_str.isdigit(): 
                    dezenas_lidas.append(int(dezena_val_str))
            
            if len(dezenas_lidas) == num_bolas_a_ler:
                sorteio_data = {"concurso": concurso_val, "data": data_formatada, "numeros": sorted(dezenas_lidas)}
                if col_ganhadores_principal and col_cidade_uf_principal and col_rateio_principal:
                    ganhadores_val = row.get(col_ganhadores_principal, '0'); cidade_uf_val = row.get(col_cidade_uf_principal, '')
                    rateio_val_str = row.get(col_rateio_principal, '0')
                    cidades_lista, num_ganhadores_parsed = parse_ganhadores_cidades_cron(str(cidade_uf_val), str(ganhadores_val))
                    
                    sorteio_data["ganhadores_principal_contagem"] = num_ganhadores_parsed
                    sorteio_data["cidades_ganhadoras_principal"] = cidades_lista
                    sorteio_data["rateio_principal_valor"] = format_currency(parse_currency_to_float(str(rateio_val_str))) if num_ganhadores_parsed > 0 else "R$ 0,00"

                    if loteria_key_func == 'megasena':
                        if col_rateio_quina_ms and config_loteria_func.get("rateio_quina_key"): 
                            rateio_quina_val_str = row.get(col_rateio_quina_ms, '0')
                            sorteio_data[config_loteria_func["rateio_quina_key"]] = format_currency(parse_currency_to_float(str(rateio_quina_val_str)))
                        if col_rateio_quadra_ms and config_loteria_func.get("rateio_quadra_key"):
                            rateio_quadra_val_str = row.get(col_rateio_quadra_ms, '0')
                            sorteio_data[config_loteria_func["rateio_quadra_key"]] = format_currency(parse_currency_to_float(str(rateio_quadra_val_str)))
                    elif loteria_key_func == 'lotofacil':
                        faixas_lotofacil_cols = { 
                            "rateio_14_key": config_loteria_func.get("col_rateio_14", "Rateio 14 acertos"),
                            "rateio_13_key": config_loteria_func.get("col_rateio_13", "Rateio 13 acertos"),
                            "rateio_12_key": config_loteria_func.get("col_rateio_12", "Rateio 12 acertos"),
                            "rateio_11_key": config_loteria_func.get("col_rateio_11", "Rateio 11 acertos")
                        }
                        for config_key_lf, column_name_lf in faixas_lotofacil_cols.items():
                            json_data_key_lf = LOTTERY_CONFIG[loteria_key_func].get(config_key_lf)
                            if json_data_key_lf and row.get(column_name_lf) is not None:
                                rateio_str_val_lf = row.get(column_name_lf, '0')
                                sorteio_data[json_data_key_lf] = format_currency(parse_currency_to_float(str(rateio_str_val_lf)))
                
                results_list.append(sorteio_data)
        except Exception as e_row: 
            app.logger.error(f"CRON ERRO ao processar linha {index+1} ({loteria_key_func.upper()}): {e_row}")
    
    if results_list:
        results_list.sort(key=lambda x: x["concurso"], reverse=True)
        json_content_to_upload = json.dumps(results_list, ensure_ascii=False, separators=(',', ':'))
        
        blob_url_retornado = upload_json_to_vercel_blob_cron(json_file_name_for_blob, json_content_to_upload, loteria_key_func)
        
        if blob_url_retornado and db_admin:
            try:
                doc_ref = db_admin.collection('lottery_data_source_urls').document(loteria_key_func)
                doc_ref.set({
                    'lottery_name': loteria_key_func,
                    'blob_url': blob_url_retornado,
                    'updated_at': admin_firestore.SERVER_TIMESTAMP,
                    'latest_contest_number': results_list[0]['concurso'] if results_list else None
                }, merge=True)
                app.logger.info(f"CRON URL do Blob para {loteria_key_func.upper()} salvo no Firestore.")
                
                if results_list: 
                    novo_resultado_oficial_para_verificar = results_list[0]
                    app.logger.info(f"CRON Disparando verificação de jogos para {loteria_key_func.upper()}, concurso {novo_resultado_oficial_para_verificar.get('concurso')}")
                    verificar_jogos_para_novo_resultado(loteria_key_func, novo_resultado_oficial_para_verificar, db_client=db_admin)

            except Exception as e_firestore_cron:
                app.logger.error(f"CRON ERRO ao salvar URL do Blob ou ao chamar verificação para {loteria_key_func.upper()}: {e_firestore_cron}")

        elif not blob_url_retornado:
            app.logger.error(f"CRON FALHA NO UPLOAD [{loteria_key_func.upper()}]: JSON não foi para o Blob.")
    else:
        app.logger.warning(f"CRON AVISO FINAL [{loteria_key_func.upper()}]: Nenhum resultado válido processado.")

    if filepath_to_read and os.path.exists(filepath_to_read) and VERCEL_TMP_DIR in filepath_to_read:
        try:
            os.remove(filepath_to_read)
            app.logger.info(f"CRON Arquivo temporário {filepath_to_read} removido.")
        except OSError as e_remove:
            app.logger.error(f"CRON Erro ao remover arquivo temporário {filepath_to_read}: {e_remove}")

@app.route('/api/cron/processar-loterias', methods=['POST','GET']) 
def cron_processar_loterias_endpoint():
    configured_cron_secret = os.environ.get('CRON_SECRET') 
    auth_header = request.headers.get('Authorization')
    bearer_token = None
    if auth_header and auth_header.startswith('Bearer '):
        bearer_token = auth_header.split(' ')[1]

    is_authorized = False
    if request.method == 'GET' and not configured_cron_secret:
        is_authorized = True
        app.logger.info("CRON: Acesso GET local permitido (CRON_SECRET não configurado no ambiente).")
    elif configured_cron_secret and bearer_token == configured_cron_secret:
        is_authorized = True
    elif request.method == 'POST': 
        if not configured_cron_secret:
             app.logger.error("CRON: POST não autorizado - CRON_SECRET não configurado no ambiente!")
             return jsonify({"error": "Configuração de segurança do servidor ausente"}), 500
        if not bearer_token or bearer_token != configured_cron_secret:
            app.logger.warning(f"CRON: POST não autorizado - Header 'Authorization' Bearer token inválido ou ausente. Recebido: {auth_header}")
            return jsonify({"error": "Não autorizado"}), 401
            
    if not is_authorized:
        app.logger.warning(f"CRON: Falha final na autorização do endpoint. Header 'Authorization': {auth_header}. ENV 'CRON_SECRET': {'Definido' if configured_cron_secret else 'Não definido'}")
        return jsonify({"error": "Não autorizado"}), 401
            
    app.logger.info("CRON: Endpoint /api/cron/processar-loterias acionado com sucesso e autorizado.")
    
    if not FB_ADMIN_INITIALIZED or not db_admin:
        app.logger.error("CRON ERRO FATAL: Firebase (db_admin) não inicializado em main.py. Processamento não pode continuar.")
        return jsonify({"status": "erro_fatal", "mensagem": "Configuração interna do servidor (Firebase) incompleta."}), 500
        
    try:
        loterias_a_processar = list(LOTTERY_CONFIG.keys()) 
        tentar_download_cron = True 
        resultados_finais_processamento = {}

        for loteria_key in loterias_a_processar:
            config_atual_loteria = LOTTERY_CONFIG.get(loteria_key)
            if not config_atual_loteria:
                app.logger.error(f"CRON: Configuração para loteria '{loteria_key}' não encontrada.")
                resultados_finais_processamento[loteria_key] = "erro_configuracao"
                continue
            
            app.logger.info(f"CRON: Iniciando processamento para {loteria_key.upper()}.")
            processar_loteria_para_cron(loteria_key, config_atual_loteria, tentar_download_cron)
            resultados_finais_processamento[loteria_key] = "processamento_concluido_com_verificacao_disparada"

        app.logger.info("CRON: Processamento de todas as loterias agendadas concluído.")
        return jsonify({"status": "sucesso_geral", "detalhes_por_loteria": resultados_finais_processamento}), 200
    except Exception as e_cron:
        app.logger.error(f"CRON: Erro geral ao processar loterias: {e_cron}", exc_info=True)
        return jsonify({"status": "erro_geral_cron", "mensagem": str(e_cron)}), 500


# --- ROTAS EXISTENTES DA API ---
@app.route('/')
def api_base_root_main():
    return jsonify({"message": "API Loto Genius Python (api/main.py).", "note": "Endpoints em /api/..." })

@app.route('/api/') 
def api_home_vercel_main():
    return jsonify({"message": "API Loto Genius Python (api/main.py).", "note": "Endpoints em /api/main/..."})

@app.route('/api/main/')
def api_main_home_main():
    return jsonify({"mensagem": "API Loto Genius AI Refatorada!", "versao": "5.0.0 - Cron Job Vercel e Lotomania XLSX"})

@app.route('/api/main/platform-stats', methods=['GET'])
def get_platform_stats_persistent():
    if not FB_ADMIN_INITIALIZED or not PLATFORM_STATS_DOC_REF or not db_admin:
        app.logger.warning("Firestore não inicializado ou refs não disponíveis, usando estatísticas em memória para /platform-stats (main.py).")
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
        app.logger.error(f"Erro ao atualizar total_generated_games no Firestore (main.py): {e}")

    should_simulate_win = False
    if random.random() < 0.15: 
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
    if not FB_ADMIN_INITIALIZED or not FICTITIOUS_WINNERS_COL_REF or not db_admin:
        app.logger.warning("Firestore não inicializado ou refs não disponíveis, usando ganhadores fallback para /top-winners (main.py).")
        winners_fallback = [{"nick": "Sortudo Virtual #777", "prize_total": format_currency(random.uniform(100000, 500000)), "lottery": "Mega-Sena", "date": "23/05/2025"}]
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
            elif hasattr(win_date_obj, 'seconds'): 
                date_str = datetime.fromtimestamp(win_date_obj.seconds, tz=timezone.utc).strftime("%d/%m/%Y")
            
            winners_list.append({
                "nick": winner_data.get("nick", "Anônimo da Sorte"),
                "prize_total": format_currency(winner_data.get("total_prize_value_bruto", 0)),
                "lottery": LOTTERY_CONFIG.get(winner_data.get("last_win_lottery", ""), {}).get("nome_exibicao", "Diversas"),
                "date": date_str
            })
        
        if not winners_list and FICTITIOUS_WINNERS_COL_REF: 
            app.logger.info("Lista de Top Winners vazia, adicionando alguns ganhadores iniciais... (main.py)")
            initial_stats_dict = get_or_create_platform_stats_from_firestore() 
            for _ in range(random.randint(3,5)): 
                initial_stats_dict = _simulate_fictitious_win(initial_stats_dict) 
            
            winners_query_retry = FICTITIOUS_WINNERS_COL_REF.order_by("total_prize_value_bruto", direction=admin_firestore.Query.DESCENDING).limit(10).stream()
            for winner_doc_retry in winners_query_retry: 
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
        app.logger.error(f"Erro ao buscar top winners do Firestore (main.py): {e}")
        return jsonify({"error": "Não foi possível buscar os top winners"}), 500
    except Exception as e_gen_tw:
        app.logger.error(f"Erro genérico ao buscar top winners (main.py): {e_gen_tw}", exc_info=True)
        return jsonify({"error": "Erro interno ao buscar top winners"}), 500

@app.route('/api/main/resultados/<lottery_name>', methods=['GET'])
def get_resultados_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results = load_processed_lottery_data(lottery_name_lower)
    if not all_results: return jsonify({"aviso": f"Dados para {lottery_name.upper()} indisponíveis no momento."}), 404
    if not isinstance(all_results, list) or not all_results:
        return jsonify({"erro": f"Formato de dados inesperado para {lottery_name.upper()}."}), 500
    latest_result = all_results[0] 
    return jsonify({
        "ultimo_concurso": latest_result.get("concurso"),
        "data": latest_result.get("data"),
        "numeros": latest_result.get("numeros"),
        "ganhadores_principal_contagem": latest_result.get("ganhadores_principal_contagem"),
        "cidades_ganhadoras_principal": latest_result.get("cidades_ganhadoras_principal"),
        "rateio_principal_valor": latest_result.get("rateio_principal_valor"), 
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
        except ValueError: pass 
    
    if not todos_numeros: return jsonify({"data": [], "mensagem": "Nenhum número válido nos dados."}), 200
    
    contagem = Counter(todos_numeros)
    frequencia_ordenada = sorted(contagem.items(), key=lambda item: (-item[1], item[0])) 
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
                if len(numeros_int_list) == numeros_por_sorteio: 
                     for par in combinations(numeros_int_list, 2): 
                        todos_os_itens_combinacao.append(tuple(par)) 
            except ValueError:
                continue 

    if not todos_os_itens_combinacao: return jsonify({"data": [], "mensagem": "Não foi possível gerar pares."}), 200
    
    contagem_itens = Counter(todos_os_itens_combinacao)
    itens_ordenados = sorted(contagem_itens.items(), key=lambda item: (-item[1], item[0])) 
    itens_formatados = [{"par": [str(n).zfill(2) for n in item_numeros], "frequencia": freq} for item_numeros, freq in itens_ordenados]
    return jsonify({"data": itens_formatados[:30]})


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
        if isinstance(cidades, list): 
            cidades_validas = [c.strip() for c in cidades if c and isinstance(c, str) and c.strip().lower() not in ["", "não especificada", "-", "nao especificada"]]
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
        rateio_bruto_str = sorteio.get("rateio_principal_valor", "0.0") 
        rateio_float = parse_currency_to_float(rateio_bruto_str) 
        
        num_ganhadores_no_sorteio = sorteio.get("ganhadores_principal_contagem", 0)
        
        if rateio_float > 0 and isinstance(cidades, list) and cidades and num_ganhadores_no_sorteio > 0:
            cidades_validas = [c.strip() for c in cidades if c and isinstance(c, str) and c.strip().lower() not in ["", "não especificada", "-", "nao especificada"]]
            for cidade_unica in set(cidades_validas): 
                ocorrencias_cidade_no_sorteio = cidades_validas.count(cidade_unica)
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
    num_sorteados_premio_max = config.get('count_sorteadas', config.get('count')) 
    num_marcados_volante_config = config.get('count_apostadas', config.get('count')) 

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
    
    num_marcados_pelo_usuario = len(numeros_usuario)
    prob_dec = 0.0
    prob_txt = "Não aplicável para esta configuração."
    descricao_prob = ""

    if lottery_type == "lotomania":
        if num_marcados_pelo_usuario == 50:
            combinacoes_totais = combinations_count(universo_total, num_sorteados_premio_max) 
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
    else: 
        if num_marcados_pelo_usuario == num_sorteados_premio_max:
            combinacoes_totais = combinations_count(universo_total, num_sorteados_premio_max)
            if combinacoes_totais > 0:
                prob_dec = 1 / combinacoes_totais
                prob_txt = f"1 em {int(combinacoes_totais):,}".replace(',', '.')
            else:
                prob_txt = "Cálculo de combinações resultou em zero."
            descricao_prob = f"Probabilidade de acertar o prêmio máximo ({num_sorteados_premio_max} acertos) com um jogo simples de {num_marcados_pelo_usuario} números."
        elif num_marcados_pelo_usuario > num_sorteados_premio_max and num_marcados_pelo_usuario <= config.get('max_numeros_aposta', num_marcados_volante_config) : 
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

def gerar_jogo_ia_aleatorio_rapido(lottery_name):
    config = LOTTERY_CONFIG.get(lottery_name)
    if not config: 
        app.logger.error(f"Configuração de loteria não encontrada para '{lottery_name}' em gerar_jogo_ia_aleatorio_rapido (main.py).")
        return {"jogo": [], "estrategia_usada": "Erro: Loteria não configurada"}
    
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    min_num, max_num = config["min"], config["max"]
    
    if (max_num - min_num + 1) < numeros_a_gerar: 
        app.logger.error(f"Erro Aleatório Rápido para {lottery_name}: range ({min_num}-{max_num}) insuficiente para gerar {numeros_a_gerar} números (main.py).")
        return {"jogo": [], "estrategia_usada": f"Erro Config (range {max_num - min_num + 1} < {numeros_a_gerar})"}
    
    try:
        jogo_final = sorted(random.sample(range(min_num, max_num + 1), numeros_a_gerar))
    except ValueError as e_sample: 
        app.logger.error(f"Erro no random.sample para {lottery_name} (range {min_num}-{max_num}, gerar {numeros_a_gerar}): {e_sample} (main.py)")
        return {"jogo": [], "estrategia_usada": "Erro Interno na Geração Aleatória (sample)"}

    if len(jogo_final) != numeros_a_gerar: 
        app.logger.error(f"Falha crítica no Aleatório Rápido para {lottery_name}. Esperado {numeros_a_gerar}, obtido {len(jogo_final)} (main.py).")
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
        app.logger.error(f"API /gerar_jogo: Falha ao gerar jogo para {lottery_name}. Esperado: {expected_count}, Recebido: {len(resultado_geracao.get('jogo', []))}. Detalhes: {resultado_geracao.get('estrategia_usada', 'Falha interna')} (main.py)")
        try:
            jogo_fallback_extremo = sorted(random.sample(range(config["min"], config["max"] + 1), expected_count))
            app.logger.info(f"Fallback extremo para /gerar_jogo {lottery_name} gerou: {jogo_fallback_extremo} (main.py)")
            return jsonify({"jogo": jogo_fallback_extremo, "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório (Fallback Crítico)", "aviso": "Usado fallback crítico."})
        except Exception as e_fallback:
            app.logger.error(f"Falha no fallback extremo para /gerar_jogo {lottery_name}: {e_fallback} (main.py)")
            return jsonify({"erro": f"Não foi possível gerar jogo para {lottery_name} mesmo com fallback.", "detalhes": resultado_geracao.get("estrategia_usada", "Falha interna na geração")}), 500

    if resultado_geracao.get("jogo") and PLATFORM_STATS_DOC_REF: 
        try:
            PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats:
            app.logger.error(f"Erro ao incrementar total_generated_games (aleatório, main.py): {e_stats}")
    return jsonify(resultado_geracao)

def get_hot_numbers_strategy(all_results, num_concursos_analisar, num_numeros_gerar, lottery_min, lottery_max, lottery_name_for_log=""):
    if not all_results: 
        app.logger.warning(f"HotNumbers para {lottery_name_for_log}: Sem resultados históricos, usando aleatório (main.py).")
        return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    recent_results = all_results[:num_concursos_analisar]
    if not recent_results: 
        recent_results = all_results
        if not recent_results: 
             app.logger.warning(f"HotNumbers para {lottery_name_for_log}: Lista de resultados recentes vazia, usando aleatório (main.py).")
             return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    all_drawn_numbers_in_slice_raw = [num_str for result in recent_results if "numeros" in result and isinstance(result["numeros"], list) for num_str in result["numeros"]]
    all_drawn_numbers_in_slice = []
    for n_str in all_drawn_numbers_in_slice_raw:
        try: all_drawn_numbers_in_slice.append(int(n_str))
        except ValueError: pass

    if not all_drawn_numbers_in_slice: 
        app.logger.warning(f"HotNumbers para {lottery_name_for_log}: Nenhum número válido na fatia de resultados, usando aleatório (main.py).")
        return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    number_counts = Counter(all_drawn_numbers_in_slice)
    hot_numbers_sorted_by_freq = sorted(number_counts.items(), key=lambda item: (-item[1], item[0])) 
    
    generated_game = [num for num, count in hot_numbers_sorted_by_freq[:num_numeros_gerar]] 
    
    if len(generated_game) < num_numeros_gerar:
        app.logger.info(f"HotNumbers para {lottery_name_for_log}: Completando com números aleatórios (main.py).")
        possible_numbers_pool = list(range(lottery_min, lottery_max + 1))
        complementar_needed = num_numeros_gerar - len(generated_game)
        
        pool_complementar = [num for num in possible_numbers_pool if num not in generated_game]
        random.shuffle(pool_complementar)
        generated_game.extend(pool_complementar[:complementar_needed])
        generated_game = list(set(generated_game)) 

    if len(generated_game) != num_numeros_gerar:
        app.logger.warning(f"HotNumbers para {lottery_name_for_log}: Contagem final incorreta ({len(generated_game)} de {num_numeros_gerar}). Ajustando (main.py).")
        if len(generated_game) > num_numeros_gerar:
            return sorted(random.sample(generated_game, num_numeros_gerar)) 
        else: 
            current_game_set = set(generated_game)
            possible_fillers = [n for n in range(lottery_min, lottery_max + 1) if n not in current_game_set]
            random.shuffle(possible_fillers)
            needed_to_fill = num_numeros_gerar - len(generated_game)
            generated_game.extend(possible_fillers[:needed_to_fill])
            if len(generated_game) != num_numeros_gerar:
                 app.logger.error(f"HotNumbers para {lottery_name_for_log}: Falha crítica no ajuste de contagem. Usando aleatório total (main.py).")
                 return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))

    return sorted(generated_game)


@app.route('/api/main/gerar_jogo/numeros_quentes/<lottery_name>', methods=['GET'])
def gerar_jogo_numeros_quentes_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404
    
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: 
        app.logger.warning(f"Números Quentes para {lottery_name}: Dados históricos indisponíveis. Usando fallback aleatório (main.py).")
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({
            "jogo": fallback_result.get("jogo", []), 
            "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Quentes (Fallback Aleatório - Sem Histórico)",
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
    
    jogo_final = get_hot_numbers_strategy(all_results, num_concursos_analisar, numeros_a_gerar, lottery_min, lottery_max, lottery_name_lower)
    
    if not jogo_final or len(jogo_final) != numeros_a_gerar:
        app.logger.warning(f"Números Quentes API para {lottery_name}: Jogo final não corresponde. Esperado: {numeros_a_gerar}, Obtido: {len(jogo_final)}. Usando fallback aleatório (main.py).")
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({
            "jogo": fallback_result.get("jogo", []), 
            "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Quentes (Fallback Aleatório Interno)", 
            "aviso": "Estratégia Quente não produziu resultado esperado, usando fallback aleatório."
        }), 200
    
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Quentes ({num_concursos_analisar} últimos concursos)"
    if PLATFORM_STATS_DOC_REF:
        try: PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats: app.logger.error(f"Erro ao incrementar total_generated_games (quentes, main.py): {e_stats}")
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

def get_cold_numbers_strategy(all_results, num_concursos_analisar, num_numeros_gerar, lottery_min, lottery_max, lottery_name_for_log=""):
    if not all_results:
        app.logger.warning(f"ColdNumbers para {lottery_name_for_log}: Sem resultados históricos, usando aleatório (main.py).")
        return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))

    recent_results_slice = all_results[:num_concursos_analisar]
    if not recent_results_slice:
        app.logger.warning(f"ColdNumbers para {lottery_name_for_log}: Fatia de resultados recentes vazia, usando aleatório (main.py).")
        return sorted(random.sample(range(lottery_min, lottery_max + 1), num_numeros_gerar))
    
    drawn_numbers_in_slice_raw = [num_str for result in recent_results_slice if "numeros" in result and isinstance(result["numeros"], list) for num_str in result["numeros"]]
    drawn_numbers_in_slice = []
    for n_str in drawn_numbers_in_slice_raw:
        try: drawn_numbers_in_slice.append(int(n_str))
        except ValueError: pass

    frequency_counts = Counter(drawn_numbers_in_slice)
    all_possible_numbers_in_range = list(range(lottery_min, lottery_max + 1))
    
    cold_numbers_candidates = [{'numero': num, 'frequencia': frequency_counts.get(num, 0)} for num in all_possible_numbers_in_range]
    cold_numbers_candidates_sorted = sorted(cold_numbers_candidates, key=lambda x: (x['frequencia'], x['numero']))
    
    final_cold_selection = [candidate['numero'] for candidate in cold_numbers_candidates_sorted[:num_numeros_gerar]]
    
    if len(final_cold_selection) < num_numeros_gerar:
        app.logger.info(f"ColdNumbers para {lottery_name_for_log}: Completando com números aleatórios (main.py).")
        remaining_possible = [num['numero'] for num in cold_numbers_candidates_sorted[num_numeros_gerar:]]
        random.shuffle(remaining_possible)
        final_cold_selection.extend(remaining_possible[:num_numeros_gerar - len(final_cold_selection)])
        final_cold_selection = list(set(final_cold_selection)) 

    if len(final_cold_selection) != num_numeros_gerar:
        app.logger.warning(f"ColdNumbers para {lottery_name_for_log}: Contagem final incorreta ({len(final_cold_selection)} de {num_numeros_gerar}). Ajustando (main.py).")
        if len(final_cold_selection) > num_numeros_gerar:
            return sorted(random.sample(final_cold_selection, num_numeros_gerar))
        else:
            current_selection_set = set(final_cold_selection)
            possible_fillers = [n for n in all_possible_numbers_in_range if n not in current_selection_set]
            random.shuffle(possible_fillers)
            needed_to_fill = num_numeros_gerar - len(final_cold_selection)
            final_cold_selection.extend(possible_fillers[:needed_to_fill])
            if len(final_cold_selection) != num_numeros_gerar:
                app.logger.error(f"ColdNumbers para {lottery_name_for_log}: Falha crítica no ajuste de contagem. Usando aleatório total (main.py).")
                return sorted(random.sample(all_possible_numbers_in_range, num_numeros_gerar))
                
    return sorted(final_cold_selection)


@app.route('/api/main/gerar_jogo/numeros_frios/<lottery_name>', methods=['GET'])
def gerar_jogo_numeros_frios_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404

    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: 
        app.logger.warning(f"Números Frios para {lottery_name}: Dados históricos indisponíveis. Usando fallback aleatório (main.py).")
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
        app.logger.warning(f"Números Frios API para {lottery_name}: Jogo final não corresponde. Esperado: {numeros_a_gerar}, Obtido: {len(jogo_final)}. Usando fallback aleatório (main.py).")
        fallback_result = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower)
        return jsonify({
            "jogo": fallback_result.get("jogo", []), 
            "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Frios (Fallback Aleatório Interno)", 
            "aviso": "Estratégia Fria não produziu resultado esperado, usando fallback aleatório."
        }), 200
    
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Números Frios ({num_concursos_analisar} últimos concursos)"
    if PLATFORM_STATS_DOC_REF:
        try: PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats: app.logger.error(f"Erro ao incrementar total_generated_games (frios, main.py): {e_stats}")
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})

def gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_numeros_gerar, min_val, max_val, lottery_name_for_log=""):
    app.logger.info(f"Gerando palpite esotérico simples com data: {data_nascimento_str} para {lottery_name_for_log} ({num_numeros_gerar} números entre {min_val}-{max_val}) (main.py)")
    numeros_base = set()
    soma_total_digitos = 0
    
    if data_nascimento_str and isinstance(data_nascimento_str, str):
        for digito in data_nascimento_str:
            if digito.isdigit(): 
                soma_total_digitos += int(digito)
    
    app.logger.info(f"Soma inicial dos dígitos para {lottery_name_for_log}: {soma_total_digitos} (main.py)")
    soma_reduzida = soma_total_digitos
    while soma_reduzida > 9 and soma_reduzida not in [11, 22, 33]: 
        soma_anterior_temp = soma_reduzida
        soma_reduzida = sum(int(d) for d in str(soma_reduzida))
        app.logger.info(f"Redução numerológica para {lottery_name_for_log}: {soma_anterior_temp} -> {soma_reduzida} (main.py)")
    
    if soma_reduzida > 0 and min_val <= soma_reduzida <= max_val:
        numeros_base.add(soma_reduzida)
        app.logger.info(f"Número base da numerologia para {lottery_name_for_log}: {soma_reduzida} (main.py)")

    if data_nascimento_str and isinstance(data_nascimento_str, str) and len(numeros_base) < num_numeros_gerar :
        dia = int(data_nascimento_str[0:2]) if len(data_nascimento_str) >= 2 else 0
        mes = int(data_nascimento_str[2:4]) if len(data_nascimento_str) >= 4 else 0

        if min_val <= dia <= max_val and dia not in numeros_base: numeros_base.add(dia)
        if len(numeros_base) < num_numeros_gerar and min_val <= mes <= max_val and mes not in numeros_base: numeros_base.add(mes)
    
    palpite_final_list = list(numeros_base)
    
    if len(palpite_final_list) < num_numeros_gerar:
        app.logger.info(f"Esotérico para {lottery_name_for_log}: Completando com números aleatórios (main.py).")
        pool_complementar = [n for n in range(min_val, max_val + 1) if n not in palpite_final_list]
        random.shuffle(pool_complementar)
        necessarios = num_numeros_gerar - len(palpite_final_list)
        palpite_final_list.extend(pool_complementar[:necessarios])
    
    final_game_set = set(palpite_final_list)
    if len(final_game_set) > num_numeros_gerar:
        final_result = sorted(random.sample(list(final_game_set), num_numeros_gerar))
    elif len(final_game_set) < num_numeros_gerar: 
        app.logger.error(f"Esotérico para {lottery_name_for_log}: Falha crítica ao completar. Usando fallback aleatório total (main.py).")
        return sorted(random.sample(range(min_val, max_val + 1), num_numeros_gerar))
    else:
        final_result = sorted(list(final_game_set))

    app.logger.info(f"Palpite esotérico simples gerado para {lottery_name_for_log}: {final_result} (main.py)")
    return final_result


def verificar_historico_combinacao(lottery_name_lower, combinacao_palpite_int_list):
    app.logger.info(f"[verificar_historico] Verificando {combinacao_palpite_int_list} para {lottery_name_lower} (main.py)")
    todos_resultados = load_processed_lottery_data(lottery_name_lower)
    if not todos_resultados: 
        app.logger.warning(f"[verificar_historico] Histórico não carregado para {lottery_name_lower} (main.py)")
        return 0, 0.0, "Histórico indisponível"
    
    ocorrencias = 0
    valor_total_ganho = 0.0
    concursos_premiados_info = [] 

    palpite_ordenado = sorted(combinacao_palpite_int_list) 

    for sorteio in todos_resultados:
        numeros_sorteados_str = sorteio.get("numeros")
        if numeros_sorteados_str and isinstance(numeros_sorteados_str, list):
            try:
                numeros_sorteados_int = sorted([int(n_str) for n_str in numeros_sorteados_str]) 
                if numeros_sorteados_int == palpite_ordenado: 
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
                continue 
    
    app.logger.info(f"[verificar_historico] Palpite {palpite_ordenado} para {lottery_name_lower}: {ocorrencias} ocorrências, R${valor_total_ganho:.2f} ganhos. Detalhes: {concursos_premiados_info} (main.py)")
    return ocorrencias, valor_total_ganho, concursos_premiados_info


@app.route('/api/main/palpite-esoterico/<lottery_name>', methods=['POST'])
def gerar_palpite_esoterico_route(lottery_name):
    app.logger.info(f"Endpoint /api/main/palpite-esoterico/{lottery_name} acessado (main.py). JSON: {request.get_json(silent=True)}")
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: 
        app.logger.warning(f"Loteria não config para palpite esotérico: {lottery_name} (main.py)")
        return jsonify({"erro": "Loteria não configurada."}), 404
    
    dados_usuario = request.get_json()
    if not dados_usuario: 
        app.logger.warning("Dados não fornecidos para palpite esotérico (main.py).")
        return jsonify({"erro": "Dados da requisição não fornecidos."}), 400
    
    data_nascimento_str = dados_usuario.get("data_nascimento") 
    if not data_nascimento_str or not re.match(r"^\d{8}$", data_nascimento_str): 
        app.logger.warning(f"'data_nascimento' inválida ou não fornecida: {data_nascimento_str} (main.py)")
        return jsonify({"erro": "Parâmetro 'data_nascimento' (DDMMAAAA) inválido ou não fornecido."}), 400
    
    num_a_gerar = config.get("count_apostadas", config.get("count", config.get("count_sorteadas")))
    min_val, max_val = config["min"], config["max"]
    
    app.logger.info(f"Gerando palpite esotérico para {lottery_name} com data {data_nascimento_str} (main.py)")
    palpite_gerado_int_list = gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_a_gerar, min_val, max_val, lottery_name_lower)
    metodo_usado = f"Baseado em Numerologia (data: {data_nascimento_str[0:2]}/{data_nascimento_str[2:4]}/{data_nascimento_str[4:8]})"
    
    if not palpite_gerado_int_list or len(palpite_gerado_int_list) != num_a_gerar:
        app.logger.error(f"Falha ao gerar palpite esotérico: {palpite_gerado_int_list}, esperado: {num_a_gerar}. Usando fallback aleatório (main.py).")
        palpite_gerado_int_list = sorted(random.sample(range(min_val, max_val + 1), num_a_gerar)) 
        metodo_usado = "Aleatório (fallback pós-falha esotérica)"
        app.logger.info(f"Fallback palpite aleatório para esotérico: {palpite_gerado_int_list} (main.py)")
    
    ocorrencias, valor_ganho, detalhes_premiacao = verificar_historico_combinacao(lottery_name_lower, palpite_gerado_int_list)
    
    response_data = {
        "loteria": config["nome_exibicao"], 
        "palpite_gerado": palpite_gerado_int_list, 
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
    app.logger.info(f"Retornando palpite esotérico para {lottery_name}: {response_data} (main.py)")
    if PLATFORM_STATS_DOC_REF: 
        try: PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats: app.logger.error(f"Erro ao incrementar total_generated_games (esotérico, main.py): {e_stats}")
    return jsonify(response_data), 200


def _generate_logical_hunch(lottery_name, all_results, config):
    app.logger.info(f"Gerando palpite lógico para {lottery_name} (main.py)")
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    min_val, max_val = config["min"], config["max"]
    
    jogo_final_set = set() 
    
    numeros_ultimo_sorteio = set()
    if all_results and len(all_results) > 0:
        try:
            numeros_ultimo_sorteio = set(int(n_str) for n_str in all_results[0].get("numeros", []))
        except ValueError:
            app.logger.warning(f"Palpite Lógico para {lottery_name}: Não foi possível converter números do último sorteio para int (main.py).")
    
    if all_results:
        todos_numeros_raw_lg = [num_str for sorteio in all_results for num_str in sorteio.get("numeros", [])]
        todos_numeros_int_lg = []
        for n_str_lg in todos_numeros_raw_lg:
            try: todos_numeros_int_lg.append(int(n_str_lg))
            except ValueError: pass

        if todos_numeros_int_lg:
            contagem_lg = Counter(todos_numeros_int_lg)
            frequencia_ordenada_lg = sorted(contagem_lg.items(), key=lambda item: (-item[1], item[0])) 
            
            num_frequentes_a_pegar = math.ceil(numeros_a_gerar * 0.4) 
            for num_freq_val, _ in frequencia_ordenada_lg:
                if len(jogo_final_set) < num_frequentes_a_pegar:
                    if int(num_freq_val) not in numeros_ultimo_sorteio: 
                        jogo_final_set.add(int(num_freq_val))
                else:
                    break
    
    pool_aleatorio_logico = [n for n in range(min_val, max_val + 1) if n not in numeros_ultimo_sorteio and n not in jogo_final_set]
    random.shuffle(pool_aleatorio_logico)

    idx_pool_lg = 0
    while len(jogo_final_set) < numeros_a_gerar and idx_pool_lg < len(pool_aleatorio_logico):
        jogo_final_set.add(pool_aleatorio_logico[idx_pool_lg])
        idx_pool_lg += 1

    jogo_final_list_lg = list(jogo_final_set)
    if len(jogo_final_list_lg) < numeros_a_gerar:
        app.logger.warning(f"Palpite Lógico para {lottery_name}: Faltaram números ({len(jogo_final_list_lg)} de {numeros_a_gerar}). Completando (main.py).")
        pool_geral_restante_lg = [n for n in range(min_val, max_val + 1) if n not in jogo_final_list_lg]
        random.shuffle(pool_geral_restante_lg)
        necessarios_lg = numeros_a_gerar - len(jogo_final_list_lg)
        jogo_final_list_lg.extend(pool_geral_restante_lg[:necessarios_lg])

    if len(jogo_final_list_lg) > numeros_a_gerar: 
        jogo_final_list_lg = random.sample(jogo_final_list_lg, numeros_a_gerar)
    
    if len(jogo_final_list_lg) != numeros_a_gerar:
        app.logger.error(f"Palpite Lógico para {lottery_name}: Falha crítica ao gerar contagem correta. Gerando totalmente aleatório (main.py).")
        return sorted(list(random.sample(range(min_val, max_val + 1), numeros_a_gerar)))

    return sorted(jogo_final_list_lg)


@app.route('/api/main/gerar_jogo/logico/<lottery_name>', methods=['GET'])
def gerar_jogo_logico_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config:
        return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404

    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response and status_code != 503 : 
         app.logger.warning(f"Palpite Lógico para {lottery_name}: Erro ao buscar dados históricos ({status_code}). Estratégia pode ser comprometida (main.py).")

    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    jogo_final = _generate_logical_hunch(lottery_name_lower, all_results, config) 

    if not jogo_final or len(jogo_final) != numeros_a_gerar:
        app.logger.error(f"API /gerar_jogo/logico: Falha ao gerar jogo para {lottery_name}. Usando fallback aleatório geral (main.py).")
        resultado_fallback = gerar_jogo_ia_aleatorio_rapido(lottery_name_lower) 
        return jsonify({
            "jogo": resultado_fallback.get("jogo", []),
            "estrategia_usada": f"{config.get('nome_exibicao', lottery_name.capitalize())}: Palpite Lógico (Fallback Aleatório Crítico)",
            "aviso": "Falha na estratégia lógica, usando palpite aleatório."
        }), 200 

    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Palpite Lógico Inteligente"
    if PLATFORM_STATS_DOC_REF:
        try: PLATFORM_STATS_DOC_REF.update({"total_generated_games": admin_firestore.Increment(1)})
        except Exception as e_stats_update: app.logger.error(f"Erro ao incrementar total_generated_games para palpite lógico (main.py): {e_stats_update}")
    return jsonify({"jogo": jogo_final, "estrategia_usada": estrategia_aplicada})


def determinar_faixa_premio_main(lottery_type, acertos):
    config_loteria = LOTTERY_CONFIG.get(lottery_type)
    if not config_loteria:
        return "Desconhecida", False

    is_premiado_geral = False
    faixa = f"{acertos} Acertos"

    if lottery_type == "megasena":
        if acertos == 6: faixa, is_premiado_geral = "Sena", True
        elif acertos == 5: faixa, is_premiado_geral = "Quina", True
        elif acertos == 4: faixa, is_premiado_geral = "Quadra", True
    elif lottery_type == "lotofacil":
        if acertos == 15: faixa, is_premiado_geral = "15 Pontos", True
        elif acertos == 14: faixa, is_premiado_geral = "14 Pontos", True
        elif acertos == 13: faixa, is_premiado_geral = "13 Pontos", True
        elif acertos == 12: faixa, is_premiado_geral = "12 Pontos", True
        elif acertos == 11: faixa, is_premiado_geral = "11 Pontos", True
    elif lottery_type == "quina":
        if acertos == 5: faixa, is_premiado_geral = "Quina", True
        elif acertos == 4: faixa, is_premiado_geral = "Quadra", True
        elif acertos == 3: faixa, is_premiado_geral = "Terno", True
        elif acertos == 2: faixa, is_premiado_geral = "Duque", True
    elif lottery_type == "lotomania":
        if acertos == 20: faixa, is_premiado_geral = "20 Pontos", True
        elif acertos == 19: faixa, is_premiado_geral = "19 Pontos", True
        elif acertos == 18: faixa, is_premiado_geral = "18 Pontos", True
        elif acertos == 17: faixa, is_premiado_geral = "17 Pontos", True
        elif acertos == 16: faixa, is_premiado_geral = "16 Pontos", True
        elif acertos == 15: faixa, is_premiado_geral = "15 Pontos", True
        elif acertos == 0: faixa, is_premiado_geral = "0 Acertos (Especial)", True

    if not is_premiado_geral and acertos > 0:
         faixa = f"{acertos} Acertos (Não Premiado)"
    elif not is_premiado_geral and acertos == 0 and lottery_type != "lotomania":
         faixa = "Nenhum Acerto"

    return faixa, is_premiado_geral


@app.route('/api/main/verificar-jogo-passado', methods=['POST'])
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
        if len(set(numeros_usuario)) != expected_numbers_count:
            return jsonify({"erro": f"Os números do usuário para {nome_exibicao_req} não devem conter duplicatas e devem ser {expected_numbers_count}."}), 400

    except (ValueError, TypeError) :
        return jsonify({"erro": "Concurso deve ser um inteiro e números do usuário devem ser uma lista de inteiros válidos."}), 400

    all_lottery_results = load_processed_lottery_data(lottery_type_req)
    if not all_lottery_results:
        return jsonify({"erro": f"Dados históricos da {nome_exibicao_req} indisponíveis no momento."}), 503

    sorteio_encontrado_req = None
    for sorteio_hist_req in all_lottery_results:
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

    faixa_premio_txt_req, premiado_geral_flag_req = determinar_faixa_premio_main(lottery_type_req, acertos_req)

    valor_premio_real = 0.0
    aviso_premio_req = None
    if premiado_geral_flag_req:
        key_rateio = None
        if lottery_type_req == "megasena":
            if acertos_req == 6: key_rateio = config_req.get("rateio_sena_key")
            elif acertos_req == 5: key_rateio = config_req.get("rateio_quina_key")
            elif acertos_req == 4: key_rateio = config_req.get("rateio_quadra_key")
        elif lottery_type_req == "lotofacil":
            if acertos_req == 15: key_rateio = config_req.get("rateio_15_key")
            elif acertos_req == 14: key_rateio = config_req.get("rateio_14_key")
            elif acertos_req == 13: key_rateio = config_req.get("rateio_13_key")
            elif acertos_req == 12: key_rateio = config_req.get("rateio_12_key")
            elif acertos_req == 11: key_rateio = config_req.get("rateio_11_key")
        elif lottery_type_req == "quina":
            if acertos_req == 5: key_rateio = config_req.get("rateio_5_key")
            elif acertos_req == 4: key_rateio = config_req.get("rateio_4_key")
            elif acertos_req == 3: key_rateio = config_req.get("rateio_3_key")
            elif acertos_req == 2: key_rateio = config_req.get("rateio_2_key")
        elif lottery_type_req == "lotomania":
            if acertos_req == 20: key_rateio = config_req.get("rateio_20_key")
            elif acertos_req == 0: key_rateio = config_req.get("rateio_0_key")


        if key_rateio and sorteio_encontrado_req.get(key_rateio) is not None:
            valor_premio_real_str = sorteio_encontrado_req.get(key_rateio)
            valor_premio_real = parse_currency_to_float(valor_premio_real_str)
        elif key_rateio and premiado_geral_flag_req :
             aviso_premio_req = f"Valor do prêmio da {faixa_premio_txt_req} não disponível na base de dados para este concurso."


    return jsonify({
        "loteria_nome_exibicao": nome_exibicao_req,
        "concurso_verificado": concurso_solicitado,
        "data_sorteio_verificado": sorteio_encontrado_req.get("data", "N/A"),
        "jogo_usuario": sorted(numeros_usuario),
        "numeros_sorteados": sorted(numeros_sorteados_oficial_req),
        "acertos": acertos_req,
        "premiado": premiado_geral_flag_req,
        "faixa_premio": faixa_premio_txt_req,
        "valor_premio_bruto_estimado": valor_premio_real,
        "valor_premio_formatado_estimado": format_currency(valor_premio_real) if premiado_geral_flag_req and valor_premio_real > 0 else ("Não aplicável" if not aviso_premio_req and premiado_geral_flag_req else "R$ 0,00"),
        "aviso": aviso_premio_req
    }), 200


@app.route('/api/internal/run-verification', methods=['POST'])
def trigger_game_verification_endpoint():
    INTERNAL_API_KEY = os.environ.get("INTERNAL_CRON_SECRET_MANUAL_VERIF") 
    if not INTERNAL_API_KEY:
        app.logger.error("INTERNAL_CRON_SECRET_MANUAL_VERIF não configurado.")
        return jsonify({"error": "Configuração interna do servidor ausente."}), 500

    request_api_key = request.headers.get('X-Internal-Api-Key')
    if request_api_key != INTERNAL_API_KEY:
        app.logger.warning("Tentativa de acesso não autorizado ao endpoint de verificação manual em lote.")
        return jsonify({"error": "Não autorizado"}), 403

    app.logger.info("Disparando verificação em lote de jogos salvos via endpoint /api/internal/run-verification.")
    try:
        if not FB_ADMIN_INITIALIZED or not db_admin:
            app.logger.error("Endpoint de verificação manual: Firebase Admin (db_admin) não está inicializado. Não pode prosseguir.")
            return jsonify({"status": "error", "message":"Erro interno: Firebase não inicializado."}), 500
        
        verificar_jogos_salvos_batch() 
        message = "Verificação em lote de jogos salvos (manual) concluída com sucesso."
        app.logger.info(message)
        return jsonify({"status": "success", "message": message}), 200
    except Exception as e_manual_verif:
        error_message = f"Erro ao executar verificação manual em lote: {e_manual_verif}"
        app.logger.error(error_message, exc_info=True)
        return jsonify({"status": "error", "message": error_message}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)