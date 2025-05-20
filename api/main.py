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

app = Flask(__name__)
CORS(app)
app.logger.setLevel(logging.INFO)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_ROOT, 'lottery_data')

LOTTERY_CONFIG = { # Mesma configuração de antes
    "megasena": {"nome_exibicao": "Mega-Sena", "min": 1, "max": 60, "count": 6, "color": "#209869", "processed_json_file": os.path.join(DATA_DIR, "megasena_processed_results.json"), "count_sorteadas": 6},
    "lotofacil": {"nome_exibicao": "Lotofácil", "min": 1, "max": 25, "count": 15, "color": "#930089", "processed_json_file": os.path.join(DATA_DIR, "lotofacil_processed_results.json"), "count_sorteadas": 15},
    "lotomania": {"nome_exibicao": "Lotomania", "min": 0, "max": 99, "count_apostadas": 50, "count_sorteadas": 20, "color": "#f78100", "processed_json_file": os.path.join(DATA_DIR, "lotomania_processed_results.json")},
    "quina": {"nome_exibicao": "Quina", "min": 1, "max": 80, "count": 5, "color": "#260085", "processed_json_file": os.path.join(DATA_DIR, "quina_processed_results.json"), "count_sorteadas": 5}
}

platform_stats_data = { # Mesma de antes
    "jogos_gerados_total": random.randint(19000, 31000),
    "jogos_premiados_estimativa": random.randint(280, 780),
    "valor_premios_estimativa_bruto": random.uniform(98000, 360000)
}

# --- Funções Auxiliares (parse_currency_to_float, etc. como antes) ---
def format_currency(value):
    if isinstance(value, (int, float)): return f"R$ {value:_.2f}".replace('.', ',').replace('_', '.')
    return "R$ 0,00"

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
        if num_ganhadores > 0: # Ajusta tamanho da lista
            if not cidades_parsed: cidades_parsed = ["Não especificada"] * num_ganhadores
            elif len(cidades_parsed) < num_ganhadores:
                if len(cidades_parsed) == 1: cidades_parsed = [cidades_parsed[0]] * num_ganhadores
                else: cidades_parsed.extend(["Não especificada"] * (num_ganhadores - len(cidades_parsed)))
            elif len(cidades_parsed) > num_ganhadores: cidades_parsed = cidades_parsed[:num_ganhadores]
    elif num_ganhadores > 0: cidades_parsed = ["Não especificada"] * num_ganhadores
    return cidades_parsed, num_ganhadores

def load_processed_lottery_data(lottery_key):
    app.logger.info(f"[load_data] Solicitado para {lottery_key.upper()} de {DATA_DIR}")
    # ... (resto da função como antes, com logs)
    config = LOTTERY_CONFIG.get(lottery_key)
    if not config: app.logger.error(f"[load_data] Config não encontrada para {lottery_key}"); return None
    processed_json_path = config.get("processed_json_file")
    if not processed_json_path: app.logger.error(f"[load_data] Caminho JSON não configurado para {lottery_key}"); return None
    if not os.path.exists(processed_json_path): app.logger.error(f"[load_data] ARQUIVO JSON NÃO ENCONTRADO: {processed_json_path}"); return None
    try:
        with open(processed_json_path, 'r', encoding='utf-8') as f: data = json.load(f)
        app.logger.info(f"[load_data] Sucesso ao carregar {lottery_key.upper()}")
        return data
    except Exception as e: app.logger.error(f"[load_data] ERRO ao ler/parsear JSON {processed_json_path}: {e}"); return None

def get_data_for_stats(lottery_name_lower):
    # ... (lógica como antes, com logs)
    app.logger.info(f"[get_data_for_stats] Solicitado para {lottery_name_lower}")
    if lottery_name_lower not in LOTTERY_CONFIG:
        app.logger.warning(f"[get_data_for_stats] Loteria não configurada: {lottery_name_lower}")
        return None, {"erro": f"Loteria '{lottery_name_lower}' não configurada."}, 404
    all_results = load_processed_lottery_data(lottery_name_lower)
    if not all_results:
        app.logger.warning(f"[get_data_for_stats] Dados indisponíveis para {lottery_name_lower}")
        return None, {"erro": f"Dados de {lottery_name_lower.upper()} indisponíveis."}, 404
    return all_results, None, None

def combinations_count(n, k): # ... (lógica como antes)
     if k < 0 or k > n: return 0
     if k == 0 or k == n: return 1
     if k > n // 2: k = n - k
     res = 1
     for i in range(k): res = res * (n - i) // (i + 1)
     return res

# --- ROTAS DA API ---
@app.route('/')
def api_base_root():
    app.logger.info("Rota / (raiz da função api/main.py) acessada")
    return jsonify({"message": "API Loto Genius Python (api/main.py).", 
                    "note": "Endpoints principais estão em /api/main/..." })

@app.route('/api/main/')
def api_main_home():
    app.logger.info("Rota /api/main/ acessada")
    return jsonify({"mensagem": "API Loto Genius AI Funcionando!", "versao": "Refatorada v4.0"})

@app.route('/api/main/platform-stats', methods=['GET'])
def get_platform_stats():
    app.logger.info("Endpoint /api/main/platform-stats acessado")
    # ... (lógica de platform_stats_data e format_currency)
    platform_stats_data["jogos_gerados_total"] += random.randint(1, 7)
    if random.random() < 0.03:
        platform_stats_data["jogos_premiados_estimativa"] += random.randint(1,2)
        platform_stats_data["valor_premios_estimativa_bruto"] += random.uniform(1000, 15000)
    return jsonify({
        "jogos_gerados_total": platform_stats_data["jogos_gerados_total"],
        "jogos_premiados_estimativa": platform_stats_data["jogos_premiados_estimativa"],
        "valor_premios_estimativa_formatado": format_currency(platform_stats_data["valor_premios_estimativa_bruto"])
    })

# ... (Rotas /api/main/recent-winning-pools e /api/main/top-winners como antes, com logs)
@app.route('/api/main/recent-winning-pools', methods=['GET'])
def get_recent_winning_pools():
    app.logger.info("Endpoint /api/main/recent-winning-pools acessado")
    pools = [{"name": "Bolão Cósmico da Virada", "lottery": "Mega-Sena", "prize": format_currency(random.uniform(250000, 850000)), "date": "31/12/2025"}, {"name": "Grupo Sorte Astral", "lottery": "Lotofácil", "prize": format_currency(random.uniform(8000, 25000)), "date": "15/10/2025"}]
    return jsonify(random.sample(pools, k=min(len(pools), random.randint(1,2))))

@app.route('/api/main/top-winners', methods=['GET'])
def get_top_winners():
    app.logger.info("Endpoint /api/main/top-winners acessado")
    winners = [{"nick": "EstrelaDaSorte", "prize_total": format_currency(random.uniform(300000, 1500000))}, {"nick": "Astro Premiado", "prize_total": format_currency(random.uniform(200000, 900000))}]
    random.shuffle(winners)
    return jsonify(winners[:random.randint(1,len(winners))])


@app.route('/api/main/resultados/<lottery_name>', methods=['GET'])
def get_resultados_api(lottery_name):
    app.logger.info(f"Endpoint /api/main/resultados/{lottery_name} acessado")
    # ... (lógica como antes)
    lottery_name_lower = lottery_name.lower()
    all_results = load_processed_lottery_data(lottery_name_lower)
    if not all_results: return jsonify({"aviso": f"Dados para {lottery_name.upper()} indisponíveis."}), 404
    latest_result = all_results[0]
    return jsonify({"ultimo_concurso": latest_result.get("concurso"), "data": latest_result.get("data"), "numeros": latest_result.get("numeros"), "ganhadores_principal_contagem": latest_result.get("ganhadores_principal_contagem"), "cidades_ganhadoras_principal": latest_result.get("cidades_ganhadoras_principal"), "rateio_principal_valor": latest_result.get("rateio_principal_valor"), "fonte": f"Dados Processados - {lottery_name.upper()}"})

# --- Endpoints de Estatísticas (Todos devem ter o prefixo /api/main/) ---
@app.route('/api/main/stats/frequencia/<lottery_name>', methods=['GET'])
def get_frequencia_numeros(lottery_name):
    app.logger.info(f"Endpoint /api/main/stats/frequencia/{lottery_name} acessado")
    # ... (lógica como antes)
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
    app.logger.info(f"Endpoint /api/main/stats/pares-frequentes/{lottery_name} acessado")
    # ... (lógica como antes)
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
    app.logger.info(f"Endpoint /api/main/stats/cidades-premiadas/{lottery_name} acessado")
    # ... (lógica como antes)
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
    app.logger.info(f"Endpoint /api/main/stats/maiores-premios-cidade/{lottery_name} acessado")
    # ... (lógica como antes)
    lottery_name_lower = lottery_name.lower()
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    soma_premios_cidade = Counter()
    for sorteio in all_results:
        cidades = sorteio.get("cidades_ganhadoras_principal", [])
        rateio = sorteio.get("rateio_principal_valor", 0.0)
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
    app.logger.info(f"Endpoint /api/main/jogo-manual/probabilidade acessado")
    # ... (lógica como antes)
    data = request.get_json()
    if not data or 'lottery_type' not in data or 'numeros_usuario' not in data: return jsonify({"erro": "Dados incompletos."}), 400
    lottery_type = data['lottery_type'].lower()
    # ... (resto da sua lógica de calcular_probabilidade_jogo)
    numeros_usuario_str_list = data['numeros_usuario']
    if lottery_type not in LOTTERY_CONFIG: return jsonify({"erro": f"Loteria '{data['lottery_type']}' não configurada."}), 404
    config = LOTTERY_CONFIG[lottery_type]; nome_loteria = config.get('nome_exibicao', lottery_type.capitalize())
    universo_total = config['max'] - config['min'] + 1
    numeros_sorteados_para_premio_max = config.get('count_sorteadas', config.get('count'))
    numeros_marcados_pelo_usuario_no_volante = config.get('count_apostadas', config.get('count'))
    if not isinstance(numeros_usuario_str_list, list): return jsonify({"erro": "Formato de 'numeros_usuario' inválido."}), 400
    numeros_usuario = []
    try:
        for n_str in numeros_usuario_str_list:
            num = int(n_str)
            if not (config['min'] <= num <= config['max']): return jsonify({"erro": f"Número {num} fora do range."}), 400
            numeros_usuario.append(num)
    except ValueError: return jsonify({"erro": "Números devem ser inteiros."}), 400
    if len(set(numeros_usuario)) != len(numeros_usuario): return jsonify({"erro": "Números repetidos."}), 400
    if len(numeros_usuario) != numeros_marcados_pelo_usuario_no_volante: return jsonify({"erro": f"Forneça {numeros_marcados_pelo_usuario_no_volante} números."}), 400
    probabilidade_decimal = 0; probabilidade_texto = "Não aplicável."
    if lottery_type == "lotomania":
        if numeros_marcados_pelo_usuario_no_volante == 50 and numeros_sorteados_para_premio_max == 20:
            comb_fav = combinations_count(numeros_marcados_pelo_usuario_no_volante, numeros_sorteados_para_premio_max)
            comb_tot = combinations_count(universo_total, numeros_sorteados_para_premio_max)
            if comb_tot > 0 and comb_fav > 0 :
                probabilidade_decimal = comb_fav / comb_tot
                val_inv = round(comb_tot / comb_fav) if comb_fav > 0 else float('inf')
                probabilidade_texto = f"1 em {val_inv:,}".replace(',', '.') if val_inv != float('inf') else "1 em infinito"
            else: probabilidade_texto = "Combinações inválidas."
        else: probabilidade_texto = "Lotomania (20 acertos) requer jogo de 50 números."
    else:
        comb_tot = combinations_count(universo_total, numeros_sorteados_para_premio_max)
        if comb_tot > 0: probabilidade_decimal = 1 / comb_tot; probabilidade_texto = f"1 em {int(comb_tot):,}".replace(',', '.')
        else: probabilidade_texto = "Combinações resultou em zero."
    return jsonify({"loteria": nome_loteria, "jogo_usuario": sorted(numeros_usuario), "probabilidade_decimal": probabilidade_decimal, "probabilidade_texto": probabilidade_texto, "descricao": f"Probabilidade de acertar o prêmio máximo."})


# --- GERADOR DE JOGO IA (ANTIGO, AGORA SIMPLIFICADO PARA 'ALEATORIO_RAPIDO') ---
def gerar_jogo_ia_simplificado(lottery_name, todos_resultados_historicos=None): # Removido estrategia e is_premium
    app.logger.info(f"[gerar_jogo_ia_simplificado] Solicitado para {lottery_name}")
    config = LOTTERY_CONFIG[lottery_name]
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    min_num, max_num = config["min"], config["max"]
    
    if (max_num - min_num + 1) < numeros_a_gerar:
        app.logger.error(f"Range insuficiente para {lottery_name} em gerar_jogo_ia_simplificado")
        return {"jogo": [], "estrategia_usada": "Erro de Configuração (range insuficiente)"}
    
    jogo_final = sorted(random.sample(range(min_num, max_num + 1), numeros_a_gerar))
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório Rápido"
    
    app.logger.info(f"[gerar_jogo_ia_simplificado] Jogo gerado para {lottery_name}: {jogo_final}")
    return {"jogo": jogo_final, "estrategia_usada": estrategia_aplicada}

@app.route('/api/main/gerar_jogo/<lottery_name>', methods=['GET'])
def gerar_jogo_api(lottery_name): # ROTA ANTIGA, AGORA SIMPLIFICADA
    app.logger.info(f"Endpoint /api/main/gerar_jogo/{lottery_name} (simplificado) acessado com args: {request.args}")
    lottery_name_lower = lottery_name.lower()
    
    # Não precisamos mais de 'todos_resultados_historicos' para o aleatório simples,
    # mas mantemos o get_data_for_stats para checar se a loteria é válida.
    _, error_resp_stats, status_code = get_data_for_stats(lottery_name_lower)
    if error_resp_stats:
         app.logger.error(f"Erro ao obter dados para IA em gerar_jogo_api para {lottery_name_lower}: {error_resp_stats}")
         return jsonify(error_resp_stats), status_code

    resultado_geracao = gerar_jogo_ia_simplificado(lottery_name_lower)
    
    if not resultado_geracao.get("jogo") or len(resultado_geracao.get("jogo")) == 0:
        app.logger.error(f"Falha na geração de jogo simplificado para {lottery_name}. Resultado: {resultado_geracao}")
        return jsonify({"erro": f"Não foi possível gerar jogo para {lottery_name}.", "detalhes": resultado_geracao.get("estrategia_usada", "Falha interna")}), 500

    if resultado_geracao.get("jogo"): platform_stats_data["jogos_gerados_total"] += 1
    app.logger.info(f"Jogo aleatório rápido gerado com sucesso para {lottery_name}.")
    return jsonify(resultado_geracao)

# --- NOVAS FUNÇÕES E ENDPOINT PARA PALPITE ESOTÉRICO ---
def gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_numeros, min_val, max_val):
    # ... (lógica como na resposta 39, já copiada aqui)
    numeros_base = set()
    soma_total_digitos = 0
    if data_nascimento_str and isinstance(data_nascimento_str, str):
        for digito in data_nascimento_str:
            if digito.isdigit(): soma_total_digitos += int(digito)
    while soma_total_digitos > 9:
        soma_total_digitos = sum(int(d) for d in str(soma_total_digitos))
    if soma_total_digitos > 0 and min_val <= soma_total_digitos <= max_val:
        numeros_base.add(soma_total_digitos)
    palpite_final = list(numeros_base)
    tentativas_aleatorias = 0; max_tentativas = num_numeros * 20 # Aumentar tentativas
    while len(palpite_final) < num_numeros and tentativas_aleatorias < max_tentativas:
        num_aleatorio = random.randint(min_val, max_val)
        if num_aleatorio not in palpite_final: palpite_final.append(num_aleatorio)
        tentativas_aleatorias += 1
    if len(palpite_final) < num_numeros:
        elementos_possiveis = [n for n in range(min_val, max_val + 1) if n not in palpite_final]
        random.shuffle(elementos_possiveis)
        necessarios = num_numeros - len(palpite_final)
        palpite_final.extend(elementos_possiveis[:necessarios])
    return sorted(palpite_final)[:num_numeros]


def verificar_historico_combinacao(lottery_name_lower, combinacao_palpite):
    # ... (lógica como na resposta 39, já copiada aqui)
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
    # ... (lógica como na resposta 39, já copiada aqui)
    app.logger.info(f"Endpoint /api/main/palpite-esoterico/{lottery_name} acessado")
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
    app.logger.info(f"Retornando palpite esotérico: {response_data}")
    return jsonify(response_data), 200

# if __name__ == '__main__':
# # Este bloco é para teste local e não é usado pela Vercel.
#     import logging
#     logging.basicConfig(level=logging.INFO) # Para ver app.logger.info no console
#     app.run(host='0.0.0.0', port=5000, debug=True)