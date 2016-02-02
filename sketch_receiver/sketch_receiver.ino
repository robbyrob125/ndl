#include <RCSwitch.h>
#include <LiquidCrystal.h>

RCSwitch sender = RCSwitch( );
LiquidCrystal lcd = LiquidCrystal(8 ,9 ,4 ,5 ,6 ,7);

//Sender
#define CodeLength 24
#define SendPin A5

const unsigned long OnCode[2] = {1381717, 1394005};
const unsigned long OffCode[2] = {1381716, 1394004};

//Sonic sensor
#define trigPin A2
#define echoPin A1

//Buttons
#define KEY_COUNT 4

int keyLimits [KEY_COUNT+1] = {100, 330, 580, 900, 1023};
int keyNames [KEY_COUNT+1] = {0, 1, 2, 3, 4};

//Timer
unsigned long timeLastSeen = 0;
bool sonicPriority = false;




/*
 *Camil Staps, s4498062
 *Robin Immel, s4372891
 *Arduino: 
 *  3.3V
 *Sender connected to 
 *  Data : A5
 *Ultrasonic connected to:
 *  Echo : A1
 *  Trig : A2
 * 
 *LCD shield connected to:
 *  Arduino

 */
 
void setup() {
  lcd.begin(16,2);
  pinMode(SendPin, OUTPUT);
  sender.enableTransmit(SendPin);
  sender.setProtocol(1);
  pinMode(trigPin, OUTPUT) ;
  pinMode(echoPin, INPUT) ;
}

void setSocket(int id, bool on) {
    sender.send((on ? OnCode : OffCode)[id], CodeLength);
    lcd.setCursor(0, id);
    lcd.print("Socket ");
    lcd.print(id);
    lcd.print(on ? " on " : " off");
}

void button_left(){
    setSocket(0, true);
    setSocket(1, false);
}

void button_right(){
    setSocket(0, false);
    setSocket(1, true);
}

void button_up(){
    setSocket(0, true);
    setSocket(1, true);
}

void button_down(){
    setSocket(0, false);
    setSocket(1, false);
}

int check_button(){
  int val = analogRead(A0);
  for (int i = 0; i <= KEY_COUNT; i++)
    if (val < keyLimits[i])
      return keyNames[i];
}

bool object_close(){
    digitalWrite(trigPin, HIGH) ;
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW) ;
    int duration = pulseIn(echoPin, HIGH) ;
    return (((duration / 2) / 29) < 100);
}

void loop() {
  bool trigger = object_close();
  //Als er iets gezien wordt in de laatste 5 seconde, gaan de lampen aan.
  if(trigger || millis() < timeLastSeen + 5000){
    setSocket(0,true);
    setSocket(1,true);

    if (trigger)
      timeLastSeen = millis();

    sonicPriority = true;
  }
  //Anders als er ooit iets gezien is, maar niet de laatste 5 seconden gaan de stopcontacten uit.
  else if (sonicPriority) {
    setSocket(0, false);
    setSocket(1, false);
    sonicPriority = false;
  } 
  //Anders kan men de stopcontacten aan/uit zetten met de knopjes.
  else {
    switch (check_button()) {
      case 0: button_right(); break;
      case 1: button_up(); break;
      case 2: button_down(); break;
      case 3: button_left(); break;
    }
  }
  
  
}
