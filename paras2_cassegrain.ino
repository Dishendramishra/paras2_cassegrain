#include <AccelStepper.h>
#include <Servo.h>

Servo servo;

int dirPin = 2;
int stepPin = 3;
int motorInterfaceType = 1;

int tung = 5;
int uar  = 6;
int sol1 = 7;
int sol2 = 8;
int servo_pin = 9;

int interrupt_sens = A0;
int is_threshold = 600;

int hom = 0;

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

void setup() {
  servo.attach(servo_pin);
  servo.write(0);
  Serial.begin(115200);

  pinMode(sol1, OUTPUT);    
  pinMode(sol2, OUTPUT);    
  pinMode(tung, OUTPUT);    
  pinMode(uar, OUTPUT);    
  
  digitalWrite(sol1,HIGH);
  digitalWrite(sol2,HIGH);
  digitalWrite(tung,HIGH);
  digitalWrite(uar,HIGH);
  
  stepper.setMaxSpeed(2000);
  stepper.setAcceleration(500);
//  go_to_home();
}

void loop() {
  
  while (Serial.available() > 0) {
    
    String str = Serial.readString();
    
    if(str.startsWith("is")){
      Serial.print("sensor val: ");
      Serial.println(sensor());
    }
    else if(str.startsWith("home")){
      go_to_home();
      Serial.println("done");
    }
    else if(str.startsWith("ma")){
      long int pos = str.substring(2).toInt();
//      if ( pos<=0 && sensor()> is_threshold){
//        Serial.print("Already at home/UAr (limit position)!");
//      }
//      else{
        stepper.moveTo(pos);
        stepper.runToPosition();
        Serial.println("done");
//      }
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
//      Serial.print("Moving degrees: ");
//      Serial.print(angle);
//      Serial.print(" ... ");
      servo.write(angle);
      Serial.println("done");
    }
    else if(str.startsWith("sol1")){
      digitalWrite(sol1, !digitalRead(sol1));
      Serial.println("done");
    }
    else if(str.startsWith("sol2")){
      digitalWrite(sol2, !digitalRead(sol2));   
      Serial.println("done");
    }
    else if(str.startsWith("tung")){
      digitalWrite(tung, !digitalRead(tung));
      Serial.println("done");
    }
    else if(str.startsWith("allrelay")){
      digitalWrite(uar, HIGH);
      delay(100);
      digitalWrite(tung, HIGH);
      delay(100);
      digitalWrite(sol1, HIGH);
      delay(100);
      digitalWrite(sol2, HIGH);
      Serial.println("done");
    }
    else if(str.startsWith("uar")){
      digitalWrite(uar, !digitalRead(uar));   
      Serial.println("done");
    }
    else{
      Serial.println("Invalid Option!");
    }
  }
}
