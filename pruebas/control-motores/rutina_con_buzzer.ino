// === Pines Motores Puente H1 ===
#define ENA   3 // Motor 1 (lado izquierdo enfrente) rojo
#define IN1   2 // café  
#define IN2   4 // verde

#define ENB   5 // Motor 2 (lado derecho enfrente) azul
#define IN3   7 // naranja
#define IN4   8 // amarillo

// === Pines Motores Puente H2 ===
#define ENA2  6  // Motor 3 (lado izquierdo atrás) rojo
#define IN5   9  // café
#define IN6   10 // gris 

#define ENB2  11 // Motor 4 (lado derecho atrás) azul
#define IN7   12 // verde
#define IN8   13 // morado

// === Sensor ultrasónico ===
#define TRIG A0
#define ECHO A1
#define BUZZERLED A2

bool iniciado = false;
int difVel = 10;
int tGiroMs = 800;
long distancia;
const int tiempoAvance = 200;

// --- Funciones de control ---
void motorControl(int EN, int INa, int INb, int velocidad, bool adelante) {
  if (adelante) {
    digitalWrite(INa, HIGH);
    digitalWrite(INb, LOW);
  } else {
    digitalWrite(INa, LOW);
    digitalWrite(INb, HIGH);
  }
  analogWrite(EN, velocidad);
}

void adelante(int vel) {
  motorControl(ENA, IN1, IN2, vel-difVel, true);
  motorControl(ENA2, IN5, IN6, vel, true);
  motorControl(ENB, IN3, IN4, vel, true);
  motorControl(ENB2, IN7, IN8, vel-difVel, true);
}

void atras(int vel) {
  motorControl(ENA, IN1, IN2, vel-difVel, false);
  motorControl(ENA2, IN5, IN6, vel, false);
  motorControl(ENB, IN3, IN4, vel, false);
  motorControl(ENB2, IN7, IN8, vel-difVel, false);
}

void derecha(int vel) {
  motorControl(ENA, IN1, IN2, vel, true);
  motorControl(ENA2, IN5, IN6, 0, true);
  motorControl(ENB, IN3, IN4, 0, false);
  motorControl(ENB2, IN7, IN8, vel, true);
  
}

void izquierda(int vel) {
  motorControl(ENA, IN1, IN2, 0, false);
  motorControl(ENA2, IN5, IN6, vel, true);
  motorControl(ENB, IN3, IN4, vel, true);
  motorControl(ENB2, IN7, IN8, 0, true);
}

void detener() {
  motorControl(ENA, IN1, IN2, 0, true);
  motorControl(ENA2, IN5, IN6, 0, true);
  motorControl(ENB, IN3, IN4, 0, true);
  motorControl(ENB2, IN7, IN8, 0, true);
}

// --- Medir distancia ---
long medirDistancia() {
  digitalWrite(TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG, LOW);

  long duracion = pulseIn(ECHO, HIGH, 30000); // timeout 30ms
  distancia = duracion * 0.034 / 2;      // en cm
  return distancia;
}

// --- Evasión de obstáculos ---
void detenerseSiHayObstaculo() {
    // con IA gernerativa
  long d = medirDistancia();

  while (d > 0 && d < 40) {

    detener();

    delay(100);
    analogWrite(A2, 1023);

    d = medirDistancia();

  }

    analogWrite(A2, 0);

}

void setup() {
  Serial.begin(9600);
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(IN5, OUTPUT); pinMode(IN6, OUTPUT);
  pinMode(IN7, OUTPUT); pinMode(IN8, OUTPUT);
  pinMode(ENA, OUTPUT); pinMode(ENB, OUTPUT);
  pinMode(ENA2, OUTPUT); pinMode(ENB2, OUTPUT);
  pinMode(TRIG, OUTPUT);
  pinMode(ECHO, INPUT);
  detener();
}

void loop() {
  if (!iniciado) {
    if (Serial.available() > 0) {
      char comando = Serial.read();
      if (comando == 'e') {
        iniciado = true;
        detener();
        Serial.println("Ejecución iniciada");
      }
    }
    return; // mientras no inicie, no hacer nada más
  }
  int vel = 150; // Velocidad base (0-255)
  
  

  for(int i = 0; i < 8; i++){
    derecha(vel);
    delay(tGiroMs);
    detenerseSiHayObstaculo();
    detener();
    delay(1000);
  }

  adelante(vel);
  delay(tiempoAvance);
  detenerseSiHayObstaculo();
  adelante(vel);
  delay(tiempoAvance);
  detenerseSiHayObstaculo();
  adelante(vel);
  delay(tiempoAvance);
  detenerseSiHayObstaculo();
  adelante(vel);
  delay(tiempoAvance);
  detenerseSiHayObstaculo();
  adelante(vel);
  delay(tiempoAvance);
  detenerseSiHayObstaculo();
  detener();
  delay(1000);

  for(int i = 0; i < 12; i++){
    detenerseSiHayObstaculo();
    derecha(vel);
    delay(tGiroMs);
    detener();
    delay(1000);
  }

  adelante(vel);
  delay(tiempoAvance);
  detenerseSiHayObstaculo();adelante(vel);
  delay(tiempoAvance);
  detenerseSiHayObstaculo();adelante(vel);
  delay(tiempoAvance);
  detenerseSiHayObstaculo();adelante(vel);
  delay(tiempoAvance);
  detenerseSiHayObstaculo();adelante(vel);
  delay(tiempoAvance);
  detenerseSiHayObstaculo();
  detener();
  delay(1000);

  if (Serial.available() > 0) {
      char comando = Serial.read();
      if (comando == 'x') {
        detener();
        iniciado = false;  // vuelve al modo de espera
        Serial.println("Ejecución detenida");
      }
    }
}