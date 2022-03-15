#include <AccelStepper.h>
#include <Servo.h>
#include <EEPROM.h>

Servo servo;

//U-Tung Motor

#define mot1dirPin 2
#define mot1stepPin 3

#define motorInterfaceType 1

//Speckle Imaging omotor

#define mot2dirPin 4
#define mot2stepPin 5

long stepper1_pos;
int stepper1_pos_loc = 0;

long stepper2_pos;
int stepper2_pos_loc = 0;

int tung = 6; byte tung_status;
int uar  = 7; byte uar_status;
int sol1 = 8; byte sol1_status; //Star-1
int sol2 = 9; byte sol2_status; //Calib
int sol3 = 10; byte sol3_status; //Star-2

int servo_pin = 11;


int interrupt_sens1 = A0; //U-Tung Homing sensor

int interrupt_sens2 = A1; //Speckle Imaging Homing sensor


// is_threshold = interrupt sensor threshold
int is_threshold1 = 600;  //U-Tung Homing sensor
int is_threshold2 = 600;  //Speckle Imaging Homing sensor

AccelStepper stepper1 = AccelStepper(motorInterfaceType, mot1stepPin, mot1dirPin);
AccelStepper stepper2 = AccelStepper(motorInterfaceType, mot2stepPin, mot2dirPin);


void go_to_home1(){
//  Serial.print("selecting lamp: UAr ");
  stepper1.setSpeed(4000);
  while(sensor1() < is_threshold1){
//    Serial.print(".");
    stepper1.move(-1000);
    stepper1.runSpeedToPosition();
  }
  stepper1.setCurrentPosition(0);
//  Serial.println();
}

int sensor1(){
  return analogRead(interrupt_sens1);
}

void save_stepper1_pos(long pos){
  EEPROM.put(stepper1_pos_loc, pos);
}




void go_to_home2(){
//  Serial.print("selecting Non Speckle position");
  stepper2.setSpeed(4000);
  while(sensor2() < is_threshold2){
//    Serial.print(".");
    stepper2.move(-1000);
    stepper2.runSpeedToPosition();
  }
  stepper2.setCurrentPosition(0);
//  Serial.println();
}

int sensor2(){
  return analogRead(interrupt_sens2);
}

void save_stepper2_pos(long pos){
  EEPROM.put(stepper2_pos_loc, pos);
}




void setup() {

  if(EEPROM.read(1023) != 123){
    // Serial.println("EEPROM not written!");
    EEPROM.write(1023, 123);
    go_to_home1();
    stepper1_pos = 0;
    EEPROM.put(stepper1_pos_loc, 0);

    go_to_home2();
    stepper2_pos = 0;
    EEPROM.put(stepper2_pos_loc, 0);
    
  }else{
     // Serial.println("EEPROM settings found :)");
    EEPROM.get(stepper1_pos_loc, stepper1_pos);
    stepper1.setCurrentPosition(stepper1_pos);
    
    EEPROM.get(stepper2_pos_loc, stepper2_pos);
    stepper1.setCurrentPosition(stepper2_pos);
  }


  Serial.begin(115200);
  while(!Serial);

  servo.attach(servo_pin);
  servo.write(0);
  
  pinMode(sol1, OUTPUT);    
  pinMode(sol2, OUTPUT);  
  pinMode(sol3, OUTPUT);  
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
  EEPROM.get(15, sol3_status);

  if (tung_status == 0) digitalWrite(tung, LOW); else digitalWrite(tung, HIGH);
  if (uar_status  == 0) digitalWrite(uar, LOW);  else digitalWrite(uar, HIGH);
  if (sol1_status == 0) digitalWrite(sol1, LOW); else digitalWrite(sol1, HIGH);
  if (sol2_status == 0) digitalWrite(sol2, LOW); else digitalWrite(sol2, HIGH);
  if (sol3_status == 0) digitalWrite(sol3, LOW); else digitalWrite(sol3, HIGH);



  stepper1.setMaxSpeed(2000);
  stepper1.setAcceleration(500);

   stepper2.setMaxSpeed(2000);
  stepper2.setAcceleration(500);
}



void loop() {
  
  while (Serial.available() > 0) {
    
    String str = Serial.readString();
    str.trim();
    
    if(str.equals("is1")){
      Serial.print("sensor1 val: ");
      Serial.println(sensor1());
    }
    else if(str.equals("home1")){
      go_to_home1();
      Serial.println("done");
    }

    else if(str.startsWith("ma1")){
      long int pos = str.substring(2).toInt();
      stepper1.moveTo(pos);
      
      while(true){
        if (sensor1() > is_threshold1){
          stepper1.setCurrentPosition(0);
          break;
        }
        stepper1.run();
      }
      Serial.println("done");
    }
    else if(str.equals("uar")){
//      stepper.moveTo(0);
//      stepper.runToPosition();
      save_stepper1_pos(0);
      go_to_home1();
      Serial.println("uar");  
    }
    else if(str.equals("tung")){
      stepper1.moveTo(19000);
      stepper1.runToPosition();
      save_stepper1_pos(19000);
      Serial.println("tung");
    }
    else if(str.equals("fabry")){
      stepper1.moveTo(38000);
      stepper1.runToPosition();
      save_stepper1_pos(38000);
      Serial.println("fabry");
    }

    else if(str.equals("is2")){
      Serial.print("sensor2 val: ");
      Serial.println(sensor2());
    }
    else if(str.equals("home2")){
      go_to_home2();
      Serial.println("done");
    }

    else if(str.startsWith("ma2")){
      long int pos = str.substring(2).toInt();
      stepper1.moveTo(pos);
      
      while(true){
        if (sensor2() > is_threshold2){
          stepper1.setCurrentPosition(0);
          break;
        }
        stepper2.run();
      }
      Serial.println("done");
    }
    else if(str.equals("nonspec")){
//      stepper.moveTo(0);
//      stepper.runToPosition();
      save_stepper2_pos(0);
      go_to_home1();
      Serial.println("nonspec");  
    }
    else if(str.equals("spec")){
      stepper2.moveTo(19000);
      stepper2.runToPosition();
      save_stepper2_pos(19000);
      Serial.println("spec");
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
      else if(str.equals("sol3")){
      digitalWrite(sol3, !digitalRead(sol3));
      Serial.println(digitalRead(sol3));
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
       Serial.print(digitalRead(sol3));

      // nd filter status
      if ( servo.read() == 0){        
        Serial.print(0);
      }
      else{
        Serial.print(1);
      }
      
      // lamp position status
      if(stepper1_pos == 0){
        Serial.println(1);
      }
      else if(stepper1_pos == 19000){
        Serial.println(2);
      }
      else{
        Serial.println(3);
      }

      // speckle Imaging postion

           if(stepper2_pos == 0){
        Serial.println(4);
      }
      else{
        Serial.println(5);
      }
    }
    
    else if(str.equals("allrelayon")){
      digitalWrite(uar, LOW);  delay(100);
      digitalWrite(tung, LOW); delay(100);
      digitalWrite(sol1, LOW); delay(100);
      digitalWrite(sol2, LOW); delay(100);
      digitalWrite(sol3, LOW);
      Serial.println("done");
    }
    else if(str.equals("allrelayoff")){
      digitalWrite(uar, HIGH);  delay(100);
      digitalWrite(tung, HIGH); delay(100);
      digitalWrite(sol1, HIGH); delay(100);
      digitalWrite(sol2, HIGH); delay(100);
      digitalWrite(sol3, HIGH);
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
      EEPROM.put(15, byte(digitalRead(sol3)) );
      Serial.println("done");
    }
    else{
      Serial.print("Invalid cmd ! : ");
      Serial.println(str);
    }
  }
}
