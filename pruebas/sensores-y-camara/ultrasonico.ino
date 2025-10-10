// Pines del sensor
const int TRIG_PIN = A0;
const int ECHO_PIN = A1;

void setup() {
  Serial.begin(9600);          // Velocidad del monitor serie
  pinMode(TRIG_PIN, OUTPUT);   // Trig como salida
  pinMode(ECHO_PIN, INPUT);    // Echo como entrada
}

void loop() {
  // Enviar pulso de 10 microsegundos en TRIG
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Medir el tiempo del eco en microsegundos
  long duracion = pulseIn(ECHO_PIN, HIGH);

  // Calcular distancia en centímetros
  float distancia = duracion * 0.0343 / 2; // (vel. sonido 343 m/s)

  // Mostrar en el monitor serie
  Serial.print("Distancia: ");
  Serial.print(distancia);
  Serial.println(" cm");

  delay(500); // Medio segundo entre lecturas
}
