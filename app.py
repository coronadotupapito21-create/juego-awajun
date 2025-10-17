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
    """Convierte 'Árbol' -> 'arbol' (minúsculas y sin tildes)."""
    s = strip_diacritics(word_es).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def local_image_paths_for(word_es: str):
    """
    Busca imágenes locales en images/<nombre>/ con nombres 1,2,3,4 y
    extensiones .jpg/.jpeg/.png/.webp.
    Si hay menos de 4, repite para completar.
    """
    slug = slugify_es(word_es)
    folder = os.path.join("images", slug)
    if not os.path.isdir(folder):
        return []

    paths = []
    for i in [1, 2, 3, 4]:
        found = None
        for ext in ("jpg", "jpeg", "png", "webp"):
            p = os.path.join(folder, f"{i}.{ext}")
            if os.path.exists(p):
                found = p
                break
        if found:
            paths.append(found)

    if not paths:
        for ext in ("jpg", "jpeg", "png", "webp"):
            paths.extend(sorted(glob.glob(os.path.join(folder, f"*.{ext}"))))

    if not paths:
        return []

    while len(paths) < 4:
        paths.append(paths[-1])
    return paths[:4]

# =========================
#   DATOS DEL JUEGO
# =========================
@dataclass
class Level:
    es: str
    aw: str
    def images(self): return local_image_paths_for(self.es)

RAW = [
    ("Agua","Nantak"),
    ("Sol","Etsa"),
    ("Luna","Nantu"),
    ("Estrella","Wáim"),
    ("Fuego","Néemi"),
    ("Tierra","Iwanch"),
]
LEVELS = [Level(es=es, aw=aw) for es, aw in RAW]

# =========================
#   ESTADO
# =========================
ss = st.session_state
if "order" not in ss:
    ss.order = list(range(len(LEVELS)))
    random.shuffle(ss.order)

if "idx" not in ss:           # índice del nivel actual (en el orden barajado)
    ss.idx = 0

if "score" not in ss:
    ss.score = 0

# Opciones estables por nivel: dict[level_id] = [opt1,opt2,opt3,opt4]
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
k = ss.order[ss.idx]     # ID real del nivel
lvl = LEVELS[k]
paths = lvl.images()

c1, c2 = st.columns(2)

def show(col, path):
    if path and os.path.exists(path):
        col.image(path, use_container_width=True)
    else:
        col.warning(f"🖼️ Falta imagen en `images/{slugify_es(lvl.es)}/1.jpg..4.jpg`")

if paths:
    show(c1, paths[0]); show(c2, paths[1])
    show(c1, paths[2]); show(c2, paths[3])
else:
    st.error(f"No encontré imágenes en `images/{slugify_es(lvl.es)}/`. "
             f"Sube 1–4 imágenes 1.jpg, 2.jpg, 3.jpg, 4.jpg.")

# =========================
#   OPCIONES ESTABLES (4)
# =========================
# Generar una sola vez por nivel
if k not in ss.options_by_level:
    # 1 correcta + 2 incorrectas (random) + 1 incorrecta extra (si quieres 4 exactas)
    correct = lvl.aw
    all_aw = [aw for _, aw in RAW if aw != correct]
    wrong = random.sample(all_aw, 3)  # 3 incorrectas
    opts = [correct] + wrong
    random.shuffle(opts)
    ss.options_by_level[k] = opts

options = ss.options_by_level[k]

st.markdown("### ✍️ Elige la palabra correcta (Awajún):")
# Clave única por nivel para que no cambie cuando se rerenderiza
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

# =========================
#   LÓGICA DE BOTONES
# =========================
if hint:
    st.info(f"💡 **Pista**: Español → **{lvl.es}**")

if check:
    if choice_value is None:
        st.warning("Selecciona una alternativa antes de comprobar.")
    else:
        if normalize(choice_value, ignore_accents) == normalize(lvl.aw, ignore_accents):
            st.success("✅ ¡Correcto!")
            ss.score += 10
            # Avanzar y limpiar selección para el próximo nivel
            ss.idx = (ss.idx + 1) % len(LEVELS)
            st.rerun()
        else:
            st.error("❌ Incorrecto, ¡inténtalo otra vez!")

if skip or nextB:
    ss.idx = (ss.idx + 1) % len(LEVELS)
    st.rerun()

st.markdown("---")
st.caption("Coloca tus imágenes en /images/<palabra>/1.jpg..4.jpg (solo minúsculas y sin tildes). Ejemplo: images/agua/1.jpg")















