# ==============================================================================
# 🧠 LOGIC.PY
# File ini berisi semua logika backend, pemrosesan data, dan interaksi dengan AI.
# ==============================================================================

import os
import pandas as pd
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Muat environment variables dari file .env
load_dotenv()

# ====================
# A. SETUP & INISIALISASI RESOURCE
# ====================

def setup_resources():
# 1. Setup Hugging Face Client
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("Token Hugging Face (HF_TOKEN) tidak ditemukan! Mohon atur di file .env")
        
    model_id = "meta-llama/Llama-3.1-8B-Instruct"
    try:
        client = InferenceClient(model=model_id, token=hf_token)
    except Exception as e:
        raise ConnectionError(f"Gagal terhubung ke Hugging Face API: {e}")

# 2. Load dan proses dataset
    try:
        df = pd.read_csv("Resep_makanan_indo.csv")
        df["Ingredients Cleaned"] = df["Ingredients"].apply(
            lambda x: [b.strip().lower() for b in str(x).split(",") if b.strip()]
        )
        df["ingredients_str"] = df["Ingredients Cleaned"].apply(lambda x: " ".join(x))
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(df["ingredients_str"])
    except FileNotFoundError:
        raise FileNotFoundError("File 'Resep_makanan_indo.csv' tidak ditemukan.")

# 3. Kamus Substitusi
    substitusi = {
        "bawang putih": ("bawang bombay", "Aroma mirip untuk tumisan dasar"),
        "minyak goreng": ("margarin", "Sebagai lemak untuk menumis/menggoreng"),
        "gula pasir": ("madu", "Pemanis alami"),
        "susu sapi": ("santan", "Memberikan tekstur creamy dan gurih"),
        "tepung terigu": ("tepung maizena", "Sebagai pengental, alternatif gluten-free"),
        "cabai merah": ("bubuk lada hitam", "Memberikan rasa pedas pengganti cabai"),
        "jeruk nipis": ("cuka masak", "Memberikan rasa asam yang segar"),
        "tomat": ("saus tomat", "Pengganti rasa asam-manis dari tomat segar"),
        "daging ayam": ("tahu atau tempe", "Alternatif protein nabati yang populer"),
        "daging sapi": ("jamur tiram atau portobello", "Memberikan tekstur 'daging' sebagai alternatif nabati"),
        "udang": ("ikan dori fillet", "Sama-sama protein dari hasil laut dengan tekstur lembut"),
    }

    return client, df, vectorizer, tfidf_matrix, substitusi

# ====================
# B. FUNGSI-FUNGSI HELPER
# ====================

#Mengubah string input bahan menjadi list bahan yang bersih.
def bersihkan_bahan(teks: str) -> list[str]:
    return sorted([b.strip().lower() for b in teks.split(",") if b.strip()])

#Mencari resep paling mirip di dataset menggunakan TF-IDF & Cosine Similarity.
def cari_resep_tfidf(user_bahan_str: str, vectorizer, tfidf_matrix, df, top_n=1) -> pd.DataFrame:
    user_vec = vectorizer.transform([user_bahan_str])
    sim = cosine_similarity(user_vec, tfidf_matrix).flatten()

# Memberikan threshold untuk memastikan kemiripan yang relevan
    if sim.max() > 0.15:
        idx_top = sim.argsort()[-top_n:][::-1]
        return df.iloc[idx_top]
    return pd.DataFrame()

# ====================
# C. LOGIKA INTI & PROMPT ENGINEERING
# ====================

#Fungsi terpusat untuk memanggil LLM dan melakukan streaming response.
def generate_response_llm(client: InferenceClient, messages: list, max_tokens: int = 2048):
    try:
        response_stream = client.chat.completions.create(
            messages=messages, max_tokens=max_tokens, temperature=0.7, top_p=0.95, stream=True
        )
        for chunk in response_stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:
        yield f"Waduh, ada sedikit gangguan di dapur Cooksy nih. Coba lagi ya. (Error: {e})"

#Otak utama pembuat resep. Menentukan mode (Minimalist/Dataset) secara otomatis dan menyusun prompt yang tegas untuk LLM.
def proses_permintaan_resep(client: InferenceClient, df: pd.DataFrame, vectorizer, tfidf_matrix, substitusi: dict, bahan_text: str):
    bahan_list = bersihkan_bahan(bahan_text)
    user_bahan_str = " ".join(bahan_list)
    
    system_prompt = (
        "Anda adalah 'Cooksy' 🧑‍🍳, seorang teman masak AI yang super ramah, gaul, dan penuh semangat. "
        "Keahlian UTAMA Anda adalah menciptakan resep masakan Indonesia yang lezat dan anti-gagal. "
        "Gunakan bahasa yang santai, sapa pengguna dengan 'Foodie' atau 'Bestie', dan selalu gunakan emoji yang ceria."
    )

# --- LOGIKA MODE OTOMATIS ---    

# MODE MINIMALIST: Jika bahan sedikit, fokus pada kreativitas dengan bahan terbatas.
    if len(bahan_list) <= 4:
        mode_info = "Bahannya simpel nih, Bestie! Aku bikinin resep minimalis yang sat-set-sat-set ya!"
        user_prompt = (
            f"**Bahan:** {', '.join(bahan_list)}\n\n"
            "**Tugas:** Buat satu resep super simpel HANYA pakai bahan di atas. **ATURAN WAJIB:** Jangan tambah bahan lain sama sekali.\n\n"
            "**Format Jawaban (Markdown):**\n# [Nama Masakan Simpel]\n## 🍳 Bahan\n## 🥣 Langkah\n## ⏱️ Waktu"
        )
# MODE DATASET (RAG): Jika bahan cukup banyak, cari inspirasi dari dataset.
    else:
        kandidat = cari_resep_tfidf(user_bahan_str, vectorizer, tfidf_matrix, df)
        mode_info = "Mantap, bahannya lumayan lengkap! Aku cari inspirasi dari buku resepku dulu ya, Foodie!"
        user_prompt = f"**Bahan utama:** {', '.join(bahan_list)}\n\n**Tugas:** Kreasikan ulang resep yang lebih baik berdasarkan bahan pengguna dan inspirasi dari database (jika ada).\n\n"
        if not kandidat.empty:
            k = kandidat.iloc[0]
            user_prompt += f"**Inspirasi Resep:**\n- Nama: {k['Title Cleaned']}\n- Bahan Asli: {', '.join(k['Ingredients Cleaned'])}\n\n"
        else:
            user_prompt += "**Info:** Tidak ada resep mirip di database, jadi buatkan resep baru yang kreatif.\n\n"
        user_prompt += "**Format Jawaban (Markdown):**\n# [Nama Masakan Keren]\n## 🍳 Bahan & Takaran\n## 🥣 Langkah Memasak\n## ✨ Tips (Opsional)"
        
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    return mode_info, generate_response_llm(client, messages)

def proses_chat_biasa(client: InferenceClient, history: list):
    return generate_response_llm(client, history, max_tokens=512)
