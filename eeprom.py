import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit.components.v1 as components
from helpers import *
import os, time, random, psutil, datetime, pickle, time

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
    /* Entferne Abstand oben von Hauptcontainer */
    .css-1d391kg {  
        padding-top: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

if 'text' not in st.session_state:
    st.session_state.text = ""

def calc_parity(byte_list):
    parity = 0
    for byte in byte_list:
        while byte:
            parity ^= (byte & 1) # XOR mit LSB
            byte >>= 1
    return parity

def generate_memory():
    memory = []
    # 12 Zeilen mit 4 Hexadezimalzahlen pro Zeile
    print('Werte: ', int(bw), float(threshold), str(mode) ) # threshold*10 in 0.1mT
    bon = int(10 * float(threshold))
    bandwidth = int(bw)
    res = 0
    if mode=='speed/speed':
        if axis=='XY':
            res = res | 12
        elif axis=='ZX':
            res = res | 16
        elif axis=='ZY':
            res = res | 20
    elif mode=='speed/direction':
        if axis=='XY':
            pass
        elif axis=='ZX':
            res = res | 4
        elif axis=='ZY':
            res = res | 8
    if fusi=='disabled':
        res = res | 1
    memory.append(res)
    res = 0
    if poweron=='low':
        res = 128
    # TC = 0ppm/K
    if int(bw)==5:
        res = res | 24
    elif int(bw)==10:
        res = res | 16
    elif int(bw)==20:
        res = res | 8
    memory.append(res)
    res = 0
    # X-TC and Y-TC offset 
    memory.append(0)
#    memory.append(0)
    memory.append(bon)
    memory.append(256 - bon) #  Two's complement
    memory.append(bon)
    memory.append(256 - bon) #  Two's complement
    #  MIC ID === 0
    memory.append(0)
    memory.append(0)
    memory.append(0)
    memory.append(0)
    memory.append(0)

    memory_masked = []

    # iterate over EEPROM #0 - #7
    for mm, bitmask in zip(memory[:-4], [239, 254, 255, 11, 255, 255, 255, 255]):
        memory_masked.append(mm & bitmask)

    # calculate parity
    parity = calc_parity(memory_masked)
    # correct parity in memory
    memory[1] = memory[1] | parity


    my_str = ""
    for byte in memory:
        my_str += str(byte)+' \n'
    mem = bytearray(memory)

    hex_string = mem.hex()
    # Verbinden der Zeilen mit Zeilenumbrüchen
    st.session_state.text = 'EEPROM bytes:\n\n' + my_str + '\nHEX String:\n\n' + hex_string + '\n\n' + 'Parity: ' + str(parity)

# Sidebar
with st.sidebar:
#    st.title("EEPROM")    
    st.markdown('''
    EEPROM Config generator  
    ''', unsafe_allow_html=True)
    st.image('static/ic_icon.png', width=200)

st.sidebar.button('Generate', on_click=generate_memory)

##exit_app = st.sidebar.button("Exit App")
##if exit_app:
##    time.sleep(.3); pid = os.getpid(); p = psutil.Process(pid);  p.terminate();

bw = st.sidebar.radio(
    "bandwidth [kHz]:",
    ["5", "10", "20"])
threshold = st.sidebar.slider('threshold', min_value=0.5, max_value=25.0, value=2.0, step=0.1)
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

st.image('static/bot3.png', width=64)
txt = '<div class="chat-row">'
#    div += '<img class="chat-icon" src="./app/static/ai_icon1.png" width=40 height=40>'
txt += '<div class="chat-bubble ai-bubble">'+'Hello, please make your inputs and generate.\n'+' </div>  </div>'
  
st.markdown(txt, unsafe_allow_html=True)
add_vertical_space(1)
st.text_area('EEPROM contents:', value=st.session_state.text, height=260)



