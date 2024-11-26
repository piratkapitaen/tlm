import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
from helpers import *
import os, time, random, datetime, re, gzip, pickle, time, psutil

TD    = 1
VLO   = 0
VMID  = 2.25
VHI   = 4.5
EPS   = 0.001
SCAL  = 2.
DELAY = 20
MODE  = 1  # 0: old 1bit mode, 1: TLM mode
UNLOCK = ['S', 0, 0, 0, 'W', 24, 71, 4, 'W', 25, 230, 4]

def func_delay():
    return [TD, VMID]

def pulse(td, v1, v2):
    if MODE==1:
        l = [(td*.25), VMID, EPS, v1, (td*.25)-EPS-EPS, v1, EPS, VMID,\
             (td*.25)-EPS, VMID, EPS, v2, (td*.25)-EPS, v2, EPS, VMID]
    else:
        l = [(td*.333), VMID, EPS, v1, (td*.333)-EPS, v1,\
             EPS, VMID, (td*.333), VMID]        
    return l

def flatten_list(l, unit):
    result = []; raw = []; ttime = 0.; result.append(str(ttime)+unit);
    result.append(str(VMID)); result.append('\n');
    raw.append(ttime); raw.append(VMID)
    result.append(str(DELAY)+unit);result.append(str(VMID)); result.append('\n');
    raw.append(DELAY); raw.append(VMID)
    ttime += DELAY
    for i in range(0, len(l), 2):
        ttime += SCAL*l[i]; result.append(str(round(ttime, 3))+unit);
        result.append(str(l[i+1])); result.append('\n');
        raw.append(round(ttime, 3)); raw.append(l[i+1])
    return ' '.join(map(str, result)), raw

def split_list(l):
    pass

def combine(l):
    new_list = []
    for item in l:
        if item==0:
            new_list += pulse(TD, VLO, VHI)
        elif item==1:
            new_list += pulse(TD, VHI, VLO)
        else:
            new_list += func_delay()
    return new_list

def cmd2bits6adr8dat(lst):
    pass

def sync():
    return [0]*18

def adr2bin(adr):
    adr = 127 - adr; a = bin(adr)[2:]; a = '0'*(7-len(a)) + a;
    return [int(digit) for digit in a]

def data2bin(data):
    data = 255 - data; a = bin(data)[2:]; a = '0'*(8-len(a)) + a;
    return [int(digit) for digit in a]

def cmd7adr8dat(lst):
    new_list = []
    for i in range(0, len(lst), 4):
        rw    = lst[i]; adr   = lst[i+1]; data  = lst[i+2]; pause = lst[i+3];
        startbit = [0]
        if rw == 'W':
            l = startbit + adr2bin(adr) + [0] + data2bin(data) + [-1]*pause
        elif rw == 'A':
            l = [1]*18 + [-1]*pause
        elif rw == 'S':
            l = [-2]
        else:
            l = startbit + adr2bin(adr) + [1] + data2bin(data) + [-1]*pause
        for item in l:
            if item==0:
                new_list += pulse(TD, VLO, VHI)
            elif item==1:
                new_list += pulse(TD, VHI, VLO)
            elif item==-2:
                new_list += pulse(TD, VLO, VLO)
            else:
                new_list += func_delay()
    return new_list
    
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
    # calculate and redraw diagram
    if mode == "yes":  
        a = cmd7adr8dat(UNLOCK + ['W', 65, 21, 4]) # unlock pattern + Adr 8: 85
        print('UNLOCK')
    else:
        a = cmd7adr8dat(['W', 65, 21, 4]) # no unlock 
        print('NO UNLOCK')
    b, raw = flatten_list(a, 'u')
    time_values = [raw[i] for i in range(len(raw)) if i % 2 == 0]
    voltage_values = [raw[i] for i in range(len(raw)) if i % 2 != 0]
    plot_piecewise_function(time_values, voltage_values)

    ##    print('Hallo')
##    st.session_state.text = 'Abcdef'
    # 12 Zeilen mit 4 Hexadezimalzahlen pro Zeile
    hex_table = [
        "\t".join(f"{random.randint(0, 255):02X}" for _ in range(4))
        for _ in range(3)
    ]
    # Verbinden der Zeilen mit Zeilenumbrüchen
    st.session_state.text = "\n".join(hex_table)

plot_placeholder = st.empty()

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

#exit_app = st.sidebar.button("Exit App")
#if exit_app:
#    time.sleep(.3); pid = os.getpid(); p = psutil.Process(pid);  p.terminate();

mode = st.sidebar.radio(
    "unlock:",
    ["yes", "no"])
addr = st.sidebar.number_input("register", min_value=0, max_value=255, value=12, step=1)
value = st.sidebar.number_input("value", min_value=0, max_value=255, value=0, step=1)
##threshold = st.sidebar.slider('threshold', min_value=0.5, max_value=25.0, value=2.0, step=0.1)
##adj = st.sidebar.slider('temp adjust', min_value=-7, max_value=8, value=0, step=1)

st.image('static/bot3.png', width=64)
txt = '<div class="chat-row">'
#    div += '<img class="chat-icon" src="./app/static/ai_icon1.png" width=40 height=40>'
txt += '<div class="chat-bubble ai-bubble">'+'Hello, please make your inputs and generate.\n'+' </div>  </div>'
  
st.markdown(txt, unsafe_allow_html=True)
add_vertical_space(1)
st.text_area('PWL:', value=st.session_state.text, height=170)

# Beispielwerte für die piecewise lineare Funktion
x_values = [0, 100]
y_values = [0, 0]

if "initialized" not in st.session_state:
    # Plot der Funktion über der Textbox
    plot_piecewise_function(x_values, y_values)
    st.session_state.initialized = False


