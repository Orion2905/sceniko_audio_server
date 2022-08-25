"""Sceniko_audio-server - Interfaccia grafica
Questo programma genera un'interfaccia in grado di gestire i
canali e le connessioni di un server paho mqtt.
Se vuoi modificare impostazioni grafiche dei widget
visita questo link https://www.tutorialspoint.com/python/tk_scale.htm
"""

# Importazione delle librerie
import datetime  # libreria per ottenere data ed ora corrente
import tkinter as tk  # libreria per l'interfaccia grafica
from tkinter import *
from tkinter import ttk
import os, sys, subprocess  # Librerie per gestire le operazioni di sistema

import pygame.mixer




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


# classe per la MenuBar [ancora non implementata] (sarebbe il menù che di solito si trova in alto esempio è File)
class MenuBar:

    def __init__(self, parent):
        font = ('Corbel', 14)
        font_2 = ('Corbel', 10)

        menubar = tk.Menu(parent.root, font=font)
        parent.root.config(menu=menubar)

        file_dropdown = tk.Menu(menubar, font=font_2, tearoff=0)

        file_dropdown.add_command(label="About")

        menubar.add_cascade(label="File", menu=file_dropdown)
# Tutte queste funzioni che ci sono in realtà non fuzionano, servono solo per una futura implementazione


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

        # Bottone per aggiornare la tabella
        # self.update_button = tk.Button(
        #     self.button_frame,
        #     image=self.update,
        #     width=50,
        #     bd=2,
        #     bg=self.BACKGROUND_COLOR,
        #     fg="#c8d6e5",
        #     border=2
        # )
        # self.update_button.grid(row=0, column=3, padx=10)

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



 


