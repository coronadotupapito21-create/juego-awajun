# -*- coding: utf-8 -*-
import streamlit as st
import unicodedata
import random
from dataclasses import dataclass
import requests

# --------------------------------
#   CONFIG & ESTILO AMAZONÍA
# --------------------------------
st.set_page_config(page_title="Awajún: 4 fotos 1 palabra", page_icon="🌿", layout="centered")
st.markdown("""
<style>
:root{ --jungle:#0d5c49; --leaf:#1f8a70; --lime:#7ed957; --cream:#f6fff5; }
html, body, [data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 600px at 10% -20%, #e8f7ee 0%, #f6fff5 35%, #ecfff7 60%, #f9fff7 100%),
              url('https://images.unsplash.com/photo-1529336953121-a1b466d8b3f7?q=80&w=1600&auto=format&fit=crop') center/cover fixed no-repeat;
}
[data-testid="stHeader"] {background-color: rgba(255,255,255,0.0);}
.block-container{padding-top:1.5rem; max-width: 980px;}
h1, h2, h3 { color: var(--jungle) !important; }
.j-card{ background: rgba(255,255,255,0.85); border: 1px solid rgba(13,92,73,.08);
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
    """
    Construye proveedores para un concepto. slot = 0..3 para variar semillas.
    1) loremflickr (temático: selva/amazonas)  2) picsum (fallback estable)
    """
    q = query.replace(" ", ",")
    seed = abs(hash(f"{q}-{slot}")) % 100000
    return [
        f"https://loremflickr.com/800/600/{q},jungle,amazon,forest?lock={seed}",
        f"https://picsum.photos/seed/{seed}/800/600",
    ]

@dataclass
class Level:
    es: str       # Español
    aw: str       # Awajún
    queries: list # 4 conceptos de imagen

    def images_bytes(self):
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

# --------------------------------
#   QUERIES por palabra (para que concuerden las imágenes)
# --------------------------------
Q = {
    "Agua": ["river water", "waterfall", "stream", "rain"],
    "Sol": ["sun sunrise", "bright sun", "sun rays", "sunset"],
    "Luna": ["moon night", "full moon", "crescent moon", "night sky"],
    "Estrella": ["starry sky", "milky way stars", "constellation", "night stars"],
    "Fuego": ["campfire", "fire flame", "bonfire night", "firewood flame"],
    "Tierra": ["soil ground", "farmland earth", "soil hands", "earth texture"],
    "Cielo": ["blue sky clouds", "cloudy sky", "sky horizon", "sky daylight"],
    "Árbol": ["single tree", "tropical tree", "tree in forest", "tree closeup"],
    "Flor": ["flower closeup", "wildflower", "jungle flower", "flower macro"],
    "Hoja": ["leaf macro", "green leaf", "jungle leaf", "leaf veins"],
    "Frío": ["cold frost", "snow cold", "winter cold", "icy landscape"],
    "Calor": ["hot sun heat", "desert heat", "heat haze", "sunny hot"],
    "Viento": ["wind blowing trees", "windy field", "flags in wind", "storm wind"],
    "Lluvia": ["rain drops", "rain street", "rainforest rain", "umbrella rain"],
    "Río": ["amazon river", "river curve", "river in forest", "river boats"],
    "Montaña": ["mountain range", "mountain peak", "andes mountains", "rocky mountain"],
    "Casa": ["jungle house", "wooden house", "hut", "rural house"],
    "Cocina": ["kitchen cooking", "traditional kitchen", "pots stove", "cooking fire"],
    "Comida": ["traditional food", "meal dish", "food plate", "banquet"],
    "Yuca": ["cassava root", "cassava harvest", "cassava food", "yuca dish"],
    "Plátano": ["plantain banana bunch", "banana plant", "banana fruit", "banana harvest"],
    "Maíz": ["corn field", "corn cobs", "corn kernels", "maize harvest"],
    "Pescar": ["fishing river", "fisherman boat", "fish catch", "net fishing"],
    "Cazar": ["hunting bow", "hunter forest", "jungle hunting", "spear hunting"],
    "Perro": ["dog portrait", "dog running", "puppy", "dog closeup"],
    "Gato": ["cat portrait", "kitten", "cat eyes", "cat sitting"],
    "Pájaro": ["bird flying", "tropical bird", "bird on branch", "colorful bird"],
    "Mono": ["monkey jungle", "howler monkey", "capuchin monkey", "monkey family"],
    "Pez": ["fish underwater", "tropical fish", "fish closeup", "river fish"],
    "Serpiente": ["snake jungle", "boa snake", "snake closeup", "viper"],
    "Hormiga": ["ant macro", "ants", "leafcutter ants", "ant trail"],
    "Mariposa": ["butterfly macro", "butterfly wings", "colorful butterfly", "butterfly flower"],
    "Árbol grande": ["giant tree", "ceiba tree", "huge tree trunk", "ancient tree"],
    "Hacha": ["axe tool", "wood chopping", "axe log", "axe closeup"],
    "Lanza": ["spear weapon", "tribal spear", "hunter spear", "wooden spear"],
    "Flecha": ["arrow quiver", "arrow bow", "arrows", "archery arrow"],
    "Cerbatana": ["blowgun", "tribal blowgun", "amazon blowgun", "hunter blowpipe"],
    "Cuerda": ["rope coil", "rope knot", "twine", "hemp rope"],
    "Ropa": ["clothes", "traditional clothes", "folded clothes", "wardrobe clothes"],
    "Sombrero": ["hat", "straw hat", "traditional hat", "hat portrait"],
    "Niño": ["boy child", "smiling boy", "kid playing", "school boy"],
    "Niña": ["girl child", "smiling girl", "kid drawing", "school girl"],
    "Hombre": ["man portrait", "adult man", "farmer man", "man outdoors"],
    "Mujer": ["woman portrait", "adult woman", "woman smile", "woman outdoors"],
    "Hermano": ["brothers", "siblings boys", "two brothers", "family brothers"],
    "Hermana": ["sisters", "siblings girls", "two sisters", "family sisters"],
    "Abuelo": ["grandfather", "elder man", "old man portrait", "grandpa"],
    "Abuela": ["grandmother", "elder woman", "old woman portrait", "grandma"],
    "Madre": ["mother child", "mom hugging child", "mother", "mom portrait"],
    "Padre": ["father child", "dad with kid", "father", "dad portrait"],
    "Fuerte": ["strong man flexing", "strength", "strong athlete", "heavy lifting"],
    "Débil": ["weak tired", "exhausted person", "sick weak", "weak hands"],
    "Grande": ["big elephant", "huge object", "giant size", "very big"],
    "Pequeño": ["small tiny", "miniature", "little kid", "tiny object"],
    "Alto": ["tall person", "tall tree", "tall building", "height"],
    "Bajo": ["short person", "low height", "low table", "short kid"],
    "Gordo": ["fat person", "overweight", "plump", "chubby"],
    "Delgado": ["slim thin", "skinny person", "thin body", "slender"],
    "Blanco": ["white color", "white wall", "white fabric", "white paint"],
    "Negro": ["black color", "black fabric", "black wall", "black texture"],
    "Verde": ["green color", "green nature", "green leaves", "green wall"],
    "Rojo": ["red color", "red paint", "red fabric", "red light"],
    "Amarillo": ["yellow color", "yellow wall", "yellow paint", "yellow fabric"],
    "Azul": ["blue color", "blue wall", "blue paint", "blue sky"],
    "Fruta": ["tropical fruits", "fruit basket", "fruit market", "fresh fruit"],
    "Arena": ["sand beach", "sand desert", "sand texture", "sand closeup"],
    "Roca": ["rock stone", "boulder rock", "rock cliff", "stone texture"],
    "Camino": ["road path", "jungle path", "trail", "dirt road"],
    "Trabajo": ["work job", "people working", "team work", "office work"],
    "Cantar": ["singing", "mic singer", "choir", "sing performance"],
    "Bailar": ["dance performance", "folk dance", "dancers", "party dance"],
    "Dormir": ["sleeping person", "sleep bed", "nap", "sleep night"],
    "Beber": ["drink water", "drinking cup", "drink bottle", "drink glass"],
    "Ver": ["watching", "binoculars", "look observe", "see view"],
    "Escuchar": ["listening headphones", "listen ear", "audio listening", "music listening"],
    "Hablar": ["talk conversation", "speaking", "people talking", "speech"],
}

def queries_for(es: str):
    # Si no definimos una entrada, usar algo genérico
    if es in Q:
        return Q[es][:4]
    return [es, f"{es} amazonía", f"{es} naturaleza", f"{es} selva"]

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
        col.info("🖼️ No se pudo cargar la imagen, intenta Siguiente.")

show(c1, img_bytes[0]); show(c2, img_bytes[1])
show(c1, img_bytes[2]); show(c2, img_bytes[3])

# --------------------------------
#   MÚLTIPLE OPCIÓN (3 alternativas)
# --------------------------------
# opciones = 1 correcta (Awajún del nivel) + 2 incorrectas al azar
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
    key=f"choice_{ss.idx}",  # para que cambie con cada nivel
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
            st.rerun()   # ← ya no experimental
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
st.caption("Hecho con ❤️ para aprender Awajún. Imágenes: LoremFlickr / Picsum (fallback) con temática amazónica.")









