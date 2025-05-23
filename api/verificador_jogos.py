# api/verificador_jogos.py
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

APP_ROOT_VERIFICADOR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_KEY_PATH = os.path.join(APP_ROOT_VERIFICADOR, "serviceAccountKey.json")
LOTTERY_DATA_DIR = os.path.join(APP_ROOT_VERIFICADOR, "lottery_data")

LOTTERY_CONFIG_VERIFICADOR = {
    "megasena": {"nome_exibicao": "Mega-Sena", "count_sorteadas": 6},
    "lotofacil": {"nome_exibicao": "Lotofácil", "count_sorteadas": 15},
    "lotomania": {"nome_exibicao": "Lotomania", "count_sorteadas": 20},
    "quina": {"nome_exibicao": "Quina", "count_sorteadas": 5}
}

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
    elif not firebase_admin._apps:
        try:
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
            return False
    else:
        default_app_name = list(firebase_admin._apps.keys())[0]
        print(f"Firebase Admin SDK já inicializado com outra app ({default_app_name}). Tentando usar o cliente default.")
        try:
            db_firestore_verificador = firestore.client()
            print(f"Cliente Firestore obtido da app default: {default_app_name}")
            return True
        except Exception as e:
            print(f"Erro ao obter cliente Firestore da app default: {e}")
            return False


def load_latest_lottery_result_from_file(lottery_key):
    json_path = os.path.join(LOTTERY_DATA_DIR, f"{lottery_key}_processed_results.json")
    if not os.path.exists(json_path):
        print(f"Arquivo de resultados não encontrado para {lottery_key} em {json_path}")
        return None
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data and isinstance(data, list):
            return data[0]
        return None
    except Exception as e:
        print(f"Erro ao carregar resultados de {lottery_key} de {json_path}: {e}")
        return None

def determinar_faixa_premio(lottery_type, acertos):
    config_loteria = LOTTERY_CONFIG_VERIFICADOR.get(lottery_type)
    if not config_loteria:
        return "Desconhecida", False, False # faixa, isPremiado, geraNotificacaoEspecial

    max_acertos_possiveis = config_loteria.get("count_sorteadas")
    is_premiado_geral = False # Indica se ganhou qualquer prêmio (para marcar no card)
    gera_notificacao_especial = False # Indica se deve mostrar o modal "Parabéns"
    faixa = f"{acertos} Acertos"

    if lottery_type == "megasena":
        if acertos == max_acertos_possiveis:
            faixa, is_premiado_geral, gera_notificacao_especial = "Sena (Prêmio Máximo!)", True, True
        elif acertos == 5:
            faixa, is_premiado_geral, gera_notificacao_especial = "Quina da Mega", True, True
        elif acertos == 4:
            faixa, is_premiado_geral, gera_notificacao_especial = "Quadra da Mega", True, True
        # Para Mega, acertos < 4 não são premiados, então is_premiado_geral permanece False

    elif lottery_type == "lotofacil":
        if acertos == 15:
            faixa, is_premiado_geral, gera_notificacao_especial = "15 Pontos (Prêmio Máximo!)", True, True
        elif acertos == 14:
            faixa, is_premiado_geral, gera_notificacao_especial = "14 Pontos", True, True
        elif acertos == 13:
            faixa, is_premiado_geral, gera_notificacao_especial = "13 Pontos", True, True
        elif acertos == 12:
            faixa, is_premiado_geral, gera_notificacao_especial = "12 Pontos", True, True # Consideramos notificação
        elif acertos == 11:
            faixa, is_premiado_geral, gera_notificacao_especial = "11 Pontos", True, True # Consideramos notificação
        # Acertos de 1 a 10 na Lotofácil não são premiados.

    elif lottery_type == "quina":
        if acertos == 5:
            faixa, is_premiado_geral, gera_notificacao_especial = "Quina (Prêmio Máximo!)", True, True
        elif acertos == 4:
            faixa, is_premiado_geral, gera_notificacao_especial = "Quadra", True, True
        elif acertos == 3:
            faixa, is_premiado_geral, gera_notificacao_especial = "Terno", True, True # Decidimos notificar para Terno
        elif acertos == 2: # Duque geralmente paga pouco, não notificamos com modal.
            faixa, is_premiado_geral, gera_notificacao_especial = "Duque", True, False
        # Acertos < 2 na Quina não são premiados

    elif lottery_type == "lotomania":
        if acertos == 20:
            faixa, is_premiado_geral, gera_notificacao_especial = "20 Pontos (Prêmio Máximo!)", True, True
        elif acertos == 0: # 0 acertos é uma faixa especial
            faixa, is_premiado_geral, gera_notificacao_especial = "0 Acertos (Premiado!)", True, True
        elif acertos >= 15: # 15, 16, 17, 18, 19
            faixa, is_premiado_geral, gera_notificacao_especial = f"{acertos} Pontos", True, True
        # Outras faixas da Lotomania não são premiadas ou pagam muito pouco

    # Se is_premiado_geral é True mas gera_notificacao_especial é False,
    # significa que o jogo foi premiado, mas não o suficiente para o modal "Parabéns".
    # Se não houve acertos e não caiu em regra especial (como 0 da Lotomania), is_premiado_geral será False.
    if not is_premiado_geral and acertos > 0: # Se teve algum acerto mas não se qualificou como premiado acima
         faixa = f"{acertos} Acertos (Não Premiado)"
    elif not is_premiado_geral and acertos == 0 and lottery_type != "lotomania":
         faixa = "Nenhum Acerto"


    return faixa, is_premiado_geral, gera_notificacao_especial


def verificar_jogos_para_novo_resultado(lottery_key_param, novo_resultado_oficial, db_client=None):
    global db_firestore_verificador
    if not db_client and not db_firestore_verificador:
        if not initialize_firebase_admin_verificador(app_name_suffix=f'Verif_{lottery_key_param}'):
            print(f"ERRO FATAL [{lottery_key_param.upper()}]: Falha ao inicializar Firebase para verificação.")
            return
        db_client_to_use = db_firestore_verificador
    elif db_client:
        db_client_to_use = db_client
    else:
        db_client_to_use = db_firestore_verificador

    print(f"Iniciando verificação para loteria: {lottery_key_param.upper()} contra novo resultado.")

    concurso_oficial_atual = novo_resultado_oficial.get('concurso')
    numeros_sorteados_oficiais = novo_resultado_oficial.get('numeros')

    if not concurso_oficial_atual or not numeros_sorteados_oficiais:
        print(f"ERRO [{lottery_key_param.upper()}]: Dados do novo resultado oficial incompletos (concurso ou números).")
        return

    try:
        numeros_sorteados_oficiais_int = [int(n) for n in numeros_sorteados_oficiais]
    except ValueError:
        print(f"ERRO [{lottery_key_param.upper()}]: Números sorteados no resultado oficial contêm valores não numéricos.")
        return

    user_games_ref = db_client_to_use.collection('userGames')
    query = user_games_ref.where('lottery', '==', lottery_key_param)
    
    docs_stream = query.stream()
    jogos_atualizados_count = 0
    novos_premiados_com_notificacao_count = 0

    for doc in docs_stream:
        game_data = doc.to_dict()
        game_id = doc.id
        
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
        
        # Agora `determinar_faixa_premio` retorna três valores
        faixa_premio_texto, foi_premiado_geral_flag, gera_notificacao_especial_flag = determinar_faixa_premio(lottery_key_param, acertos_calculados)

        dados_atualizacao = {
            'ultimoConcursoVerificado': concurso_oficial_atual,
            'dataUltimaVerificacao': firestore.SERVER_TIMESTAMP,
            'acertos': acertos_calculados,
            'numerosAcertados': sorted(numeros_acertados_lista),
            'isPremiado': foi_premiado_geral_flag, # Marca se ganhou QUALQUER prêmio
            'faixaPremio': faixa_premio_texto,
            'notificacaoPendente': gera_notificacao_especial_flag # Ativa notificação SÓ para prêmios "altos"
        }
        
        user_games_ref.document(game_id).update(dados_atualizacao)
        jogos_atualizados_count += 1
        if gera_notificacao_especial_flag: # Contabiliza apenas os que gerarão o modal "Parabéns"
            novos_premiados_com_notificacao_count += 1
            print(f"Jogo PREMIADO COM NOTIFICAÇÃO ESPECIAL! ID: {game_id}, Loteria: {lottery_key_param}, Acertos: {acertos_calculados}, Faixa: {faixa_premio_texto}")
        elif foi_premiado_geral_flag: # Foi premiado, mas sem notificação especial
            print(f"Jogo premiado (sem notificação especial). ID: {game_id}, Loteria: {lottery_key_param}, Acertos: {acertos_calculados}, Faixa: {faixa_premio_texto}")

    print(f"Verificação para {lottery_key_param.upper()} (concurso {concurso_oficial_atual}) concluída.")
    print(f"{jogos_atualizados_count} jogos verificados/atualizados. {novos_premiados_com_notificacao_count} novos prêmios com notificação especial identificados.")


def verificar_jogos_salvos_batch():
    global db_firestore_verificador
    if not db_firestore_verificador:
        if not initialize_firebase_admin_verificador(app_name_suffix='VerificadorBatch'):
            print("ERRO FATAL [BATCH]: Falha ao inicializar Firebase para verificação em lote.")
            return

    print("Iniciando verificação em lote de jogos salvos...")
    try:
        latest_official_results_map = {}
        for lottery_key_iter in LOTTERY_CONFIG_VERIFICADOR.keys():
            data_from_file = load_latest_lottery_result_from_file(lottery_key_iter)
            if data_from_file:
                latest_official_results_map[lottery_key_iter] = data_from_file
        
        if not latest_official_results_map:
            print("Nenhum resultado oficial carregado localmente. Abortando verificação em lote.")
            return

        user_games_ref_batch = db_firestore_verificador.collection('userGames')
        all_docs_batch = user_games_ref_batch.stream() 

        jogos_atualizados_batch_total = 0
        jogos_premiados_com_notificacao_batch_total = 0

        for doc_batch in all_docs_batch:
            game_data_batch = doc_batch.to_dict()
            game_id_batch = doc_batch.id
            lottery_type_batch = game_data_batch.get('lottery')
            user_numbers_batch_db = game_data_batch.get('game')

            if not lottery_type_batch or not user_numbers_batch_db:
                continue

            latest_result_for_current_lottery = latest_official_results_map.get(lottery_type_batch)
            if not latest_result_for_current_lottery:
                continue 

            concurso_oficial_batch = latest_result_for_current_lottery.get('concurso')
            
            if game_data_batch.get('ultimoConcursoVerificado') == concurso_oficial_batch:
                continue

            official_numbers_batch_str = latest_result_for_current_lottery.get('numeros')
            if not official_numbers_batch_str: continue

            try:
                official_numbers_batch_int = [int(n) for n in official_numbers_batch_str]
                user_numbers_batch_int = [int(n) for n in user_numbers_batch_db]
            except ValueError:
                continue
            
            hits_batch = 0
            hit_numbers_list_batch = []
            for num_usr_batch in user_numbers_batch_int:
                if num_usr_batch in official_numbers_batch_int:
                    hits_batch += 1
                    hit_numbers_list_batch.append(num_usr_batch)
            
            faixa_premio_str_batch, is_premiado_geral_flag_batch, gera_notif_especial_flag_batch = determinar_faixa_premio(lottery_type_batch, hits_batch)

            update_data_batch = {
                'ultimoConcursoVerificado': concurso_oficial_batch,
                'dataUltimaVerificacao': firestore.SERVER_TIMESTAMP,
                'acertos': hits_batch,
                'numerosAcertados': sorted(hit_numbers_list_batch),
                'isPremiado': is_premiado_geral_flag_batch,
                'faixaPremio': faixa_premio_str_batch,
                'notificacaoPendente': gera_notif_especial_flag_batch
            }
            
            user_games_ref_batch.document(game_id_batch).update(update_data_batch)
            jogos_atualizados_batch_total += 1
            if gera_notif_especial_flag_batch:
                jogos_premiados_com_notificacao_batch_total +=1
                print(f"BATCH Jogo PREMIADO COM NOTIFICAÇÃO! ID: {game_id_batch}, Loteria: {lottery_type_batch}, Acertos: {hits_batch}, Faixa: {faixa_premio_str_batch}")
        
        print(f"Verificação em lote concluída. {jogos_atualizados_batch_total} jogos verificados/atualizados. {jogos_premiados_com_notificacao_batch_total} novos prêmios com notificação especial identificados.")

    except Exception as e_batch:
        print(f"Erro durante a verificação em lote de jogos salvos: {e_batch}")

if __name__ == '__main__':
    print("Executando o Verificador de Jogos Salvos em modo BATCH (standalone)...")
    verificar_jogos_salvos_batch()
    print("Verificador de Jogos Salvos (BATCH) concluído.")