# -*- coding: utf-8 -*-
import streamlit as st
import unicodedata
import random
from dataclasses import dataclass

# ------------------------------
#   CONFIG & AMAZONÍA THEME
# ------------------------------
st.set_page_config(
    page_title="Awajún: 4 fotos 1 palabra",
    page_icon="🌿",
    layout="centered"
)

# Fondo y estilos (inspirado en Amazonía)
st.markdown("""
<style>
:root{
  --jungle:#0d5c49;
  --leaf:#1f8a70;
  --lime:#7ed957;
  --cream:#f6fff5;
}
html, body, [data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 600px at 10% -20%, #e8f7ee 0%, #f6fff5 35%, #ecfff7 60%, #f9fff7 100%), 
              url('https://images.unsplash.com/photo-1529336953121-a1b466d8b3f7?q=80&w=1400&auto=format&fit=crop') center/cover fixed no-repeat;
}
[data-testid="stHeader"] {background-color: rgba(255,255,255,0.0);}
.block-container{padding-top:1.5rem;}

h1, h2, h3 { color: var(--jungle) !important; }
.j-card{
  background: rgba(255,255,255,0.82);
  border: 1px solid rgba(13,92,73,.08);
  border-radius: 18px; padding: 14px 18px;
  box-shadow: 0 8px 28px rgba(13,92,73,.08);
}
.j-pill{
  background: linear-gradient(90deg, var(--leaf), var(--jungle));
  color: white; padding: 8px 14px; border-radius: 999px;
  font-weight:600; display:inline-block; letter-spacing:.2px;
}
.j-btn > button{
  border-radius: 999px !important; padding:.55rem 1rem !important; font-weight:600;
  border: 1px solid rgba(13,92,73,.15) !important;
}
hr{border-top: 1px dashed rgba(13,92,73,.22);}
.small{opacity:.8; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

# ------------------------------
#   HELPERS
# ------------------------------
def strip_diacritics(s: str) -> str:
    nf = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")

def normalize(s: str, ignore_accents=True) -> str:
    s = s.strip().casefold()
    return strip_diacritics(s) if ignore_accents else s

def img(q: str) -> str:
    """
    Imagen dinámica de Unsplash por consulta (ES/EN).
    Puedes reemplazar por URLs fijas cuando quieras.
    """
    q = q.replace(" ", "+")
    # tamaño estable; 4 imágenes con queries diferentes para variedad
    return f"https://source.unsplash.com/800x600/?{q}"

@dataclass
class Level:
    es: str
    aw: str
    # 4 consultas de imagen (se convertirán a URLs)
    queries: list

    def images(self):
        return [img(q) for q in self.queries[:4]]

# ------------------------------
#   DATASET (80 pares)
#   Para cada ítem doy 4 keywords (ES/EN) para imágenes.
# ------------------------------
RAW = [
    ("Agua","Nantak",           ["agua","river","water","rainforest"]),
    ("Sol","Etsa",              ["sol","sun","sunlight","sky"]),
    ("Luna","Nantu",            ["luna","moon","night sky","crater"]),
    ("Estrella","Wáim",         ["estrella","star","milky way","night"]),
    ("Fuego","Néemi",           ["fuego","fire","campfire","flame"]),
    ("Tierra","Iwanch",         ["tierra","soil","ground","earth"]),
    ("Cielo","Náem",            ["cielo","sky","clouds","blue sky"]),
    ("Árbol","Númi",            ["árbol","tree","tropical tree","amazon"]),

