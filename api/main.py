# api/main.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import os
import json
from collections import Counter
from itertools import combinations
import math
import pandas as pd # Essencial para pd.isna() se usado
import re           # Essencial para parse_ganhadores_cidades se usado

app = Flask(__name__)
CORS(app)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_ROOT, 'lottery_data')

LOTTERY_CONFIG = {
    "megasena": {
        "nome_exibicao": "Mega-Sena", "min": 1, "max": 60, "count": 6, "color": "#209869",
        "processed_json_file": os.path.join(DATA_DIR, "megasena_processed_results.json"),
        "count_sorteadas": 6
    },
    "lotofacil": {
        "nome_exibicao": "Lotofácil", "min": 1, "max": 25, "count": 15, "color": "#930089",
        "processed_json_file": os.path.join(DATA_DIR, "lotofacil_processed_results.json"),
        "count_sorteadas": 15
    },
    "lotomania": {
        "nome_exibicao": "Lotomania", "min": 0, "max": 99, "count_apostadas": 50, "count_sorteadas": 20, "color": "#f78100",
        "processed_json_file": os.path.join(DATA_DIR, "lotomania_processed_results.json")
    },
    "quina": {
        "nome_exibicao": "Quina", "min": 1, "max": 80, "count": 5, "color": "#260085",
        "processed_json_file": os.path.join(DATA_DIR, "quina_processed_results.json"),
        "count_sorteadas": 5
    }
}

platform_stats_data = {
    "jogos_gerados_total": random.randint(18500, 30500),
    "jogos_premiados_estimativa": random.randint(250, 750),
    "valor_premios_estimativa_bruto": random.uniform(95000, 350000)
}

# --- Funções Auxiliares ---
def format_currency(value):
    if isinstance(value, (int, float)):
        return f"R$ {value:_.2f}".replace('.', ',').replace('_', '.')
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

def load_processed_lottery_data(lottery_key):
    # Usar app.logger para logs que aparecerão na Vercel
    app.logger.info(f"Tentando carregar dados processados para {lottery_key.upper()} de {DATA_DIR}")
    config = LOTTERY_CONFIG.get(lottery_key)
    if not config:
        app.logger.error(f"Configuração não encontrada para {lottery_key}")
        return None
    processed_json_path = config.get("processed_json_file")
    if not processed_json_path:
        app.logger.error(f"Caminho do arquivo JSON processado não configurado para {lottery_key}")
        return None
    if not os.path.exists(processed_json_path):
        app.logger.error(f"Arquivo JSON processado NÃO ENCONTRADO em: {processed_json_path}")
        return None
    try:
        with open(processed_json_path, 'r', encoding='utf-8') as f: data = json.load(f)
        app.logger.info(f"Dados de {lottery_key.upper()} carregados de {processed_json_path}")
        return data
    except Exception as e:
        app.logger.error(f"CRÍTICO ao ler ou parsear JSON {processed_json_path} para {lottery_key.upper()}: {e}")
        return None

def get_data_for_stats(lottery_name_lower):
    if lottery_name_lower not in LOTTERY_CONFIG:
        return None, {"erro": f"Loteria '{lottery_name_lower}' não configurada."}, 404
    all_results = load_processed_lottery_data(lottery_name_lower)
    if not all_results:
        return None, {"erro": f"Dados de {lottery_name_lower.upper()} indisponíveis."}, 404
    return all_results, None, None

def combinations_count(n, k):
    if k < 0 or k > n: return 0
    if k == 0 or k == n: return 1
    if k > n // 2: k = n - k
    res = 1
    for i in range(k): res = res * (n - i) // (i + 1)
    return res

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
    if todos_resultados and todos_resultados[0].get("concurso"):
        concurso_mais_recente = todos_resultados[0].get("concurso")
    else: concurso_mais_recente = len(todos_resultados)
    for i, sorteio in enumerate(todos_resultados):
        concurso_atual = sorteio.get("concurso", concurso_mais_recente - i)
        for num in sorteio.get("numeros", []):
            if num in ultima_aparicao_concurso and ultima_aparicao_concurso[num] == 0:
                ultima_aparicao_concurso[num] = concurso_atual
    atrasos = {num: (concurso_mais_recente - ultima_aparicao_concurso[num]) if ultima_aparicao_concurso[num] != 0 else float('inf') for num in universo_numeros}
    frios_ordenados = sorted(atrasos.items(), key=lambda item: (-item[1], item[0]))
    return [num for num, atraso in frios_ordenados[:qtd_numeros_retorno]]

# --- ROTAS DA API ---
# O vercel.json com "src": "/api/(.*)" fará com que o Flask receba o path completo.
# Portanto, as rotas Flask devem incluir o prefixo /api/main/

@app.route('/') # Esta rota será acionada se a chamada for apenas para a raiz da função (ex: /api/)
def api_base_root():
    return jsonify({"message": "API Loto Genius Python (api/main.py). Endpoints em /api/main/..."})

@app.route('/api/main/')
def api_main_home():
    return jsonify({"mensagem": "API Loto Genius AI Funcionando!", "versao": "3.0.1 - Rotas Revisadas"})

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
    ]
    random.shuffle(winners)
    return jsonify(winners[:random.randint(2,len(winners))])

@app.route('/api/main/resultados/<lottery_name>', methods=['GET'])
def get_resultados_api(lottery_name): # O nome da função não precisa ser '_route'
    lottery_name_lower = lottery_name.lower()
    all_results = load_processed_lottery_data(lottery_name_lower)
    if not all_results:
        return jsonify({"aviso": f"Dados para {lottery_name.upper()} indisponíveis.", "numeros": []}), 404
    latest_result = all_results[0]
    return jsonify({
        "ultimo_concurso": latest_result.get("concurso"),
        "data": latest_result.get("data"),
        "numeros": latest_result.get("numeros"),
        "ganhadores_principal_contagem": latest_result.get("ganhadores_principal_contagem"),
        "cidades_ganhadoras_principal": latest_result.get("cidades_ganhadoras_principal"),
        "rateio_principal_valor": latest_result.get("rateio_principal_valor"),
        "fonte": f"Dados Processados - {lottery_name.upper()}"
    })

@app.route('/api/main/stats/frequencia/<lottery_name>', methods=['GET'])
def get_frequencia_numeros(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response: return jsonify(error_response), status_code
    todos_numeros = [num for sorteio in all_results if "numeros" in sorteio for num in sorteio["numeros"]]
    if not todos_numeros: return jsonify({"data": [], "mensagem": "Nenhum número nos dados."}), 200
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
    numeros_por_sorteio = config.get("count_sorteadas", config.get("count"))
    todos_os_itens_combinacao = [
        tuple(par) for s in all_results
        if s.get("numeros") and len(s["numeros"]) == numeros_por_sorteio
        for par in combinations(sorted(s["numeros"]), 2)
    ]
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
    contagem_cidades = Counter()
    total_premios_contabilizados = 0
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
    if len(numeros_usuario) != numeros_marcados_pelo_usuario_no_volante:
           return jsonify({"erro": f"Para {nome_loteria}, você deve fornecer {numeros_marcados_pelo_usuario_no_volante} números para este cálculo."}), 400
    probabilidade_decimal = 0; probabilidade_texto = "Não aplicável."
    if lottery_type == "lotomania":
        if numeros_marcados_pelo_usuario_no_volante == 50 and numeros_sorteados_para_premio_max == 20:
            combinacoes_favoraveis = combinations_count(numeros_marcados_pelo_usuario_no_volante, numeros_sorteados_para_premio_max)
            combinacoes_totais_sorteio = combinations_count(universo_total, numeros_sorteados_para_premio_max)
            if combinacoes_totais_sorteio > 0 and combinacoes_favoraveis > 0 :
                probabilidade_decimal = combinacoes_favoraveis / combinacoes_totais_sorteio
                valor_inverso = round(combinacoes_totais_sorteio / combinacoes_favoraveis) if combinacoes_favoraveis > 0 else float('inf')
                probabilidade_texto = f"1 em {valor_inverso:,}".replace(',', '.') if valor_inverso != float('inf') else "1 em infinito"
            else: probabilidade_texto = "Cálculo de combinações resultou em valor inválido."
        else: probabilidade_texto = "Cálculo para Lotomania (20 acertos) requer um jogo de 50 números."
    else:
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

def gerar_jogo_ia(lottery_name, todos_resultados_historicos, estrategia_req="aleatorio_inteligente", is_premium_user=False):
    config = LOTTERY_CONFIG[lottery_name]
    numeros_a_gerar = config.get("count_apostadas", config.get("count"))
    min_num, max_num = config["min"], config["max"]
    universo_numeros = list(range(min_num, max_num + 1))
    jogo_final = []
    estrategia_aplicada_nome_base = estrategia_req.replace('_', ' ').capitalize()
    estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: {estrategia_aplicada_nome_base}"
    if todos_resultados_historicos is None: todos_resultados_historicos = []
    if estrategia_req == "foco_quentes":
        if not is_premium_user:
            return {"jogo": [], "estrategia_usada": "Foco nos Quentes (✨ Premium)", "erro_premium": True}
        estrategia_aplicada = f"{config['nome_exibicao']}: Foco nos Quentes (Premium)"
        num_quentes_a_selecionar = numeros_a_gerar // 2 + (numeros_a_gerar % 2)
        num_quentes_para_amostra = num_quentes_a_selecionar + 5
        numeros_quentes = calcular_numeros_quentes(todos_resultados_historicos, 50, num_quentes_para_amostra)
        if len(numeros_quentes) >= num_quentes_a_selecionar:
            jogo_final.extend(random.sample(numeros_quentes, num_quentes_a_selecionar))
        else: jogo_final.extend(numeros_quentes)
        numeros_restantes_possiveis = [n for n in universo_numeros if n not in jogo_final]
        numeros_a_completar = numeros_a_gerar - len(jogo_final)
        if numeros_a_completar > 0:
            if len(numeros_restantes_possiveis) >= numeros_a_completar:
                jogo_final.extend(random.sample(numeros_restantes_possiveis, numeros_a_completar))
            else: jogo_final = []
    elif estrategia_req == "foco_frios":
        estrategia_aplicada = f"{config['nome_exibicao']}: Foco nos Frios (Atrasados)"
        num_frios_a_selecionar = numeros_a_gerar // 2
        num_frios_para_amostra = num_frios_a_selecionar + 5
        numeros_frios = calcular_numeros_frios(todos_resultados_historicos, universo_numeros, num_frios_para_amostra)
        if len(numeros_frios) >= num_frios_a_selecionar:
            jogo_final.extend(random.sample(numeros_frios, num_frios_a_selecionar))
        else: jogo_final.extend(numeros_frios)
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
        pares_target = min(pares_target, len(numeros_pares_disp))
        impares_target = min(impares_target, len(numeros_impares_disp))
        jogo_final.extend(random.sample(numeros_pares_disp, pares_target))
        jogo_final.extend(random.sample(numeros_impares_disp, impares_target))
        jogo_final = list(set(jogo_final))
        while len(jogo_final) < numeros_a_gerar:
            numeros_disponiveis_geral = [n for n in universo_numeros if n not in jogo_final]
            if not numeros_disponiveis_geral: break
            jogo_final.append(random.choice(numeros_disponiveis_geral))
            jogo_final = list(set(jogo_final))
    if not jogo_final or len(jogo_final) != numeros_a_gerar or estrategia_req == "aleatorio_inteligente":
        if estrategia_req == "aleatorio_inteligente" or not jogo_final or len(jogo_final) != numeros_a_gerar :
            estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório Inteligente"
        else:
            estrategia_aplicada = f"{estrategia_aplicada} (Fallback para Aleatório)"
        if (max_num - min_num + 1) >= numeros_a_gerar:
            jogo_final = sorted(random.sample(universo_numeros, numeros_a_gerar))
        else: return {"jogo": [], "estrategia_usada": "Erro de Configuração (range insuficiente)"}
    if not jogo_final or len(jogo_final) != numeros_a_gerar:
           if (max_num - min_num + 1) >= numeros_a_gerar:
               jogo_final = sorted(random.sample(universo_numeros, numeros_a_gerar))
               estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório Simples (Emergência)"
           else: return {"jogo": [], "estrategia_usada": "Falha Crítica na Geração (Range)"}
    return {"jogo": sorted(list(set(jogo_final))), "estrategia_usada": estrategia_aplicada}

@app.route('/api/main/gerar_jogo/<lottery_name>', methods=['GET'])
def gerar_jogo_api(lottery_name):
    estrategia_req = request.args.get('estrategia', 'aleatorio_inteligente')
    is_premium_simulado = request.args.get('premium_user', 'false').lower() == 'true'
    lottery_name_lower = lottery_name.lower()
    todos_resultados_para_ia, error_resp_stats, _ = get_data_for_stats(lottery_name_lower)
    if error_resp_stats and lottery_name_lower in LOTTERY_CONFIG:
        app.logger.warning(f"Dados históricos para {lottery_name_lower} não puderam ser carregados para IA.")
        todos_resultados_para_ia = []
    elif error_resp_stats:
         return jsonify(error_resp_stats), 404
    resultado_geracao = gerar_jogo_ia(lottery_name_lower, todos_resultados_para_ia, estrategia_req, is_premium_simulado)
    if resultado_geracao.get("erro_premium"):
        return jsonify({"erro": "Acesso Negado", "detalhes": resultado_geracao.get("estrategia_usada"), "premium_requerido": True}), 403
    if not resultado_geracao.get("jogo") or len(resultado_geracao.get("jogo")) == 0 :
        detalhe_erro = resultado_geracao.get("estrategia_usada", "Falha interna na geração.")
        if "Erro" not in detalhe_erro and "Falha" not in detalhe_erro: detalhe_erro = "Não foi possível gerar um palpite válido."
        return jsonify({"erro": f"Não foi possível gerar jogo para {lottery_name}.", "detalhes": detalhe_erro}), 500
    if resultado_geracao.get("jogo"): platform_stats_data["jogos_gerados_total"] += 1
    return jsonify(resultado_geracao)

# --- NOVAS FUNÇÕES E ENDPOINT PARA PALPITE ESOTÉRICO ---
def gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_numeros, min_val, max_val):
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
    tentativas_aleatorias = 0
    while len(palpite_final) < num_numeros and tentativas_aleatorias < (num_numeros * 10):
        num_aleatorio = random.randint(min_val, max_val)
        if num_aleatorio not in palpite_final: palpite_final.append(num_aleatorio)
        tentativas_aleatorias += 1
    elementos_possiveis = [n for n in range(min_val, max_val + 1) if n not in palpite_final]
    random.shuffle(elementos_possiveis)
    while len(palpite_final) < num_numeros and elementos_possiveis:
        palpite_final.append(elementos_possiveis.pop(0))
    return sorted(palpite_final)[:num_numeros]

def verificar_historico_combinacao(lottery_name_lower, combinacao_palpite):
    todos_resultados = load_processed_lottery_data(lottery_name_lower)
    if not todos_resultados:
        app.logger.warning(f"Histórico não carregado para {lottery_name_lower} ao verificar palpite.")
        return 0, 0.0
    ocorrencias = 0; valor_total_ganho = 0.0
    try: palpite_formatado = sorted([int(n) for n in combinacao_palpite])
    except (ValueError, TypeError):
        app.logger.error(f"Erro ao formatar palpite para verificação histórica: {combinacao_palpite}")
        return 0, 0.0
    for sorteio in todos_resultados:
        numeros_sorteados = sorteio.get("numeros")
        if numeros_sorteados and isinstance(numeros_sorteados, list):
            try:
                numeros_sorteados_formatados = sorted([int(n) for n in numeros_sorteados])
                if numeros_sorteados_formatados == palpite_formatado:
                    ocorrencias += 1
                    valor_total_ganho += float(sorteio.get("rateio_principal_valor", 0.0))
            except (ValueError, TypeError): continue 
    return ocorrencias, valor_total_ganho

@app.route('/api/main/palpite-esoterico/<lottery_name>', methods=['POST'])
def gerar_palpite_esoterico_route(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": "Loteria não configurada."}), 404
    dados_usuario = request.get_json()
    if not dados_usuario: return jsonify({"erro": "Dados da requisição não fornecidos (esperado JSON)."}), 400
    data_nascimento_str = dados_usuario.get("data_nascimento")
    if not data_nascimento_str: return jsonify({"erro": "Parâmetro 'data_nascimento' não fornecido."}), 400
    num_a_gerar = config.get("count_apostadas", config.get("count", config.get("count_sorteadas")))
    min_val = config["min"]; max_val = config["max"]
    palpite_gerado = gerar_numeros_baseados_em_data_simples(data_nascimento_str, num_a_gerar, min_val, max_val)
    metodo_usado = f"Baseado em Dados Esotéricos (data_nascimento: {data_nascimento_str}) - Lógica Simplificada"
    if not palpite_gerado or len(palpite_gerado) != num_a_gerar:
        app.logger.error(f"Falha ao gerar palpite esotérico: {palpite_gerado}")
        palpite_gerado = sorted(random.sample(range(min_val, max_val + 1), num_a_gerar))
        metodo_usado = "Aleatório (fallback pós-falha esotérica)"
    ocorrencias, valor_ganho = verificar_historico_combinacao(lottery_name_lower, palpite_gerado)
    return jsonify({
        "loteria": config["nome_exibicao"],
        "palpite_gerado": palpite_gerado,
        "parametros_usados": {"data_nascimento_input": data_nascimento_str},
        "metodo_geracao": metodo_usado,
        "historico_desta_combinacao": {
            "combinacao_verificada": palpite_gerado,
            "ja_foi_premiada_faixa_principal": ocorrencias > 0,
            "vezes_premiada_faixa_principal": ocorrencias,
            "valor_total_ganho_faixa_principal_formatado": format_currency(valor_ganho),
            "valor_total_ganho_faixa_principal_float": valor_ganho
        }
    }), 200

# if __name__ == '__main__':
#     import logging
#     logging.basicConfig(level=logging.INFO)
#     app.logger.info(f"Servidor Flask (versão para api/) rodando localmente para teste.")
#     app.run(host='0.0.0.0', port=5000, debug=True)