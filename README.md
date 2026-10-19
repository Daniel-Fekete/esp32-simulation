# ESP32-Simulation: Schritt für Schritt

## 1. Was ist die Aufgabe?

Wir bauen ein kleines System für Sensordaten.
Es gibt **keinen echten ESP32**. Ein Python-Programm erzeugt die Werte.
Das ist unsere Simulation.

Das Programm erzeugt alle **5 Sekunden**:

- eine Temperatur in Grad Celsius;
- eine Luftfeuchtigkeit in Prozent;
- die Zeit der Messung.

Die Werte werden als **JSON** gesendet. JSON ist ein Textformat für Daten.
Der MQTT-Topic heißt genau:

```text
fekdac22/tcmp
```

Ein Topic ist wie ein Kanal mit einem Namen.
Der Sender und der Empfänger müssen denselben Namen verwenden.
Schreibe deshalb überall genau `fekdac22/tcmp`.

## 2. Welche Programme machen was?

| Programm | Einfache Erklärung |
| --- | --- |
| Python | Erzeugt unsere erfundenen Sensorwerte. |
| paho-mqtt | Eine Python-Bibliothek. Sie sendet die Werte über MQTT. |
| Mosquitto | Der MQTT-Broker. Er nimmt Nachrichten an und verteilt sie. |
| MQTT Explorer | Zeigt die MQTT-Nachrichten an. |
| Telegraf | Liest die JSON-Nachrichten und macht daraus Messwerte für InfluxDB. |
| InfluxDB 2 | Speichert Messwerte zusammen mit ihrer Zeit. |
| Grafana | Liest die gespeicherten Werte und zeigt Diagramme. |
| Docker Compose | Startet die einzelnen Programme zusammen. |
| .env | Enthält gemeinsame Einstellungen und Beispiel-Zugangsdaten. |

Der Weg der Daten:

```text
Python → Mosquitto → Telegraf → InfluxDB → Grafana
             ↓
        MQTT Explorer
```

**MQTT Explorer ist kein Broker.** Es zeigt die Nachrichten vom Broker an.
Telegraf erhält die Nachrichten ebenfalls direkt vom Broker.
Du musst MQTT Explorer nicht offen lassen, damit die Daten gespeichert werden.

Grafana sendet keine Sensorwerte. Grafana zeigt sie nur an.
Eine Zeitreihen-Datenbank wie InfluxDB speichert, welcher Wert zu welcher Zeit gemessen wurde.

## 3. Was muss ich installieren?

Installiere diese zwei Programme:

1. **Docker Desktop:** https://docs.docker.com/desktop/
2. **MQTT Explorer:** https://mqtt-explorer.com/

Wähle auf der Download-Seite dein Betriebssystem und folge der Installation.
Starte danach Docker Desktop und warte, bis Docker bereit ist.

Falls Docker bei dir schon funktioniert, musst du es nicht noch einmal installieren.
Python, Mosquitto, Telegraf, InfluxDB und Grafana laufen in Docker.
Du musst diese Programme nicht einzeln auf deinem Computer installieren.

Die Befehle in dieser Anleitung sind für ein **Bash-Terminal**.
Unter Windows kannst du dafür Ubuntu in WSL benutzen.
Aktiviere dann in Docker Desktop die WSL-Integration für Ubuntu.

Öffne ein Terminal und prüfe Docker:

```bash
docker --version
docker compose version
docker run --rm hello-world
```

- Der erste Befehl zeigt die Docker-Version.
- Der zweite zeigt die Compose-Version.
- Der dritte startet einen kleinen Test. Danach wird der Test-Container entfernt.

Ein Container ist eine Umgebung, in der ein Programm läuft.
Wenn der Test funktioniert, kannst du weitermachen.

## 4. Projektordner vorbereiten

Wenn du den fertigen Projektordner bekommen hast, öffne ein Terminal in diesem Ordner.
Du kannst dann zu **Schritt 6** gehen. Prüfe vorher die `.env` aus Schritt 5.

Wenn du alles selbst anlegen willst, führe diese Befehle aus:

```bash
mkdir -p esp32-simulation/mosquitto esp32-simulation/telegraf esp32-simulation/simulator esp32-simulation/grafana/provisioning/datasources
cd esp32-simulation
```

`mkdir -p` erstellt die Ordner. `cd` wechselt in den Projektordner.

Am Ende soll der Ordner so aussehen:

```text
esp32-simulation/
├── README.md
├── .env
├── .gitignore
├── compose.yaml
├── esp32-dashboard.json          # zum Importieren des fertigen Diagramms
├── mosquitto/
│   └── mosquitto.conf
├── telegraf/
│   └── telegraf.conf
├── simulator/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── sensor.py
└── grafana/
    └── provisioning/
        └── datasources/
            └── influxdb.yaml
```

## 5. Dateien anlegen

Lege jede folgende Datei mit einem Texteditor an.
Kopiere den passenden Inhalt vollständig hinein und speichere die Datei.
Dateien wie `compose.yaml` dürfen nicht versehentlich `compose.yaml.txt` heißen.
Behalte die Einrückungen in YAML- und Python-Dateien bei.

### 5.1 Datei `.env`

Der Punkt gehört zum Dateinamen. Diese Datei liegt direkt im Projektordner.
Sie kann im Dateimanager als versteckte Datei angezeigt werden.

```dotenv
MQTT_TOPIC=fekdac22/tcmp
SENSOR_INTERVAL_SECONDS=5

INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=SchoolDemoInflux22
INFLUXDB_ORG=school
INFLUXDB_BUCKET=esp32
INFLUXDB_TOKEN=fekdac22-local-demo-token-change-before-use-2026

GRAFANA_USERNAME=admin
GRAFANA_PASSWORD=SchoolDemoGrafana22
```

- `MQTT_TOPIC`: der Kanal für unsere Nachrichten.
- `SENSOR_INTERVAL_SECONDS`: Abstand zwischen den Nachrichten in Sekunden.
- `INFLUXDB_ORG`: der Name unserer Organisation.
- `INFLUXDB_BUCKET`: der Name des Speicherbereichs für die Daten.
- `INFLUXDB_TOKEN`: ein Zugangsschlüssel für Telegraf und Grafana.
- Die anderen Werte sind die Benutzernamen und Passwörter.

Das sind Beispiel-Zugangsdaten für eine lokale Übung.
Wenn du sie ändern willst, mache das vor dem ersten Start.
Die `.env` mit deinen eigenen Zugangsdaten gehört nicht in ein öffentliches Git-Repository.

### 5.2 Datei `.gitignore`

```gitignore
.env
__pycache__/
```

Damit nimmt Git die `.env` nicht automatisch in das Repository auf.

### 5.3 Datei `mosquitto/mosquitto.conf`

```text
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest stdout
```

Mosquitto nimmt MQTT-Nachrichten auf Port 1883 an. Für diese lokale Übung ist kein MQTT-Login nötig. Die Nachrichten des Brokers erscheinen in den Docker-Logs.

### 5.4 Datei `simulator/requirements.txt`

```text
paho-mqtt==2.1.0
```

Hier steht die Python-Bibliothek paho-mqtt. Docker installiert sie beim Bauen des Simulators.

### 5.5 Datei `simulator/sensor.py`

```python
import json
import math
import os
import random
import threading
import time

import paho.mqtt.client as mqtt


MQTT_HOST = os.getenv("MQTT_HOST", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.environ["MQTT_TOPIC"]
INTERVAL = float(os.getenv("SENSOR_INTERVAL_SECONDS", "5"))

if INTERVAL <= 0:
    raise ValueError("SENSOR_INTERVAL_SECONDS must be greater than zero")

connected = threading.Event()


def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        connected.set()
        print(f"Connected to MQTT: {MQTT_HOST}:{MQTT_PORT}", flush=True)
    else:
        connected.clear()
        print(f"MQTT connection rejected: {reason_code}", flush=True)


def on_disconnect(client, userdata, flags, reason_code, properties):
    connected.clear()
    print(f"MQTT disconnected: {reason_code}", flush=True)


client = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id="fekdac22-esp32-simulator",
)
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.reconnect_delay_set(min_delay=1, max_delay=30)

client.connect_async(MQTT_HOST, MQTT_PORT, keepalive=60)
client.loop_start()

started = time.monotonic()

try:
    while True:
        if not connected.wait(timeout=5):
            print("Waiting for MQTT broker...", flush=True)
            continue

        elapsed = time.monotonic() - started

        reading = {
            "device": "esp32-sim",
            "timestamp": int(time.time()),
            "temperature": round(
                22 + 2 * math.sin(elapsed / 60) + random.uniform(-0.3, 0.3),
                2,
            ),
            "humidity": round(
                50 + 5 * math.sin(elapsed / 90) + random.uniform(-1, 1),
                2,
            ),
        }

        payload = json.dumps(reading)

        try:
            result = client.publish(
                MQTT_TOPIC,
                payload=payload,
                qos=1,
                retain=False,
            )
            result.wait_for_publish(timeout=10)

            if result.is_published():
                print(f"{MQTT_TOPIC}: {payload}", flush=True)
            else:
                print("Publish acknowledgement timed out", flush=True)
        except (RuntimeError, ValueError) as error:
            print(f"Publish failed: {error}", flush=True)

        time.sleep(INTERVAL)
finally:
    client.disconnect()
    client.loop_stop()
```

Das Programm erzeugt Temperatur und Luftfeuchtigkeit. random erzeugt kleine zufällige Änderungen. math erzeugt einen langsamen Verlauf. json.dumps macht aus den Werten einen JSON-Text. paho-mqtt sendet diesen Text an den Broker. timestamp ist die Messzeit in Sekunden seit dem 1. Januar 1970.

### 5.6 Datei `simulator/Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY sensor.py .

CMD ["python", "-u", "sensor.py"]
```

Docker benutzt ein Python-Image. Es installiert die Bibliothek und startet sensor.py. -u sorgt dafür, dass Ausgaben sofort im Log erscheinen.

### 5.7 Datei `telegraf/telegraf.conf`

```toml
[agent]
  interval = "5s"
  flush_interval = "5s"
  omit_hostname = true

[[inputs.mqtt_consumer]]
  servers = ["tcp://mqtt:1883"]
  topics = ["${MQTT_TOPIC}"]
  client_id = "fekdac22-telegraf"
  qos = 1
  persistent_session = true
  topic_tag = "topic"
  data_format = "json_v2"

  [[inputs.mqtt_consumer.json_v2]]
    measurement_name = "esp32_sensors"
    timestamp_path = "timestamp"
    timestamp_format = "unix"

    [[inputs.mqtt_consumer.json_v2.tag]]
      path = "device"

    [[inputs.mqtt_consumer.json_v2.field]]
      path = "temperature"
      type = "float"

    [[inputs.mqtt_consumer.json_v2.field]]
      path = "humidity"
      type = "float"

[[outputs.influxdb_v2]]
  urls = ["http://influxdb:8086"]
  token = "${INFLUXDB_TOKEN}"
  organization = "${INFLUXDB_ORG}"
  bucket = "${INFLUXDB_BUCKET}"
```

Telegraf hört auf den Topic aus der .env. Es liest device als Kennzeichnung und temperature und humidity als Zahlen. Die Messzeit kommt aus timestamp. Die Messreihe heißt esp32_sensors. Telegraf schreibt sie in den Bucket esp32.

### 5.8 Datei `grafana/provisioning/datasources/influxdb.yaml`

```yaml
apiVersion: 1

datasources:
  - name: InfluxDB-ESP32
    uid: influxdb-esp32
    type: influxdb
    access: proxy
    url: http://influxdb:8086
    isDefault: true
    editable: false
    jsonData:
      version: Flux
      organization: ${INFLUXDB_ORG}
      defaultBucket: ${INFLUXDB_BUCKET}
      httpMode: POST
    secureJsonData:
      token: ${INFLUXDB_TOKEN}
```

Grafana bekommt damit automatisch die Datenquelle InfluxDB-ESP32. Eine Datenquelle sagt Grafana, wo die Daten liegen. Diese Datei erstellt noch keine Diagramme. Das machen wir in Schritt 9.

### 5.9 Datei `compose.yaml`

```yaml
services:
  mqtt:
    image: eclipse-mosquitto:2
    restart: unless-stopped
    ports:
      - "127.0.0.1:1883:1883"
    volumes:
      - ./mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf:ro
      - mqtt-data:/mosquitto/data

  influxdb:
    image: influxdb:2.7
    restart: unless-stopped
    ports:
      - "127.0.0.1:8086:8086"
    environment:
      DOCKER_INFLUXDB_INIT_MODE: setup
      DOCKER_INFLUXDB_INIT_USERNAME: ${INFLUXDB_USERNAME}
      DOCKER_INFLUXDB_INIT_PASSWORD: ${INFLUXDB_PASSWORD}
      DOCKER_INFLUXDB_INIT_ORG: ${INFLUXDB_ORG}
      DOCKER_INFLUXDB_INIT_BUCKET: ${INFLUXDB_BUCKET}
      DOCKER_INFLUXDB_INIT_ADMIN_TOKEN: ${INFLUXDB_TOKEN}
    volumes:
      - influxdb-data:/var/lib/influxdb2
      - influxdb-config:/etc/influxdb2

  telegraf:
    image: telegraf:1.36
    restart: unless-stopped
    depends_on:
      - mqtt
      - influxdb
    environment:
      MQTT_TOPIC: ${MQTT_TOPIC}
      INFLUXDB_TOKEN: ${INFLUXDB_TOKEN}
      INFLUXDB_ORG: ${INFLUXDB_ORG}
      INFLUXDB_BUCKET: ${INFLUXDB_BUCKET}
    volumes:
      - ./telegraf/telegraf.conf:/etc/telegraf/telegraf.conf:ro

  simulator:
    build: ./simulator
    restart: unless-stopped
    depends_on:
      - mqtt
      - telegraf
    environment:
      MQTT_HOST: mqtt
      MQTT_PORT: "1883"
      MQTT_TOPIC: ${MQTT_TOPIC}
      SENSOR_INTERVAL_SECONDS: ${SENSOR_INTERVAL_SECONDS}

  grafana:
    image: grafana/grafana:12.2.0
    restart: unless-stopped
    depends_on:
      - influxdb
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      GF_SECURITY_ADMIN_USER: ${GRAFANA_USERNAME}
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
      INFLUXDB_TOKEN: ${INFLUXDB_TOKEN}
      INFLUXDB_ORG: ${INFLUXDB_ORG}
      INFLUXDB_BUCKET: ${INFLUXDB_BUCKET}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro

volumes:
  mqtt-data:
  influxdb-data:
  influxdb-config:
  grafana-data:
```

Diese Datei beschreibt die fünf Dienste. image nennt das Docker-Image. build baut unseren Simulator. environment übergibt Einstellungen. volumes speichert Daten oder verbindet Konfigurationsdateien. :ro bedeutet nur lesen. restart startet einen Dienst nach einem Absturz wieder. depends_on legt die Startreihenfolge fest; es wartet nicht darauf, dass ein Programm fertig eingerichtet ist. Wir benutzen ausdrücklich InfluxDB 2.7, damit die Flux-Abfragen dieser Anleitung passen.

Die Browser-Ports sind nur über deinen eigenen Computer erreichbar:

| Dienst | Adresse auf deinem Computer |
| --- | --- |
| MQTT-Broker | localhost:1883 |
| InfluxDB | http://localhost:8086 |
| Grafana | http://localhost:3000 |

Innerhalb von Docker heißen die Server `mqtt` und `influxdb`.
Deshalb benutzt Telegraf `mqtt:1883` und Grafana `http://influxdb:8086`.
`localhost` in einem Container bezeichnet diesen Container selbst.

## 6. System starten

Führe die Befehle im Projektordner aus. Docker Desktop muss laufen.

Prüfe die Compose-Datei:

```bash
docker compose config --quiet
```

Keine Ausgabe bedeutet: Compose hat die Konfiguration angenommen.
Bei einer Fehlermeldung prüfe die Datei und die Einrückungen.

Lade die fertigen Images herunter:

```bash
docker compose pull
```

Ein Image ist die Vorlage für einen Container.
Der Simulator wird im nächsten Schritt selbst gebaut:

```bash
docker compose build simulator
```

Docker installiert dabei paho-mqtt im Python-Container.

Starte zuerst den Broker und die Datenbank:

```bash
docker compose up -d mqtt influxdb
```

`-d` bedeutet: Die Programme laufen im Hintergrund weiter.
Warte beim ersten Start etwa 20 Sekunden.

Öffne http://localhost:8086 im Browser und melde dich an:

```text
Benutzername: admin
Passwort: SchoolDemoInflux22
```

Benutze deine eigenen Werte, falls du die `.env` geändert hast.
Prüfe unter **Load Data → Buckets**, ob der Bucket `esp32` vorhanden ist.
Wenn die Seite noch nicht erreichbar ist, warte kurz und lade sie neu.

Falls sie weiterhin nicht erreichbar ist, zeige die letzten Meldungen:

```bash
docker compose logs --tail=100 influxdb
```

Dieser Befehl zeigt die letzten 100 Log-Zeilen der Datenbank.

Wenn der Bucket vorhanden ist, starte alle Dienste:

```bash
docker compose up -d
```

Prüfe den Zustand:

```bash
docker compose ps
```

Du solltest fünf Dienste mit dem Zustand `Up` sehen:
`mqtt`, `influxdb`, `telegraf`, `simulator` und `grafana`.

Zeige die laufenden Meldungen:

```bash
docker compose logs -f simulator telegraf
```

`-f` zeigt auch neue Meldungen an.
Der Simulator sollte alle fünf Sekunden einen JSON-Text ausgeben.
Telegraf sollte mit dem MQTT-Broker verbunden sein.
Drücke **Strg+C**, wenn du das Log nicht mehr ansehen willst.
Die Container laufen trotzdem weiter.

## 7. Nachrichten in MQTT Explorer sehen

Öffne MQTT Explorer und erstelle eine neue Verbindung:

| Einstellung | Wert |
| --- | --- |
| Name | ESP32 Simulation |
| Protokoll | mqtt:// |
| Host | localhost |
| Port | 1883 |
| Benutzername | leer lassen |
| Passwort | leer lassen |
| TLS bzw. Verschlüsselung | ausgeschaltet |

Klicke auf **Connect**. Öffne links `fekdac22` und danach `tcmp`.
Du solltest Nachrichten in diesem Format sehen:

```json
{
  "device": "esp32-sim",
  "timestamp": 1791800000,
  "temperature": 22.43,
  "humidity": 51.27
}
```

Das ist nur ein Beispiel. Die Simulation sendet immer die aktuelle Zeit und neue Werte.
Die Zahlen müssen nicht genau wie im Beispiel aussehen.

Alternativ kannst du die Nachrichten im Terminal ansehen:

```bash
docker compose exec mqtt mosquitto_sub -h localhost -t 'fekdac22/tcmp' -v
```

Der Befehl startet einen MQTT-Empfänger im Broker-Container.
`-t` gibt den Topic an. `-v` zeigt den Topic neben der Nachricht.
Beende diese Anzeige mit **Strg+C**.

## 8. Gespeicherte Daten in InfluxDB sehen

Öffne http://localhost:8086 und melde dich an.
Wähle **Data Explorer** und dann den **Script Editor**.
Füge die folgende Abfrage ein und klicke auf **Submit**:

```flux
from(bucket: "esp32")
  |> range(start: -15m)
  |> filter(fn: (r) => r._measurement == "esp32_sensors")
  |> filter(fn: (r) => r.topic == "fekdac22/tcmp")
  |> filter(fn: (r) =>
    r._field == "temperature" or r._field == "humidity"
  )
```

Eine Abfrage ist eine Frage an die Datenbank.
Hier fragen wir nach Temperatur und Luftfeuchtigkeit der letzten 15 Minuten.
Warte nach dem Start etwa 10 bis 15 Sekunden, bis die ersten Werte gespeichert sind.

Wenn du Zahlen oder Linien siehst, funktioniert der Weg bis zur Datenbank.

## 9. Diagramme in Grafana anzeigen

Öffne http://localhost:3000 im Browser und melde dich an:

```text
Benutzername: admin
Passwort: SchoolDemoGrafana22
```

Benutze deine eigenen Werte, falls du die `.env` geändert hast.

Die Datenquelle **InfluxDB-ESP32** wird automatisch angelegt.
Du findest sie unter **Connections → Data sources**.
Öffne sie und klicke auf **Save & test**. Der Verbindungstest sollte erfolgreich sein.

**Die Grafana-Startseite zeigt noch keine Sensor-Diagramme.**
Du brauchst ein Dashboard. Das ist eine Seite mit Diagrammen.

### Möglichkeit A: Fertiges Dashboard importieren

Wenn du die Datei `esp32-dashboard.json` hast, ist das der kürzeste Weg:

1. Öffne **Dashboards**.
2. Wähle **New → Import**. Je nach Ansicht findest du Import auch im Menü **New** oben.
3. Lade `esp32-dashboard.json` hoch.
4. Wähle bei einer Nachfrage die Datenquelle **InfluxDB-ESP32**.
5. Klicke auf **Import**.

Das Dashboard heißt **ESP32 Simulation**.
Es zeigt Temperatur und Luftfeuchtigkeit und aktualisiert sich alle fünf Sekunden.
Die Datei benutzt den Bucket `esp32` und den Topic `fekdac22/tcmp`.

Wenn das Dashboard bereits vorhanden ist, öffne es unter **Dashboards**.
Du musst es nicht noch einmal importieren.

### Möglichkeit B: Diagramme selbst erstellen

Wenn du keine Dashboard-Datei hast oder die Einrichtung üben willst:

1. Öffne **Dashboards → New → New dashboard**.
2. Klicke auf **Add visualization**.
3. Wähle **InfluxDB-ESP32**.
4. Benutze den Texteditor für die Flux-Abfrage.
5. Füge die folgende Abfrage ein:

```flux
from(bucket: "esp32")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "esp32_sensors")
  |> filter(fn: (r) => r.topic == "fekdac22/tcmp")
  |> filter(fn: (r) => r.device == "esp32-sim")
  |> filter(fn: (r) => r._field == "temperature")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "temperature")
```

Wähle die Darstellung **Time series**.
Gib dem Diagramm den Titel **Temperatur**.
Wähle als Einheit **Celsius / °C** und speichere das Diagramm im Dashboard.

Erstelle ein zweites Diagramm mit derselben Datenquelle und dieser Abfrage:

```flux
from(bucket: "esp32")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) => r._measurement == "esp32_sensors")
  |> filter(fn: (r) => r.topic == "fekdac22/tcmp")
  |> filter(fn: (r) => r.device == "esp32-sim")
  |> filter(fn: (r) => r._field == "humidity")
  |> aggregateWindow(every: v.windowPeriod, fn: mean, createEmpty: false)
  |> yield(name: "humidity")
```

Titel: **Luftfeuchtigkeit**. Einheit: **Percent (0–100)**.
Stelle oben den Zeitraum auf **Last 15 minutes** und die Aktualisierung auf **5s**.
Speichere das Dashboard mit dem Namen **ESP32 Simulation**.

Die Abfragen verwenden den im Dashboard gewählten Zeitraum.
`aggregateWindow` fasst Werte für die Anzeige zusammen. `mean` bildet den Mittelwert.

Falls du einen anderen Bucket-Namen verwendet hast, ändere `esp32` in allen Abfragen.

## 10. Woran erkenne ich, dass die Aufgabe fertig ist?

- Alle fünf Docker-Dienste laufen.
- MQTT Explorer zeigt JSON unter `fekdac22/tcmp`.
- Die Werte ändern sich etwa alle fünf Sekunden.
- InfluxDB enthält Temperatur und Luftfeuchtigkeit mit Messzeiten.
- Grafana zeigt zwei Diagramme und aktualisiert sie automatisch.
- Im Projekt liegen `compose.yaml` und `.env`.

Du kannst dazu sagen:

> Ein Python-Programm simuliert einen ESP32. Es sendet Sensorwerte als JSON auf dem MQTT-Topic fekdac22/tcmp. Mosquitto verteilt die Nachrichten. MQTT Explorer zeigt sie an. Telegraf liest sie und schreibt die Messwerte in InfluxDB. Grafana zeigt die gespeicherten Werte als Diagramme. Docker Compose startet die Dienste, und die .env enthält die Einstellungen.

## 11. Stoppen und später weiterarbeiten

Alle Dienste stoppen:

```bash
docker compose down
```

Die gespeicherten Daten und Dashboards bleiben in den Docker-Volumes erhalten.
Ein Volume ist ein Speicherbereich, der beim Entfernen eines Containers bestehen bleibt.

Später wieder starten:

```bash
docker compose up -d
```

Nur die Simulation anhalten:

```bash
docker compose stop simulator
```

Nur die Simulation wieder starten:

```bash
docker compose start simulator
```

## 12. Was muss ich nach einer Änderung machen?

Wenn du `sensor.py` geändert hast:

```bash
docker compose up -d --build simulator
```

Dieser Befehl baut den Simulator neu und startet die neue Version.

Wenn du `telegraf.conf` geändert hast:

```bash
docker compose restart telegraf
```

Wenn du die Grafana-Datenquellen-Datei geändert hast:

```bash
docker compose restart grafana
```

Nach Änderungen an Umgebungsvariablen in der `.env`:

```bash
docker compose up -d --force-recreate
```

Damit erhalten die neu erstellten Container die neuen Einstellungen.

**Achtung:** Die ersten InfluxDB-Zugangsdaten und das erste Grafana-Admin-Passwort
werden beim ersten Einrichten gespeichert. Eine spätere Änderung der `.env`
ändert diese bereits gespeicherten Zugangsdaten nicht automatisch.
Ein Neustart löscht auch keine alten Messwerte.

## 13. Hilfe bei Fehlern

Alle letzten Log-Meldungen anzeigen:

```bash
docker compose logs --tail=100
```

| Problem | Was du prüfen solltest |
| --- | --- |
| Docker-Befehle funktionieren nicht | Läuft Docker Desktop? Funktioniert der Test aus Schritt 3? |
| Keine MQTT-Nachrichten | Läuft der Simulator? Ist der Host localhost und der Port 1883? |
| Topic fehlt | Steht in der .env genau fekdac22/tcmp? |
| MQTT funktioniert, aber InfluxDB ist leer | Prüfe die Telegraf-Logs. Stimmen Token, Organisation und Bucket? |
| Grafana zeigt nur die Startseite | Importiere oder erstelle das Dashboard aus Schritt 9. |
| Grafana zeigt No data | Prüfe den Zeitraum, den Bucket und die Abfrage. Warte kurz nach dem Start. |
| Grafana kann InfluxDB nicht erreichen | Die Datenquellen-URL muss http://influxdb:8086 sein. |
| Login funktioniert nicht | Benutze die Zugangsdaten der ersten Einrichtung. |
| Port is already allocated | Ein anderes Programm benutzt bereits Port 1883, 8086 oder 3000. |

## 14. Offizielle Anleitungen

- [Docker Desktop](https://docs.docker.com/desktop/)
- [MQTT Explorer](https://mqtt-explorer.com/)
- [Paho MQTT für Python](https://eclipse.dev/paho/clients/python/docs/)
- [Mosquitto 2](https://mosquitto.org/documentation/migrating-to-2-0/)
- [Telegraf MQTT-Eingang](https://docs.influxdata.com/telegraf/v1/input-plugins/mqtt_consumer/)
- [Telegraf JSON-Parser](https://docs.influxdata.com/telegraf/v1/data_formats/input/json_v2/)
- [InfluxDB 2 mit Docker Compose](https://docs.influxdata.com/influxdb/v2/install/use-docker-compose/)
- [Grafana mit InfluxDB](https://grafana.com/docs/grafana/latest/datasources/influxdb/configure/)
