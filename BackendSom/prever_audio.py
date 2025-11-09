"""
prever_audio.py (Versão 3 - À prova de PowerShell)
---------------
Carrega o modelo SVM treinado (o .joblib) e o usa para
prever a classe de um novo arquivo de áudio.

Esta versão remove o prefixo '& ' do PowerShell e normaliza
o caminho para o encontrar corretamente.
"""

import os
import joblib
import numpy as np
import librosa
import soundfile as sf
from scipy import stats

# ======================================
# CONFIGURAÇÕES (DEVEM SER IDÊNTICAS AO TREINO)
# ======================================
SR = 22050
N_MFCC = 13
MODELO_PATH = os.path.join(os.getcwd(), "svm_passaros_v1.joblib")

# ======================================
# FUNÇÕES DE EXTRAÇÃO (CÓPIA EXATA DO EXTRATOR)
# ======================================
def carregar_audio(caminho, sr=SR):
    try:
        y, orig_sr = sf.read(caminho, dtype='float32')
    except Exception as e:
        print(f"Erro ao ler {caminho}: {e}")
        return None
    if y.ndim > 1: y = np.mean(y, axis=1)
    if orig_sr != sr: y = librosa.resample(y, orig_sr=orig_sr, target_sr=sr)
    return y

def extrair_features_com_stats(y_audio, sr=SR, n_mfcc=N_MFCC):
    if y_audio is None or len(y_audio) == 0: 
        return None 
    mfcc = librosa.feature.mfcc(y=y_audio, sr=sr, n_mfcc=n_mfcc)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)
    mfcc_max = np.max(mfcc, axis=1)
    mfcc_min = np.min(mfcc, axis=1)
    mfcc_median = np.median(mfcc, axis=1)
    mfcc_skew = stats.skew(mfcc, axis=1)
    mfcc_kurt = stats.kurtosis(mfcc, axis=1)
    vetor_features = np.concatenate((
        mfcc_mean, mfcc_std, mfcc_max, mfcc_min, mfcc_median, mfcc_skew, mfcc_kurt
    ))
    return vetor_features

# ======================================
# EXECUÇÃO DA PREVISÃO (MODIFICADA)
# ======================================
if __name__ == "__main__":
    # 1. Carregar o modelo (o Pipeline)
    print(f"Carregando modelo de {MODELO_PATH}...")
    if not os.path.exists(MODELO_PATH):
        print("!!! ERRO: Modelo 'svm_passaros_v1.joblib' não encontrado.")
        print("Por favor, execute 'treinar_modelo_final.py' primeiro.")
        exit()
        
    pipeline_modelo = joblib.load(MODELO_PATH)
    
    # 2. Obter um novo áudio do usuário
    while True:
        caminho_audio = input("\nArraste um áudio para cá (ou digite o caminho) e pressione Enter (ou 's' para sair): ")

        if caminho_audio.lower() == 's':
            break

        # --- NOVA LÓGICA DE LIMPEZA DE CAMINHO ---
        # 1. Limpa espaços em branco no início/fim
        caminho_limpo = caminho_audio.strip()
        
        # 2. [A CHAVE] Remove o prefixo '& ' do PowerShell
        if caminho_limpo.startswith("& "):
            caminho_limpo = caminho_limpo[2:].strip() # Remove o '& ' e espaços
        
        # 3. Limpa as aspas/plicas (comuns no drag-and-drop)
        caminho_limpo = caminho_limpo.strip("'\"")
        
        # 4. Converte para um caminho absoluto e normalizado
        caminho_final = os.path.abspath(caminho_limpo)
        # ---------------------------------------------

        print(f"DEBUG: Caminho lido (original): [{caminho_audio}]")
        print(f"DEBUG: Caminho final (tentativa): [{caminho_final}]")

        # 5. Verifica se o caminho final existe
        if not os.path.exists(caminho_final):
            print(f"ERRO: O sistema não encontrou o ficheiro em: {caminho_final}")
            print("Tente novamente.")
            continue

        # 6. Processar o áudio (Usando o caminho final)
        print("Processando áudio...")
        audio_data = carregar_audio(caminho_final, sr=SR)
        features_novas = extrair_features_com_stats(audio_data, sr=SR)
        
        if features_novas is None:
            print("Não foi possível processar o áudio.")
            continue
            
        # 7. Preparar as features para o modelo
        features_2d = features_novas.reshape(1, -1)
        
        # 8. Fazer a Previsão
        predicao = pipeline_modelo.predict(features_2d)
        probabilidades = pipeline_modelo.predict_proba(features_2d)
        
        classe_predita = predicao[0]
        confianca = np.max(probabilidades) * 100
        
        print("\n--- RESULTADO DA PREVISÃO ---")
        print(f"   Espécie: {classe_predita.upper()}")
        print(f"   Confiança: {confianca:.2f}%")