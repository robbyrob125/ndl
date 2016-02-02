#include <RCSwitch.h>
#include <LiquidCrystal.h>

RCSwitch sender = RCSwitch( );
LiquidCrystal lcd = LiquidCrystal(8 ,9 ,4 ,5 ,6 ,7);
#define CodeLength 24
#define SendPin A5

#define KEY_COUNT 4

int keyLimits [KEY_COUNT+1] = {100, 330, 580, 900, 1023};
int keyNames [KEY_COUNT+1] = {0, 1, 2, 3, 4};

const unsigned long OnCode[2] = {1381717, 1394005};
const unsigned long OffCode[2] = {1381716, 1394004};

void setup() {
  lcd.begin(16,2);
  Serial.begin(9600);
  Serial.println("RC receiver");
  mySwitch.enableReceive(0); // Receiver on interrupt 0 => that is pin #2

  pinMode(SendPin, OUTPUT);
  sender.enableTransmit(SendPin);
  sender.setProtocol(1);
  pinMode(13, OUTPUT);
}

void setSocket(int id, bool on) {
    sender.send((on ? OnCode : OffCode)[id], CodeLength);
    lcd.setCursor(0, id);
    lcd.print("Socket ");
    lcd.print(id);
    lcd.print(on ? " on" : " off");
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

void loop() {
  
  switch (check_button()) {
    case 0: button_right(); break;
    case 1: button_up(); break;
    case 2: button_down(); break;
    case 3: button_left(); break;
    
  }

}
