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
import pygame.mixer
import pygame
import pygame._sdl2 as sdl2
from pygame.locals import *
import os, sys, subprocess  # Librerie per gestire le operazioni di sistema

import app
import datetime  # libreria per ottenere data ed ora corrente
import tkinter as tk  # libreria per l'interfaccia grafica
from tkinter import *
from tkinter import ttk


global_volume = 60



###################################################################################################################



# Utilizza questa funzione se vuoi mandare in output dei messaggi con questo layout
def output_layout(message):
    string = f"[{datetime.datetime.now()}] >>> {message}"
    print(string)


# Classe per creare dei frame con la scrollbar, in questo caso è usata nella tabella così che se mai i canali dovessero
# aumentare bisognerà fare interventi grafici
class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, relief="solid", width=370, height=150)
        canvas.config(background='#222f3e')
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#222f3e", relief="solid", borderwidth=0)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="x")
        scrollbar.pack(side="right", fill="y")




# Classe principale che genera la finestra
class MainWindow:
    def __init__(self, root, device, connection, global_volume, client):

        # output_layout(channels)  # mostra i canali e i loro attributi

        # Variabili globali
        self.BACKGROUND_COLOR = "#222f3e"  # colore dello sfondo [1]
        self.ROOT_TITLE = "Sceniko Audio-server"  # titolo della finestra [2]
        self.ROOT_SIZE = "500x250"  # dimensione della finestra [3]
        self.VERSION = "1.0"  # versione dell'app (cambia questo valore o lascalo cosi')

        self.connection = connection  # rende accessibile a tutto il programma lo stato della connessione (True o False)

        # caricamento delle immagini
        self.connected = PhotoImage(file=r"img/on.png").subsample(3, 3)  # immagine connessione verde
        self.not_connected = PhotoImage(file=r"img/off.png").subsample(3, 3)  # immagine non connesso
        self.settings = PhotoImage(file=r"img/settings.png").subsample(13, 13)  # immagine ingranaggio
        self.update = PhotoImage(file=r"img/update.png").subsample(13, 13)  # Immagine update

        self.root = root # rende la root disponibile per tutto il programma

        # Ottenere il device
        self.device = device  # device disponibile per tutto il programma

        # non sapevo se il device esisteva sempre cosi' ho messo questo if che nel caso il device e' diverso o minore
        # di 0 al posto del nome del device inserisce il titolo
        if self.device >= 0:
            self.title_text = "AUDIO"+str(self.device)
        else:
            self.title_text = self.ROOT_TITLE

        # impostazioni della finestra principale (vedi numeri variabili globali)
        root.title(self.ROOT_TITLE)  # [1]
        root.geometry(self.ROOT_SIZE)  # [2]
        root.config(background=self.BACKGROUND_COLOR)  # [3]
        root.resizable(False, False)  # rende le dimensioni della finestra non modificabili dall'utente (imposta True, True per il contrario)
        root.iconbitmap("img/icon.ico")  # icona della finestra

        root.update()

        # Title: qui viene mostrato il titolo (AUDIO0 per esempio)
        title = tk.Label(
            root,
            text=self.title_text,
            font=("Arial", 8, "bold"),
            pady=2,
            relief="groove",
            border=5, padx=20,
            bg="#576574"
        )
        title.pack(pady=5)

        root.update()

        # Frames: generano delle sezioni indipendenti dalla geometria della root principale
        self.main_frame = tk.Frame(root, background=self.BACKGROUND_COLOR)
        self.channels_frame = ScrollableFrame(self.main_frame)
        self.button_frame = tk.Frame(root, background=self.BACKGROUND_COLOR)

        # self.table_generator(channels)


        # Creazione della tabella
        ab = list()
        columns_list = ['CANALE', 'GRUPPO', 'FILE', 'VOLUME', 'AZIONE']  # lista delle colonne della tabella
        # Loop per le righe
        for j in range(len(columns_list)):
            self.column = tk.Label(  # riga con i nomi delle colonne
                self.channels_frame.scrollable_frame,
                text=columns_list[j],
                width=10,
                bg=self.BACKGROUND_COLOR,
                font=("Arial", 8, "bold"),
                fg="#c8d6e5",
                relief="solid"
            ).grid(row=0, column=j)

        ##########################################################################################
        ##    Riga 1
        ##########################################################################################

        # 1 colonna dei canali
        self.channel_0 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='1',
            height=1,
            relief="solid",
            width=5
        )
        self.channel_0.grid(row=1, sticky="WE")

        # 1 colonna dei gruppo
        self.group_0 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.group_0.grid(row=1, column=1, sticky="WE")

        # 1 colonna dove viene mostrato il nome del file
        self.file_0 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.file_0.grid(row=1, column=2, sticky="WE")

        # 1 colonna del volume
        self.volume_0 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid"
        )
        self.volume_0.grid(row=1, column=3, sticky="WE")

        # 1 colonna per i pulsanti di stop. Lambda mi permette di chaiamre la funzione e passarle i singoli
        # oggetti (sarebbero le colonne informazioni presenti nelle righe)
        self.button = tk.Button(
            self.channels_frame.scrollable_frame,
            text="STOP",
            height=0,
            bd=2, bg="#e74c3c",
            width=5,
            font=("Arial", 7, "bold"),
            command=lambda : self.stop0(),
        )
        self.button.grid(row=1, column=4, pady=0.5, padx=1, ipadx=0)

        ##########################################################################################
        ##    Riga 2
        ##########################################################################################

        # 2 colonna dei canali
        self.channel_1 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='2',
            height=1,
            relief="solid",
            width=5
        )
        self.channel_1.grid(row=2, sticky="WE")

        # 2 colonna dei gruppo
        self.group_1 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.group_1.grid(row=2, column=1, sticky="WE")

        # 2 colonna dove viene mostrato il nome del file
        self.file_1 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.file_1.grid(row=2, column=2, sticky="WE")

        # 2 colonna del volume
        self.volume_1 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid"
        )
        self.volume_1.grid(row=2, column=3, sticky="WE")

        # 2 colonna per i pulsanti di stop. Lambda mi permette di chaiamre la funzione e passarle i singoli
        # oggetti (sarebbero le colonne informazioni presenti nelle righe)
        self.button_1 = tk.Button(
            self.channels_frame.scrollable_frame,
            text="STOP",
            height=0,
            bd=2, bg="#e74c3c",
            width=5,
            font=("Arial", 7, "bold"),
            command=lambda : self.stop1(),
        )
        self.button_1.grid(row=2, column=4, pady=0.5, padx=1, ipadx=0)


        ##########################################################################################
        ##    Riga 3
        ##########################################################################################

        # 3 colonna dei canali
        self.channel_2 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='3',
            height=1,
            relief="solid",
            width=5
        )
        self.channel_2.grid(row=3, sticky="WE")

        # 3 colonna dei gruppo
        self.group_2 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.group_2.grid(row=3, column=1, sticky="WE")

        # 3 colonna dove viene mostrato il nome del file
        self.file_2 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.file_2.grid(row=3, column=2, sticky="WE")

        # 3 colonna del volume
        self.volume_2 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid"
        )
        self.volume_2.grid(row=3, column=3, sticky="WE")

        # 3 colonna per i pulsanti di stop. Lambda mi permette di chaiamre la funzione e passarle i singoli
        # oggetti (sarebbero le colonne informazioni presenti nelle righe)
        self.button_2 = tk.Button(
            self.channels_frame.scrollable_frame,
            text="STOP",
            height=0,
            bd=2, bg="#e74c3c",
            width=5,
            font=("Arial", 7, "bold"),
            command=lambda : self.stop2(),
        )
        self.button_2.grid(row=3, column=4, pady=0.5, padx=1, ipadx=0)

        ##########################################################################################
        ##    Riga 4
        ##########################################################################################

        # 4 colonna dei canali
        self.channel_3 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='4',
            height=1,
            relief="solid",
            width=5
        )
        self.channel_3.grid(row=4, sticky="WE")

        # 4 colonna dei gruppo
        self.group_3 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.group_3.grid(row=4, column=1, sticky="WE")

        # 4 colonna dove viene mostrato il nome del file
        self.file_3 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.file_3.grid(row=4, column=2, sticky="WE")

        # 4 colonna del volume
        self.volume_3 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid"
        )
        self.volume_3.grid(row=4, column=3, sticky="WE")

        # 4 colonna per i pulsanti di stop. Lambda mi permette di chaiamre la funzione e passarle i singoli
        # oggetti (sarebbero le colonne informazioni presenti nelle righe)
        self.button_3 = tk.Button(
            self.channels_frame.scrollable_frame,
            text="STOP",
            height=0,
            bd=2, bg="#e74c3c",
            width=5,
            font=("Arial", 7, "bold"),
            command=lambda : self.stop3(),
        )
        self.button_3.grid(row=4, column=4, pady=0.5, padx=1, ipadx=0)


        ##########################################################################################
        ##    Riga 5
        ##########################################################################################

        # 5 colonna dei canali
        self.channel_4 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='5',
            height=1,
            relief="solid",
            width=5
        )
        self.channel_4.grid(row=5, sticky="WE")

        # 5 colonna dei gruppo
        self.group_4 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.group_4.grid(row=5, column=1, sticky="WE")

        # 5 colonna dove viene mostrato il nome del file
        self.file_4 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.file_4.grid(row=5, column=2, sticky="WE")

        # 5 colonna del volume
        self.volume_4 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid"
        )
        self.volume_4.grid(row=5, column=3, sticky="WE")

        # 5 colonna per i pulsanti di stop. Lambda mi permette di chaiamre la funzione e passarle i singoli
        # oggetti (sarebbero le colonne informazioni presenti nelle righe)
        self.button_4 = tk.Button(
            self.channels_frame.scrollable_frame,
            text="STOP",
            height=0,
            bd=2, bg="#e74c3c",
            width=5,
            font=("Arial", 7, "bold"),
            command=lambda : self.stop4(),
        )
        self.button_4.grid(row=5, column=4, pady=0.5, padx=1, ipadx=0)


        ##########################################################################################
        ##    Riga 6
        ##########################################################################################

        # 6 colonna dei canali
        self.channel_5 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='6',
            height=1,
            relief="solid",
            width=5
        )
        self.channel_5.grid(row=6, sticky="WE")

        # 6 colonna dei gruppo
        self.group_5 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.group_5.grid(row=6, column=1, sticky="WE")

        # 6 colonna dove viene mostrato il nome del file
        self.file_5 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid",
            width=10
        )
        self.file_5.grid(row=6, column=2, sticky="WE")

        # 6 colonna del volume
        self.volume_5 = tk.Label(
            self.channels_frame.scrollable_frame,
            text='',
            height=1,
            relief="solid"
        )
        self.volume_5.grid(row=6, column=3, sticky="WE")
        # Motra la tabella (fine)

        # 6 colonna per i pulsanti di stop. Lambda mi permette di chaiamre la funzione e passarle i singoli
        # oggetti (sarebbero le colonne informazioni presenti nelle righe)
        self.button_5 = tk.Button(
            self.channels_frame.scrollable_frame,
            text="STOP",
            height=0,
            bd=2, bg="#e74c3c",
            width=5,
            font=("Arial", 7, "bold"),
            command=lambda : self.stop5(),
        )
        self.button_5.grid(row=6, column=4, pady=0.5, padx=1, ipadx=0)

        ##########################################################################################
        ##    Slider volume
        ##########################################################################################

        # Slider del volume globale: riporta il valora della variabile volume_globale presente in device0.py
        self.volume_chooser = tk.Scale(
            self.main_frame,
            to=0,
            from_=100,
            orient=VERTICAL,
            relief="groove",
            troughcolor="#5f27cd",
            bd=2,
            font=("Arial", 8, "bold"),
            highlightcolor="#00d2d3",
            activebackground="#f368e0",
            bg="#8395a7",
            resolution=0.5,
            width=15,
            state=DISABLED
        )

        self.channels_frame.grid(row=0, column=0, padx=10)  # geometria del frame per la tabella
        self.volume_chooser.grid(row=0, column=1, padx=10, ipady=18, pady=0, sticky="N")   # geometria per lo slider del volume

        # semplice Label che mostra la scritta "Volume generale"
        self.volume_label = tk.Label(
            self.main_frame,
            text="Volume generale",
            bd=0,
            bg=self.BACKGROUND_COLOR,
            fg="#c8d6e5"
        ).grid(row=1, column=1, sticky="N", padx=0)

        # mostra lo stato della connessione
        self.connection_status = tk.Label(
            self.button_frame,
            border=0,
            bg=self.BACKGROUND_COLOR,
            compound=RIGHT,
            fg="#c8d6e5"
        )
        self.connection_status.grid(row=0, column=0, padx=20)

        self.check_connection(connection)  # chaiamta al metodo per verificare la connessione. Nel caso lo stato modifichi premere il tasto RESET

        # Bottone per resettare il programma
        self.reset_button = tk.Button(
            self.button_frame,
            text="RESET",
            height=1,
            bd=2,
            bg="#f39c12",
            width=5,
            font=("Arial", 8, "bold"),
            command=self.reset
        )
        self.reset_button.grid(row=0, column=1, padx=10)

        # bottone per disconnettere il programma
        self.disconnect_button = tk.Button(
            self.button_frame,
            text="DISCONNETTI",
            height=1,
            bd=2,
            bg="#e74c3c",
            width=10,
            font=("Arial", 8, "bold"),
            command=lambda: self.disconnect(client),
        )
        self.disconnect_button.grid(row=0, column=2)

        # Bottone per le impostazioni (solo grafico, funzioni e metodi da implementare)
        self.settings_button = tk.Button(
            self.button_frame,
            image=self.settings,
            width=50,
            bd=2,
            bg=self.BACKGROUND_COLOR,
            fg="#c8d6e5",
            border=2
        )
        self.settings_button.grid(row=0, column=3, padx=50)

        # Geometria per i frame
        self.main_frame.pack(fill=BOTH, expand=True)
        self.button_frame.pack(fill=BOTH, expand=True)
        
        # Footer della finestra
        self.footer = tk.Label(
            root,
            text=self.ROOT_TITLE + " " + self.VERSION,
            relief="solid",
            font=("Arial", 6, "bold")
        ).pack(side=BOTTOM, fill=X)

        self.set_volume(global_volume)  # Imposta il volume globale allo slider

        # self.menu_bar = MenuBar(self)  # leva il commento se vuoi visualizzare la menu bar

    # metodo per aggiornare la finestra
    def update_root(self):
        output_layout("GUI aggiornata")
        self.root.update()
        self.button_frame.update()
        self.main_frame.update()

  
    ##########################################################################################
    ##    Funzioni stop audio
    ##########################################################################################

    
    
    def stop0(self):
        self.group_0['text'] = ''
        self.file_0['text'] = ''
        self.volume_0['text'] = ''
        pygame.mixer.Channel(0).stop()

    def stop1(self):
        self.group_1['text'] = ''
        self.file_1['text'] = ''
        self.volume_1['text'] = ''
        pygame.mixer.Channel(1).stop()

    def stop2(self):
        self.group_2['text'] = ''
        self.file_2['text'] = ''
        self.volume_2['text'] = ''
        pygame.mixer.Channel(2).stop()

    def stop3(self):
        self.group_3['text'] = ''
        self.file_3['text'] = ''
        self.volume_3['text'] = ''
        pygame.mixer.Channel(3).stop()

    def stop4(self):
        self.group_4['text'] = ''
        self.file_4['text'] = ''
        self.volume_4['text'] = ''
        pygame.mixer.Channel(4).stop()

    def stop5(self):
        self.group_5['text'] = ''
        self.file_5['text'] = ''
        self.volume_5['text'] = ''
        pygame.mixer.Channel(5).stop()












    # Funzione per riavviare il programma
    def reset(self):
        output_layout("Riavviando il programma...")
        os.execv(sys.executable, ['python'] + sys.argv)

    # Inserire qui le istruzioni per disconnettere il client (cliet viene importato da device0.py)
    def disconnect(self, client):
        output_layout(f"Client= {client}")
        output_layout("Disconnessione...")
        client.disconnect()
        self.update_root()

        # se si vuole far anche cambiare lo switch e la scritta leva i commenti dalle linee che seguono
        # o commentali se vuoi che cio' non accada
        self.connection_status['image'] = self.not_connected
        self.connection_status['text'] = "non connesso"

        self.update_root()

    # Funzione per impostare il volume generale (è preso in input come parametro e non è modificabile tramite la GUI)
    # Il volume generale rappresenta la variabile volume_generale presente nello script
    # device0.py: è passato come parametro.
    def set_volume(self, volume):
        output_layout(f"Volume globale impostato a {volume}")
        self.volume_chooser['state'] = ACTIVE
        self.volume_chooser.set(int(volume))
        self.volume_chooser['state'] = DISABLED
        self.update_root()

    # verifica se la connessione e' True o False, di conseguena modifica lo switch e la scritta connesso o non
    def check_connection(self, connection):
        output_layout("Verifica della connessione...")
        if connection:
            self.connection_status['image'] = self.connected
            self.connection_status['text'] = "connesso"
            output_layout("Connesso")
        else:
            self.connection_status['image'] = self.not_connected
            self.connection_status['text'] = "non connesso"
            output_layout("Non connesso")

    
    ##########################################################################################
    ##    Aggiorna la tabella
    ##########################################################################################


    def update_table(self, channels):
        print(channels)
        if "/" in channels['channels'][0]:
            self.group_0['text'] = channels['channels'][0].split('/')[0]
            self.file_0['text'] = channels['channels'][0].split('/')[1]

        if "/" in channels['channels'][1]:
            self.group_1['text'] = channels['channels'][1].split('/')[0]
            self.file_1['text'] = channels['channels'][1].split('/')[1]

        if "/" in channels['channels'][2]:
            self.group_2['text'] = channels['channels'][2].split('/')[0]
            self.file_2['text'] = channels['channels'][2].split('/')[1]

        if "/" in channels['channels'][3]:
            self.group_3['text'] = channels['channels'][3].split('/')[0]
            self.file_3['text'] = channels['channels'][3].split('/')[1]

        if "/" in channels['channels'][4]:
            self.group_4['text'] = channels['channels'][4].split('/')[0]
            self.file_4['text'] = channels['channels'][4].split('/')[1]

        if "/" in channels['channels'][5]:
            self.group_5['text'] = channels['channels'][5].split('/')[0]
            self.file_5['text'] = channels['channels'][5].split('/')[1]

        self.volume_0['text'] = channels['channels_volume'][0]*100
        self.volume_1['text'] = channels['channels_volume'][1]*100
        self.volume_2['text'] = channels['channels_volume'][2]*100
        self.volume_3['text'] = channels['channels_volume'][3]*100
        self.volume_4['text'] = channels['channels_volume'][4]*100
        self.volume_5['text'] = channels['channels_volume'][5]*100


























































####################################################################################################################


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


# ---------------------------------------------------------------------------------------
# Trova un canale libero, esegue il file, calcola il volume, aggiorna l'array
# ---------------------------------------------------------------------------------------

def play(channel, file, volume, loop):
    
    # print('Canale {}'.format(channel))
    # print('Nome del file {}'.format(file))
    # print('Volume {}'.format(volume))
    # Dizionario che raccoglie le informaioni dei canali

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
                # for i in range(num_channels):
                #       print("ELENCO FILE {}".format(file_playing[i]))
                # print(file_playing)
                self.group_1['text'] = 'awerqwe'
                self.file_1['text'] = 'ewrqwer'
                self.volume_1['text'] = 'ewrqwer'
        else:
            print("Playback file not found!")

        


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
    client = mqtt.Client(client_id="AUDIO" + str(DEVICE), clean_session=True, userdata=None, protocol=mqtt.MQTTv311, transport="tcp")
    client.on_connect = on_connect
    client.on_message = on_message

    time.sleep(1)

    client.loop_start()

    # Avvio della GUI

    if __name__ == "__main__":
        root = tk.Tk()
        app.MainWindow(root=root,device=DEVICE,connection=check_connection(client),global_volume=global_volume,client=client,)
        root.mainloop()



# Avvio del programma
if __name__ == "__main__":
    app.output_layout("Programma in esecuzione...")
    main()

