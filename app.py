
import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import paho.mqtt.client as paho
import json

# 🌸 Configuración del broker MQTT
broker = "broker.mqttdashboard.com"
port = 1883

client1 = paho.Client("ISA-VOICE-APP")

def on_publish(client, userdata, result):
    print("✅ Comando publicado correctamente")
    pass

def on_message(client, userdata, message):
    time.sleep(1)
    msg = str(message.payload.decode("utf-8"))
    st.write(f"📩 Mensaje recibido: {msg}")

client1.on_publish = on_publish
client1.on_message = on_message

# 💖 Interfaz Streamlit
st.set_page_config(page_title="Control por Voz 💖", page_icon="🎙️", layout="centered")

st.title("💬 INTERFACES MULTIMODALES")
st.subheader("🎤 CONTROL POR VOZ MQTT")

image = Image.open("voice_ctrl.jpg")
st.image(image, width=220, caption="Habla para controlar tu ESP32")

st.write("Haz clic y da una instrucción (por ejemplo: *enciende las luces*, *abre la puerta*).")

# 🎙️ Botón de escucha
stt_button = Button(label="🎙️ Iniciar Escucha", width=250)
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# 🧠 Publicar resultado
if result and "GET_TEXT" in result:
    texto = result.get("GET_TEXT").strip()
    st.write(f"🗣️ Dijo: **{texto}**")

    client1.connect(broker, port)
    message = json.dumps({"Act1": texto})
    client1.publish("voice_ctrl", message)  # ✅ TOPIC CORREGIDO

    st.success("✅ Instrucción enviada al ESP32")
