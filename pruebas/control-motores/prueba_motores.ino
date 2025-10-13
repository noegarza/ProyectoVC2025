// Pines Motores Puente H1
#define ENA   3 // Motor 1 (lado izquierdo enfrente) rojo
#define IN1   2 // café  
#define IN2   4 // verde

#define ENB   5 // Motor 2 (lado derecho enfrente) azul
#define IN3   7 // naranja
#define IN4   8 // amarillo

// Pines Motores Puente H2
#define ENA2  6  // Motor 3 (lado izquierdo atrás) rojo
#define IN5   9  // café
#define IN6   10 // morado 

#define ENB2  11 // Motor 4 (lado derecho atrás) azul
#define IN7   12 // verde
#define IN8   13 // morado


// --- Funciones de movimiento ---
void adelante() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  digitalWrite(IN5, HIGH);
  digitalWrite(IN6, LOW);
  digitalWrite(IN7, HIGH);
  digitalWrite(IN8, LOW);
}

void atras() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  digitalWrite(IN5, LOW);
  digitalWrite(IN6, HIGH);
  digitalWrite(IN7, LOW);
  digitalWrite(IN8, HIGH);
}

void izquierda() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  digitalWrite(IN5, LOW);
  digitalWrite(IN6, HIGH);
  digitalWrite(IN7, HIGH);
  digitalWrite(IN8, LOW);
}

void derecha() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  digitalWrite(IN5, HIGH);
  digitalWrite(IN6, LOW);
  digitalWrite(IN7, LOW);
  digitalWrite(IN8, HIGH);
}

void detener() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);

  digitalWrite(IN5, LOW);
  digitalWrite(IN6, LOW);
  digitalWrite(IN7, LOW);
  digitalWrite(IN8, LOW);
}

void setup() {
  // Configurar pines como salida
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  pinMode(IN5, OUTPUT);
  pinMode(IN6, OUTPUT);
  pinMode(IN7, OUTPUT);
  pinMode(IN8, OUTPUT);
  pinMode(ENA2, OUTPUT);
  pinMode(ENB2, OUTPUT);

  Serial.begin(9600);

  detener(); // para que al inicio esté detenido

  // Velocidad inicial (0-255)
  analogWrite(ENA, 200);
  analogWrite(ENB, 200);
  analogWrite(ENA2, 200);
  analogWrite(ENB2, 200);
}

void loop() {
  if (Serial.available() > 0) {
    char comando = Serial.read();

    if (comando == '1') {
      adelante();
      
    } else if (comando == '2') {
      atras();
      
    } else if (comando == '3') {
      derecha();
      
    } else if (comando == '4') {
      izquierda();
      
    } else if (comando == '5'){
      detener();
    }
  }
}



