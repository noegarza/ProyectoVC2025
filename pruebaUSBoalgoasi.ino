/*Hecho con chat GPT*/

int led1 = 8;
int led2 = 9;
int led3 = 10;

void setup() {
  pinMode(led1, OUTPUT);
  pinMode(led2, OUTPUT);
  pinMode(led3, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();

    if (comando == '1') {
      digitalWrite(led1, HIGH);
      Serial.println("LED1 encendido");
    } else if (comando == '2') {
      digitalWrite(led2, HIGH);
      Serial.println("LED2 encendido");
    } else if (comando == '3') {
      digitalWrite(led3, HIGH);
      Serial.println("LED3 encendido");
    } else if (comando == 'a') {
      digitalWrite(led1, LOW);
      digitalWrite(led2, LOW);
      digitalWrite(led3, LOW);
      Serial.println("Todos apagados");
    }
  }
}
