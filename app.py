# -*- coding: utf-8 -*-
import streamlit as st
import unicodedata
import random
from dataclasses import dataclass
import os, glob, re

# =========================
#   CONFIGURACIÓN VISUAL
# =========================
st.set_page_config(page_title="Awajún: 4 fotos 1 palabra", page_icon="🌿", layout="centered")

st.markdown("""
<style>
:root{ --jungle:#0d5c49; --leaf:#1f8a70; --lime:#7ed957; --cream:#f6fff5; }
html, body, [data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 600px at 10% -20%, #e8f7ee 0%, #f6fff5 35%, #ecfff7 60%, #f9fff7 100%);
}
[data-testid="stHeader"] {background-color: rgba(255,255,255,0.0);}
.block-container{padding-top:1.5rem; max-width: 980px;}
h1, h2, h3 { color: var(--jungle) !important; }
.j-card{ background: rgba(255,255,255,0.92); border: 1px solid rgba(13,92,73,.08);
  border-radius: 18px; padding: 14px 18px; box-shadow: 0 10px 28px rgba(13,92,73,.10); }
.j-pill{ background: linear-gradient(90deg, var(--leaf), var(--jungle)); color: white;
  padding: 8px 14px; border-radius: 999px; font-weight:600; display:inline-block; letter-spacing:.2px; }
hr{border-top: 1px dashed rgba(13,92,73,.22);}
.small{opacity:.85; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

# =========================
#   FUNCIONES AUXILIARES
# =========================
def strip_diacritics(s: str) -> str:
    nf = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")

def normalize(s: str, ignore_accents=True) -> str:
    s = s.strip().casefold()
    return strip_diacritics(s) if ignore_accents else s

def slugify_es(word_es: str) -> str:
    """Convierte 'Árbol' -> 'arbol' (solo minúsculas y sin tildes)."""
    s = strip_diacritics(word_es).lower()
    s = re.sub(r"[^a-z0-9]+", "", s)  # quita espacios y símbolos
    return s

def local_image_paths_for(word_es: str):
    """Busca imágenes en /images/<palabra>/1.jpg..4.jpg"""
    slug = slugify_es(word_es)
    folder = os.path.join("images", slug)
    if not os.path.isdir(folder):
        return []
    
    paths = []
    for i in [1, 2, 3, 4]:
        for ext in ("jpg", "jpeg", "png", "webp"):
            p = os.path.join(folder, f"{i}.{ext}")
            if os.path.exists(p):
                paths.append(p)
                break

    return paths if paths else []

# =========================
#   DATOS DEL JUEGO
# =========================
@dataclass
class Level:
    es: str
    aw: str
    def images(self): return local_image_paths_for(self.es)

RAW = [
    ("Agua","Nantak"), ("Sol","Etsa"), ("Luna","Nantu"), ("Estrella","Wáim"),
    ("Fuego","Néemi"), ("Tierra","Iwanch"), ("Cielo","Náem"), ("Árbol","Númi"),
    ("Flor","Páyam"), ("Hoja","Tákem"), ("Frío","Tsetsék"), ("Calor","Sékem"),
    ("Viento","Pákem"), ("Lluvia","Tsúgki"), ("Río","Nantakjai"), ("Montaña","Wákan"),
    ("Casa","Jíi"), ("Cocina","Wájam"), ("Perro","Pétsi"), ("Gato","Mítsa"),
    ("Pájaro","Wíim"), ("Mono","Túukam"), ("Pez","Námpet"), ("Serpiente","Wámpis"),
    ("Hormiga","Túutam"), ("Mariposa","Páach"), ("Niña","Túunam"), ("Comida","Núun"),
    ("Yuca","Kúcha"), ("Plátano","Pítsa"),
]
LEVELS = [Level(es=es, aw=aw) for es, aw in RAW]

# =========================
#   ESTADO
# =========================
ss = st.session_state
if "order" not in ss:
    ss.order = list(range(len(LEVELS)))
    random.shuffle(ss.order)
if "idx" not in ss:
    ss.idx = 0
if "score" not in ss:
    ss.score = 0
if "options_by_level" not in ss:
    ss.options_by_level = {}

# =========================
#   INTERFAZ PRINCIPAL
# =========================
st.markdown('<div class="j-pill">Awajún · 4 fotos 1 palabra</div>', unsafe_allow_html=True)
st.title("🌿 Aprende Awajún jugando")

colL, colR = st.columns([2,1])
with colL:
    st.markdown('<div class="j-card">', unsafe_allow_html=True)
    st.write("**Puntaje:**", ss.score)
    st.write("**Nivel:**", ss.idx + 1, "/", len(LEVELS))
    st.markdown('</div>', unsafe_allow_html=True)
with colR:
    opt = st.selectbox("Comparación", ["Flexible (ignora acentos)", "Estricta"], index=0)
    ignore_accents = (opt == "Flexible (ignora acentos)")

st.markdown("---")

# =========================
#   NIVEL ACTUAL
# =========================
k = ss.order[ss.idx]
lvl = LEVELS[k]
paths = lvl.images()

c1, c2 = st.columns(2)
def show(col, path):
    if path and os.path.exists(path):
        col.image(path, use_container_width=True)
    else:
        col.warning(f"🖼️ Falta imagen en `images/{slugify_es(lvl.es)}/1.jpg..4.jpg`")

if paths:
    show(c1, paths[0]); show(c2, paths[1] if len(paths)>1 else None)
    show(c1, paths[2] if len(paths)>2 else None); show(c2, paths[3] if len(paths)>3 else None)
else:
    st.error(f"No encontré imágenes en `images/{slugify_es(lvl.es)}/`. Sube 1–4 archivos .jpg numerados 1..4.")

# =========================
#   OPCIONES ESTABLES
# =========================
if k not in ss.options_by_level:
    correct = lvl.aw
    pool = [aw for _, aw in RAW if aw != correct]
    wrong = random.sample(pool, 3)
    opts = [correct] + wrong
    random.shuffle(opts)
    ss.options_by_level[k] = opts
options = ss.options_by_level[k]

st.markdown("### ✍️ Elige la palabra correcta (Awajún):")
choice_key = f"choice_level_{k}"
choice_value = st.radio(
    "alternativas",
    options=options,
    index=None,
    label_visibility="collapsed",
    key=choice_key,
)

b1, b2, b3, b4 = st.columns(4)
check = b1.button("Comprobar ✅", use_container_width=True)
hint  = b2.button("Pista 💡", use_container_width=True)
skip  = b3.button("Saltar ⏭️", use_container_width=True)
nextB = b4.button("Siguiente ▶️", use_container_width=True)

if hint:
    st.info(f"💡 **Pista**: Español → **{lvl.es}**")

if check:
    if choice_value is None:
        st.warning("Selecciona una alternativa antes de comprobar.")
    else:
        if normalize(choice_value, ignore_accents) == normalize(lvl.aw, ignore_accents):
            st.success("✅ ¡Correcto!")
            ss.score += 10
            ss.idx = (ss.idx + 1) % len(LEVELS)
            st.rerun()
        else:
            st.error("❌ Incorrecto, ¡inténtalo otra vez!")

if skip or nextB:
    ss.idx = (ss.idx + 1) % len(LEVELS)
    st.rerun()

st.markdown("---")
st.caption("Las carpetas deben estar en minúsculas, sin tildes y con imágenes 1.jpg..4.jpg. Ejemplo: images/montana/1.jpg")

















