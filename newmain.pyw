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
import psutil

# verklaren van enkele variabelen die nodig zijn
newr = 0
newg = 0
newb = 0
newtemp = ""
newhumid = ""
newco= ""
arduinoVals = ""


# algemene systeeminformatie
version = "KOS V1.1"
arduinoAvailable = True
actieveGrafiek = 1

# het openen van de beveiligingsdata
f = open('/home/pi/kos/Security.json')
logindata = json.load(f)

# probeer een verbinding met de arduino aan te gaan, anders foutmelding.
try:
    ser = serial.Serial('/dev/ttyUSB0', 19200, timeout=1) #USB0 of ATM0
    ser.reset_input_buffer()
except:
    arduinoAvailable = False


# Thema aanzetten
set_appearance_mode("dark")  # Modes: system (default), light, dark
set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

# functie voor het ventileren
def ventileerAlles():
	package= "C----H----T----R0G0B0L0V1\n"
	ser.write(package.encode())
	LOG("Ventilering in uitvoering, even geduld a.u.b... ")
	ventknop.configure(text="annuleer ventileren", fg_color="red", hover_color = "darkred",command=annuleerVentileer)

# functie voor het annuleren van het ventileren	
def annuleerVentileer():
	package= "C----H----T----R-G-B-L0V0\n"
	ser.write(package.encode())
	LOG("Ventilering geannuleerd!")
	ventknop.configure(text="ventileer", fg_color="#1f538d", hover_color = "#14375e",command=ventileerAlles)

# functie voor het toepassen van ingevulde waarden
def toepas():
	if ventknop.cget("fg_color") == "red":
		ERR("Waarden konden niet toegepast worden. (0xc002)")
		return
	
	if not targetCO.get() == "": 
		newco = int(round(float(targetCO.get()),4))
		if not newco >=5001 and not newco <=350:
			if newco <= 999:
				arduinoVals=("C0"+str(newco))
			else:
				arduinoVals=("C"+str(newco))
		else:
			print(newco)
			ERR("Ongeldige waarde voor CO2!")
			arduinoVals="C----"
	else:
		arduinoVals="C----"
	#except:
		#print("co empty")
		#arduinoVals="C----"
	try:
		if not targetHumid.get() == "":		
			newhumid = round(float(targetHumid.get()),1)
			if not newhumid <=29.9 and not newhumid >=90:
				arduinoVals+="H"+str(newhumid)
			else:
				ERR("Ongeldige waarde voor luchtvochtigheid!")
				arduinoVals+="H----"
		else:
			arduinoVals+="H----"
	except:
		print("humid empty")
		arduinoVals+="H----"
	try:
		if not targetTemp.get() == "":
			newtemp = round(float(targetTemp.get()),1)
			if not newtemp <=4.9 and not newtemp >30:
				if newtemp <10:
					arduinoVals+="T0"+str(newtemp)
				else:
					arduinoVals+="T"+str(newtemp)
			else:
				arduinoVals+="T----"
				ERR("Ongeldige waarde voor temperatuur!")
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
		
	print(arduinoVals)
	package = arduinoVals +"L-V-\n"
	ser.write(package.encode())

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
  lichtknop.configure(state="disabled")
  cacl.configure(state="disabled")

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
            lichtknop.configure(state="normal")
            cacl.configure(state="normal")                                
            deAuthTread = threading.Thread(target=deAuth, daemon=True)
            deAuthTread.start()
            authWindow.destroy()
            AantVentileren = 0
          elif passw=="onjuist": 
             wwtext.configure(text="haha heel grappig")
          else:
             wwtext.configure(text="wachtwoord is onjuist")
            
     
    loguitknopf.configure(state="disabled")
    authWindow = CTkFrame(master=win, height=250, width=500,border_color="white",border_width=1)
    authWindow.place(x=79,y=700)
    cancelButn = CTkButton(master=authWindow,text="X",fg_color="red",hover_color="#8b0000",height=10,width=30,command=closeAuth)
    cancelButn.place(x=5,y=15,anchor=W)
    label = CTkLabel(master=authWindow, text="Authorisatie vereist", font=("Roboto", 20))
    label.place(y=20,x=155)
    password = CTkEntry(master=authWindow, placeholder_text="Password", show="•", width=150, height=30, font=("Roboto", 10))
    password.place(y=100,x=175)
    wwtext = CTkLabel(master=authWindow, text="", text_color="#FF5733")
    wwtext.place(y=70,x=175)
    loginbutton = CTkButton(master=authWindow, text="Login", command=login, width=150, height=20)
    loginbutton.place(y=140,x=175)


def lichtConfig():
	lichtknop.configure(state="disabled")
	def closeWin():
		lichtframe.destroy()
		lichtknop.configure(state="normal")
	
	def startLicht():
		
		global C1
		global C2
		global C3
		try:
			C1 = round(float(dagOver.get()))
			C2 = round(float(nachtUren.get()))
			C3 = round(float(dagUren.get()))
			if not C1 < C3:
				ERR("Het aantal minuten over in een dag kan niet groter zijn dan het totale aantal minuten in een dag!")
				return
		except:
			print("eyy lmao")
		closeWin()
		global choice
		choice = lichtModus.get()
				
		lichtknop.configure(text="Breek lichtcyclus af", fg_color="red",hover_color="#8b0000", command=abortLicht)
		if choice == "Aan":
			lichtStatus2.configure(text="∞ minuten")
			LOG("Lichtcyclus gestart [Mode: aan]")
			lichtStatus1.configure(text="aan")
			package= "C----H----T----R-G-B-L1V-\n"
			ser.write(package.encode())

		elif choice == "Uit":
			lichtStatus2.configure(text="∞ minuten")
			LOG("Lichtcyclus gestart [Mode: uit]")
			lichtStatus1.configure(text="uit")
			package= "C----H----T----R-G-B-L0V-\n"
			ser.write(package.encode())
		else:
			LOG(f"Lichtcyclus gestart [Mode: Cyclus, Dag over: {C1} minuten, Duur nacht: {C2} minuten, Duur dag: {C3} minuten]")
			package= "C----H----T----R-G-B-L1V-\n"
			ser.write(package.encode())
			global currentLightState
			if not int(C1)==0: 
				lichtStatus1.configure(text="aan") 
				lichtStatus2.configure(text=f"{C1} minuten")
				currentLightState=1
			else: 
				lichtStatus1.configure(text="uit")
				lichtStatus2.configure(text=f"{C2} minuten")
				currentLightState=0
			lichtcyclusThread= threading.Thread(target=lichtCyclus, daemon=True)
			lichtcyclusThread.start()
			
	def lichtCyclus():
		global C1
		global C2
		global C3
		dayLeft = C1
		dayTime = C3
		nightTime = C2		
		
		global currentLightState
		while True:
			if dayLeft >=1:
				for i in range(dayLeft):
					
					time.sleep(60)
					dayLeft -=1
					lichtStatus2.configure(text=f"{dayLeft} minuten")
					
			else:
				if currentLightState == 1:
					lichtStatus1.configure(text="uit")
					lichtStatus2.configure(text=f"{nightTime} minuten")
					currentLightState=0
					dayLeft = nightTime
				elif currentLightState == 0:
					lichtStatus1.configure(text="aan")
					lichtStatus2.configure(text=f"{dayTime} minuten")
					currentLightState=1
					dayLeft = dayTime
			
			package= F"C----H----T----R-G-B-L{currentLightState}V-\n"
			ser.write(package.encode())
	
		
	def abortLicht():
		LOG(f"Lichtcyclus gestopt [Mode: {choice.lower()}]")
		lichtStatus2.configure(text="inactief")
		lichtStatus1.configure(text="uit")
		# hier nog de serial write om licht uit te zetten maar he de arduino zit niet meer vast door die kindjes
		package= "C----H----T----R-G-B-L0V-\n"
		ser.write(package.encode())
		lichtknop.configure(fg_color="#1f538d", hover_color = "#14375e", text="Laat er licht zijn!", command=lichtConfig)
	
	def lichtCallBack(choice):
		if not choice == "Cyclus":
			dagOver.delete(0, last_index=999)
			nachtUren.delete(0, last_index=999)
			dagUren.delete(0, last_index=999)
			nachtUren.configure(state="disabled")
			dagOver.configure(state="disabled")
			dagUren.configure(state="disabled")
		else:
			nachtUren.configure(state="normal", placeholder_text="in minuten")
			dagUren.configure(state="normal", placeholder_text="in minuten")
			dagOver.configure(state="normal", placeholder_text="in minuten")
	
	lichtframe = CTkFrame(master=win, height=400, width=500,border_color="white",border_width=1)
	lichtframe.place(x=79,y=500)
	cancelButn = CTkButton(master=lichtframe,text="X",fg_color="red",hover_color="#8b0000",height=10,width=30,command=closeWin)
	cancelButn.place(x=5,y=15,anchor=W)
	label = CTkLabel(master=lichtframe, text="Lichtcyclus configuratie", font=("Roboto", 20))
	label.place(y=15,x=155)
	
	ModusLabel=CTkLabel(master=lichtframe,text="Selecteer lichtmodus")
	ModusLabel.place(x=30,y=70)
	lichtModus = CTkOptionMenu(master=lichtframe,values=["Aan","Cyclus","Uit"], command=lichtCallBack)
	lichtModus.place(x=350,y=70)

	configlabel = CTkLabel(master=lichtframe,text="Cyclusinstellingen:", font=("Roboto", 16, 'bold'))
	configlabel.place(x=30,y=130)

	uurLabel = CTkLabel(master=lichtframe,text="Hoe lang het nacht moet zijn:")
	uurLabel.place(x=30,y=160)
	nachtUren = CTkEntry(master=lichtframe)
	nachtUren.place(x=350,y=160)
	
	dagUrenLabel = CTkLabel(master=lichtframe,text="Hoe lang het dag moet zijn:")
	dagUrenLabel.place(x=30,y=190)
	dagUren = CTkEntry(master=lichtframe)
	dagUren.place(x=350,y=190)
	
	dagLabel = CTkLabel(master=lichtframe,text="Over hoeveel minuten het nacht moet worden:")
	dagLabel.place(x=30,y=220)
	dagOver=CTkEntry(master=lichtframe)
	dagOver.place(x=350,y=220)
	
	nachtUren.configure(state="disabled")
	dagOver.configure(state="disabled")
	
	initLicht = CTkButton(master=lichtframe, text="Laat er licht zijn!", command=startLicht, width=150, height=20)
	initLicht.place(y=340,x=175)

def ignore():
	pass

# definieren van de window
win = CTk()
win.configure(bg="#555555")
win.geometry("1920x1080")
win.title(version)
win.attributes('-fullscreen', True)
win.attributes('-topmost', False)

win.protocol("WM_DELETE_WINDOW", ignore)

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

oArray = np.array([])
coArray = np.array([])
hArray = np.array([])
tArray = np.array([])
x = np.array([])

ax.cla()
ax2.cla()	
oGraph, = ax.plot(x, oArray, color='red',label="zuurstof (%)")
coGraph, = ax2.plot(x, coArray, label="co2 (ppm)")

def g1Active():
	global actieveGrafiek
	actieveGrafiek = 1 
	grafiek1Knop.configure(fg_color="gray10")
	grafiek2Knop.configure(fg_color="gray12")
	ax.cla()
	ax2.cla()
	oGraph, = ax.plot(x, oArray, color='red',label="zuurstof (%)")
	coGraph, = ax2.plot(x, coArray, label="co2 (ppm)")
	ax.relim()
	ax2.relim()	
	ax.legend(bbox_to_anchor=(0.15, 1.1))	
	ax2.legend(bbox_to_anchor=(1.05, 1.1))
	ax.get_xaxis().set_major_locator(MaxNLocator(integer=True))
	ax.autoscale_view()
	ax2.autoscale_view()
	canvas.draw()
	
def g2Active():
	global actieveGrafiek
	actieveGrafiek = 2
	grafiek1Knop.configure(fg_color="gray12")
	grafiek2Knop.configure(fg_color="gray10")
	ax.cla()
	ax2.cla()
	oGraph, = ax.plot(x, hArray, color='red',label="luchtvochtigheid (%)")
	coGraph, = ax2.plot(x, tArray,color='blue', label="temperatuur (°C)")
	oGraph.set_label("luchtvochtigheid (%)")
	oGraph.set_data(x,hArray)
	coGraph.set_label("temperatuur (°C)")
	coGraph.set_data(x,tArray)
	ax.relim()
	ax2.relim()	
	ax.legend(bbox_to_anchor=(0.15, 1.1))	
	ax2.legend(bbox_to_anchor=(1.05, 1.1))
	ax.get_xaxis().set_major_locator(MaxNLocator(integer=True))
	ax.autoscale_view()
	ax2.autoscale_view()
	canvas.draw()
	

def ERR(msg):
	errorMessage = CTkLabel(master=popuptext,text=msg,text_color="#FF5733",height=20 , justify='left')
	errorMessage.grid(pady=0,padx=0, sticky="NW")

def LOG(msg):
	logMessage = CTkLabel(master=popuptext,text=msg,height=20 , justify='left')
	logMessage.grid(pady=0,padx=0, sticky="NW")

grafiek1Knop = CTkButton(master=mainframe, text="grafiek 1",font=("roboto",18), width=400,height=40,fg_color="gray10", hover_color="gray10", command=g1Active)
grafiek1Knop.place(x=940,y=600)

grafiek2Knop = CTkButton(master=mainframe, text="grafiek 2",font=("roboto",18), width=400,height=40, fg_color="gray12", hover_color="gray10", command=g2Active)
grafiek2Knop.place(x=1410,y=600)

# figuur plaatsen
canvas = FigureCanvasTkAgg(fig, master=mainframe)
canvas.draw()
canvas.get_tk_widget().place(x=850, y=10, anchor=NW)

# functies voor openen/sluiten cacl
def openCacl():

	cacl.configure(text="sluit cacl bakje", command = closeCacl)
	toepasknopf.configure(state="disabled")
	package= F"C----H10.0T----R-G-B-L0V0\n"
	ser.write(package.encode())

def closeCacl():
	global humidi
	toepasknopf.configure(state="normal")
	cacl.configure(text="open cacl bakje", command = openCacl)
	print(humidi[:4])
	package= F"C----H{humidi[:4]}T----R-G-B-L0V0\n"
	ser.write(package.encode())


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
		timelapseThread = threading.Thread(target=timelapseStart, daemon=True)
		timelapseThread.start()
	
	# grafiek starten en live bijwerken
	def GraphStart():

		
							
		ax.cla()
		ax2.cla()
		aantalMetingen = int(metingen.get())
		hoevaakMetingen = int(freq.get())
		global bestandsnaam
		bestandsnaam = naamMeting.get()

		meetO =Ografiekcheck.get()
		meetCo = COgrafiekcheck.get()
		meetH = Hgrafiekcheck.get()
		meetT =Tgrafiekcheck.get()

		ConfigWindow.destroy()
		if arduinoAvailable:
			global oArray
			global coArray
			global hArray
			global tArray
			global x

			oArray = np.array([])
			coArray = np.array([])
			hArray = np.array([])
			tArray = np.array([])
			x = np.array([])


			for t in range(1,aantalMetingen+1):
				ax.cla()
				ax2.cla()
				x = np.append(x,t)


				if meetO == 1:
					newOval = float(O.cget("text").split("%")[0])
					oArray = np.append(oArray,newOval)

					if actieveGrafiek == 1:
						oGraph, = ax.plot(x, oArray, color='red',label="zuurstof (%)")
						oGraph.set_data(x,oArray)
						ax.legend(bbox_to_anchor=(0.15, 1.1))	
		
				if meetCo == 1:
					newCval = float(CO.cget("text").split(" ")[0])
					coArray = np.append(coArray, newCval)
					if actieveGrafiek == 1:
						coGraph, = ax2.plot(x, coArray,color='blue', label="co2 (ppm)")
						coGraph.set_data(x,coArray)
						ax2.legend(bbox_to_anchor=(1.05, 1.1))
				if meetH == 1:
					newHval = float(Humid.cget("text").split("%")[0])
					hArray = np.append(hArray,newHval)
					if actieveGrafiek == 2:
						oGraph, = ax.plot(x, hArray, color='red',label="luchtvochtigheid (%)")
						oGraph.set_data(x,hArray)
						ax.legend(bbox_to_anchor=(0.15, 1.1))	

				if meetT == 1:
					newTval = float(temp.cget("text").split("°")[0])
					tArray = np.append(tArray,newTval)
					if actieveGrafiek == 2:
						coGraph, = ax2.plot(x, tArray,color='blue', label="temperatuur (°C)")
						coGraph.set_data(x,tArray)
						ax2.legend(bbox_to_anchor=(1.05, 1.1))
						
				
				
				
				
						
				ax.set_xlabel("meting n")
				ax.get_xaxis().set_major_locator(MaxNLocator(integer=True))
					
				lst = [x]
				if meetO ==1: lst.append(oArray)
				if meetCo ==1: lst.append(coArray)
				if meetH ==1: lst.append(hArray)
				if meetT ==1: lst.append(tArray)

				ax.relim()
				ax2.relim()	
				ax.autoscale_view()
				ax2.autoscale_view()
				canvas.draw()
			
				time.sleep(hoevaakMetingen)	
					
						
					

					
			total_rows = len(lst)
			total_columns = len(lst[0])
				
			tijdtussenmetingen.configure(text=F"Tijd tussen metingen: {str(hoevaakMetingen)} seconden.\nOpgeslagen als: {bestandsnaam}.csv")
			tijdtussenmetingen.grid(row=0,column=0)

			arr = np.array([[]])
			if meetO==1: arr = np.append(arr,oArray)
			if meetCo ==1: arr = np.append(arr,coArray)
			if meetH ==1: arr = np.append(arr,hArray)
			if meetT ==1: arr = np.append(arr,tArray)	

			arr = np.reshape(arr,(total_rows-1,total_columns))

			df = pd.DataFrame(arr)
			df.to_csv(f"~/metingen/files/{bestandsnaam}.csv",index=False,header=x)
					
			os.system('python3 /home/pi/kos/genindex.py ~/metingen/files')

		Plotknopf.configure(state="normal")
	
	def timelapseStart():
		global GBfree
		if not CameraUberhaupt.get() == 1:
			return
		global cv2image
		if GBfree <=1:
			ERR("Timlapse niet gestart. (0xc001)")
			return
		totalTime = int(metingen.get())*int(freq.get())
		fps = 30

		

		if totalTime <=3600: secInterval = 5
		elif totalTime <=86400: secInterval = 120
		else: secInterval = 240

		numPhotos = int((totalTime)/secInterval)

		# verwijder mogelijke oude foto's van vroegere timelapses
		os.system("rm /home/pi/Pictures/*.jpg")

		for i in range(numPhotos):
			cv2.imwrite(f'/home/pi/Pictures/{i}.png',cv2image)
			time.sleep(secInterval)

		os.system(f'ffmpeg -r {fps} -f image2 -s 1920x1080 -nostats -loglevel 0 -pattern_type glob -i "/home/pi/Pictures/*.png" -vcodec libx264 -crf 25  -pix_fmt yuv420p ~/metingen/files/snapshots/{bestandsnaam}.mp4 -y')
		os.system('python3 /home/pi/kos/genindex.py ~/metingen/files/snapshots')
		
	Plotknopf.configure(state="disabled")
	
	# de popup
	ConfigWindow = CTkFrame(master=win, height=400, width=500,border_color="white",border_width=1)
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

	Tabel1 = CTkLabel(master=ConfigWindow, text="Grafiek 1")
	Tabel1.place(y=170,x=30)
	Ografieknaam = CTkLabel(master=ConfigWindow,text="Zuurstof %")
	Ografieknaam.place(y=200,x=30)
	COgrafieknaam = CTkLabel(master=ConfigWindow,text="CO2 ppm")
	COgrafieknaam.place(y=230,x=30)
	Ografiekcheck = CTkSwitch(master=ConfigWindow, text="    Luchtvochtigheid %")
	Ografiekcheck.place(y=200,x=175)
	COgrafiekcheck=CTkSwitch(master=ConfigWindow, text="    Temperatuur °C")
	COgrafiekcheck.place(y=230,x=175)
	Tabel2 = CTkLabel(master=ConfigWindow, text="Grafiek 2")
	Tabel2.place(y=170,x=230)
	Hgrafiekcheck = CTkSwitch(master=ConfigWindow,text="", width=40)
	Hgrafiekcheck.place(y=200,x=450)
	Tgrafiekcheck = CTkSwitch(master=ConfigWindow,text="", width=40)
	Tgrafiekcheck.place(y=230,x=450)
	
	CameraConfig = CTkLabel(master=ConfigWindow, text="camerainstellingen", font=("Roboto",15))
	CameraConfig.place(y=260,x=30)
	CamUTitel = CTkLabel(master=ConfigWindow,text="Opname camera")
	CamUTitel.place(y=290,x=30)
	CameraUberhaupt = CTkSwitch(master=ConfigWindow,text="", width=40)
	CameraUberhaupt.place(y=292,x=175)
	
	naamMetingTitel = CTkLabel(master=ConfigWindow, text="Naam meting voor identificatie")
	naamMetingTitel.place(y=320,x=30)
	naamMeting = CTkEntry(master=ConfigWindow, placeholder_text="voeg naam in")
	naamMeting.place(x=250, y=320)
	toepasbtn = CTkButton(master=ConfigWindow, text="Start meting", command=InitiateGraph, width=150, height=20)
	toepasbtn.place(y=360,x=175)

		
# functie voor het wissen van de output
def clearOutput():
	for msg in popuptext.winfo_children():
		msg.destroy()
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

storageLeft = CTkLabel(master=mainconfig, text="[NaN] GB opslag over", text_color="grey")
storageLeft.place(x=1700,y=300,anchor=W)

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
Plotknopf = CTkButton(master=mainconfig, text="stel meting in", command = grafiekConfig)
Plotknopf.place(x=680,y=70,anchor=NW)

# ventileer knop
ventknop = CTkButton(master=mainconfig,text="ventileer",state="disabled", command=ventileerAlles)
ventknop.place(x=680,y=100,anchor=NW)

# licht knop
lichtknop = CTkButton(master=mainconfig,text="stel lichtsystemen in", state="disabled",command=lichtConfig)
lichtknop.place(x=680,y=130,anchor=NW)

# open cacl bak
cacl = CTkButton(master=mainconfig,text="open cacl bakje",state="disabled",  command=openCacl)
cacl.place(x=680,y=160,anchor=NW)

# tekstlabel voor foutmeldingen etc.
popuptext = CTkLabel(master=tabelWindo, text_color="#FF5733", text="", justify='left')
popuptext.grid(row = 999, column = 0, sticky = NE, padx=10)

# rood licht titel
R= CTkLabel(master=mainconfig,text="Rode ledstrip")
R.place(x=10,y=130,anchor=NW)

# of rood licht aan of uit staat
Ro= CTkLabel(master=mainconfig,text="uit")
Ro.place(x=160,y=130,anchor=NW)

# switch rood licht
Rv= CTkSwitch(master=mainconfig,state="disabled",text="",button_color="red",button_hover_color	="darkred")
Rv.place(x=420,y=130,anchor=NW)

# groen licht titel
G= CTkLabel(master=mainconfig,text="Groene ledstrip")
G.place(x=10,y=160,anchor=NW)

# groen licht aan of uit
Go= CTkLabel(master=mainconfig,text="uit")
Go.place(x=160,y=160,anchor=NW)

# switch groen licht
Gv= CTkSwitch(master=mainconfig,state="disabled",text="",button_color="green",button_hover_color	="darkgreen")
Gv.place(x=420,y=160,anchor=NW)

# blauw licht titel
B= CTkLabel(master=mainconfig,text="Blauwe ledstrip")
B.place(x=10,y=190,anchor=NW)

# blauw licht aan of uit
Bo= CTkLabel(master=mainconfig,text="uit")
Bo.place(x=160,y=190,anchor=NW)

# switch blauw licht
Bv= CTkSwitch(master=mainconfig,state="disabled",text="",button_color="blue",button_hover_color	="darkblue")
Bv.place(x=420,y=190,anchor=NW)

lichtStatusi = CTkLabel(master=mainconfig, text="Lightstatus")
lichtStatusi.place(x=10,y=220,anchor=NW)

lichtStatus1 = CTkLabel(master=mainconfig,text="uit")
lichtStatus1.place(x=160,y=220,anchor=NW)

lichtStatus2 = CTkLabel(master=mainconfig, text="inactief")
lichtStatus2.place(x=420,y=220,anchor=NW)

# camera feed verversen functie
def show_frames():
    global cv2image
    cv2image = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
    # als we 'm willen draaien img = cv2.rotate(cv2image, cv2.ROTATE_90_CLOCKWISE)
    img = Image.fromarray(cv2image)
    img = img.resize((800, 600))
    imgtk = ImageTk.PhotoImage(img, size=(800, 600))
    label.image = imgtk
    label.configure(image=imgtk)
    label.after(40, show_frames)

def update_values():
	time.sleep(3)
	while True:
	   global humidi
	   if ser.in_waiting >0 and not ser.readline().rstrip() == "":
             dataStr = ser.readline().decode('utf-8').rstrip()
             ProcessedData = list(dataStr)
             raspberrypicoretemperature = round(CPUTemperature().temperature,1)
             CoreHeatVal.configure(text=str(raspberrypicoretemperature)+"°C")
             bytes_avail = psutil.disk_usage('/').free
             global GBfree
             GBfree = bytes_avail / 1024 / 1024 / 1024
             storageLeft.configure(text=f"{round(float(GBfree),2)} GB opslag over",text_color="grey") if float(GBfree) >1 else storageLeft.configure(text=f"{round(float(GBfree),2)} GB opslag over",text_color="#FF5733")
             if raspberrypicoretemperature >= 65:
                CoreHeatVal.configure(text_color="#FF5733")
             else:
                CoreHeatVal.configure(text_color="white")
	     
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
                ERR("Fout bij het lezen van sensorwaarden. (0xc003)")
                print(ProcessedData)
                print(dataStr)
	     
             try:
                if float(oxygi) >=19 and float(coi)<=2000 and ventknop.cget('fg_color') == "red":
                   package= "C----H----T----R-G-B-L0V0\n"
                   ser.write(package.encode())
                   LOG("Ventilering succesvol!")
                   ventknop.configure(text="ventileer", fg_color="#1f538d", hover_color = "#14375e",command=ventileerAlles)   
             except:
                   ERR("Onbekende byte in communicatie tussen sensoren.")
                   LOG("Gecompenseerd voor onbekende byte, functionaliteit nominaal.")
	                

# gelezen waarden bijwerken functie
if arduinoAvailable:
    waarden = threading.Thread(target=update_values, daemon=True)
    waarden.start()	
else:
    ERR("Arduino verbinding onstabiel of anders onbruikbaar. (0xc004)")
    raspberrypicoretemperature = round(CPUTemperature().temperature)
    CoreHeatVal.configure(text=str(raspberrypicoretemperature)+"°C")
    
# thread (meerdere dingen tegelijk in een cpu) starten voor waarden bijwerken


# run software voor nog een frame
	
show_frames()
win.mainloop()
