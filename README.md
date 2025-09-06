# Cooksy-RecipeAI

# 🍳 Cooksy – Teman Masak Virtualmu

Cooksy adalah aplikasi berbasis **Streamlit** yang menjadi teman masak virtual ramah untuk Foodie & Bestie semua.  
Dengan dukungan **Large Language Model (LLM)** [Meta Llama 3.1 - 8B Instruct], Cooksy mampu:

- 🎯 Menjawab pertanyaan seputar masak **atau ngobrol santai**  
- 📝 Membuat resep otomatis dari bahan yang kamu punya  
- 📥 Menyediakan tombol **download resep** (.txt)  
- 💡 Memberikan rekomendasi substitusi bahan jika ada yang tidak tersedia  

---

## 🚀 Demo
Aplikasi bisa dicoba langsung setelah dideploy di **Streamlit Cloud**.  
https://cooksy-ai-temanmasakmu.streamlit.app/

---

## 📂 Struktur Project
```
cooksy-app/
│
├── app.py                 # File utama (UI Streamlit)
├── logic.py               # Logika backend & interaksi AI
├── Resep_makanan_indo.csv # Dataset resep Indonesia
├── .gitignore             # Abaikan .env 
└── README.md              # Dokumentasi project
```

---

## ⚙️ Cara Menjalankan di Lokal

### 1. Clone Repository
```bash
git clone https://github.com/nabilaaaakn/Cooksy-RecipeAI.git
cd Cooksy-RecipeAI
```

### 2. Buat Virtual Environment (opsional tapi disarankan)
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Buat file `.env`
Di root project, buat file `.env` dengan isi:
```ini
HF_TOKEN="token_huggingface_kamu"
```

### 5. Jalankan Aplikasi
```bash
streamlit run app.py
```

---

## ☁️ Deploy ke Streamlit Cloud

1. Push project ini ke GitHub.  
2. Buka [Streamlit Cloud](https://share.streamlit.io) → **New App**.  
3. Hubungkan repo, pilih `app.py` sebagai entry point.  
4. Masuk ke menu **Settings → Secrets** di Streamlit Cloud, lalu tambahkan:  

   ```toml
   HF_TOKEN="token_huggingface_kamu"
   ```

5. Klik **Deploy** 🚀  

---

## 🔒 Catatan Keamanan
- **Jangan pernah upload `.env` ke GitHub**  
- Simpan semua token/API key di **Streamlit Secrets** atau **GitHub Secrets**  

---

## 📦 Requirements
Buat file `requirements.txt` dengan isi berikut:
```
streamlit
pandas
scikit-learn
huggingface_hub
python-dotenv
```

---

## 📖 Tentang Project Ini
Project ini termasuk kategori:
- ✅ **AI (Artificial Intelligence)**  
- ✅ **NLP (Natural Language Processing)** karena berfokus pada teks & bahasa  
- ✅ **LLM (Large Language Model)** karena menggunakan model **Llama 3.1-8B**  

Dengan kata lain:  
> Cooksy adalah aplikasi **AI berbasis NLP** yang memanfaatkan **LLM** untuk menghasilkan resep masakan dan percakapan interaktif.  

---

## ✨ Credit
- Model AI: [Meta Llama 3.1 - 8B Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)  
- Dataset: https://www.kaggle.com/datasets/albertnathaniel12/food-recipes-dataset  
- Framework: [Streamlit](https://streamlit.io)  

---.
