import streamlit as st

st.set_page_config(page_title="4 fotos 1 palabra - Awajún", page_icon="🧩", layout="centered")

st.title("🧩 4 fotos 1 palabra — Awajún")

col1, col2 = st.columns(2)
col1.image("https://images.unsplash.com/photo-1500530855697-b586d89ba3ee", use_container_width=True)
col1.image("https://images.unsplash.com/photo-1469474968028-56623f02e42e", use_container_width=True)
col2.image("https://images.unsplash.com/photo-1519681393784-d120267933ba", use_container_width=True)
col2.image("https://images.unsplash.com/photo-1470770903676-69b98201ea1c", use_container_width=True)

ans = st.text_input("✍️ Escribe la palabra en awajún:")
if st.button("Comprobar"):
    st.success("Tu respuesta fue: " + ans)
