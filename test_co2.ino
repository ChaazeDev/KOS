#include <Arduino.h>
#include "MHZ19.h"                                        
#include "DHT.h"
#include <Servo.h>
#define tempPin 2 
#define DHTTYPE DHT22

//configuratie relay nrs en die ene servo

#define roodRelay 38
#define groenRelay 37
#define blauwRelay 36
#define HRelay 35
#define ventileerRelay 34
#define CO2Relay 33
#define heatRelay 32
#define coolRelay 31
#define HServo 39

#include "DFRobot_OxygenSensor.h"                        
MHZ19 myMHZ19;    


String C;
String H;
String T;
String R;
String G;
String B;
String V;
bool RState;
bool GState;
bool BState;

#define Oxygen_IICAddress ADDRESS_3
#define COLLECT_NUMBER  10

DFRobot_OxygenSensor oxygen;
DHT dht(tempPin, DHTTYPE);
Servo HumidServo;

boolean DHTFail = false;
boolean GOSFail = false;
boolean ventileren = false;

void setup()
{
    Serial.begin(19200);
    Serial1.begin(9600);
    myMHZ19.begin(Serial1);
    myMHZ19.autoCalibration(true);
    dht.begin();
    while(!oxygen.begin(Oxygen_IICAddress)){
     oxygen.begin(Oxygen_IICAddress);
     delay(1000);
   }
   pinMode(ventileerRelay, OUTPUT);
   pinMode(CO2Relay, OUTPUT);
   pinMode(heatRelay, OUTPUT);
   pinMode(coolRelay, OUTPUT);
   pinMode(roodRelay, OUTPUT);
   pinMode(groenRelay, OUTPUT);
   pinMode(blauwRelay, OUTPUT);
   pinMode(HRelay, OUTPUT);

    //default opstelling: Ventileer uit, co2 dicht, warmtemat uit, rgb uit, luchtvochtigheid ook uit, niet alles zelfde setup
   digitalWrite(ventileerRelay,LOW);
   digitalWrite(CO2Relay,HIGH);
   digitalWrite(heatRelay,HIGH);
   digitalWrite(coolRelay,HIGH);
   digitalWrite(roodRelay,LOW);
   digitalWrite(groenRelay,LOW);
   digitalWrite(blauwRelay,LOW);
   digitalWrite(HRelay,HIGH);
  
   HumidServo.attach(HServo);
   HumidServo.writeMicroseconds(1400);
   pinMode(13,OUTPUT); //built in led
   digitalWrite(13,LOW);
}

void loop()
{
    delay(750);  

    float humi = dht.readHumidity();
    float temp = dht.readTemperature();

    float oxygenData = oxygen.getOxygenData(COLLECT_NUMBER);

    if(isnan(humi) || isnan(temp)){
      DHTFail = true;
    };
    if(isnan(oxygenData)){
    GOSFail = true;
    };
     
    int CO2; 

    CO2 = myMHZ19.getCO2();   

    if(DHTFail == true){
      Serial.print("H--.--T--.--");
    }else{
      Serial.print("H");
      Serial.print(humi);
      Serial.print("T");
      Serial.print(temp); 
    }; 
 

    Serial.print("O");
    Serial.print(oxygenData);                          // Request CO2 (as ppm)
        
    Serial.print("C");    
    if(CO2<1000){
         Serial.println("0"+String((CO2)));                  
    }else{
    Serial.println(CO2);  
    }

    char data[50];
    if (Serial.available() > 0){

      Serial.readStringUntil('\n').toCharArray(data, 50);

      C=String(data[1])+String(data[2])+String(data[3])+String(data[4]);
      H=String(data[6])+String(data[7])+String(data[8])+String(data[9]);
      T=String(data[11])+String(data[12])+String(data[13])+String(data[14]);
      R=data[16];
      G=data[18];
      B=data[20];
      V=data[22];

      GState = digitalRead(groenRelay);
      RState = digitalRead(roodRelay);
      BState = digitalRead(blauwRelay);

      
      //RGB verandert alleen bij toegepaste waarden, in de SerialAvailable statement
     if(not BState == B.toInt()){
        if(BState == 1){
          digitalWrite(blauwRelay,LOW);
        }else if(BState == 0){
          digitalWrite(blauwRelay,HIGH);
        }}
      
      if(not R.toInt() == RState){
        if(RState == 1){
        digitalWrite(roodRelay,LOW);
        }else if(RState == 0){
          digitalWrite(roodRelay,HIGH);
        }}

      if(not G.toInt() == GState){
        if(GState == 1){
        digitalWrite(groenRelay,LOW);
        }else if(GState == 0){
          digitalWrite(groenRelay,HIGH);
        }
      }

    //ventileren alleen bij externe input switchen
    if(V == "-"){
    }else{
     if(V.toInt() == 1){
      ventileren=true;
     }else if(V.toInt() == 0){
      ventileren=false;
     }else{
      // do stuf
     }

    }
}//einde van externe input statment

  
      if(humi <=H.toFloat() and not H.toFloat()== 0.00){
        digitalWrite(HRelay,HIGH);
        HumidServo.writeMicroseconds(1400);
      }else if(humi >=H.toFloat()+5 and not H.toFloat()== 0.00){
        digitalWrite(HRelay,LOW);
        HumidServo.writeMicroseconds(2900);
      }else if(not H.toFloat() ==0.00){
        digitalWrite(HRelay,LOW);
        HumidServo.writeMicroseconds(1400);
      }

      if(temp <= T.toFloat() and not T.toFloat() == 0.00){
          digitalWrite(heatRelay,LOW);
          digitalWrite(coolRelay,HIGH);
      }else if(temp >=T.toFloat()+2 and not T.toFloat() == 0.00){
          digitalWrite(heatRelay,HIGH);
          digitalWrite(coolRelay,LOW);
      }else if(not T.toFloat() ==0.00){
        digitalWrite(heatRelay,HIGH);
        digitalWrite(coolRelay,HIGH);
      }
      

    if(CO2 <= C.toFloat() and not C.toFloat()==0.00){
      digitalWrite(CO2Relay,LOW);
      digitalWrite(ventileerRelay,HIGH);
    }else if(CO2 >=C.toFloat()+100 and not C.toFloat()==0.00){
      digitalWrite(CO2Relay,HIGH);
      digitalWrite(ventileerRelay,LOW);
    }else if(not C.toFloat() ==0.00){
      digitalWrite(CO2Relay,HIGH);
      digitalWrite(ventileerRelay,HIGH);
    }

    if(ventileren==true){
      if(oxygenData >=19 and CO2 <= 2000){
        ventileren=false;
        digitalWrite(ventileerRelay,HIGH);
        digitalWrite(13,LOW);
      }else if(oxygenData <=18.9 or CO2 >=1999.9 ){
        digitalWrite(ventileerRelay,LOW);
        digitalWrite(13,HIGH);
      }
      digitalWrite(ventileerRelay,LOW);
      digitalWrite(13,HIGH);
    }else if(ventileren==false){
      digitalWrite(ventileerRelay,HIGH);
      digitalWrite(13,LOW);
    }
}
