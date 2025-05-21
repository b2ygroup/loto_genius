# api/verificador_jogos.py
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

# Caminho para a chave da conta de serviço e para os dados da loteria
APP_ROOT_VERIFICADOR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_KEY_PATH = os.path.join(APP_ROOT_VERIFICADOR, "serviceAccountKey.json")
LOTTERY_DATA_DIR = os.path.join(APP_ROOT_VERIFICADOR, "lottery_data")

# Configuração das loterias (pode ser importada ou replicada do main.py se necessário)
# Para simplificar, vamos definir uma configuração básica aqui.
# Idealmente, você importaria LOTTERY_CONFIG do main.py ou teria um módulo compartilhado.
LOTTERY_CONFIG_VERIFICADOR = {
    "megasena": {"nome_exibicao": "Mega-Sena", "count_sorteadas": 6},
    "lotofacil": {"nome_exibicao": "Lotofácil", "count_sorteadas": 15},
    "lotomania": {"nome_exibicao": "Lotomania", "count_sorteadas": 20},
    "quina": {"nome_exibicao": "Quina", "count_sorteadas": 5}
}

def initialize_firebase_admin():
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK inicializado com sucesso.")
            return True
        except Exception as e:
            print(f"Erro ao inicializar Firebase Admin SDK: {e}")
            print(f"Verifique se o arquivo '{SERVICE_ACCOUNT_KEY_PATH}' existe e está correto.")
            return False
    return True

def load_latest_lottery_result(lottery_key):
    json_path = os.path.join(LOTTERY_DATA_DIR, f"{lottery_key}_processed_results.json")
    if not os.path.exists(json_path):
        print(f"Arquivo de resultados não encontrado para {lottery_key} em {json_path}")
        return None
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if data:
            return data[0] # Retorna o concurso mais recente (o primeiro da lista)
        return None
    except Exception as e:
        print(f"Erro ao carregar resultados de {lottery_key} de {json_path}: {e}")
        return None

def determinar_faixa_premio(lottery_type, acertos):
    # Esta é uma lógica simplificada. Você precisará expandi-la
    # com as regras de premiação reais de cada loteria.
    config_loteria = LOTTERY_CONFIG_VERIFICADOR.get(lottery_type)
    if not config_loteria:
        return "Desconhecida", False

    max_acertos_possiveis = config_loteria.get("count_sorteadas")

    if acertos == max_acertos_possiveis:
        return "Prêmio Máximo!", True
    elif lottery_type == "megasena" and acertos == 5:
        return "Quina da Mega", True
    elif lottery_type == "megasena" and acertos == 4:
        return "Quadra da Mega", True
    elif lottery_type == "lotofacil" and acertos >= 11: # Exemplo: Lotofácil premia a partir de 11
        return f"{acertos} Pontos", True
    elif lottery_type == "quina" and acertos >= 2: # Exemplo
         return f"{acertos} Pontos", True
    elif lottery_type == "lotomania" and acertos == 0: # Lotomania tem prêmio para 0 acertos
        return "0 Acertos (Premiado!)", True
    elif lottery_type == "lotomania" and acertos >= 15: # E para 15, 16, 17, 18, 19, 20
        return f"{acertos} Pontos", True
    
    # Lógica padrão se não se encaixar nas regras acima
    if acertos > 0:
        return f"{acertos} Acertos (Verificar Faixa)", True # Assume premiado se houver acertos, refinar!
    
    return "Nenhum Prêmio", False


def verificar_jogos_salvos_batch():
    if not initialize_firebase_admin():
        return

    db = firestore.client()
    print("Iniciando verificação em lote de jogos salvos...")
    try:
        latest_official_results = {}
        for lottery_key in LOTTERY_CONFIG_VERIFICADOR.keys():
            data = load_latest_lottery_result(lottery_key)
            if data:
                latest_official_results[lottery_key] = data
        
        if not latest_official_results:
            print("Nenhum resultado oficial carregado. Abortando verificação.")
            return

        user_games_ref = db.collection('userGames')
        docs = user_games_ref.stream() 

        jogos_atualizados = 0
        jogos_premiados_novos = 0

        for doc in docs:
            game_data = doc.to_dict()
            game_id = doc.id
            lottery_type = game_data.get('lottery')
            user_numbers = game_data.get('game')

            if not lottery_type or not user_numbers:
                print(f"Jogo {game_id} com dados incompletos. Pulando.")
                continue

            latest_result_for_lottery = latest_official_results.get(lottery_type)
            if not latest_result_for_lottery:
                # print(f"Sem resultado recente para {lottery_type} para o jogo {game_id}. Pulando.")
                continue 

            concurso_atual_oficial = latest_result_for_lottery.get('concurso')
            
            # Evita re-verificar se já foi verificado contra este concurso
            if game_data.get('ultimoConcursoVerificado') == concurso_atual_oficial:
                continue

            official_numbers = latest_result_for_lottery.get('numeros')
            
            hits = 0
            hit_numbers_list = []
            if official_numbers:
                for num in user_numbers:
                    if num in official_numbers: # Assume que os números já são inteiros
                        hits += 1
                        hit_numbers_list.append(num)
            
            faixa_premio_str, is_premiado_flag = determinar_faixa_premio(lottery_type, hits)

            update_data = {
                'ultimoConcursoVerificado': concurso_atual_oficial,
                'dataUltimaVerificacao': firestore.SERVER_TIMESTAMP, # Usa timestamp do servidor
                'acertos': hits,
                'numerosAcertados': hit_numbers_list,
                'isPremiado': is_premiado_flag,
                'faixaPremio': faixa_premio_str,
                'notificacaoPendente': is_premiado_flag # Se premiado, marca para notificar
            }
            
            user_games_ref.document(game_id).update(update_data)
            jogos_atualizados += 1
            if is_premiado_flag:
                jogos_premiados_novos +=1
                print(f"Jogo PREMIADO! ID: {game_id}, Loteria: {lottery_type}, Acertos: {hits}, Faixa: {faixa_premio_str}")
        
        print(f"Verificação em lote concluída. {jogos_atualizados} jogos verificados/atualizados. {jogos_premiados_novos} novos prêmios identificados.")

    except Exception as e:
        print(f"Erro durante a verificação em lote de jogos salvos: {e}")

if __name__ == '__main__':
    print("Executando o Verificador de Jogos Salvos...")
    verificar_jogos_salvos_batch()
    print("Verificador de Jogos Salvos concluído.")