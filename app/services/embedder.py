import requests
from typing import List, Dict, Union

# Konfigurasi LLM (Di produksi, ini harus ditarik dari .env via app/core/config.py)
OLLAMA_URL_EMBED = "http://localhost:11434/api/embed"
EMBED_MODEL = "nomic-embed-text"

def generate_embeddings(chunks: List[Union[str, Dict]]) -> List[List[float]]:
    """
    Mengubah daftar teks menjadi vektor (768 dimensi) secara batch/massal.
    Sesuai cetak biru: Dilarang menggunakan perulangan (tight loop) HTTP per chunk 
    untuk mencegah bottleneck pada GPU/CPU.
    """
    if not chunks:
        return []

    # Ekstraksi teks jika input berupa dictionary (dari chunker.py)
    texts_to_embed = []
    for chunk in chunks:
        if isinstance(chunk, dict):
            texts_to_embed.append(chunk.get("chunk_text", ""))
        else:
            texts_to_embed.append(chunk)

    payload = {
        "model": EMBED_MODEL,
        "input": texts_to_embed
    }

    try:
        # Endpoint /api/embed Ollama memproses array teks sekaligus secara internal
        response = requests.post(OLLAMA_URL_EMBED, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        embeddings = data.get("embeddings", [])
        
        # Validasi dimensi vektor secara deterministik (Harus 768 untuk Nomic)
        if embeddings and len(embeddings[0]) != 768:
            print(f"[Fatal] Anomali dimensi vektor. Diharapkan 768, diterima {len(embeddings[0])}.")
            return []
            
        return embeddings

    except requests.exceptions.RequestException as e:
        print(f"[Fatal] Gagal menghubungi layanan embedding Ollama: {e}")
        return []
    except Exception as e:
        print(f"[Fatal] Kesalahan ekstraksi vektor: {e}")
        return []