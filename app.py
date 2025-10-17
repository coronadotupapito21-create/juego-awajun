# -*- coding: utf-8 -*-
import streamlit as st
import unicodedata
import random
from dataclasses import dataclass
import requests
import os
import glob
import re

# --------------------------------
#   CONFIG & ESTILO AMAZONÍA
# --------------------------------
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
.j-btn > button{ border-radius: 999px !important; padding:.55rem 1rem !important; font-weight:600;
  border: 1px solid rgba(13,92,73,.15) !important; }
hr{border-top: 1px dashed rgba(13,92,73,.22);}
.small{opacity:.85; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

# --------------------------------
#   UTILIDADES
# --------------------------------
def strip_diacritics(s: str) -> str:
    nf = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")

def normalize(s: str, ignore_accents=True) -> str:
    s = s.strip().casefold()
    return strip_diacritics(s) if ignore_accents else s

def slugify_es(word_es: str) -> str:
    s = strip_diacritics(word_es).lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def fetch_image_bytes(urls):
    """Devuelve bytes de la primera URL que responda 200 (con User-Agent)."""
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AwajunGame/1.0)"}
    for u in urls:
        try:
            r = requests.get(u, headers=headers, timeout=8)
            if r.status_code == 200 and r.headers.get("content-type","").startswith("image"):
                return r.content
        except Exception:
            continue
    return None

def themed_urls(query: str, slot: int):
    """Fallback online (si no hay locales)."""
    q = query.replace(" ", ",")
    seed = abs(hash(f"{q}-{slot}")) % 100000
    return [
        f"https://loremflickr.com/800/600/{q},amazon,forest?lock={seed}",
        f"https://picsum.photos/seed/{seed}/800/600",
    ]

def local_images_for(es: str):
    """
    Busca imágenes locales en repo: images/<slug>/ (cualquier extensión).
    Retorna lista de rutas (bytes list) si hay 1-4 imágenes, sino [].
    """
    slug = slugify_es(es)  # ej. "Yuca" -> "yuca", "Árbol grande" -> "arbol-grande"
    folder = os.path.join("images", slug)
    if not os.path.isdir(folder):
        return []

    paths = []
    # Tomar 1,2,3,4.* si existen, o cualquier archivo de imagen
    preferred = []
    for i in [1,2,3,4]:
        preferred.extend(glob.glob(os.path.join(folder, f"{i}.*")))
    others = []
    if not preferred:
        for ext in ("*.jpg","*.jpeg","*.png","*.webp"):
            others.extend(glob.glob(os.path.join(folder, ext)))
    files = preferred if preferred else others
    files = files[:4]

    contents = []
    for p in files:
        try:
            with open(p, "rb") as f:
                contents.append(f.read())
        except Exception:
            continue
    return contents

@dataclass
class Level:
    es: str       # Español
    aw: str       # Awajún
    queries: list # 4 conceptos para fallback

    def images_bytes(self):
        # 1) Intentar locales
        loc = local_images_for(self.es)
        if len(loc) >= 1:
            # Si hay 1-4 locales, duplica hasta 4 si faltan
            while len(loc) < 4:
                loc.append(loc[-1])
            return loc[:4]

        # 2) Fallback online (si no subiste locales)
        imgs = []
        for i, q in enumerate(self.queries[:4]):
            content = fetch_image_bytes(themed_urls(q, i))
            imgs.append(content)
        return imgs

# --------------------------------
#   VOCABULARIO (Español → Awajún)
# --------------------------------
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

# Consultas base para fallback online (por si no hay locales)
Q = {
    "Yuca": ["cassava root", "cassava harvest", "cassava food", "cassava leaves"],
    "Plátano": ["plantain banana", "banana bunch", "banana plant", "banana fruit"],
    "Maíz": ["corn field", "corn cobs", "maize kernels", "corn harvest"],
    "Agua": ["river water", "waterfall", "stream", "rain"],
    "Sol": ["sun sunrise", "bright sun", "sun rays", "sunset"],
    "Luna": ["moon night", "full moon", "crescent moon", "night sky"],
    "Estrella": ["starry sky", "milky way stars", "constellation", "night stars"],
    "Fuego": ["campfire", "fire flame", "bonfire", "firewood"],
    "Tierra": ["soil ground", "farmland earth", "soil hands", "earth texture"],
    "Río": ["amazon river", "river curve", "river in forest", "river boats"],
    "Montaña": ["mountain range", "mountain peak", "andes mountains", "rocky mountain"],
    "Casa": ["jungle house", "wooden house", "hut", "rural house"],
    "Perro": ["dog portrait", "dog running", "puppy", "dog closeup"],
    "Gato": ["cat portrait", "kitten", "cat eyes", "cat sitting"],
    "Pájaro": ["bird flying", "tropical bird", "bird on branch", "colorful bird"],
    "Mono": ["monkey jungle", "howler monkey", "capuchin monkey", "monkey family"],
    "Pez": ["fish underwater", "tropical fish", "fish closeup", "river fish"],
    "Serpiente": ["snake jungle", "boa snake", "snake closeup", "viper"],
    "Hormiga": ["ant macro", "ants", "leafcutter ants", "ant trail"],
    "Mariposa": ["butterfly macro", "butterfly wings", "colorful butterfly", "butterfly flower"],
    # ... puedes ir ampliando Q para asegurar mejor el fallback
}

def queries_for(es: str):
    if es in Q:
        return Q[es][:4]
    return [es, f"{es} naturaleza", f"{es} selva", es]

LEVELS = [Level(es=es, aw=aw, queries=queries_for(es)) for es, aw in RAW]

# --------------------------------
#   ESTADO
# --------------------------------
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

# --------------------------------
#   UI
# --------------------------------
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

# Nivel actual
k = ss.order[ss.idx]
lvl = LEVELS[k]
img_bytes = lvl.images_bytes()

c1, c2 = st.columns(2)
def show(col, content):
    if content:
        col.image(content, use_container_width=True)
    else:
        col.info("🖼️ Sube imágenes locales a /images/<palabra>/ o pulsa Siguiente.")

show(c1, img_bytes[0]); show(c2, img_bytes[1])
show(c1, img_bytes[2]); show(c2, img_bytes[3])

# --------------------------------
#   MÚLTIPLE OPCIÓN (3 alternativas)
# --------------------------------
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

with st.expander("📚 Ver respuesta"):
    st.write(f"**{lvl.es}** → **{lvl.aw}** (Awajún)")
st.markdown("---")
st.caption("Imágenes locales: repo /images/<palabra>/ (1-4). Fallback online solo si no subes locales.")










