from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import datetime
import pandas as pd
import os
import json
from collections import Counter
from itertools import combinations 
import re 
import math

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'lottery_data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

MASTER_FILES = {
    "lotofacil": "Lotofácil.xlsx",
    "megasena": "Mega-Sena.xlsx",
    "lotomania": "Lotomania.xlsx",
    "quina": "Quina.xlsx"
}

LOTTERY_CONFIG = {
    "megasena": {
        "nome_exibicao": "Mega-Sena", "min": 1, "max": 60, "count": 6, "color": "#209869",
        "processed_json_file": os.path.join(DATA_DIR, "megasena_processed_results.json"),
        "master_file_path": os.path.join(DATA_DIR, MASTER_FILES.get("megasena")),
        "col_concurso": "Concurso", "col_data_sorteio": "Data do Sorteio",
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 6,
        "col_ganhadores_principal": "Ganhadores 6 acertos", 
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 6 acertos" 
    },
    "lotofacil": {
        "nome_exibicao": "Lotofácil", "min": 1, "max": 25, "count": 15, "color": "#930089",
        "processed_json_file": os.path.join(DATA_DIR, "lotofacil_processed_results.json"),
        "master_file_path": os.path.join(DATA_DIR, MASTER_FILES.get("lotofacil")),
        "col_concurso": "Concurso", "col_data_sorteio": "Data Sorteio",
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 15,
        "col_ganhadores_principal": "Ganhadores 15 acertos", 
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 15 acertos"
    },
    "lotomania": {
        "nome_exibicao": "Lotomania", "min": 0, "max": 99, "count_apostadas": 50, "count_sorteadas": 20, "color": "#f78100",
        "processed_json_file": os.path.join(DATA_DIR, "lotomania_processed_results.json"),
        "master_file_path": os.path.join(DATA_DIR, MASTER_FILES.get("lotomania")),
        "col_concurso": "Concurso", "col_data_sorteio": "Data Sorteio", 
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 20,
        "col_ganhadores_principal": "Ganhadores 20 acertos", 
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 20 acertos"
    },
    "quina": {
        "nome_exibicao": "Quina", "min": 1, "max": 80, "count": 5, "color": "#260085",
        "processed_json_file": os.path.join(DATA_DIR, "quina_processed_results.json"),
        "master_file_path": os.path.join(DATA_DIR, MASTER_FILES.get("quina")),
        "col_concurso": "Concurso", "col_data_sorteio": "Data Sorteio", 
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 5,
        "col_ganhadores_principal": "Ganhadores 5 acertos", 
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 5 acertos"
    }
}

platform_stats_data = {
    "jogos_gerados_total": random.randint(18500, 30500),
    "jogos_premiados_estimativa": random.randint(250, 750),
    "valor_premios_estimativa_bruto": random.uniform(95000, 350000)
}

def format_currency(value):
    if isinstance(value, (int, float)):
        return f"R$ {value:_.2f}".replace('.', ',').replace('_', '.')
    return "R$ 0,00" 

def parse_currency_to_float(currency_str):
    if not isinstance(currency_str, str):
        currency_str = str(currency_str)
    cleaned_str = currency_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
    try:
        return float(cleaned_str)
    except ValueError:
        return 0.0 

def parse_ganhadores_cidades(cidade_uf_str, num_ganhadores_str):
    cidades_parsed = []
    try:
        num_ganhadores = int(str(num_ganhadores_str).strip()) if str(num_ganhadores_str).strip().isdigit() else 0
    except ValueError:
        num_ganhadores = 0

    if num_ganhadores > 0 and isinstance(cidade_uf_str, str) and cidade_uf_str.strip() and cidade_uf_str.strip() != "-":
        temp_str = re.sub(r'\s*\(\s*(\d+)\s*\)\s*', r'(\1)', cidade_uf_str)
        
        if ";" in temp_str:
            entries = [entry.strip() for entry in temp_str.split(';')]
        else:
            entries = [entry.strip() for entry in temp_str.split(',')]

        parsed_from_entries = []
        for entry in entries:
            if not entry: continue
            match_contagem = re.search(r'\((?P<contagem>\d+)\)$', entry)
            contagem_na_string = 1
            cidade_limpa = entry
            if match_contagem:
                contagem_na_string = int(match_contagem.group("contagem"))
                cidade_limpa = re.sub(r'\s*\(\d+\)$', '', entry).strip()
            
            if cidade_limpa:
                parsed_from_entries.extend([cidade_limpa] * contagem_na_string)
        
        cidades_parsed = [c for c in parsed_from_entries if c] 

        if num_ganhadores > 0:
            if not cidades_parsed: 
                cidades_parsed = ["Não especificada"] * num_ganhadores
            elif len(cidades_parsed) < num_ganhadores:
                if len(cidades_parsed) == 1: 
                    cidades_parsed = [cidades_parsed[0]] * num_ganhadores
                else: 
                    cidades_parsed.extend(["Não especificada"] * (num_ganhadores - len(cidades_parsed)))
            elif len(cidades_parsed) > num_ganhadores: 
                 cidades_parsed = cidades_parsed[:num_ganhadores]
    elif num_ganhadores > 0: 
        cidades_parsed = ["Não especificada"] * num_ganhadores
        
    return cidades_parsed, num_ganhadores

def process_local_lottery_file(lottery_key):
    print(f"DEBUG: Iniciando process_local_lottery_file para {lottery_key.upper()}")
    required_config_keys = ["master_file_path", "processed_json_file", "col_concurso",
                            "col_data_sorteio", "cols_bolas_prefix", "num_bolas_no_arquivo"]
    if lottery_key not in LOTTERY_CONFIG or \
       not all(LOTTERY_CONFIG[lottery_key].get(k) for k in required_config_keys):
        print(f"AVISO: Configuração incompleta para {lottery_key} no LOTTERY_CONFIG.")
        return {"erro": f"Configuração incompleta para {lottery_key}.", "status": 500}

    config = LOTTERY_CONFIG[lottery_key]
    master_filepath_xlsx = config["master_file_path"]
    master_filepath_csv = master_filepath_xlsx.replace(".xlsx", ".csv") if master_filepath_xlsx else None
    processed_json_path = config["processed_json_file"]

    col_concurso = config["col_concurso"]
    col_data = config["col_data_sorteio"]
    cols_bolas_prefix = config["cols_bolas_prefix"]
    num_bolas_a_ler = config["num_bolas_no_arquivo"]
    col_ganhadores_principal = config.get("col_ganhadores_principal") 
    col_cidade_uf_principal = config.get("col_cidade_uf_principal")   
    col_rateio_principal = config.get("col_rateio_principal") 
    
    actual_cols_dezenas_expected = [f'{cols_bolas_prefix}{i}' for i in range(1, num_bolas_a_ler + 1)]
    df = None
    file_used = None
    file_type_read = None

    if master_filepath_xlsx and os.path.exists(master_filepath_xlsx):
        try:
            print(f"DEBUG: Lendo XLSX: {master_filepath_xlsx} com dtype=str para todas as colunas.")
            df = pd.read_excel(master_filepath_xlsx, engine='openpyxl', dtype=str)
            file_used = master_filepath_xlsx
            file_type_read = "XLSX"
            print(f"INFO: Sucesso ao ler {file_used} para {lottery_key.upper()} (todas as colunas como string).")
        except ImportError:
            print(f"ERRO CRÍTICO: 'openpyxl' não instalado. Execute: pip install openpyxl")
            return {"erro": "'openpyxl' não instalado no servidor.", "status": 500}
        except Exception as e:
            print(f"ERRO CRÍTICO ao ler XLSX {master_filepath_xlsx} mesmo com dtype=str: {type(e).__name__} - {e}")
            df = None 

    if df is None and master_filepath_csv and os.path.exists(master_filepath_csv):
        try:
            print(f"DEBUG: Tentando ler CSV: {master_filepath_csv} com dtype=str.")
            df_raw_csv = pd.read_csv(master_filepath_csv, sep=None, engine='python', encoding='utf-8-sig', on_bad_lines='warn', skip_blank_lines=True, dtype=str)
            if df_raw_csv.shape[1] == 1 and not df_raw_csv.empty and ';' in str(df_raw_csv.iloc[0,0]): 
                 print(f"DEBUG: CSV lido como uma única coluna (UTF-8), tentando com separador ';' para {master_filepath_csv}")
                 df_raw_csv = pd.read_csv(master_filepath_csv, sep=';', engine='python', encoding='utf-8-sig', on_bad_lines='warn', skip_blank_lines=True, dtype=str)
            df = df_raw_csv 
            file_used = master_filepath_csv
            file_type_read = "CSV"
            print(f"INFO: Sucesso ao ler CSV (UTF-8): {file_used} para {lottery_key.upper()} (todas colunas como string).")
        except UnicodeDecodeError:
             print(f"AVISO: UnicodeDecodeError com UTF-8 para {master_filepath_csv}, tentando iso-8859-1.")
             try:
                df_raw_csv = pd.read_csv(master_filepath_csv, sep=None, engine='python', encoding='iso-8859-1', on_bad_lines='warn', skip_blank_lines=True, dtype=str)
                if df_raw_csv.shape[1] == 1 and not df_raw_csv.empty and ';' in str(df_raw_csv.iloc[0,0]):
                     print(f"DEBUG: CSV lido como uma única coluna (ISO-8859-1), tentando com separador ';' para {master_filepath_csv}")
                     df_raw_csv = pd.read_csv(master_filepath_csv, sep=';', engine='python', encoding='iso-8859-1', on_bad_lines='warn', skip_blank_lines=True, dtype=str)
                df = df_raw_csv 
                file_used = master_filepath_csv
                file_type_read = "CSV"
                print(f"INFO: Sucesso ao ler CSV: {file_used} para {lottery_key.upper()} (ISO-8859-1, todas colunas como string).")
             except Exception as e_csv_iso:
                print(f"ERRO: Ao ler CSV {master_filepath_csv} com ISO-8859-1: {e_csv_iso}")
                df = None
        except Exception as e_csv: 
            print(f"ERRO: Ao ler CSV {master_filepath_csv}: {e_csv}") 
            df = None

    if df is None:
        print(f"AVISO FINAL: Nenhum arquivo mestre (XLSX ou CSV) lido com sucesso para {lottery_key.upper()}.")
        return {"erro": f"Arquivo mestre para {lottery_key.upper()} não encontrado ou falha crítica na leitura.", "status": 404}

    print(f"INFO: Processando dados de {lottery_key.upper()} ({file_type_read}).")
    
    if col_concurso not in df.columns or col_data not in df.columns:
        missing_core_cols = [col for col in [col_concurso, col_data] if col not in df.columns]
        print(f"ERRO: Colunas essenciais ({', '.join(missing_core_cols)}) ausentes para {lottery_key.upper()}. Colunas disponíveis: {df.columns.tolist()}")
        return {"erro": f"Colunas essenciais ausentes no arquivo de {lottery_key.upper()}: {', '.join(missing_core_cols)}.", "status": 400}

    actual_cols_dezenas_in_file = [col for col in actual_cols_dezenas_expected if col in df.columns]
    if not actual_cols_dezenas_in_file:
        print(f"ERRO: Nenhuma coluna de dezena ({cols_bolas_prefix}X) configurada foi encontrada para {lottery_key.upper()}. Colunas disponíveis: {df.columns.tolist()}")
        return {"erro": f"Nenhuma coluna de dezena configurada encontrada no arquivo de {lottery_key.upper()}.", "status": 400}
    if len(actual_cols_dezenas_in_file) < num_bolas_a_ler:
         print(f"ALERTA SÉRIO: Encontradas apenas {len(actual_cols_dezenas_in_file)} de {num_bolas_a_ler} colunas de dezenas esperadas para {lottery_key.upper()}. Os dados podem estar incompletos. Colunas de dezenas encontradas: {actual_cols_dezenas_in_file}")

    results_list = []
    for index, row in df.iterrows():
        try:
            concurso_str = str(row.get(col_concurso, '')).strip() 
            data_str = str(row.get(col_data, '')).strip()

            if not concurso_str or concurso_str.lower() == 'nan' or concurso_str == '': continue
            if not data_str or data_str.lower() == 'nan' or data_str == '': continue
            
            concurso_val = 0
            try:
                concurso_val = int(float(concurso_str.replace(',', '')))
            except ValueError:
                continue

            data_formatada = data_str 
            try:
                dt_obj = pd.to_datetime(data_str, errors='coerce', dayfirst=True) 
                if pd.notna(dt_obj): data_formatada = dt_obj.strftime('%d/%m/%Y')
            except Exception: pass 

            dezenas_lidas = []
            for col_dezena in actual_cols_dezenas_in_file[:num_bolas_a_ler]: 
                dezena_str = str(row.get(col_dezena, '')).strip() 
                if dezena_str.isdigit(): dezenas_lidas.append(int(dezena_str))
                elif dezena_str == '-': pass 
            
            if len(dezenas_lidas) == num_bolas_a_ler:
                sorteio_data = {
                    "concurso": concurso_val, "data": data_formatada, "numeros": sorted(dezenas_lidas)
                }
                if col_ganhadores_principal and col_cidade_uf_principal and col_rateio_principal and \
                   col_ganhadores_principal in df.columns and \
                   col_cidade_uf_principal in df.columns and \
                   col_rateio_principal in df.columns:
                    
                    ganhadores_str = str(row.get(col_ganhadores_principal, '0')).strip()
                    cidade_uf_str = str(row.get(col_cidade_uf_principal, '')).strip()
                    rateio_str = str(row.get(col_rateio_principal, '0')).strip()
                    
                    cidades_lista, num_ganhadores_parsed = parse_ganhadores_cidades(cidade_uf_str, ganhadores_str)
                    sorteio_data["ganhadores_principal_contagem"] = num_ganhadores_parsed
                    sorteio_data["cidades_ganhadoras_principal"] = cidades_lista
                    sorteio_data["rateio_principal_valor"] = parse_currency_to_float(rateio_str) if num_ganhadores_parsed > 0 else 0.0
                
                results_list.append(sorteio_data)
        except Exception as e_row:
            print(f"ERRO GERAL ao processar linha {index+1} ({lottery_key.upper()}): {type(e_row).__name__} - {e_row}. Dados da linha: {row.to_dict() if isinstance(row, pd.Series) else row}")
            continue
    
    if results_list: 
        results_list.sort(key=lambda x: x["concurso"], reverse=True)
        try:
            with open(processed_json_path, 'w', encoding='utf-8') as f:
                json.dump(results_list, f, ensure_ascii=False, indent=4)
            print(f"SUCESSO: {processed_json_path} atualizado com {len(results_list)} concursos de {lottery_key.upper()}.")
            return {"message": f"Dados de {lottery_key.upper()} atualizados com {len(results_list)} concursos.", "status": 200}
        except Exception as e_json:
            print(f"ERRO ao salvar JSON {processed_json_path}: {e_json}")
            return {"erro": f"Falha ao salvar arquivo JSON processado para {lottery_key.upper()}.", "status": 500}
    else:
        print(f"AVISO FINAL: Nenhum resultado válido processado para {lottery_key.upper()} a partir de {file_used if file_used else 'arquivo desconhecido'}. Verifique o arquivo de origem, logs e configuração das colunas.")
        return {"erro": f"Nenhum resultado válido processado para {lottery_key.upper()}. Verifique o arquivo de origem e a configuração das colunas.", "status": 400}

@app.route('/api/main/')
def api_home():
    return jsonify({"mensagem": "API Loto Genius AI Funcionando!", "versao": "2.1.0 - Premium Features & Advanced IA Strategies"}) 

@app.route('/api/main/refresh-data/<lottery_name>', methods=['POST'])
def refresh_lottery_data_from_local_file(lottery_name):
    lottery_name_lower = lottery_name.lower()
    if lottery_name_lower in LOTTERY_CONFIG:
        result = process_local_lottery_file(lottery_name_lower)
        return jsonify(result), result.get("status", 200)
    return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404

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
    pools = [
        {"name": "Bolão da Virada Genius", "lottery": "Mega-Sena", "prize": format_currency(random.uniform(150000, 750000)), "date": "31/12/2024"},
        {"name": "Grupo Independência Forte", "lottery": "Lotofácil", "prize": format_currency(random.uniform(5000, 15000)), "date": "07/09/2024"},
        {"name": "Amigos da Quina Junina", "lottery": "Quina", "prize": format_currency(random.uniform(20000, 100000)), "date": "23/06/2024"},
    ]
    return jsonify(random.sample(pools, k=min(len(pools), random.randint(1,3))))

@app.route('/api/main/top-winners', methods=['GET'])
def get_top_winners():
    winners = [
        {"nick": "MestreDaSorte", "prize_total": format_currency(random.uniform(250000, 1200000))},
        {"nick": "LeoSupremo", "prize_total": format_currency(random.uniform(180000, 700000))},
        {"nick": "DamaDeCopas", "prize_total": format_currency(random.uniform(120000, 500000))},
        {"nick": "ApostaDeOuro", "prize_total": format_currency(random.uniform(90000, 350000))},
        {"nick": "NumerologoExpert", "prize_total": format_currency(random.uniform(60000, 250000))},
    ]
    random.shuffle(winners)
    return jsonify(winners[:random.randint(3,5)])

@app.route('/api/main/resultados/<lottery_name>', methods=['GET'])
def get_resultados_api(lottery_name):
    lottery_name_lower = lottery_name.lower()
    if lottery_name_lower not in LOTTERY_CONFIG:
        return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404
    processed_file_path = LOTTERY_CONFIG[lottery_name_lower].get("processed_json_file")
    if not processed_file_path: return jsonify({"erro": f"Arquivo processado não configurado para {lottery_name}."}), 500
    if os.path.exists(processed_file_path):
        try:
            with open(processed_file_path, 'r', encoding='utf-8') as f: all_results = json.load(f)
            if all_results: 
                latest_result = all_results[0] 
                return jsonify({
                    "ultimo_concurso": latest_result.get("concurso"), "data": latest_result.get("data"),
                    "numeros": latest_result.get("numeros"),
                    "ganhadores_principal_contagem": latest_result.get("ganhadores_principal_contagem"),
                    "cidades_ganhadoras_principal": latest_result.get("cidades_ganhadoras_principal"),
                    "rateio_principal_valor": latest_result.get("rateio_principal_valor"),
                    "fonte": f"Arquivo Local Processado - {lottery_name.upper()}"
                })
            else: print(f"AVISO: JSON local para {lottery_name_lower} vazio: {processed_file_path}")
        except Exception as e: print(f"ERRO: Ao ler JSON local para {lottery_name_lower} ({processed_file_path}): {e}.")
    
    master_path_config = LOTTERY_CONFIG[lottery_name_lower].get("master_file_path")
    if master_path_config and (os.path.exists(master_path_config) or os.path.exists(master_path_config.replace(".xlsx", ".csv"))):
        process_output = process_local_lottery_file(lottery_name_lower) 
        if process_output.get("status") == 200 and os.path.exists(processed_file_path):
            try:
                with open(processed_file_path, 'r', encoding='utf-8') as f_reprocessed: all_results_reprocessed = json.load(f_reprocessed)
                if all_results_reprocessed: return jsonify(all_results_reprocessed[0]) 
            except Exception as e_reprocessed: print(f"ERRO: Ao ler JSON reprocessado para {lottery_name_lower}: {e_reprocessed}.")
        return jsonify({"aviso": f"Reprocessamento para {lottery_name.upper()} falhou. {process_output.get('erro', 'Verifique logs.')}", "numeros": []}), 503
    return jsonify({"aviso": f"Dados para {lottery_name.upper()} indisponíveis. JSON e mestre ausentes.", "numeros": []}), 404

@app.route('/api/main/stats/frequencia/<lottery_name>', methods=['GET'])
def get_frequencia_numeros(lottery_name):
    lottery_name_lower = lottery_name.lower()
    if lottery_name_lower not in LOTTERY_CONFIG: return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404
    processed_file_path = LOTTERY_CONFIG[lottery_name_lower].get("processed_json_file")
    if not processed_file_path or not os.path.exists(processed_file_path):
        process_result = process_local_lottery_file(lottery_name_lower)
        if process_result.get("status") != 200 or not os.path.exists(processed_file_path):
            return jsonify({"erro": f"Dados de {lottery_name.upper()} indisponíveis. {process_result.get('erro', '')}"}), 404
    try:
        with open(processed_file_path, 'r', encoding='utf-8') as f: all_results = json.load(f)
    except Exception as e: return jsonify({"erro": f"Falha ao ler dados de {lottery_name.upper()}: {e}"}), 500
    if not all_results: return jsonify({"erro": f"Sem dados históricos para {lottery_name.upper()}."}), 404
    todos_numeros = [num for sorteio in all_results if "numeros" in sorteio for num in sorteio["numeros"]]
    if not todos_numeros: return jsonify({"data": [], "mensagem": "Nenhum número nos dados."}), 200
    contagem = Counter(todos_numeros)
    frequencia_ordenada = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))
    frequencia_formatada = [{"numero": str(num).zfill(2), "frequencia": freq} for num, freq in frequencia_ordenada]
    return jsonify({"data": frequencia_formatada, "total_sorteios_analisados": len(all_results)})

@app.route('/api/main/stats/pares-frequentes/<lottery_name>', methods=['GET'])
def get_pares_frequentes(lottery_name):
    lottery_name_lower = lottery_name.lower(); config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": "Loteria não configurada."}), 404
    processed_file_path = config.get("processed_json_file")
    if not processed_file_path or not os.path.exists(processed_file_path):
        process_result = process_local_lottery_file(lottery_name_lower)
        if process_result.get("status") != 200 or not os.path.exists(processed_file_path):
            return jsonify({"erro": f"Dados de {lottery_name.upper()} indisponíveis. {process_result.get('erro', '')}"}), 404
    try:
        with open(processed_file_path, 'r', encoding='utf-8') as f: all_results = json.load(f)
    except Exception as e: return jsonify({"erro": f"Falha ao ler dados: {e}"}), 500
    if not all_results: return jsonify({"erro": "Sem dados históricos."}), 404
    numeros_por_sorteio = config.get("count_sorteadas", config.get("count")) 
    todos_os_itens_combinacao = [tuple(par) for s in all_results if s.get("numeros") and len(s["numeros"]) == numeros_por_sorteio for par in combinations(sorted(s["numeros"]), 2)]
    if not todos_os_itens_combinacao: return jsonify({"data": [], "mensagem": "Não foi possível gerar pares."}), 200
    contagem_itens = Counter(todos_os_itens_combinacao)
    itens_ordenados = sorted(contagem_itens.items(), key=lambda item: (-item[1], item[0]))
    itens_formatados = [{"par": [str(n).zfill(2) for n in item_numeros], "frequencia": freq} for item_numeros, freq in itens_ordenados]
    return jsonify({"data": itens_formatados[:30]})

@app.route('/api/main/stats/cidades-premiadas/<lottery_name>', methods=['GET'])
def get_cidades_premiadas(lottery_name):
    lottery_name_lower = lottery_name.lower(); config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": "Loteria não configurada."}), 404
    processed_file_path = config.get("processed_json_file")
    if not processed_file_path or not os.path.exists(processed_file_path):
        process_result = process_local_lottery_file(lottery_name_lower)
        if process_result.get("status") != 200 or not os.path.exists(processed_file_path):
            return jsonify({"erro": f"Dados de {lottery_name.upper()} indisponíveis. {process_result.get('erro', '')}"}), 404
    try:
        with open(processed_file_path, 'r', encoding='utf-8') as f: all_results = json.load(f)
    except Exception as e: return jsonify({"erro": f"Falha ao ler dados: {e}"}), 500
    if not all_results: return jsonify({"erro": "Sem dados históricos."}), 404
    contagem_cidades = Counter()
    total_premios_contabilizados = 0
    for sorteio in all_results:
        cidades = sorteio.get("cidades_ganhadoras_principal", [])
        if isinstance(cidades, list):
            cidades_validas = [c for c in cidades if c and c.lower() != "não especificada"] 
            if cidades_validas:
                contagem_cidades.update(cidades_validas)
                total_premios_contabilizados += len(cidades_validas)
    cidades_ordenadas = sorted(contagem_cidades.items(), key=lambda item: (-item[1], item[0]))
    cidades_formatadas = [{"cidade_uf": cidade, "premios_principais": freq} for cidade, freq in cidades_ordenadas]
    return jsonify({"data": cidades_formatadas[:30], "total_premios_analisados": total_premios_contabilizados}) 

@app.route('/api/main/stats/maiores-premios-cidade/<lottery_name>', methods=['GET'])
def get_maiores_premios_cidade(lottery_name):
    lottery_name_lower = lottery_name.lower(); config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": "Loteria não configurada."}), 404
    processed_file_path = config.get("processed_json_file")
    if not processed_file_path or not os.path.exists(processed_file_path):
        process_result = process_local_lottery_file(lottery_name_lower)
        if process_result.get("status") != 200 or not os.path.exists(processed_file_path):
            return jsonify({"erro": f"Dados de {lottery_name.upper()} indisponíveis. {process_result.get('erro', '')}"}), 404
    try:
        with open(processed_file_path, 'r', encoding='utf-8') as f: all_results = json.load(f)
    except Exception as e: return jsonify({"erro": f"Falha ao ler dados: {e}"}), 500
    if not all_results: return jsonify({"erro": "Sem dados históricos."}), 404
    soma_premios_cidade = Counter()
    for sorteio in all_results:
        cidades = sorteio.get("cidades_ganhadoras_principal", [])
        rateio = sorteio.get("rateio_principal_valor", 0.0)
        num_ganhadores_no_sorteio = sorteio.get("ganhadores_principal_contagem", 0)
        if rateio > 0 and cidades and num_ganhadores_no_sorteio > 0:
            if len(cidades) == num_ganhadores_no_sorteio:
                 for cidade in cidades:
                    if cidade and cidade.lower() != "não especificada":
                        soma_premios_cidade[cidade] += rateio
            elif cidades: 
                for cidade_unica in set(c for c in cidades if c and c.lower() != "não especificada"): 
                    ocorrencias_cidade = cidades.count(cidade_unica)
                    soma_premios_cidade[cidade_unica] += rateio * ocorrencias_cidade
    cidades_ordenadas = sorted(soma_premios_cidade.items(), key=lambda item: (-item[1], item[0]))
    cidades_formatadas = [{"cidade_uf": cid, "total_ganho_principal_formatado": format_currency(val), "total_ganho_principal_float": val} for cid, val in cidades_ordenadas]
    return jsonify({"data": cidades_formatadas[:30]})

def combinations_count(n, k):
    if k < 0 or k > n: return 0
    if k == 0 or k == n: return 1
    if k > n // 2: k = n - k
    res = 1
    for i in range(k): res = res * (n - i) // (i + 1)
    return res

@app.route('/api/main/jogo-manual/probabilidade', methods=['POST'])
def calcular_probabilidade_jogo():
    data = request.get_json()
    if not data or 'lottery_type' not in data or 'numeros_usuario' not in data:
        return jsonify({"erro": "Dados incompletos (lottery_type, numeros_usuario)."}), 400

    lottery_type = data['lottery_type'].lower()
    numeros_usuario_str_list = data['numeros_usuario']

    if lottery_type not in LOTTERY_CONFIG:
        return jsonify({"erro": f"Loteria '{data['lottery_type']}' não configurada."}), 404

    config = LOTTERY_CONFIG[lottery_type]
    nome_loteria = config.get('nome_exibicao', lottery_type.capitalize())
    universo_total = config['max'] - config['min'] + 1
    numeros_sorteados_para_premio_max = config.get('count_sorteadas', config.get('count')) 
    numeros_marcados_pelo_usuario_no_volante = config.get('count_apostadas', config.get('count'))

    if not isinstance(numeros_usuario_str_list, list):
        return jsonify({"erro": "Formato de 'numeros_usuario' inválido. Esperado uma lista."}), 400
    
    numeros_usuario = []
    try:
        for n_str in numeros_usuario_str_list:
            num = int(n_str)
            if not (config['min'] <= num <= config['max']):
                return jsonify({"erro": f"Número {num} fora do range ({config['min']}-{config['max']}) para {nome_loteria}."}), 400
            numeros_usuario.append(num)
    except ValueError:
        return jsonify({"erro": "Números devem ser inteiros válidos."}), 400

    if len(set(numeros_usuario)) != len(numeros_usuario):
        return jsonify({"erro": "Números repetidos não permitidos."}), 400
    
    # A validação da quantidade de números DEVE corresponder à quantidade que o usuário realmente aposta
    # e para a qual a probabilidade é calculada.
    # Para Lotomania, o usuário aposta 50, e a prob. do prêmio máximo é acertar 20 DENTRE ESSES 50.
    # Para outras, o usuário aposta 'count' e precisa acertar 'count'.
    if len(numeros_usuario) != numeros_marcados_pelo_usuario_no_volante:
         return jsonify({"erro": f"Para {nome_loteria}, você deve fornecer {numeros_marcados_pelo_usuario_no_volante} números para este cálculo."}), 400


    probabilidade_decimal = 0
    probabilidade_texto = "Não aplicável para esta configuração."

    if lottery_type == "lotomania":
        # Probabilidade de acertar os 20 números sorteados, tendo escolhido 50.
        # C(numeros_marcados, numeros_sorteados_para_premio_max) / C(universo_total, numeros_sorteados_para_premio_max)
        # C(50, 20) / C(100, 20)
        if numeros_marcados_pelo_usuario_no_volante == 50 and numeros_sorteados_para_premio_max == 20:
            combinacoes_favoraveis = combinations_count(numeros_marcados_pelo_usuario_no_volante, numeros_sorteados_para_premio_max) 
            combinacoes_totais_sorteio = combinations_count(universo_total, numeros_sorteados_para_premio_max)
            if combinacoes_totais_sorteio > 0 and combinacoes_favoraveis > 0 : 
                probabilidade_decimal = combinacoes_favoraveis / combinacoes_totais_sorteio
                # O texto deve refletir a chance DO SEU JOGO DE 50 acertar os 20
                # Isso é C(50,20) / C(100,20). 
                # O valor inverso é C(100,20) / C(50,20)
                valor_inverso = round(combinacoes_totais_sorteio / combinacoes_favoraveis) if combinacoes_favoraveis > 0 else float('inf')
                probabilidade_texto = f"1 em {valor_inverso:,}".replace(',', '.') if valor_inverso != float('inf') else "1 em infinito"
            else: probabilidade_texto = "Cálculo de combinações resultou em valor inválido."
        else: probabilidade_texto = "Cálculo para Lotomania (20 acertos) requer um jogo de 50 números."
    else: 
        # Probabilidade de um jogo específico de 'count' números ser o sorteado
        combinacoes_totais = combinations_count(universo_total, numeros_sorteados_para_premio_max)
        if combinacoes_totais > 0:
            probabilidade_decimal = 1 / combinacoes_totais
            probabilidade_texto = f"1 em {int(combinacoes_totais):,}".replace(',', '.')
        else: probabilidade_texto = "Cálculo de combinações resultou em zero."
            
    return jsonify({
        "loteria": nome_loteria, "jogo_usuario": sorted(numeros_usuario),
        "probabilidade_decimal": probabilidade_decimal, "probabilidade_texto": probabilidade_texto,
        "descricao": f"Probabilidade de acertar o prêmio máximo ({numeros_sorteados_para_premio_max} acertos) com o jogo fornecido."
    })

def calcular_numeros_quentes(todos_resultados, qtd_sorteios_analise, qtd_numeros_retorno):
    if not todos_resultados or qtd_sorteios_analise <= 0: return []
    ultimos_n = todos_resultados[:min(len(todos_resultados), qtd_sorteios_analise)]
    numeros_recentes = [num for r in ultimos_n for num in r.get("numeros", [])]
    if not numeros_recentes: return []
    contagem = Counter(numeros_recentes)
    return [num for num, freq in contagem.most_common(qtd_numeros_retorno)]

def calcular_numeros_frios(todos_resultados, universo_numeros, qtd_numeros_retorno):
    if not todos_resultados: return random.sample(list(universo_numeros), min(len(universo_numeros), qtd_numeros_retorno))
    ultima_aparicao_concurso = {num: 0 for num in universo_numeros}
    
    concurso_mais_recente = 0
    if todos_resultados and todos_resultados[0].get("concurso"): # Assume que resultados estão ordenados decrescente por concurso
        concurso_mais_recente = todos_resultados[0].get("concurso")
    else: # Fallback se não houver número de concurso (usa a contagem de sorteios como aproximação)
        concurso_mais_recente = len(todos_resultados)

    for i, sorteio in enumerate(todos_resultados): 
        concurso_atual = sorteio.get("concurso", concurso_mais_recente - i) # Usa o concurso do sorteio
        for num in sorteio.get("numeros", []):
            if num in ultima_aparicao_concurso and ultima_aparicao_concurso[num] == 0: 
                 ultima_aparicao_concurso[num] = concurso_atual
                 
    atrasos = {num: (concurso_mais_recente - ultima_aparicao_concurso[num]) if ultima_aparicao_concurso[num] != 0 else float('inf') for num in universo_numeros}
    frios_ordenados = sorted(atrasos.items(), key=lambda item: (-item[1], item[0])) # Ordena por maior atraso
    return [num for num, atraso in frios_ordenados[:qtd_numeros_retorno]]

def gerar_jogo_ia(lottery_name, todos_resultados_historicos=None, estrategia_req="aleatorio_inteligente", is_premium_user=False):
    print(f"DEBUG [gerar_jogo_ia]: Loteria: {lottery_name}, Estratégia: {estrategia_req}, Premium: {is_premium_user}")
    config = LOTTERY_CONFIG[lottery_name]
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    min_num, max_num = config["min"], config["max"]
    universo_numeros = list(range(min_num, max_num + 1))
    jogo_final = []
    estrategia_aplicada_nome_base = estrategia_req.replace('_', ' ').capitalize()
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: {estrategia_aplicada_nome_base}"

    if todos_resultados_historicos is None: # Garante que temos uma lista, mesmo que vazia
        todos_resultados_historicos = [] 
        processed_file_path = config.get("processed_json_file")
        if processed_file_path and os.path.exists(processed_file_path):
            try:
                with open(processed_file_path, 'r', encoding='utf-8') as f:
                    todos_resultados_historicos = json.load(f)
            except Exception: pass # Mantém lista vazia se falhar
    
    # --- ESTRATÉGIAS ---
    if estrategia_req == "foco_quentes":
        if not is_premium_user:
            return {"jogo": [], "estrategia_usada": "Foco nos Quentes (✨ Premium)", "erro_premium": True}
        estrategia_aplicada = f"{config['nome_exibicao']}: Foco nos Quentes (Premium)"
        # Lógica: Pega X números mais frequentes nos últimos 50 jogos, completa com aleatórios
        num_quentes_a_selecionar = numeros_a_gerar // 2 + (numeros_a_gerar % 2) # Metade ou um pouco mais
        num_quentes_para_amostra = num_quentes_a_selecionar + 5 # Pega mais para ter variedade
        
        numeros_quentes = calcular_numeros_quentes(todos_resultados_historicos, 50, num_quentes_para_amostra)
        
        if len(numeros_quentes) >= num_quentes_a_selecionar:
            jogo_final.extend(random.sample(numeros_quentes, num_quentes_a_selecionar))
        else: # Se não há quentes suficientes, pega todos que tem
            jogo_final.extend(numeros_quentes)
        
        # Completa com aleatórios não repetidos
        numeros_restantes_possiveis = [n for n in universo_numeros if n not in jogo_final]
        numeros_a_completar = numeros_a_gerar - len(jogo_final)
        
        if numeros_a_completar > 0:
            if len(numeros_restantes_possiveis) >= numeros_a_completar:
                jogo_final.extend(random.sample(numeros_restantes_possiveis, numeros_a_completar))
            else: # Se ainda faltar e não houver mais distintos
                jogo_final = [] # Falha, vai para fallback geral

    elif estrategia_req == "foco_frios":
        estrategia_aplicada = f"{config['nome_exibicao']}: Foco nos Frios (Atrasados)"
        num_frios_a_selecionar = numeros_a_gerar // 2
        num_frios_para_amostra = num_frios_a_selecionar + 5
        numeros_frios = calcular_numeros_frios(todos_resultados_historicos, universo_numeros, num_frios_para_amostra)

        if len(numeros_frios) >= num_frios_a_selecionar:
            jogo_final.extend(random.sample(numeros_frios, num_frios_a_selecionar))
        else:
            jogo_final.extend(numeros_frios)

        numeros_restantes_possiveis = [n for n in universo_numeros if n not in jogo_final]
        numeros_a_completar = numeros_a_gerar - len(jogo_final)
        if numeros_a_completar > 0:
            if len(numeros_restantes_possiveis) >= numeros_a_completar:
                jogo_final.extend(random.sample(numeros_restantes_possiveis, numeros_a_completar))
            else: jogo_final = []

    elif estrategia_req == "equilibrio_par_impar":
        estrategia_aplicada = f"{config['nome_exibicao']}: Equilíbrio Par/Ímpar"
        pares_target, impares_target = 0,0
        if lottery_name == "megasena" and numeros_a_gerar == 6: pares_target, impares_target = 3,3
        elif lottery_name == "lotofacil" and numeros_a_gerar == 15:
            if random.choice([True,False]): pares_target, impares_target = 7,8
            else: pares_target, impares_target = 8,7
        elif lottery_name == "quina" and numeros_a_gerar == 5:
            choice = random.choice([True,False]); 
            if choice : pares_target, impares_target = 2,3
            else: pares_target, impares_target = 3,2
        else: 
            pares_target = numeros_a_gerar // 2
            impares_target = numeros_a_gerar - pares_target
            
        numeros_pares_disp = [n for n in universo_numeros if n % 2 == 0]
        numeros_impares_disp = [n for n in universo_numeros if n % 2 != 0]
        random.shuffle(numeros_pares_disp); random.shuffle(numeros_impares_disp)

        # Garante que não tentamos pegar mais do que disponível
        pares_target = min(pares_target, len(numeros_pares_disp))
        impares_target = min(impares_target, len(numeros_impares_disp))

        jogo_final.extend(random.sample(numeros_pares_disp, pares_target))
        jogo_final.extend(random.sample(numeros_impares_disp, impares_target))
        
        jogo_final = list(set(jogo_final)) # Remove duplicatas se as seleções se sobrepuserem
        
        # Completa se faltarem números devido a amostragem menor que target ou set()
        while len(jogo_final) < numeros_a_gerar:
            numeros_disponiveis_geral = [n for n in universo_numeros if n not in jogo_final]
            if not numeros_disponiveis_geral: break 
            jogo_final.append(random.choice(numeros_disponiveis_geral))
            jogo_final = list(set(jogo_final)) # Garante unicidade após adicionar
    
    # Fallback
    if not jogo_final or len(jogo_final) != numeros_a_gerar or estrategia_req == "aleatorio_inteligente":
        if estrategia_req == "aleatorio_inteligente" or not jogo_final or len(jogo_final) != numeros_a_gerar :
            estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório Inteligente"
        else: 
            print(f"DEBUG: Estratégia '{estrategia_req}' não completou o jogo ({len(jogo_final)}/{numeros_a_gerar}). Usando fallback.")
            estrategia_aplicada = f"{estrategia_aplicada} (Fallback para Aleatório)"
        
        if (max_num - min_num + 1) >= numeros_a_gerar:
            jogo_final = sorted(random.sample(universo_numeros, numeros_a_gerar))
        else: 
            print(f"ERRO [gerar_jogo_ia]: Range insuficiente para {lottery_name} no fallback.")
            return {"jogo": [], "estrategia_usada": "Erro de Configuração (range insuficiente)"}

    # Garantia final
    if not jogo_final or len(jogo_final) != numeros_a_gerar:
         print(f"ERRO FATAL [gerar_jogo_ia]: Não foi possível gerar o número correto de dezenas ({len(jogo_final)}/{numeros_a_gerar}) para {lottery_name} com estratégia {estrategia_req}.")
         if (max_num - min_num + 1) >= numeros_a_gerar:
            jogo_final = sorted(random.sample(universo_numeros, numeros_a_gerar))
            estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório Simples (Emergência)"
         else: return {"jogo": [], "estrategia_usada": "Falha Crítica na Geração (Range)"}

    return {"jogo": sorted(list(set(jogo_final))), "estrategia_usada": estrategia_aplicada}


@app.route('/api/main/gerar_jogo/<lottery_name>', methods=['GET'])
def gerar_jogo_api(lottery_name):
    estrategia_req = request.args.get('estrategia', 'aleatorio_inteligente') 
    is_premium_simulado = request.args.get('premium_user', 'false').lower() == 'true' 
    
    print(f"API Endpoint: /gerar_jogo/{lottery_name} chamado com estrategia: {estrategia_req}, Premium Simulado: {is_premium_simulado}")
    lottery_name_lower = lottery_name.lower()
    if lottery_name_lower not in LOTTERY_CONFIG:
        return jsonify({"erro": f"Loteria '{lottery_name}' não configurada."}), 404

    todos_resultados_para_ia = None 
    processed_file_path = LOTTERY_CONFIG[lottery_name_lower].get("processed_json_file")
    if processed_file_path and os.path.exists(processed_file_path):
        try:
            with open(processed_file_path, 'r', encoding='utf-8') as f: todos_resultados_para_ia = json.load(f) 
        except Exception as e: print(f"AVISO: Não foi possível ler arquivo de resultados para IA da {lottery_name_lower}: {e}")
    else: print(f"AVISO: Arquivo JSON de resultados não encontrado para {lottery_name_lower} para uso na IA.")

    resultado_geracao = gerar_jogo_ia(lottery_name_lower, todos_resultados_para_ia, estrategia_req, is_premium_simulado) 
    
    if resultado_geracao.get("erro_premium"): # Checa a flag de erro premium
        return jsonify({"erro": "Acesso Negado", "detalhes": resultado_geracao.get("estrategia_usada"), "premium_requerido": True}), 403

    if not resultado_geracao.get("jogo") or len(resultado_geracao.get("jogo")) == 0 :
        detalhe_erro = resultado_geracao.get("estrategia_usada", "Falha interna na geração.")
        if "Erro" not in detalhe_erro and "Falha" not in detalhe_erro: detalhe_erro = "Não foi possível gerar um palpite válido."
        return jsonify({"erro": f"Não foi possível gerar jogo para {lottery_name}.", "detalhes": detalhe_erro}), 500

    if resultado_geracao.get("jogo"): platform_stats_data["jogos_gerados_total"] += 1
    return jsonify(resultado_geracao)


if __name__ == '__main__':
    print(f"Servidor Flask rodando. Diretório de dados: {DATA_DIR}")
    for key_lottery in LOTTERY_CONFIG.keys(): 
        config_loteria = LOTTERY_CONFIG[key_lottery] 
        master_file_path = config_loteria.get("master_file_path")
        if master_file_path:
            master_file_xlsx_path = master_file_path
            master_file_csv_path = master_file_path.replace(".xlsx", ".csv")
            arquivo_mestre_encontrado = False
            if os.path.exists(master_file_xlsx_path): arquivo_mestre_encontrado = True
            elif os.path.exists(master_file_csv_path): arquivo_mestre_encontrado = True 
            if arquivo_mestre_encontrado:
                print(f"INFO: Tentando processar arquivo local para {key_lottery.upper()} na inicialização...")
                process_local_lottery_file(key_lottery)
            else:
                processed_json_path_check = config_loteria.get("processed_json_file")
                if processed_json_path_check and not os.path.exists(processed_json_path_check): print(f"AVISO: Arquivo mestre para {key_lottery.upper()} NÃO encontrado E JSON processado '{processed_json_path_check}' também NÃO existe.")
                elif not processed_json_path_check: print(f"AVISO: 'processed_json_file' não configurado para {key_lottery.upper()} e mestre não encontrado.")
                else: print(f"INFO: Arquivo mestre para {key_lottery.upper()} não encontrado. Usando JSON existente: '{processed_json_path_check}'")
        else: print(f"AVISO: 'master_file_path' não configurado para {key_lottery.upper()}")
    app.run(host='0.0.0.0', port=5000, debug=True)