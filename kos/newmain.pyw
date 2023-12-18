from gpiozero import CPUTemperature
from tkinter import *
from customtkinter import *
from PIL import Image, ImageTk
import cv2
import threading
import serial
import time
import logging
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import json
import os

# verklaren van enkele variabelen die nodig zijn
newr = 0
newg = 0
newb = 0
newtemp = ""
newhumid = ""
newco= ""
arduinoVals = ""


# algemene systeeminformatie
version = "KOS V1.0.1"
arduinoAvailable = True

# het openen van de beveiligingsdata
f = open('/home/pi/kos/Security.json')
logindata = json.load(f)

# probeer een verbinding met de arduino aan te gaan, anders foutmelding.
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1.5) #USB0 of ATM0
    ser.reset_input_buffer()
except:
    arduinoAvailable = False


# Thema aanzetten
set_appearance_mode("dark")  # Modes: system (default), light, dark
set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

# functie voor het ventileren
def ventileerAlles():
	package= "C----H----T----R-G-B-V1\n"
	ser.write(package.encode())
	erderetext = popuptext.cget("text")
	popuptext.configure(text=erderetext+"\nVentilering in uitvoering, even geduld a.u.b... ")
	ventknop.configure(text="annuleer ventileren", fg_color="red", hover_color = "darkred",command=annuleerVentileer)

# functie voor het annuleren van het ventileren	
def annuleerVentileer():
	package= "C----H----T----R-G-B-V0\n"
	ser.write(package.encode())
	erderetext = popuptext.cget("text")
	popuptext.configure(text=erderetext+"\nVentilering geannuleerd!")
	ventknop.configure(text="ventileer", fg_color="#1f538d", hover_color = "#14375e",command=ventileerAlles)

# functie voor het toepassen van ingevulde waarden
def toepas():
	if ventknop.cget("fg_color") == "red":
		erderetext = popuptext.cget("text")
		popuptext.configure(text=erderetext+"\nKan waarden niet toepassen tijdens het ventileren!\nAnnuleer het ventileringsproces om waarden toe te passen.")
		return
	try:
		if not targetCO.get() == "": 
			newco = int(round(float(targetCO.get()),4))
			if not newco >=5001 and not newco <=999:
				arduinoVals=("C"+str(newco))
				print(arduinoVals)
			else:
				print("co fiale")
				arduinoVals="C----"
		else:
			arduinoVals="C----"
	except:
		print("co empty")
		arduinoVals="C----"
	print(arduinoVals)
	try:
		if not targetHumid.get() == "":		
			newhumid = round(float(targetHumid.get()),1)
			if not newhumid <=29.9 and not newhumid >=90:
				arduinoVals+="H"+str(newhumid)
			else:
				arduinoVals+="H----"
		else:
			arduinoVals+="H----"
	except:
		print("humid empty")
		arduinoVals+="H----"
	try:
		if not targetTemp.get() == "":
			newtemp = round(float(targetTemp.get()),1)
			if not newtemp <=4.9 and not newtemp >=30:
				if newtemp <10:
					arduinoVals+="T0"+str(newtemp)
				else:
					arduinoVals+="T"+str(newtemp)
			else:
				arduinoVals+="T----"
		else:
			arduinoVals+="T----"
	except:
		arduinoVals+="T----"
	try:
		newr = int(Rv.get())
		arduinoVals+="R"+str(newr)
		if bool(newr)==True:
			Ro.configure(text="aan")
		elif bool(newr)==False:
			Ro.configure(text="uit")
	except:
		print("R empty")
	try:
		newg = int(Gv.get())
		arduinoVals+="G"+str(newg)
		if bool(newg)==True:
			Go.configure(text="aan")
		elif bool(newg)==False:
			Go.configure(text="uit")
	except:
		print("G empty")
	try:
		newb = int(Bv.get())
		arduinoVals+="B"+str(newb)
		if bool(newb)==True:
			Bo.configure(text="aan")
		elif bool(newb)==False:
			Bo.configure(text="uit")
	except:
		print("B empty")
		
	package = arduinoVals +"V-\n"
	ser.write(package.encode())

# lees de waarden die de arduion doorstuurt
def write_read(x):
    data = ser.readline().decode('utf-8').rstrip()
    return data

# verlies de rechten na 5 minuten
def deAuth():
  time.sleep(300)
  targetCO.configure(state="disabled")
  targetTemp.configure(state="disabled")
  targetHumid.configure(state="disabled")
  toepasknopf.configure(state="disabled")
  Bv.configure(state="disabled")
  Gv.configure(state="disabled")
  Rv.configure(state="disabled")  
  loguitknopf.configure(state="normal")
  ventknop.configure(state="disabled")

# popup login en login handelen
def rechtCheck():
    def closeAuth():
      authWindow.destroy()
      loguitknopf.configure(state="normal")
      
    def login():
      passw = password.get()
      for i in logindata['accountGegevens']:
          if passw ==  i["pass"]:
            if i["Debug"] == "True":
                exit(0)
			 
            targetCO.configure(state="normal",placeholder_text="voeg waarde in")
            targetTemp.configure(state="normal",placeholder_text="voeg waarde in")
            targetHumid.configure(state="normal",placeholder_text="voeg waarde in")
            toepasknopf.configure(state="normal")
            Bv.configure(state="normal")
            Gv.configure(state="normal")
            Rv.configure(state="normal")  
            ventknop.configure(state="normal")                                  
            deAuthTread = threading.Thread(target=deAuth, daemon=True)
            deAuthTread.start()
            authWindow.destroy()
            AantVentileren = 0
            
     
    loguitknopf.configure(state="disabled")
    authWindow = CTkFrame(master=win, height=250, width=500,border_color="white",border_width=1)
    authWindow.place(x=79,y=700)
    cancelButn = CTkButton(master=authWindow,text="X",fg_color="red",hover_color="#8b0000",height=10,width=30,command=closeAuth)
    cancelButn.place(x=5,y=15,anchor=W)
    label = CTkLabel(master=authWindow, text="Authorisatie vereist", font=("Roboto", 20))
    label.place(y=20,x=175)
    password = CTkEntry(master=authWindow, placeholder_text="Password", show="•", width=150, height=30, font=("Roboto", 10))
    password.place(y=100,x=175)
    loginbutton = CTkButton(master=authWindow, text="Login", command=login, width=150, height=20)
    loginbutton.place(y=140,x=175)


# definieren van de window
win = CTk()
win.configure(bg="#555555")
win.geometry("1920x1080")
win.title(version)
win.attributes('-fullscreen', True)
win.attributes('-topmost', False)

# het frame waar bijna alles op zit
mainframe = CTkFrame(master=win, height=700, width=1880)
mainframe.place(x=20, y=10)

# label waar de camerafeed op komt
label = CTkLabel(mainframe, text="")
label.place(x=20, y=10, anchor=NW)

# camera feed
cap = cv2.VideoCapture(0)

# figuur voor de grafiek maken en assen
fig = plt.Figure(figsize=(10, 6), dpi=100)
ax = fig.add_subplot(111)
ax.set_xlabel("aantal metingen")
ax.get_xaxis().set_major_locator(MaxNLocator(integer=True))
ax2 = ax.twinx()

# figuur plaatsen
canvas = FigureCanvasTkAgg(fig, master=mainframe)
canvas.draw()
canvas.get_tk_widget().place(x=850, y=10, anchor=NW)

# functie voor popup grafiek en grafiek instellen
def grafiekConfig():

	# sluit popup grafiek
	def closeGConfig():
         ConfigWindow.destroy()
         Plotknopf.configure(state="normal")
	
	# call de functie voor grafiek starten in thread
	def InitiateGraph():
		plotThread = threading.Thread(target=GraphStart, daemon=True)
		plotThread.start()
	
	# grafiek starten en live bijwerken
	def GraphStart():
		try:
			
						
			ax.cla()
			ax2.cla()
			aantalMetingen = int(metingen.get())
			hoevaakMetingen = int(freq.get())
			ConfigWindow.destroy()
			if arduinoAvailable:
				oArray = np.array([])
				coArray = np.array([])
				x = np.array([])
				oGraph, = ax.plot(x, oArray, color='red',label="zuurstof (%)")
				coGraph, = ax2.plot(x, coArray, label="co2 (ppm)")

				ax.legend(loc="upper left")	
				ax2.legend(loc="upper right")
					
				ax.set_xlabel("meting n")
				ax.get_xaxis().set_major_locator(MaxNLocator(integer=True))
				
				if gemetenvals.get() == "CO2 en O2":
					for t in range(1,aantalMetingen+1):
						newOval = float(O.cget("text").split("%")[0])
						newCval = float(CO.cget("text").split(" ")[0])
						oArray = np.append(oArray,newOval)
						coArray = np.append(coArray, newCval)
						x = np.append(x,t)
						oGraph.set_data(x,oArray)
						coGraph.set_data(x,coArray)
						ax2.relim()
						ax.relim()	
						ax2.autoscale_view()
						ax.autoscale_view()
						canvas.draw()
						time.sleep(hoevaakMetingen)					
					lst = [x,oArray,coArray]
				elif gemetenvals.get() == "O2":
					for t in range(1,aantalMetingen+1):
						newOval = float(O.cget("text").split("%")[0])
						oArray = np.append(oArray,newOval)
						x = np.append(x,t)
						oGraph.set_data(x,oArray)
						ax.relim()
						ax2.relim()	
						ax.autoscale_view()
						ax2.autoscale_view()
						canvas.draw()
						time.sleep(hoevaakMetingen)					
					lst = [x,oArray]
					
				elif gemetenvals.get() == "CO2":
					for t in range(1,aantalMetingen+1):
						newCval = float(CO.cget("text").split(" ")[0])
						coArray = np.append(coArray, newCval)
						x = np.append(x,t)
						coGraph.set_data(x,coArray)
						ax2.relim()
						ax.relim()	
						ax2.autoscale_view()
						ax.autoscale_view()
						canvas.draw()
						time.sleep(hoevaakMetingen)					
					lst = [x,coArray]
				
				
				
				bestandsnaam = time.strftime("%H%M%S",time.localtime())+".csv"
				
				total_rows = len(lst)
				total_columns = len(lst[0])
				
				tijdtussenmetingen.configure(text=F"Tijd tussen metingen: {str(hoevaakMetingen)} seconden.\nOpgeslagen als: {bestandsnaam}")
				tijdtussenmetingen.grid(row=0,column=0)
				for i in range(total_rows):
					for j in range(total_columns):
						e = CTkEntry(Tabelhierin, width=100,font=('Arial',16,'bold'))
						e.grid(row=j+1, column=i) 
						e.insert(END,lst[i][j])
						
				arr = np.array((coArray,oArray))



				df = pd.DataFrame(arr)
				df.to_csv(f"/home/pi/metingen/files/{bestandsnaam}",index=False,header=x)
				
				os.system('python3 /home/pi/kos/genindex.py ~/metingen/files')



			Plotknopf.configure(state="normal")
				
		except:
			Plotknopf.configure(state="normal")
			erderetext = popuptext.cget("text")
			popuptext.configure(text=erderetext+"\nEr is iets foutgegaan met het maken van de grafiek of tabel!")
	
	
	Plotknopf.configure(state="disabled")
	
	# de popup
	ConfigWindow = CTkFrame(master=win, height=300, width=500,border_color="white",border_width=1)
	ConfigWindow.place(x=800,y=400)
	cancelButn = CTkButton(master=ConfigWindow,text="X",fg_color="red",hover_color="#8b0000",height=10,width=30,command=closeGConfig)
	cancelButn.place(x=5,y=15,anchor=W)
	label = CTkLabel(master=ConfigWindow, text="Configureer meting", font=("Roboto", 20))
	label.place(y=20,x=175)
	freqnaam = CTkLabel(master=ConfigWindow, text="Hoeveel seconden er tussen een meting moet zitten")
	freqnaam.place(y=50,x=30)
	freq = CTkEntry(master=ConfigWindow, placeholder_text="minimaal 1", width=150, height=30, font=("Roboto", 10))
	freq.place(y=80,x=30)
	aantalnaam = CTkLabel(master=ConfigWindow, text="Hoeveel metingen er in totaal moeten plaatsvinden")
	aantalnaam.place(y=110,x=30)
	metingen = CTkEntry(master=ConfigWindow, placeholder_text="minimaal 1", width=150, height=30, font=("Roboto", 10))
	metingen.place(y=140,x=30)
	"""gemetenvalsnaam = CTkLabel(master=ConfigWindow, text="Welke gassen er op de grafiek moeten komen")
	gemetenvalsnaam.place(y=170,x=30)
	gemetenvals =  CTkOptionMenu(master=ConfigWindow, values=["CO2 en O2","O2","CO2"], width = 150, height=30)
	gemetenvals.place(y=200,x=30)"""

	Tabel1 = CTkLabel(master=ConfigWindow, text="Grafiek 1")
	Tabel1.place(y=170,x=30)
	Ografieknaam = CTkLabel(master=ConfigWindow,text="Zuurstof %")
	Ografieknaam.place(y=200,x=30)
	COgrafieknaam = CTkLabel(master=ConfigWindow,text="CO2 ppm")
	COgrafieknaam.place(y=230,x=30)
	Ografiekcheck = CTkSwitch(master=ConfigWindow)
	Ografiekcheck.place(y=200,x=175)
	COgrafiekcheck=CTkSwitch(master=ConfigWindow)
	COgrafiekcheck.place(y=230,x=175)
	toepasbtn = CTkButton(master=ConfigWindow, text="Start grafiek", command=InitiateGraph, width=150, height=20)
	toepasbtn.place(y=260,x=175)

# functie voor het bijwerken van de grafiek
def update_graph():
	if arduinoAvailable:
		ax.relim()
		oArray = np.array([])
		x = np.array([])
		coArray = np.array([])
			
# functie voor het wissen van de output
def clearOutput():
	popuptext.configure(text="")
	for widgets in Tabelhierin.winfo_children():
		widgets.destroy()
	Tabelhierin.destroy()
	tijdtussenmetingen.configure(text="")
	
# frame voor de meeste configuratiefunctionaliteit in de software
mainconfig = CTkFrame(master=win, height=380, width=1920)
mainconfig.place(x=0, y=750)

# scrollwindow voor de output
tabelWindo = CTkScrollableFrame(master=mainconfig, width=750, height=300)
tabelWindo.place(x=900, y=10)

# scrollwiel omhoog/omlaag koppelen aan scrollen in de scrollwindow
tabelWindo.bind_all("<Button-4>", lambda e: tabelWindo._parent_canvas.yview("scroll", -1, "units"))
tabelWindo.bind_all("<Button-5>", lambda e: tabelWindo._parent_canvas.yview("scroll", 1, "units"))

# stukje in de scrollwindow waar de tabel komt
Tabelhierin = CTkFrame(master=tabelWindo, width=0, height=0)
Tabelhierin.grid(column=0, row=1)

# label voor hoeveel seconden er tussen metingen zitten
tijdtussenmetingen = CTkLabel(tabelWindo,width=100, font=('Arial',16,'bold'))

# titel luchtvochtigheid
HumidVal = CTkLabel(master=mainconfig, text="Luchtvochtigheid")
HumidVal.place(x=10, y=10, anchor=NW)

# gemeten luchtvochtigheid
Humid = CTkLabel(master=mainconfig, text="lezen...")
Humid.place(x=160, y=10, anchor=NW)

# input voor luchtvochtigheid
targetHumid = CTkEntry(master=mainconfig, placeholder_text="voeg waarde in", state="disabled")
targetHumid.place(x=420, y=10, anchor=NW)

# titel temperatuur
tempVal = CTkLabel(master=mainconfig, text="Temperatuur")
tempVal.place(x=10, y=40, anchor=NW)

# gemeten temperatuur
temp = CTkLabel(master=mainconfig, text="lezen...")
temp.place(x=160, y=40, anchor=NW)

# input voor temperatuur
targetTemp = CTkEntry(master=mainconfig, placeholder_text="voeg waarde in", state="disabled")
targetTemp.place(x=420, y=40, anchor=NW)

# titel zuurstof
OVal = CTkLabel(master=mainconfig, text="O2")
OVal.place(x=10, y=70, anchor=NW)

# gemeten zuurstof
O = CTkLabel(master=mainconfig, text="lezen...")
O.place(x=160, y=70, anchor=NW)

# titel co2
COVal = CTkLabel(master=mainconfig, text="CO2")
COVal.place(x=10, y=100, anchor=NW)

# gemeten co2
CO = CTkLabel(master=mainconfig, text="lezen...")
CO.place(x=160, y=100, anchor=NW)

# input voor co2
targetCO = CTkEntry(master=mainconfig, placeholder_text="voeg waarde in", state="disabled")
targetCO.place(x=420, y=100, anchor=NW)

# titel van de pi cpu temperatuur
Coreheat = CTkLabel(master=mainconfig, text="PI CPU temp:")
Coreheat.place(x=1700, y=30, anchor=W)

# gemeten pi cpu temperatuur
CoreHeatVal = CTkLabel(master=mainconfig, text="ERROR!", text_color="white")
CoreHeatVal.place(x=1800, y=30, anchor=W)

# knop voor de output wissen
ClearOutputbtn =CTkButton(master=mainconfig,text="verwijder alle output", command = clearOutput)
ClearOutputbtn.place(x=1700,y=60,anchor=NW)

# verhoog rechten knop
loguitknopf = CTkButton(master=mainconfig, text="verhoog rechten", command=rechtCheck)
loguitknopf.place(x=680, y=10, anchor=NW)

# pas waarden toe knop
toepasknopf= CTkButton(master=mainconfig,text="waarden toepassen", command=toepas,state="disabled")
toepasknopf.place(x=680,y=40,anchor=NW)

# grafiek instellen knop
Plotknopf = CTkButton(master=mainconfig, text="stel live grafiek in", command = grafiekConfig)
Plotknopf.place(x=680,y=70,anchor=NW)

# ventileer knop
ventknop = CTkButton(master=mainconfig,text="ventileer",state="disabled", command=ventileerAlles)
ventknop.place(x=680,y=100,anchor=NW)

# tekstlabel voor foutmeldingen etc.
popuptext = CTkLabel(master=tabelWindo, text_color="#FF5733", text="", justify='left')
popuptext.grid(row = 999, column = 0, sticky = NE, padx=10)

# rood licht titel
R= CTkLabel(master=mainconfig,text="R",text_color="red")
R.place(x=10,y=130,anchor=NW)

# of rood licht aan of uit staat
Ro= CTkLabel(master=mainconfig,text="uit")
Ro.place(x=160,y=130,anchor=NW)

# switch rood licht
Rv= CTkSwitch(master=mainconfig,state="disabled",text="",button_color="red",button_hover_color	="darkred")
Rv.place(x=420,y=130,anchor=NW)

# groen licht titel
G= CTkLabel(master=mainconfig,text="G",text_color="green")
G.place(x=10,y=160,anchor=NW)

# groen licht aan of uit
Go= CTkLabel(master=mainconfig,text="uit")
Go.place(x=160,y=160,anchor=NW)

# switch groen licht
Gv= CTkSwitch(master=mainconfig,state="disabled",text="",button_color="green",button_hover_color	="darkgreen")
Gv.place(x=420,y=160,anchor=NW)

# blauw licht titel
B= CTkLabel(master=mainconfig,text="B",text_color="blue")
B.place(x=10,y=190,anchor=NW)

# blauw licht aan of uit
Bo= CTkLabel(master=mainconfig,text="uit")
Bo.place(x=160,y=190,anchor=NW)

# switch blauw licht
Bv= CTkSwitch(master=mainconfig,state="disabled",text="",button_color="blue",button_hover_color	="darkblue")
Bv.place(x=420,y=190,anchor=NW)

# camera feed verversen functie
def show_frames():
    cv2image = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
    img = cv2.rotate(cv2image, cv2.ROTATE_90_CLOCKWISE)
    img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    img = Image.fromarray(img)
    img = img.resize((800, 600))
    imgtk = ImageTk.PhotoImage(img, size=(800, 600))
    label.image = imgtk
    label.configure(image=imgtk)
    label.after(30, show_frames)


# gelezen waarden bijwerken functie
def update_values():
    raspberrypicoretemperature = round(CPUTemperature().temperature,1)
    CoreHeatVal.configure(text=str(raspberrypicoretemperature)+"°C")
    time.sleep(8)
    if arduinoAvailable:
        while True:
            time.sleep(1)
            
            if raspberrypicoretemperature >= 65:
                CoreHeatVal.configure(text_color="#FF5733")
            else:
                CoreHeatVal.configure(text_color="white")
            
            dataStr = write_read("")
            ProcessedData = list(dataStr)
            try: 
                oxygi = ProcessedData[13]+ProcessedData[14]+ProcessedData[15]+ProcessedData[16]+ProcessedData[17]
                tempi = ProcessedData[7]+ProcessedData[8]+ProcessedData[9]+ProcessedData[10]+ProcessedData[11]+"°C"
                humidi = ProcessedData[1]+ProcessedData[2]+ProcessedData[3]+ProcessedData[4]+ProcessedData[5]+"%"
                if not ProcessedData[19] == "0":
                    coi = ProcessedData[19]+ProcessedData[20]+ProcessedData[21]+ProcessedData[22]
                else:
                     coi = ProcessedData[20]+ProcessedData[21]+ProcessedData[22]
                O.configure(text=oxygi+"%")
                temp.configure(text=tempi)
                Humid.configure(text=humidi)
                CO.configure(text=coi+" ppm")
            except:
                 oldtext = popuptext.cget("text")
                 popuptext.configure(text=oldtext+"\nSensor error")
                 print(ProcessedData)
                 print(dataStr)
            if float(oxygi) >=19 and float(coi)<=2000 and ventknop.cget('fg_color') == "red":
                package= "C----H----T----R-G-B-V0\n"
                ser.write(package.encode())
                erderetext = popuptext.cget("text")
                popuptext.configure(text=erderetext+"\nVentilering succesvol!")
                ventknop.configure(text="ventileer", fg_color="#1f538d", hover_color = "#14375e",command=ventileerAlles)
	                
    else:
        popuptext.configure(text="Arduino verbinding onstabiel of anders onbruikbaar")
        raspberrypicoretemperature = round(CPUTemperature().temperature)
        CoreHeatVal.configure(text=str(raspberrypicoretemperature)+"°C")
        

# thread (meerdere dingen tegelijk in een cpu) starten voor waarden bijwerken
varThread = threading.Thread(target=update_values, daemon=True)
varThread.start()

# run software voor nog een frame
show_frames()
win.mainloop()
