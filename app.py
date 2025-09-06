# ==============================================================================
# 🖥️ APP.PY
# File ini HANYA berisi kode untuk User Interface (UI) menggunakan Streamlit.
# Versi ini ditambahkan dengan fitur download resep.
# ==============================================================================
import streamlit as st
import logic
import re

st.set_page_config(page_title="Cooksy", page_icon="🍳", layout="centered")

@st.cache_resource
def load_all_resources():
    try:
        return logic.setup_resources()
    except (ValueError, ConnectionError, FileNotFoundError) as e:
        st.error(f"Gagal memuat aplikasi: {e}")
        st.stop()

client, df, vectorizer, tfidf_matrix, substitusi = load_all_resources()

def generate_filename(recipe_text: str) -> str:
    match = re.search(r"^#\s*(.*)", recipe_text, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        clean_title = re.sub(r'[^\w\s-]', '', title).strip().lower()
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        return f"resep_{clean_title}.txt"
    return "resep_sobat_dapur.txt"

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Anda adalah 'Cooksy' 🧑‍🍳, seorang teman masak AI yang super ramah, gaul, dan penuh semangat. "
        "Keahlian UTAMA Anda adalah menciptakan resep masakan Indonesia yang lezat dan anti-gagal. "
        "Anda juga BISA dan SUKA ngobrol santai tentang topik lain di luar memasak. "
        "Gunakan bahasa yang santai, sapa pengguna dengan 'Foodie' atau 'Bestie', dan selalu gunakan emoji yang ceria."
    )
}

if "messages" not in st.session_state:
    st.session_state.messages = [
        SYSTEM_PROMPT,
        {"role": "assistant", "content": "Hai, Foodie! Aku **Cooksy** 🧑‍🍳, teman masak virtualmu! Siap bikin masakan enak hari ini? Atau mau ngobrol-ngobrol dulu juga boleh, lho!"}
    ]

st.title("🧑‍🍳 Cooksy")
st.caption("✨ Resep enaakk & obrolan hangat, langsung dari Teman Masakmu! ✨")

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("is_recipe", False):
                st.download_button(
                    label="📥 Unduh Resep (.txt)", data=message["content"],
                    file_name=message.get("file_name", "resep.txt"), mime="text/plain"
                )

if prompt := st.chat_input("Masak apa kita hari ini, Foodie?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Cooksy lagi ngubek-ngubek ide nih... 🍳"):
            classification_prompt = (
                f"Apakah pertanyaan ini meminta resep masakan? Jawab HANYA 'Resep' atau 'Obrolan'.\n\nPertanyaan: \"{prompt}\""
            )
            try:
                classifier_response = client.chat.completions.create(
                    messages=[{"role": "user", "content": classification_prompt}], max_tokens=5, temperature=0.0
                )
                decision = classifier_response.choices[0].message.content.strip()
            except Exception:
                keywords_resep = ["masak", "resep", "buat", "bikin", "bahan", "ada", "punya", "dari", ","]
                decision = "Resep" if any(keyword in prompt.lower() for keyword in keywords_resep) else "Obrolan"

            if "Resep" in decision:
                st.info("Siaap! Kayaknya ada yang mau masak enak nih. Aku cariin resep paling pas ya, Bestie! 📝", icon="👍")
                mode_info, response_generator = logic.proses_permintaan_resep(
                    client, df, vectorizer, tfidf_matrix, substitusi, prompt
                )
                full_response = st.write_stream(response_generator)
                st.session_state.messages.append({
                    "role": "assistant", "content": full_response,
                    "is_recipe": True, "file_name": generate_filename(full_response)
                })
                st.download_button(
                    label="📥 Unduh Resep (.txt)", data=full_response,
                    file_name=generate_filename(full_response), mime="text/plain"
                )
            else:
                st.info("Asiik, kita ngobrol santai aja ya! 💬", icon="😊")
                response_generator = logic.proses_chat_biasa(client, st.session_state.messages)
                full_response = st.write_stream(response_generator)
                st.session_state.messages.append({
                    "role": "assistant", "content": full_response, "is_recipe": False
                })
