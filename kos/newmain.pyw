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
import json

newr = 0
newg = 0
newb = 0
newtemp = ""
newhumid = ""
newco= ""
arduinoVals = ""

version = "KOS V0.2.2"
arduinoAvailable = True
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
f = open('/home/pi/kos/Security.json')
logindata = json.load(f)
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1.5) #USB0 of ATM0
    ser.reset_input_buffer()
except:
    arduinoAvailable = False
set_appearance_mode("dark")  # Modes: system (default), light, dark
set_default_color_theme("dark-blue")  # Themes: blue (default), dark-blue, green

def donothing():
    donothingval = 0

def toepas():
	#kan tijdelijk nog niet, maar iets met Serial.write() en alle waarden.
	
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
	print(arduinoVals)
		
	package = arduinoVals +"V-\n"
	ser.write(package.encode())

def ventileerAlles():
	package= "C----H----T----R-G-B-V1\n"
	ser.write(package.encode())

def write_read(x):
    ser.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = ser.readline().decode('utf-8').rstrip()
    return data

def read():
    data = ser.readline().decode('utf-8').rstrip()
    return data

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

def rechtCheck():
    def closeAuth():
      authWindow.destroy()
      loguitknopf.configure(state="normal")
      
    def login():
      passw = password.get()
      for i in logindata['accountGegevens']:
          if passw ==  i["pass"]:
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




win = CTk()
win.configure(bg="#555555")
win.geometry("1920x1080")
win.title(version)
win.attributes('-fullscreen', True)

mainframe = CTkFrame(master=win, height=700, width=1880)
mainframe.place(x=20, y=10)

label = CTkLabel(mainframe, text="")
label.place(x=20, y=10, anchor=NW)

cap = cv2.VideoCapture(0)

fig = plt.Figure(figsize=(10, 6), dpi=100)



ax = fig.add_subplot(111)
ax.set_xlabel("aantal metingen")
ax.get_xaxis().set_major_locator(MaxNLocator(integer=True))
	
ax2 = ax.twinx()


#test waarden y = np.array([0,0.2,2,3.4,4,5,6.4,7.2,9,8,5,3,7,4])
#y = np.append(y, 1)
#y = np.append(y,2)




# test grafiek ax.plot(x, y)


canvas = FigureCanvasTkAgg(fig, master=mainframe)
canvas.draw()
canvas.get_tk_widget().place(x=850, y=10, anchor=NW)

def grafiekConfig():

	def closeGConfig():
         ConfigWindow.destroy()
         Plotknopf.configure(state="normal")
	
	def InitiateGraph():
		plotThread = threading.Thread(target=GraphStart, daemon=True)
		plotThread.start()
	
	
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
				
				
				
				
				total_rows = len(lst)
				total_columns = len(lst[0])

				tijdtussenmetingen = CTkLabel(tabelWindo,width=100, font=('Arial',16,'bold'))
				tijdtussenmetingen.configure(text="Tijd tussen metingen: "+str(hoevaakMetingen)+" seconden")
				tijdtussenmetingen.grid(row=0,column=0)
				for i in range(total_rows):
					for j in range(total_columns):
						e = CTkEntry(Tabelhierin, width=100,font=('Arial',16,'bold'))
						e.grid(row=j+1, column=i) 
						e.insert(END,lst[i][j])
						
				
			Plotknopf.configure(state="normal")
				
		except:
			Plotknopf.configure(state="normal")
			erderetext = popuptext.cget("text")
			popuptext.configure(text=erderetext+"\nEr is iets foutgegaan met het maken van de grafiek of tabel!")
	
	
	Plotknopf.configure(state="disabled")
	
	ConfigWindow = CTkFrame(master=win, height=300, width=500,border_color="white",border_width=1)
	ConfigWindow.place(x=800,y=400)
	cancelButn = CTkButton(master=ConfigWindow,text="X",fg_color="red",hover_color="#8b0000",height=10,width=30,command=closeGConfig)
	cancelButn.place(x=5,y=15,anchor=W)
	label = CTkLabel(master=ConfigWindow, text="Configureer grafiek", font=("Roboto", 20))
	label.place(y=20,x=175)
	freqnaam = CTkLabel(master=ConfigWindow, text="Hoeveel seconden er tussen een meting moet zitten")
	freqnaam.place(y=50,x=30)
	freq = CTkEntry(master=ConfigWindow, placeholder_text="minimaal 1", width=150, height=30, font=("Roboto", 10))
	freq.place(y=80,x=30)
	aantalnaam = CTkLabel(master=ConfigWindow, text="Hoeveel metingen er in totaal moeten plaatsvinden")
	aantalnaam.place(y=110,x=30)
	metingen = CTkEntry(master=ConfigWindow, placeholder_text="minimaal 1", width=150, height=30, font=("Roboto", 10))
	metingen.place(y=140,x=30)
	gemetenvalsnaam = CTkLabel(master=ConfigWindow, text="Welke gassen er op de grafiek moeten komen")
	gemetenvalsnaam.place(y=170,x=30)
	gemetenvals =  CTkOptionMenu(master=ConfigWindow, values=["CO2 en O2","O2","CO2"], width = 150, height=30)
	gemetenvals.place(y=200,x=30)
	toepasbtn = CTkButton(master=ConfigWindow, text="Start grafiek", command=InitiateGraph, width=150, height=20)
	toepasbtn.place(y=260,x=175)

def update_graph():
	if arduinoAvailable:
		ax.relim()
		oArray = np.array([])
		x = np.array([])
		coArray = np.array([])
			

mainconfig = CTkFrame(master=win, height=380, width=1920)
mainconfig.place(x=0, y=750)

tabelWindo = CTkScrollableFrame(master=mainconfig, width=750, height=300)
tabelWindo.place(x=900, y=10)

tabelWindo.bind_all("<Button-4>", lambda e: tabelWindo._parent_canvas.yview("scroll", -1, "units"))
tabelWindo.bind_all("<Button-5>", lambda e: tabelWindo._parent_canvas.yview("scroll", 1, "units"))

Tabelhierin = CTkFrame(master=tabelWindo, width=0, height=0)
Tabelhierin.grid(column=0, row=1)

HumidVal = CTkLabel(master=mainconfig, text="Luchtvochtigheid")
HumidVal.place(x=10, y=10, anchor=NW)

Humid = CTkLabel(master=mainconfig, text="lezen...")
Humid.place(x=160, y=10, anchor=NW)

targetHumid = CTkEntry(master=mainconfig, placeholder_text="voeg waarde in", state="disabled")
targetHumid.place(x=420, y=10, anchor=NW)

tempVal = CTkLabel(master=mainconfig, text="Temperatuur")
tempVal.place(x=10, y=40, anchor=NW)

temp = CTkLabel(master=mainconfig, text="lezen...")
temp.place(x=160, y=40, anchor=NW)

targetTemp = CTkEntry(master=mainconfig, placeholder_text="voeg waarde in", state="disabled")
targetTemp.place(x=420, y=40, anchor=NW)

OVal = CTkLabel(master=mainconfig, text="O2")
OVal.place(x=10, y=70, anchor=NW)

O = CTkLabel(master=mainconfig, text="lezen...")
O.place(x=160, y=70, anchor=NW)

COVal = CTkLabel(master=mainconfig, text="CO2")
COVal.place(x=10, y=100, anchor=NW)

CO = CTkLabel(master=mainconfig, text="lezen...")
CO.place(x=160, y=100, anchor=NW)

targetCO = CTkEntry(master=mainconfig, placeholder_text="voeg waarde in", state="disabled")
targetCO.place(x=420, y=100, anchor=NW)

Coreheat = CTkLabel(master=mainconfig, text="PI CPU temp:")
Coreheat.place(x=1700, y=30, anchor=W)

CoreHeatVal = CTkLabel(master=mainconfig, text="ERROR!", text_color="#FF5733")
CoreHeatVal.place(x=1800, y=30, anchor=W)



loguitknopf = CTkButton(master=mainconfig, text="verhoog rechten", command=rechtCheck)
loguitknopf.place(x=680, y=10, anchor=NW)

toepasknopf= CTkButton(master=mainconfig,text="waarden toepassen", command=toepas,state="disabled")
toepasknopf.place(x=680,y=40,anchor=NW)

Plotknopf = CTkButton(master=mainconfig, text="stel live grafiek in", command = grafiekConfig)
Plotknopf.place(x=680,y=70,anchor=NW)

ventknop = CTkButton(master=mainconfig,text="ventileer",state="disabled", command=ventileerAlles)
ventknop.place(x=680,y=100,anchor=NW)

popuptext = CTkLabel(master=tabelWindo, text_color="#FF5733", text="")
popuptext.grid(row = 999, column = 0, sticky = NE, padx=10)

R= CTkLabel(master=mainconfig,text="R",text_color="red")
R.place(x=10,y=130,anchor=NW)

Ro= CTkLabel(master=mainconfig,text="uit")
Ro.place(x=160,y=130,anchor=NW)

Rv= CTkSwitch(master=mainconfig,state="disabled",text="",button_color="red",button_hover_color	="darkred")
Rv.place(x=420,y=130,anchor=NW)

G= CTkLabel(master=mainconfig,text="G",text_color="green")
G.place(x=10,y=160,anchor=NW)

Go= CTkLabel(master=mainconfig,text="uit")
Go.place(x=160,y=160,anchor=NW)


Gv= CTkSwitch(master=mainconfig,state="disabled",text="",button_color="green",button_hover_color	="darkgreen")
Gv.place(x=420,y=160,anchor=NW)

B= CTkLabel(master=mainconfig,text="B",text_color="blue")
B.place(x=10,y=190,anchor=NW)

Bo= CTkLabel(master=mainconfig,text="uit")
Bo.place(x=160,y=190,anchor=NW)

Bv= CTkSwitch(master=mainconfig,state="disabled",text="",button_color="blue",button_hover_color	="darkblue")
Bv.place(x=420,y=190,anchor=NW)

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



def update_values():
    time.sleep(5)
    if arduinoAvailable:
        CoreHeatVal.configure(text_color="#f2f3f4")
        while True:
            raspberrypicoretemperature = round(CPUTemperature().temperature)
            CoreHeatVal.configure(text=str(raspberrypicoretemperature)+"°C")
            time.sleep(1)
            dataStr = write_read("")
            ProcessedData = list(dataStr)
            try: 
                oxygi = ProcessedData[13]+ProcessedData[14]+ProcessedData[15]+ProcessedData[16]+ProcessedData[17]+"%"
                tempi = ProcessedData[7]+ProcessedData[8]+ProcessedData[9]+ProcessedData[10]+ProcessedData[11]+"°C"
                humidi = ProcessedData[1]+ProcessedData[2]+ProcessedData[3]+ProcessedData[4]+ProcessedData[5]+"%"
                coi = ProcessedData[19]+ProcessedData[20]+ProcessedData[21]+ProcessedData[22]+" ppm"
                O.configure(text=oxygi)
                temp.configure(text=tempi)
                Humid.configure(text=humidi)
                CO.configure(text=coi)
                print(ProcessedData)
            except:
                 popuptext.configure(text="Sensor failure")
                 print(ProcessedData)
                 print(dataStr)
	                
    else:
        popuptext.configure(text="Arduino verbinding onstabiel of anders onbruikbaar")



varThread = threading.Thread(target=update_values, daemon=True)
varThread.start()
show_frames()
win.mainloop()
