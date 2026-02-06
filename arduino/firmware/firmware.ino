/*******************************************************
 * Projeto: Leitura de sensores + protocolo Serial + alerta
 *
 * Sensores:
 *  - MQ7 (A0) e MQ2 (A1)
 *  - DHT22 (pino 2)
 *
 * Comandos via Serial:
 *  "#01" : solicita leitura
 *  "#02" : estado normal
 *  "#03" : estado anormal
 *
 * Saída:
 *  LEITURA|ID=n|MQ7=|MQ2=|T=|U=|S=
 *
 * A leitura só é enviada quando solicitada (#01)
 * Existe um intervalo mínimo entre leituras
 *******************************************************/

#include <DHT.h>
#define DHTTYPE DHT22

// -------------------------
// Mapeamento de hardware
// -------------------------
const int PIN_MQ7 = A0;
const int PIN_MQ2 = A1;
const int PIN_DHT = 2;

DHT dht(PIN_DHT, DHTTYPE);

// Atuadores
const int PIN_LED_VERDE = 3;
const int PIN_BUZZER    = 4;

// -------------------------
// Comandos Serial
// -------------------------
const String CMD_ENVIAR_LEITURA = "#01";
const String CMD_ALERTA_NORMAL  = "#02";
const String CMD_ALERTA_ANORMAL = "#03";

// -------------------------
// Controle de leitura
// -------------------------
unsigned long ultimoEnvioLeituraMs = 0;
const unsigned long intervaloLeituraMs = 2000;
bool leituraPendente = false;

// -------------------------
// Controle do alarme
// -------------------------
bool alarmeAtivo = false;
bool buzzerLigado = false;

unsigned long tempoUltimoBuzzerMs = 0;
const unsigned long intervaloBuzzerMs = 3000;

// -------------------------
// Identificador da leitura
// -------------------------
int idLeitura = 0;

/*
 * Lê os sensores e envia a mensagem no formato esperado pelo PC.
 *
 * Essa função apenas executa a leitura quando chamada.
 * O controle de quando medir acontece no loop.
 */
void enviarLeitura() {

  int leituraMq7 = analogRead(PIN_MQ7);
  int leituraMq2 = analogRead(PIN_MQ2);

  float leituraTemperatura = dht.readTemperature();
  float leituraUmidade     = dht.readHumidity();

  String statusLeitura = "OK";
  String temperaturaStr = String(leituraTemperatura, 2);
  String umidadeStr     = String(leituraUmidade, 2);

  if (isnan(leituraTemperatura) || isnan(leituraUmidade)) {
    statusLeitura = "DHT_FAIL";
    temperaturaStr = "NA";
    umidadeStr = "NA";
  }

  String mensagem = "LEITURA|ID=" + String(idLeitura)
                    + "|MQ7=" + String(leituraMq7)
                    + "|MQ2=" + String(leituraMq2)
                    + "|T="   + temperaturaStr
                    + "|U="   + umidadeStr
                    + "|S="   + statusLeitura;

  Serial.println(mensagem);
}

// -------------------------
// Estado normal
// -------------------------
void alertaNormal() {
  noTone(PIN_BUZZER);
  digitalWrite(PIN_LED_VERDE, HIGH);
  alarmeAtivo = false;
  buzzerLigado = false;
}

// -------------------------
// Estado de alarme
// -------------------------
void alertaAnormal() {
  digitalWrite(PIN_LED_VERDE, LOW);
  alarmeAtivo = true;
  tempoUltimoBuzzerMs = millis();
  buzzerLigado = false;
}

void setup() {
  Serial.begin(9600);
  dht.begin();

  pinMode(PIN_LED_VERDE, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);

  // Começa sempre em estado normal
  alertaNormal();
}

void loop() {

  // -------------------------
  // Controle do buzzer
  // -------------------------
  if (alarmeAtivo) {
    unsigned long agora = millis();
    if (agora - tempoUltimoBuzzerMs >= intervaloBuzzerMs) {
      tempoUltimoBuzzerMs = agora;

      if (buzzerLigado) {
        noTone(PIN_BUZZER);
        buzzerLigado = false;
      } else {
        tone(PIN_BUZZER, 4500);
        buzzerLigado = true;
      }
    }
  }

  // -------------------------
  // Leitura de comandos
  // -------------------------
  if (Serial.available() > 0) {
    String comandoSerial = Serial.readStringUntil('\n');
    comandoSerial.trim();

    if (comandoSerial == CMD_ENVIAR_LEITURA) {
      leituraPendente = true;
    }

    if (comandoSerial == CMD_ALERTA_NORMAL) {
      alertaNormal();
    }

    if (comandoSerial == CMD_ALERTA_ANORMAL) {
      if (!alarmeAtivo) {
        alertaAnormal();
      }
    }
  }

  // -------------------------
  // Envio da leitura
  // -------------------------
  unsigned long agora = millis();
  if (leituraPendente && (agora - ultimoEnvioLeituraMs >= intervaloLeituraMs)) {
    ultimoEnvioLeituraMs = agora;
    idLeitura++;
    enviarLeitura();
    leituraPendente = false;
  }
}
