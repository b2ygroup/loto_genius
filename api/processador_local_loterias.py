import pandas as pd
import os
import json
import re
import requests
import shutil

# --- CONFIGURAÇÕES DE DIRETÓRIO ---
# Assume que este script (processador_local_loterias.py) está DENTRO da pasta 'api'
# E que a pasta 'lottery_data' está NO MESMO NÍVEL que este script, dentro de 'api'
DIRETORIO_SCRIPT_ATUAL = os.path.dirname(os.path.abspath(__file__))

DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS = os.path.join(DIRETORIO_SCRIPT_ATUAL, "arquivos_excel_caixa")
DIRETORIO_JSON_SAIDA_API = os.path.join(DIRETORIO_SCRIPT_ATUAL, "lottery_data")

if not os.path.exists(DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS):
    os.makedirs(DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS)
if not os.path.exists(DIRETORIO_JSON_SAIDA_API):
    os.makedirs(DIRETORIO_JSON_SAIDA_API)

# --- CONFIGURAÇÃO DAS LOTERIAS ---
MASTER_FILES_LOCAL_NAMES = {
    "lotofacil": "Lotofácil_Resultados.xlsx",
    "megasena": "Mega-Sena_Resultados.xlsx",
    "lotomania": "Lotomania_Resultados.xlsx",
    "lotomania_csv_manual": "Lotomania_Resultados_MANUAL.csv",
    "quina": "Quina_Resultados.xlsx"
}

DOWNLOAD_URL_BASE = "https://servicebus2.caixa.gov.br/portaldeloterias/api/resultados/download"

LOTTERY_CONFIG_PROCESSAMENTO = {
    "megasena": {
        "modalidade_param_value": "Mega-Sena",
        "master_file_name_local": MASTER_FILES_LOCAL_NAMES.get("megasena"),
        "processed_json_name": "megasena_processed_results.json",
        "col_concurso": "Concurso", "col_data_sorteio": "Data do Sorteio",
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 6,
        "col_ganhadores_principal": "Ganhadores 6 acertos",
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 6 acertos"
    },
    "lotofacil": {
        "modalidade_param_value": "Lotofácil",
        "master_file_name_local": MASTER_FILES_LOCAL_NAMES.get("lotofacil"),
        "processed_json_name": "lotofacil_processed_results.json",
        "col_concurso": "Concurso", "col_data_sorteio": "Data Sorteio",
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 15,
        "col_ganhadores_principal": "Ganhadores 15 acertos",
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 15 acertos"
    },
    "lotomania": {
        "modalidade_param_value": "Lotomania",
        "master_file_name_local": MASTER_FILES_LOCAL_NAMES.get("lotomania"),
        "manual_csv_filename": MASTER_FILES_LOCAL_NAMES.get("lotomania_csv_manual"),
        "processed_json_name": "lotomania_processed_results.json",
        "col_concurso": "Concurso", "col_data_sorteio": "Data Sorteio",
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 20,
        "col_ganhadores_principal": "Ganhadores 20 acertos",
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 20 acertos"
    },
    "quina": {
        "modalidade_param_value": "Quina",
        "master_file_name_local": MASTER_FILES_LOCAL_NAMES.get("quina"),
        "processed_json_name": "quina_processed_results.json",
        "col_concurso": "Concurso", "col_data_sorteio": "Data Sorteio",
        "cols_bolas_prefix": "Bola", "num_bolas_no_arquivo": 5,
        "col_ganhadores_principal": "Ganhadores 5 acertos",
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 5 acertos"
    }
}

def parse_currency_to_float(currency_str):
    if pd.isna(currency_str): return 0.0
    if not isinstance(currency_str, str): currency_str = str(currency_str)
    cleaned_str = currency_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
    if not cleaned_str or cleaned_str == '-': return 0.0
    try: return float(cleaned_str)
    except ValueError: return 0.0

def parse_ganhadores_cidades(cidade_uf_str, num_ganhadores_str):
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
            contagem_na_string = 1
            cidade_limpa = entry
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

def baixar_arquivo_loteria(loteria_key_func, config_loteria_func):
    modalidade_valor = config_loteria_func.get("modalidade_param_value")
    nome_arquivo_local_func = config_loteria_func.get("master_file_name_local")
    if not modalidade_valor or not nome_arquivo_local_func:
        print(f"ERRO [{loteria_key_func.upper()}]: Configuração de download incompleta.")
        return False
    caminho_completo_destino = os.path.join(DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS, nome_arquivo_local_func)
    params = {'modalidade': modalidade_valor}
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://loterias.caixa.gov.br/'
    })
    try:
        print(f"Baixando arquivo para {loteria_key_func.upper()} de {DOWNLOAD_URL_BASE} com params {params}...")
        response = session.get(DOWNLOAD_URL_BASE, params=params, stream=True, timeout=60, allow_redirects=True)
        print(f"Status da resposta para {loteria_key_func.upper()}: {response.status_code}")
        response.raise_for_status()
        with open(caminho_completo_destino, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): f.write(chunk)
        print(f"SUCESSO [{loteria_key_func.upper()}]: Arquivo salvo em {caminho_completo_destino}")
        return True
    except requests.exceptions.HTTPError as http_err:
        print(f"ERRO HTTP ao baixar para {loteria_key_func.upper()}: {http_err}")
        if hasattr(http_err, 'response') and http_err.response is not None:
            try: error_content = http_err.response.text[:1000]
            except UnicodeDecodeError: error_content = str(http_err.response.content[:1000])
            print(f"Conteúdo da resposta (detalhes): {error_content}")
    except requests.exceptions.RequestException as e:
        print(f"ERRO de Conexão/Requisição ao baixar para {loteria_key_func.upper()}: {e}")
    except Exception as e:
        print(f"ERRO inesperado ao salvar {loteria_key_func.upper()}: {e}")
    return False

def processar_e_salvar_loteria_json(loteria_key_func, config_loteria_func):
    print(f"Iniciando processamento JSON para {loteria_key_func.upper()}")
    
    processed_json_path_api = os.path.join(DIRETORIO_JSON_SAIDA_API, config_loteria_func["processed_json_name"])
    df = None

    if loteria_key_func == 'lotomania':
        manual_csv_filename = config_loteria_func.get("manual_csv_filename")
        if not manual_csv_filename:
            print(f"ERRO [{loteria_key_func.upper()}]: Nome do arquivo CSV manual não configurado.")
            return
        
        filepath_to_read = os.path.join(DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS, manual_csv_filename)
        print(f"INFO [{loteria_key_func.upper()}]: Tentando ler CSV salvo manually: {filepath_to_read}")
        if os.path.exists(filepath_to_read):
            try:
                df = pd.read_csv(filepath_to_read, sep=',', dtype=str, na_values=['-'], keep_default_na=True, engine='python')
                print(f"Sucesso ao ler CSV manual para {loteria_key_func.upper()} (usando sep=',').")
            except pd.errors.ParserError as pe:
                print(f"ERRO de Parser ao ler CSV manual da Lotomania {filepath_to_read} com sep=',' : {pe}")
                print(f"Tentando com separador ';' para Lotomania...")
                try:
                    df = pd.read_csv(filepath_to_read, sep=';', dtype=str, na_values=['-'], keep_default_na=True, engine='python')
                    print(f"Sucesso ao ler CSV manual para {loteria_key_func.upper()} (usando sep=';').")
                except Exception as e_csv_semicolon:
                    print(f"ERRO ao ler CSV manual da Lotomania {filepath_to_read} também com sep=';' : {type(e_csv_semicolon).__name__} - {e_csv_semicolon}")
                    return
            except Exception as e_csv:
                print(f"ERRO ao ler CSV manual da Lotomania {filepath_to_read}: {type(e_csv).__name__} - {e_csv}")
                return
        else:
            print(f"AVISO [{loteria_key_func.upper()}]: Arquivo CSV manual '{manual_csv_filename}' não encontrado em '{DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS}'.")
            print(f"Por favor, baixe o XLSX da Lotomania, abra-o no Excel/Calc, salve como CSV com o nome '{manual_csv_filename}' nesta pasta.")
            return
    else:
        master_filename_xlsx = config_loteria_func.get("master_file_name_local")
        filepath_to_read = os.path.join(DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS, master_filename_xlsx)
        if os.path.exists(filepath_to_read):
            try:
                print(f"Lendo XLSX: {filepath_to_read}")
                df = pd.read_excel(filepath_to_read, engine='openpyxl', dtype=str,
                                   na_values=['-'], keep_default_na=True)
                print(f"Sucesso ao ler {filepath_to_read} para {loteria_key_func.upper()}.")
            except ValueError as ve_read_xlsx:
                print(f"ERRO DE VALOR ao ler XLSX {filepath_to_read}: {ve_read_xlsx}")
                return
            except ImportError:
                print(f"ERRO CRÍTICO: 'openpyxl' não instalado.")
                return
            except Exception as e:
                print(f"ERRO CRÍTICO GERAL ao ler XLSX {filepath_to_read}: {type(e).__name__} - {e}")
                return
        else:
            print(f"AVISO: Arquivo mestre {master_filename_xlsx} não encontrado para {loteria_key_func.upper()}.")
            return

    if df is None:
        print(f"AVISO FINAL: DataFrame não foi carregado para {loteria_key_func.upper()}.")
        return

    col_concurso = config_loteria_func["col_concurso"]
    col_data = config_loteria_func["col_data_sorteio"]
    cols_bolas_prefix = config_loteria_func["cols_bolas_prefix"]
    num_bolas_a_ler = config_loteria_func["num_bolas_no_arquivo"]
    col_ganhadores_principal = config_loteria_func.get("col_ganhadores_principal")
    col_cidade_uf_principal = config_loteria_func.get("col_cidade_uf_principal")
    col_rateio_principal = config_loteria_func.get("col_rateio_principal")
    results_list = []

    for index, row in df.iterrows():
        try:
            concurso_str = str(row.get(col_concurso, '')).strip()
            data_str = str(row.get(col_data, '')).strip()
            concurso_str_cleaned = concurso_str.replace(',', '')
            if pd.isna(concurso_str_cleaned) or not concurso_str_cleaned or \
               concurso_str_cleaned.lower() == 'nan' or concurso_str_cleaned == '-':
                continue
            try: concurso_val = int(float(concurso_str_cleaned))
            except ValueError: continue
            
            if pd.isna(data_str) or not data_str or \
               data_str.lower() == 'nan' or data_str == '-':
                continue
            
            data_formatada = data_str
            try:
                dt_obj = pd.to_datetime(data_str, errors='coerce', dayfirst=True)
                if pd.notna(dt_obj): data_formatada = dt_obj.strftime('%d/%m/%Y')
            except Exception: pass

            dezenas_lidas = []
            for col_dezena_idx in range(1, num_bolas_a_ler + 1):
                col_dezena_nome = f'{cols_bolas_prefix}{col_dezena_idx}'
                if col_dezena_nome in df.columns:
                    dezena_val = row.get(col_dezena_nome)
                    if pd.isna(dezena_val): continue
                    dezena_str = str(dezena_val).strip()
                    if dezena_str.isdigit(): dezenas_lidas.append(int(dezena_str))
            
            if len(dezenas_lidas) == num_bolas_a_ler:
                sorteio_data = {"concurso": concurso_val, "data": data_formatada, "numeros": sorted(dezenas_lidas)}
                if col_ganhadores_principal and col_cidade_uf_principal and col_rateio_principal and \
                   col_ganhadores_principal in df.columns and \
                   col_cidade_uf_principal in df.columns and \
                   col_rateio_principal in df.columns:
                    ganhadores_val = row.get(col_ganhadores_principal, '0')
                    cidade_uf_val = row.get(col_cidade_uf_principal, '')
                    rateio_val = row.get(col_rateio_principal, '0')
                    ganhadores_str = str(ganhadores_val if not pd.isna(ganhadores_val) else '0').strip()
                    cidade_uf_str = str(cidade_uf_val if not pd.isna(cidade_uf_val) else '').strip()
                    rateio_str = str(rateio_val if not pd.isna(rateio_val) else '0').strip()
                    cidades_lista, num_ganhadores_parsed = parse_ganhadores_cidades(cidade_uf_str, ganhadores_str)
                    sorteio_data["ganhadores_principal_contagem"] = num_ganhadores_parsed
                    sorteio_data["cidades_ganhadoras_principal"] = cidades_lista
                    sorteio_data["rateio_principal_valor"] = parse_currency_to_float(rateio_str) if num_ganhadores_parsed > 0 else 0.0
                results_list.append(sorteio_data)
        except Exception as e_row:
            print(f"ERRO GERAL ao processar linha {index+1} ({loteria_key_func.upper()}): {type(e_row).__name__} - {e_row}. Concurso: {concurso_str if 'concurso_str' in locals() else 'N/A'}. Dados da linha (parcial): {dict(list(row.items())[:5]) if isinstance(row, pd.Series) else str(row)[:150]}")
            continue

    if results_list:
        results_list.sort(key=lambda x: x["concurso"], reverse=True)
        try:
            with open(processed_json_path_api, 'w', encoding='utf-8') as f:
                json.dump(results_list, f, ensure_ascii=False, indent=4)
            print(f"SUCESSO [{loteria_key_func.upper()}]: JSON salvo diretamente em {processed_json_path_api} com {len(results_list)} concursos.")
        except Exception as e_json:
            print(f"ERRO ao salvar JSON em {processed_json_path_api}: {e_json}")
    else:
        print(f"AVISO FINAL [{loteria_key_func.upper()}]: Nenhum resultado válido processado.")


if __name__ == '__main__':
    print("Iniciando script de download e processamento de dados das loterias...")
    print(f"Arquivos Excel baixados serão salvos em: {os.path.abspath(DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS)}")
    print(f"Arquivos JSON processados serão salvos DIRETAMENTE em: {os.path.abspath(DIRETORIO_JSON_SAIDA_API)} para deploy.")

    baixar_novamente = input("Deseja tentar baixar novamente os arquivos Excel da Caixa? (s/N): ").strip().lower()
    fazer_download = baixar_novamente == 's'

    for loteria_key_loop, config_loop in LOTTERY_CONFIG_PROCESSAMENTO.items():
        print(f"\n--- Processando {loteria_key_loop.upper()} ---")
        
        if fazer_download:
            download_sucesso = baixar_arquivo_loteria(loteria_key_loop, config_loop)
            if not download_sucesso and loteria_key_loop == 'lotomania':
                print(f"AVISO [{loteria_key_loop.upper()}]: Download do XLSX falhou. "
                      f"Tentará usar o CSV manual '{config_loop.get('manual_csv_filename')}' se existir.")
            elif not download_sucesso:
                 print(f"AVISO [{loteria_key_loop.upper()}]: Download falhou. Tentando processar arquivo local existente (se houver).")
        else:
            print(f"Download pulado para {loteria_key_loop.upper()} conforme instrução do usuário.")
        
        processar_e_salvar_loteria_json(loteria_key_loop, config_loop)
            
    print("\nProcessamento local concluído.")
    print(f"Os arquivos JSON foram salvos em '{os.path.abspath(DIRETORIO_JSON_SAIDA_API)}'. "
          "Certifique-se de que esta pasta com os JSONs atualizados seja incluída no seu próximo deploy na Vercel.")