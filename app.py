# -*- coding: utf-8 -*-
import streamlit as st
import unicodedata
import random
import os, re

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
.block-container{padding-top:1.2rem; max-width: 980px;}
h1, h2, h3 { color: var(--jungle) !important; text-align:center; }

.option-btn{
  display:inline-block; background:#f8faf9; color:#0d5c49;
  border:2px solid #0d5c49; border-radius:12px; padding:12px 16px;
  font-weight:700; text-align:center; margin:8px; width:100%;
  transition:all .15s ease;
}
.option-btn:hover{ background:#dff4ec; border-color:#1f8a70; }

.result-box{
  padding:26px; border-radius:16px; text-align:center;
  font-size:28px; font-weight:800; color:white; margin:18px 0 6px 0;
}
.correct{ background:#1f8a70; }
.incorrect{ background:#c0392b; }

.j-chip{
  display:inline-block; padding:6px 12px; border-radius:999px;
  background:linear-gradient(90deg,#1f8a70,#0d5c49); color:#fff; font-weight:700;
}
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
    """Convierte 'Árbol grande' -> 'arbolgrande' (solo minúsculas y sin tildes) para el nombre de carpeta."""
    s = strip_diacritics(word_es).lower()
    s = re.sub(r"[^a-z0-9]+", "", s)
    return s

def local_image_paths_for(word_es: str):
    """Busca imágenes en /images/<palabra>/1.jpg..4.jpg (jpg/jpeg/png/webp)."""
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
#   DATOS DEL JUEGO (30 niveles)
# =========================
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

TOTAL_LEVELS = len(RAW)  # 30
POINTS_PER_HIT = 5

# =========================
#   PANTALLA FINAL
# =========================
def show_final_screen():
    st.header("🏁 ¡Juego finalizado!")
    st.subheader(f"Respondiste correctamente **{ss.corrects} de {TOTAL_LEVELS}** preguntas")
    st.write(f"**Puntaje total:** {ss.score} puntos")

    ratio = ss.corrects / TOTAL_LEVELS
    if ratio == 1:
        st.success("🌟 ¡Felicidades! Eres un verdadero maestro del Awajún. ¡Perfecto!")
    elif ratio >= 0.8:
        st.success("💪 ¡Excelente! Conoces muy bien las palabras Awajún.")
    elif ratio >= 0.5:
        st.warning("🙂 Buen trabajo, sigue practicando para mejorar.")
    else:
        st.error("🌱 ¡Ánimo! Cada intento suma. Vuelve a jugar y mejorarás.")

    st.markdown("#### 📊 Tus resultados")
    # Gráfica nativa (sin matplotlib)
    import pandas as pd
    df = pd.DataFrame(
        {"Cantidad": [ss.corrects, ss.incorrects]},
        index=["Correctas", "Incorrectas"]
    )
    st.bar_chart(df)

    st.divider()
    if st.button("🔄 Jugar de nuevo", use_container_width=True):
        ss.idx = 0
        ss.score = 0
        ss.corrects = 0
        ss.incorrects = 0
        ss.finished = False
        ss.options_by_level = {}
        st.rerun()

# =========================
#   JUEGO
# =========================
st.markdown('<span class="j-chip">Awajún · 4 fotos 1 palabra</span>', unsafe_allow_html=True)
st.title("🌿 Aprende Awajún jugando")

if ss.finished:
    show_final_screen()
    st.stop()

# Nivel actual
es, aw = RAW[ss.idx]
paths = local_image_paths_for(es)

st.subheader(f"Nivel {ss.idx+1} / {TOTAL_LEVELS}")
st.caption("¿Cuál es la palabra en Awajún?")

c1, c2 = st.columns(2)
if len(paths) >= 4:
    c1.image(paths[0], use_container_width=True); c2.image(paths[1], use_container_width=True)
    c1.image(paths[2], use_container_width=True); c2.image(paths[3], use_container_width=True)
else:
    st.warning(f"Faltan imágenes en: `images/{slugify_es(es)}/1.jpg..4.jpg`")

# Opciones estables por nivel
if ss.idx not in ss.options_by_level:
    correct = aw
    pool = [opp_aw for _, opp_aw in RAW if opp_aw != correct]
    wrong = random.sample(pool, 3)
    options = [correct] + wrong
    random.shuffle(options)
    ss.options_by_level[ss.idx] = options
else:
    options = ss.options_by_level[ss.idx]

# Botones tipo “cuadritos”
cols = st.columns(2)
selected = None
for i, opt in enumerate(options):
    if cols[i % 2].button(f"{opt}", use_container_width=True, key=f"opt_{ss.idx}_{i}"):
        selected = opt

# Validación y avance
if selected:
    if normalize(selected) == normalize(aw):
        ss.score += POINTS_PER_HIT
        ss.corrects += 1
        st.markdown('<div class="result-box correct">✅ ¡CORRECTO!</div>', unsafe_allow_html=True)
    else:
        ss.incorrects += 1
        st.markdown('<div class="result-box incorrect">❌ INCORRECTO</div>', unsafe_allow_html=True)

    ss.idx += 1
    if ss.idx >= TOTAL_LEVELS:
        ss.finished = True
    st.experimental_rerun()

st.markdown(f"**Puntaje:** {ss.score} puntos")
st.divider()
st.caption("Coloca tus imágenes en `/images/<palabra>/1.jpg..4.jpg` (minúsculas, sin tildes). Ej: `images/montana/1.jpg`")




















