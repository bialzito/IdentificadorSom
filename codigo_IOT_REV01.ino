#include <WiFi.h>
#include <WebServer.h>
#include <driver/i2s.h>

const char* ssid = "Casa 2.4";
const char* password = "luandavi2131";

const int ledPin = 22;
WebServer server(80);

// Pinos do microfone INMP441
#define I2S_SCK 26      // Clock
#define I2S_WS 25       // Word Select
#define I2S_SD 33       // Serial Data (entrada)
#define I2S_PORT I2S_NUM_0

// Buffer pequeno para 1 segundo (16000 amostras)
const int BUFFER_SIZE = 34000;
int16_t audioBuffer[BUFFER_SIZE];
int bufferIndex = 0;

// Função para configurar o I2S
void setupI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 1024,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_SCK,
        .ws_io_num = I2S_WS,
        .data_out_num = -1,
        .data_in_num = I2S_SD
    };

    i2s_set_pin(I2S_PORT, &pin_config);
    Serial.println("I2S configurado!");
}

// Função para gravar áudio
void recordAudio() {
    bufferIndex = 0;
    Serial.println("Iniciando gravação");

    unsigned long startTime = millis();
    
    // Grava enquanto não atingir 1 segundo
    while (millis() - startTime < 2000 && bufferIndex < BUFFER_SIZE - 512) {
        size_t bytesRead = 0;
        
        // Ler dados do microfone (512 amostras por vez)
        i2s_read(I2S_PORT, (void*)&audioBuffer[bufferIndex], 512 * sizeof(int16_t), &bytesRead, portMAX_DELAY);
        
        // Atualizar índice
        bufferIndex += bytesRead / sizeof(int16_t);
    }

    Serial.print("Gravação concluída! Amostras: ");
    Serial.println(bufferIndex);
}

// Rota para iniciar gravação
void handleRecord() {
    recordAudio();
    server.send(200, "text/plain", "Gravacao concluida!");
}

// Rota para verificar se há áudio gravado
void handleStatus() {
    if (bufferIndex > 0) {
        server.send(200, "text/plain", "ok");
    } else {
        server.send(200, "text/plain", "vazio");
    }
}

// Rota para enviar áudio em formato WAV
void handleAudio() {
    // Verificar se há áudio gravado
    if (bufferIndex == 0) {
        Serial.println("Erro: Nenhum audio gravado");
        server.send(404, "text/plain", "Nenhum audio gravado");
        return;
    }

    Serial.print("Enviando audio. Amostras: ");
    Serial.println(bufferIndex);

    // Calcular tamanho dos dados
    uint32_t dataSize = bufferIndex * 2;  // 2 bytes por amostra
    uint32_t fileSize = 36 + dataSize;

    // Configurar headers HTTP
    server.sendHeader("Content-Type", "audio/wav");
    server.sendHeader("Content-Length", String(44 + dataSize));
    server.sendHeader("Content-Disposition", "inline; filename=\"audio.wav\"");
    server.setContentLength(44 + dataSize);

    // Iniciar resposta
    WiFiClient client = server.client();

    // ===== CABEÇALHO WAV =====
    // "RIFF"
    client.write((const uint8_t*)"RIFF", 4);
    
    // Tamanho do arquivo - 8
    uint32_t riffSize = fileSize;
    client.write((uint8_t*)&riffSize, 4);
    
    // "WAVE"
    client.write((const uint8_t*)"WAVE", 4);

    // ===== SUBCHUNK1 (fmt) =====
    // "fmt "
    client.write((const uint8_t*)"fmt ", 4);
    
    // Tamanho do subchunk1
    uint32_t subchunk1Size = 16;
    client.write((uint8_t*)&subchunk1Size, 4);
    
    // Formato de áudio (1 = PCM)
    uint16_t audioFormat = 1;
    client.write((uint8_t*)&audioFormat, 2);
    
    // Número de canais (1 = mono)
    uint16_t numChannels = 1;
    client.write((uint8_t*)&numChannels, 2);
    
    // Taxa de amostragem (16000 Hz)
    uint32_t sampleRate = 16000;
    client.write((uint8_t*)&sampleRate, 4);
    
    // Byte rate (16000 * 1 * 16 / 8 = 32000)
    uint32_t byteRate = 32000;
    client.write((uint8_t*)&byteRate, 4);
    
    // Block align (1 * 16 / 8 = 2)
    uint16_t blockAlign = 2;
    client.write((uint8_t*)&blockAlign, 2);
    
    // Bits por amostra
    uint16_t bitsPerSample = 16;
    client.write((uint8_t*)&bitsPerSample, 2);

    // ===== SUBCHUNK2 (data) =====
    // "data"
    client.write((const uint8_t*)"data", 4);
    
    // Tamanho dos dados
    uint32_t subchunk2Size = dataSize;
    client.write((uint8_t*)&subchunk2Size, 4);

    // Escrever dados de áudio
    client.write((const uint8_t*)audioBuffer, dataSize);

    Serial.println("Audio enviado com sucesso!");
}

// Página HTML com interface
void handleRoot() {
    
    String html =
        "<!DOCTYPE html>"
        "<html>"
        "<head>"
            "<meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>ESP32 - Audio</title>"
            "<style>"
                "* { margin: 0; padding: 0; box-sizing: border-box; }"
                "body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }"
                ".container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); max-width: 500px; width: 100%; }"
                "h1 { color: #333; margin-bottom: 20px; text-align: center; }"
                "h2 { color: #555; margin-top: 25px; margin-bottom: 15px; font-size: 18px; border-bottom: 2px solid #667eea; padding-bottom: 10px; }"
                ".status-box { background: #f8f9fa; padding: 15px; border-radius: 10px; margin-bottom: 20px; }"
                ".info { color: #666; margin: 10px 0; font-size: 14px; }"
                "button { width: 100%; padding: 12px 20px; font-size: 16px; font-weight: bold; cursor: pointer; border: none; border-radius: 8px; transition: all 0.3s; background: #e74c3c; color: white; margin: 20px 0; }"
                "button:hover { background: #c0392b; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(231, 76, 60, 0.4); }"
                "button:active { transform: translateY(0); }"
                "button:disabled { background: #95a5a6; cursor: not-allowed; }"
                "audio { width: 100%; margin: 20px 0; height: 40px; }"
                ".audio-container { background: #f8f9fa; padding: 15px; border-radius: 10px; }"
                "#status { margin-top: 10px; color: #667eea; font-weight: bold; text-align: center; }"
                ".download-btn { background: #27ae60; margin-top: 10px; }"
                ".download-btn:hover { background: #229954; }"
            "</style>"
        "</head>"
        "<body>"
            "<div class='container'>"
                "<h1>🎤 ESP32 - Microfone</h1>"

                "<div class='status-box'>"
                    "<h2>Gravador de Audio</h2>"
                    "<p style='color: #666; margin-bottom: 15px;'>Clique para gravar</p>"
                    "<button id='btnRecord' onclick='gravarAudio()'>🔴 Gravar Audio</button>"
                    "<div id='status'></div>"
                "</div>"

                "<div class='status-box'>"
                    "<h2>Reprodutor de Audio</h2>"
                    "<div class='audio-container'>"
                        "<audio id='audioPlayer' controls style='width: 100%;'>"
                            "<source id='audioSource' src='' type='audio/wav'>"
                            "Seu navegador nao suporta o elemento de audio."
                        "</audio>"
                        "<button class='download-btn' onclick='baixarAudio()'>⬇️ Baixar Audio</button>"
                    "</div>"
                "</div>"
            "</div>"

            "<script>"
                "function gravarAudio() {"
                    "const btn = document.getElementById('btnRecord');"
                    "const status = document.getElementById('status');"
                    "btn.disabled = true;"
                    "btn.textContent = '⏳ Gravando...';"
                    "status.textContent = 'Gravando...';"
                    ""
                    "fetch('/record')"
                        ".then(r => r.text())"
                        ".then(t => {"
                            "btn.disabled = false;"
                            "btn.textContent = '🔴 Gravar Audio';"
                            "status.textContent = '✅ ' + t;"
                            "atualizarPlayer();"
                            "setTimeout(() => { status.textContent = ''; }, 3000);"
                        "})"
                        ".catch(e => {"
                            "btn.disabled = false;"
                            "btn.textContent = '🔴 Gravar Audio';"
                            "status.textContent = '❌ Erro: ' + e;"
                        "});"
                "}"
                ""
                "function atualizarPlayer() {"
                    "const source = document.getElementById('audioSource');"
                    "const player = document.getElementById('audioPlayer');"
                    "source.src = '/audio?t=' + Date.now();"
                    "player.load();"
                "}"
                ""
                "function baixarAudio() {"
                    "const link = document.createElement('a');"
                    "link.href = '/audio';"
                    "link.download = 'audio.wav';"
                    "document.body.appendChild(link);"
                    "link.click();"
                    "document.body.removeChild(link);"
                "}"
            "</script>"
        "</body>"
        "</html>";

    server.send(200, "text/html", html);
}

void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("Iniciando ESP32...");

    // Configurar LED
    pinMode(ledPin, OUTPUT);
    digitalWrite(ledPin, LOW);

    // Configurar I2S (microfone)
    setupI2S();

    // Conectar ao WiFi
    Serial.print("Conectando ao WiFi");
    WiFi.begin(ssid, password);
    int tentativas = 0;
    while (WiFi.status() != WL_CONNECTED && tentativas < 40) {
        delay(250);
        Serial.print(".");
        tentativas++;
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("WiFi conectado!");
        Serial.print("IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println("Falha ao conectar ao WiFi.");
    }

    // Configurar rotas do servidor
    server.on("/", HTTP_GET, handleRoot);
    server.on("/record", HTTP_GET, handleRecord);
    server.on("/audio", HTTP_GET, handleAudio);
    server.on("/status", HTTP_GET, handleStatus);

    server.begin();
    Serial.println("Servidor HTTP iniciado");
}

void loop() {

    // Processar requisições HTTP
    server.handleClient();
}