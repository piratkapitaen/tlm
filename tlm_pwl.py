import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
from helpers import *
import os, time, random, datetime, re, gzip, pickle, time, psutil

# CSS für weniger Abstand nach oben
##st.markdown("""
##    <style>
##    .css-1d391kg {  /* Haupt-Container */
##        padding-top: 0rem;
##    }
##    .css-1d391kg > div:nth-child(1) {  /* Sidebar spezifisch */
##        padding-top: -1rem;
##    }
##    </style>
##    """, unsafe_allow_html=True)

# App title
st.set_page_config(page_title="TLM protocol", layout="wide")

st.markdown("""
    <style>
    /* Entferne Standard-Padding und Abstand der Sidebar */
    [data-testid="stSidebar"] {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    /* Entferne Abstand oben von Hauptcontainer */
    .css-1d391kg {  
        padding-top: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

if 'text' not in st.session_state:
    st.session_state.text = ""

def load_pickle_gzip(filename):
    with gzip.open(filename, 'rb') as file:
        return pickle.load(file)

def generate_memory():
##    print('Hallo')
##    st.session_state.text = 'Abcdef'
    # 12 Zeilen mit 4 Hexadezimalzahlen pro Zeile
    hex_table = [
        "\t".join(f"{random.randint(0, 255):02X}" for _ in range(4))
        for _ in range(3)
    ]
    # Verbinden der Zeilen mit Zeilenumbrüchen
    st.session_state.text = "\n".join(hex_table)    

# Funktion zum Plotten einer piecewise linearen Funktion
def plot_piecewise_function(x_values, y_values):
    fig, ax = plt.subplots(figsize=(6, 2.1))
    ax.plot(x_values, y_values, marker="", linestyle="-", color="b")
    ax.set_title("TLM protocol", fontsize=9)
    ax.set_xlabel("time [us]", fontsize=8)
    ax.set_ylabel("voltage", fontsize=8)
    ax.grid(True)
    st.pyplot(fig)
    
# Sidebar
with st.sidebar:
    st.title("TLM PWL protocol")    
    st.image('static/pwl.jpg', width=240)

st.sidebar.button('Generate', on_click=generate_memory)

exit_app = st.sidebar.button("Exit App")
if exit_app:
    time.sleep(.3); pid = os.getpid(); p = psutil.Process(pid);  p.terminate();

mode = st.sidebar.radio(
    "unlock:",
    ["yes", "no"])
addr = st.sidebar.number_input("register", min_value=0, max_value=255, value=12, step=1)
value = st.sidebar.number_input("value")
##threshold = st.sidebar.slider('threshold', min_value=0.5, max_value=25.0, value=2.0, step=0.1)
##adj = st.sidebar.slider('temp adjust', min_value=-7, max_value=8, value=0, step=1)

txt = '<div class="chat-row">'
#    div += '<img class="chat-icon" src="./app/static/ai_icon1.png" width=40 height=40>'
txt += '<img class="chat-icon" src="bot3.png" width=40 height=40>'
txt += '<div class="chat-bubble ai-bubble">'+'Hello, please make your inputs and generate.\n'+' </div>  </div>'
    
st.markdown(txt, unsafe_allow_html=True)
add_vertical_space(1)
st.text_area('PWL:', value=st.session_state.text, height=170)

# Beispielwerte für die piecewise lineare Funktion
x_values = [0, 100]
y_values = [0, 0]

# Plot der Funktion über der Textbox
plot_piecewise_function(x_values, y_values)


