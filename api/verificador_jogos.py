# api/verificador_jogos.py
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

# Caminho para a chave da conta de serviço e para os dados da loteria
APP_ROOT_VERIFICADOR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_KEY_PATH = os.path.join(APP_ROOT_VERIFICADOR, "serviceAccountKey.json")
LOTTERY_DATA_DIR = os.path.join(APP_ROOT_VERIFICADOR, "lottery_data") # Usado se carregando localmente

# Configuração das loterias (replicada para uso standalone, idealmente compartilhada)
LOTTERY_CONFIG_VERIFICADOR = {
    "megasena": {"nome_exibicao": "Mega-Sena", "count_sorteadas": 6},
    "lotofacil": {"nome_exibicao": "Lotofácil", "count_sorteadas": 15},
    "lotomania": {"nome_exibicao": "Lotomania", "count_sorteadas": 20},
    "quina": {"nome_exibicao": "Quina", "count_sorteadas": 5}
}

# Variável global para o cliente Firestore
db_firestore_verificador = None

def initialize_firebase_admin_verificador(app_name_suffix='VerificadorJogos'):
    global db_firestore_verificador
    if db_firestore_verificador:
        print(f"Cliente Firestore já inicializado para {app_name_suffix}.")
        return True

    app_name = f'lotoGeniusApp{app_name_suffix}'

    if app_name in firebase_admin._apps:
        print(f"Firebase Admin SDK ({app_name}) já inicializado. Reutilizando.")
        current_app = firebase_admin.get_app(name=app_name)
        db_firestore_verificador = firestore.client(app=current_app)
        return True
    elif not firebase_admin._apps: # Nenhuma app inicializada, tenta inicializar a default ou com nome
        try:
            # Tenta carregar do ENV VAR primeiro (para Vercel)
            service_account_json_str = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
            if service_account_json_str:
                service_account_info = json.loads(service_account_json_str)
                cred = credentials.Certificate(service_account_info)
                print(f"Inicializando Firebase Admin SDK para {app_name} via ENV VAR.")
            elif os.path.exists(SERVICE_ACCOUNT_KEY_PATH):
                cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
                print(f"Inicializando Firebase Admin SDK para {app_name} via arquivo local.")
            else:
                print(f"ERRO: Nem FIREBASE_SERVICE_ACCOUNT_JSON (ENV VAR) nem '{SERVICE_ACCOUNT_KEY_PATH}' (local) encontrados.")
                return False

            current_app = firebase_admin.initialize_app(cred, name=app_name)
            db_firestore_verificador = firestore.client(app=current_app)
            print(f"Firebase Admin SDK ({app_name}) inicializado com sucesso.")
            return True
        except Exception as e:
            print(f"Erro ao inicializar Firebase Admin SDK ({app_name}): {e}")
            print(f"Verifique se o arquivo '{SERVICE_ACCOUNT_KEY_PATH}' existe e está correto ou se a ENV VAR está configurada.")
            return False
    else: # Outras apps existem, mas não a que queremos. Não ideal, mas pode acontecer.
          # Para evitar conflitos, idealmente o processador passaria a instância do 'db'
        default_app_name = list(firebase_admin._apps.keys())[0]
        print(f"Firebase Admin SDK já inicializado com outra app ({default_app_name}). Tentando usar o cliente default.")
        try:
            db_firestore_verificador = firestore.client() # Tenta pegar o cliente da app default
            print(f"Cliente Firestore obtido da app default: {default_app_name}")
            return True
        except Exception as e:
            print(f"Erro ao obter cliente Firestore da app default: {e}")
            return False


def load_latest_lottery_result_from_file(lottery_key): # Usado pela função batch standalone
    json_path = os.path.join(LOTTERY_DATA_DIR, f"{lottery_key}_processed_results.json")
    if not os.path.exists(json_path):
        print(f"Arquivo de resultados não encontrado para {lottery_key} em {json_path}")
        return None
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data and isinstance(data, list):
            return data[0] # Retorna o concurso mais recente (o primeiro da lista)
        return None
    except Exception as e:
        print(f"Erro ao carregar resultados de {lottery_key} de {json_path}: {e}")
        return None

def determinar_faixa_premio(lottery_type, acertos):
    config_loteria = LOTTERY_CONFIG_VERIFICADOR.get(lottery_type)
    if not config_loteria:
        return "Desconhecida", False

    max_acertos_possiveis = config_loteria.get("count_sorteadas")
    premiado = False
    faixa = f"{acertos} Acertos"

    if lottery_type == "megasena":
        if acertos == max_acertos_possiveis: faixa, premiado = "Sena (Prêmio Máximo!)", True
        elif acertos == 5: faixa, premiado = "Quina da Mega", True
        elif acertos == 4: faixa, premiado = "Quadra da Mega", True
        elif acertos > 0: faixa, premiado = f"{acertos} Acertos (Verificar Faixa)", True # Considera premiado para fins de notificação genérica
    elif lottery_type == "lotofacil":
        if acertos >= 11: faixa, premiado = f"{acertos} Pontos", True
        if acertos == 15 : faixa = "15 Pontos (Prêmio Máximo!)"
    elif lottery_type == "quina":
        if acertos >= 2: faixa, premiado = f"{acertos} Pontos", True
        if acertos == 5 : faixa = "Quina (Prêmio Máximo!)"
    elif lottery_type == "lotomania":
        if acertos == 0: faixa, premiado = "0 Acertos (Premiado!)", True
        elif acertos >= 15: faixa, premiado = f"{acertos} Pontos", True
        if acertos == 20: faixa = "20 Pontos (Prêmio Máximo!)"
    
    if acertos > 0 and not premiado: # Lógica genérica se não caiu em regra específica mas teve acertos
        premiado = True
        faixa = f"{acertos} Acertos (Verificar Faixa)"
    elif acertos == 0 and not premiado and lottery_type != "lotomania": # Lotomania já trata 0 acertos
        faixa = "Nenhum Prêmio"
        premiado = False


    return faixa, premiado


def verificar_jogos_para_novo_resultado(lottery_key_param, novo_resultado_oficial, db_client=None):
    """
    Verifica jogos salvos de uma loteria específica contra um novo resultado oficial.
    Esta função é para ser chamada pelo processador_local_loterias.py.
    """
    global db_firestore_verificador
    if not db_client and not db_firestore_verificador:
        if not initialize_firebase_admin_verificador(app_name_suffix=f'Verif_{lottery_key_param}'):
            print(f"ERRO FATAL [{lottery_key_param.upper()}]: Falha ao inicializar Firebase para verificação.")
            return
        db_client_to_use = db_firestore_verificador
    elif db_client:
        db_client_to_use = db_client # Usa o cliente passado pelo processador
    else: # db_firestore_verificador já está inicializado
        db_client_to_use = db_firestore_verificador

    print(f"Iniciando verificação para loteria: {lottery_key_param.upper()} contra novo resultado.")

    concurso_oficial_atual = novo_resultado_oficial.get('concurso')
    numeros_sorteados_oficiais = novo_resultado_oficial.get('numeros')

    if not concurso_oficial_atual or not numeros_sorteados_oficiais:
        print(f"ERRO [{lottery_key_param.upper()}]: Dados do novo resultado oficial incompletos (concurso ou números).")
        return

    # Converte números sorteados para inteiros para comparação
    try:
        numeros_sorteados_oficiais_int = [int(n) for n in numeros_sorteados_oficiais]
    except ValueError:
        print(f"ERRO [{lottery_key_param.upper()}]: Números sorteados no resultado oficial contêm valores não numéricos.")
        return

    user_games_ref = db_client_to_use.collection('userGames')
    # Busca jogos da loteria que ainda NÃO foram verificados contra ESTE concurso específico.
    # Ou seja, ultimoConcursoVerificado é DIFERENTE do concurso_oficial_atual.
    # Isso inclui jogos nunca verificados (ultimoConcursoVerificado é null) ou verificados em concursos anteriores.
    query = user_games_ref.where('lottery', '==', lottery_key_param)
    # Adicionar .where('ultimoConcursoVerificado', '!=', concurso_oficial_atual) pode ser muito restritivo
    # se um jogo nunca foi verificado. É melhor filtrar no loop por agora.

    docs_stream = query.stream()
    jogos_atualizados_count = 0
    novos_premiados_count = 0

    for doc in docs_stream:
        game_data = doc.to_dict()
        game_id = doc.id
        
        # Pula se já foi verificado contra este concurso específico
        if game_data.get('ultimoConcursoVerificado') == concurso_oficial_atual:
            continue

        user_numbers_from_db = game_data.get('game')
        if not user_numbers_from_db or not isinstance(user_numbers_from_db, list):
            print(f"Jogo {game_id} sem números ou formato inválido. Pulando.")
            continue
        
        try:
            user_numbers_int = [int(n) for n in user_numbers_from_db]
        except ValueError:
            print(f"Jogo {game_id} contém números não numéricos. Pulando.")
            continue

        acertos_calculados = 0
        numeros_acertados_lista = []
        
        for num_usuario in user_numbers_int:
            if num_usuario in numeros_sorteados_oficiais_int:
                acertos_calculados += 1
                numeros_acertados_lista.append(num_usuario)
        
        faixa_premio_texto, foi_premiado_flag = determinar_faixa_premio(lottery_key_param, acertos_calculados)

        dados_atualizacao = {
            'ultimoConcursoVerificado': concurso_oficial_atual,
            'dataUltimaVerificacao': firestore.SERVER_TIMESTAMP,
            'acertos': acertos_calculados,
            'numerosAcertados': sorted(numeros_acertados_lista),
            'isPremiado': foi_premiado_flag,
            'faixaPremio': faixa_premio_texto,
            'notificacaoPendente': foi_premiado_flag # Ativa notificação se premiado
        }
        
        user_games_ref.document(game_id).update(dados_atualizacao)
        jogos_atualizados_count += 1
        if foi_premiado_flag:
            novos_premiados_count += 1
            print(f"Jogo PREMIADO! ID: {game_id}, Loteria: {lottery_key_param}, Acertos: {acertos_calculados}, Faixa: {faixa_premio_texto}")
        
    print(f"Verificação para {lottery_key_param.upper()} (concurso {concurso_oficial_atual}) concluída.")
    print(f"{jogos_atualizados_count} jogos verificados/atualizados. {novos_premiados_count} novos prêmios identificados.")


def verificar_jogos_salvos_batch(): # Função original para verificação em lote (standalone)
    global db_firestore_verificador
    if not db_firestore_verificador:
        if not initialize_firebase_admin_verificador(app_name_suffix='VerificadorBatch'):
            print("ERRO FATAL [BATCH]: Falha ao inicializar Firebase para verificação em lote.")
            return

    print("Iniciando verificação em lote de jogos salvos...")
    try:
        latest_official_results_map = {}
        for lottery_key_iter in LOTTERY_CONFIG_VERIFICADOR.keys():
            # Esta função usa o carregamento de arquivo local, não o blob da Vercel diretamente
            # Para usar o blob, você precisaria integrar a lógica de download do processador aqui
            # ou ter um mecanismo para o `verificador_jogos.py` acessar as URLs dos blobs.
            # Por simplicidade, vamos assumir que os JSONs estão disponíveis localmente para esta função batch.
            data_from_file = load_latest_lottery_result_from_file(lottery_key_iter)
            if data_from_file:
                latest_official_results_map[lottery_key_iter] = data_from_file
        
        if not latest_official_results_map:
            print("Nenhum resultado oficial carregado localmente. Abortando verificação em lote.")
            return

        user_games_ref_batch = db_firestore_verificador.collection('userGames')
        all_docs_batch = user_games_ref_batch.stream() 

        jogos_atualizados_batch_total = 0
        jogos_premiados_novos_batch_total = 0

        for doc_batch in all_docs_batch:
            game_data_batch = doc_batch.to_dict()
            game_id_batch = doc_batch.id
            lottery_type_batch = game_data_batch.get('lottery')
            user_numbers_batch = game_data_batch.get('game')

            if not lottery_type_batch or not user_numbers_batch:
                # print(f"Jogo {game_id_batch} com dados incompletos. Pulando.")
                continue

            latest_result_for_current_lottery = latest_official_results_map.get(lottery_type_batch)
            if not latest_result_for_current_lottery:
                # print(f"Sem resultado recente para {lottery_type_batch} para o jogo {game_id_batch}. Pulando.")
                continue 

            concurso_oficial_batch = latest_result_for_current_lottery.get('concurso')
            
            if game_data_batch.get('ultimoConcursoVerificado') == concurso_oficial_batch:
                continue # Já verificado contra o mais recente deste lote

            official_numbers_batch_str = latest_result_for_current_lottery.get('numeros')
            if not official_numbers_batch_str: continue

            try:
                official_numbers_batch_int = [int(n) for n in official_numbers_batch_str]
                user_numbers_batch_int = [int(n) for n in user_numbers_batch]
            except ValueError:
                # print(f"Erro ao converter números para int no jogo {game_id_batch} ou resultado oficial. Pulando.")
                continue
            
            hits_batch = 0
            hit_numbers_list_batch = []
            for num_usr_batch in user_numbers_batch_int:
                if num_usr_batch in official_numbers_batch_int:
                    hits_batch += 1
                    hit_numbers_list_batch.append(num_usr_batch)
            
            faixa_premio_str_batch, is_premiado_flag_batch = determinar_faixa_premio(lottery_type_batch, hits_batch)

            update_data_batch = {
                'ultimoConcursoVerificado': concurso_oficial_batch,
                'dataUltimaVerificacao': firestore.SERVER_TIMESTAMP,
                'acertos': hits_batch,
                'numerosAcertados': sorted(hit_numbers_list_batch),
                'isPremiado': is_premiado_flag_batch,
                'faixaPremio': faixa_premio_str_batch,
                'notificacaoPendente': is_premiado_flag_batch
            }
            
            user_games_ref_batch.document(game_id_batch).update(update_data_batch)
            jogos_atualizados_batch_total += 1
            if is_premiado_flag_batch:
                jogos_premiados_novos_batch_total +=1
                print(f"BATCH Jogo PREMIADO! ID: {game_id_batch}, Loteria: {lottery_type_batch}, Acertos: {hits_batch}, Faixa: {faixa_premio_str_batch}")
        
        print(f"Verificação em lote concluída. {jogos_atualizados_batch_total} jogos verificados/atualizados. {jogos_premiados_novos_batch_total} novos prêmios identificados.")

    except Exception as e_batch:
        print(f"Erro durante a verificação em lote de jogos salvos: {e_batch}")

if __name__ == '__main__':
    print("Executando o Verificador de Jogos Salvos em modo BATCH (standalone)...")
    # Para rodar standalone, certifique-se que os JSONs processados estão em LOTTERY_DATA_DIR
    # e que as credenciais do Firebase estão acessíveis.
    verificar_jogos_salvos_batch()
    print("Verificador de Jogos Salvos (BATCH) concluído.")