import pandas as pd
import os
import json
import re
import requests
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Importa a função de verificação do outro arquivo
from verificador_jogos import verificar_jogos_para_novo_resultado, initialize_firebase_admin_verificador as init_fb_verificador

load_dotenv()

DIRETORIO_SCRIPT_ATUAL = os.path.dirname(os.path.abspath(__file__))
DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS = os.path.join(DIRETORIO_SCRIPT_ATUAL, "arquivos_excel_caixa")
DIRETORIO_JSON_SAIDA_LOCAL_TEMP = os.path.join(DIRETORIO_SCRIPT_ATUAL, "lottery_data_temp_for_upload")

if not os.path.exists(DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS):
    os.makedirs(DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS)
if not os.path.exists(DIRETORIO_JSON_SAIDA_LOCAL_TEMP):
    os.makedirs(DIRETORIO_JSON_SAIDA_LOCAL_TEMP)

BLOB_ACCESS_TOKEN = os.environ.get("BLOB_READ_WRITE_TOKEN")

SERVICE_ACCOUNT_KEY_PATH_PROCESSOR = os.path.join(DIRETORIO_SCRIPT_ATUAL, "serviceAccountKey.json")
db_firestore = None
firebase_app_processor = None # Guardar a instância da app

try:
    app_name_proc = 'lotteryProcessorAppMain'
    if app_name_proc not in firebase_admin._apps:
        service_account_json_str_env = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
        if service_account_json_str_env:
            service_account_info_env = json.loads(service_account_json_str_env)
            cred_proc = credentials.Certificate(service_account_info_env)
            print(f"Inicializando Firebase Admin SDK para {app_name_proc} (Processador) via ENV VAR.")
            firebase_app_processor = firebase_admin.initialize_app(cred_proc, name=app_name_proc)
        elif os.path.exists(SERVICE_ACCOUNT_KEY_PATH_PROCESSOR):
            cred_proc = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH_PROCESSOR)
            print(f"Inicializando Firebase Admin SDK para {app_name_proc} (Processador) via arquivo local.")
            firebase_app_processor = firebase_admin.initialize_app(cred_proc, name=app_name_proc)
        else:
            print(f"ALERTA [{app_name_proc}]: Nem FIREBASE_SERVICE_ACCOUNT_JSON (ENV VAR) nem '{SERVICE_ACCOUNT_KEY_PATH_PROCESSOR}' (local) encontrados.")
    else: # App já existe
        print(f"Firebase Admin SDK ({app_name_proc}) já inicializado (Processador). Reutilizando.")
        firebase_app_processor = firebase_admin.get_app(name=app_name_proc)

    if firebase_app_processor:
        db_firestore = firestore.client(app=firebase_app_processor)
        print(f"Cliente Firestore obtido para {app_name_proc} (Processador).")
        # Tenta inicializar o verificador também, passando o nome da app se necessário
        # para que ele possa tentar reutilizar ou coexistir.
        init_fb_verificador(app_name_suffix=f'VerifViaProc')

except Exception as e_fb_admin_proc:
    print(f"Erro GERAL ao inicializar Firebase Admin SDK no processador: {e_fb_admin_proc}")


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
        "col_concurso": "Concurso",
        "col_data_sorteio": "Data do Sorteio",
        "cols_bolas_prefix": "Bola",
        "num_bolas_no_arquivo": 6,
        "col_ganhadores_principal": "Ganhadores 6 acertos",
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 6 acertos",
        "col_rateio_quina": "Rateio 5 acertos",
        "col_rateio_quadra": "Rateio 4 acertos"
    },
    "lotofacil": {
        "modalidade_param_value": "Lotofácil",
        "master_file_name_local": MASTER_FILES_LOCAL_NAMES.get("lotofacil"),
        "processed_json_name": "lotofacil_processed_results.json",
        "col_concurso": "Concurso",
        "col_data_sorteio": "Data Sorteio",
        "cols_bolas_prefix": "Bola",
        "num_bolas_no_arquivo": 15,
        "col_ganhadores_principal": "Ganhadores 15 acertos",
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 15 acertos"
    },
    "lotomania": {
        "modalidade_param_value": "Lotomania",
        "master_file_name_local": MASTER_FILES_LOCAL_NAMES.get("lotomania"),
        "manual_csv_filename": MASTER_FILES_LOCAL_NAMES.get("lotomania_csv_manual"),
        "processed_json_name": "lotomania_processed_results.json",
        "col_concurso": "Concurso",
        "col_data_sorteio": "Data Sorteio",
        "cols_bolas_prefix": "Bola",
        "num_bolas_no_arquivo": 20,
        "col_ganhadores_principal": "Ganhadores 20 acertos",
        "col_cidade_uf_principal": "Cidade / UF",
        "col_rateio_principal": "Rateio 20 acertos"
    },
    "quina": {
        "modalidade_param_value": "Quina",
        "master_file_name_local": MASTER_FILES_LOCAL_NAMES.get("quina"),
        "processed_json_name": "quina_processed_results.json",
        "col_concurso": "Concurso",
        "col_data_sorteio": "Data Sorteio",
        "cols_bolas_prefix": "Bola",
        "num_bolas_no_arquivo": 5,
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
        response.raise_for_status()
        with open(caminho_completo_destino, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192): f.write(chunk)
        print(f"SUCESSO [{loteria_key_func.upper()}]: Arquivo salvo em {caminho_completo_destino}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"ERRO ao baixar para {loteria_key_func.upper()}: {e}")
    return False

def upload_json_to_vercel_blob(pathname_in_blob, json_content_str, loteria_key_func):
    if not BLOB_ACCESS_TOKEN:
        print(f"ERRO CRÍTICO [{loteria_key_func.upper()}]: BLOB_READ_WRITE_TOKEN não configurado.")
        return None
    upload_url = f"https://blob.vercel-storage.com/{pathname_in_blob}"
    headers = {
        "Authorization": f"Bearer {BLOB_ACCESS_TOKEN}",
        "Content-Type": "application/json; charset=utf-8",
        "x-api-version": "6" 
    }
    print(f"Fazendo upload de '{pathname_in_blob}' para Vercel Blob...")
    try:
        response = requests.put(upload_url, headers=headers, data=json_content_str.encode('utf-8'))
        response.raise_for_status()
        blob_data = response.json()
        blob_access_url = blob_data.get('url') 
        print(f"SUCESSO [{loteria_key_func.upper()}]: JSON enviado para Vercel Blob. URL: {blob_access_url}")
        return blob_access_url
    except requests.exceptions.HTTPError as http_err:
        print(f"ERRO HTTP ao enviar JSON para Vercel Blob ({loteria_key_func.upper()}): {http_err} - {http_err.response.text if http_err.response else ''}")
    except requests.exceptions.RequestException as e_blob:
        print(f"ERRO de requisição ao enviar JSON para Vercel Blob ({loteria_key_func.upper()}): {e_blob}")
    except Exception as e_gen_blob:
        print(f"Erro genérico ao enviar para Vercel Blob ({loteria_key_func.upper()}): {e_gen_blob}")
    return None

def processar_e_salvar_loteria_json(loteria_key_func, config_loteria_func):
    global db_firestore # Acessa o db_firestore inicializado no escopo do módulo
    print(f"Iniciando processamento JSON para {loteria_key_func.upper()}")
    json_file_name_for_blob = config_loteria_func["processed_json_name"]
    df = None
    
    if loteria_key_func == 'lotomania':
        manual_csv_filename = config_loteria_func.get("manual_csv_filename")
        if not manual_csv_filename: print(f"ERRO [{loteria_key_func.upper()}]: CSV manual não configurado."); return
        filepath_to_read = os.path.join(DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS, manual_csv_filename)
        if os.path.exists(filepath_to_read):
            try: df = pd.read_csv(filepath_to_read, sep=',', dtype=str, na_values=['-'], keep_default_na=True, engine='python')
            except Exception: 
                try: df = pd.read_csv(filepath_to_read, sep=';', dtype=str, na_values=['-'], keep_default_na=True, engine='python')
                except Exception as e_csv: print(f"ERRO ao ler CSV {filepath_to_read}: {e_csv}"); return
        else: print(f"AVISO [{loteria_key_func.upper()}]: CSV manual '{manual_csv_filename}' não encontrado."); return
    else:
        master_filename_xlsx = config_loteria_func.get("master_file_name_local")
        filepath_to_read = os.path.join(DIRETORIO_ARQUIVOS_MESTRE_BAIXADOS, master_filename_xlsx)
        if os.path.exists(filepath_to_read):
            try: df = pd.read_excel(filepath_to_read, engine='openpyxl', dtype=str, na_values=['-'], keep_default_na=True)
            except Exception as e: print(f"ERRO ao ler XLSX {filepath_to_read}: {e}"); return
        else: print(f"AVISO: Arquivo mestre {master_filename_xlsx} não encontrado."); return

    if df is None: print(f"AVISO FINAL: DataFrame não carregado para {loteria_key_func.upper()}."); return

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
            try: dt_obj = pd.to_datetime(data_str, errors='coerce', dayfirst=True); data_formatada = dt_obj.strftime('%d/%m/%Y') if pd.notna(dt_obj) else data_str
            except Exception: pass
            
            dezenas_lidas = []
            for i in range(1, num_bolas_a_ler + 1):
                dezena_val = row.get(f'{cols_bolas_prefix}{i}');
                if not pd.isna(dezena_val) and str(dezena_val).strip().isdigit(): dezenas_lidas.append(int(str(dezena_val).strip()))
            
            if len(dezenas_lidas) == num_bolas_a_ler:
                sorteio_data = {"concurso": concurso_val, "data": data_formatada, "numeros": sorted(dezenas_lidas)}
                if col_ganhadores_principal and col_cidade_uf_principal and col_rateio_principal:
                    ganhadores_val = row.get(col_ganhadores_principal, '0'); cidade_uf_val = row.get(col_cidade_uf_principal, '')
                    rateio_val_str = row.get(col_rateio_principal, '0')
                    cidades_lista, num_ganhadores_parsed = parse_ganhadores_cidades(str(cidade_uf_val), str(ganhadores_val))
                    
                    sorteio_data["ganhadores_principal_contagem"] = num_ganhadores_parsed
                    sorteio_data["cidades_ganhadoras_principal"] = cidades_lista
                    # Salva o rateio como string formatada, a conversão para float ocorre no main.py ou verificador
                    sorteio_data["rateio_principal_valor"] = f"R$ {parse_currency_to_float(str(rateio_val_str)):_.2f}".replace('.', ',').replace('_', '.') if num_ganhadores_parsed > 0 else "R$ 0,00"


                    if loteria_key_func == 'megasena':
                        if col_rateio_quina_ms:
                            rateio_quina_val_str = row.get(col_rateio_quina_ms, '0')
                            sorteio_data["rateio_quina_valor"] = f"R$ {parse_currency_to_float(str(rateio_quina_val_str)):_.2f}".replace('.', ',').replace('_', '.')
                        if col_rateio_quadra_ms:
                            rateio_quadra_val_str = row.get(col_rateio_quadra_ms, '0')
                            sorteio_data["rateio_quadra_valor"] = f"R$ {parse_currency_to_float(str(rateio_quadra_val_str)):_.2f}".replace('.', ',').replace('_', '.')
                
                results_list.append(sorteio_data)
        except Exception as e_row: print(f"ERRO ao processar linha {index+1} ({loteria_key_func.upper()}): {e_row}")
    
    if results_list:
        results_list.sort(key=lambda x: x["concurso"], reverse=True)
        json_content_to_upload = json.dumps(results_list, ensure_ascii=False, separators=(',', ':'))
        
        blob_url_retornado = upload_json_to_vercel_blob(json_file_name_for_blob, json_content_to_upload, loteria_key_func)
        
        if blob_url_retornado and db_firestore:
            try:
                doc_ref = db_firestore.collection('lottery_data_source_urls').document(loteria_key_func)
                doc_ref.set({
                    'lottery_name': loteria_key_func,
                    'blob_url': blob_url_retornado,
                    'updated_at': firestore.SERVER_TIMESTAMP,
                    'latest_contest_number': results_list[0]['concurso'] if results_list else None
                })
                print(f"URL do Blob para {loteria_key_func.upper()} salvo no Firestore.")

                # >>> INÍCIO DA INTEGRAÇÃO COM VERIFICADOR_JOGOS <<<
                if results_list: # Se há resultados, o primeiro é o mais novo
                    novo_resultado_oficial_para_verificar = results_list[0]
                    print(f"Disparando verificação de jogos para {loteria_key_func.upper()}, concurso {novo_resultado_oficial_para_verificar.get('concurso')}")
                    verificar_jogos_para_novo_resultado(loteria_key_func, novo_resultado_oficial_para_verificar, db_client=db_firestore)
                # >>> FIM DA INTEGRAÇÃO COM VERIFICADOR_JOGOS <<<

            except Exception as e_firestore:
                print(f"ERRO ao salvar URL do Blob ou ao chamar verificação para {loteria_key_func.upper()}: {e_firestore}")

        elif not blob_url_retornado:
            processed_json_path_local_temp = os.path.join(DIRETORIO_JSON_SAIDA_LOCAL_TEMP, json_file_name_for_blob)
            try:
                with open(processed_json_path_local_temp, 'w', encoding='utf-8') as f_local:
                    json.dump(results_list, f_local, ensure_ascii=False, indent=4) 
                print(f"FALHA NO UPLOAD [{loteria_key_func.upper()}]: JSON salvo localmente em {processed_json_path_local_temp}.")
            except Exception as e_json_local:
                print(f"ERRO ao salvar JSON local de fallback {processed_json_path_local_temp}: {e_json_local}")
    else:
        print(f"AVISO FINAL [{loteria_key_func.upper()}]: Nenhum resultado válido processado.")

if __name__ == '__main__':
    if not BLOB_ACCESS_TOKEN:
        print("ERRO CRÍTICO: A variável de ambiente BLOB_READ_WRITE_TOKEN não está configurada.")
        exit()
    if not db_firestore: # Verifica se db_firestore foi inicializado
        print("ERRO CRÍTICO: Firebase Admin (db_firestore) não foi inicializado no processador. URLs dos Blobs não serão salvos e a verificação automática não ocorrerá.")
        # Você pode optar por sair ou continuar sem a funcionalidade do Firestore
        # exit() 

    print("Iniciando script de download, processamento e UPLOAD para Vercel Blob...")
    
    baixar_novamente = input("Deseja tentar baixar novamente os arquivos Excel da Caixa? (s/N): ").strip().lower()
    fazer_download = baixar_novamente == 's'

    for loteria_key_loop, config_loop in LOTTERY_CONFIG_PROCESSAMENTO.items():
        print(f"\n--- Processando {loteria_key_loop.upper()} ---")
        if fazer_download and loteria_key_loop != 'lotomania': # Lotomania usa CSV manual
            baixar_arquivo_loteria(loteria_key_loop, config_loop)
        elif fazer_download and loteria_key_loop == 'lotomania':
            print(f"AVISO [{loteria_key_loop.upper()}]: Download automático não aplicável. Use o CSV manual.")

        processar_e_salvar_loteria_json(loteria_key_loop, config_loop)
            
    print("\nProcessamento, tentativas de uploads e verificações de jogos concluídos.")