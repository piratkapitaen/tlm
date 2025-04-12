import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit.components.v1 as components
from helpers import *
import os, time, random, psutil, datetime, pickle, time
import numpy as np
import matplotlib.pyplot as plt

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
st.set_page_config(page_title="EEPROM config", layout="wide")

st.markdown("""
    <style>
    /* Entferne Standard-Padding und Abstand der Sidebar */
    [data-testid="stSidebar"] {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    .main {
        padding-top: 0rem !important;
    }
        header {
            visibility: hidden;
        }    
    /* Entferne Abstand oben von Hauptcontainer */
    .css-1d391kg {  
        padding-top: 0rem;
    }
    .css-znku1x.e16nr0p33 {
      margin-top: -75px;
    }
        /* Sidebar-Inhalt ganz oben platzieren */
        section[data-testid="stSidebar"] > div:first-child {
            padding-top: 0rem;
        }    
    </style>
    """, unsafe_allow_html=True)

if 'text' not in st.session_state:
    st.session_state.text = ""

# Zeitachse & Signale
x = np.linspace(0, 4 * np.pi, 1000)
y_sin = 25.*np.sin(x)
y_cos = 25.*np.cos(x)

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
fig.tight_layout()
st.session_state['fig'] = fig  # Diagramm merken

def calc_parity(byte_list):
    parity = 0
    for byte in byte_list:
        while byte:
            parity ^= (byte & 1) # XOR mit LSB
            byte >>= 1
    return parity

# Hysterese-Funktion
def hysterese(signal, thresh_high, thresh_low):
    output = np.zeros_like(signal)
    state = 0
    for i, val in enumerate(signal):
        if state == 0 and val > thresh_high:
            state = 10
        elif state == 10 and val < thresh_low:
            state = 0
        output[i] = state
    return output

def generate_memory():
    # Hysterese anwenden
    y_sin_hyst = hysterese(y_sin, int(1. * float(threshold)), -1.*int(1. * float(threshold)))
    y_cos_hyst = hysterese(y_cos, int(1. * float(threshold)), -1.*int(1. * float(threshold)))

    memory = []
    # 12 Zeilen mit 4 Hexadezimalzahlen pro Zeile
    print('Werte: ', int(bw), float(threshold), str(mode) ) # threshold*10 in 0.1mT
    bon = int(10 * float(threshold))
    bandwidth = int(bw)
    res = 0
    if axis=='XY':
        pass
    elif axis=='ZX':
        res = res | 1
    elif axis=='ZY':
        res = res | 2
    memory.append(res);     res = 0;

    if mode=='speed/speed':
        res = res | 8
    else:
        res = 0
    # TC = 0ppm/K
    if int(bw)==5:
        res = res | 6
    elif int(bw)==10:
        res = res | 4
    elif int(bw)==20:
        res = res | 2
    elif int(bw)==40:
        res = res | 0
    memory.append(res);     res = 0;
    memory.append(0);       res = 0;

    if fusi!='disabled':
        res = res | 2
    if poweron!='low':
        res = res | 1
    memory.append(res);     res = 0;
    
    memory.append(256 - bon) #  Two's complement
    memory.append(bon)
    memory.append(256 - bon) #  Two's complement
    memory.append(bon)
    if UID=='0x00000000':
        memory.append(0)
        memory.append(0)
        memory.append(0)
        memory.append(0)
    else:
        memory.append(85)
        memory.append(170)
        memory.append(85)
        memory.append(170)

    memory_masked = []

    # iterate over EEPROM #0 - #7
    for mm, bitmask in zip(memory[:-4], [239, 254, 255, 11, 255, 255, 255, 255]):
        memory_masked.append(mm & bitmask)

    # calculate parity
    parity = calc_parity(memory_masked)
    # correct parity in memory
    memory[1] = memory[1] | parity


# + '     0b'+format(byte, '08b')
    my_str = ""
    arr = '['
    for byte in memory:
        my_str += str(byte)+ '     0b'+format(byte, '08b')+ ' \n'
        arr += str(byte) + ' '
    mem = bytearray(memory)
    arr += ']\n'

    hex_string = mem.hex()
    # Verbinden der Zeilen mit Zeilenumbrüchen
    st.session_state.text = 'EEPROM bytes:   '+arr+ 'HEX String:    ' + hex_string + '\n' + 'Parity: ' + str(parity)+'\n'+my_str

    # Channel A and B plots
    ax1.plot(x, y_sin, label='Channel A', alpha=0.4)
    ax1.plot(x, y_sin_hyst, label='OUT1', color='red')
    ax1.axhline(int(1. * float(threshold)), color='green', linestyle='--', label='BON')
    ax1.axhline(-1.*int(1. * float(threshold)), color='orange', linestyle='--', label='BOFF')
    ax1.set_ylabel('Channel A')
#    ax1.set_title('Channel A')
    ax1.legend()
    ax1.grid(True)
    ax2.plot(x, y_cos, label='Channel B', alpha=0.4)
    ax2.plot(x, y_cos_hyst, label='OUT2', color='blue')
    ax2.axhline(int(1. * float(threshold)), color='green', linestyle='--', label='BON')
    ax2.axhline(-1.*int(1. * float(threshold)), color='orange', linestyle='--', label='BOFF')
    ax2.set_ylabel('Channel B')
    ax2.set_xlabel('x')
#    ax2.set_title('Channel B')
    ax2.legend()
    ax2.grid(True)

    if 'fig' in st.session_state:
        st.pyplot(st.session_state['fig'])

# Sidebar
with st.sidebar:
#    st.title("EEPROM")    
    st.markdown('''
    EEPROM Config generator  
    ''', unsafe_allow_html=True)
    st.image('static/ic_icon.png', width=100)

st.sidebar.button('Generate', on_click=generate_memory)

##exit_app = st.sidebar.button("Exit App")
##if exit_app:
##    time.sleep(.3); pid = os.getpid(); p = psutil.Process(pid);  p.terminate();

bw = st.sidebar.radio(
    "bandwidth [kHz]:",
    ["5", "10", "20", "40"])
threshold = st.sidebar.slider('threshold', min_value=0.5, max_value=12.5, value=2.0, step=0.1)
#adj = st.sidebar.slider('temp adjust', min_value=-7, max_value=8, value=0, step=1)
mode = st.sidebar.radio(
    "mode:",
    ["speed/speed", "speed/direction"])
axis = st.sidebar.radio(
    "axis:",
    ["XY", "ZX", "ZY"])
fusi = st.sidebar.radio(
    "fusi:",
    ["enabled", "disabled"])
poweron = st.sidebar.radio(
    "power on state:",
    ["high-Z", "low"])
UID = st.sidebar.radio(
    "UID:",
    ["0x00000000", "ckeckerboard: 0x55AA55AA"])

st.image('static/evm.png', width=64)
txt = '<div class="chat-row">'
#    div += '<img class="chat-icon" src="./app/static/ai_icon1.png" width=40 height=40>'
txt += '<div class="chat-bubble ai-bubble">'+'Hello, please make your inputs and generate.\n'+' </div>  </div>'
  
#st.markdown(txt, unsafe_allow_html=True)
add_vertical_space(1)
st.text_area('Hello, please make your inputs and generate.  EEPROM contents:', value=st.session_state.text, height=370)

##fig.tight_layout()
##st.pyplot(fig)

