# -*- coding: utf-8 -*-
import streamlit as st
import unicodedata
import random
import os, glob, re
import matplotlib.pyplot as plt
from dataclasses import dataclass

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
[data-testid="stHeader"] {background-color: rgba(255,255,255,0);}
.block-container{padding-top:1.5rem; max-width: 980px;}
h1, h2, h3 { color: var(--jungle) !important; text-align:center; }
.option-btn{
  display:inline-block; background:#f2f2f2; color:#0d5c49;
  border:2px solid #0d5c49; border-radius:12px; padding:10px 15px;
  font-weight:600; text-align:center; margin:6px; width:40%;
}
.option-btn:hover{ background:#dff4ec; border-color:#1f8a70; }
.result-box{
  padding:25px; border-radius:16px; text-align:center;
  font-size:28px; font-weight:700; color:white; margin-top:15px;
}
.correct{ background:#1f8a70; }
.incorrect{ background:#c0392b; }
</style>
""", unsafe_allow_html=True)

# =========================
#   FUNCIONES AUXILIARES
# =========================
def strip_diacritics(s: str) -> str:
    nf = unicodedata.normalize("NFD", s)
    return "".join(ch for ch in nf if unicodedata.category(ch) != "Mn")

def normalize(s: str) -> str:
    return strip_diacritics(s.strip().casefold())

def slugify_es(word_es: str) -> str:
    """Convierte 'Árbol' -> 'arbol' (solo minúsculas y sin tildes)."""
    s = strip_diacritics(word_es).lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s

def local_image_paths_for(word_es: str):
    """Busca imágenes en /images/<palabra>/1.jpg..4.jpg"""
    slug = slugify_es(word_es)
    folder = os.path.join("images", slug)
    paths = []
    for i in [1, 2, 3, 4]:
        for ext in ("jpg", "jpeg", "png", "webp"):
            p = os.path.join(folder, f"{i}.{ext}")
            if os.path.exists(p):
                paths.append(p)
                break
    return paths

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
    ("Fuego","Néemi"), ("Tierra","Iwanch"), ("Cielo","Náem"), ("Arbol","Númi"),
    ("Flor","Páyam"), ("Hoja","Tákem"), ("Frio","Tsetsék"), ("Calor","Sékem"),
    ("Viento","Pákem"), ("Lluvia","Tsúgki"), ("Rio","Nantakjai"), ("Montana","Wákan"),
    ("Casa","Jíi"), ("Cocina","Wájam"), ("Perro","Pétsi"), ("Gato","Mítsa"),
    ("Pajaro","Wíim"), ("Mono","Túukam"), ("Pez","Námpet"), ("Serpiente","Wámpis"),
    ("Hormiga","Túutam"), ("Mariposa","Páach"), ("Nina","Túunam"), ("Comida","Núun"),
    ("Yuca","Kúcha"), ("Platano","Pítsa"),
]
LEVELS = [Level(es=es, aw=aw) for es, aw in RAW]

# =========================
#   ESTADO DEL JUEGO
# =========================
ss = st.session_state
if "idx" not in ss: ss.idx = 0
if "score" not in ss: ss.score = 0
if "corrects" not in ss: ss.corrects = 0
if "incorrects" not in ss: ss.incorrects = 0
if "finished" not in ss: ss.finished = False
if "options_by_level" not in ss: ss.options_by_level = {}

# =========================
#   JUEGO FINALIZADO
# =========================
if ss.finished:
    st.header("🏁 ¡Juego finalizado!")
    st.subheader(f"Respondiste correctamente {ss.corrects} de {len(LEVELS)} preguntas")

    # Mensaje final según puntaje
    ratio = ss.corrects / len(LEVELS)
    if ratio == 1:
        st.success("🌟 ¡Felicidades! Eres un verdadero maestro del Awajún. ¡Perfecto!")
    elif ratio >= 0.8:
        st.success("💪 ¡Excelente! Conoces muy bien las palabras Awajún.")
    elif ratio >= 0.5:
        st.warning("🙂 Buen intento, sigue practicando para mejorar.")
    else:
        st.error("🌱 No te preocupes, sigue aprendiendo. ¡La práctica hace al maestro!")

    # Gráfica de resultados
    fig, ax = plt.subplots()
    ax.bar(["Correctas", "Incorrectas"], [ss.corrects, ss.incorrects], color=["#1f8a70", "#c0392b"])
    ax.set_title("Resultados del Juego", fontsize=16)
    st.pyplot(fig)

    st.markdown("---")
    if st.button("🔄 Jugar de nuevo"):
        ss.idx = 0
        ss.score = 0
        ss.corrects = 0
        ss.incorrects = 0
        ss.finished = False
        ss.options_by_level = {}
        st.rerun()
    st.stop()

# =========================
#   NIVEL ACTUAL
# =========================
lvl = LEVELS[ss.idx]
paths = lvl.images()

st.title(f"Nivel {ss.idx+1} / {len(LEVELS)}")
st.subheader(f"¿Cuál es la palabra en Awajún?")

col1, col2 = st.columns(2)
if len(paths) >= 4:
    col1.image(paths[0]); col2.image(paths[1])
    col1.image(paths[2]); col2.image(paths[3])
else:
    st.warning(f"Faltan imágenes en: images/{slugify_es(lvl.es)}/")

# =========================
#   OPCIONES (BOTONES)
# =========================
if ss.idx not in ss.options_by_level:
    correct = lvl.aw
    pool = [aw for _, aw in RAW if aw != correct]
    wrong = random.sample(pool, 3)
    opts = [correct] + wrong
    random.shuffle(opts)
    ss.options_by_level[ss.idx] = opts

options = ss.options_by_level[ss.idx]
cols = st.columns(2)
selected = None

for i, opt in enumerate(options):
    if cols[i % 2].button(opt, use_container_width=True):
        selected = opt

# =========================
#   VALIDACIÓN DE RESPUESTA
# =========================
if selected:
    if normalize(selected) == normalize(lvl.aw):
        ss.score += 5
        ss.corrects += 1
        st.markdown('<div class="result-box correct">✅ ¡CORRECTO!</div>', unsafe_allow_html=True)
    else:
        ss.incorrects += 1
        st.markdown('<div class="result-box incorrect">❌ INCORRECTO</div>', unsafe_allow_html=True)
    
    ss.idx += 1
    if ss.idx >= len(LEVELS):
        ss.finished = True
    st.rerun()

st.markdown(f"**Puntaje:** {ss.score} puntos")
st.markdown("---")
st.caption("Coloca tus imágenes en /images/<palabra>/1.jpg..4.jpg (todo en minúsculas, sin tildes).")



















