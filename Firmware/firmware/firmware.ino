#include <DHT.h>
#define DHTTYPE DHT22

const int MQ7 = A0;
const int MQ2 = A1;
DHT dht(2, DHTTYPE);
const int Led_Verde = 3;
const int Buzzer = 4;

const String CMD_ENVIAR_LEITURA = "#01";
const String CMD_ALERTA_NORMAL = "#02";
const String CMD_ALERTA_ANORMAL = "#03";

unsigned long TEMPO_LEITURA = 0;
unsigned long INTERVALO_LEITURA = 2000;
bool Leitura_Pendente = false;

bool alarmeAtivo = false;
bool buzzerLigado = false;

unsigned long tBuzzer = 0;
const unsigned long INTERVALO_Buzzer = 3000; // 3 segundos

int id_leitura = 0;

void inferencia(){

  int leitura_MQ7 = analogRead(MQ7);
  int leitura_MQ2 = analogRead(MQ2);
  float leitura_Temperatura = dht.readTemperature();
  float leitura_Umidade = dht.readHumidity();

  String status = "OK";
  String tStr = String(leitura_Temperatura,2);
  String uStr = String(leitura_Umidade,2);

  if (isnan(leitura_Temperatura) || isnan(leitura_Umidade)){
    status = "DHT_FAIL";
    tStr = "NA";
    uStr = "NA";
  }

  String mensagem = "LEITURA|ID=" + String(id_leitura)
                    + "|MQ7="  + String(leitura_MQ7) 
                    + "|MQ2=" + String(leitura_MQ2) 
                    + "|T=" + tStr 
                    + "|U=" + uStr 
                    + "|S=" + status;

  Serial.println(mensagem);
  }





void alerta_normal(){
  noTone(Buzzer);
  digitalWrite(Led_Verde,HIGH);
  alarmeAtivo = false;
  buzzerLigado = false;
}

void alerta_anormal(){
  digitalWrite(Led_Verde,LOW);
  alarmeAtivo = true;
  tBuzzer = millis();
  buzzerLigado = false;
}


void setup() {
  Serial.begin(9600);
  dht.begin();
  pinMode(Led_Verde, OUTPUT);
  pinMode(Buzzer, OUTPUT);

  alerta_normal();
}

void loop() {

  if(alarmeAtivo){
    unsigned long agora = millis();
    if (agora - tBuzzer >= INTERVALO_Buzzer){
      tBuzzer = agora;
      if (buzzerLigado){
        noTone(Buzzer);
        buzzerLigado = false;
      } else {
        tone(Buzzer, 4500);
        buzzerLigado = true;
      }
    }
  }

  if(Serial.available()>0){
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if(cmd == CMD_ENVIAR_LEITURA){
      Leitura_Pendente = true;
    }

    if(cmd == CMD_ALERTA_NORMAL){
      alerta_normal();
    }

    if(cmd == CMD_ALERTA_ANORMAL){
      if(!alarmeAtivo){
        alerta_anormal();
      }
    }    
    

  } 
      unsigned long agora = millis();
      if(Leitura_Pendente && agora - TEMPO_LEITURA >= INTERVALO_LEITURA){
        TEMPO_LEITURA = agora;
        id_leitura = id_leitura + 1;
        inferencia();
        Leitura_Pendente = false;
      }
  
}
