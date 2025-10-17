# -*- coding: utf-8 -*-
import streamlit as st
import unicodedata
import random
from dataclasses import dataclass
import os, glob, re

# =========================
#   CONFIG & ESTILO
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
#   HELPERS
# =========================
def strip_diacritics(s: str) -> str:
    nf = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")

def normalize(s: str, ignore_accents=True) -> str:
    s = s.strip().casefold()
    return strip_diacritics(s) if ignore_accents else s

def slugify_es(word_es: str) -> str:
    """Convierte 'Árbol grande' -> 'arbol-grande' (para nombre de carpeta)."""
    s = strip_diacritics(word_es).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def local_image_paths_for(word_es: str):
    """
    Busca imágenes locales en images/<slug>/
    Prioriza 1.*, 2.*, 3.*, 4.*; si no, toma cualquier imagen.
    Devuelve hasta 4 rutas; si hay <4, repite para completar 4.
    """
    slug = slugify_es(word_es)
    folder = os.path.join("images", slug)
    if not os.path.isdir(folder):
        return []

    preferred = []
    for i in [1, 2, 3, 4]:
        preferred.extend(sorted(glob.glob(os.path.join(folder, f"{i}.*"))))
    others = []
    if not preferred:
        for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
            others.extend(sorted(glob.glob(os.path.join(folder, ext))))

    files = preferred if preferred else others
    files = files[:4]
    if not files:
        return []

    # Completar hasta 4
    while len(files) < 4:
        files.append(files[-1])
    return files[:4]

@dataclass
class Level:
    es: str   # Español (para carpeta y pista)
    aw: str   # Awajún (respuesta correcta)

    def images(self):
        return local_image_paths_for(self.es)

# =========================
#   VOCABULARIO (80)
# =========================
RAW = [
    ("Agua","Nantak"), ("Sol","Etsa"), ("Luna","Nantu"), ("Estrella","Wáim"),
    ("Fuego","Néemi"), ("Tierra","Iwanch"), ("Cielo","Náem"), ("Árbol","Númi"),
    ("Flor","Páyam"), ("Hoja","Tákem"), ("Frío","Tsetsék"), ("Calor","Sékem"),
    ("Viento","Pákem"), ("Lluvia","Tsúgki"), ("Río","Nantakjai"), ("Montaña","Wákan"),
    ("Casa","Jíi"), ("Cocina","Wájam"), ("Comida","Núun"), ("Yuca","Kúcha"),
    ("Plátano","Pítsa"), ("Maíz","Kúnki"), ("Pescar","Nampet"), ("Cazar","Wáju"),
    ("Perro","Pétsi"), ("Gato","Mítsa"), ("Pájaro","Wíim"), ("Mono","Túukam"),
    ("Pez","Námpet"), ("Serpiente","Wámpis"), ("Hormiga","Túutam"), ("Mariposa","Páach"),
    ("Árbol grande","Númijáa"), ("Hacha","Wáncham"), ("Lanza","Tsámak"), ("Flecha","Píjam"),
    ("Cerbatana","Túuntam"), ("Cuerda","Wátsa"), ("Ropa","Tújam"), ("Sombrero","Wáipam"),
    ("Niño","Túujin"), ("Niña","Túunam"), ("Hombre","Aéntsa"), ("Mujer","Núwa"),
    ("Hermano","Wáajin"), ("Hermana","Wáajum"), ("Abuelo","Apachum"), ("Abuela","Apatum"),
    ("Madre","Núwam"), ("Padre","Aéntsam"), ("Fuerte","Kákajam"), ("Débil","Nútsam"),
    ("Grande","Wájam"), ("Pequeño","Tíjam"), ("Alto","Nátkam"), ("Bajo","Wáatsam"),
    ("Gordo","Wátsum"), ("Delgado","Nátsum"), ("Blanco","Tsáam"), ("Negro","Wáampam"),
    ("Verde","Núkam"), ("Rojo","Wáinam"), ("Amarillo","Túmpam"), ("Azul","Pátkam"),
    ("Fruta","Píkam"), ("Arena","Tsáamaj"), ("Roca","Pátam"), ("Camino","Náim"),
    ("Trabajo","Wájamum"), ("Cantar","Pátsuk"), ("Bailar","Nújain"), ("Dormir","Tákam"),
    ("Beber","Náajum"), ("Ver","Wájeem"), ("Escuchar","Tsáitum"), ("Hablar","Núkamun"),
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
if "reveal" not in ss:
    ss.reveal = False
if "choice" not in ss:
    ss.choice = None

# =========================
#   UI
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

# ===== Nivel actual =====
k = ss.order[ss.idx]
lvl = LEVELS[k]
paths = lvl.images()

c1, c2 = st.columns(2)

def show(col, path):
    if path and os.path.exists(path):
        col.image(path, use_container_width=True)
    else:
        col.warning("🖼️ Falta imagen local. Sube a `images/{}/1..4.jpg`."
                    .format(slugify_es(lvl.es)))

if paths:
    show(c1, paths[0]); show(c2, paths[1] if len(paths)>1 else None)
    show(c1, paths[2] if len(paths)>2 else None); show(c2, paths[3] if len(paths)>3 else None)
else:
    st.error(f"No encontré imágenes en `images/{slugify_es(lvl.es)}/`. "
             f"Sube 1-4 archivos .jpg/.png/.webp con nombres 1,2,3,4.")

# ===== Alternativas (3) =====
all_aw = [aw for _, aw in RAW]
wrong = random.sample([aw for aw in all_aw if aw != lvl.aw], 2)
options = [lvl.aw] + wrong
random.shuffle(options)

st.markdown("### ✍️ Elige la palabra correcta (Awajún):")
ss.choice = st.radio(
    label="alternativas",
    options=options,
    index=None,
    label_visibility="collapsed",
    key=f"choice_{ss.idx}",
)

b1, b2, b3, b4 = st.columns(4)
check = b1.button("Comprobar ✅", use_container_width=True)
hint  = b2.button("Pista 💡", use_container_width=True)
skip  = b3.button("Saltar ⏭️", use_container_width=True)
nextB = b4.button("Siguiente ▶️", use_container_width=True)

if hint:
    ss.reveal = True

if check:
    if ss.choice is None:
        st.warning("Selecciona una alternativa antes de comprobar.")
    else:
        if normalize(ss.choice, ignore_accents) == normalize(lvl.aw, ignore_accents):
            st.success("✅ ¡Correcto!")
            ss.score += 10
            ss.idx = (ss.idx + 1) % len(LEVELS)
            ss.reveal = False
            st.rerun()
        else:
            st.error("❌ Incorrecto, ¡inténtalo otra vez!")

if skip or nextB:
    ss.idx = (ss.idx + 1) % len(LEVELS)
    ss.reveal = False
    st.rerun()

if ss.reveal:
    st.info(f"💡 **Pista**: Español → **{lvl.es}**")

st.markdown("---")
st.caption("Coloca tus imágenes en /images/<palabra>/1..4.jpg (minúsculas, sin acentos). Ej: images/yuca/1.jpg")











