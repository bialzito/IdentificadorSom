#include <WiFi.h>
#include <WebServer.h>
#include <driver/i2s.h>
#include <SPIFFS.h>

const char* ssid = "Luanzito";
const char* password = "987654321";

WebServer server(80);

// Pinos do microfone INMP441
#define I2S_SCK 26      // Clock
#define I2S_WS 25       // Word Select
#define I2S_SD 33       // Serial Data (entrada)
#define I2S_PORT I2S_NUM_0

// Configurações de gravação
const int BUFFER_SIZE = 4096;           // Buffer temporário (menor)
int16_t audioBuffer[BUFFER_SIZE];       // Buffer temporário para leitura
const int RECORDING_TIME_MS = 5000;    // 10 segundos de gravação
const char* AUDIO_FILE = "/spiffs/audio.wav";

const int SAMPLE_RATE = 16000;

int totalSamples = 0;
bool isRecording = false;

//definindo pinos do led RGB e da chave
const int r = 23;
const int g = 21;
const int b = 32;
const int chave = 18;

//função para testar led e botões
void piscaLeds() {


    if(digitalRead(chave) == LOW){

      digitalWrite(b, !digitalRead(r));
       
      while(digitalRead(chave) == LOW){
          digitalWrite(r, !digitalRead(r));
          digitalWrite(b, !digitalRead(b));
          delay(500);
          digitalWrite(g, !digitalRead(g));
          digitalWrite(r, !digitalRead(r));
          delay(500);
          digitalWrite(b, !digitalRead(b));
          digitalWrite(g, !digitalRead(g));
          delay(500);
       }
    }
    else{
            digitalWrite(r, LOW);
            digitalWrite(g, LOW);
            digitalWrite(b, LOW);
        }
}

// Função para configurar o I2S
void setupI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 8,
        .dma_buf_len = 1024,
        .use_apll = true,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0,
        .mclk_multiple = I2S_MCLK_MULTIPLE_256 
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

// Função para configurar SPIFFS
void setupSPIFFS() {
    if (!SPIFFS.begin(true)) {
        Serial.println("Erro ao montar SPIFFS!");
        return;
    }
    Serial.println("SPIFFS montado com sucesso!");
    
    // Limpar arquivo anterior
    SPIFFS.remove(AUDIO_FILE);
}

// Função para gravar áudio no SPIFFS
void recordAudio() {
    Serial.println("Iniciando gravação...");
    isRecording = true;
    totalSamples = 0;

    // Abrir arquivo em modo escrita
    File audioFile = SPIFFS.open(AUDIO_FILE, "w");
    if (!audioFile) {
        Serial.println("Erro ao abrir arquivo para gravação!");
        isRecording = false;
        return;
    }

    // Escrever cabeçalho WAV temporário (será atualizado depois)
    uint32_t fileSize = 36;
    uint32_t dataSize = 0;
    uint32_t byteRate = SAMPLE_RATE * 1 * 16 / 8;  // SAMPLE_RATE × channels × bits ÷ 8
    uint16_t blockAlign = 2;

    // Escrever cabeçalho vazio (será preenchido depois)
    audioFile.seek(0);
    
    // "RIFF"
    audioFile.write((const uint8_t*)"RIFF", 4);
    audioFile.write((uint8_t*)&fileSize, 4);
    audioFile.write((const uint8_t*)"WAVE", 4);
    
    // "fmt "
    audioFile.write((const uint8_t*)"fmt ", 4);
    uint32_t subchunk1Size = 16;
    audioFile.write((uint8_t*)&subchunk1Size, 4);
    uint16_t audioFormat = 1;
    audioFile.write((uint8_t*)&audioFormat, 2);
    uint16_t numChannels = 1;
    audioFile.write((uint8_t*)&numChannels, 2);
    uint32_t sampleRate = SAMPLE_RATE;
    audioFile.write((uint8_t*)&sampleRate, 4);
    audioFile.write((uint8_t*)&byteRate, 4);
    audioFile.write((uint8_t*)&blockAlign, 2);
    uint16_t bitsPerSample = 16;
    audioFile.write((uint8_t*)&bitsPerSample, 2);
    
    // "data"
    audioFile.write((const uint8_t*)"data", 4);
    audioFile.write((uint8_t*)&dataSize, 4);

    unsigned long startTime = millis();
    size_t bytesRead = 0;

    // Gravar durante o tempo especificado
    while (millis() - startTime < RECORDING_TIME_MS) {
        // Ler dados do microfone
        i2s_read(I2S_PORT, (void*)audioBuffer, BUFFER_SIZE * sizeof(int16_t), &bytesRead, portMAX_DELAY);

        if (bytesRead > 0) {
            // Escrever dados no arquivo
            audioFile.write((const uint8_t*)audioBuffer, bytesRead);
            totalSamples += bytesRead / sizeof(int16_t);

            // Feedback a cada 1 segundo
            if (totalSamples % SAMPLE_RATE == 0) {
                Serial.print("Gravado: ");
                Serial.print(totalSamples / SAMPLE_RATE);
                Serial.println(" segundos");
            }
        }
    }

    // Atualizar cabeçalho WAV com tamanho real
    dataSize = totalSamples * 2;
    fileSize = 36 + dataSize;

    audioFile.seek(4);
    audioFile.write((uint8_t*)&fileSize, 4);
    audioFile.seek(40);
    audioFile.write((uint8_t*)&dataSize, 4);

    audioFile.close();

    isRecording = false;
    Serial.print("Gravação concluída! Total: ");
    Serial.print(totalSamples);
    Serial.println(" amostras");

    // Exibir tamanho do arquivo
    File checkFile = SPIFFS.open(AUDIO_FILE, "r");
    if (checkFile) {
        Serial.print("Tamanho do arquivo: ");
        Serial.print(checkFile.size());
        Serial.println(" bytes");
        checkFile.close();
    }
}

// Rota para iniciar gravação
void handleRecord() {
    if (isRecording) {
        server.send(400, "text/plain", "Ja esta gravando!");
        return;
    }
    recordAudio();
    server.send(200, "text/plain", "Gravacao concluida!");
}

// Rota para verificar se há áudio gravado
void handleStatus() {
    if (totalSamples > 0) {
        server.send(200, "text/plain", "ok");
    } else {
        server.send(200, "text/plain", "vazio");
    }
}

// Rota para enviar áudio em formato WAV
void handleAudio() {
    // Verificar se há áudio gravado
    if (totalSamples == 0) {
        Serial.println("Erro: Nenhum audio gravado");
        server.send(404, "text/plain", "Nenhum audio gravado");
        return;
    }

    File audioFile = SPIFFS.open(AUDIO_FILE, "r");
    if (!audioFile) {
        server.send(404, "text/plain", "Arquivo nao encontrado");
        return;
    }

    size_t fileSize = audioFile.size();
    Serial.print("Enviando audio. Tamanho: ");
    Serial.println(fileSize);

    // Configurar headers HTTP
    server.sendHeader("Content-Type", "audio/wav");
    server.sendHeader("Content-Length", String(fileSize));
    server.sendHeader("Content-Disposition", "inline; filename=\"audio.wav\"");
    server.setContentLength(fileSize);

    // Enviar arquivo em chunks
    WiFiClient client = server.client();
    const size_t CHUNK_SIZE = 4096;
    uint8_t buffer[CHUNK_SIZE];

    while (audioFile.available()) {
        size_t bytesToRead = audioFile.read(buffer, CHUNK_SIZE);
        if (bytesToRead > 0) {
            client.write(buffer, bytesToRead);
        }
    }

    audioFile.close();
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
                    "<p style='color: #666; margin-bottom: 15px;'>Clique para gravar (10 segundos)</p>"
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
                    "btn.textContent = '⏳ Gravando... (10s)';"
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

    // Configurar SPIFFS
    setupSPIFFS();

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

    pinMode(r, OUTPUT);
    pinMode(g, OUTPUT);
    pinMode(b, OUTPUT);
    pinMode(chave, INPUT_PULLUP);

    digitalWrite(r, LOW);
    digitalWrite(g, LOW);
    digitalWrite(b, LOW);
}

void loop() {
    // Processar requisições HTTP
    server.handleClient();
    piscaLeds();
}
