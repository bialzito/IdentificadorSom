"""
extrator_features.py
--------------------
Extrai features MFCC de áudios de pássaros e salva em CSV.

Funciona em Windows, Linux ou macOS.
Baixa automaticamente os áudios do GitHub, caso não existam.

Mapeamento de classes:
- 'sabia' -> 1
- 'bemtevi' -> 2
"""

import os
import numpy as np
import librosa
import soundfile as sf
import pandas as pd
import requests
import zipfile
import io

# ======================================
# CONFIGURAÇÕES GERAIS
# ======================================
PASTA_BASE = os.path.join(os.getcwd(), "audios_passaros")
ARQUIVO_SAIDA = os.path.join(os.getcwd(), "features_passaros.csv")

# Repositórios de áudio no GitHub
LINKS_AUDIO = {
    "bemtevi": "https://github.com/FilipyTav/IdentificadorSom/archive/refs/heads/master.zip",
    "sabia": "https://github.com/FilipyTav/IdentificadorSom/archive/refs/heads/master.zip"
}

CATEGORIAS_MAP = {
    "sabia": 1,
    "bemtevi": 2
}

SR = 22050
N_MFCC = 13

# ======================================
# FUNÇÕES AUXILIARES
# ======================================
def baixar_audios():
    """Baixa o repositório com os áudios e extrai apenas as pastas dos pássaros."""
    if os.path.exists(PASTA_BASE):
        return

    print("Baixando áudios do GitHub...")
    os.makedirs(PASTA_BASE, exist_ok=True)

    url = "https://github.com/FilipyTav/IdentificadorSom/archive/refs/heads/master.zip"
    r = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(PASTA_BASE)

    origem = os.path.join(PASTA_BASE, "IdentificadorSom-master", "DadosDeAudio")

    # Mapeia e copia apenas as pastas de interesse
    for especie, nome_pasta in {
        "bemtevi": "Bem-te-vi (Pitangus sulphuratus)",
        "sabia": "Sabiá-laranjeira (Turdus rufiventris)"
    }.items():
        origem_pasta = os.path.join(origem, nome_pasta)
        destino_pasta = os.path.join(PASTA_BASE, especie)
        os.makedirs(destino_pasta, exist_ok=True)
        for arq in os.listdir(origem_pasta):
            if arq.lower().endswith((".wav", ".mp3", ".ogg")):
                os.replace(
                    os.path.join(origem_pasta, arq),
                    os.path.join(destino_pasta, arq)
                )

    print("Áudios baixados e organizados em:", PASTA_BASE)

def carregar_audio(caminho, sr=SR):
    """Carrega e normaliza o áudio."""
    try:
        y, orig_sr = sf.read(caminho)
    except Exception as e:
        print(f"Erro ao ler {caminho}: {e}")
        return None

    if y.ndim > 1:
        y = np.mean(y, axis=1)

    if orig_sr != sr:
        y = librosa.resample(y.astype(float), orig_sr=orig_sr, target_sr=sr)

    if np.max(np.abs(y)) > 0:
        y = y / np.max(np.abs(y))

    return y

def extrair_mfcc(caminho, sr=SR, n_mfcc=N_MFCC):
    """Extrai o vetor médio de MFCCs."""
    y = carregar_audio(caminho, sr)
    if y is None:
        return None
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfcc, axis=1)

# ======================================
# EXECUÇÃO
# ======================================
if __name__ == "__main__":
    baixar_audios()
    lista_de_features = []

    print("\nIniciando extração de features...\n")

    for categoria, label in CATEGORIAS_MAP.items():
        pasta = os.path.join(PASTA_BASE, categoria)
        if not os.path.exists(pasta):
            print(f"[AVISO] Pasta não encontrada: {pasta}")
            continue

        print(f"Processando categoria: {categoria} (Label: {label})")
        for arquivo in os.listdir(pasta):
            if arquivo.lower().endswith((".wav", ".mp3", ".ogg")):
                caminho = os.path.join(pasta, arquivo)
                vetor_mfcc = extrair_mfcc(caminho)
                if vetor_mfcc is not None:
                    linha = {f"mfcc_{i}": vetor_mfcc[i] for i in range(N_MFCC)}
                    linha["label"] = label
                    linha["arquivo_origem"] = arquivo
                    lista_de_features.append(linha)

    df = pd.DataFrame(lista_de_features)
    df.to_csv(ARQUIVO_SAIDA, index=False)

    print(f"\nExtração concluída!")
    print(f"Total de {len(df)} arquivos processados.")
    print(f"Features salvas em: {ARQUIVO_SAIDA}")
    print("\nDistribuição das classes:")
    print(df['label'].value_counts())
