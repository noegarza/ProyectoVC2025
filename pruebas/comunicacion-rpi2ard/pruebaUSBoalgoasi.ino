/**
 * @file pruebaUSBoalgoasi.ino
 * @brief Ejemplo de recepción de comandos seriales en Arduino enviados desde una Raspberry Pi.
 *
 * Este código demuestra cómo un Arduino puede recibir comandos a través del puerto serial,
 * enviados por una Raspberry Pi, para controlar el estado de tres LEDs conectados a los pines 8, 9 y 10.
 * Dependiendo del comando recibido ('1', '2', '3' para encender cada LED individualmente, y 'a' para apagar todos),
 * el Arduino realiza la acción correspondiente y envía una confirmación por el mismo canal serial.
 *
 * El propósito principal de este ejemplo es mostrar la interacción básica entre una Raspberry Pi y un Arduino
 * mediante comunicación serial, permitiendo el control remoto de dispositivos conectados al Arduino.
 */
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
