# 📌 Sistema de Detecção de Anomalias

## 📖 Visão Geral

O **Sistema de Detecção de Anomalias** é um projeto de monitoramento ambiental desenvolvido em grupo, que integra **sensores físicos**, **Arduino**, **comunicação serial** e **Machine Learning** para identificar comportamentos anormais em tempo real e acionar alertas automáticos.

O sistema coleta dados de sensores de gás e ambiente, processa essas informações em uma aplicação Python e utiliza um modelo de detecção de anomalias para classificar o estado do ambiente como **normal** ou **anormal**, acionando alertas visuais e sonoros quando necessário.

---

## 🎯 Objetivo do Projeto

- Monitorar variáveis ambientais em tempo real  
- Detectar padrões anormais nos dados coletados  
- Emitir alertas automáticos em situações críticas  
- Aplicar conceitos de **IoT**, **processamento de dados** e **Machine Learning**  
- Servir como projeto acadêmico e de portfólio profissional  

---

## 🧠 Funcionalidades

- Leitura de sensores ambientais (MQ2, MQ7, DHT22)
- Comunicação serial entre Arduino e aplicação Python
- Conversão, validação e padronização dos dados recebidos
- Detecção de anomalias por modelo de Machine Learning
- Sistema de alerta com LED e buzzer
- Controle de estado para evitar alertas duplicados
- Registro das leituras e resultados de predição

---

## 🔧 Tecnologias Utilizadas

### Hardware
- Arduino
- Sensor MQ2 (Gás inflamável)
- Sensor MQ7 (Monóxido de Carbono)
- Sensor DHT22 (Temperatura e Umidade)
- LED
- Buzzer

### Software
- Arduino (C/C++)
- Python
- Comunicação Serial
- Machine Learning (Detecção de Anomalias)
- Git e GitHub

---

## 🏗️ Arquitetura do Sistema

1. O Arduino realiza a leitura dos sensores
2. Os dados são enviados via comunicação serial
3. A aplicação Python recebe e trata os dados
4. Os dados são padronizados conforme o modelo treinado
5. O modelo de Machine Learning classifica o estado do ambiente
6. Em caso de anomalia, o sistema aciona alertas físicos (LED e buzzer)

