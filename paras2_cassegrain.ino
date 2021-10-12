#include <AccelStepper.h>
#include <Servo.h>
#include <EEPROM.h>

Servo servo;

int dirPin = 2;
int stepPin = 3;
int motorInterfaceType = 1;

long stepper_pos;
int stepper_pos_loc = 0;

int tung = 5; byte tung_status;
int uar  = 6; byte uar_status;
int sol1 = 7; byte sol1_status;
int sol2 = 8; byte sol2_status;

int servo_pin = 9;
int interrupt_sens = A0;

// is_threshold = interrupt sensor threshold
int is_threshold = 600; 

AccelStepper stepper = AccelStepper(motorInterfaceType, stepPin, dirPin);

void go_to_home(){
  Serial.print("selecting lamp: UAr ");
  stepper.setSpeed(4000);
  while(sensor() < is_threshold){
    Serial.print(".");
    stepper.move(-1000);
    stepper.runSpeedToPosition();
  }
  stepper.setCurrentPosition(0);
  Serial.println();
}

int sensor(){
  return analogRead(interrupt_sens);
}

void save_stepper_pos(long pos){
  EEPROM.put(stepper_pos_loc, pos);
}

void setup() {

  if(EEPROM.read(1023) != 123){
    // Serial.println("EEPROM not written!");
    EEPROM.write(1023, 123);
    go_to_home();
    stepper_pos = 0;
    EEPROM.put(stepper_pos_loc, 0);
  }else{
     // Serial.println("EEPROM settings found :)");
    EEPROM.get(stepper_pos_loc, stepper_pos);
    stepper.setCurrentPosition(stepper_pos);
  }

  servo.attach(servo_pin);
  Serial.begin(115200);
  while(!Serial);

  pinMode(sol1, OUTPUT);    
  pinMode(sol2, OUTPUT);    
  pinMode(tung, OUTPUT);    
  pinMode(uar,  OUTPUT);    
  
  // digitalWrite(sol1, HIGH);
  // digitalWrite(sol2, HIGH);
  // digitalWrite(tung, HIGH);
  // digitalWrite(uar,  HIGH);
  
  EEPROM.get(11, tung_status);
  EEPROM.get(12, uar_status);
  EEPROM.get(13, sol1_status);
  EEPROM.get(14, sol2_status);

  if (tung_status == 0) digitalWrite(tung, LOW); else digitalWrite(tung, HIGH);
  if (uar_status  == 0) digitalWrite(uar, LOW);  else digitalWrite(uar, HIGH);
  if (sol1_status == 0) digitalWrite(sol1, LOW); else digitalWrite(sol1, HIGH);
  if (sol2_status == 0) digitalWrite(sol2, LOW); else digitalWrite(sol2, HIGH);


  stepper.setMaxSpeed(2000);
  stepper.setAcceleration(500);
}

void loop() {
  
  while (Serial.available() > 0) {
    
    String str = Serial.readString();
    str.trim();
    
    if(str.equals("is")){
      Serial.print("sensor val: ");
      Serial.println(sensor());
    }
    else if(str.equals("home")){
      go_to_home();
      Serial.println("done");
    }
    else if(str.startsWith("ma")){
      long int pos = str.substring(2).toInt();
      stepper.moveTo(pos);
      
      while(true){
        if (sensor() > is_threshold){
          stepper.setCurrentPosition(0);
          break;
        }
        stepper.run();
      }
      Serial.println("done");
    }
    else if(str.equals("uar")){
      stepper.moveTo(0);
      stepper.runToPosition();
      save_stepper_pos(0);
      Serial.println("uar");  
    }
    else if(str.equals("tung")){
      stepper.moveTo(19000);
      stepper.runToPosition();
      save_stepper_pos(19000);
      Serial.println("tung");
    }
    else if(str.equals("fabry")){
      stepper.moveTo(38000);
      stepper.runToPosition();
      save_stepper_pos(38000);
      Serial.println("fabry");
    }
//    else if (str.startsWith("mr")){
//      stepper.setSpeed(2000);
//      long int pos = str.substring(2).toInt();
//      Serial.print("mr: "); Serial.println(pos);
//      stepper.move(pos);
//      stepper.runSpeedToPosition();
//      while (stepper.currentPosition() != stepper.targetPosition()) {
//        Serial.print("current pos:"); Serial.println(stepper.currentPosition());
//        Serial.print("target pos:");  Serial.println(stepper.targetPosition());
//        stepper.runSpeedToPosition();
//      }
//    }
    else if(str.startsWith("nd")){
      int angle = str.substring(2).toInt();
      servo.write(angle);
      Serial.println("done");
    }
    else if(str.equals("sol1")){
      digitalWrite(sol1, !digitalRead(sol1));
      Serial.println(digitalRead(sol1));
    }
    else if(str.equals("sol2")){
      digitalWrite(sol2, !digitalRead(sol2));
      Serial.println(digitalRead(sol2));
    }
    else if(str.equals("tung_relay")){
      digitalWrite(tung, !digitalRead(tung));
      Serial.println(digitalRead(tung));
    }
    else if(str.equals("uar_relay")){
      digitalWrite(uar, !digitalRead(uar));
      Serial.println(digitalRead(uar));
    }
    else if(str.equals("status")){

      // returns 0 0 0 0 0 0 
      //         |-----| | |
      //         relays  | lamp_position
      //                 |
      //              nd_filter

      //  relays status
      Serial.print(digitalRead(uar));
      Serial.print(digitalRead(tung));
      Serial.print(digitalRead(sol1));
      Serial.print(digitalRead(sol2));

      // nd filter status
      if ( servo.read() == 0){        
        Serial.print(0);
      }
      else{
        Serial.print(1);
      }
      
      // lamp position status
      if(stepper_pos == 0){
        Serial.println(1);
      }
      else if(stepper_pos == 19000){
        Serial.println(2);
      }
      else{
        Serial.println(3);
      }
    }
    else if(str.equals("allrelayon")){
      digitalWrite(uar, LOW);  delay(100);
      digitalWrite(tung, LOW); delay(100);
      digitalWrite(sol1, LOW); delay(100);
      digitalWrite(sol2, LOW);
      Serial.println("done");
    }
    else if(str.equals("allrelayoff")){
      digitalWrite(uar, HIGH);  delay(100);
      digitalWrite(tung, HIGH); delay(100);
      digitalWrite(sol1, HIGH); delay(100);
      digitalWrite(sol2, HIGH);
      Serial.println("done");
    }
    else if(str.equals("clear")){
      for (int i = 0 ; i < EEPROM.length() ; i++) {
        EEPROM.write(i, 0);
      }
      Serial.println("EEPROM cleared!");
    }
    else if(str.equals("save_relays")){
      EEPROM.put(11, byte(digitalRead(tung)) );
      EEPROM.put(12, byte(digitalRead(uar))  );
      EEPROM.put(13, byte(digitalRead(sol1)) );
      EEPROM.put(14, byte(digitalRead(sol2)) );
      Serial.println("done");
    }
    else{
      Serial.print("Invalid cmd ! : ");
      Serial.println(str);
    }
  }
}
