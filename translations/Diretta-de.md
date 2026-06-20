# Aufbau einer dedizierten Diretta-Verbindung mit AudioLinux auf dem Raspberry Pi

Dieser Leitfaden bietet eine umfassende Schritt-für-Schritt-Anleitung zur Konfiguration zweier Raspberry Pi-Geräte als dedizierter Diretta-Host und Diretta-Target. Dieses Setup verwendet eine direkte Ethernet-Punkt-zu-Punkt-Verbindung zwischen den beiden Geräten, um ein Höchstmaß an Netzwerkisolierung und Audioleistung zu gewährleisten.

Der **Diretta-Host** wird mit Ihrem Hauptnetzwerk verbunden (für den Zugriff auf Ihren Musikserver) und fungiert gleichzeitig als Gateway für das Target. Das **Diretta-Target** wird ausschließlich mit dem Host und Ihrem USB-DAC oder DDC verbunden.

## Versionsverwaltung

Ich bemühe mich, diesen Leitfaden mit dem aktuellen offiziellen AudioLinux-Download-Link von Piero kompatibel zu halten.

**Aktuelle Validierung:**
Diese Anweisungen wurden zuletzt mit **AudioLinux V5** getestet (Image: `audiolinux_pi4-pi5_520`, Menüversion: `536`).

**Ein Hinweis zu Updates:**
Da AudioLinux auf Arch (einem Rolling Release) basiert, zieht eine Neuinstallation immer die absolut neueste Software. Sobald Ihr System wunschgemäß läuft, haben Sie zwei Möglichkeiten:

1.  **Regelmäßig aktualisieren:** Verpflichten Sie sich, mindestens monatlich Updates durchzuführen, um kleine Fehler direkt nach ihrem Auftreten zu beheben.
2.  **Einfrieren (Empfohlen):** Wenn es großartig klingt, ändern Sie nichts mehr. Erstellen Sie ein Backup-Image und genießen Sie die Musik!

## Eine Einführung in die Referenz-Roon-Architektur

Willkommen zum definitiven Leitfaden für den Aufbau eines hochmodernen Roon-Streaming-Endpunkts. Obwohl AudioLinux auch andere Protokolle unterstützt, verwende ich für diesen Aufbau Roon als Beispiel. Sie können über das Menüsystem des Diretta-Hosts Unterstützung für andere Protokolle installieren, darunter HQPlayer, Audirvana, DLNA, AirPlay usw. Bevor wir in die schrittweisen Anweisungen eintauchen, ist es wichtig, das „Warum“ hinter diesem Projekt zu verstehen. Diese Einführung erklärt das Problem, das diese Architektur löst, warum sie vielen hochpreisigen kommerziellen Alternativen grundlegend überlegen ist und wie dieses DIY-Projekt einen direkten und lohnenden Weg darstellt, um die ultimative Klangqualität aus Ihrem Roon-System herauszuholen.

### Das Roon-Paradoxon: Ein mächtiges Erlebnis mit einem klanglichen Vorbehalt

Roon wird fast universell als das leistungsstärkste und ansprechendste Musikverwaltungssystem gefeiert. Seine umfangreichen Metadaten und die nahtlose Benutzererfahrung sind unübertroffen. Diese funktionale Überlegenheit wurde jedoch lange von einer beständigen Kritik aus einem lautstarken Teil der audiophilen Gemeinschaft begleitet: Die Klangqualität von Roon sei kompromittiert, oft beschrieben als „flach, stumpf und leblos“ im Vergleich zu anderen Playern.

Dieser „Roon-Klang“ ist kein Mythos und auch kein Fehler in Roons bit-perfekter Software. Es ist ein mögliches Symptom der leistungsstarken und ressourcenintensiven Natur von Roon. Der „schwergewichtige“ Roon Core benötigt erhebliche Rechenleistung, was wiederum elektrisches Rauschen (RFI/EMI) erzeugt. Wenn der Computer, auf dem der Roon Core läuft, in unmittelbarer Nähe Ihres empfindlichen Digital-Analog-Wandlers (DAC) steht, kann dieses Rauschen die analoge Ausgangsstufe kontaminieren, Details verdecken, die Klangbühne verkleinern und der Musik ihre Lebendigkeit rauben.

---

### Mehr als nur „Notlösungen“: Eine fundamentale Lösung

Roon Labs selbst plädiert für eine „Zwei-Boxen“-Architektur, um dieses primäre Problem zu lösen: Die Trennung des anspruchsvollen **Roon Core** von einem leichtgewichtigen Netzwerk-**Endpunkt** (auch Streaming-Transport genannt). Dies ist der richtige erste Schritt, da die schwere Rechenlast auf eine entfernte Maschine ausgelagert und deren Rauschen von Ihrem Audio-Rack isoliert wird.

Doch selbst in diesem überlegenen zweistufigen Design bleibt ein subtileres Problem bestehen. Standard-Netzwerkprotokolle, einschließlich Roons eigenem RAAT, liefern Audiodaten in intermittierenden „Bursts“ (Schüben). Dies zwingt die CPU des Endpunkts dazu, ihre Aktivität ständig hochzufahren, um diese Bursts zu verarbeiten, was zu schnellen Schwankungen in der Stromaufnahme führt. Diese Schwankungen erzeugen ihr eigenes niederfrequentes elektrisches Rauschen direkt am Endpunkt – jener Komponente, die Ihrem DAC am nächsten ist.

High-End-Audiohersteller versuchen, die *Symptome* dieses stoßweisen Datenverkehrs mit verschiedenen „Notlösungen“ zu bekämpfen: massive lineare Netzteile, um die Stromspitzen besser zu bewältigen, Ultra-Low-Power-CPUs, um die Intensität der Spitzen zu minimieren, und zusätzliche Filterstufen, um das resultierende Rauschen zu bereinigen. Während diese Strategien helfen können, gehen sie nicht die Ursache des Rauschens an: die stoßweise Verarbeitung selbst.

Dieser Leitfaden präsentiert eine elegantere und dramatisch effektivere Lösung. Anstatt zu versuchen, das Rauschen nachträglich zu bereinigen, bauen wir eine Architektur, die verhindert, dass das Rauschen überhaupt erst entsteht.

---

### Die Drei-Stufen-Architektur: Roon + Diretta

Dieses Projekt entwickelt Roons empfohlenes Zwei-Boxen-Setup zu einem ultimativen dreistufigen System weiter, das mehrere, sich ergänzende Schichten der Isolierung bietet.

1.  **Stufe 1: Roon Core**: Ihr leistungsstarker Roon-Server läuft auf einer dedizierten Maschine, weit entfernt von Ihrem Hörraum. Er übernimmt die schwere Rechenarbeit, und sein elektrisches Rauschen bleibt von Ihrem Audiosystem isoliert.
2.  **Stufe 2: Diretta-Host**: Der erste Raspberry Pi in unserem Aufbau fungiert als **Diretta-Host**. Er verbindet sich mit Ihrem Hauptnetzwerk, empfängt den Audiostream vom Roon Core und sendet ihn in winzigen, präzise getakteten Segmenten weiter, wodurch die Stoßhaftigkeit des ursprünglichen Datenstroms eliminiert wird.
3.  **Stufe 3: Diretta-Target**: Der zweite Raspberry Pi, das **Diretta-Target**, verbindet sich *ausschließlich* über ein kurzes Ethernet-Kabel mit dem Host-Pi und schafft so eine galvanisch getrennte Punkt-zu-Punkt-Verbindung. Es empfängt die Audiodaten vom Host und verbindet sich per USB mit Ihrem DAC oder DDC.

### Was Diretta und AudioLinux bieten

Die Überlegenheit dieses Designs beruht auf zwei wichtigen Softwarekomponenten, die auf den Raspberry Pi-Geräten laufen:

* **AudioLinux**: Dies ist ein speziell für audiophile Zwecke entwickeltes Echtzeit-Betriebssystem. Im Gegensatz zu einem Allzweck-Betriebssystem ist es optimiert, um Prozessorlatenzen und System-„Jitter“ zu minimieren und so eine stabile, rauscharme Grundlage für unseren Endpunkt zu bieten.
* **Diretta**: Dieses bahnbrechende Protokoll ist die Geheimzutat, die das Wurzelproblem löst. Es erkennt, dass Schwankungen in der Verarbeitungslast des Endpunkts niederfrequentes elektrisches Rauschen erzeugen, das die interne Filterung eines DACs (definiert durch dessen PSRR – Power Supply Rejection Ratio) umgehen und die analoge Leistung subtil verschlechtern kann. Um dies zu bekämpfen, verwendet Diretta sein „Host-Target“-Modell, bei dem der Host Daten in einem kontinuierlichen, synchronisierten Strom kleiner, gleichmäßig verteilter Pakete sendet. Dies glättet die Verarbeitungslast auf dem Target-Gerät, stabilisiert die Stromaufnahme und minimiert die Erzeugung dieses schädlichen elektrischen Rauschens.

Die Kombination aus der physikalischen galvanischen Trennung durch die Ethernet-Punkt-zu-Punkt-Verbindung und der Eliminierung des Verarbeitungsrauschens durch das Diretta-Protokoll schafft einen extrem sauberen Signalweg zu Ihrem DAC – einen, der Lösungen, die viele tausend Euro kosten, übertreffen kann.

---

### Ein lohnender Weg zu klanglicher Exzellenz

Dieses Projekt ist mehr als nur eine technische Übung; es ist eine lohnende Möglichkeit, sich mit dem Hobby zu beschäftigen und die direkte Kontrolle über die Leistung Ihres Systems zu übernehmen. Durch den Bau dieser „Diretta-Bridge“ setzen Sie nicht einfach nur Komponenten zusammen; Sie implementieren eine hochmoderne Architektur, die die Kernherausforderungen der digitalen Audiowiedergabe direkt angeht. Sie werden ein tieferes Verständnis dafür gewinnen, worauf es bei der digitalen Wiedergabe wirklich ankommt, und mit einem Maß an Klarheit, Detailtreue und musikalischem Realismus von Roon belohnt, das Sie vielleicht nicht für möglich gehalten hätten.

Lassen Sie uns nun beginnen.

---

Wenn Sie sich in den USA befinden, müssen Sie mit etwa 320 $ rechnen (zuzüglich Steuern und Versand), um den Basisaufbau abzuschließen, der für die Evaluierung auf 44,1/48 kHz Wiedergabe beschränkt ist, sowie mit weiteren 100 €, um die Hi-Res-Wiedergabe freizuschalten (Preise können sich ändern):
- Hardware ($240)
- Ein Jahr AudioLinux-Abonnement ($79)
- Diretta-Target-Lizenz (€100)

## Inhaltsverzeichnis
1.  [Voraussetzungen](#1-voraussetzungen)
2.  [Vorbereitung des Installations-Images](#2-vorbereitung-des-installations-images)
3.  [Kernsystem-Konfiguration (Auf beiden Geräten durchführen)](#3-kernsystem-konfiguration-auf-beiden-geräten-durchführen)
4.  [System-Updates (Auf beiden Geräten durchführen)](#4-system-updates-auf-beiden-geräten-durchführen)
5.  [Punkt-zu-Punkt-Netzwerkkonfiguration](#5-punkt-zu-punkt-netzwerkkonfiguration)
6.  [Komfortabler und sicherer SSH-Zugriff](#6-komfortabler-und-sicherer-ssh-zugriff)
7.  [Allgemeine Systemoptimierungen](#7-allgemeine-systemoptimierungen)
8.  [Installation und Konfiguration der Diretta-Software](#8-installation-und-konfiguration-der-diretta-software)
9.  [Abschließende Schritte und Roon-Integration](#9-abschließende-schritte-und-roon-integration)
10. [Anhang 1: Optionale Lüftersteuerung für Argon ONE](#10-anhang-1-optionale-lüftersteuerung-für-argon-one)
11. [Anhang 2: Optionale IR-Fernbedienung](#11-anhang-2-optionale-ir-fernbedienung)
12. [Anhang 3: Optionaler Purist-Modus](#12-anhang-3-optionaler-purist-modus)
13. [Anhang 4: Optionale Web-Oberfläche zur Systemsteuerung](#13-anhang-4-optionale-web-oberfläche-zur-systemsteuerung)
14. [Anhang 5: System-Gesundheitschecks](#14-anhang-5-system-gesundheitschecks)
15. [Anhang 6: Optionales Echtzeit-Leistungstuning](#15-anhang-6-optionales-echtzeit-leistungstuning)
16. [Anhang 7: Optionale IRQ- und Thread-Optimierungen](#16-anhang-7-optionale-irq-und-thread-optimierungen)
17. [Anhang 8: Optionale puristische Netzwerkgeschwindigkeiten](#17-anhang-8-optionale-puristische-netzwerkgeschwindigkeiten)
18. [Anhang 9: Optionale Jumbo-Frames-Optimierung](#18-anhang-9-optionale-jumbo-frames-optimierung)
19. [Anhang 10: Optionale System-Updates](#19-anhang-10-optionale-system-updates)

---

### **Wie Sie diesen Leitfaden verwenden**

Dieser Leitfaden ist so einfach wie möglich gestaltet, um die manuelle Bearbeitung von Dateien auf ein Minimum zu reduzieren. Der primäre Arbeitsablauf besteht darin, Befehlsblöcke aus diesem Dokument direkt per **Copy & Paste** in ein Terminalfenster zu kopieren, das mit Ihren Raspberry Pi-Geräten verbunden ist.

Hier ist der Prozess, dem Sie für die meisten Schritte folgen werden:

1.  **Verbindung über SSH**: Sie verwenden einen SSH-Client auf Ihrem Hauptcomputer, um sich entweder auf dem **Diretta-Host** oder dem **Diretta-Target** anzumelden, wie in jedem Abschnitt angewiesen.
2.  **Befehl kopieren**: Fahren Sie in Ihrem Webbrowser mit der Maus über die obere rechte Ecke eines Befehlsblocks in diesem Leitfaden. Ein **Kopier-Symbol** wird angezeigt. Klicken Sie darauf, um den gesamten Block in Ihre Zwischenablage zu kopieren.
3.  **Einfügen und Ausführen**: Fügen Sie die kopierten Befehle in das richtige SSH-Terminalfenster ein und drücken Sie `Enter`.

Die Skripte und Befehle wurden sorgfältig geschrieben, um sicher zu sein und Fehler zu vermeiden, selbst wenn sie mehr als einmal ausgeführt werden. Durch Befolgen dieser Copy-and-Paste-Methode können Sie Tippfehler und Konfigurationsfehler vermeiden.

---

### Video-Walkthrough

Hier ist ein Link zu einer Reihe von kurzen Videos, die diesen Prozess veranschaulichen:

* [Diretta-Aufbau-Walkthrough mit zwei Raspberry Pi-Computern (Englisch)](https://youtube.com/playlist?list=PLMl09rJ6zKCk13V-IH_kRKW7FP8Q0_Fw0&si=u_E8rUEhgMiQ4NIb)

---

### 1. Voraussetzungen

#### Hardware

Eine vollständige Stückliste finden Sie unten. Obwohl andere Teile ersetzt werden können, verbessert die Verwendung dieser spezifischen Komponenten die Chancen auf einen erfolgreichen Aufbau.

**Kernkomponenten (von [pishop.us](https://www.pishop.us/) oder einem ähnlichen Anbieter):**
* 2 x [Raspberry Pi 5/1GB](https://www.pishop.us/product/raspberry-pi-5-1gb/)
* 2 x [Flirc Raspberry Pi 5 Gehäuse](https://www.pishop.us/product/flirc-raspberry-pi-5-case/)
* 2 x [64 GB A2 microSDXC-Karte](https://www.bhphotovideo.com/c/product/1830849-REG/lexar_lmssipl064g_bnanu_64gb_silver_plus_microsdxc.html)
* 2 x [Raspberry Pi 45W USB-C Netzteil - Weiß](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)

**Erforderliche Netzwerkkomponenten:**
* 1 x [Plugable USB3 auf Ethernet-Adapter](https://www.amazon.com/dp/B00AQM8586) (für den Diretta-Host)
* 1 x [Kurzes CAT6 Ethernet-Patchkabel](https://www.amazon.com/Cable-Matters-Snagless-Ethernet-Internet/dp/B0B57S1G2Y/?th=1) (für die Punkt-zu-Punkt-Verbindung)

**Optional, aber hilfreich bei der Fehlersuche:**
* 1 x [Micro-HDMI auf Standard HDMI (A/M), 2m Kabel, Weiß](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Offizielle Raspberry Pi Tastatur - Rot/Weiß](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**Optionale Upgrades:**
* 2 x [Argon ONE V3 Raspberry Pi 5 Gehäuse](https://www.amazon.com/Argon-ONE-V3-Raspberry-Case/dp/B0CNGSXGT2/) (anstelle der Flirc-Gehäuse)
* 1 x [Argon IR Fernbedienung](https://www.amazon.com/Argon-Raspberry-Infrared-Batteries-Included/dp/B091F3XSF6/) (um dem Diretta-Host Fernbedienungsfunktionen hinzuzufügen)
* 1 x [Flirc USB IR Empfänger](https://www.pishop.us/product/flirc-rpi-usb-xbmc-ir-remote-receiver/) (um die Argon IR Fernbedienung mit dem Diretta-Host in einem Flirc-Gehäuse zu verwenden)
* 1 x [Blue Jeans BJC CAT6a Belden Bonded Pairs 500 MHz](https://www.bluejeanscable.com/store/data-cables/index.htm) (für die Punkt-zu-Punkt-Verbindung zwischen Host und Target)
* 1 x [iFi SilentPower iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (um das Diretta-Target mit sauberem Strom zu versorgen)
* 1 x [iFi SilentPower Pulsar USB Kabel](https://www.silentpower.tech/products/pulsar-usb) (USB-Verbindung mit galvanischer Trennung)
* 1 x [DC 5,5mm x 2,1mm auf USB C Adapter](https://www.amazon.com/5-5mm-Adapter-Female-Convert-Connector/dp/B0CRB7N4GH/) (benötigt, um den Stecker des iPower Elite an den USB-C-Stromeingang des Diretta-Targets anzupassen)
* 1 x [SMSL PO100 PRO DDC](https://www.amazon.com/dp/B0BLYVZCV5) (ein Digital-Digital-Wandler für DACs, denen ein guter USB-Eingang fehlt)
* 1 x [USB WLAN-Adapter](https://www.pishop.us/product/raspberry-pi-dual-band-5ghz-2-4ghz-usb-wifi-adapter-with-antenna/) (eine kabelgebundene Verbindung ist sehr zu bevorzugen und zuverlässiger. Falls das Verlegen eines Ethernet-Kabels in der Nähe Ihres Audiosystems jedoch unpraktisch ist, ersetzen Sie den Plugable USB-zu-Ethernet-Adapter durch diesen WLAN-Adapter)
* 1 x [Stromverteilerkabel](https://www.amazon.com/dp/B01K3ADXX2?th=1) (beide 45W-Netzteile in eine einzige Steckdose stecken)

**Erforderliche Audiokomponente:**
* 1 x USB DAC oder DDC

**Erforderliche Werkzeuge:**
* Laptop oder Desktop-PC mit Linux, macOS (iTerm2, https://iterm2.com/, empfohlen) oder Microsoft Windows mit [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
* Ein SD- oder microSD-Kartenleser
* Ein HDMI-Fernseher oder Monitor und eine USB-Tastatur (optional, aber nützlich bei der Fehlersuche)

#### Software- & Lizenzkosten

* **AudioLinux:** Eine „Unlimited“-Lizenz wird für Enthusiasten empfohlen und kostet derzeit **$158** (Preise können sich ändern). Für den Einstieg reicht jedoch ein Jahresabonnement für derzeit **$79**. Beide Optionen erlauben die Installation auf mehreren Geräten am selben Standort.
* **Diretta-Target:** Für die Hi-Res-Wiedergabe (höher als 48 kHz PCM) über das Diretta-Target-Gerät ist eine Lizenz erforderlich, die derzeit **€100** kostet.
    * Sie können das Diretta-Target mit 44,1/48-kHz-Streams über einen längeren Zeitraum evaluieren. Daher empfehle ich, während der Testphase die **Abtastratenkonvertierung** (Sample rate conversion) in Roon unter den **MUSE** DSP-Einstellungen zu nutzen, um alle Inhalte auf 44,1 kHz zu konvertieren. Wenn Sie zufrieden sind, kaufen Sie die Diretta-Target-Lizenz, um diese Einschränkung aufzuheben. Lassen Sie die Einstellungen zur Abtastratenkonvertierung aktiv, bis Sie die zweite E-Mail vom Diretta-Team erhalten, die bestätigt, dass Ihre Hardware in deren Datenbank aktiviert wurde.
    * **WICHTIG:** Diese Lizenz ist an die spezifische Hardware des Raspberry Pi gebunden, für den sie gekauft wurde. Es ist unerlässlich, dass Sie den abschließenden Lizenzierungsschritt auf genau der Hardware durchführen, die Sie dauerhaft verwenden möchten.
    * Diretta bietet unter Umständen einen einmaligen Lizenzersatz bei Hardwareausfall innerhalb der ersten zwei Jahre an (bitte überprüfen Sie die Bedingungen zum Zeitpunkt des Kaufs). Wenn Sie die Hardware aus einem anderen Grund wechseln, muss eine neue Lizenz erworben werden.

---

### 2. Vorbereitung des Installations-Images

1.  **Kauf und Download:** Erwerben Sie das AudioLinux-Image von der [offiziellen Website](https://www.audio-linux.com/). Sie erhalten in der Regel innerhalb von 24 Stunden nach dem Kauf per E-Mail einen Link zum Herunterladen der `.img.gz`- oder `.img.xz`-Datei.
2.  **Image flashen:** Verwenden Sie den [Raspberry Pi Imager](https://www.raspberrypi.com/software/), um das heruntergeladene AudioLinux-Image auf **beide** microSD-Karten zu schreiben.

---

### 3. Kernsystem-Konfiguration (Auf beiden Geräten durchführen)

Nach dem Flashen müssen Sie jeden Raspberry Pi einzeln konfigurieren, um Netzwerkkonflikte zu vermeiden.

Für die beste Leistung verwendet dieser Leitfaden den Raspberry Pi 5 sowohl für das Diretta-Target (das Gerät, das mit Ihrem DAC verbunden ist) als auch für den Diretta-Host. Sie werden zuerst den Host konfigurieren.

> **KRITISCHE WARNUNG:** Da beide Geräte mit dem exakt gleichen Image geflasht wurden, besitzen sie identische `machine-id`-Werte. Wenn Sie beide Geräte gleichzeitig einschalten, während sie mit demselben LAN verbunden sind, wird Ihr DHCP-Server ihnen wahrscheinlich dieselbe IP-Adresse zuweisen, was zu einem Netzwerkkonflikt führt.
>
> **Sie müssen den ersten Start und die Konfiguration für jedes Gerät nacheinander durchführen.**

1.  Legen Sie die microSD-Karte in den **ersten** Raspberry Pi ein, verbinden Sie ihn mit Ihrem Netzwerk und schalten Sie ihn ein. **Hinweis:** Wenn Sie das Argon-ONE-Gehäuse verwenden, hören Sie möglicherweise Lüftergeräusche. Keine Sorge. Sobald die Diretta-Einrichtung abgeschlossen ist, finden Sie in [Anhang 1](#10-anhang-1-optionale-lüftersteuerung-für-argon-one) eine Anleitung zur Behebung dieses Problems.
2.  Führen Sie **alle Schritte aus Abschnitt 3** für dieses erste Gerät durch.
3.  Sobald das erste Gerät mit seiner neuen, einzigartigen Konfiguration neu gestartet wurde, fahren Sie es herunter.
4.  Schalten Sie nun den **zweiten** Raspberry Pi ein und wiederholen Sie **alle Schritte aus Abschnitt 3** für ihn.

Bitte entnehmen Sie den standardmäßigen SSH-Benutzer und die sudo-/root-Passwörter Ihrem Kaufbeleg von AudioLinux. Notieren Sie sich diese, da Sie sie im Laufe dieses Prozesses noch oft benötigen werden.

Sie werden den SSH-Client auf Ihrem lokalen Computer verwenden, um sich während dieses Prozesses auf den RPi-Geräten anzumelden. Hierfür müssen Sie die IP-Adresse der RPis herausfinden, welche sich bei jedem Neustart ändern kann. Am einfachsten finden Sie diese Informationen in der Benutzeroberfläche oder App Ihres Heim-Routers, optional können Sie jedoch auch die App [fing](https://www.fing.com/app/) auf Ihrem Smartphone oder Tablet installieren.

Sobald Sie die IP-Adresse eines Ihrer RPis haben, verwenden Sie den SSH-Client auf Ihrem lokalen Computer, um sich wie folgt anzumelden. Notieren Sie sich den Beispiel-`ssh`-Befehl, da Sie im Verlauf dieser Anleitung ähnliche Befehle verwenden werden.
```bash
cmd=$(cat <<'EOT'
read -rp "Enter the address of your RPi and hit [enter]: " RPi_IP_Address
echo 'Reminder: the default password is in your AudioLinux email from Piero'
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 3.1. Die Machine ID neu generieren

Die `machine-id` is eine eindeutige Kennung für die Betriebssysteminstallation. Sie **muss** für jedes Gerät unterschiedlich sein.

```bash
echo ""
echo "Old Machine ID: $(cat /etc/machine-id)"
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
echo "New Machine ID: $(cat /etc/machine-id)"
```

#### 3.2. Eindeutige Hostnamen setzen

Legen Sie für jedes Gerät einen eindeutigen Hostnamen fest, um sie leicht identifizieren zu können. **Hinweis:** Wenn dies nicht Ihr erster Aufbau nach dieser Anleitung ist und Sie bereits ein Diretta-Host/Target-Paar in Ihrem Netzwerk haben, sollten Sie für diesen neuen Diretta-Host einen anderen Namen wählen (z. B. `diretta-host2`), um diesen Teil zu vereinfachen. Dies erleichtert später den unabhängigen Zugriff auf beide Geräte.

**On your FIRST device (the future Diretta Host):**
```bash
# Auf dem Diretta-Host
sudo hostnamectl set-hostname diretta-host
```

**On your SECOND device (the future Diretta Target):**
```bash
# Auf dem Diretta-Target
sudo hostnamectl set-hostname diretta-target
```

**Fahren Sie das Gerät an dieser Stelle herunter. Wiederholen Sie die [obigen Schritte](#3-core-system-configuration-perform-on-both-devices) für den zweiten Raspberry Pi.**
```bash
sudo sync && sudo poweroff
```

---

### 4. System-Updates (Auf beiden Geräten durchführen)

Für die Schritte in diesem Abschnitt ist es meist am effizientesten (und am wenigsten verwirrend), den gesamten Abschnitt 4 auf dem Diretta-Host abzuschließen und ihn dann auf dem Diretta-Target komplett zu wiederholen.

Jeder RPi hat nun eine eigene Machine-ID, sodass Sie beide jetzt einschalten können. Wenn Sie über zwei Netzwerkkabel verfügen, ist es praktischer, beide Geräte für die nächsten Schritte gleichzeitig mit Ihrem Heimnetzwerk zu verbinden, andernfalls können Sie nacheinander vorgehen. **Hinweis:** Ihr Router wird ihnen wahrscheinlich andere IP-Adressen zuweisen als beim ersten Login. Verwenden Sie für Ihre SSH-Befehle unbedingt die neue IP-Adresse. Hier ist eine Erinnerung:

```bash
cmd=$(cat <<'EOT'
read -rp "Enter the (new) address of your RPi and hit [enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 4.1. „Chrony“ installieren, um die Systemzeit zu aktualisieren

Die Systemzeit muss korrekt sein, bevor wir Updates installieren können. Da der Raspberry Pi keine Pufferbatterie (NVRAM) besitzt, muss die Uhrzeit bei jedem Systemstart neu eingestellt werden. Dies geschieht in der Regel über einen Netzwerkdienst. Dieses Skript stellt sicher, dass die Uhrzeit eingestellt wird und während des Betriebs des Computers korrekt bleibt.

```bash
sudo id
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh | sudo bash
sleep 5
chronyc sources
```

#### 4.2. Zeitzone einstellen

```bash
cmd=$(cat <<'EOT'
clear
echo "Welcome to the interactive timezone setup."
echo "You will first select a region, then a specific timezone."

# Dem Benutzer erlauben, eine Region auszuwählen
PS3="
Please select a number for your region: "
select region in $(timedatectl list-timezones | grep -F / | cut -d/ -f1 | sort -u); do
  if [[ -n "$region" ]]; then
    echo "You have selected the region: $region"
    break
  else
    echo "Invalid selection. Please try again."
  fi
done

echo ""

# Dem Benutzer erlauben, eine Zeitzone innerhalb der Region auszuwählen
PS3="
Please select a number for your timezone: "
select timezone in $(timedatectl list-timezones | grep "^$region/"); do
  if [[ -n "$timezone" ]]; then
    echo "You have selected the timezone: $timezone"
    break
  else
    echo "Invalid selection. Please try again."
  fi
done

# Die ausgewählte Zeitzone einstellen
echo
echo "Setting timezone to ${timezone}..."
sudo timedatectl set-timezone "$timezone"
echo "✅ Timezone has been set."

# Die Änderung überprüfen
echo
echo "Current system time and timezone:"
timedatectl status
EOT
)
bash -c "$cmd"
```

#### 4.3. DNS-Utilities installieren
Installieren Sie das Paket `dnsutils`, damit das **Menü-Update** Zugriff auf den Befehl `dig` hat:
```bash
sudo pacman -S --noconfirm --needed dnsutils
```

#### 4.4. System- und Menü-Updates ausführen

Nutzen Sie das AudioLinux-Menüsystem, um alle Updates durchzuführen. Halten Sie die E-Mail von Piero mit Ihren Zugangsdaten (Benutzername und Passwort) bereit. Diese werden für das Menü-Update benötigt. Die Abfrage nach **„your menu update user“** ist etwas verwirrend: Gefragt ist der Benutzername, den Sie zum Herunterladen des AudioLinux-Installations-Images verwendet haben.

1.  Führen Sie `menu` im Terminal aus.
2.  Wählen Sie **INSTALL/UPDATE menu**.
    ```text
    Verifying license...
    Please enter the email address used at the time of purchase
    (You will only be asked once)
    ?
    <email address used to purchase AudioLinux support>
    OK
    OK

    Please type your menu update user
    ?
    <AUDIOLINUX RASPBERRY "user:" from your license email)>
    Please type your menu update password
    ?
    <AUDIOLINUX RASPBERRY "password:" from your license email)>
    ```
3.  Wählen Sie auf dem nächsten Bildschirm **UPDATE system** und warten Sie, bis der Vorgang abgeschlossen ist.
4.  Nachdem das System-Update abgeschlossen ist, wählen Sie auf demselben Bildschirm **Update menu**, um die neueste Version der AudioLinux-Skripte zu erhalten. *Hinweis:* Sie benötigen die E-Mail-Adresse, mit der Sie AudioLinux erworben haben, sowie Ihren Download-Benutzernamen und Ihr Passwort.
5.  Verlassen Sie das Menüsystem, um zum Terminal zurückzukehren.

#### 4.5. Neustart
Starten Sie das System neu, um den Kernel und andere Updates zu laden:
```bash
sudo sync && sudo reboot
```

---

### 5. Punkt-zu-Punkt-Netzwerkkonfiguration

In diesem Abschnitt erstellen wir die Netzwerkkonfigurationsdateien, die die dedizierte private Verbindung aktivieren. Um eine physische Tastatur und einen Monitor (Konsolenzugriff) zu vermeiden, führen wir diese Schritte aus, während beide Geräte noch mit Ihrem Haupt-LAN verbunden und über SSH erreichbar sind.

Wenn Sie die Aktualisierung Ihres Diretta-Targets gerade abgeschlossen haben, klicken Sie [hier](https://github.com/dsnyder0pc/rpi-for-roon/blob/main/Diretta.md#52-pre-configure-the-diretta-target) zu jump to the point-to-point network configuration steps for the Target.

---
> #### **Ein Hinweis zur Netzwerkkonfiguration: Warum keine einfache Bridge?**
>
> Benutzer, die mit AudioLinux vertraut sind, fragen sich vielleicht, warum dieser Leitfaden spezielle Skripte verwendet, um eine geroutete Punkt-zu-Punkt-Verbindung mit NAT zu konfigurieren, anstatt die einfachere Netzwerk-Bridge-Option zu nutzen, die im `menu`-System angeboten wird. Dies ist eine bewusste architektonische Entscheidung, um ein Höchstmaß an Netzwerkisolierung zu erreichen.
>
> * Eine **Netzwerk-Bridge** würde das Diretta-Target direkt in Ihr Haupt-LAN einbinden, wodurch es dem gesamten unbeteiligten Netzwerk-Broadcast- und Multicast-Verkehr ausgesetzt wäre.
> * Unser **geroutetes Setup** erstellt ein vollständig separates Subnetz hinter einer Firewall. Der Diretta-Host schützt das Target vor unnötigem Netzwerkverkehr und stellt sicher, dass der Prozessor des Targets nur den Audiostream verarbeitet. Dies minimiert die Systemaktivität und potenzielle elektrische Störungen, was das eigentliche Ziel dieser puristischen Architektur ist.
>
> Obwohl eine Bridge funktionell einfacher einzurichten ist, bietet die geroutete Methode durch maximale Isolierung eine theoretisch überlegene Grundlage für die Audioleistung.
---

#### 5.1. Den Diretta-Host vorkonfigurieren

1.  **Netzwerkdateien erstellen:**
    Erstellen Sie die folgenden zwei Dateien auf dem **Diretta-Host**. Die Datei `end0.network` legt die statische IP für die zukünftige Punkt-zu-Punkt-Verbindung fest. Die Datei `usb-uplink.network` stellt sicher, dass der USB-Ethernet-Adapter weiterhin eine IP aus Ihrem Haupt-LAN bezieht.

    *Datei: `/etc/systemd/network/end0.network`*
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/network/end0.network
    [Match]
    Name=end0

    [Link]
    MTUBytes=1500

    [Network]
    Address=172.20.0.1/24
    EOT
    ```

    *Datei: `/etc/systemd/network/usb-uplink.network`*
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/network/usb-uplink.network
    [Match]
    Name=en[pu]*

    [Link]
    MTUBytes=1500

    [Network]
    DHCP=yes
    DNSSEC=no
    EOT
    ```

    **Wichtig:** Entfernen Sie die alte en.network-Datei, falls vorhanden:
    ```bash
    # Die alte generische Netzwerkdatei entfernen, um Konflikte zu vermeiden.
    sudo rm -fv /etc/systemd/network/{en,enp,auto,eth}.network
    ```

    Fügen Sie einen Eintrag in `/etc/hosts` für das Diretta-Target hinzu:
    ```bash
    HOSTS_FILE="/etc/hosts"
    TARGET_IP="172.20.0.2"
    TARGET_HOST="diretta-target"

    # Einen Eintrag für das Diretta-Target hinzufügen, falls noch nicht vorhanden
    if ! grep -q "$TARGET_IP\s\+$TARGET_HOST" "$HOSTS_FILE"; then
      printf "%s\t%s target\n" "$TARGET_IP" "$TARGET_HOST" | sudo tee -a "$HOSTS_FILE"
    fi
    ```

2.  **IP-Weiterleitung aktivieren:**
    ```bash
    # Für die aktuelle Sitzung aktivieren
    sudo sysctl -w net.ipv4.ip_forward=1

    # Dauerhaft über Neustarts hinweg aktivieren
    echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ip-forwarding.conf
    ```

3.  **Network Address Translation (NAT) konfigurieren:**
    ```bash
    # Sicherstellen, dass nft ist installiert
    sudo pacman -S --noconfirm --needed nftables

    # Firewall- und NAT-Regeln installieren
    cat <<'EOT' | sudo tee /etc/nftables.conf
    #!/usr/sbin/nft -f

    # Alle alten Regeln aus dem Speicher löschen
    flush ruleset

    # Eine IPv4-Tabelle namens 'my_table' erstellen
    table ip my_table {

        # === Regel 2: Portweiterleitung (DNAT) ===
        # Diese Kette klinkt sich in den 'prerouting'-Pfad für NAT ein
        chain prerouting {
            type nat hook prerouting priority dstnat;

            # Host-Port 5101 an Target-Port 172.20.0.2:5001 weiterleiten
            tcp dport 5101 dnat to 172.20.0.2:5001
        }

        # === Regel 3: Weitergeleiteten Verkehr erlauben (FILTER) ===
        # Diese Kette klinkt sich in den 'forward'-Pfad für Paketfilterung ein
        chain forward {
            type filter hook forward priority 0;

            # Standardmäßig allen weitergeleiteten Verkehr blockieren
            policy drop;

            # Verbindungen erlauben, die bereits aufgebaut oder verwandt sind
            ct state established,related accept

            # Neuen Verkehr erlauben, der Ihrer Portweiterleitungsregel entspricht
            ip daddr 172.20.0.2 tcp dport 5001 ct state new accept

            # Allen anderen neuen Verkehr aus dem Target-Subnetz erlauben
            ip saddr 172.20.0.0/24 accept
        }

        # === Regel 1: Internetzugang (MASQUERADE) ===
        # Diese Kette klinkt sich in den 'postrouting'-Pfad für NAT ein
        chain postrouting {
            type nat hook postrouting priority 100;

            # Verkehr aus Ihrem Subnetz maskieren (NAT), der
            # über Schnittstellen ausgeht, die mit 'enp', 'enu' oder 'wlp' beginnen
            ip saddr 172.20.0.0/24 oifname "enp*" masquerade
            ip saddr 172.20.0.0/24 oifname "enu*" masquerade
            ip saddr 172.20.0.0/24 oifname "wlp*" masquerade
        }
    }
    EOT

    # Den alten iptables-Dienst stoppen und deaktivieren, falls vorhanden (2>/dev/null unterdrückt Fehler, falls nicht vorhanden)
    sudo systemctl disable --now iptables.service 2>/dev/null
    sudo rm /etc/iptables/iptables.rules 2>/dev/null

    # Regeln über nft aktivieren und anwenden
    sudo systemctl enable --now nftables.service
    ```

4.  **Den Plugable USB-zu-Ethernet-Adapter konfigurieren**

    Der Standard-USB-Treiber unterstützt nicht alle Funktionen des Plugable-Ethernet-Adapters. Für eine zuverlässige Leistung müssen wir dem Kernel-Gerätemanager mitteilen, wie das Gerät beim Einstecken zu behandeln ist:
    ```bash
    cat <<'EOT' | sudo tee /etc/udev/rules.d/99-ax88179a.rules
    ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0b95", ATTR{idProduct}=="1790", ATTR{bConfigurationValue}!="1", ATTR{bConfigurationValue}="1"
    EOT
    sudo udevadm control --reload-rules
    ```

5.  **Das `update_motd.sh`-Skript reparieren**

    Das Skript, das das Login-Banner (`/etc/motd`) aktualisiert, kommt mit zwei Netzwerkschnittstellen nicht richtig zurecht. Dies verhindert, dass der Login-Bildschirm nach dem Neustart mit falschen IP-Adressen überflutet wird. Das folgende neue Skript behebt dieses Problem.
    ```bash
    [ -f /opt/scripts/update/update_motd.sh.dist ] || \
    sudo mv /opt/scripts/update/update_motd.sh /opt/scripts/update/update_motd.sh.dist
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh
    sudo install -m 0755 update_motd.sh /opt/scripts/update/
    rm update_motd.sh
    ```

    Schalten Sie schließlich den Host aus:
    ```bash
    sudo sync && sudo poweroff
    ```

#### 5.2. Das Diretta-Target vorkonfigurieren

**Hinweis:** Wenn Sie [Schritt 4](#4-system-updates-auf-beiden-geräten-durchführen) auf dem Diretta-Target noch nicht durchgeführt haben, tun Sie das [jetzt](#4-system-updates-auf-beiden-geräten-durchführen) und kehren Sie dann hierher zurück.

Erstellen Sie auf dem **Diretta-Target** die Datei `end0.network`. Dies konfiguriert seine statische IP und weist es an, den Diretta-Host als Gateway für den gesamten Internetverkehr zu verwenden.

*Datei: `/etc/systemd/network/end0.network`*
```bash
cat <<'EOT' | sudo tee /etc/systemd/network/end0.network
[Match]
Name=end0

[Link]
MTUBytes=1500

[Network]
Address=172.20.0.2/24
Gateway=172.20.0.1
DNS=1.1.1.1
EOT
```

**Wichtig:** Entfernen Sie die alte en.network-Datei, falls vorhanden:
```bash
# Die alte generische Netzwerkdatei entfernen, um Konflikte zu vermeiden.
sudo rm -fv /etc/systemd/network/{en,auto,eth}.network
```

Fügen Sie einen Eintrag in `/etc/hosts` für den Diretta-Host hinzu. **Hinweis:** Selbst wenn Sie einen anderen Netzwerknamen für Ihren Diretta-Host gewählt haben, ist es am besten, wenn das Diretta-Target Ihren Host als `diretta-host` kennt.
```bash
HOSTS_FILE="/etc/hosts"
HOST_IP="172.20.0.1"
HOST_NAME="diretta-host"

# Einen Eintrag für den Diretta-Host hinzufügen, falls noch nicht vorhanden
if ! grep -q "$HOST_IP\s\+$HOST_NAME" "$HOSTS_FILE"; then
  printf "%s\t%s host\n" "$HOST_IP" "$HOST_NAME" | sudo tee -a "$HOSTS_FILE"
fi
```

> ---
> ### ⚠️ Kritische Topologie-Warnung: Filterplatzierung nur vorgeschaltet (Upstream)
>
> Falls Sie planen, dieses Projekt mit LAN-Regeneratoren, galvanischen Isolatoren oder Filtern (wie dem StackAudio SmoothLAN, iFi SilentPower LAN iSilencer oder LAN iPurifier Pro) zu erweitern, **müssen diese dem Diretta-Host vorgeschaltet werden** (zwischen Ihrem Haupt-Netzwerk-Switch/Router und dem USB-zu-Ethernet-Adapter des Hosts).
>
> **Platzieren Sie niemals einen Netzwerkfilter oder ein aktives Reclocking-Gerät auf der Direktverbindung (Punkt-zu-Punkt) zwischen dem Host und dem Target.** Dies verschlechtert fast immer die Audioleistung und kann zu schwerwiegenden Verbindungsstörungen führen.
>
> * **Das Haupt-LAN ist die primäre Rauschquelle:** Die Verbindung von Ihrem Heimrouter oder Haupt-Switch ist mit elektromagnetischen Störungen (EMI), Hochfrequenzstörungen (RFI) und unnötigem Broadcast-Verkehr überflutet. Ein Regenerator *vor* dem Host filtert diese digitale Verschmutzung an der Grenze heraus. Der Host verarbeitet dann einen sauberen Datenstrom, wodurch seine eigene CPU-Last, Stromschwankungen und thermisches Rauschen auf einem absoluten Minimum gehalten werden.
> * **Erhalt des Layer-2-Timings:** Das Einfügen eines aktiven Geräts in die direkte Punkt-zu-Punkt-Brücke stört die extrem engen Timing-Vorgaben von Diretta (`CycleTime` und `syncBufferCount`). Dies beeinträchtigt die präzise Zustellung der Layer-2-Frames, was zu klanglichen Einbußen, Latenzaritfakten oder einem vollständigen Scheitern des Targets bei der Aushandlung von Netzwerkgeschwindigkeitsänderungen führt.
> * **Das Prinzip der kaskadierten Isolierung:** Echte Isolierung wird in Schichten aufgebaut, um Ihren empfindlichen DAC vollständig vom Heimnetzwerk zu entkoppeln:
>   * **Hauptnetzwerk** → `[ LAN-Filter/Regenerator ]` → **Diretta-Host** *(Isoliert den Host vom Heimnetzwerk)*
>   * **Diretta-Host** → `[ Dediziertes Ethernet-Kabel ]` → **Diretta-Target** *(Isoliert durch die Punkt-zu-Punkt-Verbindung und den Protokoll-Stack)*
> ---

#### 5.3. Änderung der physischen Verbindung

> **Warnung:** Überprüfen Sie den Inhalt der soeben erstellten Dateien sorgfältig. Ein Tippfehler könnte ein Gerät nach dem Neustart unerreichbar machen, was eine Konsolensitzung oder ein erneutes Flashen der SD-Karte zur Behebung erfordern würde.

1.  Sobald Sie die Dateien überprüft haben, fahren Sie **beide** Geräte sauber herunter:
    ```bash
    sudo sync && sudo poweroff
    ```
2.  Trennen Sie beide Geräte von Ihrem Haupt-LAN-Switch/Router.
3.  Verbinden Sie den **integrierten Ethernet-Anschluss** des Diretta-Hosts direkt mit dem **integrierten Ethernet-Anschluss** des Diretta-Targets über ein einziges Ethernet-Kabel.
4.  Stecken Sie den **USB-zu-Ethernet-Adapter** in einen der blauen USB-3.0-Anschlüsse des Diretta-Host-Computers.
5.  Verbinden Sie den **USB-zu-Ethernet-Adapter** des Diretta-Hosts mit Ihrem Haupt-LAN-Switch/Router.
6.  Schalten Sie beide Geräte ein.

Nach dem Booten verwenden sie automatisch die neuen Netzwerkkonfigurationen. **Hinweis:** Die IP-Adresse Ihres Diretta-Hosts hat sich wahrscheinlich geändert, da er nun über den USB-zu-Ethernet-Adapter mit Ihrem Heimnetzwerk verbunden ist. Sie müssen die neue Adresse in der Web-Oberfläche Ihres Routers oder der Fing-App ermitteln. Diese sollte ab jetzt stabil bleiben.

```bash
cmd=$(cat <<'EOT'
read -rp "Enter the final address of your Diretta Host and hit [enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

Sie sollten nun in der Lage sein, das Target vom Host aus anzupingen:
```bash
echo ""
echo "\$ ping -c 3 172.20.0.2"
ping -c 3 172.20.0.2
```

Zudem sollten Sie sich vom Host aus auf dem Target einloggen können:
```bash
echo ""
echo "\$ ssh target"
ssh -o StrictHostKeyChecking=accept-new target
```

Versuchen wir nun vom Target aus einen Host im Internet anzupingen, um zu überprüfen, ob die Verbindung funktioniert:
```bash
echo ""
echo "\$ ping -c 3 one.one.one.one"
ping -c 3 one.one.one.one
```

---

### 6. Komfortabler und sicherer SSH-Zugriff

#### 6.1. Die `ProxyJump`-Anforderung

Da das Netzwerk nun konfiguriert ist, befindet sich das **Diretta-Target** in einem isolierten Netzwerk (`172.20.0.0/24`) und kann von Ihrem Haupt-LAN aus nicht direkt erreicht werden. Der Zugriff ist nur über einen „Sprung“ (Jump) durch den **Diretta-Host** möglich.

Die `ProxyJump`-Direktive in Ihrer lokalen SSH-Konfiguration ist die standardmäßige und erforderliche Methode, um dies zu erreichen.

1.  Führen Sie diesen Befehl auf Ihrem lokalen Computer aus (nicht auf dem Raspberry Pi). Sie werden nach der IP-Adresse des Diretta-Hosts gefragt, und das Skript gibt anschließend den genauen Konfigurationsblock aus, den Sie benötigen.
```bash
cmd=$(cat <<'EOT'
clear
# --- Interaktives SSH-Alias-Setup-Skript ---

SSH_CONFIG_FILE="$HOME/.ssh/config"
SSH_DIR="$HOME/.ssh"

# --- Sicherstellen, dass das .ssh-Verzeichnis und die Konfigurationsdatei mit den richtigen Berechtigungen existieren ---
mkdir -p "$SSH_DIR"
chmod 0700 "$SSH_DIR"
touch "$SSH_CONFIG_FILE"
chmod 0600 "$SSH_CONFIG_FILE"

# --- Den empfohlenen Block für globale Einstellungen definieren ---
GLOBAL_SETTINGS=$(cat <<'EOF'
# --- Empfohlene globale SSH-Einstellungen ---
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519

EOF
)

# --- Globale Einstellungen voranstellen, falls sie noch nicht existieren ---
if ! grep -q "AddKeysToAgent yes" "$SSH_CONFIG_FILE"; then
  echo "✅ Adding recommended global SSH settings..."
  # Eine temporäre Datei verwenden, um die Einstellungen voranzustellen
  echo "$GLOBAL_SETTINGS" | cat - "$SSH_CONFIG_FILE" > temp_ssh_config && mv temp_ssh_config "$SSH_CONFIG_FILE"
else
  echo "✅ Recommended global SSH settings already exist. No changes made."
fi

# --- Add Diretta-specific host configurations ---
if grep -q "Host diretta-host" "$SSH_CONFIG_FILE"; then
  echo "✅ SSH configuration for 'diretta-host' already exists. No changes made."
else
  read -rp "Enter the LAN IP address of your Diretta Host and press [Enter]: " Diretta_Host_IP

  # Die neue Konfiguration zur besseren Übersichtlichkeit mittels Heredoc anhängen
  cat <<EOT_HOSTS >> "$SSH_CONFIG_FILE"

# --- Diretta-Konfiguration (durch Skript hinzugefügt) ---
Host diretta-host host
    HostName ${Diretta_Host_IP}
    User audiolinux

Host diretta-target target
    HostName 172.20.0.2
    User audiolinux
    ProxyJump diretta-host
EOT_HOSTS

  echo "✅ SSH configuration for 'diretta-host' and 'diretta-target' has been added."
fi

# --- StrictHostKeyChecking aus älteren Versionen dieser Anleitung bereinigen ---
# Dies ist mit dem empfohlenen SSH-Schlüssel-Setup nicht mehr erforderlich
if command -v sed >/dev/null; then
    sed -i.bak -e '/StrictHostKeyChecking/d' "$SSH_CONFIG_FILE"
    # Eventuell verbliebene Leerzeilen entfernen
    sed -i.bak -e '/^$/N;/^\n$/D' "$SSH_CONFIG_FILE"
    rm -f "${SSH_CONFIG_FILE}.bak"
fi

echo ""
echo "--- Your ~/.ssh/config file now contains: ---"
cat "$SSH_CONFIG_FILE"
EOT
)
bash -c "$cmd"
```

2.  **Verbindung überprüfen:**

Sie sollten nun in der Lage sein, sich über die neuen Aliase mit beiden Geräten zu verbinden. Testen Sie die Verbindung mit folgenden Befehlen:

**Um sich auf dem Diretta-Host einzuloggen:**
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-host
```

Geben Sie `exit` ein, um sich abzumelden.

**Um sich auf dem Diretta-Target einzuloggen:** _(Sie werden zweimal nach dem Passwort gefragt)_
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-target
```
**Hinweis:** Sie werden einmal für den diretta-host (die Jumpbox) und ein zweites Mal für das diretta-target selbst nach dem Passwort gefragt. Der nächste Abschnitt ersetzt dies durch eine nahtlose schlüsselbasierte Authentifizierung.

**Hinweis:** Sie können kurz `ssh host` und `ssh target` verwenden.

#### 6.2. Empfohlen: Sichere Authentifizierung mit SSH-Schlüsseln

Obwohl Sie Passwörter verwenden können, ist die schlüsselbasierte Authentifizierung die sicherste und bequemste Methode. Unsere SSH-Konfiguration automatisiert den Großteil dieses Prozesses. Nach einer einmaligen Einrichtung können Sie sich sicher und ohne Passworteingabe sowohl auf dem Host als auch auf dem Target einloggen.

**Auf Ihrem lokalen Computer:**

1.  **Einen SSH-Schlüssel erstellen (falls Sie noch keinen haben):**
    Es wird empfohlen, einen modernen Algorithmus wie `ed25519` zu verwenden. Geben Sie bei der Aufforderung eine sichere, einprägsame **Passphrase** ein. Dies ist nicht Ihr Login-Passwort, sondern ein Passwort, das Ihre private Schlüsseldatei schützt.

    ```bash
    ssh-keygen -t ed25519 -C "audiolinux"
    ```

2.  **Ihren öffentlichen Schlüssel auf die Geräte kopieren:**
    Diese Befehle übertragen Ihren Schlüssel sicher auf die Geräte. Der erste Befehl fragt nach dem Passwort des Diretta-Hosts. Da die Verbindung zum Host dadurch passwortlos wird, fragt der zweite Befehl nur noch nach dem Passwort des Diretta-Targets.

    ```bash
    echo ""
    ssh-copy-id diretta-host
    echo ""
    ssh-copy-id diretta-target
    ```

3.  **Sicher einloggen:**
    Sie können sich nun per SSH auf Ihren Geräten einloggen. Beim ersten Verbindungsaufbau zu jedem Gerät werden Sie nach der in Schritt 1 erstellten **Passphrase** gefragt.

    ```bash
    ssh diretta-host
    ```

      * **Unter Linux:** Dank der Einstellung `AddKeysToAgent yes` wird Ihr Schlüssel für Ihre aktuelle Terminal-Sitzung zum SSH-Agenten hinzugefügt. Sie werden erst wieder nach der Passphrase gefragt, wenn Sie das System neu starten oder eine neue Login-Sitzung beginnen.

---

### (Optional) Für ein besseres Linux-Erlebnis

Wenn Sie Linux nutzen und möchten, dass Ihre SSH-Passphrase über Neustarts hinweg erhalten bleibt (ähnlich wie unter macOS), wird die Installation von `keychain` dringend empfohlen.

  * **Keychain installieren (Ubuntu/Debian):**

    ```bash
    sudo apt update && sudo apt install keychain
    ```

  * **Ihre Shell konfigurieren:** Fügen Sie die folgende Zeile in Ihre `~/.bashrc` (oder `~/.zshrc`, `~/.profile` etc.) ein, um `keychain` beim Öffnen eines Terminals zu starten. Sie werden dann nur einmal beim ersten Terminalstart nach einem Neustart nach der Passphrase gefragt.

    ```bash
    eval "$(keychain --eval --quiet id_ed25519)"
    ```

  * Laden Sie Ihre Shell neu, indem Sie ein neues Terminal öffnen oder den Befehl `source ~/.bashrc` ausführen.

Sie können sich nun ohne Passworteingabe per SSH auf beiden Geräten einloggen (`ssh diretta-host`, `ssh diretta-target`), sicher authentifiziert durch Ihren SSH-Schlüssel.

---

### 7. Allgemeine Systemoptimierungen

Bitte führen Sie diese Schritte auf _beiden_ Computern (Diretta-Host und -Target) aus. Wenn Sie später ein `menu`-Update durchführen, müssen Sie den `sudoers`-Fix erneut anwenden.

#### 7.1. Den Systemd-Status „Degraded“ beheben

Bei einer frischen AudioLinux-Installation wird der Systemstatus oft als `degraded` (beeinträchtigt) gemeldet. Dies wird meist durch eine harmlose Inkonsistenz zwischen den Gruppendateien des Systems (`/etc/group` and `/etc/gshadow`) verursacht. Der folgende Befehl synchronisiert diese Dateien sicher, was den fehlgeschlagenen `shadow.service` behebt und für einen sauberen Systemzustand sorgt.

```bash
sudo grpconv
```

#### 7.2. Die Priorität der `sudoers`-Regeln korrigieren

Eine Standardregel in der Hauptdatei `/etc/sudoers` kann manchmal spezifischere Regeln überschreiben, die für das Web-UI und andere Funktionen benötigt werden. Dies kann dazu führen, dass Befehle, die passwortlos ausgeführt werden sollten, fälschlicherweise nach einem Passwort verlangen.

Das folgende Skript korrigiert die Reihenfolge der Regeln in der Datei `/etc/sudoers` auf sichere Weise, um sicherzustellen, dass spezifische Ausnahmen korrekt verarbeitet werden. Das Skript nimmt Änderungen nur vor, wenn es die falsche Reihenfolge erkennt.

```bash
SUDOERS_FILE="/etc/sudoers"
TEMP_SUDOERS=$(mktemp)

# Einen Perl-Filter verwenden, um eine korrigierte Version der sudoers-Datei zu erstellen.
# Dieses Skript ist idempotent und ändert keine Datei, die bereits korrekt ist.
sudo cat "$SUDOERS_FILE" | perl -e '
while (<>) {
  if (m{/etc/sudoers.d} and not $found_audiolinux_all) {
    pop @lines if $#lines > -1 and $lines[$#lines] =~ /^$/;
    push @drop_in, $_;
  } else {
    push @lines, $_;
  }
  if (/^audiolinux ALL=\(ALL\) ALL$/) {
    $found_audiolinux_all++;
    push @lines, ("\n", @drop_in) if @drop_in;
  }
}
print @lines;
' > "$TEMP_SUDOERS"

# Die neue Datei vor der Installation mit visudo überprüfen
if [ -s "$TEMP_SUDOERS" ] && sudo visudo -c -f "$TEMP_SUDOERS"; then
    echo "Sudoers file passed validation. Installing corrected version..."
    # 'install' verwenden, um die korrekten Eigentümer/Berechtigungen zu setzen und das Original zu ersetzen
    sudo install -m 0440 -o root -g root "$TEMP_SUDOERS" "$SUDOERS_FILE"
else
    echo "ERROR: The modified sudoers file failed validation. No changes were made." >&2
fi
rm -f "$TEMP_SUDOERS"
```

#### 7.3. Bootzeit optimieren
Um eine lange Verzögerung beim Booten zu verhindern, während das System auf eine Netzwerkverbindung wartet, deaktivieren wir den Dienst „wait-online“.
```bash
# Den Netzwerk-Wartedienst deaktivieren, um lange Bootverzögerungen zu verhindern
sudo systemctl disable systemd-networkd-wait-online.service

# Ein Override erstellen, damit das MOTD-Skript auf eine Standardroute wartet
sudo mkdir -p /etc/systemd/system/update_motd.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/update_motd.service.d/wait-for-ip.conf
[Service]
ExecStartPre=/bin/sh -c "while [ -z \"$(ip route show default)\" ]; do sleep 0.5; done"
EOT
```

#### 7.4. Das Reparaturskript erstellen
Das Standardverhalten von Arch Linux besteht darin, das /boot-Dateisystem in einem unsauberen Zustand zu hinterlassen, wenn der Computer nicht ordnungsgemäß heruntergefahren wird. Dies ist normalerweise unbedenklich, führt jedoch manchmal zu einer Race-Condition beim Aufbau unseres privaten Netzwerks. Zudem neigen Benutzer dazu, diese Geräte einfach vom Strom zu trennen, ohne sie vorher herunterzufahren. Um dem entgegenzuwirken, fügen wir ein Workaround-Skript hinzu, welches das /boot-Dateisystem (das nur bei Software-Updates geändert wird) sauber hält.

Dieses Skript kann sowohl automatisch beim Booten als auch manuell auf einem laufenden System sicher ausgeführt werden.
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh
sudo install -m 0755 check-and-repair-boot.sh /usr/local/sbin/
rm check-and-repair-boot.sh
```

#### 7.5. Die `systemd`-Servicedatei erstellen und den Dienst aktivieren
```bash
cat <<'EOT' | sudo tee /etc/systemd/system/boot-repair.service
[Unit]
Description=Check and repair /boot filesystem before other services
DefaultDependencies=no
Conflicts=shutdown.target
Before=local-fs.target network-pre.target shutdown.target

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/check-and-repair-boot.sh
RemainAfterExit=yes

[Install]
WantedBy=local-fs.target
EOT
sudo systemctl daemon-reload
sudo systemctl --now enable boot-repair.service
sleep 5
journalctl -b -u boot-repair.service
```

#### 7.6. Festplatten-I/O minimieren
Ändern Sie `#Storage=auto` in `Storage=volatile` in der Datei `/etc/systemd/journald.conf`
```bash
sudo sed -i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
```

---

### 8. Installation und Konfiguration der Diretta-Software

#### 8.1. Auf dem Diretta-Target

1.  Schließen Sie Ihren USB-DAC an einen der schwarzen USB-2.0-Anschlüsse des **Diretta-Targets** an und stellen Sie sicher, dass der DAC eingeschaltet ist.
2.  Verbinden Sie sich per SSH mit dem Target: `ssh diretta-target`.
3.  Kompatible Compiler-Toolchain konfigurieren
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```
4.  Führen Sie `menu` aus.
5.  Wählen Sie **AUDIO extra menu**.
6.  Wählen Sie **DIRETTA target installation/configuration**. Sie sehen folgendes Menü:
    ```text
    What do you want to do?

    1) Install/update last version
    2) Enable/Disable Diretta Target
    3) Configure Audio card
    4) Edit configuration
    5) Copy and edit new default configuration
    6) License
    7) Diretta Target log
    8) Exit

    ?
    ```
7.  Sie sollten diese Aktionen nacheinander ausführen:
    * Wählen Sie **1) Install/update**, um die Software zu installieren (bestätigen Sie alle Abfragen mit „Y“).
    * Wählen Sie **2) Enable/Disable Diretta Target** und aktivieren Sie es.
    * Wählen Sie **3) Configure Audio card**. Das System listet Ihre verfügbaren Audiogeräte auf. Geben Sie die Kartennummer ein, die Ihrem USB-DAC entspricht.
        ```text
        ?3
        This option will set DIRETTA target to use a specific card
        Your available cards are:

        card 0: AUDIO [SMSL USB AUDIO], device 0: USB Audio [USB Audio]

        Please type the card number (0,1,2...) you want to use:
        ?0
        ```
    * Wählen Sie **4) Edit configuration**. Setzen Sie `AlsaLatency=20` für ein Raspberry Pi 5 Target oder `AlsaLatency=40` für RPi4.
    * Wählen Sie **6) License**. Das System spielt hochauflösendes Audio (mehr als 44,1 kHz PCM) 6 Minuten lang im Testmodus ab. Folgen Sie dem Link auf dem Bildschirm und den Anweisungen, um Ihre vollständige Lizenz für Hi-Res-Unterstützung zu erwerben und anzuwenden. Dies erfordert den in Schritt 5 konfigurierten Internetzugang.
        ```text
        The price of this third party license is 100$
        Without license DIRETTA Target will work for 6 min.
        If you see a link, you can use it to purchase a license
        If you see instead the word 'valid' the license has been correctly applied
        Please wait a few seconds...

        https://www.diretta.link/cgi-bin/target_app_regist.cgi?hash=1fd430fe950936867b31cc084a9dac031ffa7c57c8ba1d5034a1a5219444f441&vender=Audlinux


        The license will be applied at the next DIRETTA target start
        Press any key to continue
        ```
    * Wählen Sie **8) Exit**. Folgen Sie den Anweisungen, um zum Terminal zurückzukehren.

#### 8.2. Auf dem Diretta-Host

1.  Verbinden Sie sich per SSH mit dem Host: `ssh diretta-host`.

2.  Kompatible Compiler-Toolchain konfigurieren
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```

3.  Führen Sie `menu` aus.

4.  Wählen Sie **AUDIO extra menu**.

5.  Wählen Sie **DIRETTA host installation/configuration**. Sie sehen folgendes Menü:
    ```text
    What do you want to do?

    1) Install/update last version
    2) Enable/Disable Diretta daemon
    3) Set Ethernet interface
    4) Edit configuration
    5) Copy and edit new default configuration
    6) Diretta log
    7) Exit

    ?
    ```

6.  Sie sollten diese Aktionen nacheinander ausführen:
    * Wählen Sie **1) Install/update**, um die Software zu installieren (bestätigen Sie alle Abfragen mit „Y“). *(Hinweis: Möglicherweise sehen Sie `error: package 'lld' was not found`. Keine Sorge, dies wird durch die Installation automatisch korrigiert)*
    * Wählen Sie **2) Enable/Disable Diretta daemon** und aktivieren Sie ihn.
    * Wählen Sie **3) Set Ethernet interface**. Es ist wichtig, `end0` auszuwählen, also die Schnittstelle für die Punkt-zu-Punkt-Verbindung.
        ```text
        ?3
        Your available Ethernet interfaces are: end0  enu1
        Please type the name of your preferred interface:
        end0
        ```
    * Wählen Sie **4) Edit configuration** nur, wenn Sie erweiterte Änderungen vornehmen möchten. Die vorherigen Schritte sollten ausreichen; hier sind jedoch einige optimierte Einstellungen, die Sie ausprobieren können:
        ```text
        ScanOnlineStop=enable
        InfoCycle=80000
        FlexCycle=disable
        CycleTime=800
        periodMin=16
        periodSizeMin=2048
        ```

    * Wenn Sie nur die oben genannten optimierten Parameter installieren möchten, können Sie diesen Befehlsblock verwenden:
        ```bash
        cat <<'EOT' | sudo tee /opt/diretta-alsa/setting.inf
        [global]
        Interface=end0
        Broadcast=disable
        ScanOnlineStop=enable
        ScanInterval=
        TargetProfileLimitTime=200
        ThredMode=1
        InfoCycle=80000
        FlexCycle=disable
        CycleTime=800
        CycleMinTime=
        Debug=stdout
        periodMax=32
        periodMin=16
        periodSizeMax=38400
        periodSizeMin=2048
        syncBufferCount=8
        alsaUnderrun=enable
        alsaUnderrunSleep=0
        alsaUnderrunClear=disable
        unInitMemDet=disable
        CpuSend=
        CpuOther=
        LatencyBuffer=0
        disConnectDelay=enable
        singleMode=
        EOT
        ```
    * Wählen Sie **7) Exit**. Folgen Sie den Anweisungen, um zum Terminal zurückzukehren.

7.  Erstellen Sie ein Override, damit der Diretta-Dienst bei Fehlern automatisch neu startet
    ```bash
    sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta_alsa.service.d/restart.conf
    [Service]
    Restart=on-failure
    RestartSec=5
    EOT
    ```

---

### 9. Final Steps & Roon Integration

1.  Führen Sie `menu` aus, falls Sie nach dem vorherigen Schritt zum Terminal zurückgekehrt sind, andernfalls gehen Sie zum **Main menu**.

2.  **Roon Bridge installieren (auf dem Host):** Wenn Sie Roon verwenden, führen Sie die folgenden Schritte auf dem **Diretta-Host** aus:
    * Führen Sie `menu` aus.
    * Wählen Sie **INSTALL/UPDATE menu**.
    * Wählen Sie **INSTALL/UPDATE Roonbridge**.
    * Die Installation wird fortgesetzt und kann ein bis zwei Minuten dauern.

3.  **Roon Bridge aktivieren (auf dem Host):**
    * Wählen Sie **Audio menu** aus dem Hauptmenü.
    * Wählen Sie **SHOW audio service**.
    * Falls Sie **roonbridge** unter den aktivierten Diensten nicht sehen, wählen Sie **ROONBRIDGE enable/disable**.

4.  **Beide Geräte neu starten:** Für einen sauberen Start starten Sie sowohl das Target als auch den Host in dieser Reihenfolge neu:
    ```bash
    sudo sync && sudo reboot
    ```

5.  **Roon konfigurieren:**
    * Öffnen Sie Roon auf Ihrem Steuerungsgerät.
    * Gehen Sie zu `Settings` -> `Audio`.
    * Unter `diretta-host` sollten Sie Ihr Gerät sehen. Der Name basiert auf Ihrem DAC.
    * Klicken Sie auf `Enable`, geben Sie ihm einen Namen, und Sie können Musik abspielen!

Ihre dedizierte Diretta-Verbindung ist nun vollständig für eine makellose, isolierte Audiowiedergabe konfiguriert.
**Hinweis:** Die „Limited“-Zone für den Diretta-Target-Test verschwindet nach sechs Minuten Wiedergabe von hochauflösender Musik aus Roon. Dies ist normal. An diesem Punkt müssen Sie eine Lizenz für das Diretta-Target erwerben. Die Kosten betragen derzeit 100 € und die Aktivierung kann bis zu 48 Stunden dauern. Sie erhalten zwei E-Mails vom Diretta-Team. Die erste ist Ihre Quittung, die zweite Ihre Aktivierungsbenachrichtigung. Sobald Sie die Aktivierungs-E-Mail erhalten haben, starten Sie Ihren Target-Computer neu, damit die Aktivierung wirksam wird.

> ---
> ### ✅ Checkpoint: Kernsystem überprüfen
>
> Ihr Diretta- und Roon-Kernsystem sollte nun voll funktionsfähig sein. Um alle Dienste und Verbindungen zu überprüfen, fahren Sie bitte mit [**Anhang 5**](#14-anhang-5-system-gesundheitschecks) fort und führen Sie den universellen Befehl **System-Gesundheitscheck** sowohl auf dem Host als auch auf dem Target aus.
>
> ---

---

## 10. Appendix 1: Optional Argon ONE Fan Control
Wenn Sie sich für ein Argon-ONE-Gehäuse für Ihren Raspberry Pi entschieden haben, geht das Standard-Installationsskript davon aus, dass Sie ein Debian-Betriebssystem verwenden. Da AudioLinux jedoch auf Arch Linux basiert, müssen Sie stattdessen diesen Schritten folgen.

Wenn Sie Argon-ONE-Gehäuse sowohl für den Diretta-Host als auch für das Target verwenden, müssen Sie diese Schritte auf beiden Computern ausführen.

### Step 1: Skip the `argon1.sh` script in the manual
Im Handbuch steht, dass Sie das Skript `argon1.sh` von download.argon40.com herunterladen und an `bash` übergeben sollen. Dies funktioniert unter AudioLinux nicht, da das Skript ein Debian-basiertes Betriebssystem voraussetzt. Überspringen Sie diesen Schritt und folgen Sie stattdessen den unten stehenden Schritten.

### Step 2: Configure your system:
Diese Befehle aktivieren die I2C-Schnittstelle und fügen das spezifische `dtoverlay` für das Argon-ONE-Gehäuse hinzu. Das Skript versucht zunächst, den Parameter `i2c_arm` zu entkommentieren, falls er auskommentiert ist, und fügt dann das `argonone`-Overlay hinzu, falls es fehlt. Dies verhindert Fehler und doppelte Einträge.
```bash
BOOT_CONFIG="/boot/config.txt"
I2C_PARAM="dtparam=i2c_arm=on"

# --- I2C aktivieren, indem die Zeile entkommentiert wird, falls sie existiert ---
if grep -q -F "#$I2C_PARAM" "$BOOT_CONFIG"; then
  echo "Enabling I2C parameter..."
  sudo sed -i -e "s/^#\($I2C_PARAM\)/\1/" "$BOOT_CONFIG"
fi
```

### Step 3: Configure `udev` permissions
```bash
cat <<'EOT' | sudo tee /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c-[0-9]*", MODE="0666"
EOT
```

### Step 4: Install the Argon One Package
```bash
yay -S argonone-c-git
```

**Note:** If the above command fails with compiler errors, you can try this manual procedure to fix and install the package:
```bash
# Das Paket-Repository klonen
git clone https://aur.archlinux.org/argonone-c-git.git
cd argonone-c-git

# Quellcode herunterladen, ohne zu bauen
makepkg -o

# Patch anwenden, um Compilerfehler mit GCC 14+ zu beheben
sed -i 's/_timer_thread()/_timer_thread(void *args)/g' src/argonone-c-git/src/event_timer.c

# Unter Verwendung der gepatchten Quelle kompilieren und installieren
makepkg -e -i --noconfirm

# Bereinigen
cd ..
rm -rf argonone-c-git
```

### Step 5: Switch Argon ONE case from hardware to software control
```bash
sudo pacman -S --noconfirm --needed i2c-tools libgpiod
```

```bash
# Systemd-Overrides erstellen, um das Gehäuse beim Booten in den Softwaremodus zu schalten
sudo mkdir -pv /etc/systemd/system/argononed.service.d
cat <<'EOT'| sudo tee /etc/systemd/system/argononed.service.d/software-mode.conf
[Service]
ExecStartPre=/bin/sh -c "while [ ! -e /dev/i2c-1 ]; do sleep 0.1; done && /usr/bin/i2cset -y 1 0x1a 0"
EOT

cat <<'EOT'| sudo tee /etc/systemd/system/argononed.service.d/override.conf
[Unit]
After=multi-user.target
EOT
```

### Step 6: Enable the Service
```bash
# Den systemd-Manager neu laden, um die neue Konfiguration zu lesen
sudo systemctl daemon-reload

# Den Dienst so aktivieren, dass er beim Booten startet
sudo systemctl enable argononed.service
```

### Step 7: Reboot
Starten Sie schließlich Ihren Raspberry Pi neu, damit alle Änderungen wirksam werden (zuerst das Target, dann der Host):
```bash
sudo sync && sudo reboot
```

Nun wird der Lüfter durch den Daemon gesteuert und der Einschaltknopf ist voll funktionsfähig.

### Step 8: Verify the service
```bash
systemctl status argononed.service
journalctl -u argononed.service -b
```

### Step 9: Review Fan Mode and Settings:
Führen Sie den folgenden Befehl aus, um die aktuellen Konfigurationswerte anzuzeigen:
```bash
sudo argonone-cli --decode
```

Um diese Werte anzupassen, müssen Sie eine Konfigurationsdatei erstellen. Verwenden Sie diese Werte als Ausgangspunkt:
```bash
cat <<'EOT' | sudo tee /etc/argononed.conf
temp0=55
fan0=0
temp1=60
fan1=50
temp2=65
fan2=100
hysteresis=3
EOT
```

Restarten Sie den Dienst neu, um die neuen Konfigurationswerte zu übernehmen:
```bash
sudo systemctl restart argononed.service
echo ""
echo "Updated fan values:"
sleep 5
sudo argonone-cli --decode
```

Jetzt können Sie die Werte nach Bedarf anpassen, indem Sie den obigen Schritten folgen.

---

## 11. Appendix 2: Optional IR Remote Control

Dieser Leitfaden enthält Anweisungen zur Installation und Konfiguration einer IR-Fernbedienung zur Steuerung von Roon. Die Einrichtung ist in zwei Teile unterteilt.

  * **Part 1** covers the hardware-specific setup. You will choose **one** of the two appendices depending on whether you are using the Flirc USB receiver or the Argon One case's built-in receiver.
  * **Part 2** covers the software setup for the `roon-ir-remote` control script, which is identical for both hardware options.

**Note:** You will _only_ perform these steps on the Diretta Host. Das Target sollte nicht zur Weiterleitung von IR-Fernbedienungsbefehlen an den Roon Server verwendet werden.

---

### **Part 1: IR Receiver Hardware Setup**

*Follow the appendix for the hardware you are using.*

#### **Option 1: Flirc USB IR Receiver Setup**

1.  **Das Flirc-Gerät erwerben und programmieren:**
    Sie benötigen den Flirc-USB-IR-Empfänger, der auf der Website erworben werden kann: [https://flirc.tv/products/flirc-usb-receiver](https://flirc.tv/products/flirc-usb-receiver)

    Das Flirc-Gerät muss auf einem Desktop-Computer mit der Flirc-GUI-Software programmiert werden.

      * Stecken Sie den Flirc in Ihren Desktop-Computer und öffnen Sie die Flirc-GUI.
      * Gehen Sie zu `Controllers` und wählen Sie `Full Keyboard`.
      * Programmieren Sie die für das Skript erforderlichen Tasten (z. B. KEY_UP, KEY_DOWN, KEY_ENTER etc.), indem Sie die Taste in der GUI anklicken und dann die entsprechende Taste auf Ihrer physischen Fernbedienung drücken.
      * Schließen Sie den Flirc nach der Programmierung an den **Diretta-Host** an.

2.  **Das Flirc-Gerät testen:**
    Überprüfen Sie, ob der Raspberry Pi den Flirc als Tastatur erkennt.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Wählen Sie das „Flirc“-Gerät aus dem Menü. Wenn Sie Tasten auf Ihrer Fernbedienung drücken, sollten Tastatur-Ereignisse auf dem Bildschirm ausgegeben werden.

3.  Springen Sie zu [Teil 2: Software-Einrichtung des Steuerungsskripts](#part-2-control-script-software-setup)

---

#### **Option 2: Einrichtung der Argon-One-IR-Fernbedienung**

1.  **Die IR-Empfänger-Hardware aktivieren:**
    Sie müssen das Hardware-Overlay für den IR-Empfänger des Argon-One-Gehäuses aktivieren.

      * Dieser Befehl fügt das erforderliche Hardware-Overlay sicher zu Ihrer Datei `/boot/config.txt` hinzu und prüft vorher, ob es nicht bereits vorhanden ist.
        ```bash
        BOOT_CONFIG="/boot/config.txt"
        IR_CONFIG="dtoverlay=gpio-ir,gpio_pin=23"

        # IR-Fernbedienungs-Overlay hinzufügen, falls noch nicht vorhanden
        if ! sed 's/#.*//' $BOOT_CONFIG | grep -q -F "$IR_CONFIG"; then
          echo "Enabling Argon One IR Receiver..."
          sudo sed -i "/# Uncomment this to enable infrared communication./a $IR_CONFIG" /boot/config.txt
        else
          echo "Argon One IR Receiver already enabled."
        fi
        ```
      * Ein Neustart ist erforderlich, damit die Hardware-Änderung wirksam wird.
        ```bash
        sudo sync && sudo reboot
        ```

2.  **IR-Tools installieren und Protokolle aktivieren:**
    Installieren Sie `ir-keytable`
    ```bash
    sudo pacman -S --noconfirm v4l-utils
    ```

3.  **Tasten-Scancodes erfassen:**
     Aktivieren Sie alle Kernel-Protokolle, damit Signale von Ihrer Fernbedienung decodiert werden können. Führen Sie das Test-Tool aus, um den eindeutigen Scancode für jede Fernbedienungstaste zu sehen.
    ```bash
    sudo ir-keytable -p all
    sudo ir-keytable -t
    ```

    Press each button you want to use and note its scancode from the `MSC_SCAN` event output (e.g., `value ca`). Press `Ctrl+C` when done.

4.  **Die Keymap-Datei erstellen:**
    Diese Datei ordnet die Scancodes Standard-Tastennamen zu.

      * Erstellen Sie eine neue Keymap-Datei:
        ```bash
        cat <<'EOT' | sudo tee /etc/rc_keymaps/argon.toml
        # /etc/rc_keymaps/argon.toml
        [[protocols]]
        name = "argon_remote"
        protocol = "nec"
        [protocols.scancodes]
        0xca = "KEY_UP"
        0xd2 = "KEY_DOWN"
        0x99 = "KEY_LEFT"
        0xc1 = "KEY_RIGHT"
        0xce = "KEY_ENTER"
        0x90 = "KEY_ESC"
        0x80 = "KEY_VOLUMEUP"
        0x81 = "KEY_VOLUMEDOWN"
        0xcb = "KEY_MUTE"
        EOT
        ```
      * Wenn die Scancodes in der obigen Beispieldatei nicht mit den von Ihnen aufgezeichneten übereinstimmen, bearbeiten Sie die Datei (`sudo nano /etc/rc_keymaps/argon.toml`) und passen Sie sie entsprechend an.

5.  **Einen `systemd`-Dienst zum Laden der Keymap erstellen:**
    Dieser Dienst lädt Ihre Keymap beim Booten automatisch.

    Erstellen Sie eine neue Servicedatei und aktivieren Sie den Dienst:
    ```bash
    cat <<'EOT' | sudo tee /etc/systemd/system/ir-keymap.service
    [Unit]
    Description=Load custom IR keymap
    After=multi-user.target

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    ExecStart=/usr/bin/ir-keytable -c -p nec -w /etc/rc_keymaps/argon.toml

    [Install]
    WantedBy=multi-user.target
    EOT
    sudo systemctl enable --now ir-keymap.service
    ```

6.  **Das Eingabegerät testen:**
    Überprüfen Sie, ob das System Tastatur-Ereignisse von der IR-Fernbedienung empfängt.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Wählen Sie das `gpio_ir_recv`-Gerät. Wenn Sie Tasten auf der Fernbedienung drücken, sollten die entsprechenden Tastenereignisse angezeigt werden.
    Drücken Sie `Ctrl+C`, wenn Sie den Test beendet haben.

---

### **Teil 2: Software-Einrichtung des Steuerungsskripts**

*Nachdem Sie Ihre Hardware in Teil 1 eingerichtet haben, folgen Sie diesen Schritten, um das Python-Steuerungsskript zu installieren und zu konfigurieren.*

### **Schritt 1: `audiolinux` zur Gruppe `input` hinzufügen**
Dies ist erforderlich, damit das `audiolinux`-Konto Zugriff auf Ereignisse des Fernbedienungsempfängers hat.
```bash
sudo usermod --append --groups input audiolinux
```
Melden Sie sich ab und wieder an, damit diese Änderung wirksam wird. Sie können dies mit folgendem Befehl überprüfen:
```bash
echo ""
echo ""
echo "Checking your group memberships:"
echo "\$ groups"
groups
echo ""
echo "Above, you should see:"
echo "audiolinux realtime video input audio wheel"
```

---

### **Schritt 2: Python über `pyenv` installieren**

Installieren Sie `pyenv` und die neueste stabile Python-Version.

```bash
# Build-Abhängigkeiten installieren
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

# Pyenv nur installieren, falls noch nicht installiert
if [ ! -d "$HOME/.pyenv" ]; then
  echo "--- Installing pyenv ---"
  curl -fsSL https://pyenv.run | bash
else
  echo "--- pyenv is already installed. Skipping installation. ---"
fi

# Shell für pyenv konfigurieren
if grep -q 'pyenv init' ~/.bashrc; then
  :
else
  cat <<'EOT'>> ~/.bashrc

export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
eval "$(pyenv virtualenv-init -)"
EOT
fi

# Die Datei einlesen (source), um pyenv in der aktuellen Shell verfügbar zu machen
. ~/.bashrc

# Die neueste Python-Version nur installieren und setzen, falls noch nicht installiert
PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')

if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
    # Gesamten Arbeitsspeicher in MB ermitteln
    TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

    if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- Physical RAM is ${TOTAL_MEM}MB. Limiting to 1 core to prevent lockup. ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
    else
        echo "--- Physical RAM is ${TOTAL_MEM}MB. Proceeding with parallel build. ---"
    fi

    echo "--- Installing Python ${PYVER}. This will take several minutes... ---"
    pyenv install "$PYVER"
    [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
else
    echo "--- Python ${PYVER} is already installed. ---"
fi

pyenv global "$PYVER"
```

**Hinweis:** Es ist normal, dass der Teil `Installing Python-3.14.5...` etwa 10 Minuten dauert, da Python aus den Quellen kompiliert wird. Geben Sie nicht auf! Entspannen Sie sich bei schöner Musik über Ihre neue Diretta-Zone in Roon, während Sie warten. Diese sollte verfügbar sein, während Python auf dem Host installiert wird.

---

### **Schritt 3: Das `roon-ir-remote`-Software-Repository herunterladen**

Klonen Sie das Skript-Repository und rufen Sie einen Patch ab, um Tastencodes korrekt über den Namen statt über die Nummer zu verarbeiten.

```bash
cd
# Das Repository klonen, falls noch nicht vorhanden, andernfalls aktualisieren
if [ ! -d "roon-ir-remote" ]; then
  git clone https://github.com/dsnyder0pc/roon-ir-remote.git
else
  (cd roon-ir-remote && git pull)
fi
```

---

### **Schritt 4: Die Roon-Umgebungskonfigurationsdatei erstellen**

Konfigurieren Sie das Skript mit Ihren Roon-Details. **Hinweis:** Die `event_mapping`-Codes müssen mit den in Ihrem Hardware-Setup definierten Tastennamen übereinstimmen (`KEY_ENTER`, `KEY_VOLUMEUP` etc.).

```bash
bash <<'EOF'
# --- Skript-Anfang ---

# Roon-Zone abrufen und in einer Variablen speichern
echo "Enter the name of your Roon zone."
echo "IMPORTANT: This must match the zone name in the Roon app exactly (case-sensitive)."
# Diese Zeile ist der Fix: < /dev/tty weist read an, das Terminal zu verwenden
read -rp "Enter your Roon Zone name: " MY_ROON_ZONE < /dev/tty

# Erkennen, ob Flirc-/Tastatur-Mapping erforderlich ist
if [ -f "/etc/systemd/system/ir-keymap.service" ]; then
    VOL_UP_CODE="KEY_VOLUMEUP"
    VOL_DOWN_CODE="KEY_VOLUMEDOWN"
    echo "--- Standard IR receiver detected. Using KEY_VOLUMEUP/DOWN. ---"
else
    VOL_UP_CODE="KEY_UP"
    VOL_DOWN_CODE="KEY_DOWN"
    echo "--- Flirc/HID adapter detected. Using KEY_UP/DOWN for volume. ---"
fi

# Sicherstellen, dass das Zielverzeichnis existiert
mkdir -p roon-ir-remote

# Die Konfigurationsdatei mittels Here-Dokument erstellen
# Die Variable wird nun korrekt ersetzt
cat <<EOD > roon-ir-remote/app_info.json
{
  "roon": {
    "app_info": {
      "extension_id": "com.smangels.roon-ir-remote",
      "display_name": "Roon IR Remote",
      "display_version": "1.1.0",
      "publisher": "dsnyder",
      "email": "dsnyder0cnn@gmail.com",
      "website": "https://github.com/dsnyder0pc/roon-ir-remote"
    },
    "zone": {
      "name": "${MY_ROON_ZONE}"
    },
    "event_mapping": {
      "codes": {
        "play_pause": "KEY_ENTER",
        "stop": "KEY_ESC",
        "skip": "KEY_RIGHT",
        "prev": "KEY_LEFT",
        "vol_up": "${VOL_UP_CODE}",
        "vol_down": "${VOL_DOWN_CODE}",
        "mute": "KEY_MUTE"
      }
    }
  }
}
EOD

echo ""
echo "✅ Configuration file 'roon-ir-remote/app_info.json' created successfully."

# --- Skript-Ende ---
EOF
```

---

### **Schritt 5: `roon-ir-remote` vorbereiten und testen**

Installieren Sie die Abhängigkeiten des Skripts in einer virtuellen Umgebung und führen Sie es zum ersten Mal aus.

```bash
cd ~/roon-ir-remote
# Die virtuelle Umgebung nur erstellen, falls sie noch nicht existiert
if ! pyenv versions --bare | grep -q "^roon-ir-remote$"; then
  echo "--- Creating 'roon-ir-remote' virtual environment ---"
  pyenv virtualenv roon-ir-remote
else
  echo "--- 'roon-ir-remote' virtual environment already exists ---"
fi
pyenv activate roon-ir-remote
pip3 install --upgrade pip
pip3 install -r requirements.txt

python roon_remote.py
```

Beim ersten Start des Skripts müssen Sie **die Erweiterung in Roon autorisieren**, indem Sie zu `Settings` -> `Extensions` gehen.

Während Musik in Ihrer neuen Diretta-Roon-Zone abgespielt wird, richten Sie Ihre IR-Fernbedienung direkt auf den Diretta-Host-Computer und drücken Sie die Wiedergabe-/Pause-Taste (möglicherweise die mittlere Taste auf dem Steuerkreuz). Versuchen Sie auch „Weiter“ und „Zurück“. Falls dies nicht funktioniert, überprüfen Sie Ihr Terminalfenster auf Fehlermeldungen. Wenn Sie den Test beendet haben, geben Sie `Ctrl+C` ein, um das Programm zu beenden.

---

### **Schritt 6: Einen `systemd`-Dienst erstellen**

Erstellen Sie einen Dienst, um das Skript automatisch im Hintergrund auszuführen.

```bash
cat <<EOT | sudo tee /etc/systemd/system/roon-ir-remote.service
[Unit]
Description=Roon IR Remote Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${LOGNAME}
Group=${LOGNAME}
WorkingDirectory=/home/${LOGNAME}/roon-ir-remote
ExecStart=/home/${LOGNAME}/.pyenv/versions/roon-ir-remote/bin/python /home/${LOGNAME}/roon-ir-remote/roon_remote.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOT

# Den Dienst aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable --now roon-ir-remote.service

# Den Status überprüfen
sudo systemctl status roon-ir-remote.service
```

---

### **Schritt 7: Die Protokolle kurz beobachten:**
```bash
journalctl -b -u roon-ir-remote.service -f
```

Drücken Sie `Ctrl+C`, sobald Sie sich vergewissert haben, dass alles wie erwartet funktioniert.

---

### **Schritt 8: Das Skript `set-roon-zone` installieren**
Es ist praktisch, ein Skript zu haben, mit dem Sie den Namen der Roon-Zone später bei Bedarf aktualisieren können. So installieren Sie es:
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone
sudo install -m 0755 set-roon-zone /usr/local/bin/
rm set-roon-zone
```

Um es zu nutzen, melden Sie sich einfach auf dem Diretta-Host-Computer an und geben Sie ein:
```bash
set-roon-zone
```
Folgen Sie den Anweisungen, um den neuen Namen für Ihre Roon-Zone einzugeben. Möglicherweise müssen Sie das Root-Passwort eingeben, damit die Änderungen wirksam werden.

**Hinweis: Ein besserer Weg, die Zone einzustellen**
Obwohl dieses Skript einwandfrei funktioniert, ist die empfohlene Methode zur Änderung der Roon-Zone die Verwendung der Webanwendung AnCaolas Link System Control, die in [Anhang 4](#13-anhang-4-optionale-web-oberfläche-zur-systemsteuerung) beschrieben wird. Die Weboberfläche bietet eine eigene Seite zum Anzeigen und Bearbeiten des Zonennamens von Ihrem Smartphone oder Browser aus.

### **Schritt 9: Fertig! 📈**

> ---
> ### ✅ Checkpoint: Überprüfen Sie Ihr IR-Fernbedienungs-Setup
>
> Ihre IR-Fernbedienungs-Hardware und -Software sollten nun konfiguriert sein. Um das Setup zu überprüfen, fahren Sie mit [**Anhang 5**](#14-anhang-5-system-gesundheitschecks) fort und führen Sie den universellen Befehl **System-Gesundheitscheck** auf dem Diretta-Host aus.
>
> ---

Ihre IR-Fernbedienung sollte nun Roon steuern. Viel Spaß!

---

## 12. Anhang 3: Optionaler Purist-Modus
Auf dem Diretta-Target-Computer gibt es nur minimale Netzwerk- und Hintergrundaktivitäten, die nicht mit der Musikwiedergabe über das Diretta-Protokoll zusammenhängen. Einige Benutzer bevorzugen jedoch zusätzliche Maßnahmen, um die Wahrscheinlichkeit solcher Aktivitäten weiter zu verringern. Wir befinden uns bereits an der äußersten Grenze der Audioleistung, also warum nicht?

---
> KRITISCHE WARNUNG: NUR für das Diretta-Target
>
> Das `purist-mode`-Skript und alle Anweisungen in diesem Anhang sind ausschließlich für das Diretta-Target gedacht.
>
> Installieren oder führen Sie dieses Skript NICHT auf dem Diretta-Host aus. Andernfalls wird die Verbindung des Hosts zu Ihrem Hauptnetzwerk getrennt, wodurch er unerreichbar wird und nicht mehr mit Ihrem Roon Core oder Streaming-Diensten kommunizieren kann. Dies würde das gesamte System funktionsunfähig machen, bis Sie Konsolenzugriff (mit einer physischen Tastatur und einem Monitor) erlangen, um die Änderungen rückgängig zu machen.
---

### Schritt 1: Das `purist-mode`-Skript installieren **(nur auf dem Diretta-Target-Computer)**
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode
sudo install -m 0755 purist-mode /usr/local/bin
rm purist-mode

# Skript zur Anzeige des Purist-Modus-Status beim Login
cat <<'EOT' | sudo tee /etc/profile.d/purist-status.sh
#!/bin/sh
BACKUP_FILE="/etc/nsswitch.conf.purist-bak"

if [ -f "$BACKUP_FILE" ]; then
    echo -e '\n\e[1;32m✅ Purist Mode is ACTIVE.\e[0m System optimized for the highest sound quality.'
else
    echo -e '\n\e[1;33m⚠️ CAUTION: Purist Mode is DISABLED.\e[0m Background activity may impact sound quality.'
fi
EOT
```

Um es auszuführen, melden Sie sich einfach auf dem Diretta-Target an und geben Sie `purist-mode` ein:
```bash
purist-mode
```

Zum Beispiel:
```text
[audiolinux@diretta-target ~]$ purist-mode
This script requires sudo privileges. You may be prompted for a password.
🚀 Activating Purist Mode...
  -> Stopping time synchronization service (chronyd)...
  -> Disabling DNS lookups...
  -> Overriding gateway with high-priority blackhole route...

✅ Purist Mode is ACTIVE.
```

Hören Sie eine Weile hinein, um festzustellen, ob Ihnen der Klang (oder das beruhigende Gefühl) besser gefällt.

---

### Schritt 2: Den Purist-Modus standardmäßig aktivieren

Wenn Sie sich entschieden haben, den Klang mit aktiviertem Purist-Modus zu bevorzugen, machen Sie diesen zur Standardeinstellung nach jedem Neustart.

```bash
echo ""
echo "- Disabling Purist Mode to ensure a clean state"
purist-mode --revert

echo ""
echo "- Creating the Service to Revert to Standard Mode on Every Boot"
cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-revert-on-boot.service
[Unit]
Description=Revert Purist Mode on Boot to Ensure Standard Operation
After=network-online.target
Wants=network-online.target
Before=purist-mode-auto.service

[Service]
Type=oneshot
ExecStart=/usr/local/bin/purist-mode --revert

[Install]
WantedBy=multi-user.target
EOT

echo ""
echo "- Creating the Delayed Auto-Activation Service"
cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-auto.service
[Unit]
Description=Activate Purist Mode 60 seconds after boot
After=diretta-cache.service

[Service]
Type=oneshot
TimeoutStartSec=infinity
ExecStart=/bin/bash -c "until ping -c 1 -q 172.20.0.1 &>/dev/null; do sleep 2; done && sleep 60 && /usr/local/bin/purist-mode"

[Install]
WantedBy=multi-user.target
EOT

echo ""
echo "- Enabling the new services"
sudo systemctl daemon-reload
sudo systemctl enable purist-mode-revert-on-boot.service
sudo systemctl enable purist-mode-auto.service
```

---

### Schritt 3: Einen Wrapper um den Befehl `menu` installieren
Viele Funktionen in AudioLinux erfordern einen Internetzugang. Damit alles wie erwartet funktioniert, fügen wir einen Wrapper um den Befehl `menu` hinzu, der den Purist-Modus deaktiviert, während Sie das Menü verwenden, und ihn beim Verlassen des Menüs wieder aktiviert.

```bash
if grep -q menu_wrapper ~/.bashrc; then
  :
else
  echo ""
  echo "Add a wrapper around the menu command"
  cat <<'EOT' | tee -a ~/.bashrc

# Benutzerdefinierter Wrapper für das AudioLinux-Menü zur Verwaltung des Purist-Modus
menu_wrapper() {
  local was_active=false
  # Den anfänglichen Status des Purist-Modus überprüfen, indem nach der Backup-Datei gesucht wird.
  if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
    was_active=true
  fi

  # Wenn der Purist-Modus aktiv war, wird er für das Menü vorübergehend deaktiviert.
  if [ "$was_active" = true ]; then
    echo "Checking credentials to manage Purist Mode..."
    sudo -v

    echo "Temporarily disabling Purist Mode to run menu..."
    purist-mode --revert > /dev/null 2>&1 # Leise zurücksetzen
  fi

  # Den originalen menu-Befehl aufrufen
  /usr/bin/menu

  # Wenn der Purist-Modus zuvor aktiv war, wird er jetzt wieder aktiviert.
  if [ "$was_active" = true ]; then
    echo "Re-activating Purist Mode..."
    purist-mode > /dev/null 2>&1 # Leise aktivieren
    echo "Purist Mode is active again."
  fi
}

# Den 'menu'-Befehl als Alias auf unsere neue Wrapper-Funktion legen
alias menu='menu_wrapper'
# Aliase zur Verwaltung des automatischen Purist-Modus-Dienstes
alias purist-mode-auto-enable='echo "Enabling Purist Mode on boot..."; purist-mode; sudo systemctl enable purist-mode-auto.service'
alias purist-mode-auto-disable='echo "Disabling Purist Mode on boot..."; purist-mode --revert; sudo systemctl disable --now purist-mode-auto.service'
EOT
fi

source ~/.bashrc
```

---

### Die Zustände des Purist-Modus verstehen

Das Purist-Modus-System ist flexibel gestaltet, sodass Sie es manuell steuern oder nach dem Systemstart automatisch aktivieren lassen können. Es arbeitet in zwei Hauptzuständen:

  * **Deaktiviert (Standard-Modus):**
    Dies ist der normale, voll funktionsfähige Zustand des Diretta-Targets. Das Netzwerk-Gateway ist aktiv, alle Dienste (`chronyd`, `argononed`) laufen und das Gerät arbeitet ohne Einschränkungen.

  * **Aktiviert (Purist-Modus):**
    Dies ist der optimierte Zustand für anspruchsvolles Hören. Das Netzwerk-Gateway wird getrennt, um Internetverkehr zu verhindern, und nicht benötigte Hintergrunddienste (einschließlich des Argon-ONE-Lüfters) werden gestoppt, um alle potenziellen Systemstörungen zu minimieren.

Diese Zustände werden auf zwei Arten verwaltet: **automatisch** beim Booten und **manuell** über die Befehlszeile.

#### Automatische Steuerung (Beim Booten)

Der Boot-Vorgang ist sicher und vorhersehbar gestaltet, mit einer optionalen automatischen Umschaltung in den Purist-Modus.

1.  **Zwingendes Zurücksetzen beim Booten:** Unabhängig von dem Zustand, in dem es heruntergefahren wurde, bootet das Diretta-Target **immer** zuerst im **Standard-Modus**. Dies ist eine wichtige Funktion, die sicherstellt, dass essenzielle Dienste wie die Netzwerkzeitsynchronisation korrekt ausgeführt werden können.

2.  **Optionale Auto-Aktivierung:** Wenn Sie die automatische Funktion aktiviert haben, wartet das System nach dem Booten 60 Sekunden und schaltet dann automatisch in den **Purist-Modus**. Dies bietet ein komfortables Benutzererlebnis für diejenigen, die immer im optimierten Zustand hören möchten.

#### Manuelle Steuerung (Interaktive Nutzung)

Sie haben jederzeit die volle interaktive Kontrolle über das System.

  * Um den Purist-Modus für eine Hörsitzung **manuell zu aktivieren**, melden Sie sich auf dem Diretta-Target-Computer an und führen Sie aus:

    ```bash
    purist-mode
    ```

  * Um den Purist-Modus **manuell zu deaktivieren** und zum Standardbetrieb zurückzukehren, führen Sie aus:

    ```bash
    purist-mode --revert
    ```

  * Um das **automatische Boot-Verhalten** zu steuern, verwenden Sie die praktischen Aliase auf dem Diretta-Target:

    ```bash
    # Dies aktiviert die automatische Aktivierung nach 60 Sekunden beim nächsten Booten
    purist-mode-auto-enable

    # Dies deaktiviert die automatische Aktivierung beim nächsten Booten
    purist-mode-auto-disable
    ```

---

## 13. Anhang 4: Optionale Web-Oberfläche zur Systemsteuerung

Dieser Anhang enthält Anweisungen zur Installation einer einfachen webbasierten Anwendung auf dem Diretta-Host. Diese Anwendung bietet eine benutzerfreundliche Oberfläche, auf die über ein Smartphone oder Tablet zugegriffen werden kann, um wichtige Funktionen Ihres Diretta-Systems zu verwalten, einschließlich des Purist-Modus auf dem Target und der Einstellungen für die Roon-IR-Fernbedienung auf dem Host.

> **KRITISCHE WARNUNG: Führen Sie diese Schritte sorgfältig aus.**
> Dieses Setup beinhaltet das Erstellen eines neuen Benutzers und das Ändern von Sicherheitseinstellungen. Befolgen Sie die Anweisungen genau, um sicherzustellen, dass das System sicher und funktionsfähig bleibt.

Das Setup ist in zwei Teile unterteilt: Zuerst konfigurieren wir das **Diretta-Target** so, dass es Befehle sicher akzeptiert, und zweitens installieren wir die Webanwendung auf dem **Diretta-Host**. Seien Sie jedoch aufmerksam, da wir häufig zwischen den Hosts wechseln.

---

### **Teil 1: Diretta-Target-Konfiguration**

Auf dem **Diretta-Target** erstellen wir einen neuen Benutzer mit sehr eingeschränkten Berechtigungen. Diesem Benutzer wird es nur gestattet, die spezifischen Befehle auszuführen, die zur Verwaltung des Purist-Modus erforderlich sind.

1.  **SSH-Verbindung zum Diretta-Target:**
    ```bash
    ssh diretta-target
    ```

2.  **Einen neuen Benutzer für die App erstellen:**
    Dieser Befehl erstellt einen neuen Benutzer namens `purist-app` und dessen Heimatverzeichnis. Eine gültige Shell ist erforderlich, damit nicht-interaktive SSH-Befehle funktionieren.
    ```bash
    sudo useradd --create-home --shell /bin/bash purist-app
    ```

3.  **Sichere Befehlsskripte erstellen:**
    Wir werden vier kleine, dedizierte Skripte erstellen. Dies sind die *einzigen* Aktionen, die die Web-App ausführen darf. Dies ist ein wichtiger Sicherheitsschritt.
    ```bash
    # Skript zum Abrufen des aktuellen Status, einschließlich des Lizenzstatus
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-status
    #!/bin/bash
    IS_ACTIVE="false"
    IS_AUTO_ENABLED="false"
    LICENSE_LIMITED="false"

    # Auf Purist-Modus prüfen
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
      IS_ACTIVE="true"
    fi

    # Prüfen, ob der Autostart aktiviert ist
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      IS_AUTO_ENABLED="true"
    fi

    # Den validierten Boot-Cache auf einen aktiven Evaluierungs-Link prüfen
    if [ ! -f /tmp/diretta_license_url.cache ] || grep -q "http" /tmp/diretta_license_url.cache; then
      LICENSE_LIMITED="true"
    fi

    # Alle Status-Flags als ein einzelnes JSON-Objekt ausgeben
    echo "{\"purist_mode_active\": $IS_ACTIVE, \"auto_start_enabled\": $IS_AUTO_ENABLED, \"license_needs_activation\": $LICENSE_LIMITED}"
    EOT

    # Skript zum Umschalten des Purist-Modus
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-mode
    # Skript zum Umschalten des Autostart-Dienstes
    if [[ "$1" == "--enforce" ]]; then
        # Absolute Erzwingung: Wenn es aktiv sein soll, führen Sie das
        # Baseline-Skript erneut aus, um wiederbelebte Standardrouten zu bereinigen.
        if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
            /usr/local/bin/purist-mode
        fi
    elif [ -f "/etc/nsswitch.conf.purist-bak" ]; then
        /usr/local/bin/purist-mode --revert
    else
        /usr/local/bin/purist-mode
    fi
    EOT

    # Skript zum Umschalten des Autostart-Dienstes
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-auto
    #!/bin/bash
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      systemctl disable --now purist-mode-auto.service
    else
      systemctl enable purist-mode-auto.service
    fi
    EOT

    # Das Skript zum Neustart des Diretta-Dienstes erstellen
    cat <<'EOT' | sudo tee /usr/local/bin/pm-restart-target
    #!/bin/bash
    # Startet den Diretta-ALSA-Target-Dienst neu.
    # Dieses Skript soll über sudo durch den purist-app-Benutzer aufgerufen werden.
    /usr/bin/systemctl restart diretta_alsa_target.service
    EOT

    # Das Skript zum Abrufen der Diretta-Lizenz-URL erstellen
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-license-url
    #!/bin/bash

    # Die einzige Aufgabe dieses Skripts ist es, die beim Booten erstellte Cache-Datei zu lesen.
    readonly CACHE_FILE="/tmp/diretta_license_url.cache"

    if [ -s "$CACHE_FILE" ]; then
        # Wenn der Cache existiert und Inhalt hat, diesen anzeigen.
        cat "$CACHE_FILE"
    else
        # Wenn nicht, einen hilfreichen Fehler nach stderr ausgeben und beenden.
        echo "Error: License cache not found or is empty." >&2
        exit 1
    fi
    EOT

    # Skript zum Einstellen der Verbindungsgeschwindigkeit erstellen
    cat <<'EOT' | sudo tee /usr/local/bin/pm-set-link
    #!/bin/bash
    # Profilskript zur Durchsetzung physischer Verbindungsgrenzen des Targets
    # Refaktoriert unter Verwendung expliziter Advertisement-Masken, um Hardware-Deadlocks zu verhindern

    SPEED="$1"

    if [ "$SPEED" = "10" ]; then
        echo "Scheduling 10Mbps clamp (Super Purist)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x002" >/dev/null 2>&1 < /dev/null &
    elif [ "$SPEED" = "100" ]; then
        echo "Scheduling 100Mbps clamp (Purist)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x008" >/dev/null 2>&1 < /dev/null &
    elif [ "$SPEED" = "1000" ]; then
        echo "Releasing clamps. Restoring full 10/100/1000 portfolio (Standard)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x03f" >/dev/null 2>&1 < /dev/null &
    else
        echo "Usage: $0 [10|100|1000]"
        exit 1
    fi
    EOT

    # Die neuen Skripte ausführbar machen
    sudo chmod -v +x /usr/local/bin/pm-*
    ```

4.  **Sudo-Berechtigungen erteilen:**
    Dieser Schritt ermöglicht es dem Benutzer `purist-app`, unsere vier neuen Skripte mit Root-Rechten und ohne die Notwendigkeit eines interaktiven Terminals auszuführen.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/purist-app
    # Sudo anweisen, kein TTY für den Benutzer purist-app zu erfordern
    Defaults:purist-app !requiretty

    # Dem Benutzer purist-app erlauben, die spezifischen Steuerungsskripte ohne Passwort auszuführen
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-status
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-mode
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-auto
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-restart-target
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-license-url
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-set-link
    EOT
    ```

5.  **Die Diretta-Lizenz-Cache-Datei beim Booten befüllen**
    Das Abrufen der Diretta-Lizenz-URL erfordert eine Internetverbindung. Wenn der Purist-Modus standardmäßig aktiviert ist, kann das Target die URL niemals abrufen. Beim Booten ist der Purist-Modus jedoch für 60 Sekunden deaktiviert, um die Uhrzeit einzustellen und nach einer Diretta-Lizenzaktivierung zu suchen. Wir können dieses Zeitfenster nutzen, um auch die URL abzurufen.
    ```bash
    # Das Skript herunterladen, die korrekten Berechtigungen setzen und im Systempfad platzieren
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh
    sudo install -m 0755 create-diretta-cache.sh /usr/local/bin/
    rm create-diretta-cache.sh

    # Einen Dienst zum Befüllen des Lizenzstatus-Caches erstellen
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta-cache.service
    [Unit]
    Description=Asynchronous Diretta License Cache Collector
    After=network.target purist-mode-revert-on-boot.service
    Before=purist-mode-auto.service

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    # Blockieren Sie die Ausführung sauber hier, bis der Host auf ein Ping antwortet
    TimeoutStartSec=infinity
    ExecStartPre=/bin/bash -c "until ping -c 1 -q 172.20.0.1 &>/dev/null; do sleep 2; done"
    ExecStart=/usr/local/bin/create-diretta-cache.sh
    Restart=no

    [Install]
    WantedBy=multi-user.target
    EOT

    # Systemd neu laden, um die aktualisierte Drop-in-Konfiguration zu übernehmen
    sudo rm -rf /etc/systemd/system/purist-mode-revert-on-boot.service.d
    sudo systemctl daemon-reload
    sudo systemctl enable diretta-cache.service

    # Führen Sie das Skript einmal manuell aus
    sudo /usr/local/bin/create-diretta-cache.sh
    ls -l /tmp/diretta_license_url.cache
    ```

---

### **Teil 2: Diretta-Host-Konfiguration**

Nun führen wir auf dem **Diretta-Host** alle Schritte zur Installation und Konfiguration der Webanwendung durch. Sie sollten für diesen gesamten Abschnitt als Benutzer `audiolinux` eingeloggt sein.

1.  **SSH-Verbindung zum Diretta-Host:**
    ```bash
    ssh diretta-host
    ```

2.  **Einen dedizierten SSH-Schlüssel generieren:**
    Dies erstellt ein neues SSH-Schlüsselpaar speziell für die Web-App. Es wird keine Passphrase vergeben.
    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/purist_app_key -N "" -C "purist-app-key"
    ```

3.  **SSH konfigurieren und den Schlüssel auf das Target kopieren:**
    Dieser Schritt erstellt eine SSH-Konfiguration und kopiert den öffentlichen Schlüssel sicher auf das Target.
    ```bash
    mkdir -p ~/.ssh
    chmod go-rwx ~/.ssh
    cat <<'EOT' > ~/.ssh/config
    Host diretta-target target
        StrictHostKeyChecking no
        UserKnownHostsFile /dev/null
        GlobalKnownHostsFile /dev/null
        LogLevel ERROR
        ConnectTimeout 5
    EOT

    # Den öffentlichen Schlüssel in das Heimatverzeichnis des Targets kopieren
    echo "--> Copying public key to the Target..."
    scp -o StrictHostKeyChecking=accept-new ~/.ssh/purist_app_key.pub diretta-target:
    ```

4.  **Den Schlüssel auf dem Target autorisieren:**
    ```bash
    ssh diretta-target

    ```

    Sobald Sie auf dem Target eingeloggt sind, führen Sie dieses Skript aus, um den Schlüssel für den Benutzer 'purist-app' einzurichten
    ```bash
    echo "--> Running setup script on the Target..."
    set -e
    # Den öffentlichen Schlüssel aus der soeben kopierten Datei lesen
    PUB_KEY=$(cat purist_app_key.pub)

    # Sicherstellen, dass das .ssh-Verzeichnis existiert und die korrekten Berechtigungen hat
    sudo mkdir -p /home/purist-app/.ssh
    sudo chmod 0700 /home/purist-app/.ssh

    # Die Datei authorized_keys mit den erforderlichen Sicherheitsbeschränkungen erstellen
    echo "command=\"sudo \$SSH_ORIGINAL_COMMAND\",from=\"172.20.0.1\",no-port-forwarding,no-x11-forwarding,no-agent-forwarding,no-pty ${PUB_KEY}" | sudo tee /home/purist-app/.ssh/authorized_keys > /dev/null

    # Endgültige Besitzer und Berechtigungen setzen
    sudo chown -R purist-app:purist-app /home/purist-app/.ssh
    sudo chmod 0600 /home/purist-app/.ssh/authorized_keys

    # Die kopierte öffentliche Schlüsseldatei bereinigen
    rm purist_app_key.pub

    echo "✅ SSH key has been successfully authorized on the Target."
    ```

5.  **Die Remote-Befehle manuell testen (Empfohlen):**
    Bevor Sie die Web-App starten, testen Sie die schreibgeschützten Remote-Befehle vom Terminal des **Diretta-Hosts** aus, um zu bestätigen, dass das Backend funktioniert.
    ```bash
    # Den Status-Befehl testen (sollte eine JSON-Zeichenkette zurückgeben)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-status'

    # Den Befehl zum Abrufen des Lizenzstatus testen.
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-license-url'
    ```

6.  **Python über pyenv** auf dem **Diretta-Host** installieren (Sie können diesen Schritt überspringen, wenn Sie dies bereits für die IR-Fernbedienung getan haben)
    Installieren Sie `pyenv` und die neueste stabile Python-Version.
    ```bash
    # Build-Abhängigkeiten installieren
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

    # Pyenv nur installieren, falls noch nicht installiert
    if [ ! -d "$HOME/.pyenv" ]; then
      echo "--- Installing pyenv ---"
      curl -fsSL https://pyenv.run | bash
    else
      echo "--- pyenv is already installed. Skipping installation. ---"
    fi

    # Shell für pyenv konfigurieren
    if grep -q 'pyenv init' ~/.bashrc; then
      :
    else
      cat <<'EOT'>> ~/.bashrc

    export PYENV_ROOT="$HOME/.pyenv"
    [[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init - bash)"
    eval "$(pyenv virtualenv-init -)"
    EOT
    fi

    # Die Datei einlesen (source), um pyenv in der aktuellen Shell verfügbar zu machen
    . ~/.bashrc

    # Die neueste Python-Version nur installieren und setzen, falls noch nicht installiert
    PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
    if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
      # Gesamten Arbeitsspeicher in MB ermitteln
      TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

      if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- Physical RAM is ${TOTAL_MEM}MB. Limiting to 1 core to prevent lockup. ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
      else
        echo "--- Physical RAM is ${TOTAL_MEM}MB. Proceeding with parallel build. ---"
      fi

      echo "--- Installing Python ${PYVER}. This will take several minutes... ---"
      pyenv install $PYVER
      [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
    else
      echo "--- Python ${PYVER} is already installed. ---"
    fi

    pyenv global $PYVER
    ```

    **Hinweis:** Es ist normal, dass der Teil `Installing Python-3.14.5...` etwa 10 Minuten dauert, da Python aus den Quellen kompiliert wird. Geben Sie nicht auf! Entspannen Sie sich bei schöner Musik über Ihre neue Diretta-Zone in Roon, während Sie warten. Diese sollte verfügbar sein, während Python auf dem Host installiert wird.

7.  **Avahi und Python-Abhängigkeiten auf dem Diretta-Host installieren:**

    **Note:** OPTIONAL – Wenn Sie mehr als einen Diretta-Host in Ihrem Netzwerk haben, stellen Sie bitte sicher, dass diese eindeutige Namen besitzen. Sie können einen Befehl wie den folgenden verwenden, um diesen umzubenennen, bevor Sie fortfahren:

    ```bash
    # Optional den Diretta-Host umbenennen, falls dies Ihr zweiter Aufbau im selben Netzwerk ist
    sudo hostnamectl set-hostname diretta-host2
    ```

    Dieser Schritt wird auf dem **Diretta-Host** ausgeführt. Er installiert den Avahi-Daemon und verwendet eine `requirements.txt`-Datei, um Flask in einer dedizierten virtuellen Umgebung zu installieren.
    ```bash
    # Avahi für die .local-Namensauflösung installieren
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm avahi

    # Den Namen der USB-Ethernet-Schnittstelle dynamisch ermitteln (z. B. enp... oder enu1...)
    USB_INTERFACE=$(ip -o link show | awk -F': ' '/en[pu]/{print $2}')

    # Ein Konfigurations-Override für Avahi erstellen, um es auf die USB-Schnittstelle zu isolieren
    echo "--- Configuring Avahi to use interface: $USB_INTERFACE ---"
    sudo mkdir -p /etc/avahi/avahi-daemon.conf.d
    cat <<EOT | sudo tee /etc/avahi/avahi-daemon.conf.d/interface-scoping.conf
    [server]
    allow-interfaces=$USB_INTERFACE
    deny-interfaces=end0
    EOT

    # Den Avahi-Daemon aktivieren und starten
    sudo systemctl enable --now avahi-daemon.service

    # Das Anwendungsverzeichnis und die Requirements-Datei erstellen
    mkdir -p ~/purist-mode-webui
    echo "Flask" > ~/purist-mode-webui/requirements.txt

    # Eine virtuelle Umgebung erstellen und Abhängigkeiten installieren
    echo "--- Setting up Python environment for the Web UI ---"
    # Die virtuelle Umgebung nur erstellen, falls sie noch nicht existiert
    if ! pyenv versions --bare | grep -q "^purist-webui$"; then
      echo "--- Creating 'purist-webui' virtual environment ---"
      pyenv virtualenv purist-webui
    else
      echo "--- 'purist-webui' virtual environment already exists ---"
    fi
    pyenv activate purist-webui
    pip install -r ~/purist-mode-webui/requirements.txt
    pyenv deactivate
    ```

8.  **Die Flask-App installieren:**
    Laden Sie das Python-Skript direkt von GitHub in das Anwendungsverzeichnis auf dem **Diretta-Host** herunter.
    ```bash
    curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py -o ~/purist-mode-webui/app.py
    ```

9. **Port-Binding-Berechtigung erteilen**
    Wir müssen der Python-Ausführungsdatei die Berechtigung erteilen, sich an Port 80 des Diretta-Hosts zu binden, damit unsere Web-App starten kann.
    ```bash
    # Das Paket installieren, welches den Befehl 'setcap' bereitstellt
    sudo pacman -S --noconfirm --needed libcap

    # Den realen Pfad zur Python-Ausführungsdatei ermitteln, unter Auflösung aller symbolischen Links
    PYTHON_EXEC=$(readlink -f /home/audiolinux/.pyenv/versions/purist-webui/bin/python)

    # Die Port-Binding-Berechtigung direkt der endgültigen Python-Ausführungsdatei erteilen
    echo "Applying capability to the real file: ${PYTHON_EXEC}"
    sudo setcap 'cap_net_bind_service=+ep' "$PYTHON_EXEC"
    ```

10. **Sudo-Berechtigungen auf dem Host erteilen:**
    Dieser Schritt ist entscheidend, um der Webanwendung das Neustarten der erforderlichen Roon-Dienste ohne Passworteingabe zu ermöglichen.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/webui-restarts
    # Dem Web-UI (das als audiolinux läuft) erlauben, Host-Profile durchzusetzen und Dienste neu zu starten
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl daemon-reload
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roon-ir-remote.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roonbridge.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart diretta_alsa.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/ethtool -s end0 *
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/mv /tmp/setting.inf.tmp /opt/diretta-alsa/setting.inf
    EOT
    sudo chmod 0440 /etc/sudoers.d/webui-restarts
    ```

11. **Die Flask-App interaktiv testen:**
    Führen Sie nun die App über die Befehlszeile auf dem **Diretta-Host** aus, um sicherzustellen, dass sie korrekt startet.
    ```bash
    cd ~/purist-mode-webui
    pyenv activate purist-webui
    python app.py
    ```
    Sie sollten eine Ausgabe sehen, die anzeigt, dass der Flask-Server auf Port **8080** gestartet wurde. Rufen Sie von einem anderen Gerät aus [http://diretta-host.local:8080](http://diretta-host.local:8080) auf. Wenn es funktioniert, kehren Sie zum SSH-Terminal zurück und drücken Sie `Ctrl+C`, um den Server zu stoppen.

12. **Den `systemd`-Dienst erstellen:**
    Dieser Dienst führt die Web-App automatisch auf dem **Diretta-Host** aus, wobei die korrekte Python-Ausführungsdatei aus unserer virtuellen `pyenv`-Umgebung verwendet wird.
    ```bash
    cat <<EOT | sudo tee /etc/systemd/system/purist-webui.service
    [Unit]
    Description=Purist Mode Web UI
    After=network-online.target
    Wants=network-online.target

    [Service]
    Type=simple
    User=${LOGNAME}
    Group=${LOGNAME}
    WorkingDirectory=/home/${LOGNAME}/purist-mode-webui
    ExecStart=/home/${LOGNAME}/.pyenv/versions/purist-webui/bin/python app.py
    Restart=on-failure
    RestartSec=5

    [Install]
    WantedBy=multi-user.target
    EOT
    ```

13. **Die Web-App aktivieren und starten:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl stop purist-webui.service
    sudo systemctl enable --now purist-webui.service
    ```

14. **Die Protokolle kurz beobachten:**
    ```bash
    journalctl -b -u purist-webui.service -f
    ```

15. **Das Web-UI mit der endgültigen URL testen:**
    Öffnen Sie einen Browser unter [http://diretta-host.local](http://diretta-host.local) und beobachten Sie die Protokolle auf Fehler.

Drücken Sie `Ctrl+C`, sobald Sie sich vergewissert haben, dass alles wie erwartet funktioniert.

---

### **Zugriff auf das Web-UI**

Sie sind startklar! Öffnen Sie einen Webbrowser auf Ihrem Smartphone, Tablet oder Computer, der mit demselben Netzwerk wie der Diretta-Host verbunden ist. Navigieren Sie zur Hauptseite:

[http://diretta-host.local](http://diretta-host.local)

---
> **Ein Hinweis zu Sicherheitswarnungen des Browsers**
> Wenn Sie http://diretta-host.local zum ersten Mal besuchen, zeigt Ihr Browser wahrscheinlich eine Sicherheitswarnung an, dass die Verbindung nicht sicher sei. Dies ist zu erwarten und kann sicher umgangen werden. Die Warnung erscheint, weil die Verbindung Standard-`HTTP` anstelle von verschlüsseltem `HTTPS` verwendet – eine bewusste Entscheidung, um den Verarbeitungsaufwand auf dem Audiogerät zu minimieren. Da die App nur in Ihrem privaten Heimnetzwerk läuft und keine sensiblen Daten verarbeitet, können Sie getrost auf „Weiter zur Website“ klicken.
---

Auf der Startseite führt Sie eine Navigationsleiste am oberen Rand zu den verschiedenen Bedienfeldern:

* **Home:** Die Hauptseite mit Links zu den verschiedenen Anwendungen.

* **Purist-Modus-App:** Diese Seite enthält die Steuerelemente zum Umschalten des Purist-Modus und seines Autostart-Verhaltens auf dem Diretta-Target. Sie aktualisiert sich alle 30 Sekunden automatisch, um den aktuellen Status anzuzeigen. Sie enthält auch die Schaltfläche „Dienste neu starten“ zur Verwendung nach einer Diretta-Lizenzaktivierung.

* **IR-Fernbedienung-App:** Wenn Sie die Einrichtung der IR-Fernbedienung abgeschlossen haben (Anhang 2), wird dieser Link angezeigt. Diese Seite bietet ein einfaches Formular zum Anzeigen und Aktualisieren des Namens der Roon-Zone, die Ihre Fernbedienung steuern soll. Diese Seite aktualisiert sich nicht automatisch, sodass Sie sich so viel Zeit nehmen können, wie Sie für Ihre Änderungen benötigen.

### 🔗 Hinweis zur vollen Funktionalität des Web-UI

Um die vollen Funktionen des System-Control-Web-UI freizuschalten – insbesondere die Anpassung der Netzwerk-**Verbindungsgeschwindigkeit** (Link Speed) und das Umschalten auf **Super Purist** – müssen Sie auch die Hardware- und Dienstekonfigurationen ausführen, die in [**Anhang 8: Optionale puristische Netzwerkgeschwindigkeiten**](#17-hang-8-optionale-puristische-netzwerkgeschwindigkeiten) beschrieben sind. Die Weboberfläche verlässt sich direkt auf die in diesem Abschnitt eingerichteten Skripte, Flags und Dienste, um die physischen Geschwindigkeitsgrenzen Ihrer Punkt-zu-Punkt-Verbindung erfolgreich zu ändern und durchzusetzen.

> ---
> ### ✅ Checkpoint: Überprüfen Sie Ihr Web-UI-Setup
>
> Das Purist-Modus-Web-UI sollte nun betriebsbereit sein. Um alle Komponenten dieser komplexen Funktion zu überprüfen, fahren Sie mit [**Anhang 5**](#14-anhang-5-system-gesundheitschecks) fort und führen Sie den universellen Befehl **System-Gesundheitscheck** sowohl auf dem Host als auch auf dem Target aus.
>
> ---

## 14. Anhang 5: System-Gesundheitschecks

Nach dem Ausfüllen wichtiger Abschnitte dieser Anleitung ist es ratsam, einen schnellen Qualitätssicherungs-Check (QA) durchzuführen, um zu überprüfen, ob alles korrekt konfiguriert ist.

Wir haben ein intelligentes Skript erstellt, das automatisch erkennt, ob Sie es auf dem **Diretta-Host** oder dem **Diretta-Target** ausführen, und die entsprechenden Überprüfungen vornimmt.

### **So führen Sie den Check aus**

Führen Sie auf dem Host oder dem Target den folgenden einzelnen Befehl aus. Er lädt das QA-Skript herunter und führt es aus, was einen detaillierten Bericht über den Status Ihres Systems liefert.

```bash
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh | sudo bash
```

---

## 15. Anhang 6: Optionales Echtzeit-Leistungstuning

Die folgenden Schritte sind optional, werden aber Benutzern empfohlen, die das absolute Maximum an Leistung aus ihrem Diretta-Setup herausholen möchten. Die Strategie basiert auf Ratschlägen des AudioLinux-Autors Piero und zielt darauf ab, sowohl auf dem Host- als auch auf dem Target-Gerät eine möglichst stabile und elektrisch rauscharme Umgebung zu schaffen.

Dies wird erreicht, indem **CPU-Isolierung** genutzt wird, um bestimmte Prozessorkerne ausschließlich Audioaufgaben zuzuweisen und sie so vom restlichen Betriebssystem abzuschirmen, sowie durch die präzise Abstimmung von **Echtzeitprioritäten** (Realtime priorities), damit der Audiodatenpfad niemals unterbrochen wird.

> **Hinweis:** Dies ist ein fortgeschrittener Tuning-Prozess. Bitte stellen Sie sicher, dass Ihr Diretta-Kernsystem voll funktionsfähig ist, indem Sie die Abschnitte 1–9 der Hauptanleitung abschließen, bevor Sie fortfahren. Eine angemessene Kühlung für beide Raspberry Pi-Geräte ist unerlässlich.

---

### **Teil 1: Optimierung des Diretta-Targets**

Das Ziel für das Target ist es, es in einen reinen Audio-Endpunkt mit geringer Latenz zu verwandeln. Wir werden die Diretta-Anwendung auf einem einzelnen, dedizierten CPU-Kern isolieren und ihr eine hohe, aber nicht übermäßige Echtzeitpriorität zuweisen.

#### **Schritt 6.1: Einen CPU-Kern für die Audioanwendung isolieren**

Dieser Schritt reserviert einen CPU-Kern exklusiv für die Diretta-Target-Anwendung.

1.  SSH-Verbindung zum Diretta-Target:
    ```bash
    ssh diretta-target
    ```
2.  Rufen Sie das AudioLinux-Menüsystem auf:
    ```bash
    menu
    ```
3.  Navigieren Sie zum Menü **ISOLATED CPU CORES configuration** (unter **SYSTEM menu**).

4.  Bestätigen Sie, dass isolated cores deaktiviert ist. Wenn nicht, verwenden Sie Option 3, um es zu deaktivieren:
    ```text
    ISOLATED CORES CONFIGURATION
    This option will divide CPU cores in 2 or more sets: one for audio services, one for system processes
    After you can specify the CPU core set used by each audio service
    You can also assign Audio or Network IRQ to specific cores

    Isolated cores is disabled

    Please chose your option:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    ```

5.  Navigieren Sie zurück zum Menü **ISOLATED CPU CORES configuration** (unter **SYSTEM menu**). Folgen Sie den Eingabeaufforderungen genau wie unten gezeigt, um die **Kerne 2 und 3** zu isolieren und die Diretta-Anwendung diesen zuzuweisen.
    ```text
    Please chose your option:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    1

    How many groups do you want to create? (1 or more)
    ?1
    Please type the cores of the group 1:
    ?2,3

    Type the service that should be confined to group 1...
    ?diretta_alsa_target

    Please type the Address (iSerial) number of your card(s)...
    ?end0
    ```

6.  Nachdem der Vorgang abgeschlossen ist, kehren Sie zum Terminal zurück.

> **Ein Hinweis zur automatischen IRQ-Affinität:** Sie werden vielleicht bemerken, dass das Skript meldet, es habe auch die `end0`-Netzwerk-IRQs auf demselben Kern isoliert. Dies ist kein Fehler, sondern eine intelligente Optimierung. Das Skript heftet (pinnt) die Netzwerk-Interrupts automatisch an denselben Kern wie die Anwendung, die das Netzwerk nutzt, wodurch ein möglichst effizienter Datenpfad entsteht.

#### **Schritt 6.2: Den veralteten `rtapp`-Timer deaktivieren**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **Schritt 6.3: Neustart, um die Änderungen zu übernehmen.**
```bash
sudo sync && sudo reboot
```

---

### **Teil 2: Optimierung des Diretta-Hosts**

Das Ziel für den Host ist es, den Diretta-Dienst-Threads dedizierte Verarbeitungsressourcen bereitzustellen, jedoch ohne hohe Echtzeitprioritäten zu verwenden. CPU-Isolierung ist hier ein mächtigeres Werkzeug, da sie verhindert, dass die Prozesse überhaupt unterbrochen werden.

#### **Schritt 6.4: CPU-Kerne für Audioanwendungen isolieren**

Dieser Schritt reserviert zwei CPU-Kerne für die Verarbeitung der Diretta-Host-Dienst-Threads.

1.  SSH-Verbindung zum Diretta-Host:
    ```bash
    ssh diretta-host
    ```
2.  Rufen Sie das AudioLinux-Menüsystem auf:
    ```bash
    menu
    ```
3.  Navigieren Sie zum Menü **ISOLATED CPU CORES configuration** (unter **SYSTEM menu**).

4.  Bestätigen Sie, dass isolated cores deaktiviert ist. Wenn nicht, verwenden Sie Option 3, um es zu deaktivieren:
    ```text
    ISOLATED CORES CONFIGURATION
    This option will divide CPU cores in 2 or more sets: one for audio services, one for system processes
    After you can specify the CPU core set used by each audio service
    You can also assign Audio or Network IRQ to specific cores

    Isolated cores is disabled

    Please chose your option:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    ```

5.  Navigieren Sie zurück zum Menü **ISOLATED CPU CORES configuration** (unter **SYSTEM menu**). Folgen Sie den Aufforderungen, um die **Kerne 2 und 3** zu isolieren und sie Diretta ALSA zuzuweisen.
    ```text
    Please chose your option:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    1

    How many groups do you want to create? (1 or more)
    ?1
    Please type the cores of the group 1:
    ?2,3

    Type the service that should be confined to group 1...
    ?diretta_alsa

    Please type the Address (iSerial) number of your card(s)...
    ?end0
    ```

6.  Nachdem der Vorgang abgeschlossen ist, kehren Sie zum Terminal zurück.

---

#### **Schritt 6.5: Den veralteten `rtapp`-Timer deaktivieren**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **Schritt 6.6: Neustart, um die Änderungen zu übernehmen.**
```bash
sudo sync && sudo reboot
```

## 16. Anhang 7: Optionale IRQ- und Thread-Optimierungen

### Part 1: USB-Pfad-Isolierung auf dem Diretta-Target
Standardmäßig können USB-Interrupts selbst bei isolierten CPU-Kernen immer noch mit den Ressourcen auf den „unruhigen“ Systemkernen (0 und 1) konkurrieren. Dieses Skript identifiziert dynamisch den spezifischen USB-Controller, an den Ihr DAC angeschlossen ist, und heftet (pinnt) dessen Hardware-Interrupts an Ihre isolierten Audiokerne (2 und 3). Beim Raspberry Pi 5 werden die USB-Controller vom RP1-Chip verwaltet, wodurch wir Hardware-Interrupts an bestimmte Kerne leiten können.

**Hinweis:** Diese Optimierung ist beim Raspberry Pi 4 aufgrund hardwareseitig blockierter Interrupts nicht anwendbar.

1.  Stellen Sie sicher, dass Ihr DAC eingeschaltet und mit dem Target verbunden ist.
2.  Starten Sie die Musikwiedergabe auf dem Diretta-Target. Dies stellt sicher, dass das Skript aktiven Interrupt-Verkehr erkennen kann.
3.  Führen den folgenden Befehl auf dem Diretta-Target aus:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/usb-isolation.sh | sudo bash
    ```
4.  Starten Sie das System neu, um die Änderungen zu übernehmen:
    ```bash
    sudo sync && sudo reboot
    ```

**Was dies bewirkt:** Das Skript lokalisiert den aktiven DAC-Pfad (z. B. xhci-hcd:usb1 oder xhci-hcd:usb3). Anschließend fügt es die spezifische Kennung zu Ihrer AudioLinux-Isolierungsgruppe hinzu, um einen zu 100 % isolierten Datenpfad vom Netzwerkeingang bis zum USB-Ausgang zu erstellen.

---

### Teil 2: Thread-Optimierung auf dem Diretta-Host

Mit den Echtzeit-Kernel-Optimierungen kann der Diretta-Host nun ein aggressiveres Paketintervall verarbeiten, was zu einer verbesserten Klangqualität führen kann. Dieser letzte Schritt reduziert den Parameter `CycleTime` von 800 auf 514 Mikrosekunden. Dieser kleinere Zeitabstand zwischen den Paketen stellt sicher, dass alle Inhalte bis zu DSD256 und DXD (32-Bit, 352.8 kHz) nur ein Paket pro Zyklus erfordern. Wir können Diretta-Threads auch bestimmten Kernen zuweisen.

1.  Melden Sie sich per SSH auf dem **Diretta-Host** an, falls Sie nicht bereits eingeloggt sind.
2.  Führen Sie den folgenden Befehl aus, um die optimierte Einstellung anzuwenden:
    ```bash
    cat <<'EOT' | sudo tee /opt/diretta-alsa/setting.inf
    [global]
    Interface=end0
    Broadcast=disable
    ScanOnlineStop=enable
    ScanInterval=
    TargetProfileLimitTime=200
    ThredMode=17
    InfoCycle=51400
    FlexCycle=disable
    CycleTime=514
    CycleMinTime=
    Debug=disable
    periodMax=32
    periodMin=16
    periodSizeMax=38400
    periodSizeMin=2048
    syncBufferCount=8
    alsaUnderrun=enable
    alsaUnderrunSleep=0
    alsaUnderrunClear=disable
    unInitMemDet=disable
    CpuSend=2
    CpuOther=3
    CPUFLOW=3
    LatencyBuffer=0
    disConnectDelay=enable
    singleMode=
    EOT
    ```
3.  Starten Sie den Diretta-Dienst neu, damit die Änderung wirksam wird:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart diretta_alsa.service
    ```

> ---
> ### ✅ Checkpoint: Echtzeit-Tuning überprüfen
>
> Ihr erweitertes Echtzeit-Tuning sollte nun abgeschlossen sein. Um alle Komponenten dieser neuen Konfiguration zu überprüfen, kehren Sie bitte zu [**Anhang 5**](#14-anhang-5-system-gesundheitschecks) zurück und führen Sie den universellen Befehl **System-Gesundheitscheck** sowohl auf dem Host als auch auf dem Target aus.
>
> ---

## 17. Anhang 8: Optionale puristische Netzwerkgeschwindigkeiten

**Ziel:** Reduzierung des elektrischen Rauschens und Verbesserung der Präzision des Betriebssystem-Schedulers durch Begrenzung der dedizierten Netzwerkverbindungsgeschwindigkeit und explizites Deaktivieren von Energy Efficient Ethernet (EEE).

Obwohl es kontraintuitiv erscheint, kann die Reduzierung der Verbindungsgeschwindigkeit von 1 Gbit/s auf 100 Mbit/s (oder sogar 10 Mbit/s) auf der dedizierten Verbindung (`end0`) die Klangqualität verbessern. Die niedrigere Betriebsfrequenz von 100BASE-TX (31,25 MHz gegenüber 62,5 MHz) erzeugt weniger Rauschen (RFI). Im Extremfall senkt eine Reduzierung auf 10 Mbit/s die Frequenz auf nur noch 10 MHz. Darüber hinaus verhindert die Deaktivierung von EEE, dass die Verbindung in den Ruhezustand wechselt, was Latenzspitzen (Flapping) eliminiert und eine absolut stabile Verbindung auf der Raspberry Pi 5-Hardware gewährleistet.

> ---
> ### 🎧 Deep Dive: Warum ein Limit auf 10 Mbit/s klangliche „Ruhe“ bringt
>
> Die Beschränkung Ihrer dedizierten Audioverbindung auf 10 Mbit/s bringt strikte Formatbeschränkungen mit sich – die Wiedergabe wird auf maximal **natives DSD64** und **32-Bit/96 kHz PCM** begrenzt. Für Hörer, die der Redbook-CD-Qualität oder standardmäßigen High-Res-Dateien den Vorzug geben, bringt dieser Kompromiss jedoch erhebliche klangliche Vorteile, da die eigentlichen Ursachen digitaler Schärfe angegangen werden.
>
> * **Drastisch niedrigere Trägerfrequenzen:** Standard-Gigabit-Ethernet arbeitet mit einem Hochfrequenz-Trägersignal von 62,5 MHz (unter Verwendung einer komplexen Multi-Level-Codierung). Die Reduzierung auf 100 Mbit/s senkt diese auf 31,25 MHz. Der Schritt hinunter zu einer 10-Mbit/s-Verbindung (10BASE-T) nutzt ein wunderbar einfaches Manchester-Codierungsverfahren, das mit einer nativen Trägerfrequenz von nur **10 MHz** arbeitet. Diese enorme Reduzierung der Betriebsfrequenz verringert die im Gehäuse und entlang des Kabels entstehenden Hochfrequenzstörungen (RFI) erheblich.
> * **Reduzierter Verarbeitungsaufwand auf dem Target:** Netzwerke mit hoher Bandbreite zwingen die Netzwerkkarte (NIC) und die CPU dazu, Datenpakete in einem schnellen, aggressiven Rhythmus zu verarbeiten. Indem Sie die Verbindungsgeschwindigkeit auf den tatsächlichen Bedarf von Standard-Audiodaten begrenzen, reduzieren Sie die Menge an Netzwerk-Interrupts, die das Betriebssystem des Targets verarbeiten muss, drastisch.
> * **Synergie mit der Kernphilosophie von Diretta:** Das gesamte Ziel des Diretta-Protokolls besteht darin, stoßweise Verarbeitung zu eliminieren und die Stromaufnahme zu stabilisieren. Eine 10-Mbit/s-Leitung fungiert als physischer Ausgleicher für den Datenfluss und verhindert die Hochgeschwindigkeits-Datenspitzen, die Stromversorgungsschwankungen verursachen.
>
> Das Ergebnis dieser „Super Purist“-Einschränkung ist ein sofort spürbares Absinken des digitalen Grundrauschens. Hörer berichten häufig von einer breiteren, entspannteren Klangbühne, einer saubereren Einschwinggeschwindigkeit im Hochtonbereich und einem allgemeinen Gefühl von analoger Leichtigkeit und Ruhe, das perfekt zu dem passt, was AudioLinux und Diretta zu erreichen versuchen.
> ---

> **Hinweis:** Sie sehen möglicherweise „buffer low“-Warnungen in den Target-Protokollen (wobei der `LatencyBuffer` auf 1 sinkt). Dies ist ein normales Verhalten aufgrund der erhöhten Serialisierungslatenz der langsameren Verbindung und führt nicht zu hörbaren Aussetzern.

### Schritt 1: Host und Target konfigurieren (EEE deaktivieren)

Energy Efficient Ethernet (EEE) kann bei manchen Hardwarekombinationen zu Verbindungsinstabilitäten führen. Wir werden einen Dienst erstellen, um EEE sowohl auf dem Host als auch auf dem Target explizit zu deaktivieren, um ein konsistentes Verhalten zu gewährleisten.

**Erstellen Sie den Deaktivierungsdienst:** *(Sowohl auf dem Host als auch auf dem Target ausführen)*

```bash
cat <<'EOT' | sudo tee /etc/systemd/system/disable-eee.service
[Unit]
Description=Disable EEE on end0 for Link Stability
After=network.target
BindsTo=sys-subsystem-net-devices-end0.device
After=sys-subsystem-net-devices-end0.device

[Service]
Type=oneshot
# Bis zu 5 Sekunden warten, bis die Schnittstelle tatsächlich als UP (aktiv) angezeigt wird
ExecStartPre=/usr/bin/bash -c 'for i in {1..5}; do if ip link show end0 | grep -q "UP"; then exit 0; fi; sleep 1; done; exit 1'
# Now set the hardware optimization
ExecStart=-/usr/bin/ethtool -s end0 advertise 0x03f
ExecStart=-/usr/bin/ethtool --set-eee end0 eee off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

sudo systemctl daemon-reload
sudo systemctl enable --now disable-eee.service
```

### Schritt 2: Das Target markieren (Für die Qualitätssicherung)

Um sicherzustellen, dass das **Target-QA-Skript** weiß, dass es diese spezifische Konfiguration validieren soll, erstellen Sie eine Markierungsdatei auf dem Target:

```bash
sudo touch /etc/diretta-100m
```

### Schritt 3: Den Host konfigurieren (Geschwindigkeitsbegrenzung)
Wir werden auf dem **Host** einen Dienst erstellen, der diesen zwingt, *entweder* 10 Mbit/s oder 100 Mbit/s Vollduplex anzubieten, je nachdem, ob der „Super Purist“-Modus aktiviert ist. Das Target wird die Geschwindigkeitsänderung automatisch erkennen und sich anpassen.

**Erstellen Sie das Begrenzungsskript und den Dienst:** *(Nur auf dem Host ausführen)*
```bash
cat <<'EOT' | sudo tee /usr/local/bin/set-link-speed.sh
#!/bin/bash
# Verbindungsgeschwindigkeit basierend auf dem Super Purist Web-UI-Flag unter Verwendung sicherer Advertisement-Masken festlegen
FLAG_FILE="/home/audiolinux/purist-mode-webui/super_purist.flag"
INTERFACE="end0"

# WICHTIG: Bis zu 60 Sekunden warten, bis die physische Schnittstelle die Verbindungsschicht (Carrier Link Layer) initialisiert hat
echo "Synchronizing with physical link layer..."
for i in {1..60}; do
    if [ -f /sys/class/net/$INTERFACE/carrier ] && [ "$(cat /sys/class/net/$INTERFACE/carrier 2>/dev/null)" "==" "1" ]; then
        echo "Physical link layer detected after $i seconds."
        break
    fi
    sleep 1
done

# Die Advertisement-Maske basierend auf dem Flag-Zustand anwenden
if [ -f "$FLAG_FILE" ]; then
    echo "Super Purist flag detected. Advertising 10 Mbps Full Duplex..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x002
else
    echo "Standard/Purist mode. Advertising up to 100 Mbps Full Duplex..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x00a
fi

# Plattformspezifische Behandlung der Aushandlung (Negotiation)
if grep -q "Raspberry Pi 4" /proc/device-tree/model 2>/dev/null; then
    echo "Raspberry Pi 4 detected. Triggering mandatory hardware renegotiation pulse..."
    /usr/bin/ethtool -r $INTERFACE
elif grep -q "Raspberry Pi 5" /proc/device-tree/model 2>/dev/null; then
    echo "Raspberry Pi 5 detected. Internal phylib automatic pulse relied upon; skipping manual reset."
else
    /usr/bin/ethtool -r $INTERFACE || true
fi

echo "Link speed policy successfully finalized."
EOT
sudo chmod +x /usr/local/bin/set-link-speed.sh

cat <<'EOT' | sudo tee /etc/systemd/system/limit-speed-100m.service
[Unit]
Description=Set end0 link speed for Audio Purity
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecCondition=/usr/bin/ip link show end0
ExecStart=/usr/local/bin/set-link-speed.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

echo "Enable and start the service:"
sudo systemctl daemon-reload
sudo systemctl enable --now limit-speed-100m.service
```

***
> **Hinweis zur Wiedergabelatenz:**
> Sie bemerken möglicherweise eine leichte Verzögerung zwischen dem Drücken von „Play“ und dem Hören von Musik (bis zu ca. 1 Sekunde). Dies ist ein normales Verhalten. Indem wir die Verbindung auf 10 oder 100 Mbit/s begrenzen, drosseln wir absichtlich den anfänglichen Datenschub, um sicherzustellen, dass die Verbindung auf einer niedrigeren, ruhigeren Frequenz arbeitet. Das System tauscht sofortige Startzeiten gegen einen stabileren, rauschärmeren Dauerzustand während der Wiedergabe ein.
***

>
>
> ---
>
> ### ✅ Checkpoint: Netzwerk-Konfiguration überprüfen
>
> Ihre dedizierte Netzwerkverbindung ist nun für den „Purist“-Betrieb mit 100 Mbit/s konfiguriert. Um zu überprüfen, ob der Host-Dienst aktiv ist und das Target die Geschwindigkeit korrekt ausgehandelt hat (erkannt über die Markierungsdatei), kehren Sie bitte zu [**Anhang 5**](#14-anhang-5-system-gesundheitschecks) zurück und führen Sie den universellen Befehl **System-Gesundheitscheck** sowohl auf dem Host als auch auf dem Target aus.
>
> ---

## 18. Anhang 9: Optional: Jumbo-Frames-Optimierung
Dieser Abschnitt optimiert den Transport für hohe Bandbreiteneffizienz.

#### **Schritt 1:** Schnittstellen vorbereiten

Wir müssen die Netzwerkschnittstellen vorübergehend auf MTU 9000 zwingen, um die Kernel-Unterstützung zu überprüfen und uns auf den Verbindungstest vorzubereiten.

**Führen Sie dies zuerst auf dem Target, dann auf dem Host aus:**

```bash
sudo sh -c 'ip link set end0 down; sleep 2; ip link set end0 mtu 9000; ip link set end0 up'
end0_mtu=$(ip link show dev end0 | awk '/mtu/ {print $5}')
if [[ "9000" == "$end0_mtu" ]]; then
  echo "SUCCESS: Kernel supports Jumbo frames. Proceed to Step 2."
else
  echo "STOP: Your kernel does not appear to support Jumbo frames."
fi
```

*Wenn Sie entweder auf dem Host oder auf dem Target „STOP“ sehen, fahren Sie nicht fort. Ihrem Kernel fehlt der erforderliche Patch.*

---

#### **Schritt 2:** Automatische Target-Konfiguration

Melden Sie sich per SSH auf dem Target (`diretta-target`) an und fügen Sie den folgenden Block ein.

```bash
# 1. Verbindungslimit erkennen (Full vs. Baby)
echo "Testing Link Capability..."
if ping -c 1 -w 1 -M "do" -s 8972 host &>/dev/null; then
  NEW_MTU=9000
  echo "SUCCESS: Full Jumbo Frames (9000 MTU) supported."
elif ping -c 1 -w 1 -M "do" -s 2004 host &>/dev/null; then
  NEW_MTU=2032
  echo "SUCCESS: Baby Jumbo Frames (2032 MTU) supported."
else
  echo "FAIL: Link cannot support Jumbo Frames. Reverting to safe defaults."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. System-Netzwerkkonfiguration anwenden
  echo "Configuring /etc/systemd/network/end0.network..."
  cat <<EOF | sudo tee /etc/systemd/network/end0.network
[Match]
Name=end0

[Link]
MTUBytes=$NEW_MTU

[Network]
Address=172.20.0.2/24
Gateway=172.20.0.1
DNS=1.1.1.1
EOF
  sudo systemctl daemon-reload
  sudo networkctl reload

  # 3. Diretta-Konfiguration anwenden
  echo "Configuring Diretta Target..."
  CONF="/opt/diretta-alsa-target/diretta_app_target_setting.inf"
  sudo sed -i '/^ExtEtherMTU=/d' $CONF
  sudo sed -i '/^EtherMTU=/d' $CONF

  if [ "$NEW_MTU" -eq 9000 ]; then
    echo "ExtEtherMTU=9014" | sudo tee -a $CONF
    echo "EtherMTU=9000" | sudo tee -a $CONF
  else
    echo "ExtEtherMTU=2046" | sudo tee -a $CONF
    echo "EtherMTU=2032" | sudo tee -a $CONF
  fi
  sudo systemctl restart diretta_alsa_target
  echo "DONE: Target optimization complete."
}

```

---

#### **Schritt 3:** Automatische Host-Konfiguration

Melden Sie sich per SSH auf dem Host (`diretta-host`) an und fügen den folgenden Block ein. Er prüft die Verbindung, konfiguriert die dauerhaften Netzwerkeinstellungen und aktualisiert Diretta.

```bash
# 1. Verbindungslimit erkennen (Full vs. Baby)
echo "Testing Link Capability..."
# Der Verbindung nach der manuellen MTU-Änderung einen Moment Zeit geben, sich zu beruhigen
sleep 2

if ping -c 1 -w 1 -M "do" -s 8972 target &>/dev/null; then
  NEW_MTU=9000
  echo "SUCCESS: Full Jumbo Frames (9000 MTU) supported."
elif ping -c 1 -w 1 -M "do" -s 2004 target &>/dev/null; then
  NEW_MTU=2032
  echo "SUCCESS: Baby Jumbo Frames (2032 MTU) supported."
else
  echo "FAIL: Link cannot support Jumbo Frames. Reverting to safe defaults."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. System-Netzwerkkonfiguration anwenden
  echo "Configuring /etc/systemd/network/end0.network..."
  cat <<EOF | sudo tee /etc/systemd/network/end0.network
[Match]
Name=end0

[Link]
MTUBytes=$NEW_MTU

[Network]
Address=172.20.0.1/24
EOF
  sudo systemctl daemon-reload
  sudo networkctl reload

  # 3. Diretta-Konfiguration anwenden
  echo "Configuring Diretta Host..."

  # FlexCycle für Jumbo Frames immer aktivieren, um Stabilität zu gewährleisten
  sudo sed -i 's/^FlexCycle=.*/FlexCycle=enable/' /opt/diretta-alsa/setting.inf

  # Konditionale Optimierung von CycleTime und InfoCycle
  if [ "$NEW_MTU" -eq 9000 ]; then
    echo "Optimization: Full Jumbo Frames detected. Relaxing CycleTime to 1000us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=1000/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=100000/' /opt/diretta-alsa/setting.inf
  else
    echo "Optimization: Baby Jumbo Frames detected. Setting CycleTime to 700us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=700/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=70000/' /opt/diretta-alsa/setting.inf
  fi

  sudo systemctl restart diretta_alsa
  echo "DONE: Host optimization complete."
}
```

#### **Schritt 4:** Neustart, um die MTU-Änderungen zu übernehmen
Starten Sie zuerst das Target neu, dann den Host:
```bash
sudo sync && sudo reboot
```

>
>
> ---
>
> ### ✅ Checkpoint: Netzwerk-Konfiguration überprüfen
>
> Wenn Sie die Unterstützung für Jumbo Frames für Ihre Konfiguration aktivieren konnten, ist jetzt ein guter Zeitpunkt, zu [**Anhang 5**](#14-anhang-5-system-gesundheitschecks) zurückzukehren und den universellen Befehl **System-Gesundheitscheck** sowohl auf dem Host als auch auf dem Target auszuführen.
>
> ---

## 19. Anhang 10: Optional: System-Updates
Dieser Abschnitt bietet Anleitungen zum Anwenden von Updates auf die Raspberry Pi-Hardware, das AudioLinux-Betriebssystem und den Diretta-Software-Stack.

#### **Teil 1:** Aktualisierung des Raspberry Pi-Bootloaders (Optional)

Die Aktualisierung des Raspberry Pi-Bootloaders (EEPROM) ist nicht zwingend erforderlich und birgt gewisse Risiken. Das Aufspielen der aktuellen Firmware kann jedoch Vorteile wie niedrigere Betriebstemperaturen und sauberere Startsequenzen bieten, da die Raspberry Pi Foundation kontinuierlich Fehler behebt.

*Warnung: Stellen Sie sicher, dass Sie nur das jeweils korrekte Firmware-Image auf das entsprechende Board aufspielen. Das Flashen eines Raspberry Pi 4 mit einem Raspberry Pi 5-Bootloader (oder umgekehrt) kann schwerwiegende Folgen haben, bis hin zur dauerhaften Beschädigung (Bricking) des Boards.*

**Aktuelle Bootloader-Version überprüfen**
Bevor Sie beginnen, melden Sie sich per SSH sowohl auf dem Host als auch auf dem Target an und führen Sie den folgenden Befehl aus, um das Veröffentlichungsdatum Ihres aktuellen Bootloaders zu überprüfen. Notieren Sie sich diese Daten, um das Update später verifizieren zu können.

```bash
vcgencmd bootloader_version
```

*(Achten Sie auf das Datum in der ersten Zeile der Ausgabe).* 

**Das Update-Medium vorbereiten**
Sie benötigen eine leere microSD-Karte, ein SD-Kartenlesegerät und die offizielle Raspberry Pi Imager-Software auf Ihrem Computer.

1. Öffnen Sie den Raspberry Pi Imager. Klicken Sie auf **CHOOSE DEVICE** und wählen Sie das spezifische Raspberry Pi-Board aus, das Sie aktualisieren möchten.

   ![Select Raspberry Pi 5 Device](images/01-rpi-dev.png)

2. Klicken Sie auf **CHOOSE OS**, scrollen Sie in der Liste nach unten und wählen Sie **Misc utility images**.

   ![Select Misc Utility Images](images/02-rpi-misc.png)

3. Wählen Sie **Bootloader**. *(Hinweis: Das Menü zeigt die in Schritt 1 ausgewählte Pi-Familie an).* 

   ![Select Bootloader for Pi 5 Family](images/03-rpi-bl.png)

4. Wählen Sie **SD Card Boot**.

   ![Select SD Card Boot](images/04-rpi-sd.png)

5. Klicken Sie auf **CHOOSE STORAGE**, wählen Sie Ihre leere microSD-Karte aus, klicken Sie auf **NEXT** und schreiben Sie das Image.

*Wichtig: Wenn Ihr Target ein Raspberry Pi 5 und Ihr Host ein Raspberry Pi 4 ist (oder eine andere gemischte Kombination), können Sie dieselbe Update-Karte nicht wiederverwenden. Sie müssen zu Ihrem Computer zurückkehren und eine neue Update-microSD-Karte speziell für den zweiten Board-Typ flashen, bevor Sie fortfahren.*

**Das Hardware-Update durchführen**

1. Fahren Sie beide Rechner sicher herunter. Fahren Sie das Target zuerst herunter, dann den Host (`sudo poweroff`).
2. Trennen Sie die Stromkabel von beiden Geräten.
3. Entfernen Sie die primären Boot-microSD-Karten aus beiden Geräten und legen Sie sie sicher beiseite.
4. Setzen Sie die frisch vorbereitete Update-microSD-Karte vorsichtig in das Board ein (stellen Sie sicher, dass die goldenen Kontakte zur Unterseite des Raspberry Pi-Boards zeigen).
5. Schließen Sie den Strom wieder an das Board an.
6. Beobachten Sie die Aktivitäts-LEDs auf dem Board. Warten Sie, bis die grüne LED beginnt, in einem schnellen, kontinuierlichen Rhythmus zu blinken (dies dauert normalerweise etwa 10 Sekunden). Das gleichmäßige Blinken zeigt an, dass der EEPROM-Flash-Vorgang abgeschlossen ist.
7. Trennen Sie den Strom vom Board.
8. Entfernen Sie die Update-microSD-Karte und setzen Sie Ihre ursprüngliche Boot-microSD-Karte wieder ein.
9. Schließen Sie den Strom wieder an die Systeme an. **Schalten Sie zuerst den Host ein, dann das Target.**

Sobald die Systeme vollständig hochgefahren und erreichbar sind, führen Sie die Bootloader-Versionsprüfung auf jedem Computer erneut aus, um zu bestätigen, dass sich die Bootloader-Daten auf das vom Imager geschriebene Veröffentlichungsdatum verschoben haben. Wenn Ihr Host und Ihr Target unterschiedliche Board-Typen verwenden (z. B. RPi4 und RPi5), werden sich die Versionen wahrscheinlich unterscheiden. Das ist völlig in Ordnung.

```bash
vcgencmd bootloader_version
```

---

#### **Teil 2:** AudioLinux- und Diretta-Software aktualisieren

Der Systemaktualisierungsprozess erfordert eine strikte Reihenfolge, um sicherzustellen, dass der angepasste Kernel, die Compiler-Toolchains und der ALSA-Daemon perfekt synchronisiert bleiben.

#### Führen Sie nun die Updates durch
1. Starten Sie das AudioLinux-Konfigurationstool, indem Sie `menu` an der Eingabeaufforderung eingeben.
2. Navigieren Sie zum Menü **Install/Update menu** und wählen Sie **UPDATE System**.
3. Wählen Sie im selben Menü **Install/Update menu** die Option **UPDATE menu**.
   *(Hinweis: Sie müssen die E-Mail-Adresse eingeben, die für Ihren AudioLinux-Kauf verwendet wurde, sowie den spezifischen Benutzernamen und das Passwort, die Piero für den Download des AudioLinux-Images bereitgestellt hat).* 
4. Wählen Sie **SELECT/UPDATE kernel**. Wählen Sie die genaue Kernelversion, die zuvor in [**Schritt 4**](#44-run-system-and-menu-updates) empfohlen wurde.
5. Re-apply the `motd` fix from [**Section 5.1**](#51-pre-configure-the-diretta-host) on the **Host**.
6. Wenden Sie den `sudoers`-Patch aus [**Abschnitt 7.2**](#72-correct-sudoers-rule-precedence) erneut auf **sowohl** dem Target als auch dem Host an.
7. Starten Sie zuerst das Target neu, gefolgt vom Host.
8. Once back online, re-run the "Configure Compatible Compiler Toolchain" script from [**Step 8**](#8-diretta-software-installation--configuration) on **both** the Target and the Host.
9. Führen Sie auf dem **Target** den in [**Abschnitt 8.1**](#81-on-the-diretta-target) beschriebenen Diretta-Installations-/Aktualisierungsschritt aus.
10. Führen Sie auf dem **Host** den in [**Abschnitt 8.2**](#82-on-the-diretta-host) beschriebenen Diretta-Installations-/Aktualisierungsschritt aus.
11. Starten Sie zuerst das Target neu, gefolgt vom Host.
>
>
> ---
>
> ### ✅ Checkpoint: System-Gesundheit und Regressionstests
>
> Nach Abschluss der Aktualisierungssequenz müssen Sie die Stabilität der Audio-Pipeline überprüfen, um sicherzustellen, dass während des Upgrades keine Software- oder Konfigurationsregressionen aufgetreten sind.
>
> 1. Öffnen Sie Roon, warten Sie auf die Rückkehr der Netzwerkzone und spielen Sie mindestens einige Sekunden Musik ab, um die Verbindung der Transportschicht zu überprüfen und die Hardware-Zähler in Bewegung zu setzen.
> 2. Verbinden Sie sich per SSH mit dem **Target** und kehren Sie vorübergehend in den Standard-Modus zurück, damit Diagnose-Skripte den Datenverkehr ungehindert über die Verbindung prüfen können:
>    ```bash
>    purist-mode --revert
>    ```
> 3. Führen Sie das universelle **System Health Check** QA-Skript aus [**Anhang 5**](#14-anhang-5-system-gesundheitschecks) sowohl auf dem Host als auch auf dem Target aus.
> 4. Überprüfen Sie sorgfältig die Ausgabe und beheben Sie alle isolierten Thread-Affinitäts- oder Prioritätsprobleme, die vom Skript erkannt wurden.
>
> ---

---

#### **Teil 3:** USB-Stromgrenzen überschreiben (nur Raspberry Pi 5)

Wenn Sie einen Raspberry Pi 5 verwenden und ihn mit einem erstklassigen Netzteil eines Drittanbieters (z. B. iFi SilentPower Elite 5V oder ein lineares Netzteil mit 5A Nennstrom) anstelle des offiziellen Raspberry Pi 27W USB-C-Netzteils betreiben, verhandelt der Pi standardmäßig sichere 5V/3A. Dadurch wird die kombinierte Stromaufnahme über alle vier USB-Anschlüsse hinweg auf 600mA begrenzt.

Dies ist für reine Audio-Transporte in der Regel belanglos, aber wenn Sie wissen, dass Ihr Netzteil kontinuierlich mindestens 5A bei 5V liefern kann, können Sie diese Einschränkung sicher umgehen.

**Führen Sie diesen Befehl aus, um den Override an Ihre Boot-Konfiguration anzuhängen:**

```bash
if ! grep -q "^usb_max_current_enable=" /boot/config.txt; then
  echo "usb_max_current_enable=1" | sudo tee -a /boot/config.txt
else
  echo "Optimization already present in /boot/config.txt. Skipping configuration."
fi
sudo sync && sudo reboot
```

---
