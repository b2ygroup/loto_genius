# api/main.py
from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import os
import json
from collections import Counter
from itertools import combinations
import math # Usado em combinations_count

# Se você removeu pandas do requirements.txt para Vercel,
# certifique-se que não há 'import pandas as pd' aqui,
# ou que as funções que o usavam foram ajustadas ou são condicionais.
# Ex: pd.isna() precisaria ser substituído por checagens de None ou string 'nan'.
# Por simplicidade, vou manter a lógica com pd.isna por enquanto,
# mas isso implica que 'pandas' precisaria estar no api/requirements.txt.
import pandas as pd # Mantenha se parse_currency_to_float etc. ainda usarem pd.isna E FOREM USADAS
import re # Mantenha se parse_ganhadores_cidades for usada e precisar

app = Flask(__name__)
CORS(app)

# --- CAMINHO PARA OS DADOS ---
# __file__ refere-se ao caminho deste arquivo (api/main.py)
# os.path.dirname(__file__) dá o diretório api/
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(APP_ROOT, 'lottery_data') # Correto, pois lottery_data está em api/lottery_data

# --- CONFIGURAÇÃO DAS LOTERIAS (Lendo de DATA_DIR em api/lottery_data) ---
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

def format_currency(value):
    if isinstance(value, (int, float)):
        return f"R$ {value:_.2f}".replace('.', ',').replace('_', '.')
    return "R$ 0,00"

# Funções parse_currency_to_float e parse_ganhadores_cidades
# Se seus JSONs já estão 100% limpos pelo script local, estas podem ser desnecessárias aqui.
# Se ainda houver chance de dados "crus" nos JSONs, mantenha-as.
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
# --- FIM DAS FUNÇÕES DE PARSE OPCIONAIS ---

def load_processed_lottery_data(lottery_key):
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
        app.logger.info(f"Certifique-se de que o arquivo {os.path.basename(processed_json_path)} "
                        f"foi pré-processado e incluído no diretório '{DATA_DIR}' do deployment.")
        return None
    try:
        with open(processed_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        app.logger.info(f"Dados de {lottery_key.upper()} carregados de {processed_json_path}")
        return data
    except Exception as e:
        app.logger.error(f"CRÍTICO ao ler ou parsear JSON {processed_json_path} para {lottery_key.upper()}: {e}")
        return None

# --- ROTAS DA API ---
# Se o vercel.json tem "dest": "api/main.py" para rotas como "/api/main/(.*)",
# então o Flask não precisa repetir /api/main/ em suas rotas.
# As rotas Flask devem ser relativas ao ponto de entrada da função.
# Exemplo: se o cliente chama /api/main/platform-stats
# e vercel.json direciona /api/main/(.*) para api/main.py,
# a rota Flask deve ser @app.route('/platform-stats')

@app.route('/') # Esta será a raiz da função, ex: loto-genius.vercel.app/api (se "api/main.py" for o entrypoint)
def api_root_message():
    # Esta rota pode não ser diretamente acessível dependendo da configuração de "routes" no vercel.json
    # e como você mapeia o path base da API.
    return jsonify({"message": "Função API Python está no ar!", "entry_point_info": "Esta é a raiz da função definida em api/main.py"})

@app.route('/platform-stats', methods=['GET'])
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

@app.route('/recent-winning-pools', methods=['GET'])
def get_recent_winning_pools():
    pools = [
        {"name": "Bolão da Virada Genius", "lottery": "Mega-Sena", "prize": format_currency(random.uniform(150000, 750000)), "date": "31/12/2024"},
        {"name": "Grupo Independência Forte", "lottery": "Lotofácil", "prize": format_currency(random.uniform(5000, 15000)), "date": "07/09/2024"},
        {"name": "Amigos da Quina Junina", "lottery": "Quina", "prize": format_currency(random.uniform(20000, 100000)), "date": "23/06/2024"},
    ]
    return jsonify(random.sample(pools, k=min(len(pools), random.randint(1,3))))

@app.route('/top-winners', methods=['GET'])
def get_top_winners():
    winners = [
        {"nick": "MestreDaSorte", "prize_total": format_currency(random.uniform(250000, 1200000))},
        {"nick": "LeoSupremo", "prize_total": format_currency(random.uniform(180000, 700000))},
        {"nick": "DamaDeCopas", "prize_total": format_currency(random.uniform(120000, 500000))},
    ]
    random.shuffle(winners)
    return jsonify(winners[:random.randint(2,len(winners))])


@app.route('/resultados/<lottery_name>', methods=['GET'])
def get_resultados_api(lottery_name):
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

def get_data_for_stats(lottery_name_lower): # Helper
    if lottery_name_lower not in LOTTERY_CONFIG:
        return None, {"erro": f"Loteria '{lottery_name_lower}' não configurada."}, 404
    all_results = load_processed_lottery_data(lottery_name_lower)
    if not all_results:
        return None, {"erro": f"Dados de {lottery_name_lower.upper()} indisponíveis."}, 404
    return all_results, None, None

@app.route('/stats/frequencia/<lottery_name>', methods=['GET'])
def get_frequencia_numeros(lottery_name):
    lottery_name_lower = lottery_name.lower()
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response:
        return jsonify(error_response), status_code
    todos_numeros = [num for sorteio in all_results if "numeros" in sorteio for num in sorteio["numeros"]]
    if not todos_numeros:
        return jsonify({"data": [], "mensagem": "Nenhum número nos dados."}), 200
    contagem = Counter(todos_numeros)
    frequencia_ordenada = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))
    frequencia_formatada = [{"numero": str(num).zfill(2), "frequencia": freq} for num, freq in frequencia_ordenada]
    return jsonify({"data": frequencia_formatada, "total_sorteios_analisados": len(all_results)})

@app.route('/stats/pares-frequentes/<lottery_name>', methods=['GET'])
def get_pares_frequentes(lottery_name):
    lottery_name_lower = lottery_name.lower()
    config = LOTTERY_CONFIG.get(lottery_name_lower)
    if not config: return jsonify({"erro": "Loteria não configurada."}), 404
    all_results, error_response, status_code = get_data_for_stats(lottery_name_lower)
    if error_response:
        return jsonify(error_response), status_code
    numeros_por_sorteio = config.get("count_sorteadas", config.get("count"))
    todos_os_itens_combinacao = [
        tuple(par) for s in all_results
        if s.get("numeros") and len(s["numeros"]) == numeros_por_sorteio
        for par in combinations(sorted(s["numeros"]), 2)
    ]
    if not todos_os_itens_combinacao:
        return jsonify({"data": [], "mensagem": "Não foi possível gerar pares."}), 200
    contagem_itens = Counter(todos_os_itens_combinacao)
    itens_ordenados = sorted(contagem_itens.items(), key=lambda item: (-item[1], item[0]))
    itens_formatados = [{"par": [str(n).zfill(2) for n in item_numeros], "frequencia": freq} for item_numeros, freq in itens_ordenados]
    return jsonify({"data": itens_formatados[:30]})

@app.route('/stats/cidades-premiadas/<lottery_name>', methods=['GET'])
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

@app.route('/stats/maiores-premios-cidade/<lottery_name>', methods=['GET'])
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

def combinations_count(n, k):
    if k < 0 or k > n: return 0
    if k == 0 or k == n: return 1
    if k > n // 2: k = n - k
    res = 1
    for i in range(k): res = res * (n - i) // (i + 1)
    return res

@app.route('/jogo-manual/probabilidade', methods=['POST'])
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
    probabilidade_decimal = 0
    probabilidade_texto = "Não aplicável para esta configuração."
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
        else:
            return {"jogo": [], "estrategia_usada": "Erro de Configuração (range insuficiente)"}

    if not jogo_final or len(jogo_final) != numeros_a_gerar:
           if (max_num - min_num + 1) >= numeros_a_gerar:
               jogo_final = sorted(random.sample(universo_numeros, numeros_a_gerar))
               estrategia_aplicada = f"{config.get('nome_exibicao', lottery_name.capitalize())}: Aleatório Simples (Emergência)"
           else: return {"jogo": [], "estrategia_usada": "Falha Crítica na Geração (Range)"}
    return {"jogo": sorted(list(set(jogo_final))), "estrategia_usada": estrategia_aplicada}

@app.route('/gerar_jogo/<lottery_name>', methods=['GET'])
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


# Para rodar localmente para teste (a Vercel não usa este bloco diretamente para servir)
# No entanto, a Vercel usa o objeto 'app' definido neste arquivo.
# if __name__ == '__main__':
#     import logging
#     logging.basicConfig(level=logging.INFO) # Para ver os logs do app.logger
#     app.logger.info(f"Servidor Flask (versão Vercel) rodando localmente para teste.")
#     app.logger.info(f"Lendo dados de: {DATA_DIR}")
#     for key_lottery, config_loteria in LOTTERY_CONFIG.items():
#         processed_json_path_check = config_loteria.get("processed_json_file")
#         if processed_json_path_check and not os.path.exists(processed_json_path_check):
#             app.logger.warning(f"Arquivo JSON para {key_lottery.upper()} NÃO encontrado em '{processed_json_path_check}'.")
#     app.run(host='0.0.0.0', port=5000, debug=False)