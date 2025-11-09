import os
import numpy as np
import librosa
import soundfile as sf
import pandas as pd
import requests
import hashlib
from scipy import stats 
from audiomentations import Compose, AddGaussianNoise, PitchShift, TimeStretch, Shift 

# ======================================
# CONFIGURAÇÕES GERAIS
# ======================================
PASTA_BASE = os.path.join(os.getcwd(), "audios_passaros")
ARQUIVO_SAIDA = os.path.join(os.getcwd(), "features_passaros_AUG_SK.csv") 

CATEGORIAS_MAP = {
    "sabia": 1,
    "bemtevi": 2
}

SR = 22050
N_MFCC = 13
FORMATO_PRIORITARIO = ['.wav', '.mp3', '.ogg'] 

# --- NOVA SEÇÃO: CONFIGURAÇÃO DO DATA AUGMENTATION ---
augment_pipeline = Compose([
    AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.5),
    PitchShift(min_semitones=-2, max_semitones=2, p=0.5),
    TimeStretch(min_rate=0.8, max_rate=1.2, p=0.5),
    
    # --- LINHA CORRIGIDA ---
    Shift(min_shift=-0.5, max_shift=0.5, shift_unit="fraction", p=0.5) 
    # -----------------------
])

N_AUMENTACOES = 4 

# ======================================
# FUNÇÕES DE DOWNLOAD (Sem mudanças)
# ======================================
def baixar_pasta_github_api(api_url, local_path, pasta_raiz=""):
    try:
        r = requests.get(api_url)
        r.raise_for_status() 
        itens = r.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar API do GitHub ({api_url}): {e}")
        return
    if not isinstance(itens, list):
        print(f"Resposta inesperada da API: {itens.get('message', 'Erro')}")
        return
    for item in itens:
        if item['type'] == 'file' and any(item['name'].lower().endswith(ext) for ext in FORMATO_PRIORITARIO):
            caminho_arquivo_local = os.path.join(local_path, item['name'])
            if os.path.exists(caminho_arquivo_local): continue
            try:
                file_r = requests.get(item['download_url'])
                file_r.raise_for_status()
                os.makedirs(os.path.dirname(caminho_arquivo_local), exist_ok=True)
                with open(caminho_arquivo_local, 'wb') as f: f.write(file_r.content)
            except requests.exceptions.RequestException as e:
                print(f"    Falha ao baixar {item['name']}: {e}")
        elif item['type'] == 'dir':
            baixar_pasta_github_api(item['url'], os.path.join(local_path, item['name']), os.path.join(pasta_raiz, item['name']))

def baixar_audios():
    if os.path.exists(PASTA_BASE):
        print("Pasta de áudios já existe. Pulando download.")
        return
    print("Baixando áudios do GitHub via API...")
    os.makedirs(PASTA_BASE, exist_ok=True)
    API_BASE_URL = "https://api.github.com/repos/FilipyTav/IdentificadorSom/contents/"
    BRANCH_REF = "?ref=master"
    pastas_para_baixar = {
        "DadosDeAudio/Bem-te-vi (Pitangus sulphuratus)": "bemtevi",
        "DadosDeAudio/Sabiá-laranjeira (Turdus rufiventris)": "sabia"
    }
    for pasta_api, pasta_local in pastas_para_baixar.items():
        url_completa_api = API_BASE_URL + pasta_api + BRANCH_REF
        caminho_local_completo = os.path.join(PASTA_BASE, pasta_local)
        print(f"\nProcessando pasta: {pasta_local}")
        os.makedirs(caminho_local_completo, exist_ok=True)
        baixar_pasta_github_api(url_completa_api, caminho_local_completo)
    print("\nDownload seletivo concluído.")

# ======================================
# FUNÇÕES DE EXTRAÇÃO (Sem mudanças)
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

def calcular_hash_arquivo(caminho, block_size=65536):
    md5 = hashlib.md5()
    try:
        with open(caminho, 'rb') as f:
            while True:
                data = f.read(block_size)
                if not data: break
                md5.update(data)
    except IOError as e:
        print(f"Erro ao ler arquivo {caminho} para hash: {e}")
        return None
    return md5.hexdigest()

# ======================================
# EXECUÇÃO (Sem mudanças)
# ======================================
if __name__ == "__main__":
    baixar_audios()
    
    lista_de_features = []
    hashes_processados = set()
    stat_names = ['mean', 'std', 'max', 'min', 'median', 'skew', 'kurt'] 

    print("\nIniciando extração (Plano C: Data Augmentation + SK features)...\n")
    print(f"Vamos gerar 1 amostra Original + {N_AUMENTACOES} amostras Aumentadas por áudio.\n")

    for categoria, label in CATEGORIAS_MAP.items():
        pasta = os.path.join(PASTA_BASE, categoria)
        if not os.path.exists(pasta):
            print(f"[AVISO] Pasta não encontrada: {pasta}")
            continue

        print(f"Processando categoria: {categoria} (Label: {label})")
        
        arquivos_mapeados = {}
        for arquivo in os.listdir(pasta):
            if any(arquivo.lower().endswith(ext) for ext in FORMATO_PRIORITARIO):
                nome_base, ext = os.path.splitext(arquivo)
                ext = ext.lower()
                if nome_base not in arquivos_mapeados:
                    arquivos_mapeados[nome_base] = []
                arquivos_mapeados[nome_base].append(ext)
        print(f"  Encontrados {len(arquivos_mapeados)} áudios únicos (por nome).")
        
        i = 0
        total_arquivos = len(arquivos_mapeados)
        for nome_base, extensoes in arquivos_mapeados.items():
            i += 1
            extensao_escolhida = next((f for f in FORMATO_PRIORITARIO if f in extensoes), None)
            if extensao_escolhida is None: continue
            
            arquivo_final = nome_base + extensao_escolhida
            caminho = os.path.join(pasta, arquivo_final)
            
            print(f"  Processando ({i}/{total_arquivos}): {arquivo_final:<40}", end="")
            
            hash_arquivo = calcular_hash_arquivo(caminho)
            if hash_arquivo is None:
                print(" -> [ERRO HASH] Pulando.")
                continue
            if hash_arquivo in hashes_processados:
                print(" -> [DUPLICADO] Pulando.")
                continue
            hashes_processados.add(hash_arquivo)
            
            audio_original = carregar_audio(caminho, sr=SR)
            if audio_original is None:
                print(" -> [ERRO LEITURA] Pulando.")
                continue
                
            features_originais = extrair_features_com_stats(audio_original, sr=SR)
            if features_originais is None:
                print(" -> [ERRO FEATURES] Pulando.")
                continue
            
            linha = {}
            for j, stat_name in enumerate(stat_names):
                bloco = features_originais[j * N_MFCC : (j + 1) * N_MFCC]
                for k, valor in enumerate(bloco):
                    linha[f"mfcc_{k}_{stat_name}"] = valor
            linha["label"] = label
            linha["arquivo_origem"] = arquivo_final
            lista_de_features.append(linha)
            
            amostras_aumentadas = 0
            for n in range(N_AUMENTACOES):
                audio_aumentado = augment_pipeline(samples=audio_original, sample_rate=SR)
                features_aumentadas = extrair_features_com_stats(audio_aumentado, sr=SR)
                
                if features_aumentadas is not None:
                    linha_aug = {}
                    for j, stat_name in enumerate(stat_names):
                        bloco = features_aumentadas[j * N_MFCC : (j + 1) * N_MFCC]
                        for k, valor in enumerate(bloco):
                            linha_aug[f"mfcc_{k}_{stat_name}"] = valor
                    linha_aug["label"] = label
                    linha_aug["arquivo_origem"] = f"AUG_{n}_{arquivo_final}"
                    lista_de_features.append(linha_aug)
                    amostras_aumentadas += 1
            
            print(f" -> [OK] (1 Original + {amostras_aumentadas} Aumentadas)")

    df = pd.DataFrame(lista_de_features)
    df.to_csv(ARQUIVO_SAIDA, index=False)

    print(f"\nExtração concluída!")
    print(f"Total de {len(df)} amostras (originais + aumentadas) processadas.")
    print(f"Features salvas em: {ARQUIVO_SAIDA}")
    print("\nDistribuição das classes:")
    print(df['label'].value_counts())