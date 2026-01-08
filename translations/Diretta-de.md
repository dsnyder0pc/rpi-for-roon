# Aufbau einer dedizierten Diretta-Verbindung mit AudioLinux auf dem Raspberry Pi

Dieser Leitfaden bietet eine umfassende Schritt-für-Schritt-Anleitung zur Konfiguration zweier Raspberry Pi-Geräte als dedizierter Diretta-Host und Diretta-Target. Dieses Setup verwendet eine direkte Ethernet-Punkt-zu-Punkt-Verbindung zwischen den beiden Geräten, um ein Höchstmaß an Netzwerkisolierung und Audioleistung zu gewährleisten.

Der **Diretta-Host** wird mit Ihrem Hauptnetzwerk verbunden (für den Zugriff auf Ihren Musikserver) und fungiert gleichzeitig als Gateway für das Target. Das **Diretta-Target** wird ausschließlich mit dem Host und Ihrem USB-DAC oder DDC verbunden.

# Haftungsausschluss

Diretta entwickelt sich stetig weiter. Ich freue mich jedoch bestätigen zu können, dass die Version 146_7 (und neuere?) sehr gut funktioniert, die CPU-Last auf dem Target um ca. 45 % reduziert und hervorragend klingt.

Hier einige Links für weitere Informationen (in Englisch):
* https://help.diretta.link/support/solutions/articles/73000661018-146
* https://help.diretta.link/support/solutions/articles/73000661171-dds-diretta-direct-stream


## Eine Einführung in die Referenz-Roon-Architektur

Willkommen zum definitiven Leitfaden für den Aufbau eines hochmodernen Roon-Streaming-Endpunkts. Obwohl AudioLinux auch andere Protokolle unterstützt, verwende ich für diesen Aufbau Roon als Beispiel. Sie können über das Menüsystem des Diretta-Hosts Unterstützung für andere Protokolle installieren, darunter HQPlayer, Audirvana, DLNA, AirPlay usw. Bevor wir in die schrittweisen Anweisungen eintauchen, ist es wichtig, das "Warum" hinter diesem Projekt zu verstehen. Diese Einführung erklärt das Problem, das diese Architektur löst, warum sie vielen hochpreisigen kommerziellen Alternativen grundlegend überlegen ist und wie dieses DIY-Projekt einen direkten und lohnenden Weg darstellt, um die ultimative Klangqualität aus Ihrem Roon-System herauszuholen.

### Das Roon-Paradoxon: Ein mächtiges Erlebnis mit einem klanglichen Vorbehalt

Roon wird fast universell als das leistungsstärkste und ansprechendste Musikverwaltungssystem gefeiert. Seine umfangreichen Metadaten und die nahtlose Benutzererfahrung sind unübertroffen. Diese funktionale Überlegenheit wurde jedoch lange von einer beständigen Kritik aus einem lautstarken Teil der audiophilen Gemeinschaft begleitet: Die Klangqualität von Roon sei kompromittiert, oft beschrieben als "flach, stumpf und leblos" im Vergleich zu anderen Playern.

Dieser "Roon-Klang" ist kein Mythos und auch kein Fehler in Roons bit-perfekter Software. Es ist ein mögliches Symptom der leistungsstarken und ressourcenintensiven Natur von Roon. Der "schwergewichtige" Roon Core benötigt erhebliche Rechenleistung, was wiederum elektrisches Rauschen (RFI/EMI) erzeugt. Wenn der Computer, auf dem der Roon Core läuft, in unmittelbarer Nähe Ihres empfindlichen Digital-Analog-Wandlers (DAC) steht, kann dieses Rauschen die analoge Ausgangsstufe kontaminieren, Details verdecken, die Klangbühne verkleinern und der Musik ihre Lebendigkeit rauben.

---

### Mehr als nur "Pflaster": Eine fundamentale Lösung

Roon Labs selbst plädiert für eine "Zwei-Boxen"-Architektur, um dieses primäre Problem zu lösen: Die Trennung des anspruchsvollen **Roon Core** von einem leichtgewichtigen Netzwerk-**Endpoint** (auch Streaming-Transport genannt). Dies ist der richtige erste Schritt, da die schwere Rechenlast auf eine entfernte Maschine ausgelagert und deren Rauschen von Ihrem Audio-Rack isoliert wird.

Doch selbst in diesem überlegenen zweistufigen Design bleibt ein subtileres Problem bestehen. Standard-Netzwerkprotokolle, einschließlich Roons eigenem RAAT, liefern Audiodaten in intermittierenden "Bursts" (Schüben). Dies zwingt die CPU des Endpunkts dazu, ihre Aktivität ständig hochzufahren, um diese Bursts zu verarbeiten, was zu schnellen Schwankungen in der Stromaufnahme führt. Diese Schwankungen erzeugen ihr eigenes niederfrequentes elektrisches Rauschen direkt am Endpunkt – jener Komponente, die Ihrem DAC am nächsten ist.

High-End-Audiohersteller versuchen, die *Symptome* dieses stoßweisen Datenverkehrs mit verschiedenen "Pflaster"-Lösungen zu bekämpfen: massive lineare Netzteile, um die Stromspitzen besser zu bewältigen, Ultra-Low-Power-CPUs, um die Intensität der Spitzen zu minimieren, und zusätzliche Filterstufen, um das resultierende Rauschen zu bereinigen. Während diese Strategien helfen können, gehen sie nicht die Ursache des Rauschens an: die stoßweise Verarbeitung selbst.

Dieser Leitfaden präsentiert eine elegantere und dramatisch effektivere Lösung. Anstatt zu versuchen, das Rauschen nachträglich zu bereinigen, bauen wir eine Architektur, die verhindert, dass das Rauschen überhaupt erst entsteht.

---

### Die Drei-Stufen-Architektur: Roon + Diretta

Dieses Projekt entwickelt Roons empfohlenes Zwei-Boxen-Setup zu einem ultimativen dreistufigen System weiter, das mehrere, sich ergänzende Schichten der Isolierung bietet.

1.  **Stufe 1: Roon Core**: Ihr leistungsstarker Roon-Server läuft auf einer dedizierten Maschine, weit entfernt von Ihrem Hörraum. Er übernimmt die schwere Rechenarbeit, und sein elektrisches Rauschen bleibt von Ihrem Audiosystem isoliert.
2.  **Stufe 2: Diretta-Host**: Der erste Raspberry Pi in unserem Aufbau fungiert als **Diretta-Host**. Er verbindet sich mit Ihrem Hauptnetzwerk, empfängt den Audiostream vom Roon Core und bereitet ihn für die Weiterleitung über ein spezialisiertes Protokoll vor.
3.  **Stufe 3: Diretta-Target**: Der zweite Raspberry Pi, das **Diretta-Target**, verbindet sich *nur* über ein kurzes Ethernet-Kabel mit dem Host und schafft so eine galvanisch getrennte Punkt-zu-Punkt-Verbindung. Er empfängt das Audio vom Host und leitet es per USB an Ihren DAC oder DDC weiter.

### Was Diretta und AudioLinux bieten

Die Überlegenheit dieses Designs beruht auf zwei wichtigen Softwarekomponenten, die auf den Raspberry Pi-Geräten laufen:

* **AudioLinux**: Dies ist ein speziell für audiophile Zwecke entwickeltes Echtzeit-Betriebssystem. Im Gegensatz zu einem Allzweck-Betriebssystem ist es optimiert, um Prozessorlatenzen und System-"Jitter" zu minimieren und so eine stabile, rauscharme Grundlage für unseren Endpunkt zu bieten.
* **Diretta**: Dieses bahnbrechende Protokoll ist die "Geheimzutat", die das Wurzelproblem löst. Es erkennt, dass Schwankungen in der Verarbeitungslast des Endpunkts niederfrequentes elektrisches Rauschen erzeugen, das die interne Filterung eines DACs (definiert durch dessen PSRR - Power Supply Rejection Ratio) umgehen und die analoge Leistung subtil verschlechtern kann. Um dies zu bekämpfen, verwendet Diretta sein "Host-Target"-Modell, bei dem der Host Daten in einem kontinuierlichen, synchronisierten Strom kleiner, gleichmäßig verteilter Pakete sendet. Dies "glättet" die Verarbeitungslast auf dem Target-Gerät, stabilisiert die Stromaufnahme und minimiert die Erzeugung dieses schädlichen elektrischen Rauschens.

Die Kombination aus der physikalischen galvanischen Trennung durch die Ethernet-Punkt-zu-Punkt-Verbindung und der Eliminierung des Verarbeitungsrauschens durch das Diretta-Protokoll schafft einen zutiefst sauberen Signalweg zu Ihrem DAC – einen, der Lösungen, die viele tausend Euro kosten, übertreffen kann.

---

### Ein lohnender Weg zu klanglicher Exzellenz

Dieses Projekt ist mehr als nur eine technische Übung; es ist eine lohnende Möglichkeit, sich mit dem Hobby zu beschäftigen und die direkte Kontrolle über die Leistung Ihres Systems zu übernehmen. Durch den Bau dieser "Diretta-Bridge" setzen Sie nicht einfach nur Komponenten zusammen; Sie implementieren eine hochmoderne Architektur, die die Kernherausforderungen der digitalen Audiowiedergabe direkt angeht. Sie werden ein tieferes Verständnis dafür gewinnen, worauf es bei der digitalen Wiedergabe wirklich ankommt, und mit einem Maß an Klarheit, Detailtreue und musikalischem Realismus von Roon belohnt, das Sie vielleicht nicht für möglich gehalten hätten.

Lassen Sie uns beginnen.

---

Wenn Sie sich in den USA befinden, rechnen Sie mit etwa 329 $ (plus Steuern und Versand), um den Basisaufbau zu vervollständigen (zunächst limitiert auf 44,1 kHz Wiedergabe zur Evaluierung), plus weitere 100 €, um die Hi-Res-Wiedergabe zu aktivieren (Preise können sich ändern):
- Hardware ($250)
- Ein Jahr AudioLinux-Abonnement ($79)
- Diretta-Target-Lizenz (€100)

## Inhaltsverzeichnis
1.  [Voraussetzungen](#1-voraussetzungen)
2.  [Vorbereitung des Installations-Images](#2-vorbereitung-des-installations-images)
3.  [Kernsystem-Konfiguration (Auf beiden Geräten durchführen)](#3-kernsystem-konfiguration-auf-beiden-ger%C3%A4ten-durchf%C3%BChren)
4.  [System-Updates (Auf beiden Geräten durchführen)](#4-system-updates-auf-beiden-ger%C3%A4ten-durchf%C3%BChren)
5.  [Punkt-zu-Punkt Netzwerk-Konfiguration](#5-punkt-zu-punkt-netzwerk-konfiguration)
6.  [Komfortabler & Sicherer SSH-Zugriff](#6-komfortabler--sicherer-ssh-zugriff)
7.  [Allgemeine Systemoptimierungen](#7-allgemeine-systemoptimierungen)
8.  [Installation & Konfiguration der Diretta-Software](#8-installation--konfiguration-der-diretta-software)
9.  [Abschließende Schritte & Roon-Integration](#9-abschlie%C3%9Fende-schritte--roon-integration)
10. [Anhang 1: Optionale Lüftersteuerung für Argon ONE](#10-anhang-1-optionale-argon-one-l%C3%BCftersteuerung)
11. [Anhang 2: Optionale IR-Fernbedienung](#11-anhang-2-optionale-ir-fernbedienung)
12. [Anhang 3: Optionaler Purist-Modus](#12-anhang-3-optionaler-purist-modus)
13. [Anhang 4: Optionale Web-Oberfläche zur Systemsteuerung](#13-anhang-4-optionale-web-oberfl%C3%A4che-zur-systemsteuerung)
14. [Anhang 5: System-Gesundheitschecks](#14-anhang-5-system-gesundheitschecks)
15. [Anhang 6: Erweitertes Echtzeit-Leistungstuning](#15-anhang-6-erweitertes-echtzeit-leistungstuning)
16. [Anhang 7: CPU-Optimierung mit ereignisgesteuerten Hooks](#16-anhang-7-cpu-optimierung-mit-ereignisgesteuerten-hooks)
17. [Anhang 8: Optionaler puristischer 100Mbps Netzwerk-Modus](#17-anhang-8-optionaler-puristischer-100mbps-netzwerk-modus)
18. [Anhang 9: Optionale Jumbo-Frames-Optimierung](#18-anhang-9-optional-jumbo-frames-optimierung)

---

### **Wie Sie diesen Leitfaden verwenden**

Dieser Leitfaden ist so einfach wie möglich gestaltet, um die manuelle Bearbeitung von Dateien auf ein Minimum zu reduzieren. Der primäre Arbeitsablauf besteht darin, Befehlsblöcke aus diesem Dokument direkt per **Copy & Paste** in ein Terminalfenster zu kopieren, das mit Ihren Raspberry Pi-Geräten verbunden ist.

So gehen Sie bei den meisten Schritten vor:

1.  **Verbindung via SSH**: Sie verwenden einen SSH-Client auf Ihrem Hauptcomputer, um sich entweder beim **Diretta-Host** oder beim **Diretta-Target** anzumelden, wie im jeweiligen Abschnitt angewiesen.
2.  **Befehl kopieren**: Fahren Sie in Ihrem Webbrowser über die obere rechte Ecke eines Befehlsblocks in diesem Leitfaden. Ein **Kopier-Symbol** erscheint. Klicken Sie darauf, um den gesamten Block in Ihre Zwischenablage zu kopieren.
3.  **Einfügen und Ausführen**: Fügen Sie die kopierten Befehle in das korrekte SSH-Terminalfenster ein und drücken Sie `Enter`.

Die Skripte und Befehle wurden sorgfältig geschrieben, um sicher zu sein und Fehler zu vermeiden, selbst wenn sie mehr als einmal ausgeführt werden. Wenn Sie dieser Copy-and-Paste-Methode folgen, vermeiden Sie häufige Tippfehler und Konfigurationsfehler.

---

### Video-Walkthrough

Hier ist ein Link zu einer Reihe kurzer Videos (in Englisch), die diesen Prozess begleiten:

* [Diretta Build Walkthrough with Two Raspberry Pi Computers](https://youtube.com/playlist?list=PLMl09rJ6zKCk13V-IH_kRKW7FP8Q0_Fw0&si=u_E8rUEhgMiQ4NIb)

---

### 1. Voraussetzungen

#### Hardware

Eine vollständige Stückliste finden Sie unten. Während andere Teile ersetzt werden können, verbessert die Verwendung dieser spezifischen Komponenten die Chancen auf einen erfolgreichen Aufbau.

**Kernkomponenten (von [pishop.us](https://www.pishop.us/) oder einem ähnlichen Anbieter):**
* 1 x [Raspberry Pi 5/1GB](https://www.pishop.us/product/raspberry-pi-5-1gb/) (für das Diretta-Target)
* 1 x [Raspberry Pi 5/2GB](https://www.pishop.us/product/raspberry-pi-5-2gb/) (für den Diretta-Host)
* 2 x [Flirc Raspberry Pi 5 Gehäuse](https://www.pishop.us/product/flirc-raspberry-pi-5-case/)
* 2 x [64 GB A2 microSDXC Karte (Lexar Alternative)](https://www.bhphotovideo.com/c/product/1830849-REG/lexar_lmssipl064g_bnanu_64gb_silver_plus_microsdxc.html)
* 2 x [Raspberry Pi 45W USB-C Netzteil - Weiß](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)

**Erforderliche Netzwerkkomponenten:**
* 1 x [Plugable USB3 auf Ethernet Adapter](https://www.amazon.com/dp/B00AQM8586) (für den Diretta-Host)
* 1 x [Kurzes CAT6 Ethernet Patchkabel](https://www.amazon.com/Cable-Matters-Snagless-Ethernet-Internet/dp/B0B57S1G2Y/?th=1) (für die Punkt-zu-Punkt-Verbindung)

**Optional, aber hilfreich zur Fehlersuche:**
* 1 x [Micro-HDMI auf Standard HDMI (A/M), 2m Kabel, Weiß](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Offizielle Raspberry Pi Tastatur - Rot/Weiß](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**Optionale Upgrades:**
* 2 x [Argon ONE V3 Raspberry Pi 5 Gehäuse](https://www.amazon.com/Argon-ONE-V3-Raspberry-Case/dp/B0CNGSXGT2/) (anstelle der Flirc-Gehäuse)
* 1 x [Argon IR Fernbedienung](https://www.amazon.com/Argon-Raspberry-Infrared-Batteries-Included/dp/B091F3XSF6/) (um dem Diretta-Host Fernbedienungsfunktionen hinzuzufügen)
* 1 x [Flirc USB IR Empfänger](https://www.pishop.us/product/flirc-rpi-usb-xbmc-ir-remote-receiver/) (um die Argon IR Fernbedienung mit dem Diretta-Host in einem Flirc-Gehäuse zu verwenden)
* 1 x [Blue Jeans BJC CAT6a Belden Bonded Pairs 500 MHz](https://www.bluejeanscable.com/store/data-cables/index.htm) (für die Punkt-zu-Punkt-Verbindung zwischen Host und Target)
* 1 x [iFi SilentPower iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (um das Diretta-Target mit sauberem Strom zu versorgen)
* 1 x [iFi SilentPower Pulsar USB Kabel](https://www.silentpower.tech/products/pulsar-usb) (USB-Verbindung mit galvanischer Trennung)
* 1 x [DC 5,5mm x 2,1mm auf USB-C Adapter](https://www.amazon.com/5-5mm-Adapter-Female-Convert-Connector/dp/B0CRB7N4GH/) (benötigt, um den Stecker des iPower Elite an den USB-C Stromeingang des Diretta-Targets anzupassen)
* 1 x [SMSL PO100 PRO DDC](https://www.amazon.com/dp/B0BLYVZCV5) (ein Digital-Digital-Wandler für DACs, denen ein guter USB-Eingang fehlt)
* 1 x [USB WLAN-Adapter](https://www.pishop.us/product/raspberry-pi-dual-band-5ghz-2-4ghz-usb-wifi-adapter-with-antenna/) (eine kabelgebundene Verbindung ist sehr zu bevorzugen, aber wenn ein Ethernet-Kabel in der Nähe Ihres Audiosystems unpraktisch ist, ersetzen Sie den Plugable USB-zu-Ethernet-Adapter durch diesen WLAN-Adapter)
* 1 x [Stromverteilerkabel](https://www.amazon.com/dp/B01K3ADXX2?th=1) (beide 45W-Netzteile in eine einzige Steckdose stecken)

**Erforderliche Audiokomponente:**
* 1 x USB DAC oder DDC

**Erforderliche Werkzeuge:**
* Laptop oder Desktop-PC mit Linux, macOS (iTerm2, https://iterm2.com/, empfohlen) oder Microsoft Windows mit [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
* Ein SD- oder microSD-Kartenleser
* Ein HDMI-Fernseher oder Monitor (optional, aber nützlich zur Fehlersuche)

#### Software- & Lizenzkosten

* **AudioLinux:** Eine "Unlimited"-Lizenz wird für Enthusiasten empfohlen und kostet derzeit **$158** (Preise können sich ändern). Für den Einstieg reicht jedoch ein Jahresabonnement für derzeit **$79**. Beide Optionen erlauben die Installation auf mehreren Geräten am selben Standort.
* **Diretta-Target:** Für die Hi-Res-Wiedergabe (höher als 44,1 kHz PCM) über das Diretta-Target-Gerät ist eine Lizenz erforderlich, die derzeit **€100** kostet.
    * Sie können das Diretta-Target mit 44,1 kHz-Streams über einen längeren Zeitraum evaluieren. Daher empfehle ich, während der Testphase die **Abtastratenkonvertierung** (Sample rate conversion) in Roon unter den **MUSE** DSP-Einstellungen zu nutzen, um alle Inhalte auf 44,1 kHz zu konvertieren. Wenn Sie zufrieden sind, kaufen Sie die Diretta-Target-Lizenz, um diese Einschränkung aufzuheben. Lassen Sie die Einstellungen zur Abtastratenkonvertierung aktiv, bis Sie die zweite E-Mail vom Diretta-Team erhalten, die bestätigt, dass Ihre Hardware aktiviert wurde.
    * **WICHTIG:** Diese Lizenz ist an die spezifische Hardware des Raspberry Pi gebunden, für den sie gekauft wurde. Es ist unerlässlich, dass Sie den abschließenden Lizenzierungsschritt auf genau der Hardware durchführen, die Sie dauerhaft verwenden möchten.
    * Diretta bietet möglicherweise einen einmaligen Lizenzersatz bei Hardwareausfall innerhalb der ersten zwei Jahre an (bitte überprüfen Sie die Bedingungen zum Zeitpunkt des Kaufs). Wenn Sie die Hardware aus einem anderen Grund wechseln, muss eine neue Lizenz erworben werden.

---

### 2. Vorbereitung des Installations-Images

1.  **Kauf und Download:** Erwerben Sie das AudioLinux-Image von der [offiziellen Website](https://www.audio-linux.com/). Sie erhalten in der Regel innerhalb von 24 Stunden nach dem Kauf per E-Mail einen Link zum Herunterladen der `.img.gz`-Datei.
2.  **Image flashen:** Verwenden Sie den [Raspberry Pi Imager](https://www.raspberrypi.com/software/), um das heruntergeladene AudioLinux-Image auf **beide** microSD-Karten zu schreiben.
    > **Hinweis:** Das AudioLinux-Image ist ein direkter Festplattenabzug, kein komprimierter Installer. Daher ist die Image-Datei recht groß und der Flash-Vorgang kann ungewöhnlich lange dauern. Rechnen Sie mit bis zu 15 Minuten pro Karte, abhängig von der Geschwindigkeit Ihrer microSD-Karte und Ihres Lesegeräts.

---

### 3. Kernsystem-Konfiguration (Auf beiden Geräten durchführen)

Nach dem Flashen müssen Sie jeden Raspberry Pi einzeln konfigurieren, um Netzwerkkonflikte zu vermeiden.

Für die beste Leistung verwendet dieser Leitfaden den Raspberry Pi 5 sowohl für das Diretta-Target (das Gerät, das mit Ihrem DAC verbunden ist) als auch für den Diretta-Host. Sie werden zuerst den Host konfigurieren.

> **KRITISCHE WARNUNG:** Da beide Geräte vom exakt gleichen Image geflasht werden, haben sie identische `machine-id` Werte. Wenn Sie beide Geräte gleichzeitig einschalten, während sie mit demselben LAN verbunden sind, wird Ihr DHCP-Server ihnen wahrscheinlich dieselbe IP-Adresse zuweisen, was zu einem Netzwerkkonflikt führt.
>
> **Sie müssen den ersten Start und die Konfiguration für jedes Gerät nacheinander durchführen.**

1.  Stecken Sie die microSD-Karte in den **ersten** Raspberry Pi, verbinden Sie ihn mit Ihrem Netzwerk und schalten Sie ihn ein. **Hinweis:** Wenn Sie das Argon ONE Gehäuse verwenden, hören Sie möglicherweise Geräusche vom Lüfter. Keine Sorge. Sobald Sie mit der Diretta-Einrichtung fertig sind, finden Sie in [Anhang 1](#10-anhang-1-optionale-argon-one-l%C3%BCftersteuerung) Anweisungen zur Behandlung des Lüftergeräuschs.
2.  Führen Sie **alle Schritte von Abschnitt 3** für dieses erste Gerät durch.
3.  Sobald das erste Gerät mit seiner neuen, einzigartigen Konfiguration neu gestartet wurde, fahren Sie es herunter.
4.  Schalten Sie nun den **zweiten** Raspberry Pi ein und wiederholen Sie **alle Schritte von Abschnitt 3** für ihn.

Bitte entnehmen Sie den Standard-SSH-Benutzer und die sudo/root-Passwörter Ihrem Kaufbeleg von AudioLinux. Notieren Sie sich diese, da Sie sie während dieses Prozesses oft benötigen werden.

Sie verwenden den SSH-Client auf Ihrem lokalen Computer, um sich während dieses Prozesses auf den RPi-Computern anzumelden. Dieser Client erfordert, dass Sie die IP-Adresse der RPi-Computer kennen, die sich von einem Neustart zum nächsten ändern kann. Der einfachste Weg, diese Informationen zu erhalten, ist über die Web-Oberfläche oder App Ihres Heimnetzwerk-Routers, aber Sie können optional auch die [fing](https://www.fing.com/app/) App auf Ihrem Smartphone oder Tablet installieren.

Sobald Sie die IP-Adresse eines Ihrer RPi-Computer haben, verwenden Sie den SSH-Client auf Ihrem lokalen Computer, um sich mit diesem Prozess anzumelden. Merken Sie sich den Beispielbefehl `ssh`, da Sie ähnliche Befehle in diesem Leitfaden verwenden werden.
```bash
cmd=$(cat <<'EOT'
read -rp "Geben Sie die Adresse Ihres RPi ein und drücken Sie [Enter]: " RPi_IP_Address
echo 'Erinnerung: Das Standardpasswort finden Sie in Ihrer AudioLinux E-Mail von Piero'
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 3.1. Die Machine ID neu generieren

Die `machine-id` ist eine eindeutige Kennung für die OS-Installation. Sie **muss** für jedes Gerät unterschiedlich sein.

```bash
echo ""
echo "Alte Machine ID: $(cat /etc/machine-id)"
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
echo "Neue Machine ID: $(cat /etc/machine-id)"
```

#### 3.2. Eindeutige Hostnamen setzen

Legen Sie für jedes Gerät einen eindeutigen Hostnamen fest, um sie leicht identifizieren zu können. **Hinweis:** Wenn dies nicht Ihr erster Aufbau mit diesen Anweisungen ist und Sie bereits ein Diretta Host/Target-Paar in Ihrem Netzwerk haben, sollten Sie für diesen neuen Diretta-Host einen anderen Namen wählen, wie z.B. `diretta-host2`, nur für diesen Teil. Dies erleichtert den späteren unabhängigen Zugriff auf die beiden.

**Auf Ihrem ERSTEN Gerät (der zukünftige Diretta-Host):**
```bash
# Auf dem Diretta-Host
sudo hostnamectl set-hostname diretta-host
```

**Auf Ihrem ZWEITEN Gerät (das zukünftige Diretta-Target):**
```bash
# Auf dem Diretta-Target
sudo hostnamectl set-hostname diretta-target
```

**Fahren Sie das Gerät an diesem Punkt herunter. Wiederholen Sie die [oben genannten Schritte](#3-kernsystem-konfiguration-auf-beiden-ger%C3%A4ten-durchf%C3%BChren) für den zweiten Raspberry Pi.**
```bash
sudo sync && sudo poweroff
```

---

### 4. System-Updates (Auf beiden Geräten durchführen)

Für die Schritte in diesem Abschnitt ist es meist am effizientesten (und am wenigsten verwirrend), den gesamten Abschnitt 4 zunächst auf dem Diretta-Host abzuschließen und dann den gesamten Abschnitt auf dem Diretta-Target zu wiederholen.

Jeder RPi hat seine eigene Machine-ID, Sie können sie also jetzt einschalten. Wenn Sie zwei Netzwerkkabel haben, ist es bequemer, beide für die nächsten Schritte gleichzeitig mit Ihrem Heimnetzwerk zu verbinden. Andernfalls können Sie nacheinander vorgehen. **Hinweis**: Ihr Router wird ihnen wahrscheinlich andere IP-Adressen zuweisen als die, die Sie beim ersten Login verwendet haben. Stellen Sie sicher, dass Sie die neue IP-Adresse für Ihre SSH-Befehle verwenden. Hier zur Erinnerung:

```bash
cmd=$(cat <<'EOT'
read -rp "Geben Sie die (neue) Adresse Ihres RPi ein und drücken Sie [Enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 4.1. "Chrony" installieren, um die Systemuhr zu aktualisieren

Die Systemuhr muss genau gehen, bevor wir Updates installieren können. Der Raspberry Pi hat keine NVRAM-Batterie, daher muss die Uhr bei jedem Bootvorgang neu gestellt werden. Dies geschieht typischerweise durch Verbindung mit einem Netzwerkdienst. Dieses Skript stellt sicher, dass die Uhr gestellt wird und während des Betriebs korrekt bleibt.

```bash
sudo id
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh | sudo bash
sleep 5
chronyc sources
```

#### 4.2. Ihre Zeitzone einstellen

```bash
cmd=$(cat <<'EOT'
clear
echo "Willkommen zum interaktiven Zeitzonen-Setup."
echo "Sie wählen zuerst eine Region, dann eine spezifische Zeitzone."

# Region auswählen
PS3="
Bitte wählen Sie eine Nummer für Ihre Region: "
select region in $(timedatectl list-timezones | grep -F / | cut -d/ -f1 | sort -u); do
  if [[ -n "$region" ]]; then
    echo "Sie haben die Region gewählt: $region"
    break
  else
    echo "Ungültige Auswahl. Bitte versuchen Sie es erneut."
  fi
done

echo ""

# Zeitzone innerhalb der Region auswählen
PS3="
Bitte wählen Sie eine Nummer für Ihre Zeitzone: "
select timezone in $(timedatectl list-timezones | grep "^$region/"); do
  if [[ -n "$timezone" ]]; then
    echo "Sie haben die Zeitzone gewählt: $timezone"
    break
  else
    echo "Ungültige Auswahl. Bitte versuchen Sie es erneut."
  fi
done

# Die gewählte Zeitzone setzen
echo
echo "Setze Zeitzone auf ${timezone}..."
sudo timedatectl set-timezone "$timezone"
echo "✅ Zeitzone wurde gesetzt."

# Änderung verifizieren
echo
echo "Aktuelle Systemzeit und Zeitzone:"
timedatectl status
EOT
)
bash -c "$cmd"
```

#### 4.3. DNS-Tools installieren
Installieren Sie das Paket `dnsutils`, damit das **Menü**-Update Zugriff auf den Befehl `dig` hat:
```bash
sudo pacman -S --noconfirm --needed dnsutils
```

#### 4.4. System- und Menü-Updates ausführen

Verwenden Sie das AudioLinux-Menüsystem, um alle Updates durchzuführen. Halten Sie Ihre E-Mail von Piero mit dem Benutzer und Passwort für den Image-Download bereit. Sie werden diese für das Menü-Update benötigen. Das System fragt nach **Ihrem Menü-Update-Benutzer**, was etwas verwirrend sein kann. Gemeint sind der Benutzername und das Passwort, die Sie zum Herunterladen des AudioLinux-Installationsimages verwendet haben.

1.  Führen Sie `menu` im Terminal aus.
2.  Wählen Sie **INSTALL/UPDATE menu**.
3.  Wählen Sie auf dem nächsten Bildschirm **UPDATE system** und lassen Sie den Prozess durchlaufen.
4.  Nachdem das System-Update abgeschlossen ist, wählen Sie auf demselben Bildschirm **Update menu**, um die neueste Version der AudioLinux-Skripte zu erhalten.
5.  Verlassen Sie das Menüsystem, um zum Terminal zurückzukehren.

---
> Hinweis: Workaround für Pacman-Update-Problem
>
> Es gab ein [bekanntes Problem](https://archlinux.org/news/linux-firmware-2025061312fe085f-5-upgrade-requires-manual-intervention/), das das System-Update aufgrund widersprüchlicher NVIDIA-Firmware-Dateien verhindern konnte (auch wenn der RPi diese nicht verwendet). Wenn Sie auf dieses Problem stoßen, entfernen Sie zuerst `linux-firmware` und installieren Sie es als Teil des Upgrades neu:
>
> ```bash
> sudo pacman -Rdd --noconfirm linux-firmware
> sudo pacman -Syu --noconfirm linux-firmware
> ```
---

#### 4.5. Neustart
Starten Sie neu, um den Kernel und andere Updates zu laden:
```bash
sudo sync && sudo reboot
```

---

### 5. Punkt-zu-Punkt Netzwerk-Konfiguration

In diesem Abschnitt erstellen wir die Netzwerkkonfigurationsdateien, die die dedizierte private Verbindung aktivieren. Um keinen physischen Monitor und Tastatur (Konsolenzugriff) zu benötigen, führen wir diese Schritte durch, während beide Geräte noch mit Ihrem Haupt-LAN verbunden und per SSH erreichbar sind.

Wenn Sie gerade das Update Ihres Diretta-Targets abgeschlossen haben, klicken Sie [hier](#52-den-diretta-target-vorkonfigurieren), um zu den Konfigurationsschritten für das Target zu springen.

---
> #### **Ein Hinweis zur Netzwerkkonfiguration: Warum keine einfache Bridge?**
>
> Benutzer, die mit AudioLinux vertraut sind, fragen sich vielleicht, warum dieser Leitfaden spezifische Skripte verwendet, um eine geroutete Punkt-zu-Punkt-Verbindung mit NAT zu konfigurieren, anstatt die einfachere Netzwerk-Bridge-Option im `menu`-System zu nutzen. Dies ist eine bewusste architektonische Entscheidung, um das höchstmögliche Maß an Netzwerkisolierung zu erreichen.
>
> * Eine **Netzwerk-Bridge** würde das Diretta-Target direkt in Ihr Haupt-LAN stellen und es somit allem nicht damit zusammenhängenden Broadcast- und Multicast-Verkehr aussetzen.
> * Unser **geroutetes Setup** schafft ein komplett separates, durch eine Firewall geschütztes Subnetz. Der Diretta-Host schützt das Target vor unnötigem Netzwerk-"Geplapper", sodass der Prozessor des Targets nur den Audiostrom verarbeitet. Dies minimiert die Systemaktivität und potenzielles elektrisches Rauschen, was das ultimative Ziel dieser puristischen Architektur ist.
>
> Während eine Bridge funktional einfacher einzurichten ist, bietet die geroutete Methode eine theoretisch überlegene Grundlage für die Audioleistung durch maximale Isolierung.
---

#### 5.1. Den Diretta-Host vorkonfigurieren

1.  **Netzwerkdateien erstellen:**
    Erstellen Sie die folgenden zwei Dateien auf dem **Diretta-Host**. Die Datei `end0.network` setzt die statische IP für die zukünftige Punkt-zu-Punkt-Verbindung. Die Datei `usb-uplink.network` stellt sicher, dass der USB-Ethernet-Adapter weiterhin eine IP von Ihrem Haupt-LAN erhält.

    *Datei: `/etc/systemd/network/end0.network*`
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

    *Datei: `/etc/systemd/network/usb-uplink.network*`
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
    # Alte generische Netzwerkdatei entfernen, um Konflikte zu vermeiden.
    sudo rm -fv /etc/systemd/network/{en,enp,auto,eth}.network
    ```

    Fügen Sie einen /etc/hosts Eintrag für das Diretta-Target hinzu:
    ```bash
    HOSTS_FILE="/etc/hosts"
    TARGET_IP="172.20.0.2"
    TARGET_HOST="diretta-target"

    # Eintrag für das Diretta-Target hinzufügen, falls nicht vorhanden
    if ! grep -q "$TARGET_IP\s\+$TARGET_HOST" "$HOSTS_FILE"; then
      printf "%s\t%s target\n" "$TARGET_IP" "$TARGET_HOST" | sudo tee -a "$HOSTS_FILE"
    fi
    ```

2.  **IP-Forwarding aktivieren:**
    ```bash
    # Für die aktuelle Sitzung aktivieren
    sudo sysctl -w net.ipv4.ip_forward=1

    # Dauerhaft über Neustarts hinweg aktivieren
    echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ip-forwarding.conf
    ```

3.  **Network Address Translation (NAT) konfigurieren:**
    ```bash
    # Sicherstellen, dass nft installiert ist
    sudo pacman -S --noconfirm --needed nftables

    # Firewall- und NAT-Regeln installieren
    cat <<'EOT' | sudo tee /etc/nftables.conf
    #!/usr/sbin/nft -f

    # Alle alten Regeln aus dem Speicher löschen
    flush ruleset

    # Eine Tabelle namens 'ip' (IPv4) namens 'my_table' erstellen
    table ip my_table {

        # === Regel 2: Port Forwarding (DNAT) ===
        # Diese Chain greift in den 'prerouting' Pfad für NAT ein
        chain prerouting {
            type nat hook prerouting priority dstnat;

            # Leite Host Port 5101 an Target Port 172.20.0.2:5001 weiter
            tcp dport 5101 dnat to 172.20.0.2:5001
        }

        # === Regel 3: Weitergeleiteten Verkehr erlauben (FILTER) ===
        # Diese Chain greift in den 'forward' Pfad für Paketfilterung ein
        chain forward {
            type filter hook forward priority 0;

            # Standardmäßig allen weitergeleiteten Verkehr verwerfen
            policy drop;

            # Verbindungen erlauben, die bereits bestehen oder verwandt sind
            ct state established,related accept

            # NEUEN Verkehr erlauben, der Ihrer Port-Forwarding-Regel entspricht
            ip daddr 172.20.0.2 tcp dport 5001 ct state new accept

            # Allen anderen NEUEN Verkehr aus dem Target-Subnetz erlauben
            ip saddr 172.20.0.0/24 accept
        }

        # === Regel 1: Internetzugriff (MASQUERADE) ===
        # Diese Chain greift in den 'postrouting' Pfad für NAT ein
        chain postrouting {
            type nat hook postrouting priority 100;

            # NAT (Masquerade) für Verkehr aus Ihrem Subnetz, der über
            # eine Schnittstelle rausgeht, die mit 'enp', 'enu' oder 'wlp' beginnt
            ip saddr 172.20.0.0/24 oifname "enp*" masquerade
            ip saddr 172.20.0.0/24 oifname "enu*" masquerade
            ip saddr 172.20.0.0/24 oifname "wlp*" masquerade
        }
    }
    EOT

    # Alten iptables-Dienst stoppen und deaktivieren, falls vorhanden
    sudo systemctl disable --now iptables.service 2>/dev/null
    sudo rm /etc/iptables/iptables.rules 2>/dev/null

    # Regeln via nft aktivieren und anwenden
    sudo systemctl enable --now nftables.service
    ```

4.  **Den Plugable USB-zu-Ethernet-Adapter konfigurieren**

    Der Standard-USB-Treiber unterstützt nicht alle Funktionen des Plugable Ethernet-Adapters. Um eine zuverlässige Leistung zu erhalten, müssen wir dem Gerätemanager des Kernels mitteilen, wie das Gerät behandelt werden soll:
    ```bash
    cat <<'EOT' | sudo tee /etc/udev/rules.d/99-ax88179a.rules
    ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0b95", ATTR{idProduct}=="1790", ATTR{bConfigurationValue}!="1", ATTR{bConfigurationValue}="1"
    EOT
    sudo udevadm control --reload-rules
    ```

5.  **Das `update_motd.sh` Skript reparieren**

    Das Skript, das den Login-Banner (`/etc/motd`) aktualisiert, behandelt den Fall von zwei Netzwerkschnittstellen nicht korrekt. Dies verhindert, dass der Login-Bildschirm nach Neustarts mit falschen IP-Adressinformationen überladen wird. Das neue Skript unten behebt dieses Problem.
    ```bash
    [ -f /opt/scripts/update/update_motd.sh.dist ] || \
    sudo mv /opt/scripts/update/update_motd.sh /opt/scripts/update/update_motd.sh.dist
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh
    sudo install -m 0755 update_motd.sh /opt/scripts/update/
    rm update_motd.sh
    ```

    Schließlich den Host ausschalten:
    ```bash
    sudo sync && sudo poweroff
    ```

#### 5.2. Den Diretta-Target vorkonfigurieren

**Hinweis:** Wenn Sie [Schritt 4](#4-system-updates-auf-beiden-ger%C3%A4ten-durchf%C3%BChren) auf dem Diretta-Target noch nicht durchgeführt haben, tun Sie das [jetzt](#4-system-updates-auf-beiden-ger%C3%A4ten-durchf%C3%BChren) und kehren Sie dann hierher zurück.

Erstellen Sie auf dem **Diretta-Target** die Datei `end0.network`. Dies konfiguriert seine statische IP und weist es an, den Diretta-Host als Gateway für den gesamten Internetverkehr zu nutzen.

*Datei: `/etc/systemd/network/end0.network*`
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
# Alte generische Netzwerkdatei entfernen, um Konflikte zu vermeiden.
sudo rm -fv /etc/systemd/network/{en,auto,eth}.network
```

Fügen Sie einen /etc/hosts Eintrag für den Diretta-Host hinzu. **Hinweis:** Auch wenn Sie einen anderen Netzwerknamen für Ihren Diretta-Host gewählt haben, ist es am besten, wenn das Diretta-Target Ihren Host als `diretta-host` kennt.
```bash
HOSTS_FILE="/etc/hosts"
HOST_IP="172.20.0.1"
HOST_NAME="diretta-host"

# Eintrag für den Diretta-Host hinzufügen, falls nicht vorhanden
if ! grep -q "$HOST_IP\s\+$HOST_NAME" "$HOSTS_FILE"; then
  printf "%s\t%s host\n" "$HOST_IP" "$HOST_NAME" | sudo tee -a "$HOSTS_FILE"
fi
```

#### 5.3. Die physische Verbindung ändern

> **Warnung:** Überprüfen Sie den Inhalt der Dateien, die Sie gerade erstellt haben, doppelt. Ein Tippfehler könnte dazu führen, dass ein Gerät nach dem Neustart nicht mehr erreichbar ist, was einen Konsolenzugriff oder das erneute Flashen der SD-Karte erfordern würde.

1.  Sobald Sie die Dateien verifiziert haben, führen Sie einen sauberen Shutdown auf **beiden** Geräten durch:
    ```bash
    sudo sync && sudo poweroff
    ```
2.  Trennen Sie beide Geräte von Ihrem Haupt-LAN Switch/Router.
3.  Verbinden Sie den **Onboard-Ethernet-Port** des Diretta-Hosts direkt mit dem **Onboard-Ethernet-Port** des Diretta-Targets unter Verwendung eines einzelnen Ethernet-Kabels.
4.  Stecken Sie den **USB-zu-Ethernet-Adapter** in einen der blauen USB 3.0 Ports am Diretta-Host Computer.
5.  Verbinden Sie den **USB-zu-Ethernet-Adapter** am Diretta-Host mit Ihrem Haupt-LAN Switch/Router.
6.  Schalten Sie beide Geräte ein.

Beim Booten verwenden sie automatisch die neuen Netzwerkkonfigurationen. **Hinweis:** Die IP-Adresse Ihres Diretta-Hosts wird sich wahrscheinlich geändert haben, da er nun über den USB-zu-Ethernet-Adapter mit Ihrem Heimnetzwerk verbunden ist. Sie müssen zur Web-Oberfläche Ihres Routers oder zur Fing-App zurückkehren, um die neue Adresse zu finden, die an diesem Punkt stabil sein sollte.

```bash
cmd=$(cat <<'EOT'
read -rp "Geben Sie die finale Adresse Ihres Diretta-Hosts ein und drücken Sie [Enter]: " RPi_IP_Address
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

Außerdem sollten Sie sich vom Host aus auf dem Target einloggen können:
```bash
echo ""
echo "\$ ssh target"
ssh -o StrictHostKeyChecking=accept-new target
```

Vom Target aus versuchen wir, einen Host im Internet anzupingen, um zu verifizieren, dass die Verbindung funktioniert:
```bash
echo ""
echo "\$ ping -c 3 one.one.one.one"
ping -c 3 one.one.one.one
```

---

### 6. Komfortabler & Sicherer SSH-Zugriff

#### 6.1. Die `ProxyJump` Anforderung

Da das Netzwerk nun konfiguriert ist, befindet sich das **Diretta-Target** in einem isolierten Netzwerk (`172.20.0.0/24`) und kann nicht direkt von Ihrem Haupt-LAN erreicht werden. Der einzige Weg darauf zuzugreifen, ist der "Sprung" (Jump) über den **Diretta-Host**.

Die `ProxyJump`-Anweisung in Ihrer lokalen SSH-Konfiguration ist die Standardmethode, um dies zu erreichen.

1.  Führen Sie diesen Befehl auf Ihrem lokalen Computer aus (nicht auf dem Raspberry Pi). Er wird Sie nach der IP-Adresse des Diretta-Hosts fragen und dann den genauen Konfigurationsblock ausgeben, den Sie benötigen.
```bash
cmd=$(cat <<'EOT'
clear
# --- Interaktives SSH Alias Setup Skript ---

SSH_CONFIG_FILE="$HOME/.ssh/config"
SSH_DIR="$HOME/.ssh"

# --- Sicherstellen, dass das .ssh Verzeichnis und die Config-Datei existieren ---
mkdir -p "$SSH_DIR"
chmod 0700 "$SSH_DIR"
touch "$SSH_CONFIG_FILE"
chmod 0600 "$SSH_CONFIG_FILE"

# --- Empfohlene globale Einstellungen definieren ---
GLOBAL_SETTINGS=$(cat <<'EOF'
# --- Empfohlene Globale SSH Einstellungen ---
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519

EOF
)

# --- Globale Einstellungen voranstellen, falls sie nicht existieren ---
if ! grep -q "AddKeysToAgent yes" "$SSH_CONFIG_FILE"; then
  echo "✅ Füge empfohlene globale SSH Einstellungen hinzu..."
  # Temporäre Datei nutzen, um Einstellungen voranzustellen
  echo "$GLOBAL_SETTINGS" | cat - "$SSH_CONFIG_FILE" > temp_ssh_config && mv temp_ssh_config "$SSH_CONFIG_FILE"
else
  echo "✅ Empfohlene globale SSH Einstellungen existieren bereits. Keine Änderungen."
fi

# --- Diretta-spezifische Host-Konfigurationen hinzufügen ---
if grep -q "Host diretta-host" "$SSH_CONFIG_FILE"; then
  echo "✅ SSH Konfiguration für 'diretta-host' existiert bereits. Keine Änderungen."
else
  read -rp "Geben Sie die LAN IP-Adresse Ihres Diretta-Hosts ein und drücken Sie [Enter]: " Diretta_Host_IP

  # Neue Konfiguration anhängen
  cat <<EOT_HOSTS >> "$SSH_CONFIG_FILE"

# --- Diretta Konfiguration (durch Skript hinzugefügt) ---
Host diretta-host host
    HostName ${Diretta_Host_IP}
    User audiolinux

Host diretta-target target
    HostName 172.20.0.2
    User audiolinux
    ProxyJump diretta-host
EOT_HOSTS

  echo "✅ SSH Konfiguration für 'diretta-host' und 'diretta-target' wurde hinzugefügt."
fi

# --- Bereinigung von StrictHostKeyChecking aus älteren Versionen dieses Leitfadens ---
# Dies ist mit dem empfohlenen SSH-Key-Setup nicht mehr erforderlich
if command -v sed >/dev/null; then
    sed -i.bak -e '/StrictHostKeyChecking/d' "$SSH_CONFIG_FILE"
    # Leere Zeilen entfernen, die übrig geblieben sein könnten
    sed -i.bak -e '/^$/N;/^\n$/D' "$SSH_CONFIG_FILE"
    rm -f "${SSH_CONFIG_FILE}.bak"
fi

echo ""
echo "--- Ihre ~/.ssh/config Datei enthält nun: ---"
cat "$SSH_CONFIG_FILE"
EOT
)
bash -c "$cmd"
```

2.  **Verbindung verifizieren:**

Sie sollten sich nun über die neuen Aliase mit beiden Geräten verbinden können. Testen Sie die Verbindung mit den folgenden Befehlen:

**Um sich beim Diretta-Host anzumelden:**
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-host
```

Tippen Sie `exit` zum Ausloggen.

**Um sich beim Diretta-Target anzumelden:** *(Sie werden zweimal nach dem Passwort gefragt)*
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-target
```
**Hinweis:** Sie werden einmal für den `diretta-host` (den Jump-Host) und ein zweites Mal für das `diretta-target` selbst gefragt. Der nächste Abschnitt ersetzt dies durch eine nahtlose schlüsselbasierte Authentifizierung.

**Hinweis:** Sie können kurz `ssh host` und `ssh target` verwenden.

#### 6.2. Empfohlen: Sichere Authentifizierung mit SSH-Schlüsseln

Obwohl Sie Passwörter verwenden können, ist die sicherste und bequemste Methode die Public-Key-Authentifizierung. Unsere SSH-Konfiguration automatisiert den Großteil dieses Prozesses. Nach einer einmaligen Einrichtung können Sie sich sicher bei Host und Target anmelden, ohne ein Passwort einzutippen.

**Auf Ihrem lokalen Computer:**

1.  **Einen SSH-Schlüssel erstellen (falls Sie noch keinen haben):**
    Es ist bewährte Praxis, einen modernen Algorithmus wie `ed25519` zu verwenden. Wenn Sie gefragt werden, geben Sie eine starke, einprägsame **Passphrase** ein. Dies ist nicht Ihr Login-Passwort; es ist ein Passwort, das Ihre private Schlüsseldatei selbst schützt.

    ```bash
    ssh-keygen -t ed25519 -C "audiolinux"
    ```

2.  **Ihren öffentlichen Schlüssel auf die Geräte kopieren:**
    Diese Befehle gewähren Ihrem Schlüssel sicheren Zugriff auf jedes Gerät. Der erste Befehl fragt nach dem Passwort des Diretta-Hosts. Da dies die Verbindung zum Host passwortlos macht, fragt der zweite Befehl nur noch nach dem Passwort des Diretta-Targets.

    ```bash
    echo ""
    ssh-copy-id diretta-host
    echo ""
    ssh-copy-id diretta-target
    ```

3.  **Sicher einloggen:**
    Sie können nun per SSH auf Ihre Geräte zugreifen. Beim ersten Verbindungsaufbau zu jedem Gerät werden Sie nach der **Passphrase** gefragt, die Sie in Schritt 1 erstellt haben.

    ```bash
    ssh diretta-host
    ```

    * **Unter Linux:** Dank der Einstellung `AddKeysToAgent yes` wird Ihr Schlüssel zum SSH-Agent für Ihre aktuelle Terminalsitzung hinzugefügt. Sie werden erst nach einem Neustart oder Start einer neuen Login-Sitzung wieder nach der Passphrase gefragt.

---

### (Optional) Für ein verbessertes Linux-Erlebnis

Wenn Sie Linux-Benutzer sind und möchten, dass Ihre SSH-Schlüssel-Passphrase über Neustarts hinweg erhalten bleibt (ähnlich wie bei macOS), wird die Installation von `keychain` dringend empfohlen.

  * **keychain installieren (Ubuntu/Debian):**

    ```bash
    sudo apt update && sudo apt install keychain
    ```

  * **Ihre Shell konfigurieren:** Fügen Sie die folgende Zeile zu Ihrer `~/.bashrc` (oder `~/.zshrc`, `~/.profile`, etc.) hinzu, um `keychain` zu starten, wenn Sie ein Terminal öffnen. Es wird nur einmal nach Ihrer Passphrase fragen, beim ersten Öffnen eines Terminals nach einem Neustart.

    ```bash
    eval `keychain --eval --quiet id_ed25519`
    ```

  * Laden Sie Ihre Shell neu, indem Sie ein neues Terminal öffnen oder `source ~/.bashrc` ausführen.

Sie können nun per SSH auf beide Geräte (`ssh diretta-host`, `ssh diretta-target`) zugreifen, ohne nach einem Passwort gefragt zu werden, sicher authentifiziert durch Ihren SSH-Schlüssel.

---

### 7. Allgemeine Systemoptimierungen

Bitte führen Sie diese Schritte auf *beiden* Computern durch (Diretta-Host und Target). Wenn Sie später ein `menu`-Update durchführen, müssen Sie den `sudoers`-Fix erneut ausführen.

#### 7.1. Systemd "Degraded" Status beheben

Bei einer frischen AudioLinux-Installation wird der Systemstatus oft als `degraded` (beeinträchtigt) gemeldet. Dies wird typischerweise durch eine harmlose Inkonsistenz zwischen den Gruppendateien des Systems (`/etc/group` und `/etc/gshadow`) verursacht. Der folgende Befehl synchronisiert diese Dateien sicher, was den fehlgeschlagenen `shadow.service` behebt und einen sauberen Systemzustand gewährleistet.

```bash
sudo grpconv
```

#### 7.2. `sudoers` Regel-Priorität korrigieren

Eine Standardregel in der Hauptdatei `/etc/sudoers` kann manchmal spezifischere Regeln außer Kraft setzen, die für die Web-Oberfläche und andere Funktionen benötigt werden. Dies kann dazu führen, dass Befehle, die passwortlos sein sollten, fälschlicherweise nach einem Passwort fragen.

Das folgende Skript korrigiert sicher die Reihenfolge der Regeln in der `/etc/sudoers`-Datei, um sicherzustellen, dass spezifische Ausnahmen korrekt verarbeitet werden. Das Skript nimmt nur Änderungen vor, wenn es die falsche Reihenfolge erkennt.

```bash
SUDOERS_FILE="/etc/sudoers"
TEMP_SUDOERS=$(mktemp)

# Perl-Filter verwenden, um eine korrigierte Version der sudoers-Datei zu erstellen.
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

# Die neue Datei mit visudo validieren vor der Installation
if [ -s "$TEMP_SUDOERS" ] && sudo visudo -c -f "$TEMP_SUDOERS"; then
    echo "Sudoers Datei hat die Validierung bestanden. Installiere korrigierte Version..."
    # install verwenden, um korrekte Besitzer/Rechte zu setzen und das Original zu ersetzen
    sudo install -m 0440 -o root -g root "$TEMP_SUDOERS" "$SUDOERS_FILE"
else
    echo "FEHLER: Die modifizierte sudoers Datei hat die Validierung nicht bestanden. Keine Änderungen." >&2
fi
rm -f "$TEMP_SUDOERS"
```

#### 7.3. Bootzeit optimieren
Um eine lange Bootverzögerung zu verhindern, während das System auf eine Netzwerkverbindung wartet, deaktivieren wir den "wait-online" Dienst.
```bash
# Den Netzwerk-Warte-Dienst deaktivieren, um lange Bootverzögerungen zu verhindern
sudo systemctl disable systemd-networkd-wait-online.service

# Ein Override erstellen, damit das MOTD-Skript auf eine Standardroute wartet
sudo mkdir -p /etc/systemd/system/update_motd.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/update_motd.service.d/wait-for-ip.conf
[Service]
ExecStartPre=/bin/sh -c "while [ -z \"$(ip route show default)\" ]; do sleep 0.5; done"
EOT
```

#### 7.4. Das Reparatur-Skript erstellen
Das Standardverhalten von Arch Linux ist es, das /boot Dateisystem in einem unsauberen Zustand zu lassen, wenn der Computer nicht sauber heruntergefahren wurde. Das ist meistens sicher, aber ich habe festgestellt, dass es zu einer Race Condition führen kann, wenn unser privates Netzwerk hochgefahren wird. Dazu kommt, dass Benutzer diese Geräte wahrscheinlich einfach ausstecken, ohne sie vorher herunterzufahren. Um uns vor diesen Problemen zu schützen, fügen wir ein Workaround-Skript hinzu, das das /boot Dateisystem (das nur während Software-Updates geändert wird) sauber hält.

Dieses Skript kann sowohl automatisch beim Booten als auch manuell auf einem laufenden System sicher ausgeführt werden.
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh
sudo install -m 0755 check-and-repair-boot.sh /usr/local/sbin/
rm check-and-repair-boot.sh
```

#### 7.5. Die `systemd` Service-Datei erstellen und den Dienst aktivieren
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

#### 7.6. Disk I/O minimieren
Ändern Sie `#Storage=auto` zu `Storage=volatile` in `/etc/systemd/journald.conf`
```bash
sudo sed -i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
```

---

### 8. Installation & Konfiguration der Diretta-Software

#### 8.1. Auf dem Diretta-Target

1.  Verbinden Sie Ihren USB-DAC mit einem der schwarzen USB 2.0 Ports am **Diretta-Target** und stellen Sie sicher, dass der DAC eingeschaltet ist.
2.  Verbinden Sie sich per SSH mit dem Target: `ssh diretta-target`.
3.  Kompatible Compiler-Toolchain konfigurieren:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    source /etc/profile.d/llvm_diretta.sh
    ```
4.  Führen Sie `menu` aus.
5.  Wählen Sie **AUDIO extra menu**.
6.  Wählen Sie **DIRETTA target installation**. Sie sehen das folgende Menü:
    ```text
    What do you want to do?

    0) Install previous stable version
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
7.  Führen Sie diese Aktionen nacheinander aus:
    * Wählen Sie **1) Install/update**, um die Software zu installieren.
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
    * Wählen Sie **4) Edit configuration**. Setzen Sie `AlsaLatency=20` für ein Raspberry Pi 5 Target oder `AlsaLatency=40` für einen RPi4.
    * Wählen Sie **6) License**. Das System wird Hi-Res (höher als 44,1 kHz PCM Audio) für 6 Minuten im Testmodus abspielen. Folgen Sie dem Link auf dem Bildschirm und den Anweisungen, um Ihre Volllizenz für Hi-Res-Support zu kaufen und anzuwenden. Dies erfordert den in Schritt 5 konfigurierten Internetzugang.
    * Wählen Sie **8) Exit**. Folgen Sie den Aufforderungen, um zum Terminal zurückzukehren.

#### 8.2. Auf dem Diretta-Host

1.  Verbinden Sie sich per SSH mit dem Host: `ssh diretta-host`.

2.  Kompatible Compiler-Toolchain konfigurieren:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    source /etc/profile.d/llvm_diretta.sh
    ```

3.  Führen Sie `menu` aus.

4.  Wählen Sie **AUDIO extra menu**.

5.  Wählen Sie **DIRETTA host installation/configuration**. Sie sehen das folgende Menü:
    ```text
    What do you want to do?

    0) Install previous stable version
    1) Install/update last version
    2) Enable/Disable Diretta daemon
    3) Set Ethernet interface
    4) Edit configuration
    5) Copy and edit new default configuration
    6) Diretta log
    7) Exit

    ?
    ```

6.  Führen Sie diese Aktionen nacheinander aus:
    * Wählen Sie **1) Install/update**, um die Software zu installieren. *(Hinweis: Sie sehen möglicherweise `error: package 'lld' was not found`. Keine Sorge, das wird automatisch durch die Installation korrigiert)*
    * Wählen Sie **2) Enable/Disable Diretta daemon** und aktivieren Sie ihn.
    * Wählen Sie **3) Set Ethernet interface**. Es ist entscheidend, `end0` auszuwählen, die Schnittstelle für die Punkt-zu-Punkt-Verbindung.
        ```text
        ?3
        Your available Ethernet interfaces are: end0  enu1
        Please type the name of your preferred interface:
        end0
        ```
    * Wählen Sie **4) Edit configuration** nur, wenn Sie fortgeschrittene Änderungen vornehmen müssen. Die vorherigen Schritte sollten ausreichen; hier sind jedoch einige optimierte Einstellungen, die Sie vielleicht ausprobieren möchten:
        ```text
        TargetProfileLimitTime=0
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
        TargetProfileLimitTime=0
        ThredMode=1
        InfoCycle=100000
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
        unInitMemDet=disable
        CpuSend=
        CpuOther=
        LatencyBuffer=0
        disConnectDelay=enable
        singleMode=
        EOT
        ```
    * Wählen Sie **7) Exit**. Folgen Sie den Aufforderungen, um zum Terminal zurückzukehren.

7.  Erstellen Sie einen Override, damit der Diretta-Dienst bei einem Fehler automatisch neu startet:
    ```bash
    sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta_alsa.service.d/restart.conf
    [Service]
    Restart=on-failure
    RestartSec=5
    EOT
    ```

---

### 9. Abschließende Schritte & Roon-Integration

1.  Führen Sie `menu` aus, falls Sie nach dem vorherigen Schritt zum Terminal zurückgekehrt sind, andernfalls gehen Sie zum **Main menu**.

2.  **Roon Bridge installieren (auf dem Host):** Wenn Sie Roon verwenden, führen Sie die folgenden Schritte auf dem **Diretta-Host** aus:
    * Führen Sie `menu` aus.
    * Wählen Sie **INSTALL/UPDATE menu**.
    * Wählen Sie **INSTALL/UPDATE Roonbridge**.
    * Die Installation wird fortgesetzt. Dies kann ein oder zwei Minuten dauern.

3.  **Roon Bridge aktivieren (auf dem Host):**
    * Wählen Sie **Audio menu** aus dem Hauptmenü.
    * Wählen Sie **SHOW audio service**.
    * Wenn Sie **roonbridge** nicht unter den aktivierten Diensten sehen, wählen Sie **ROONBRIDGE enable/disable**.

4.  **Beide Geräte neu starten:** Für einen sauberen Start starten Sie sowohl das Target als auch den Host neu, in dieser Reihenfolge:
    ```bash
    sudo sync && sudo reboot
    ```

5.  **Roon konfigurieren:**
    * Öffnen Sie Roon auf Ihrem Steuergerät.
    * Gehen Sie zu `Einstellungen` -> `Audio`.
    * Unter dem Abschnitt "Diretta" sollten Sie Ihr Gerät sehen. Der Name basiert auf Ihrem DAC.
    * Klicken Sie auf `Aktivieren`, geben Sie ihm einen Namen, und Sie sind bereit, Musik abzuspielen!

Ihre dedizierte Diretta-Verbindung ist nun vollständig für eine unverfälschte, isolierte Audiowiedergabe konfiguriert.
**Hinweis:** Die "Limited"-Zone für Diretta-Target-Tests verschwindet nach sechs Minuten Hi-Res-Musikwiedergabe aus Roon. Das ist normal. An diesem Punkt müssen Sie eine Lizenz für das Diretta-Target erwerben. Die Kosten betragen derzeit 100 €, und die Aktivierung kann bis zu 48 Stunden dauern. Sie erhalten zwei E-Mails vom Diretta-Team. Die erste ist Ihre Quittung; die zweite Ihre Aktivierungsbenachrichtigung. Sobald Sie die Aktivierungs-E-Mail erhalten haben, starten Sie Ihren Target-Computer neu, um die Aktivierung zu übernehmen.

> ---
> ### ✅ Checkpoint: Überprüfen Sie Ihr Kernsystem
>
> Ihr Diretta- und Roon-Kernsystem sollte nun voll funktionsfähig sein. Um alle Dienste und Verbindungen zu überprüfen, fahren Sie bitte mit [**Anhang 5**](#14-anhang-5-system-gesundheitschecks) fort und führen Sie den universellen **System Health Check** sowohl auf dem Host als auch auf dem Target aus.
>
> ---

---

## 10. Anhang 1: Optionale Argon ONE Lüftersteuerung
Wenn Sie sich für ein Argon ONE Gehäuse für Ihren Raspberry Pi entschieden haben, geht das Standard-Installationsskript davon aus, dass Sie ein Debian-Betriebssystem verwenden. Da AudioLinux jedoch auf Arch Linux basiert, müssen Sie stattdessen diesen Schritten folgen.

Wenn Sie Argon ONE Gehäuse für sowohl Diretta-Host als auch -Target verwenden, müssen Sie diese Schritte auf beiden Computern durchführen.

### Schritt 1: Überspringen Sie das `argon1.sh` Skript im Handbuch
Das Handbuch besagt, dass man das `argon1.sh` Skript von download.argon40.com herunterladen und an `bash` weiterleiten soll. Dies funktioniert unter AudioLinux nicht, da das Skript ein Debian-basiertes Betriebssystem voraussetzt. Überspringen Sie diesen Schritt also und folgen Sie stattdessen den unten stehenden Schritten.

### Schritt 2: Konfigurieren Sie Ihr System:
Diese Befehle aktivieren die I2C-Schnittstelle und fügen das spezifische `dtoverlay` für das Argon ONE Gehäuse hinzu. Das Skript versucht zunächst, den `i2c_arm` Parameter auszukommentieren, falls er auskommentiert ist, und fügt dann das `argonone` Overlay hinzu, falls es fehlt, um Fehler und doppelte Einträge zu vermeiden.
```bash
BOOT_CONFIG="/boot/config.txt"
I2C_PARAM="dtparam=i2c_arm=on"

# --- Enable I2C by uncommenting the line if it exists ---
if grep -q -F "#$I2C_PARAM" "$BOOT_CONFIG"; then
  echo "Enabling I2C parameter..."
  sudo sed -i -e "s/^#\($I2C_PARAM\)/\1/" "$BOOT_CONFIG"
fi
```

### Schritt 3: `udev`-Berechtigungen konfigurieren
```bash
cat <<'EOT' | sudo tee /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c-[0-9]*", MODE="0666"
EOT
```

### Schritt 4: Das Argon One Paket installieren
```bash
yay -S argonone-c-git
```

**Hinweis:** Wenn der obige Befehl mit Compiler-Fehlern fehlschlägt, können Sie dieses manuelle Verfahren versuchen, um das Paket zu reparieren und zu installieren:
```bash
# Clone the package repository
git clone https://aur.archlinux.org/argonone-c-git.git
cd argonone-c-git

# Download source code without building
makepkg -o

# Apply patch to fix compilation error with GCC 14+
sed -i 's/_timer_thread()/_timer_thread(void *args)/g' src/argonone-c-git/src/event_timer.c

# Compile and install using the patched source
makepkg -e -i --noconfirm

# Clean up
cd ..
rm -rf argonone-c-git
```

### Schritt 5: Argon ONE Gehäuse von Hardware- auf Softwaresteuerung umschalten
```bash
sudo pacman -S --noconfirm --needed i2c-tools libgpiod
```

```bash
# Create systemd overrides to switch the case to software mode on boot
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

### Schritt 6: Den Dienst aktivieren
```bash
# Reload the systemd manager to read the new configuration
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable argononed.service
```

### Schritt 7: Neustart
Starten Sie schließlich Ihren Raspberry Pi neu, damit alle Änderungen wirksam werden (zuerst Target, dann Host):
```bash
sudo sync && sudo reboot
```

Nun wird der Lüfter durch den Daemon gesteuert und der Power-Button hat seine volle Funktionalität.

### Schritt 8: Den Dienst verifizieren
```bash
systemctl status argononed.service
journalctl -u argononed.service -b
```

### Schritt 9: Lüftermodus und Einstellungen überprüfen:
Um die aktuellen Konfigurationswerte zu sehen, führen Sie den folgenden Befehl aus:
```bash
sudo argonone-cli --decode
```

Um diese Werte anzupassen, müssen Sie eine Konfigurationsdatei erstellen. Verwenden Sie diese Werte als Startpunkt:
```bash
cat <<'EOT' | sudo tee /etc/argononed.conf
[Schedule]
temp0=55
fan0=0
temp1=60
fan1=50
temp2=65
fan2=100

[Setting]
hysteresis=3
EOT
```

Starten Sie den Dienst neu, um die neuen Konfigurationswerte zu übernehmen:
```bash
sudo systemctl restart argononed.service
echo ""
echo "Updated fan values:"
sleep 5
sudo argonone-cli --decode
```

Fühlen Sie sich nun frei, die Werte nach Bedarf anzupassen, indem Sie den obigen Schritten folgen.

---

## 11. Anhang 2: Optionale IR-Fernbedienung

Dieser Leitfaden enthält Anweisungen zur Installation und Konfiguration einer IR-Fernbedienung zur Steuerung von Roon. Die Einrichtung ist in zwei Teile gegliedert.

  * **Teil 1** behandelt die hardwarespezifische Einrichtung. Sie wählen **einen** der beiden Anhänge, je nachdem, ob Sie den Flirc USB-Empfänger oder den im Argon One-Gehäuse integrierten Empfänger verwenden.
  * **Teil 2** behandelt die Software-Einrichtung für das `roon-ir-remote` Steuerungsskript, die für beide Hardware-Optionen identisch ist.

**Hinweis:** Sie führen diese Schritte _nur_ auf dem Diretta-Host durch. Das Target sollte nicht für die Weiterleitung von IR-Fernbedienungsbefehlen an den Roon Server verwendet werden.

---

### **Teil 1: Hardware-Einrichtung des IR-Empfängers**

*Folgen Sie dem Anhang für die Hardware, die Sie verwenden.*

#### **Option 1: Flirc USB IR-Empfänger Einrichtung**

1.  **Kauf und Programmierung des Flirc-Geräts:**
    Sie benötigen den Flirc USB IR-Empfänger, der auf deren Website erworben werden kann: https://flirc.tv/products/flirc-usb-receiver

    Das Flirc-Gerät muss an einem Desktop-Computer mit der Flirc GUI-Software programmiert werden.

      * Stecken Sie den Flirc in Ihren Desktop-Computer und öffnen Sie die Flirc GUI.
      * Gehen Sie zu `Controllers` und wählen Sie `Full Keyboard`.
      * Programmieren Sie die für das Skript benötigten Tasten (z.B. KEY_UP, KEY_DOWN, KEY_ENTER usw.), indem Sie die Taste in der GUI anklicken und dann die entsprechende Taste auf Ihrer physischen Fernbedienung drücken.
      * Sobald programmiert, stecken Sie den Flirc in den **Diretta-Host**.

2.  **Testen des Flirc-Geräts:**
    Verifizieren Sie, dass der Raspberry Pi den Flirc als Tastatur erkennt.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Wählen Sie das "Flirc"-Gerät aus dem Menü. Wenn Sie Tasten auf Ihrer Fernbedienung drücken, sollten Sie Tastaturereignisse auf dem Bildschirm sehen.

3.  Springen Sie zu [Teil 2: Einrichtung des Steuerungs-Skripts](#teil-2-einrichtung-des-steuerungs-skripts)

---

#### **Option 2: Argon One IR-Fernbedienung Einrichtung**

1.  **Die IR-Empfänger-Hardware aktivieren:**
    Sie müssen das Hardware-Overlay für den IR-Empfänger des Argon One-Gehäuses aktivieren.

      * Dieser Befehl fügt das erforderliche Hardware-Overlay sicher zu Ihrer `/boot/config.txt`-Datei hinzu und prüft zuerst, ob es nicht bereits hinzugefügt wurde.
        ```bash
        BOOT_CONFIG="/boot/config.txt"
        IR_CONFIG="dtoverlay=gpio-ir,gpio_pin=23"

        # IR-Remote-Overlay hinzufügen, falls noch nicht vorhanden
        if ! sed 's/#.*//' $BOOT_CONFIG | grep -q -F "$IR_CONFIG"; then
          echo "Aktiviere Argon One IR-Empfänger..."
          sudo sed -i "/# Uncomment this to enable infrared communication./a $IR_CONFIG" /boot/config.txt
        else
          echo "Argon One IR-Empfänger bereits aktiviert."
        fi
        ```
      * Ein Neustart ist erforderlich, damit die Hardwareänderung wirksam wird.
        ```bash
        sudo sync && sudo reboot
        ```

2.  **IR-Tools installieren und Protokolle aktivieren:**
    Installieren Sie `ir-keytable`
    ```bash
    sudo pacman -S --noconfirm v4l-utils
    ```

3.  **Tasten-Scancodes erfassen:**
     Aktivieren Sie alle Kernel-Protokolle, damit Signale von Ihrer Fernbedienung dekodiert werden können. Führen Sie das Test-Tool aus, um den eindeutigen Scancode für jede Fernbedienungstaste zu sehen.
    ```bash
    sudo ir-keytable -p all
    sudo ir-keytable -t
    ```

    Drücken Sie jede Taste, die Sie verwenden möchten, und notieren Sie deren Scancode aus der Ausgabe des `MSC_SCAN` Ereignisses (z.B. `value ca`). Drücken Sie `Ctrl+C`, wenn Sie fertig sind.

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
      * Wenn die Scancodes in der Beispieldatei oben nicht mit denen übereinstimmen, die Sie aufgezeichnet haben, bearbeiten Sie die Datei (`sudo nano /etc/rc_keymaps/argon.toml`) und passen Sie sie an.

5.  **Einen `systemd` Service zum Laden der Keymap erstellen:**
    Dieser Dienst lädt Ihre Keymap automatisch beim Booten.

    Erstellen Sie eine neue Service-Datei und aktivieren Sie den Dienst:
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
    Verifizieren Sie, dass das System Tastaturereignisse von der IR-Fernbedienung empfängt.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Wählen Sie das `gpio_ir_recv` Gerät. Wenn Sie Tasten auf der Fernbedienung drücken, sollten Sie die entsprechenden Tastenereignisse sehen.
    Tippen Sie `CTRL-C`, wenn Sie mit dem Testen fertig sind.

---

### **Teil 2: Einrichtung des Steuerungs-Skripts**

*Nachdem Sie Ihre Hardware in Teil 1 eingerichtet haben, folgen Sie diesen Schritten, um das Python-Steuerungsskript zu installieren und zu konfigurieren.*

### **Schritt 1: `audiolinux` zur Gruppe `input` hinzufügen**
Dies ist notwendig, damit das `audiolinux`-Konto Zugriff auf Ereignisse des Fernbedienungsempfängers hat.
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

Installieren Sie `pyenv` und die neueste stabile Version von Python.

```bash
# Build-Abhängigkeiten installieren
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

# pyenv nur installieren, wenn es noch nicht installiert ist
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

# Datei einlesen, um pyenv in der aktuellen Shell verfügbar zu machen
. ~/.bashrc

# Die neueste Python-Version installieren und setzen, falls noch nicht geschehen
PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
  echo "--- Installing Python ${PYVER}. This will take several minutes... ---"
  pyenv install $PYVER
else
  echo "--- Python ${PYVER} is already installed. Skipping installation. ---"
fi

# Globale Python-Version setzen
pyenv global $PYVER
```

**Hinweis:** Es ist normal, dass der Teil `Installing Python-3.14.2...` etwa 10 Minuten dauert, da Python aus dem Quellcode kompiliert wird. Geben Sie nicht auf! Fühlen Sie sich frei, sich bei schöner Musik über Ihre neue Diretta-Zone in Roon zu entspannen, während Sie warten. Sie sollte verfügbar sein, während Python auf dem Host installiert wird.

---

### **Schritt 3: `roon-ir-remote` Software-Repo herunterladen**

Klonen Sie das Skript-Repository und rufen Sie einen Patch ab, um Tastencodes korrekt nach Namen statt nach Nummer zu behandeln.

```bash
cd
# Repo klonen, falls es nicht existiert, sonst aktualisieren
if [ ! -d "roon-ir-remote" ]; then
  git clone https://github.com/dsnyder0pc/roon-ir-remote.git
else
  (cd roon-ir-remote && git pull)
fi
```

---

### **Schritt 4: Die Roon-Umgebungs-Konfigurationsdatei erstellen**

Konfigurieren Sie das Skript mit Ihren Roon-Details. **Hinweis:** Die `event_mapping` Codes müssen mit den Tastennamen übereinstimmen, die Sie in Ihrer Hardware-Einrichtung definiert haben (`KEY_ENTER`, `KEY_VOLUMEUP`, usw.).

```bash
bash <<'EOF'
# --- Start of Script ---

# Roon Zone abfragen und in Variable speichern
echo "Geben Sie den Namen Ihrer Roon-Zone ein."
echo "WICHTIG: Dieser muss exakt mit dem Zonennamen in der Roon-App übereinstimmen (Groß-/Kleinschreibung beachten)."
# Diese Zeile ist der Fix: < /dev/tty weist read an, das Terminal zu nutzen
read -rp "Geben Sie Ihren Roon-Zonennamen ein: " MY_ROON_ZONE < /dev/tty

# Zielverzeichnis sicherstellen
mkdir -p roon-ir-remote

# Konfigurationsdatei mittels Here Document erstellen
# Die Variable wird nun korrekt substituiert
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
        "vol_up": "KEY_VOLUMEUP",
        "vol_down": "KEY_VOLUMEDOWN",
        "mute": "KEY_MUTE"
      }
    }
  }
}
EOD

echo ""
echo "✅ Configuration file 'roon-ir-remote/app_info.json' created successfully."

# --- End of Script ---
EOF
```

---

### **Schritt 5: `roon-ir-remote` vorbereiten und testen**

Installieren Sie die Abhängigkeiten des Skripts in eine virtuelle Umgebung und führen Sie es zum ersten Mal aus.

```bash
cd ~/roon-ir-remote
# Virtuelle Umgebung nur erstellen, wenn sie noch nicht existiert
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

Wenn Sie das Skript zum ersten Mal ausführen, müssen Sie **die Erweiterung in Roon autorisieren**, indem Sie zu `Einstellungen` -> `Erweiterungen` gehen.

Während Musik in Ihrer neuen Diretta Roon-Zone spielt, richten Sie Ihre IR-Fernbedienung direkt auf den Diretta-Host-Computer und drücken Sie die Play/Pause-Taste (möglicherweise die mittlere Taste im 5-Wege-Controller). Versuchen Sie auch Weiter und Zurück. Wenn diese nicht funktionieren, überprüfen Sie Ihr Terminalfenster auf Fehlermeldungen. Sobald Sie mit dem Testen fertig sind, tippen Sie `CTRL-C` zum Beenden.

---

### **Schritt 6: Einen `systemd` Service erstellen**

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

# Dienst aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable --now roon-ir-remote.service

# Status prüfen
sudo systemctl status roon-ir-remote.service
```

---

### **Schritt 7: Die Logs kurz beobachten:**
```bash
journalctl -b -u roon-ir-remote.service -f
```

Tippen Sie `CTRL-C`, sobald Sie zufrieden sind, dass alles wie erwartet funktioniert.

---

### **Schritt 8: `set-roon-zone` Skript installieren**
Es ist gut, ein Skript zu haben, mit dem Sie den Roon-Zonennamen später bei Bedarf aktualisieren können. So installieren Sie es:
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone
sudo install -m 0755 set-roon-zone /usr/local/bin/
rm set-roon-zone
```

Um es zu verwenden, loggen Sie sich einfach auf dem Diretta-Host-Computer ein und tippen Sie:
```bash
set-roon-zone
```
Folgen Sie den Aufforderungen, um den neuen Namen für Ihre Roon-Zone einzugeben. Möglicherweise müssen Sie das Root-Passwort eingeben, damit die Änderungen wirksam werden.

**Hinweis: Ein besserer Weg, die Zone festzulegen**
Obwohl dieses Skript perfekt funktioniert, ist die empfohlene Methode zum Ändern der Roon-Zone die Verwendung der AnCaolas Link System Control Web-Anwendung, die in [Anhang 4](#13-anhang-4-optionale-web-oberfl%C3%A4che-zur-systemsteuerung) detailliert beschrieben wird. Die Web-Oberfläche bietet eine dedizierte Seite zum Anzeigen und Bearbeiten des Zonennamens von Ihrem Telefon oder Browser aus.

### **Schritt 9: Profit! 📈**

> ---
> ### ✅ Checkpoint: Überprüfen Sie Ihre IR-Fernbedienungseinrichtung
>
> Ihre IR-Fernbedienungshardware und -software sollten nun konfiguriert sein. Um die Einrichtung zu überprüfen, fahren Sie mit **[Anhang 5](#14-anhang-5-system-gesundheitschecks)** fort und führen Sie den universellen **System Health Check** auf dem Diretta-Host aus.
>
> ---

Ihre IR-Fernbedienung sollte nun Roon steuern. Viel Spaß!

---

## 12. Anhang 3: Optionaler Purist-Modus
Auf dem Diretta-Target-Computer gibt es minimale Netzwerk- und Hintergrundaktivitäten, die nicht mit der Musikwiedergabe über das Diretta-Protokoll zusammenhängen. Einige Benutzer ziehen es jedoch vor, zusätzliche Schritte zu unternehmen, um die Möglichkeit solcher Aktivitäten zu reduzieren. Wir befinden uns bereits am extremen Rand der Audioleistung, also warum nicht?

---
> KRITISCHE WARNUNG: NUR für das Diretta-Target
>
> Das `purist-mode` Skript und alle Anweisungen in diesem Anhang sind ausschließlich für das Diretta-Target bestimmt.
>
> Installieren oder führen Sie dieses Skript NICHT auf dem Diretta-Host aus. Dies würde die Verbindung des Hosts zu Ihrem Hauptnetzwerk trennen, ihn unerreichbar machen und die Kommunikation mit Ihrem Roon Core oder Streaming-Diensten verhindern. Dies würde das gesamte System funktionsunfähig machen, bis Sie Konsolenzugriff (mit physischer Tastatur und Monitor) erhalten, um die Änderungen rückgängig zu machen.
---

### Schritt 1: Das `purist-mode` Skript installieren **(nur auf dem Diretta-Target Computer)**
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode
sudo install -m 0755 purist-mode /usr/local/bin
rm purist-mode

# Skript zum Anzeigen des Purist-Modus-Status beim Login
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

Um es auszuführen, loggen Sie sich einfach auf dem Diretta-Target ein und tippen Sie `purist-mode`:
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
  -> Dropping default gateway...

✅ Purist Mode is ACTIVE.
```

Hören Sie eine Weile zu, um zu sehen, ob Sie den Klang (oder die Gewissheit) bevorzugen.

---

### Schritt 2: Purist-Modus standardmäßig aktivieren

Wenn Sie entschieden haben, dass Sie den Klang mit aktiviertem Purist-Modus bevorzugen, machen Sie ihn nach jedem Neustart zum Standard.

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

[Service]
Type=oneshot
ExecStart=/bin/bash -c "sleep 60 && /usr/local/bin/purist-mode"

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

### Schritt 3: Einen Wrapper um den `menu` Befehl installieren
Viele Funktionen in AudioLinux erfordern Internetzugang. Damit alles wie erwartet funktioniert, fügen Sie einen Wrapper um den `menu` Befehl hinzu, der den Purist-Modus deaktiviert, während Sie das Menü verwenden, und ihn wieder aktiviert, wenn Sie zum Terminal zurückkehren.

```bash
if grep -q menu_wrapper ~/.bashrc; then
  :
else
  echo ""
  echo "Add a wrapper around the menu command"
  cat <<'EOT' | tee -a ~/.bashrc

# Custom wrapper for the AudioLinux menu to manage Purist Mode
menu_wrapper() {
  local was_active=false
  # Check the initial state of Purist Mode by looking for the backup file.
  if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
    was_active=true
  fi

  # If Purist Mode was active, temporarily revert it for the menu.
  if [ "$was_active" = true ]; then
    echo "Checking credentials to manage Purist Mode..."
    sudo -v

    echo "Temporarily disabling Purist Mode to run menu..."
    purist-mode --revert > /dev/null 2>&1 # Revert quietly
  fi

  # Call the original menu command
  /usr/bin/menu

  # If Purist Mode was active before, re-enable it now.
  if [ "$was_active" = true ]; then
    echo "Re-activating Purist Mode..."
    purist-mode > /dev/null 2>&1 # Activate quietly
    echo "Purist Mode is active again."
  fi
}

# Alias the 'menu' command to our new wrapper function
alias menu='menu_wrapper'
# Aliases to manage the automatic Purist Mode service
alias purist-mode-auto-enable='echo "Enabling Purist Mode on boot..."; purist-mode; sudo systemctl enable purist-mode-auto.service'
alias purist-mode-auto-disable='echo "Disabling Purist Mode on boot..."; purist-mode --revert; sudo systemctl disable --now purist-mode-auto.service'
EOT
fi

source ~/.bashrc
```

---

### Die Purist-Modus-Zustände verstehen

Das Purist-Modus-System ist flexibel gestaltet und erlaubt es Ihnen, es manuell zu steuern oder automatisch nach dem Systemstart aktivieren zu lassen. Es arbeitet in zwei Hauptzuständen:

  * **Deaktiviert (Standard-Modus):**
    Dies ist der normale, voll funktionsfähige Zustand des Diretta-Targets. Das Netzwerk-Gateway ist aktiv, alle Dienste (`chronyd`, `argononed`) laufen, und das Gerät arbeitet ohne Einschränkungen.

  * **Aktiv (Purist-Modus):**
    Dies ist der optimierte Zustand für kritisches Hören. Das Netzwerk-Gateway wird entfernt, um Internetverkehr zu verhindern, und nicht wesentliche Hintergrunddienste (einschließlich des Argon ONE Lüfters) werden gestoppt, um alle potenziellen Systemstörungen zu minimieren.

Diese Zustände werden auf zwei Arten verwaltet: **automatisch** beim Booten und **manuell** über die Kommandozeile.

#### Automatische Steuerung (Beim Booten)

Der Bootvorgang ist sicher und vorhersehbar gestaltet, mit einer optionalen automatischen Umschaltung in den Purist-Modus.

1.  **Zwingender Revert beim Booten:** Unabhängig vom Zustand beim Herunterfahren bootet das Diretta-Target **immer** zuerst in den **Standard-Modus**. Dies ist eine wichtige Funktion, die sicherstellt, dass wesentliche Dienste wie die Netzwerkzeitsynchronisation korrekt ausgeführt werden können.

2.  **Optionale Auto-Aktivierung:** Wenn Sie die automatische Funktion aktiviert haben, wartet das System 60 Sekunden nach dem Booten und schaltet dann automatisch in den **Purist-Modus**. Dies bietet eine "Set it and forget it"-Erfahrung für Benutzer, die immer im optimierten Zustand hören möchten.

#### Manuelle Steuerung (Interaktive Nutzung)

Sie haben jederzeit volle interaktive Kontrolle über das System.

  * Um den Purist-Modus für eine Hörsitzung **manuell zu aktivieren**, loggen Sie sich auf dem Diretta-Target-Computer ein und führen Sie aus:

    ```bash
    purist-mode
    ```

  * Um den Purist-Modus **manuell zu deaktivieren** und zum Standardbetrieb zurückzukehren, führen Sie aus:

    ```bash
    purist-mode --revert
    ```

  * Um das **automatische Bootverhalten** zu steuern, verwenden Sie die Komfort-Aliase auf dem Diretta-Target:

    ```bash
    # Dies aktiviert die 60-Sekunden-Auto-Aktivierung beim nächsten Boot
    purist-mode-auto-enable

    # Dies deaktiviert die Auto-Aktivierung beim nächsten Boot
    purist-mode-auto-disable
    ```

---

## 13. Anhang 4: Optionale Web-Oberfläche zur Systemsteuerung

Dieser Anhang bietet Anweisungen zur Installation einer einfachen webbasierten Anwendung auf dem Diretta-Host. Diese Anwendung bietet eine einfach zu bedienende Oberfläche, die von einem Telefon oder Tablet aus zugänglich ist, um Schlüsselfunktionen Ihres Diretta-Systems zu verwalten, einschließlich Purist-Modus auf dem Target und Roon IR Remote-Integrationseinstellungen auf dem Host.

> **KRITISCHE WARNUNG: Führen Sie diese Schritte sorgfältig aus.**
> Diese Einrichtung beinhaltet das Erstellen eines neuen Benutzers und das Ändern von Sicherheitseinstellungen. Folgen Sie den Anweisungen genau, um sicherzustellen, dass das System sicher und funktionsfähig bleibt.

Die Einrichtung ist in zwei Teile gegliedert: Zuerst konfigurieren wir das **Diretta-Target**, um Befehle sicher zu akzeptieren, und zweitens installieren wir die Webanwendung auf dem **Diretta-Host**. Passen Sie jedoch auf, da wir häufig zwischen den Hosts wechseln.

---

### **Teil 1: Diretta-Target Konfiguration**

Auf dem **Diretta-Target** erstellen wir einen neuen Benutzer mit sehr eingeschränkten Rechten. Dieser Benutzer darf nur die spezifischen Befehle ausführen, die für die Verwaltung des Purist-Modus erforderlich sind.

1.  **SSH zum Diretta-Target:**
    ```bash
    ssh diretta-target
    ```

2.  **Einen neuen Benutzer für die App erstellen:**
    Dieser Befehl erstellt einen neuen Benutzer namens `purist-app` und dessen Home-Verzeichnis. Eine gültige Shell ist erforderlich, damit nicht-interaktive SSH-Befehle funktionieren.
    ```bash
    sudo useradd --create-home --shell /bin/bash purist-app
    ```

3.  **Sichere Befehls-Skripte erstellen:**
    Wir erstellen vier kleine, dedizierte Skripte, die die *einzigen* Aktionen sind, die die Web-App ausführen darf. Dies ist ein kritischer Sicherheitsschritt.
    ```bash
    # Skript zum Abrufen des aktuellen Status, einschließlich Lizenzstatus
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-status
    #!/bin/bash
    IS_ACTIVE="false"
    IS_AUTO_ENABLED="false"
    LICENSE_LIMITED="false"

    # Check for Purist Mode
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
      IS_ACTIVE="true"
    fi

    # Check if auto-start is enabled
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      IS_AUTO_ENABLED="true"
    fi

    # Check for the presence of the Diretta License Key File
    if ! ls /opt/diretta-alsa-target/ | grep -qv '^diretta'; then
      LICENSE_LIMITED="true"
    fi

    # Output all status flags as a single JSON object
    echo "{\"purist_mode_active\": $IS_ACTIVE, \"auto_start_enabled\": $IS_AUTO_ENABLED, \"license_needs_activation\": $LICENSE_LIMITED}"
    EOT

    # Skript zum Umschalten des Purist-Modus
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-mode
    #!/bin/bash
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
      /usr/local/bin/purist-mode --revert
    else
      /usr/local/bin/purist-mode
    fi
    EOT

    # Skript zum Umschalten des Auto-Start-Dienstes
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-auto
    #!/bin/bash
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      systemctl disable --now purist-mode-auto.service
    else
      systemctl enable purist-mode-auto.service
    fi
    EOT

    # Skript zum Neustarten des Diretta-Dienstes erstellen
    cat <<'EOT' | sudo tee /usr/local/bin/pm-restart-target
    #!/bin/bash
    # Restarts the Diretta ALSA Target service.
    # This script is intended to be called via sudo by the purist-app user.
    /usr/bin/systemctl restart diretta_alsa_target.service
    EOT

    # Skript zum Abrufen der Diretta-Lizenz-URL erstellen
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-license-url
    #!/bin/bash

    # This script's only job is to read the cache file created at boot.
    readonly CACHE_FILE="/tmp/diretta_license_url.cache"

    if [ -s "$CACHE_FILE" ]; then
        # If the cache exists and has content, display it.
        cat "$CACHE_FILE"
    else
        # If not, print a helpful error to stderr and exit.
        echo "Error: License cache not found or is empty." >&2
        exit 1
    fi
    EOT

    # Die neuen Skripte ausführbar machen
    sudo chmod -v +x /usr/local/bin/pm-*
    ```

4.  **Sudo-Berechtigungen gewähren:**
    Dieser Schritt erlaubt dem `purist-app` Benutzer, unsere vier neuen Skripte mit Root-Rechten auszuführen, ohne ein interaktives Terminal zu benötigen.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/purist-app
    # Tell sudo not to require a TTY for the purist-app user
    Defaults:purist-app !requiretty

    # Allow the purist-app user to run the specific control scripts without a password
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-status
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-mode
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-auto
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-restart-target
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-license-url
    EOT
    ```

5.  **Die Diretta-Lizenz-Cache-Datei beim Booten füllen**
    Das Abrufen der Diretta-Lizenz-URL erfordert eine Internetverbindung. Wenn wir den Purist-Modus standardmäßig aktiviert haben, wird das Target nie in der Lage sein, die URL abzurufen. Beim Booten haben wir jedoch den Purist-Modus für 60 Sekunden deaktiviert, um die Uhr zu stellen und auf eine Diretta-Lizenzaktivierung zu prüfen. Wir können dieses Zeitfenster nutzen, um auch die URL abzurufen.
    ```bash
    # Skript herunterladen, korrekte Rechte setzen und im Systempfad platzieren
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh
    sudo install -m 0755 create-diretta-cache.sh /usr/local/bin/
    rm create-diretta-cache.sh

    # Die Systemd Drop-in Datei erstellen
    sudo mkdir -p /etc/systemd/system/purist-mode-revert-on-boot.service.d
    cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-revert-on-boot.service.d/create-cache.conf
    [Service]
    ExecStartPost=/usr/local/bin/create-diretta-cache.sh
    EOT

    # Skript einmal manuell ausführen
    sudo /usr/local/bin/create-diretta-cache.sh
    ```

---

### **Teil 2: Diretta-Host Konfiguration**

Nun führen wir auf dem **Diretta-Host** alle Schritte zur Installation und Konfiguration der Webanwendung durch. Sie sollten für diesen gesamten Abschnitt als `audiolinux` Benutzer eingeloggt sein.

1.  **SSH zum Diretta-Host:**
    ```bash
    ssh diretta-host
    ```

2.  **Einen dedizierten SSH-Schlüssel generieren:**
    Dies erstellt ein neues SSH-Schlüsselpaar speziell für die Web-App. Es wird keine Passphrase haben.
    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/purist_app_key -N "" -C "purist-app-key"
    ```

3.  **Den Schlüssel zum Target kopieren:**
    Dieser Schritt kopiert den öffentlichen Schlüssel sicher auf das Target.
    ```bash
    echo "--- Authorizing the new SSH key on the Diretta Target ---"

    # Step A: Copy the public key to the Target's home directory
    echo "--> Copying public key to the Target..."
    scp -o StrictHostKeyChecking=accept-new ~/.ssh/purist_app_key.pub diretta-target:
    ```

4.  **Den Schlüssel auf dem Target autorisieren:**
    ```bash
    ssh diretta-target

    ```

    Sobald Sie auf dem Target eingeloggt sind, führen Sie dieses Skript aus, um den Schlüssel für den 'purist-app' Benutzer einzurichten
    ```bash
    echo "--> Running setup script on the Target..."
    set -e
    # Read the public key from the file we just copied
    PUB_KEY=$(cat purist_app_key.pub)

    # Ensure the .ssh directory exists and has correct permissions
    sudo mkdir -p /home/purist-app/.ssh
    sudo chmod 0700 /home/purist-app/.ssh

    # Create the authorized_keys file with the required security restrictions
    echo "command=\"sudo \$SSH_ORIGINAL_COMMAND\",from=\"172.20.0.1\",no-port-forwarding,no-x11-forwarding,no-agent-forwarding,no-pty ${PUB_KEY}" | sudo tee /home/purist-app/.ssh/authorized_keys > /dev/null

    # Set final ownership and permissions
    sudo chown -R purist-app:purist-app /home/purist-app/.ssh
    sudo chmod 0600 /home/purist-app/.ssh/authorized_keys

    # Clean up the copied public key file
    rm purist_app_key.pub

    echo "✅ SSH key has been successfully authorized on the Target."
    ```

5.  **Manuelles Testen der Remote-Befehle (Empfohlen):**
    Bevor Sie die Web-App starten, testen Sie jeden der Remote-Befehle vom Terminal des **Diretta-Hosts**, um zu bestätigen, dass das Backend funktioniert.
    ```bash
    # Status-Befehl testen (sollte einen JSON-String zurückgeben)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-status'

    # Purist-Modus Umschaltung testen (zweimal ausführen, um an- und dann auszuschalten)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-toggle-mode'

    # Auto-Start beim Booten testen (zweimal ausführen, um zu aktivieren, dann zu deaktivieren)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-toggle-auto'

    # Abrufen der Diretta-Target-Lizenz-URL testen
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-license-url'

    # Neustart des Diretta-Target-Dienstes testen
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-restart-target'
    ```

6.  **Python via pyenv installieren** auf dem **Diretta-Host** (Sie können diesen Schritt überspringen, wenn Sie dies bereits getan haben, um die IR-Fernbedienung zum Laufen zu bringen)
    Installieren Sie `pyenv` und die neueste stabile Version von Python.
    ```bash
    # Build-Abhängigkeiten installieren
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

    # pyenv nur installieren, wenn es noch nicht installiert ist
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

    # Datei einlesen, um pyenv in der aktuellen Shell verfügbar zu machen
    . ~/.bashrc

    # Die neueste Python-Version installieren und setzen, falls noch nicht geschehen
    PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
    if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
      echo "--- Installing Python ${PYVER}. This will take several minutes... ---"
      pyenv install $PYVER
    else
      echo "--- Python ${PYVER} is already installed. Skipping installation. ---"
    fi

    # Globale Python-Version setzen
    pyenv global $PYVER
    ```

    **Hinweis:** Es ist normal, dass der Teil `Installing Python-3.14.2...` etwa 10 Minuten dauert, da Python aus dem Quellcode kompiliert wird. Geben Sie nicht auf! Fühlen Sie sich frei, sich bei schöner Musik über Ihre neue Diretta-Zone in Roon zu entspannen, während Sie warten. Sie sollte verfügbar sein, während Python auf dem Host installiert wird.

7.  **Avahi und Python-Abhängigkeiten auf dem Diretta-Host installieren:**

    **Hinweis:** OPTIONAL - Wenn Sie mehr als einen Diretta-Host in Ihrem Netzwerk haben, stellen Sie bitte sicher, dass sie eindeutige Namen haben. Sie können einen Befehl wie den folgenden verwenden, um diesen umzubenennen, bevor Sie fortfahren:

    ```bash
    # Optional den Diretta-Host umbenennen, wenn dies Ihr zweiter Aufbau im selben Netzwerk ist
    sudo hostnamectl set-hostname diretta-host2
    ```

    Dieser Schritt läuft auf dem **Diretta-Host**. Er installiert den Avahi-Daemon und verwendet eine `requirements.txt`-Datei, um Flask in eine dedizierte virtuelle Umgebung zu installieren.
    ```bash
    # Avahi für .local Namensauflösung installieren
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm avahi

    # Dynamisch den Namen der USB-Ethernet-Schnittstelle finden (z.B. enp... oder enu1...)
    USB_INTERFACE=$(ip -o link show | awk -F': ' '/en[pu]/{print $2}')

    # Konfigurations-Override für Avahi erstellen, um es auf die USB-Schnittstelle zu isolieren
    echo "--- Configuring Avahi to use interface: $USB_INTERFACE ---"
    sudo mkdir -p /etc/avahi/avahi-daemon.conf.d
    cat <<EOT | sudo tee /etc/avahi/avahi-daemon.conf.d/interface-scoping.conf
    [server]
    allow-interfaces=$USB_INTERFACE
    deny-interfaces=end0
    EOT

    # Avahi-Daemon aktivieren und starten
    sudo systemctl enable --now avahi-daemon.service

    # Anwendungsverzeichnis und Requirements-Datei erstellen
    mkdir -p ~/purist-mode-webui
    echo "Flask" > ~/purist-mode-webui/requirements.txt

    # Virtuelle Umgebung erstellen und Abhängigkeiten installieren
    echo "--- Setting up Python environment for the Web UI ---"
    # Virtuelle Umgebung nur erstellen, wenn sie noch nicht existiert
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

9.  **Port-Binding-Fähigkeit gewähren**
    Wir müssen der Python-Ausführungsdatei die Erlaubnis geben, an Port 80 auf dem Diretta-Host zu binden, damit unsere Web-App starten kann.
    ```bash
    # Paket installieren, das den 'setcap' Befehl bereitstellt
    sudo pacman -S --noconfirm --needed libcap

    # Den echten Pfad zur Python-Ausführungsdatei finden und alle symbolischen Links auflösen
    PYTHON_EXEC=$(readlink -f /home/audiolinux/.pyenv/versions/purist-webui/bin/python)

    # Die Port-Binding-Fähigkeit direkt der finalen Python-Ausführungsdatei gewähren
    echo "Applying capability to the real file: ${PYTHON_EXEC}"
    sudo setcap 'cap_net_bind_service=+ep' "$PYTHON_EXEC"
    ```

10. **Sudo-Berechtigungen auf dem Host gewähren:**
    Dieser Schritt ist kritisch, damit die Webanwendung die notwendigen Roon-bezogenen Dienste ohne Passwort neu starten kann.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/webui-restarts
    # Allow the webui (running as audiolinux) to restart required services
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roon-ir-remote.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roonbridge.service
    EOT
    sudo chmod 0440 /etc/sudoers.d/webui-restarts
    ```

11. **Die Flask-App interaktiv testen:**
    Führen Sie die App nun von der Kommandozeile auf dem **Diretta-Host** aus, um sicherzustellen, dass sie korrekt startet.
    ```bash
    cd ~/purist-mode-webui
    pyenv activate purist-webui
    python app.py
    ```
    Sie sollten eine Ausgabe sehen, die anzeigt, dass der Flask-Server auf Port **8080** gestartet wurde. Greifen Sie von einem anderen Gerät auf [http://diretta-host.local:8080](http://diretta-host.local:8080) zu. Wenn es funktioniert, kehren Sie zum SSH-Terminal zurück und drücken Sie `Ctrl+C`, um den Server zu stoppen.

12. **Den `systemd` Service erstellen:**
    Dieser Dienst führt die Web-App automatisch auf dem **Diretta-Host** aus und verwendet dabei die korrekte Python-Ausführungsdatei aus unserer `pyenv` virtuellen Umgebung.
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
    sudo systemctl enable --now purist-webui.service
    ```

14. **Die Logs kurz beobachten:**
    ```bash
    journalctl -b -u purist-webui.service -f
    ```

15. **Die Web-Oberfläche mit der finalen URL testen:**
    Öffnen Sie einen Browser unter [http://diretta-host.local](http://diretta-host.local) und beobachten Sie die Logs auf Fehler.

Tippen Sie `CTRL-C`, sobald Sie zufrieden sind, dass alles wie erwartet funktioniert.

---

### **Zugriff auf die Web-Oberfläche**

Sie sind fertig! Öffnen Sie einen Webbrowser auf Ihrem Telefon, Tablet oder Computer, der mit demselben Netzwerk wie der Diretta-Host verbunden ist. Navigieren Sie zur Hauptseite:

[http://diretta-host.local](http://diretta-host.local)

---
> **Ein Hinweis zu Browser-Sicherheitswarnungen**
> Wenn Sie http://diretta-host.local zum ersten Mal besuchen, zeigt Ihr Browser wahrscheinlich eine Sicherheitswarnung an, dass die Verbindung nicht sicher ist. Dies ist erwartet und kann sicher umgangen werden. Die Warnung erscheint, weil die Verbindung Standard-`HTTP` anstelle von verschlüsseltem `HTTPS` verwendet, eine bewusste Entscheidung, um den Rechenaufwand auf dem Audiogerät zu minimieren. Da die App nur in Ihrem privaten Heimnetzwerk läuft und keine sensiblen Daten verarbeitet, können Sie getrost auf "Weiter zur Seite" klicken.
---

Von der Hauptseite aus führt Sie eine Navigationsleiste oben zu den verschiedenen Bedienfeldern:

* **Home:** Die Hauptseite mit Links zu den verschiedenen Anwendungen.

* **Purist Mode App:** Diese Seite enthält die Steuerelemente zum Umschalten des Purist-Modus und seines Auto-Start-Verhaltens auf dem Diretta-Target. Sie aktualisiert sich automatisch alle 30 Sekunden, um den aktuellen Status anzuzeigen. Sie enthält auch die Schaltfläche "Dienste neu starten" zur Verwendung nach einer Diretta-Lizenzaktivierung.

* **IR Remote App:** Wenn Sie die Einrichtung der IR-Fernbedienung (Anhang 2) abgeschlossen haben, erscheint dieser Link. Diese Seite bietet ein einfaches Formular zum Anzeigen und Aktualisieren des Roon-Zonennamens, den Ihre Fernbedienung steuern soll. Diese Seite aktualisiert sich nicht automatisch, sodass Sie sich so viel Zeit wie nötig nehmen können, um Ihre Änderungen vorzunehmen.

> ---
> ### ✅ Checkpoint: Überprüfen Sie Ihre Web-Oberflächen-Einrichtung
>
> Die Purist-Modus Web-Oberfläche sollte nun betriebsbereit sein. Um alle Komponenten dieser komplexen Funktion zu überprüfen, fahren Sie mit **[Anhang 5](#14-anhang-5-system-gesundheitschecks)** fort und führen Sie den universellen **System Health Check** sowohl auf dem Host als auch auf dem Target aus.
>
> ---

## 14. Anhang 5: System-Gesundheitschecks

Nach Abschluss der Hauptabschnitte dieses Leitfadens ist es eine gute Idee, einen schnellen Qualitätssicherungs-Check (QS) durchzuführen, um zu verifizieren, dass alles korrekt konfiguriert ist.

Wir haben ein intelligentes Skript erstellt, das automatisch erkennt, ob Sie es auf dem **Diretta-Host** oder dem **Diretta-Target** ausführen, und den entsprechenden Satz von Überprüfungen durchführt.

### **Wie man den Check ausführt**

Führen Sie auf dem Host oder dem Target den folgenden Einzelbefehl aus. Er lädt das QS-Skript herunter, führt es aus und liefert einen detaillierten Bericht über den Status Ihres Systems.

```bash
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh | sudo bash
```

---

## 15. Anhang 6: Erweitertes Echtzeit-Leistungstuning

Die folgenden Schritte sind optional, werden aber für Benutzer empfohlen, die die absolut maximale Leistung aus ihrem Diretta-Setup herausholen möchten. Die Strategie, basierend auf Ratschlägen von AudioLinux-Autor Piero, besteht darin, die stabilste und elektrisch ruhigste Umgebung wie möglich auf beiden Geräten (Host und Target) zu schaffen.

Dies wird durch **CPU-Isolierung** erreicht, um spezifische Prozessorkerne für Audioaufgaben zu reservieren und sie vom Betriebssystem abzuschirmen, sowie durch sorgfältiges Abstimmen der **Echtzeit-Prioritäten**, um sicherzustellen, dass der Audiodatenpfad niemals unterbrochen wird.

> **Hinweis:** Dies ist ein fortgeschrittener Tuning-Prozess. Bitte stellen Sie sicher, dass Ihr Diretta-Kernsystem voll funktionsfähig ist, indem Sie die Abschnitte 1-9 des Hauptleitfadens abschließen, bevor Sie fortfahren. Eine angemessene Kühlung für beide Raspberry Pi-Geräte ist unerlässlich.

---

### **Teil 1: Optimierung des Diretta-Targets**

Das Ziel für das Target ist es, es zu einem reinen Audio-Endpunkt mit niedriger Latenz zu machen. Wir werden die Diretta-Anwendung auf einem einzelnen, dedizierten CPU-Kern isolieren und ihr eine hohe, aber nicht übermäßige Echtzeit-Priorität geben.

#### **Schritt 6.1: Einen CPU-Kern für die Audio-Anwendung isolieren**

Dieser Schritt widmet einen CPU-Kern exklusiv der Diretta-Target-Anwendung.

1.  SSH zum Diretta-Target:
    ```bash
    ssh diretta-target
    ```
2.  Öffnen Sie das AudioLinux-Menüsystem:
    ```bash
    menu
    ```
3.  Navigieren Sie zum Menü **ISOLATED CPU CORES configuration** (unter **SYSTEM menu**).

4.  Deaktivieren Sie alle vorherigen Einstellungen wie unten gezeigt:
    ```text
    Please chose your option:
    1) Configure and enable
    2) Disable
    3) Exit
    ?
    2

    ISOLATED CORES has been reset

    IRQ balancer was disabled
    It can be enabled in Expert menu

    PRESS RETURN TO EXIT
    ```

5.  Navigieren Sie zurück zum Menü **ISOLATED CPU CORES configuration** (unter **SYSTEM menu**). Folgen Sie den Aufforderungen genau wie unten gezeigt, um **Kerne 2 und 3** zu isolieren und die Diretta-Anwendung diesen zuzuweisen.
    ```text
    Please chose your option:
    1) Configure and enable
    2) Disable
    3) Exit
    ?
    1

    How many groups do you want to create? (1 or more)
    ?1
    Please type the cores of the group 1:
    ?2,3

    Type the application(s) that should be confined to group 1...:
    ?diretta_app_target

    Please type the Address (iSerial) number of your card(s)...:
    (Press ENTER if you don't want to assign IRQ to this group):
    ?end0
    ```
6.  Nachdem der Vorgang abgeschlossen ist, drücken Sie **ENTER**, um zum Systemmenü zurückzukehren. **Starten Sie noch nicht neu.**

> **Ein Hinweis zur automatischen IRQ-Affinität:** Sie werden bemerken, dass das Skript meldet, dass es auch die `end0` Netzwerk-IRQs auf denselben Kern isoliert hat. Dies ist kein Fehler, sondern eine intelligente Optimierung. Das Skript bindet die Netzwerk-Interrupts automatisch an denselben Kern wie die Anwendung, die das Netzwerk nutzt, wodurch der effizienteste Datenpfad geschaffen wird.

---

#### **Schritt 6.2: Echtzeit-Priorität setzen**

Als Nächstes geben wir der Diretta-Anwendung eine "nicht zu hohe" Priorität, um sicherzustellen, dass sie reibungslos läuft, ohne die kritischeren USB-Audio-Interrupts zu stören.

1.  Ebenfalls im **SYSTEM menu**, navigieren Sie zum Menü **REALTIME PRIORITY configuration**.
2.  Wählen Sie **Option 3) Configure IRQ priority**.
3.  Folgen Sie den Aufforderungen, um sicherzustellen, dass es eine Standard-IRQ-Priorität gibt.
    ```text
    Do you want to set the IRQ priority for each device? (1/2)
    1 - IRQ priority (advanced)
    2 - IRQ priority (simple)
    3 - Exit
    ?2

    -> Your previous configuration has been saved to /etc/rtpriority/rtirqs.conf.bak
    Please type xhci (default) or snd for internal cards
    ?xhci

    The max. available realtime priority is 98
    Suggested values are 95 (extreme) or 90 (default)
    Please enter your value:
    ?90

    Do you want to set the IRQ priority for each device? (1/2)
    1 - IRQ priority (advanced)
    2 - IRQ priority (simple)
    3 - Exit
    ?3
    ```
4.  Wählen Sie **Option 4) Configure APPLICATION priority**.
5.  Folgen Sie den Aufforderungen, um eine **manuelle** Priorität von **70** festzulegen.

    ```text
    ...
    Type Y if you want to edit it
    ?
    [PRESS ENTER]

    Here you will configure the max. priority given to audio applications...
    ?70

    Now you can configure your preferred method...
    ?manual
    ```
6.  Nach Bestätigung der Änderungen wählen Sie **5) Exit** und kehren zur Kommandozeile zurück.
7.  Starten Sie das Diretta-Target neu, damit alle Änderungen wirksam werden.
    ```bash
    sudo sync && sudo reboot
    ```

---

### **Teil 2: Optimierung des Diretta-Hosts**

Das Ziel für den Host ist es, Roon Bridge und dem Diretta-Dienst dedizierte Verarbeitungsressourcen zu geben, jedoch ohne hohe Echtzeit-Prioritäten zu verwenden. CPU-Isolierung ist hier ein mächtigeres Werkzeug, da sie verhindert, dass die Prozesse überhaupt unterbrochen werden.

#### **Schritt 6.3: CPU-Kerne für Audio-Anwendungen isolieren**

Dieser Schritt reserviert zwei CPU-Kerne für die Behandlung von sowohl Roon Bridge als auch dem Diretta-Host-Dienst.

1.  SSH zum Diretta-Host:
    ```bash
    ssh diretta-host
    ```
2.  Öffnen Sie das AudioLinux-Menüsystem:
    ```bash
    menu
    ```
3.  Navigieren Sie zum Menü **ISOLATED CPU CORES configuration** (unter **SYSTEM menu**).

4.  Deaktivieren Sie alle vorherigen Einstellungen wie unten gezeigt:
    ```text
    Please chose your option:
    1) Configure and enable
    2) Disable
    3) Exit
    ?
    2

    ISOLATED CORES has been reset

    IRQ balancer was disabled
    It can be enabled in Expert menu

    PRESS RETURN TO EXIT
    ```

5.  Navigieren Sie zurück zum Menü **ISOLATED CPU CORES configuration** (unter **SYSTEM menu**). Folgen Sie den Aufforderungen, um **Kerne 2 und 3** zu isolieren und die relevanten Anwendungen zuzuweisen.

    ```text
    Please chose your option:
    1) Configure and enable
    ...
    ?
    1

    How many groups do you want to create? (1 or more)
    ?1
    Please type the cores of the group 1:
    ?2,3

    Type the application(s) that should be confined to group 1...:
    ?RoonBridge syncAlsa

    Please type the Address (iSerial) number of your card(s)...:
    (Press ENTER if you don't want to assign IRQ to this group):
    ?end0
    ```

6.  Nachdem der Vorgang abgeschlossen ist, drücken Sie **ENTER**, um zum Systemmenü zurückzukehren. **Starten Sie noch nicht neu.**

---

#### **Schritt 6.4: Anwendungs-Echtzeit-Priorität deaktivieren**

Da unsere Audioanwendungen auf dedizierten Kernen laufen, müssen sie nicht mehr um CPU-Zeit konkurrieren. Das Erzwingen einer hohen Echtzeit-Priorität ist nun unnötig und kann kontraproduktiv sein. Wir werden den Dienst auf dem Host vollständig deaktivieren.

1.  Ebenfalls im **SYSTEM menu**, navigieren Sie zum Menü **REALTIME PRIORITY configuration**.
2.  Wählen Sie **Option 2) Enable/disable APPLICATION service (rtapp)**. Dies deaktiviert den Dienst sofort.
3.  Wählen Sie **5) Exit** und kehren Sie zur Kommandozeile zurück.
4.  Starten Sie den Diretta-Host neu.
    ```bash
    sudo sync && sudo reboot
    ```

---

#### **Schritt 6.5: Diretta `CycleTime` reduzieren**

Mit den installierten Echtzeit-Kernel-Optimierungen kann der Diretta-Host nun ein aggressiveres Paketintervall bewältigen, was zu einer verbesserten Klangqualität führen kann. Dieser letzte Schritt reduziert den Parameter `CycleTime` von 800 auf 514 Mikrosekunden. Dieser kleinere Zeitabstand zwischen den Paketen stellt sicher, dass alle Inhalte bis zu DSD256 und DXD (32-Bit, 352,8 kHz) nur ein Paket pro Zyklus benötigen.

1.  SSH zum **Diretta-Host**, falls Sie nicht mehr eingeloggt sind.
2.  Führen Sie den folgenden Befehl aus, um die optimierte Einstellung anzuwenden:
    ```bash
    cat <<'EOT' | sudo tee /opt/diretta-alsa/setting.inf
    [global]
    Interface=end0
    TargetProfileLimitTime=0
    ThredMode=1
    InfoCycle=100000
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
    unInitMemDet=disable
    CpuSend=
    CpuOther=
    LatencyBuffer=0
    disConnectDelay=enable
    singleMode=
    EOT
    ```
3.  Starten Sie den Diretta-Dienst neu, damit die Änderung wirksam wird:
    ```bash
    sudo systemctl restart diretta_alsa.service
    ```

---

> ---
> ### ✅ Checkpoint: Überprüfen Sie Ihr Echtzeit-Tuning
>
> Ihr erweitertes Echtzeit-Tuning sollte nun abgeschlossen sein. Um alle Komponenten dieser neuen Konfiguration zu überprüfen, kehren Sie bitte zu **[Anhang 5](#14-anhang-5-system-gesundheitschecks)** zurück und führen Sie den universellen **System Health Check** sowohl auf dem Host als auch auf dem Target aus.
>
> ---

## 16. Anhang 7: CPU-Optimierung mit ereignisgesteuerten Hooks

Dieser Anhang bietet eine fortgeschrittene Optimierung, um System-Jitter und unnötige CPU-Aktivität weiter zu reduzieren.

Die Standardkonfiguration von AudioLinux enthält Hintergrund-"Timer" (z.B. `isolated_app.timer`, `rtapp.timer`), die einmal pro Minute Tuning-Skripte ausführen. Obwohl effektiv, verursachen diese Timer periodische CPU-Spitzen, was unserem Ziel eines ruhigen, stabilen Systems widerspricht.

Dieser Leitfaden ersetzt dieses "periodische" Verhalten durch ein "ereignisgesteuertes". Wir werden **die Timer deaktivieren** und stattdessen `systemd` Drop-in-Dateien verwenden, um diese Tuning-Skripte **nur einmal** auszuführen, wenn die Haupt-Audio-Dienste starten. Dieser "Einmal einrichten und vergessen"-Ansatz eliminiert die einminütigen CPU-Spitzen vollständig.

---

### **Teil 1: Optimierung des Diretta-Targets**

Auf dem Target deaktivieren wir sowohl `isolated_app.timer` als auch `rtapp.timer` und hängen ihre Skripte in den `diretta_alsa_target.service` ein.

1.  SSH zum Diretta-Target:

    ```bash
    ssh diretta-target
    ```

2.  **Die Timer stoppen und deaktivieren:**
    Dieser Befehl stoppt die Timer dauerhaft und entfernt ihre Autostart-Verknüpfungen.

    ```bash
    sudo systemctl stop isolated_app.timer rtapp.timer
    sudo systemctl disable isolated_app.timer rtapp.timer
    ```

3.  **Den Systemd Drop-in Hook erstellen:**
    Dieser Befehl erstellt eine neue Konfigurationsdatei, die `systemd` anweist, die beiden Skripte auszuführen, *nachdem* der Hauptdienst `diretta_alsa_target.service` gestartet ist.

    ```bash
    # Das Verzeichnis erstellen
    sudo mkdir -p /etc/systemd/system/diretta_alsa_target.service.d/

    # Die Drop-in Datei erstellen
    sudo bash -c 'cat <<EOF > /etc/systemd/system/diretta_alsa_target.service.d/10-local-hooks.conf
    [Service]
    ExecStartPost=sleep 1.5
    ExecStartPost=/opt/scripts/system/isolated_app.sh
    ExecStartPost=-/bin/bash /usr/bin/rtapp
    EOF'
    ```

    > **Hinweis zum Bindestrich (`-`):**
    > Das Präfix `-` vor dem Befehl `/bin/bash /usr/bin/rtapp` ist beabsichtigt. Das `rtapp`-Skript könnte in diesem Kontext fehlschlagen (mit einem Status ungleich Null beenden). Der Bindestrich weist `systemd` an, "Fehler zu ignorieren" für diesen spezifischen Befehl, sodass der Hauptdienst `diretta_alsa_target.service` weiterlaufen kann.

4.  **Systemd neu laden und den Dienst neu starten:**

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart diretta_alsa_target.service
    ```

5.  **Die Änderungen verifizieren:**

    ```bash
    systemctl status diretta_alsa_target.service
    ```

    In der Ausgabe sollten Sie sehen, dass der Dienst `Active: active (running)` ist. Sie sollten auch zwei `Process:`-Zeilen sehen, eine für `isolated_app.sh` (die `status=0/SUCCESS` zeigen sollte) und eine für `rtapp` (die wahrscheinlich `status=1/FAILURE` zeigt). Dies ist das korrekte und erwartete Ergebnis.

---

### **Teil 2: Optimierung des Diretta-Hosts**

Auf dem Host deaktivieren wir den `isolated_app.timer` und hängen sein Skript sowohl in den `roonbridge.service` als auch in den `diretta_alsa.service` ein. Dies stellt sicher, dass die Optimierungen angewendet werden, unabhängig davon, welcher Dienst zuerst startet.

1.  SSH zum Diretta-Host:

    ```bash
    ssh diretta-host
    ```

2.  **Den Timer stoppen und deaktivieren:**

    ```bash
    sudo systemctl stop isolated_app.timer
    sudo systemctl disable isolated_app.timer
    ```

3.  **Die Systemd Drop-in Hooks erstellen:**
    Wir müssen zwei separate Drop-in-Dateien erstellen, eine für jeden Dienst.

    **Für `roonbridge.service`:**

    ```bash
    # Das Verzeichnis erstellen
    sudo mkdir -p /etc/systemd/system/roonbridge.service.d/

    # Die Drop-in Datei erstellen
    sudo bash -c 'cat <<EOF > /etc/systemd/system/roonbridge.service.d/10-local-hooks.conf
    [Service]
    ExecStartPost=/opt/scripts/system/isolated_app.sh
    EOF'
    ```

    **Für `diretta_alsa.service`:**

    ```bash
    # Das Verzeichnis erstellen
    sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d/

    # Die Drop-in Datei erstellen
    sudo bash -c 'cat <<EOF > /etc/systemd/system/diretta_alsa.service.d/10-local-hooks.conf
    [Service]
    ExecStartPost=/opt/scripts/system/isolated_app.sh
    EOF'
    ```

4.  **Systemd neu laden und die Dienste neu starten:**

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart roonbridge.service
    sudo systemctl restart diretta_alsa.service
    ```

5.  **Die Änderungen verifizieren:**
    Überprüfen Sie den Status beider Dienste.

    ```bash
    systemctl status roonbridge.service
    systemctl status diretta_alsa.service
    ```

    Für beide Dienste sollten Sie `Active: active (running)` und eine `Process:`-Zeile für `isolated_app.sh` sehen, die `status=0/SUCCESS` zeigt.

>
>
> ---
>
> ### ✅ Checkpoint: Überprüfen Sie Ihre CPU-Optimierungen
>
> Ihr System ist nun optimiert, um seine Tuning-Skripte nur beim Booten auszuführen, wodurch periodische CPU-Spitzen eliminiert werden. Um zu verifizieren, dass diese neue Konfiguration korrekt mit dem Rest des Systems zusammenarbeitet, kehren Sie bitte zu **[Anhang 5](#14-anhang-5-system-gesundheitschecks)** zurück und führen Sie den universellen **System Health Check** sowohl auf dem Host als auch auf dem Target aus.
>
> ---

## 17. Anhang 8: Optionaler puristischer 100Mbps Netzwerk-Modus

**Ziel:** Reduzierung des elektrischen Rauschens und Verbesserung der Präzision des OS-Schedulers durch Begrenzung der dedizierten Netzwerkverbindung auf 100 Mbps und explizite Deaktivierung von Energy Efficient Ethernet (EEE).

Obwohl es kontraintuitiv erscheinen mag, kann die Reduzierung der Verbindungsgeschwindigkeit von 1 Gbps auf 100 Mbps auf der dedizierten Verbindung (`end0`) die Klangqualität verbessern. Die niedrigere Betriebsfrequenz von 100BASE-TX (31,25 MHz vs. 62,5 MHz) erzeugt weniger Funkstörungen (RFI). Darüber hinaus verhindert die Sicherstellung, dass EEE deaktiviert ist, dass die Verbindung in Schlafzustände übergeht, was potenzielle Latenzspitzen (Flapping) eliminiert und eine absolut solide Stabilität auf Raspberry Pi 5 Hardware gewährleistet.

> **Hinweis:** Sie sehen möglicherweise Warnungen über "buffer low" in den Target-Logs (`LatencyBuffer` fällt auf 1). Dies ist ein normales Verhalten aufgrund der erhöhten Serialisierungslatenz der langsameren Verbindung und verursacht keine hörbaren Aussetzer.

### Schritt 1: Den Host konfigurieren (Geschwindigkeitsbegrenzung)
Wir erstellen einen Dienst auf dem **Host**, der ihn zwingt, *nur* 100 Mbps Full Duplex anzubieten (Advertise). Das Target wird dies automatisch erkennen und sich anpassen.

**Den Begrenzungsdienst erstellen:** *(Nur auf dem Host durchführen)*
```bash
cat <<'EOT' | sudo tee /etc/systemd/system/limit-speed-100m.service
[Unit]
Description=Limit end0 advertisement to 100Mbps for Audio Purity
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecCondition=/usr/bin/ip link show end0
# Enable Auto-Neg but strictly limit advertisement to 100Mbps/Full
ExecStart=/usr/bin/ethtool -s end0 speed 100 duplex full autoneg on
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

echo "Enable and start the service:"
sudo systemctl daemon-reload
sudo systemctl enable --now limit-speed-100m.service
```

### Schritt 2: Host und Target konfigurieren (EEE deaktivieren)

Energy Efficient Ethernet (EEE) kann auf einigen Hardwarekombinationen zu Instabilität der Verbindung führen. Wir werden einen Dienst erstellen, um es explizit auf **beiden**, Host und Target, zu deaktivieren, um ein konsistentes Verhalten sicherzustellen.

**Den Deaktivierungsdienst erstellen:** *(Auf BEIDEN, Host und Target, durchführen)*

```bash
cat <<'EOT' | sudo tee /etc/systemd/system/disable-eee.service
[Unit]
Description=Disable EEE on end0 for Link Stability
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecCondition=/usr/bin/ip link show end0
# Explicitly disable EEE (ignore errors if unsupported by driver)
ExecStart=-/usr/bin/ethtool --set-eee end0 eee off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

echo "Enable and start the service:"
sudo systemctl daemon-reload
sudo systemctl enable --now disable-eee.service
```

### Schritt 3: Das Target markieren (Für QS)

Um sicherzustellen, dass das **Target QS Skript** weiß, dass diese spezifische Konfiguration validiert werden soll, erstellen Sie eine Marker-Datei auf dem Target:

```bash
sudo touch /etc/diretta-100m
```

***
> **Hinweis zur Wiedergabelatenz:**
> Sie bemerken möglicherweise eine leichte Erhöhung der Verzögerung zwischen dem Drücken von "Play" und dem Hören von Musik (bis zu ~1 Sekunde). Dies ist ein erwartetes Verhalten. Durch die Begrenzung der Verbindung auf 100 Mbps drosseln wir absichtlich den anfänglichen Datenstoß, um sicherzustellen, dass die Verbindung auf einer niedrigeren, ruhigeren Frequenz arbeitet. Das System tauscht sofortige Startzeiten gegen einen stabileren, rauschärmeren Dauerzustand während der Wiedergabe.
***

>
>
> ---
>
> ### ✅ Checkpoint: Überprüfen Sie die Netzwerkkonfiguration
>
> Ihre dedizierte Netzwerkverbindung ist nun für den "puristischen" 100Mbps-Betrieb konfiguriert. Um zu verifizieren, dass der Host-Dienst aktiv ist und das Target die Geschwindigkeit korrekt ausgehandelt hat (erkannt durch die Marker-Datei), kehren Sie bitte zu **[Anhang 5](#14-anhang-5-system-gesundheitschecks)** zurück und führen Sie den universellen **System Health Check** sowohl auf dem Host als auch auf dem Target aus.
>
> ---

## 18. Anhang 9: Optional: Jumbo-Frames-Optimierung
Dieser Abschnitt optimiert den Transport für hohe Bandbreiteneffizienz.

#### **Schritt 1:** Schnittstellen vorbereiten

Wir müssen die Netzwerkschnittstellen vorübergehend auf MTU 9000 zwingen, um die Kernel-Unterstützung zu verifizieren und den Verbindungstest vorzubereiten.

**Führen Sie dies zuerst auf dem Target aus, dann auf dem Host:**

```bash
sudo sh -c 'ip link set end0 down; sleep 2; ip link set end0 mtu 9000; ip link set end0 up'
end0_mtu=$(ip link show dev end0 | awk '/mtu/ {print $5}')
if [[ "9000" == "$end0_mtu" ]]; then
  echo "SUCCESS: Kernel supports Jumbo frames. Proceed to Step 2."
else
  echo "STOP: Your kernel does not appear to support Jumbo frames."
fi
```

*Wenn Sie "STOP" auf **entweder** dem Host oder dem Target sehen, fahren Sie nicht fort. Ihrem Kernel fehlt der erforderliche Patch.*

---

#### **Schritt 2:** Automatisierte Target-Konfiguration

SSH in das Target (`diretta-target`) und fügen Sie den folgenden Block ein.

```bash
# 1. Detect Link Limit (Full vs Baby)
echo "Testing Link Capability..."
if ping -c 1 -w 1 -M do -s 8972 host &>/dev/null; then
  NEW_MTU=9000
  echo "SUCCESS: Full Jumbo Frames (9000 MTU) supported."
elif ping -c 1 -w 1 -M do -s 2004 host &>/dev/null; then
  NEW_MTU=2032
  echo "SUCCESS: Baby Jumbo Frames (2032 MTU) supported."
else
  echo "FAIL: Link cannot support Jumbo Frames. Reverting to safe defaults."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Apply System Network Config
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
  sudo networkctl reload

  # 3. Apply Diretta Config
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

#### **Schritt 3:** Automatisierte Host-Konfiguration

SSH in den Host (`diretta-host`) und fügen Sie den folgenden Block ein. Er wird die Verbindung prüfen, die permanenten Netzwerkeinstellungen konfigurieren und Diretta aktualisieren.

```bash
# 1. Detect Link Limit (Full vs Baby)
echo "Testing Link Capability..."
# Give the link a moment to settle after the manual MTU change
sleep 2

if ping -c 1 -w 1 -M do -s 8972 target &>/dev/null; then
  NEW_MTU=9000
  echo "SUCCESS: Full Jumbo Frames (9000 MTU) supported."
elif ping -c 1 -w 1 -M do -s 2004 target &>/dev/null; then
  NEW_MTU=2032
  echo "SUCCESS: Baby Jumbo Frames (2032 MTU) supported."
else
  echo "FAIL: Link cannot support Jumbo Frames. Reverting to safe defaults."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Apply System Network Config
  echo "Configuring /etc/systemd/network/end0.network..."
  cat <<EOF | sudo tee /etc/systemd/network/end0.network
[Match]
Name=end0

[Link]
MTUBytes=$NEW_MTU

[Network]
Address=172.20.0.1/24
EOF
  sudo networkctl reload

  # 3. Apply Diretta Config
  echo "Configuring Diretta Host..."

  # Always enable FlexCycle for Jumbo Frames to ensure stability
  sudo sed -i 's/^FlexCycle=.*/FlexCycle=enable/' /opt/diretta-alsa/setting.inf

  # Conditional CycleTime Optimization
  if [ "$NEW_MTU" -eq 9000 ]; then
    echo "Optimization: Full Jumbo Frames detected. Relaxing CycleTime to 1000us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=1000/' /opt/diretta-alsa/setting.inf
  else
    echo "Optimization: Baby Jumbo Frames detected. Setting CycleTime to 700us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=700/' /opt/diretta-alsa/setting.inf
  fi

  sudo systemctl restart diretta_alsa
  echo "DONE: Host optimization complete."
}
```

#### **Schritt 4:** Neustart, um MTU-Änderungen zu übernehmen
Starten Sie zuerst das Target neu, dann den Host:
```bash
sudo sync && sudo reboot
```

>
>
> ---
>
> ### ✅ Checkpoint: Überprüfen Sie die Netzwerkkonfiguration
>
> Wenn Sie in der Lage waren, die Unterstützung für Jumbo-Frames für Ihre Konfiguration zu aktivieren, ist jetzt ein guter Zeitpunkt, um zu **[Anhang 5](#14-anhang-5-system-gesundheitschecks)** zurückzukehren und den universellen **System Health Check** sowohl auf dem Host als auch auf dem Target auszuführen.
>
> ---
