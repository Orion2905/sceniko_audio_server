# ---------------------------------------------------------------------------------------
# Versione 1.2
# Aggiunta attesa di 60 sec iniziali per attesa connessione rete
# Da sistemare loop connessione MQTT
#
# Versione 1.1
# Aggiunta funzione LOOP
# Da sistemare loop connessione MQTT
#
# Versione 1.0
# Da sistemare loop connessione MQTT
# ---------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------
# DEVICE 0
# ---------------------------------------------------------------------------------------

DEVICE = 0

import time
# time.sleep(60)

import paho.mqtt.client as mqtt
import sys
import pygame.mixer
import pygame
import pygame._sdl2 as sdl2
from pygame.locals import *
import os, subprocess

import app
import tkinter as tk


global_volume = 60

# ---------------------------------------------------------------------------------------
# Crea un elenco di audio device disponibili
# ---------------------------------------------------------------------------------------

pygame.init()
is_capture = 0  # zero to request playback devices, non-zero to request recording devices
num = sdl2.get_num_audio_devices(is_capture)
devices = [str(sdl2.get_audio_device_name(i, is_capture), encoding="utf-8") for i in range(num)]
print("\n".join(devices))
pygame.quit()

# ---------------------------------------------------------------------------------------
# Inizializza il mixer e il numero totale di canali
# ---------------------------------------------------------------------------------------

num_channels = 7  # numero totale 6 canali
pygame.mixer.pre_init(
    devicename="Speakers (Realtek(R) Audio)"
)
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1000)
pygame.mixer.set_num_channels(num_channels)
total_channels = pygame.mixer.get_num_channels()
# print("Numero totale di canali: " + str(total_channels))

# ---------------------------------------------------------------------------------------
# Crea un array per la gestione dei file riprodotti nei vari canali
# ---------------------------------------------------------------------------------------

file_playing = ["" for i in range(num_channels)]
volume_playing = ["" for i in range(num_channels)]  # lista per i volumi


# Funzione aggiunta: controlla che la connessione avvenga corrattamente, True se e' connesso False se non lo e'
def check_connection(client):
    try:
        client.username_pw_set(username="ScenikoMQTT", password="ScenikoMQTT")
        client.connect('127.0.0.1', port=1883, keepalive=60)
        return True
    except ConnectionRefusedError as Error:
        print(Error)
        return False

# ---------------------------------------------------------------------------------------
# Una volta connesso al server MQTT effettua i vari subscribe
# ---------------------------------------------------------------------------------------
def on_connect(client, userdata, flags, rc) :
    # print("Connection returned result: " + str(rc))
    if not rc:
        # print('Connected to MQTT broker')

        client.subscribe("VOLUME")
        client.subscribe("AUDIO" + str(DEVICE) + "/PLAY")
        client.subscribe("AUDIO" + str(DEVICE) + "/LOOP")
        client.subscribe("AUDIO" + str(DEVICE) + "/STOP")
        client.subscribe("AUDIO/PLAY")
        client.subscribe("AUDIO/LOOP")
        client.subscribe("AUDIO/STOP")

    else:
        print("no connack received!")
        raise ConnectionError("Failed to receive Ack!")


# ---------------------------------------------------------------------------------------
# Verifica i canali liberi ed aggiorna la tabella
# ---------------------------------------------------------------------------------------


def play_ended():    
    
     while(1):
        time.sleep(1)
        for n in range(num_channels-1):
            if pygame.mixer.Channel(n).get_busy():
                print('Canale occupato: {}'.format(n))
            else :
                print('Canale libero: {}'.format(n))
           
        root.after(100, play_ended)


# ---------------------------------------------------------------------------------------
# Trova un canale libero, esegue il file, calcola il volume, aggiorna l'array
# ---------------------------------------------------------------------------------------

def play(channel, file, volume, loop):
    
    # print('Canale {}'.format(channel))
    # print('Nome del file {}'.format(file))
    # print('Volume {}'.format(volume))
    # Dizionario che raccoglie le informaioni dei canali
    global channels_info
    channels_info = {
        "channels": [],
        "channels_volume": ['','','','','','']  # Se dovessero essere aggiunti nuovi canali aggiungere uno spazio alla lista
    }

    if ".wav" in file:
        if os.path.isfile(str(file)):
            # print("File exists")
            canale_libero = 0
            notFound = True
            while notFound:
                if pygame.mixer.Channel(canale_libero).get_busy():
                    canale_libero = (canale_libero + 1)
                else :
                    notFound = False

            if canale_libero > 5:
                print('Nessun canale libero')
            else:
                # print('Canale libero: {}'.format(canale_libero))
                # print('VOLUME GLOBALE {}'.format(global_volume))
                pygame.mixer.Channel(canale_libero).set_volume(volume * global_volume)
                pygame.mixer.Channel(canale_libero).play(
                    pygame.mixer.Sound(str(file)), loops=loop)
                # print('playing now!')
                file_playing[canale_libero] = channel + "/" + file
                volume_playing[canale_libero] = volume  # nuova lista che si popola con i volumi dei canali ed in seguito si aggiunge al dizionario
                # for i in range(num_channels):
                #       print("ELENCO FILE {}".format(file_playing[i]))
                # print(file_playing)
        else:
            print("Playback file not found!")

        channels_info['channels'] = file_playing  # qui viene aggiunto file_playing che contiene le altre informazioni
        channels_info['channels_volume'] = volume_playing  # qui viene aggiunto volume_playing che contiene le altre informazioni
        table_update(channels_info)
        return channels_info  # La funzione play restituisce questo dizionario che e' popolato dai dati ottenuti dai canali inseriti


def reset_channels_info():
    channels_info = {
        "channels": [],
        "channels_volume": ['', '', '', '', '', '']
        # Se dovessero essere aggiunti nuovi canali aggiungere uno spazio alla lista
    }

# ---------------------------------------------------------------------------------------
# Elabora i messaggi ricevuti dal server MQTT
# ---------------------------------------------------------------------------------------
def on_message(client, userdata, msg) :
    print("Data {} is received on topic {}".format(str(msg.payload.decode("utf-8")), str(msg.topic)))

    topic_content = msg.topic.split("/")
    topic_length = len(topic_content)
    # print('Topic suddiviso in: {}'.format(str(topic_content)))
    # print('Quantità di dati nel topic: {}'.format(topic_length))

    if topic_content[0] == "VOLUME":

        global global_volume
        global_volume = msg.payload.decode("utf-8").split("%")
        global_volume = int(global_volume[0].strip()) / 100
        set_volume(global_volume) # imposto il volume globale
        print('Contollo volume globale {}'.format(global_volume))


    elif (topic_content[1] == "PLAY") or (topic_content[1] == "LOOP"):
        # print('Play audio')
        payload_content = msg.payload.decode("utf-8").split("/")
        payload_length = len(payload_content)
        # print('Payload suddiviso in: {}'.format(str(payload_content)))
        # print('Quantità di dati nel payload: {}'.format(payload_length))

        if payload_length == 3 :
            channel_volume = payload_content[2].split("%")
            channel_volume = int(channel_volume[0].strip()) / 100
            # print('Volume rilevato: {}'.format(str(channel_volume)))
        elif payload_length == 2 :
            # print('Nessun volume assegnato')
            channel_volume = 1

        if (topic_content[1] == "PLAY") :
            play(payload_content[0], payload_content[1], channel_volume, 0)
            # table_generator(channels_info)  # aggiorna tabella
        elif (topic_content[1] == "LOOP") :
            play(payload_content[0], payload_content[1], channel_volume, -1)
            # table_generator(channels_info)  # aggiorna tabella

    elif topic_content[1] == "STOP":

        payload_content = msg.payload.decode("utf-8").split("/")
        payload_length = len(payload_content)
        # print('Payload suddiviso in: {}'.format(str(payload_content)))
        # print('Quantità di dati nel payload: {}'.format(payload_length))
        if payload_content[0] == "ALL" :
            # print('STOP tutto')
            pygame.mixer.stop()
        else :
            # print('STOP singolo audio')
            posizione_trovata = "False"
            posizione = 0

            while posizione_trovata == "False":
                if file_playing[posizione] == str(msg.payload.decode("utf-8")):
                    posizione_trovata = "True"
                else :
                    posizione += 1
                if posizione > 6 :
                    posizione_trovata = "NonTrovato"

            if posizione_trovata == "NonTrovato":
                print("Nessuna corrispondenza")
            else :
                # print("Posizione trovata {}".format(posizione))
                pygame.mixer.Channel(posizione).stop()
                file_playing[posizione] = ""


# ---------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------
def main():
    client = mqtt.Client(
        client_id="AUDIO" + str(DEVICE), clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp"
    )
    client.on_connect = on_connect
    client.on_message = on_message

    time.sleep(1)

    client.loop_start()

    # Avvio della GUI

   
    a = app
    if __name__ == "__main__":
        root = tk.Tk()
        main = app.MainWindow(
            root=root,
            device=DEVICE,
            connection=check_connection(client),
            global_volume=global_volume,
            client=client,
        )
        global set_volume, table_generator, table_update  # creo la variabile globale set_volume
        # table_generator = main.table_generator_
        table_update = main.update_table
        set_volume = main.set_volume  # Importo il metodo per cambiare il volume. Da usare nelle funzioni dove serve
        
        play('test','test.wav',100,1)

        root.mainloop()

    # while True:
    #   time.sleep(1)


# Avvio del programma
if __name__ == "__main__":
    app.output_layout("Programma in esecuzione...")
    main()

