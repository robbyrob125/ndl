
#include <RCSwitch.h>
#include <LiquidCrystal.h>

RCSwitch mySwitch = RCSwitch( );
RCSwitch sender = RCSwitch( );
LiquidCrystal lcd = LiquidCrystal(8 ,9 ,4 ,5 ,6 ,7);
#define OnCode1 1381717
#define OffCode1 1381716
#define OnCode2 1394005
#define OffCode2 1394004
#define CodeLength 24
#define SendPin A5

#define KEY_COUNT 4

int keyLimits [KEY_COUNT+1] = {100, 330, 580, 900, 1023};
int keyNames [KEY_COUNT+1] = {0, 1, 2, 3, 4};

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

void button_left(){
    sender.send(OffCode1, CodeLength);
    sender.send(OnCode2, CodeLength);
}

void button_right(){
   sender.send(OnCode1, CodeLength);
   sender.send(OffCode2, CodeLength);
}

void button_up(){
  sender.send(OnCode1, CodeLength);
  sender.send(OnCode2, CodeLength);
}

void button_down(){
  sender.send(OffCode1, CodeLength);
  sender.send(OffCode2, CodeLength);
}

int check_button(){
  int val = analogRead(A0);
  lcd.setCursor(0,0);
  lcd.print(val); 
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
