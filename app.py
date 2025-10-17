# -*- coding: utf-8 -*-
import streamlit as st
import unicodedata
import random
from dataclasses import dataclass

# ------------------------------
#   CONFIG & ESTILO AMAZONÍA
# ------------------------------
st.set_page_config(
    page_title="Awajún: 4 fotos 1 palabra",
    page_icon="🌿",
    layout="centered"
)

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
              url('https://images.unsplash.com/photo-1529336953121-a1b466d8b3f7?q=80&w=1600&auto=format&fit=crop') center/cover fixed no-repeat;
}
[data-testid="stHeader"] {background-color: rgba(255,255,255,0.0);}
.block-container{padding-top:1.5rem; max-width: 980px;}

h1, h2, h3 { color: var(--jungle) !important; }
.j-card{
  background: rgba(255,255,255,0.85);
  border: 1px solid rgba(13,92,73,.08);
  border-radius: 18px; padding: 14px 18px;
  box-shadow: 0 10px 28px rgba(13,92,73,.10);
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
.small{opacity:.85; font-size:.9rem;}
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

def img_url(q: str) -> str:
    """Imagen dinámica (Unsplash Source) por consulta simple."""
    q = q.replace(" ", "+")
    return f"https://source.unsplash.com/800x600/?{q}"

@dataclass
class Level:
    es: str
    aw: str
    queries: list  # 4 strings para imágenes

    def images(self):
        return [img_url(q) for q in self.queries[:4]]

def q4(word_es: str):
    # 4 búsquedas por palabra con sabores amazónicos
    return [
        word_es,
        f"{word_es} amazonía",
        f"{word_es} naturaleza",
        f"{word_es} selva"
    ]

# ------------------------------
#   DATA: Español → Awajún (80)
#   (Si quieres cambiar imágenes, edita las queries con lo que desees)
# ------------------------------
RAW = [
    ("Agua","Nantak"),
    ("Sol","Etsa"),
    ("Luna","Nantu"),
    ("Estrella","Wáim"),
    ("Fuego","Néemi"),
    ("Tierra","Iwanch"),
    ("Cielo","Náem"),
    ("Árbol","Númi"),
    ("Flor","Páyam"),
    ("Hoja","Tákem"),
    ("Frío","Tsetsék"),
    ("Calor","Sékem"),
    ("Viento","Pákem"),
    ("Lluvia","Tsúgki"),
    ("Río","Nantakjai"),
    ("Montaña","Wákan"),
    ("Casa","Jíi"),
    ("Cocina","Wájam"),
    ("Comida","Núun"),
    ("Yuca","Kúcha"),
    ("Plátano","Pítsa"),
    ("Maíz","Kúnki"),
    ("Pescar","Nampet"),
    ("Cazar","Wáju"),
    ("Perro","Pétsi"),
    ("Gato","Mítsa"),
    ("Pájaro","Wíim"),
    ("Mono","Túukam"),
    ("Pez","Námpet"),
    ("Serpiente","Wámpis"),
    ("Hormiga","Túutam"),
    ("Mariposa","Páach"),
    ("Árbol grande","Númijáa"),
    ("Hacha","Wáncham"),
    ("Lanza","Tsámak"),
    ("Flecha","Píjam"),
    ("Cerbatana","Túuntam"),
    ("Cuerda","Wátsa"),
    ("Ropa","Tújam"),
    ("Sombrero","Wáipam"),
    ("Niño","Túujin"),
    ("Niña","Túunam"),
    ("Hombre","Aéntsa"),
    ("Mujer","Núwa"),
    ("Hermano","Wáajin"),
    ("Hermana","Wáajum"),
    ("Abuelo","Apachum"),
    ("Abuela","Apatum"),
    ("Madre","Núwam"),
    ("Padre","Aéntsam"),
    ("Fuerte","Kákajam"),
    ("Débil","Nútsam"),
    ("Grande","Wájam"),
    ("Pequeño","Tíjam"),
    ("Alto","Nátkam"),
    ("Bajo","Wáatsam"),
    ("Gordo","Wátsum"),
    ("Delgado","Nátsum"),
    ("Blanco","Tsáam"),
    ("Negro","Wáampam"),
    ("Verde","Núkam"),
    ("Rojo","Wáinam"),
    ("Amarillo","Túmpam"),
    ("Azul","Pátkam"),
    ("Fruta","Píkam"),
    ("Flor","Páyam"),     # (repetido en tu lista; lo dejamos como nivel adicional)
    ("Hoja","Tákem"),     # (repetido)
    ("Fuego","Néemi"),    # (repetido)
    ("Arena","Tsáamaj"),
    ("Roca","Pátam"),
    ("Camino","Náim"),
    ("Trabajo","Wájamum"),
    ("Cantar","Pátsuk"),
    ("Bailar","Nújain"),
    ("Dormir","Tákam"),
    ("Comer","Núun"),     # (repetido)
    ("Beber","Náajum"),
    ("Ver","Wájeem"),
    ("Escuchar","Tsáitum"),
    ("Hablar","Núkamun"),
]

LEVELS = [Level(es=es, aw=aw, queries=q4(es)) for es, aw in RAW]

# ------------------------------
#   ESTADO
# ------------------------------
if "order" not in st.session_state:
    st.session_state.order = list(range(len(LEVELS)))
    random.shuffle(st.session_state.order)

if "idx" not in st.session_state:
    st.session_state.idx = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "reveal" not in st.session_state:
    st.session_state.reveal = False

# ------------------------------
#   UI
# ------------------------------
st.markdown('<div class="j-pill">Awajún · 4 fotos 1 palabra</div>', unsafe_allow_html=True)
st.title("🌿 Aprende Awajún jugando")

with st.container():
    colL, colR = st.columns([2,1])
    with colL:
        st.markdown('<div class="j-card">', unsafe_allow_html=True)
        st.write("**Puntaje:**", st.session_state.score)
        st.write("**Nivel:**", st.session_state.idx + 1, "/", len(LEVELS))
        st.markdown('</div>', unsafe_allow_html=True)
    with colR:
        opt = st.selectbox("Comparación", ["Flexible (ignora acentos)", "Estricta"], index=0)
        ignore_accents = (opt == "Flexible (ignora acentos)")

st.markdown("---")

# Nivel actual
k = st.session_state.order[st.session_state.idx]
lvl = LEVELS[k]
imgs = lvl.images()

c1, c2 = st.columns(2)
c1.image(imgs[0], use_container_width=True)
c2.image(imgs[1], use_container_width=True)
c1.image(imgs[2], use_container_width=True)
c2.image(imgs[3], use_container_width=True)

st.markdown("### ✍️ Escribe la palabra en **awajún**:")
ans = st.text_input(" ", placeholder="Tu respuesta aquí…", label_visibility="collapsed")

b1, b2, b3, b4 = st.columns(4)
check = b1.button("Comprobar ✅", use_container_width=True)
hint  = b2.button("Pista 💡", use_container_width=True)
skip  = b3.button("Saltar ⏭️", use_container_width=True)
nextB = b4.button("Siguiente ▶️", use_container_width=True)

target = lvl.aw
if hint:
    st.session_state.reveal = True

if check:
    if normalize(ans, ignore_accents) == normalize(target, ignore_accents) and ans.strip():
        st.success("✅ ¡Correcto!")
        st.session_state.score += 10
        st.session_state.idx = (st.session_state.idx + 1) % len(LEVELS)
        st.session_state.reveal = False
        st.experimental_rerun()
    else:
        st.error("❌ Incorrecto, ¡inténtalo otra vez!")

if skip or nextB:
    st.session_state.idx = (st.session_state.idx + 1) % len(LEVELS)
    st.session_state.reveal = False
    st.experimental_rerun()

if st.session_state.reveal:
    st.info(f"💡 **Pista**: Español → **{lvl.es}**")

with st.expander("📚 Ver respuesta (solo si te atascas)"):
    st.write(f"**{lvl.es}** → **{lvl.aw}** (Awajún)")

st.markdown("---")
st.caption("Hecho con ❤️ para aprender Awajún. Imágenes: Unsplash (búsqueda automática).")



