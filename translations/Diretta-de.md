
Aufbau einer dedizierten Diretta-Verbindung mit AudioLinux auf dem Raspberry PiDieser Leitfaden bietet eine
umfassende Schritt-für-Schritt-Anleitung zur Konfiguration von zwei Raspberry Pi-Geräten als dedizierten
Diretta Host und Diretta Target. Dieser Aufbau nutzt eine direkte Punkt-zu-Punkt-Ethernet-Verbindung
zwischen den beiden Geräten, um ein Höchstmaß an Netzwerkisolierung und Audioleistung zu gewährleisten.Der
Diretta Host wird mit Ihrem Hauptnetzwerk verbunden (um auf Ihren Musikserver zuzugreifen) und fungiert
gleichzeitig als Gateway für das Target. Das Diretta Target verbindet sich ausschließlich mit dem Host und
Ihrem USB-DAC oder DDC.Vorab-HinweisDiretta entwickelt sich ständig weiter ("Moving Target"). Ich freue mich
jedoch bestätigen zu können, dass die Version 146_7 (und neuere) sehr gut funktioniert, die CPU-Last auf dem
Target um ca. 45 % reduziert und hervorragend klingt.Hier einige Links für weitere Informationen
(Englisch):https://help.diretta.link/support/solutions/articles/73000661018-146https://help.diretta.link/support/solutions/articles/73000661171-dds-diretta-direct-streamEinführung
in die Referenz-Roon-ArchitekturWillkommen zum ultimativen Leitfaden für den Bau eines hochmodernen
Roon-Streaming-Endpoints. Obwohl AudioLinux auch andere Protokolle unterstützt, verwende ich für diesen
Aufbau Roon als Beispiel. Sie können über das Menüsystem des Diretta Hosts natürlich auch Unterstützung für
andere Protokolle wie HQPlayer, Audirvana, DLNA, AirPlay usw. installieren. Bevor wir in die
Schritt-für-Schritt-Anleitung eintauchen, ist es wichtig, das "Warum" hinter diesem Projekt zu verstehen.
Diese Einführung erklärt das Problem, das diese Architektur löst, warum sie vielen teuren kommerziellen
Alternativen grundlegend überlegen ist und wie dieses DIY-Projekt einen direkten und lohnenden Weg
darstellt, um die ultimative Klangqualität aus Ihrem Roon-System herauszuholen.Das Roon-Paradoxon: Ein
mächtiges Erlebnis mit einem klanglichen HakenRoon wird fast universell als das leistungsfähigste und
ansprechendste Musikverwaltungssystem gefeiert. Die umfangreichen Metadaten und die nahtlose
Benutzererfahrung suchen ihresgleichen. Diese funktionale Überlegenheit wird jedoch seit langem von einer
beständigen Kritik aus einem lautstarken Teil der audiophilen Gemeinschaft begleitet: Die Klangqualität von
Roon sei kompromittiert, oft beschrieben als "flach, stumpf und leblos" im Vergleich zu anderen
Playern.Dieser "Roon-Klang" ist kein Mythos und auch kein Fehler in Roons bit-perfekter Software. Er ist ein
potenzielles Symptom der leistungsstarken und ressourcenintensiven Natur von Roon. Der "schwergewichtige"
Roon Core benötigt erhebliche Rechenleistung, was wiederum elektrisches Rauschen (RFI/EMI) erzeugt. Wenn der
Computer, auf dem der Roon Core läuft, in unmittelbarer Nähe Ihres empfindlichen Digital-Analog-Wandlers
(DAC) steht, kann dieses Rauschen die analoge Ausgangsstufe verunreinigen, Details verdecken, die Klangbühne
schrumpfen lassen und der Musik ihre Lebendigkeit rauben.Mehr als nur "Pflaster" – eine fundamentale
LösungRoon Labs selbst plädiert für eine "Two-Box"-Architektur (Zwei-Geräte-Lösung), um dieses primäre
Problem zu lösen: Die Trennung des anspruchsvollen Roon Core von einem leichtgewichtigen Netzwerk-Endpoint
(auch Streaming-Transport genannt). Dies ist der richtige erste Schritt, da die schwere Rechenlast auf einen
entfernten Rechner ausgelagert wird und dessen Rauschen von Ihrem Audiosystem isoliert bleibt.Doch selbst in
diesem überlegenen zweistufigen Design bleibt ein subtileres Problem bestehen. Standard-Netzwerkprotokolle,
einschließlich Roons eigenem RAAT, übertragen Audiodaten in intermittierenden "Bursts" (Schüben). Dies
zwingt die CPU des Endpoints dazu, ihre Aktivität ständig hochzufahren, um diese Bursts zu verarbeiten, was
zu schnellen Schwankungen in der Stromaufnahme führt. Diese Schwankungen erzeugen ihr eigenes
niederfrequentes elektrisches Rauschen direkt am Endpoint – also genau an der Komponente, die Ihrem DAC am
nächsten ist.High-End-Audiohersteller versuchen, die Symptome dieses stoßweisen Datenverkehrs mit
verschiedenen "Pflaster"-Lösungen zu bekämpfen: massive Linearnetzteile, um die Stromspitzen besser zu
bewältigen, Ultra-Low-Power-CPUs, um die Intensität der Spitzen zu minimieren, und zusätzliche Filterstufen,
um das resultierende Rauschen zu bereinigen. Diese Strategien können zwar helfen, gehen aber nicht an die
Wurzel des Problems: die stoßweise Verarbeitung selbst.Dieser Leitfaden stellt eine elegantere und
dramatisch effektivere Lösung vor. Anstatt zu versuchen, das Rauschen nachträglich zu bereinigen, bauen wir
eine Architektur, die verhindert, dass das Rauschen überhaupt erst entsteht.Die Drei-Stufen-Architektur:
Roon + DirettaDieses Projekt entwickelt Roons empfohlenes Zwei-Boxen-Setup zu einem ultimativen dreistufigen
System weiter, das mehrere, sich ergänzende Isolationsebenen bietet.Stufe 1: Roon Core: Ihr leistungsstarker
Roon-Server läuft auf einer dedizierten Maschine, die weit entfernt von Ihrem Hörraum platziert ist. Er
übernimmt die Schwerstarbeit ("Heavy Lifting"), und sein elektrisches Rauschen bleibt von Ihrem Audiosystem
isoliert.Stufe 2: Diretta Host: Der erste Raspberry Pi in unserem Aufbau fungiert als Diretta Host. Er
verbindet sich mit Ihrem Hauptnetzwerk, empfängt den Audiostream vom Roon Core und bereitet ihn dann für die
Weiterleitung über ein spezialisiertes Protokoll vor.Stufe 3: Diretta Target: Der zweite Raspberry Pi, das
Diretta Target, verbindet sich ausschließlich über ein kurzes Ethernet-Kabel mit dem Host. Dadurch entsteht
eine galvanisch getrennte Punkt-zu-Punkt-Verbindung. Er empfängt die Audiodaten vom Host und leitet sie via
USB an Ihren DAC oder DDC weiter.Was Diretta und AudioLinux auf den Tisch bringenDie Überlegenheit dieses
Designs beruht auf zwei Schlüsselkomponenten der Software, die auf den Raspberry Pi-Geräten
läuft:AudioLinux: Dies ist ein speziell entwickeltes Echtzeit-Betriebssystem für audiophile Anwendungen. Im
Gegensatz zu einem Allzweck-Betriebssystem ist es darauf optimiert, Prozessorlatenzen und System-"Jitter" zu
minimieren und so eine stabile, rauscharme Grundlage für unseren Endpoint zu bieten.Diretta: Dieses
bahnbrechende Protokoll ist das "Geheimrezept", das das Wurzelproblem löst. Es erkennt, dass Schwankungen in
der Verarbeitungslast des Endpoints niederfrequentes elektrisches Rauschen erzeugen, das die internen Filter
eines DACs (definiert durch dessen PSRR – Power Supply Rejection Ratio) umgehen und die analoge Leistung
subtil verschlechtern kann. Um dies zu bekämpfen, verwendet Diretta sein "Host-Target"-Modell, bei dem der
Host Daten in einem kontinuierlichen, synchronisierten Strom kleiner, gleichmäßig verteilter Pakete sendet.
Dies "glättet" die Verarbeitungslast auf dem Target-Gerät, stabilisiert dessen Stromaufnahme und minimiert
die Erzeugung dieses schädlichen elektrischen Rauschens.Die Kombination aus der physischen galvanischen
Trennung durch die Punkt-zu-Punkt-Ethernet-Verbindung und der Eliminierung des Verarbeitungsrauschens durch
das Diretta-Protokoll schafft einen zutiefst sauberen Signalweg zu Ihrem DAC – einen, der Lösungen, die
viele tausend Euro kosten, in den Schatten stellen kann.Ein lohnender Weg zu klanglicher ExzellenzDieses
Projekt ist mehr als nur eine technische Übung; es ist ein lohnender Weg, sich mit dem Hobby
auseinanderzusetzen und direkte Kontrolle über die Leistung Ihres Systems zu übernehmen. Indem Sie diese
"Diretta Bridge" bauen, fügen Sie nicht einfach nur Komponenten zusammen; Sie implementieren eine
hochmoderne Architektur, die die Kernherausforderungen der digitalen Audiowiedergabe frontal angeht. Sie
werden ein tieferes Verständnis dafür gewinnen, was für die digitale Wiedergabe wirklich zählt, und mit
einem Maß an Klarheit, Detailreichtum und musikalischem Realismus von Roon belohnt werden, das Sie
vielleicht nicht für möglich gehalten hätten.Lassen Sie uns anfangen.Wenn Sie sich in den USA befinden,
rechnen Sie mit ca. 299 $ (plus Steuern und Versand), um den Basisaufbau zu vervollständigen (begrenzt auf
44,1 kHz Wiedergabe zu Evaluierungszwecken), plus weitere 100 €, um die Hi-Res-Wiedergabe freizuschalten
(Preise können sich ändern):Hardware (ca. 220 $)Einjähriges AudioLinux-Abonnement (79 $)Diretta Target
Lizenz (100 €)InhaltsverzeichnisVoraussetzungenVorbereitung des ImagesKernsystem-Konfiguration (Auf beiden
Geräten durchführen)System-Updates (Auf beiden Geräten durchführen)Punkt-zu-Punkt
Netzwerk-KonfigurationKomfortabler & Sicherer SSH-ZugriffAllgemeine SystemoptimierungenDiretta Software
Installation & KonfigurationAbschließende Schritte & Roon-IntegrationAnhang 1: Optionale Argon ONE
LüftersteuerungAnhang 2: Optionale IR-FernbedienungAnhang 3: Optionaler Purist-ModusAnhang 4: Optionale
Systemsteuerungs-WeboberflächeAnhang 5: System-Gesundheitscheck (Health Checks)Anhang 6: Fortgeschrittenes
Echtzeit-LeistungstuningAnhang 7: CPU-Optimierung mit ereignisgesteuerten HooksAnhang 8: Optionaler Purist
100Mbps Netzwerk-ModusAnhang 9: Optionale Jumbo Frames OptimierungWie Sie diesen Leitfaden nutzenDieser
Leitfaden ist so konzipiert, dass er so einfach wie möglich ist und die Notwendigkeit manueller
Dateibearbeitung minimiert. Der primäre Arbeitsablauf besteht darin, Befehlsblöcke aus diesem Dokument zu
kopieren und direkt in ein Terminalfenster einzufügen, das mit Ihren Raspberry Pi-Geräten verbunden ist.Hier
ist der Prozess, dem Sie für die meisten Schritte folgen werden:Verbinden via SSH: Sie verwenden einen
SSH-Client auf Ihrem Hauptcomputer, um sich entweder beim Diretta Host oder beim Diretta Target anzumelden,
wie im jeweiligen Abschnitt angewiesen.Befehl kopieren: Fahren Sie in Ihrem Webbrowser über die obere rechte
Ecke eines Befehlsblocks in diesem Leitfaden. Ein Kopier-Symbol erscheint. Klicken Sie darauf, um den
gesamten Block in Ihre Zwischenablage zu kopieren.Einfügen und Ausführen: Fügen Sie die kopierten Befehle in
das korrekte SSH-Terminalfenster ein und drücken Sie Enter.Die Skripte und Befehle wurden sorgfältig
geschrieben, um sicher zu sein und Fehler zu vermeiden, selbst wenn sie mehrmals ausgeführt werden. Wenn Sie
dieser "Copy-and-Paste"-Methode folgen, vermeiden Sie häufige Tippfehler und
Konfigurationsfehler.Video-AnleitungHier ist ein Link zu einer Reihe von kurzen Videos, die diesen Prozess
durchgehen (Englisch):Diretta Build Walkthrough with Two Raspberry Pi Computers1.
VoraussetzungenHardwareEine vollständige Materialliste finden Sie unten. Obwohl andere Teile verwendet
werden können, erhöht die Verwendung dieser spezifischen Komponenten die Chancen auf einen erfolgreichen
Aufbau.Kernkomponenten (von pishop.us oder ähnlichen Lieferanten):1 x Raspberry Pi 5/1GB (für das Diretta
Target)1 x Raspberry Pi 5/2GB (für den Diretta Host)2 x Flirc Raspberry Pi 5 Gehäuse2 x 64 GB A2 microSDXC
Karte2 x Raspberry Pi 45W USB-C Netzteil - WeißErforderliche Netzwerkkomponenten:1 x Plugable USB3 zu
Ethernet Adapter (für den Diretta Host)1 x Kurzes CAT6 Ethernet-Patchkabel (für die
Punkt-zu-Punkt-Verbindung)Optional, aber hilfreich zur Fehlersuche:1 x Micro-HDMI zu Standard HDMI (A/M), 2m
Kabel, Weiß1 x Offizielle Raspberry Pi Tastatur - Rot/WeißOptionale Upgrades:2 x Argon ONE V3 Raspberry Pi 5
Gehäuse (statt der Flirc Gehäuse)2 x 64 GB A2 microSDXC Karte (Lexar Alternative)1 x Argon IR Fernbedienung
(um Fernbedienungsfunktionen zum Diretta Host hinzuzufügen)1 x Flirc USB IR Empfänger (um die Argon IR
Fernbedienung mit dem Diretta Host in einem Flirc Gehäuse zu nutzen)1 x Blue Jeans BJC CAT6a Belden Bonded
Pairs 500 MHz (für die Verbindung zwischen Host und Target)1 x iFi SilentPower iPower Elite (für sauberen
Strom am Diretta Target)1 x iFi SilentPower Pulsar USB Kabel (USB-Verbindung mit galvanischer Trennung)1 x
DC 5.5mm x 2.1mm auf USB-C Adapter (nötig, um den iPower Elite an den USB-C Eingang des Diretta Target
anzuschließen)1 x SMSL PO100 PRO DDC (ein Digital-Digital-Wandler für DACs ohne gute USB-Implementierung)1 x
USB WLAN-Adapter (eine kabelgebundene Verbindung ist stark bevorzugt, aber falls Ethernet an der Anlage
unpraktisch ist, ersetzen Sie den Plugable USB-Ethernet-Adapter durch diesen WLAN-Adapter)1 x
Stromverteilerkabel (beide 45W Netzteile an einer Steckdose)Erforderliche Audiokomponente:1 x USB DAC oder
DDCErforderliche Werkzeuge:Laptop oder Desktop-PC mit Linux, macOS (iTerm2 empfohlen), oder Microsoft
Windows mit WSL2Ein SD- oder microSD-KartenleserEin HDMI-Fernseher oder Monitor (optional, aber nützlich zur
Fehlersuche)Software & LizenzkostenAudioLinux: Eine "Unlimited"-Lizenz wird für Enthusiasten empfohlen
(derzeit 158 $; Preise können sich ändern). Für den Einstieg reicht jedoch ein Einjahresabonnement für
derzeit 79 $. Beide Optionen erlauben die Installation auf mehreren Geräten am selben Standort.Diretta
Target: Eine Lizenz ist für die Hi-Res-Wiedergabe (höher als 44,1 kHz PCM) über das Diretta Target-Gerät
erforderlich und kostet derzeit 100 €.Sie können das Diretta Target mit 44,1 kHz-Streams über einen längeren
Zeitraum evaluieren. Ich empfehle daher, die Roon-Funktion Sample rate conversion in den MUSE
DSP-Einstellungen zu nutzen, um während der Testphase alle Inhalte auf 44,1 kHz zu konvertieren. Wenn Sie
zufrieden sind, kaufen Sie die Diretta Target Lizenz, um die Beschränkung aufzuheben. Lassen Sie die
Konvertierung aktiv, bis Sie die zweite E-Mail vom Diretta-Team erhalten, die bestätigt, dass Ihre Hardware
aktiviert wurde.WICHTIG: Diese Lizenz ist an die spezifische Hardware des Raspberry Pi gebunden, für den sie
gekauft wurde. Es ist essenziell, dass Sie den finalen Lizenzierungsschritt auf genau der Hardware
durchführen, die Sie dauerhaft nutzen möchten.Diretta bietet möglicherweise eine einmalige Ersatzlizenz bei
Hardwareausfall innerhalb der ersten zwei Jahre an (bitte Bedingungen beim Kauf prüfen). Bei Hardwarewechsel
aus anderen Gründen muss eine neue Lizenz erworben werden.2. Vorbereitung des ImagesKauf und Download:
Erwerben Sie das AudioLinux-Image von der offiziellen Webseite. Sie erhalten in der Regel innerhalb von 24
Stunden nach dem Kauf per E-Mail einen Link zum Herunterladen der .img.gz-Datei.Flashen des Images:
Verwenden Sie den Raspberry Pi Imager, um das heruntergeladene AudioLinux-Image auf beide microSD-Karten zu
schreiben.Hinweis: Das AudioLinux-Image ist ein direkter Festplatten-Dump, kein komprimierter Installer.
Daher ist die Image-Datei recht groß und der Flash-Vorgang kann ungewöhnlich lange dauern. Rechnen Sie mit
bis zu 15 Minuten pro Karte, abhängig von der Geschwindigkeit Ihrer microSD-Karte und des Lesegeräts.3.
Kernsystem-Konfiguration (Auf beiden Geräten durchführen)Nach dem Flashen müssen Sie jeden Raspberry Pi
individuell konfigurieren, um Netzwerkkonflikte zu vermeiden.Für die beste Leistung verwendet dieser
Leitfaden den Raspberry Pi 5 sowohl für das Diretta Target (das Gerät am DAC) als auch für den Diretta Host.
Sie werden zuerst den Host konfigurieren.KRITISCHE WARNUNG: Da beide Geräte vom exakt gleichen Image
geflasht werden, haben sie identische machine-id-Werte. Wenn Sie beide Geräte gleichzeitig einschalten,
während sie im selben LAN sind, wird Ihr DHCP-Server ihnen wahrscheinlich dieselbe IP-Adresse zuweisen, was
zu einem Netzwerkkonflikt führt.Sie müssen den ersten Start und die Konfiguration für jedes Gerät
nacheinander durchführen.Legen Sie die microSD-Karte in den ersten Raspberry Pi ein, verbinden Sie ihn mit
Ihrem Netzwerk und schalten Sie ihn ein. Hinweis: Wenn Sie das Argon ONE Gehäuse verwenden, hören Sie
möglicherweise Lüftergeräusche. Keine Sorge. Nach Abschluss der Diretta-Einrichtung gibt es in Anhang 1
Anweisungen zur Lüftersteuerung.Schließen Sie den kompletten Abschnitt 3 für dieses erste Gerät ab.Sobald
das erste Gerät mit seiner neuen, eindeutigen Konfiguration neu gestartet ist, schalten Sie es aus.Schalten
Sie nun den zweiten Raspberry Pi ein und wiederholen Sie den kompletten Abschnitt 3 für ihn.Bitte entnehmen
Sie Ihrer AudioLinux-Kaufquittung den Standard-SSH-Benutzer und das sudo/root-Passwort. Notieren Sie diese,
da Sie sie in diesem Prozess oft benötigen werden.Sie verwenden den SSH-Client auf Ihrem lokalen Computer,
um sich während dieses Prozesses bei den RPi-Computern anzumelden. Dafür müssen Sie die IP-Adresse der RPis
herausfinden, die sich nach einem Neustart ändern kann. Der einfachste Weg ist über die Weboberfläche oder
App Ihres Heimrouters, optional können Sie auch die fing App auf Ihrem Smartphone nutzen.Sobald Sie die
IP-Adresse eines Ihrer RPis haben, loggen Sie sich mit dem folgenden Prozess ein. Merken Sie sich den
Beispiel-ssh-Befehl, da Sie ähnliche Befehle in diesem Leitfaden verwenden werden.cmd=$(cat <<'EOT'
read -rp "Geben Sie die Adresse Ihres RPi ein und drücken Sie [Enter]: " RPi_IP_Address
echo 'Erinnerung: Das Standardpasswort steht in Ihrer AudioLinux E-Mail von Piero'
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
3.1. Machine ID neu generierenDie machine-id ist eine eindeutige Kennung für die OS-Installation. Sie muss
für jedes Gerät unterschiedlich sein.echo ""
echo "Alte Machine ID: $(cat /etc/machine-id)"
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
echo "Neue Machine ID: $(cat /etc/machine-id)"
3.2. Eindeutige Hostnamen setzenSetzen Sie einen klaren Hostnamen für jedes Gerät zur einfachen
Identifizierung. Hinweis: Falls dies nicht Ihr erster Aufbau nach dieser Anleitung ist und Sie bereits ein
Diretta Host/Target-Paar im Netzwerk haben, wählen Sie für diesen neuen Diretta Host einen anderen Namen,
wie z.B. diretta-host2, nur für diesen Teil. Das erleichtert später den Zugriff.Auf Ihrem ERSTEN Gerät (dem
zukünftigen Diretta Host):# Auf dem Diretta Host
sudo hostnamectl set-hostname diretta-host
Auf Ihrem ZWEITEN Gerät (dem zukünftigen Diretta Target):# Auf dem Diretta Target
sudo hostnamectl set-hostname diretta-target
Fahren Sie das Gerät an diesem Punkt herunter. Wiederholen Sie die oben genannten Schritte für den zweiten
Raspberry Pi.sudo sync && sudo poweroff
4. System-Updates (Auf beiden Geräten durchführen)Für die Schritte in diesem Abschnitt ist es meist am
effizientesten (und am wenigsten verwirrend), den gesamten Abschnitt 4 auf dem Diretta Host abzuschließen
und dann den gesamten Abschnitt auf dem Diretta Target zu wiederholen.Jeder RPi hat nun seine eigene Machine
ID, Sie können sie also jetzt einschalten. Wenn Sie zwei Netzwerkkabel haben, ist es bequemer, beide
gleichzeitig mit dem Heimnetzwerk zu verbinden, aber Sie können auch nacheinander vorgehen. Hinweis: Ihr
Router wird ihnen wahrscheinlich andere IP-Adressen zuweisen als beim ersten Login. Nutzen Sie die neuen
Adressen für Ihre SSH-Befehle. Hier eine Erinnerung:cmd=$(cat <<'EOT'
read -rp "Geben Sie die (neue) Adresse Ihres RPi ein und drücken Sie [Enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
4.1. "Chrony" installieren, um die Systemuhr zu aktualisierenDie Systemuhr muss genau sein, bevor wir
Updates installieren können. Der Raspberry Pi hat keine NVRAM-Batterie, daher muss die Uhr bei jedem
Bootvorgang gestellt werden. Dies geschieht typischerweise über einen Netzwerkdienst. Dieses Skript stellt
sicher, dass die Uhr gestellt wird und während des Betriebs korrekt bleibt.sudo id
curl -fsSL
[https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh](https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh)
| sudo bash
sleep 5
chronyc sources
4.2. Zeitzone einstellencmd=$(cat <<'EOT'
clear
echo "Willkommen zur interaktiven Zeitzonen-Einrichtung."
echo "Wählen Sie zuerst eine Region, dann eine spezifische Zeitzone."

# Region auswählen lassen
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

# Zeitzone innerhalb der Region auswählen lassen
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
4.3. DNS Utils installierenInstallieren Sie das dnsutils-Paket, damit das Menü-Update Zugriff auf den
dig-Befehl hat:sudo pacman -S --noconfirm --needed dnsutils
4.4. System- und Menü-Updates ausführenVerwenden Sie das AudioLinux-Menüsystem, um alle Updates
durchzuführen. Halten Sie die E-Mail von Piero mit Ihrem Image-Download-Benutzer und Passwort bereit. Sie
werden für das Menü-Update benötigt. Es fragt nach Ihrem Menü-Update-Benutzer, was etwas verwirrend sein
kann. Gemeint sind Benutzername und Passwort, die Sie zum Herunterladen des AudioLinux-Installationsimages
verwendet haben.Geben Sie menu im Terminal ein.Wählen Sie INSTALL/UPDATE menu.Wählen Sie auf dem nächsten
Bildschirm UPDATE system und lassen Sie den Prozess durchlaufen.Nachdem das System-Update fertig ist, wählen
Sie Update menu auf demselben Bildschirm, um die neueste Version der AudioLinux-Skripte zu
erhalten.Verlassen Sie das Menüsystem, um zum Terminal zurückzukehren.Hinweis: Workaround für Pacman
Update-ProblemEs gab ein bekanntes Problem, das das System-Update aufgrund von Konflikten mit
NVIDIA-Firmware-Dateien verhindern konnte (obwohl der RPi diese nicht nutzt). Falls Sie auf dieses Problem
stoßen, entfernen Sie zuerst linux-firmware und installieren Sie es als Teil des Upgrades neu:sudo pacman
-Rdd --noconfirm linux-firmware
sudo pacman -Syu --noconfirm linux-firmware
4.5. NeustartStarten Sie neu, um den Kernel und andere Updates zu laden:sudo sync && sudo reboot
5. Punkt-zu-Punkt Netzwerk-KonfigurationIn diesem Abschnitt erstellen wir die Netzwerkkonfigurationsdateien,
die die dedizierte private Verbindung aktivieren. Um keine physische Tastatur und Monitor zu benötigen,
führen wir diese Schritte durch, während beide Geräte noch mit Ihrem Haupt-LAN verbunden und per SSH
erreichbar sind.Wenn Sie gerade das Update Ihres Diretta Targets abgeschlossen haben, klicken Sie hier, um
zu den Netzwerkschritten für das Target zu springen.Ein Hinweis zur Netzwerkkonfiguration: Warum keine
einfache Bridge?Nutzer, die mit AudioLinux vertraut sind, fragen sich vielleicht, warum dieser Leitfaden
spezifische Skripte für eine geroutete Punkt-zu-Punkt-Verbindung mit NAT verwendet, anstatt die einfachere
Netzwerk-Bridge-Option im menu zu nutzen. Dies ist eine bewusste architektonische Entscheidung, um das
höchstmögliche Maß an Netzwerkisolierung zu erreichen.Eine Netzwerk-Bridge würde das Diretta Target direkt
in Ihr Haupt-LAN stellen und es somit sämtlichem Broadcast- und Multicast-Traffic aussetzen.Unser geroutetes
Setup schafft ein komplett separates, durch eine Firewall geschütztes Subnetz. Der Diretta Host schützt das
Target vor allem nicht-essenziellen Netzwerkverkehr ("Chatter"), sodass der Prozessor des Targets nur den
Audiostream verarbeitet. Dies minimiert Systemaktivität und potenzielles elektrisches Rauschen – das
ultimative Ziel dieser puristischen Architektur.Während eine Bridge funktional einfacher einzurichten ist,
bietet die geroutete Methode theoretisch eine überlegene Grundlage für die Audioleistung durch maximale
Isolation.5.1. Den Diretta Host vorkonfigurierenNetzwerkdateien erstellen:Erstellen Sie die folgenden zwei
Dateien auf dem Diretta Host. Die Datei end0.network setzt die statische IP für die zukünftige
Punkt-zu-Punkt-Verbindung. Die Datei usb-uplink.network stellt sicher, dass der USB-Ethernet-Adapter
weiterhin eine IP von Ihrem Haupt-LAN erhält.Datei: /etc/systemd/network/end0.networkcat <<'EOT' | sudo tee
/etc/systemd/network/end0.network
[Match]
Name=end0

[Link]
MTUBytes=1500

[Network]
Address=172.20.0.1/24
EOT
Datei: /etc/systemd/network/usb-uplink.networkcat <<'EOT' | sudo tee /etc/systemd/network/usb-uplink.network
[Match]
Name=en[pu]*

[Link]
MTUBytes=1500

[Network]
DHCP=yes
DNSSEC=no
EOT
Wichtig: Entfernen Sie die alte en.network Datei, falls vorhanden:# Alte generische Netzwerkdatei entfernen,
um Konflikte zu vermeiden.
sudo rm -fv /etc/systemd/network/{en,enp,auto,eth}.network
Fügen Sie einen /etc/hosts Eintrag für das Diretta Target hinzu:HOSTS_FILE="/etc/hosts"
TARGET_IP="172.20.0.2"
TARGET_HOST="diretta-target"

# Eintrag für das Diretta Target hinzufügen, falls nicht vorhanden
if ! grep -q "$TARGET_IP\s\+$TARGET_HOST" "$HOSTS_FILE"; then
  printf "%s\t%s target\n" "$TARGET_IP" "$TARGET_HOST" | sudo tee -a "$HOSTS_FILE"
fi
IP Forwarding aktivieren:# Für die aktuelle Sitzung aktivieren
sudo sysctl -w net.ipv4.ip_forward=1

# Dauerhaft speichern (überlebt Neustarts)
echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ip-forwarding.conf
Network Address Translation (NAT) konfigurieren:# Sicherstellen, dass nft installiert ist
sudo pacman -S --noconfirm --needed nftables

# Firewall- und NAT-Regeln installieren
cat <<'EOT' | sudo tee /etc/nftables.conf
#!/usr/sbin/nft -f

# Alte Regeln aus dem Speicher löschen
flush ruleset

# Eine Tabelle namens 'ip' (IPv4) namens 'my_table' erstellen
table ip my_table {

    # === Regel 2: Port Forwarding (DNAT) ===
    # Diese Chain greift in den 'prerouting' Pfad für NAT ein
    chain prerouting {
        type nat hook prerouting priority dstnat;

        # Leite Host Port 5101 weiter an Target Port 172.20.0.2:5001
        tcp dport 5101 dnat to 172.20.0.2:5001
    }

    # === Regel 3: Weitergeleiteten Verkehr erlauben (FILTER) ===
    # Diese Chain greift in den 'forward' Pfad für Paketfilterung ein
    chain forward {
        type filter hook forward priority 0;

        # Standardmäßig allen weitergeleiteten Verkehr verwerfen
        policy drop;

        # Bereits bestehende oder verwandte Verbindungen erlauben
        ct state established,related accept

        # NEUEN Verkehr erlauben, der der Port-Forwarding-Regel entspricht
        ip daddr 172.20.0.2 tcp dport 5001 ct state new accept

        # Allen anderen NEUEN Verkehr aus dem Target-Subnetz erlauben
        ip saddr 172.20.0.0/24 accept
    }

    # === Regel 1: Internetzugriff (MASQUERADE) ===
    # Diese Chain greift in den 'postrouting' Pfad für NAT ein
    chain postrouting {
        type nat hook postrouting priority 100;

        # NAT (Masquerade) Verkehr aus Ihrem Subnetz, der über
        # Interfaces rausgeht, die mit 'enp', 'enu' oder 'wlp' beginnen
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
Den Plugable USB-Ethernet-Adapter konfigurierenDer Standard-USB-Treiber unterstützt nicht alle Funktionen
des Plugable Ethernet-Adapters. Für zuverlässige Leistung müssen wir dem Gerätemanager des Kernels sagen,
wie er das Gerät behandeln soll:cat <<'EOT' | sudo tee /etc/udev/rules.d/99-ax88179a.rules
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0b95", ATTR{idProduct}=="1790",
ATTR{bConfigurationValue}!="1", ATTR{bConfigurationValue}="1"
EOT
sudo udevadm control --reload-rules
Das update_motd.sh Skript reparierenDas Skript, das das Login-Banner (/etc/motd) aktualisiert, kommt mit
zwei Netzwerkschnittstellen nicht gut klar. Dies verhindert, dass der Login-Bildschirm nach Neustarts mit
falschen IP-Informationen überladen wird. Das folgende Skript behebt dies.[ -f
/opt/scripts/update/update_motd.sh.dist ] || \
sudo mv /opt/scripts/update/update_motd.sh /opt/scripts/update/update_motd.sh.dist
curl -LO
[https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh](https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh)
sudo install -m 0755 update_motd.sh /opt/scripts/update/
rm update_motd.sh
Schließlich den Host ausschalten:sudo sync && sudo poweroff
5.2. Das Diretta Target vorkonfigurierenHinweis: Wenn Sie Schritt 4 auf dem Diretta Target noch nicht
durchgeführt haben, tun Sie das jetzt und kehren Sie hierher zurück.Erstellen Sie auf dem Diretta Target die
Datei end0.network. Dies konfiguriert seine statische IP und weist es an, den Diretta Host als Gateway für
jeglichen Internetverkehr zu nutzen.Datei: /etc/systemd/network/end0.networkcat <<'EOT' | sudo tee
/etc/systemd/network/end0.network
[Match]
Name=end0

[Link]
MTUBytes=1500

[Network]
Address=172.20.0.2/24
Gateway=172.20.0.1
DNS=1.1.1.1
EOT
Wichtig: Entfernen Sie die alte en.network Datei, falls vorhanden:# Alte generische Netzwerkdatei entfernen,
um Konflikte zu vermeiden.
sudo rm -fv /etc/systemd/network/{en,auto,eth}.network
Fügen Sie einen /etc/hosts Eintrag für den Diretta Host hinzu. Hinweis: Selbst wenn Sie einen anderen
Netzwerknamen für Ihren Diretta Host gewählt haben, ist es am besten, wenn das Diretta Target Ihren Host als
diretta-host kennt.HOSTS_FILE="/etc/hosts"
HOST_IP="172.20.0.1"
HOST_NAME="diretta-host"

# Eintrag für den Diretta Host hinzufügen, falls nicht vorhanden
if ! grep -q "$HOST_IP\s\+$HOST_NAME" "$HOSTS_FILE"; then
  printf "%s\t%s host\n" "$HOST_IP" "$HOST_NAME" | sudo tee -a "$HOSTS_FILE"
fi
5.3. Die Änderung der physischen VerbindungWarnung: Überprüfen Sie den Inhalt der Dateien, die Sie gerade
erstellt haben, doppelt. Ein Tippfehler könnte ein Gerät nach dem Neustart unzugänglich machen, was einen
Konsolenzugriff oder das erneute Flashen der SD-Karte erfordern würde.Sobald Sie die Dateien verifiziert
haben, führen Sie ein sauberes Herunterfahren beider Geräte durch:sudo sync && sudo poweroff
Trennen Sie beide Geräte von Ihrem Haupt-LAN-Switch/Router.Verbinden Sie den Onboard-Ethernet-Port des
Diretta Hosts direkt mit dem Onboard-Ethernet-Port des Diretta Targets mit einem einzigen
Ethernet-Kabel.Stecken Sie den USB-zu-Ethernet-Adapter in einen der blauen USB 3.0 Ports am Diretta Host
Computer.Verbinden Sie den USB-zu-Ethernet-Adapter am Diretta Host mit Ihrem
Haupt-LAN-Switch/Router.Schalten Sie beide Geräte ein.Beim Booten verwenden sie automatisch die neuen
Netzwerkkonfigurationen. Hinweis: Die IP-Adresse Ihres Diretta Hosts hat sich wahrscheinlich geändert, da er
nun über den USB-zu-Ethernet-Adapter mit Ihrem Heimnetzwerk verbunden ist. Sie müssen erneut in der
Weboberfläche Ihres Routers oder in der Fing App nach der neuen Adresse suchen, die ab jetzt stabil sein
sollte.cmd=$(cat <<'EOT'
read -rp "Geben Sie die finale Adresse Ihres Diretta Hosts ein und drücken Sie [Enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
Sie sollten nun in der Lage sein, das Target vom Host aus anzupingen:echo ""
echo "\$ ping -c 3 172.20.0.2"
ping -c 3 172.20.0.2
Außerdem sollten Sie sich vom Host aus auf dem Target einloggen können:echo ""
echo "\$ ssh target"
ssh -o StrictHostKeyChecking=accept-new target
Vom Target aus versuchen wir, einen Host im Internet anzupingen, um zu verifizieren, dass die Verbindung
funktioniert:echo ""
echo "\$ ping -c 3 one.one.one.one"
ping -c 3 one.one.one.one
6. Komfortabler & Sicherer SSH-Zugriff6.1. Die ProxyJump-AnforderungDa das Netzwerk nun konfiguriert ist,
befindet sich das Diretta Target in einem isolierten Netzwerk (172.20.0.0/24) und kann nicht direkt von
Ihrem Haupt-LAN erreicht werden. Der einzige Weg, darauf zuzugreifen, ist ein "Sprung" über den Diretta
Host.Die ProxyJump-Anweisung in Ihrer lokalen SSH-Konfiguration ist die Standardmethode, um dies zu
erreichen.Führen Sie diesen Befehl auf Ihrem lokalen Computer aus (nicht auf dem Raspberry Pi). Er wird Sie
nach der IP-Adresse des Diretta Hosts fragen und dann den genauen Konfigurationsblock ausgeben, den Sie
benötigen.cmd=$(cat <<'EOT'
clear
# --- Interaktives SSH Alias Setup Skript ---

SSH_CONFIG_FILE="$HOME/.ssh/config"
SSH_DIR="$HOME/.ssh"

# --- Sicherstellen, dass .ssh Verzeichnis und Config-Datei existieren und korrekte Rechte haben ---
mkdir -p "$SSH_DIR"
chmod 0700 "$SSH_DIR"
touch "$SSH_CONFIG_FILE"
chmod 0600 "$SSH_CONFIG_FILE"

# --- Empfohlenen globalen Einstellungsblock definieren ---
GLOBAL_SETTINGS=$(cat <<'EOF'
# --- Empfohlene globale SSH Einstellungen ---
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519

EOF
)

# --- Globale Einstellungen voranstellen, falls nicht vorhanden ---
if ! grep -q "AddKeysToAgent yes" "$SSH_CONFIG_FILE"; then
  echo "✅ Füge empfohlene globale SSH Einstellungen hinzu..."
  # Temporäre Datei nutzen, um Einstellungen voranzustellen
  echo "$GLOBAL_SETTINGS" | cat - "$SSH_CONFIG_FILE" > temp_ssh_config && mv temp_ssh_config
"$SSH_CONFIG_FILE"
else
  echo "✅ Empfohlene globale SSH Einstellungen existieren bereits. Keine Änderungen."
fi

# --- Diretta-spezifische Host-Konfigurationen hinzufügen ---
if grep -q "Host diretta-host" "$SSH_CONFIG_FILE"; then
  echo "✅ SSH Konfiguration für 'diretta-host' existiert bereits. Keine Änderungen."
else
  read -rp "Geben Sie die LAN IP-Adresse Ihres Diretta Hosts ein und drücken Sie [Enter]: " Diretta_Host_IP

  # Neue Konfiguration anhängen
  cat <<EOT_HOSTS >> "$SSH_CONFIG_FILE"

# --- Diretta Konfiguration (vom Skript hinzugefügt) ---
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

# --- StrictHostKeyChecking von älteren Versionen dieser Anleitung bereinigen ---
# Dies wird mit dem empfohlenen SSH-Key-Setup nicht mehr benötigt
if command -v sed >/dev/null; then
    sed -i.bak -e '/StrictHostKeyChecking/d' "$SSH_CONFIG_FILE"
    # Leere Zeilen entfernen
    sed -i.bak -e '/^$/N;/^\n$/D' "$SSH_CONFIG_FILE"
    rm -f "${SSH_CONFIG_FILE}.bak"
fi

echo ""
echo "--- Ihre ~/.ssh/config Datei enthält nun: ---"
cat "$SSH_CONFIG_FILE"
EOT
)
bash -c "$cmd"
Verbindung verifizieren:Sie sollten sich nun über die neuen Aliases mit beiden Geräten verbinden können.
Testen Sie die Verbindung mit folgenden Befehlen:Login auf dem Diretta Host:ssh -o
StrictHostKeyChecking=accept-new diretta-host
Tippen Sie exit zum Ausloggen.Login auf dem Diretta Target: (Sie werden zweimal nach dem Passwort
gefragt)ssh -o StrictHostKeyChecking=accept-new diretta-target
Hinweis: Sie werden einmal für den diretta-host (die "Jump Box") und ein zweites Mal für das diretta-target
selbst gefragt. Der nächste Abschnitt wird dies durch nahtlose Key-basierte Authentifizierung
ersetzen.Hinweis: Sie können ssh host und ssh target als Abkürzung verwenden.6.2. Empfohlen: Sichere
Authentifizierung mit SSH-KeysWährend Sie Passwörter verwenden können, ist die sicherste und bequemste
Methode die Authentifizierung per Public Key. Unsere SSH-Konfiguration automatisiert den Großteil des
Prozesses. Nach einer einmaligen Einrichtung können Sie sich sicher auf Host und Target einloggen, ohne ein
Passwort zu tippen.Auf Ihrem lokalen Computer:SSH Key erstellen (falls Sie noch keinen haben):Es ist Best
Practice, einen modernen Algorithmus wie ed25519 zu verwenden. Wenn Sie gefragt werden, geben Sie eine
starke, merkbare Passphrase ein. Dies ist nicht Ihr Login-Passwort, sondern ein Passwort, das Ihre private
Schlüsseldatei selbst schützt.ssh-keygen -t ed25519 -C "audiolinux"
Ihren Public Key auf die Geräte kopieren:Diese Befehle gewähren Ihrem Schlüssel sicheren Zugriff auf jedes
Gerät. Der erste Befehl fragt nach dem Passwort des Diretta Hosts. Da dies die Verbindung zum Host
passwortlos macht, wird der zweite Befehl nur noch nach dem Passwort des Diretta Targets fragen.echo ""
ssh-copy-id diretta-host
echo ""
ssh-copy-id diretta-target
Sicher einloggen:Sie können nun per SSH auf Ihre Geräte zugreifen. Beim ersten Verbinden werden Sie nach der
Passphrase gefragt, die Sie in Schritt 1 erstellt haben.ssh diretta-host
Unter Linux: Dank der Einstellung AddKeysToAgent yes wird Ihr Schlüssel zum SSH-Agent für Ihre aktuelle
Terminalsitzung hinzugefügt. Sie werden erst nach einem Neustart oder bei einer neuen Login-Sitzung wieder
nach der Passphrase gefragt.(Optional) Für ein verbessertes Linux-ErlebnisWenn Sie Linux-Nutzer sind und
möchten, dass Ihre SSH-Key-Passphrase über Neustarts hinweg erhalten bleibt (ähnlich wie bei macOS), wird
die Installation von keychain dringend empfohlen.Keychain installieren (Ubuntu/Debian):sudo apt update &&
sudo apt install keychain
Shell konfigurieren: Fügen Sie die folgende Zeile zu Ihrer ~/.bashrc (oder ~/.zshrc, ~/.profile, etc.)
hinzu, um keychain beim Öffnen eines Terminals zu starten. Es fragt nur einmal nach Ihrer Passphrase, wenn
Sie das erste Mal nach einem Neustart ein Terminal öffnen.eval `keychain --eval --quiet id_ed25519`
Laden Sie Ihre Shell neu, indem Sie ein neues Terminal öffnen oder source ~/.bashrc ausführen.Sie können nun
per SSH auf beide Geräte (ssh diretta-host, ssh diretta-target) zugreifen, ohne nach einem Passwort gefragt
zu werden, sicher authentifiziert durch Ihren SSH-Key.7. Allgemeine SystemoptimierungenBitte führen Sie
diese Schritte auf beiden Computern (Diretta Host und Target) aus. Falls Sie später ein menu-Update
durchführen, müssen Sie den sudoers-Fix erneut ausführen.7.1. Systemd "Degraded" Status behebenBei einer
frischen AudioLinux-Installation wird der Systemstatus oft als degraded (beeinträchtigt) gemeldet. Dies wird
typischerweise durch eine harmlose Inkonsistenz zwischen den Gruppendateien des Systems (/etc/group und
/etc/gshadow) verursacht. Der folgende Befehl synchronisiert diese Dateien sicher, was den fehlgeschlagenen
shadow.service behebt und einen sauberen Systemstatus gewährleistet.sudo grpconv
7.2. sudoers Regel-Priorität korrigierenEine Standardregel in der Hauptdatei /etc/sudoers kann manchmal
spezifischere Regeln überschreiben, die für die Web-UI und andere Funktionen benötigt werden. Dies kann dazu
führen, dass Befehle, die passwortlos sein sollten, fälschlicherweise nach einem Passwort fragen.Das
folgende Skript korrigiert die Reihenfolge der Regeln in der /etc/sudoers-Datei sicher, um zu gewährleisten,
dass spezifische Ausnahmen korrekt verarbeitet werden.SUDOERS_FILE="/etc/sudoers"
TEMP_SUDOERS=$(mktemp)

# Perl-Filter nutzen, um eine korrigierte Version der sudoers-Datei zu erstellen.
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

# Datei validieren vor der Installation
if [ -s "$TEMP_SUDOERS" ] && sudo visudo -c -f "$TEMP_SUDOERS"; then
    echo "Sudoers-Datei validiert. Installiere korrigierte Version..."
    sudo install -m 0440 -o root -g root "$TEMP_SUDOERS" "$SUDOERS_FILE"
else
    echo "FEHLER: Die modifizierte sudoers-Datei hat die Validierung nicht bestanden. Keine Änderungen
vorgenommen." >&2
fi
rm -f "$TEMP_SUDOERS"
7.3. Bootzeit optimierenUm eine lange Verzögerung beim Booten zu vermeiden, während das System auf eine
Netzwerkverbindung wartet, deaktivieren wir den "wait-online"-Dienst.# Netzwerk-Warte-Dienst deaktivieren,
um lange Boot-Verzögerungen zu vermeiden
sudo systemctl disable systemd-networkd-wait-online.service

# Override erstellen, damit das MOTD-Skript auf eine Default-Route wartet
sudo mkdir -p /etc/systemd/system/update_motd.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/update_motd.service.d/wait-for-ip.conf
[Service]
ExecStartPre=/bin/sh -c "while [ -z \"$(ip route show default)\" ]; do sleep 0.5; done"
EOT
7.4. Reparaturskript erstellenDas Standardverhalten von Arch Linux ist es, das /boot-Dateisystem in einem
"unclean"-Zustand zu belassen, wenn der Computer nicht sauber heruntergefahren wird. Das ist meist sicher,
aber ich habe festgestellt, dass dies beim Hochfahren unseres privaten Netzwerks zu Timing-Problemen ("Race
Condition") führen kann. Zudem ziehen Nutzer diese Geräte oft einfach vom Strom ab. Um uns davor zu
schützen, fügen wir ein Workaround-Skript hinzu, das das /boot-Dateisystem (das nur bei Software-Updates
geändert wird) sauber hält.Dieses Skript ist sicher sowohl automatisch beim Booten als auch manuell auf
einem laufenden System ausführbar.curl -LO
[https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh](https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh)
sudo install -m 0755 check-and-repair-boot.sh /usr/local/sbin/
rm check-and-repair-boot.sh
7.5. systemd Service-Datei erstellen und Dienst aktivierencat <<'EOT' | sudo tee
/etc/systemd/system/boot-repair.service
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
7.6. Disk I/O minimierenÄndern Sie #Storage=auto zu Storage=volatile in /etc/systemd/journald.confsudo sed
-i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
8. Diretta Software Installation & Konfiguration8.1. Auf dem Diretta TargetVerbinden Sie Ihren USB-DAC mit
einem der schwarzen USB 2.0 Ports am Diretta Target und stellen Sie sicher, dass der DAC eingeschaltet
ist.SSH zum Target: ssh diretta-target.Kompatible Compiler Toolchain konfigurierencurl -fsSL
[https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh](https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh)
| sudo bash
source /etc/profile.d/llvm_diretta.sh
Führen Sie menu aus.Wählen Sie AUDIO extra menu.Wählen Sie DIRETTA target installation. Sie sehen folgendes
Menü:What do you want to do?

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
Führen Sie diese Aktionen nacheinander aus:Wählen Sie 1) Install/update, um die Software zu
installieren.Wählen Sie 2) Enable/Disable Diretta Target und aktivieren (enable) Sie es.Wählen Sie 3)
Configure Audio card. Das System listet Ihre verfügbaren Audiogeräte auf. Geben Sie die Kartennummer Ihres
USB-DACs ein.?3
This option will set DIRETTA target to use a specific card
Your available cards are:

card 0: AUDIO [SMSL USB AUDIO], device 0: USB Audio [USB Audio]

Please type the card number (0,1,2...) you want to use:
?0
Wählen Sie 4) Edit configuration. Setzen Sie AlsaLatency=20 für einen Raspberry Pi 5 Target oder
AlsaLatency=40 für RPi4.Wählen Sie 6) License. Das System spielt für 6 Minuten Hi-Res-Audio (höher als 44,1
kHz PCM) im Testmodus ab. Folgen Sie dem Link auf dem Bildschirm und den Anweisungen, um Ihre volle Lizenz
für Hi-Res-Support zu kaufen und anzuwenden. Dies benötigt den Internetzugriff, den wir in Schritt 5
konfiguriert haben.Wählen Sie 8) Exit. Folgen Sie den Anweisungen zurück zum Terminal.8.2. Auf dem Diretta
HostSSH zum Host: ssh diretta-host.Kompatible Compiler Toolchain konfigurierencurl -fsSL
[https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh](https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh)
| sudo bash
source /etc/profile.d/llvm_diretta.sh
Führen Sie menu aus.Wählen Sie AUDIO extra menu.Wählen Sie DIRETTA host installation/configuration. Sie
sehen folgendes Menü:What do you want to do?

0) Install previous stable version
1) Install/update last version
2) Enable/Disable Diretta daemon
3) Set Ethernet interface
4) Edit configuration
5) Copy and edit new default configuration
6) Diretta log
7) Exit

?
Führen Sie diese Aktionen nacheinander aus:Wählen Sie 1) Install/update, um die Software zu installieren.
(Hinweis: Sie sehen vielleicht error: package 'lld' was not found. Keine Sorge, das wird automatisch
korrigiert)Wählen Sie 2) Enable/Disable Diretta daemon und aktivieren (enable) Sie ihn.Wählen Sie 3) Set
Ethernet interface. Es ist kritisch, hier end0 zu wählen, das Interface für die Punkt-zu-Punkt-Verbindung.?3
Your available Ethernet interfaces are: end0  enu1
Please type the name of your preferred interface:
end0
Wählen Sie 4) Edit configuration nur, wenn Sie fortgeschrittene Änderungen vornehmen müssen. Die vorherigen
Schritte sollten ausreichen; hier sind jedoch einige getunte Einstellungen, die Sie ausprobieren
können:TargetProfileLimitTime=0
FlexCycle=disable
CycleTime=800
periodMin=16
periodSizeMin=2048
Wenn Sie nur die getunten Parameter oben installieren wollen, können Sie diesen Befehlsblock nutzen:cat
<<'EOT' | sudo tee /opt/diretta-alsa/setting.inf
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
Wählen Sie 7) Exit. Folgen Sie den Anweisungen zurück zum Terminal.Erstellen Sie ein Override, damit der
Diretta-Dienst bei Fehler automatisch neustartetsudo mkdir -p /etc/systemd/system/diretta_alsa.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/diretta_alsa.service.d/restart.conf
[Service]
Restart=on-failure
RestartSec=5
EOT
9. Abschließende Schritte & Roon-IntegrationFühren Sie menu aus, falls Sie es verlassen haben, andernfalls
gehen Sie zum Main menu.Roon Bridge installieren (auf Host): Wenn Sie Roon nutzen, führen Sie folgendes auf
dem Diretta Host aus:Führen Sie menu aus.Wählen Sie INSTALL/UPDATE menu.Wählen Sie INSTALL/UPDATE
Roonbridge.Die Installation läuft. Das kann ein oder zwei Minuten dauern.Roon Bridge aktivieren (auf dem
Host):Wählen Sie Audio menu vom Hauptmenü.Wählen Sie SHOW audio service.Wenn Sie roonbridge nicht unter den
aktivierten Diensten sehen, wählen Sie ROONBRIDGE enable/disable.Beide Geräte neustarten: Für einen sauberen
Start, rebooten Sie Target und Host, in dieser Reihenfolge:sudo sync && sudo reboot
Roon konfigurieren:Öffnen Sie Roon auf Ihrem Steuergerät.Gehen Sie zu Einstellungen -> Audio.Unter der
Sektion "Diretta" sollten Sie Ihr Gerät sehen. Der Name basiert auf Ihrem DAC.Klicken Sie auf Aktivieren,
geben Sie ihm einen Namen und Sie sind bereit, Musik zu spielen!Ihre dedizierte Diretta-Verbindung ist nun
vollständig für makellose, isolierte Audiowiedergabe konfiguriert.Hinweis: Die "Limited"-Zone für
Diretta-Target-Tests verschwindet nach sechs Minuten Hi-Res-Musikwiedergabe aus Roon. Das ist normal. An
diesem Punkt müssen Sie eine Lizenz für das Diretta Target kaufen. Die Kosten betragen derzeit 100 € und die
Aktivierung kann bis zu 48 Stunden dauern. Sie erhalten zwei E-Mails vom Diretta-Team. Die erste ist Ihre
Quittung, die zweite Ihre Aktivierungsbenachrichtigung. Sobald Sie die Aktivierungs-E-Mail erhalten, starten
Sie Ihren Target-Computer neu, um die Aktivierung zu übernehmen.✅ Checkpoint: Kernsystem verifizierenIhr
Diretta- und Roon-Kernsystem sollte nun voll funktionsfähig sein. Um alle Dienste und Verbindungen zu
prüfen, gehen Sie bitte zu Anhang 5 und führen Sie den universellen System Health Check Befehl auf Host und
Target aus.10. Anhang 1: Optionale Argon ONE LüftersteuerungWenn Sie sich für ein Argon ONE Gehäuse für
Ihren Raspberry Pi entschieden haben, geht das Standard-Installationsskript davon aus, dass Sie ein
Debian-Betriebssystem nutzen. AudioLinux basiert jedoch auf Arch Linux, daher müssen Sie stattdessen diesen
Schritten folgen.Wenn Sie Argon ONE Gehäuse für beide (Host und Target) verwenden, müssen Sie diese Schritte
auf beiden Computern ausführen.Schritt 1: Das argon1.sh Skript im Handbuch überspringenDas Handbuch sagt,
Sie sollen das argon1.sh Skript von download.argon40.com laden und an bash pipen. Das funktioniert auf
AudioLinux nicht, da das Skript ein Debian-basiertes OS voraussetzt. Überspringen Sie diesen Schritt und
folgen Sie stattdessen den Schritten unten.Schritt 2: System konfigurieren:Diese Befehle aktivieren das
I2C-Interface und fügen das spezifische dtoverlay für das Argon ONE Gehäuse hinzu. Das Skript versucht erst,
den i2c_arm Parameter auszukommentieren, falls er kommentiert ist, und fügt dann das argonone Overlay hinzu,
falls es fehlt, um Fehler und doppelte Einträge zu vermeiden.BOOT_CONFIG="/boot/config.txt"
I2C_PARAM="dtparam=i2c_arm=on"

# --- I2C aktivieren durch Entfernen des Kommentars, falls vorhanden ---
if grep -q -F "#$I2C_PARAM" "$BOOT_CONFIG"; then
  echo "Enabling I2C parameter..."
  sudo sed -i -e "s/^#\($I2C_PARAM\)/\1/" "$BOOT_CONFIG"
fi
Schritt 3: udev Berechtigungen konfigurierencat <<'EOT' | sudo tee /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c-[0-9]*", MODE="0666"
EOT
Schritt 4: Das Argon One Paket installierenyay -S argonone-c-git
Hinweis: Falls der obige Befehl mit Compiler-Fehlern abbricht, versuchen Sie diese manuelle Prozedur, um das
Paket zu reparieren und zu installieren:# Repository klonen
git clone [https://aur.archlinux.org/argonone-c-git.git](https://aur.archlinux.org/argonone-c-git.git)
cd argonone-c-git

# Quellcode herunterladen ohne zu bauen
makepkg -o

# Patch anwenden, um Kompilierungsfehler mit GCC 14+ zu beheben
sed -i 's/_timer_thread()/_timer_thread(void *args)/g' src/argonone-c-git/src/event_timer.c

# Mit gepatchtem Source kompilieren und installieren
makepkg -e -i --noconfirm

# Aufräumen
cd ..
rm -rf argonone-c-git
Schritt 5: Argon ONE Gehäuse von Hardware- auf Softwaresteuerung umschaltensudo pacman -S --noconfirm
--needed i2c-tools libgpiod
# Systemd Overrides erstellen, um das Gehäuse beim Booten in den Software-Modus zu schalten
sudo mkdir -pv /etc/systemd/system/argononed.service.d
cat <<'EOT'| sudo tee /etc/systemd/system/argononed.service.d/software-mode.conf
[Service]
ExecStartPre=/bin/sh -c "while [ ! -e /dev/i2c-1 ]; do sleep 0.1; done && /usr/bin/i2cset -y 1 0x1a 0"
EOT

cat <<'EOT'| sudo tee /etc/systemd/system/argononed.service.d/override.conf
[Unit]
After=multi-user.target
EOT
Schritt 6: Dienst aktivieren# Den Systemd Manager neu laden, um die neue Konfiguration zu lesen
sudo systemctl daemon-reload

# Den Dienst aktivieren, damit er beim Booten startet
sudo systemctl enable argononed.service
Schritt 7: NeustartSchließlich den Raspberry Pi neustarten (erst Target, dann Host), damit alle Änderungen
wirksam werden:sudo sync && sudo reboot
Jetzt wird der Lüfter vom Daemon gesteuert und der Power-Knopf hat volle Funktionalität.Schritt 8: Dienst
verifizierensystemctl status argononed.service
journalctl -u argononed.service -b
Schritt 9: Lüftermodus und Einstellungen überprüfen:Um die aktuellen Konfigurationswerte zu sehen, führen
Sie folgenden Befehl aus:sudo argonone-cli --decode
Um diese Werte anzupassen, müssen Sie eine Konfigurationsdatei erstellen. Nutzen Sie diese Werte als
Startpunkt:cat <<'EOT' | sudo tee /etc/argononed.conf
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
Starten Sie den Dienst neu, um die neuen Werte zu übernehmen:sudo systemctl restart argononed.service
echo ""
echo "Aktualisierte Lüfterwerte:"
sleep 5
sudo argonone-cli --decode
Jetzt können Sie die Werte nach Bedarf anpassen, indem Sie die Schritte oben befolgen.11. Anhang 2:
Optionale IR-FernbedienungDieser Leitfaden bietet Anweisungen zur Installation und Konfiguration einer
IR-Fernbedienung zur Steuerung von Roon. Die Einrichtung ist in zwei Teile gegliedert.Teil 1 deckt das
hardware-spezifische Setup ab. Sie wählen einen der beiden Anhänge, je nachdem, ob Sie den Flirc
USB-Empfänger oder den eingebauten Empfänger des Argon One Gehäuses nutzen.Teil 2 deckt das Software-Setup
für das roon-ir-remote Steuerungsskript ab, welches für beide Hardware-Optionen identisch ist.Hinweis: Sie
führen diese Schritte nur auf dem Diretta Host aus. Das Target sollte nicht zur Weiterleitung von
IR-Befehlen an den Roon Server genutzt werden.Teil 1: IR-Empfänger Hardware SetupFolgen Sie dem Anhang für
die Hardware, die Sie verwenden.Option 1: Flirc USB IR-Empfänger SetupKauf und Programmierung des
Flirc-Geräts:Sie benötigen den Flirc USB IR Receiver, erhältlich auf deren Website:
https://flirc.tv/products/flirc-usb-receiverDas Flirc-Gerät muss an einem Desktop-Computer mit der Flirc
GUI-Software programmiert werden.Stecken Sie den Flirc in Ihren Desktop-Computer und öffnen Sie die Flirc
GUI.Gehen Sie zu Controllers und wählen Sie Full Keyboard.Programmieren Sie die Tasten, die für das Skript
benötigt werden (z.B. KEY_UP, KEY_DOWN, KEY_ENTER, etc.), indem Sie die Taste in der GUI anklicken und dann
die entsprechende Taste auf Ihrer physischen Fernbedienung drücken.Sobald programmiert, stecken Sie den
Flirc in den Diretta Host.Testen des Flirc-Geräts:Verifizieren Sie, dass der Raspberry Pi den Flirc als
Tastatur erkennt.sudo pacman -S --noconfirm evtest
sudo evtest
Wählen Sie das "Flirc"-Gerät aus dem Menü. Wenn Sie Tasten auf Ihrer Fernbedienung drücken, sollten Sie
Tastaturereignisse auf dem Bildschirm sehen.Springen Sie zu Teil 2: Steuerungsskript Software SetupOption 2:
Argon One IR-Fernbedienung SetupIR-Empfänger Hardware aktivieren:Sie müssen das Hardware-Overlay für den
IR-Empfänger des Argon One Gehäuses aktivieren.Dieser Befehl fügt das benötigte Hardware-Overlay sicher zu
Ihrer /boot/config.txt hinzu und prüft vorher, dass es nicht doppelt hinzugefügt
wird.BOOT_CONFIG="/boot/config.txt"
IR_CONFIG="dtoverlay=gpio-ir,gpio_pin=23"

# IR Overlay hinzufügen, falls nicht bereits vorhanden
if ! sed 's/#.*//' $BOOT_CONFIG | grep -q -F "$IR_CONFIG"; then
  echo "Aktiviere Argon One IR Receiver..."
  sudo sed -i "/# Uncomment this to enable infrared communication./a $IR_CONFIG" /boot/config.txt
else
  echo "Argon One IR Receiver bereits aktiviert."
fi
Ein Neustart ist erforderlich, damit die Hardwareänderung wirksam wird.sudo sync && sudo reboot
IR Tools installieren und Protokolle aktivieren:Installieren Sie ir-keytablesudo pacman -S --noconfirm
v4l-utils
Tasten-Scancodes erfassen:Aktivieren Sie alle Kernel-Protokolle, damit Signale von Ihrer Fernbedienung
dekodiert werden können. Führen Sie das Test-Tool aus, um den eindeutigen Scancode für jede Taste zu
sehen.sudo ir-keytable -p all
sudo ir-keytable -t
Drücken Sie jede Taste, die Sie nutzen möchten, und notieren Sie ihren Scancode aus der MSC_SCAN
Ereignis-Ausgabe (z.B. value ca). Drücken Sie Ctrl+C, wenn Sie fertig sind.Keymap-Datei erstellen:Diese
Datei ordnet die Scancodes Standard-Tastennamen zu.Erstellen Sie eine neue Keymap-Datei:cat <<'EOT' | sudo
tee /etc/rc_keymaps/argon.toml
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
Falls die Scancodes im Beispiel oben nicht mit denen übereinstimmen, die Sie notiert haben, bearbeiten Sie
die Datei (sudo nano /etc/rc_keymaps/argon.toml) und passen Sie sie an.Einen systemd Service erstellen, um
die Keymap zu laden:Dieser Dienst lädt Ihre Keymap automatisch beim Booten.Erstellen Sie eine neue
Service-Datei und aktivieren Sie den Dienst:cat <<'EOT' | sudo tee /etc/systemd/system/ir-keymap.service
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
Eingabegerät testen:Verifizieren Sie, dass das System Tastaturereignisse von der IR-Fernbedienung
empfängt.sudo pacman -S --noconfirm evtest
sudo evtest
Wählen Sie das gpio_ir_recv Gerät. Wenn Sie Tasten auf der Fernbedienung drücken, sollten Sie die
entsprechenden Key-Events sehen.Tippen Sie CTRL-C, wenn Sie mit dem Testen fertig sind.Teil 2:
Steuerungsskript Software SetupNachdem Sie Ihre Hardware in Teil 1 eingerichtet haben, folgen Sie diesen
Schritten, um das Python-Steuerungsskript zu installieren und zu konfigurieren.Schritt 1: audiolinux zur
input Gruppe hinzufügenDies ist notwendig, damit der audiolinux-Account Zugriff auf Ereignisse des
Fernbedienungsempfängers hat.sudo usermod --append --groups input audiolinux
Loggen Sie sich aus und wieder ein, damit diese Änderung wirksam wird. Sie können dies mit folgendem Befehl
prüfen:echo ""
echo ""
echo "Prüfe Gruppenmitgliedschaften:"
echo "\$ groups"
groups
echo ""
echo "Oben sollten Sie sehen:"
echo "audiolinux realtime video input audio wheel"
Schritt 2: Python via pyenv installierenInstallieren Sie pyenv und die neueste stabile Python-Version.#
Build-Abhängigkeiten installieren
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline
util-linux db gdbm sqlite vim jq

# pyenv nur installieren, wenn es nicht bereits installiert ist
if [ ! -d "$HOME/.pyenv" ]; then
  echo "--- Installiere pyenv ---"
  curl -fsSL [https://pyenv.run](https://pyenv.run) | bash
else
  echo "--- pyenv ist bereits installiert. Überspringe Installation. ---"
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

# Datei sourcen, um pyenv in der aktuellen Shell verfügbar zu machen
. ~/.bashrc

# Neueste Python-Version installieren und setzen, falls nicht bereits vorhanden
PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
  echo "--- Installiere Python ${PYVER}. Dies wird einige Minuten dauern... ---"
  pyenv install $PYVER
else
  echo "--- Python ${PYVER} ist bereits installiert. Überspringe Installation. ---"
fi

# Globale Python-Version setzen
pyenv global $PYVER
Hinweis: Es ist normal, dass der Teil Installing Python-3.14.2... ca. 10 Minuten dauert, da Python aus dem
Quellcode kompiliert wird. Geben Sie nicht auf! Entspannen Sie sich bei guter Musik über Ihre neue
Diretta-Zone in Roon, während Sie warten. Sie sollte verfügbar sein, während Python auf dem Host installiert
wird.Schritt 3: roon-ir-remote Software Repo herunterladenKlonen Sie das Skript-Repository und holen Sie
einen Patch, um Keycodes korrekt nach Namen statt Nummer zu behandeln.cd
# Repo klonen wenn nicht vorhanden, sonst updaten
if [ ! -d "roon-ir-remote" ]; then
  git clone
[https://github.com/dsnyder0pc/roon-ir-remote.git](https://github.com/dsnyder0pc/roon-ir-remote.git)
else
  (cd roon-ir-remote && git pull)
fi
Schritt 4: Roon Umgebungs-Konfigurationsdatei erstellenKonfigurieren Sie das Skript mit Ihren Roon-Details.
Hinweis: Die event_mapping-Codes müssen mit den Tastennamen übereinstimmen, die Sie im Hardware-Setup
definiert haben (KEY_ENTER, KEY_VOLUMEUP, etc.).bash <<'EOF'
# --- Start des Skripts ---

# Roon Zone abfragen und in Variable speichern
echo "Geben Sie den Namen Ihrer Roon Zone ein."
echo "WICHTIG: Dies muss exakt mit dem Zonennamen in der Roon App übereinstimmen (Groß-/Kleinschreibung
beachten)."
# Diese Zeile ist der Fix: < /dev/tty sagt read, das Terminal zu nutzen
read -rp "Geben Sie Ihren Roon Zonen-Namen ein: " MY_ROON_ZONE < /dev/tty

# Zielverzeichnis sicherstellen
mkdir -p roon-ir-remote

# Konfigurationsdatei mit Here Document erstellen
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
      "website":
"[https://github.com/dsnyder0pc/roon-ir-remote](https://github.com/dsnyder0pc/roon-ir-remote)"
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
echo "✅ Konfigurationsdatei 'roon-ir-remote/app_info.json' erfolgreich erstellt."

# --- Ende des Skripts ---
EOF
Schritt 5: roon-ir-remote vorbereiten und testenInstallieren Sie die Abhängigkeiten des Skripts in eine
virtuelle Umgebung und führen Sie es zum ersten Mal aus.cd ~/roon-ir-remote
# Virtuelle Umgebung erstellen, nur wenn sie nicht existiert
if ! pyenv versions --bare | grep -q "^roon-ir-remote$"; then
  echo "--- Erstelle 'roon-ir-remote' virtuelle Umgebung ---"
  pyenv virtualenv roon-ir-remote
else
  echo "--- 'roon-ir-remote' virtuelle Umgebung existiert bereits ---"
fi
pyenv activate roon-ir-remote
pip3 install --upgrade pip
pip3 install -r requirements.txt

python roon_remote.py
Beim ersten Ausführen müssen Sie die Erweiterung in Roon autorisieren, indem Sie zu Einstellungen ->
Erweiterungen gehen.Während Musik in Ihrer neuen Diretta Roon-Zone spielt, richten Sie Ihre IR-Fernbedienung
auf den Diretta Host Computer und drücken Sie die Play/Pause-Taste (oft die mittlere Taste im Steuerkreuz).
Probieren Sie auch Weiter und Zurück. Wenn diese nicht funktionieren, prüfen Sie Ihr Terminalfenster auf
Fehlermeldungen. Wenn Sie mit dem Testen fertig sind, tippen Sie CTRL-C zum Beenden.Schritt 6: Einen systemd
Service erstellenErstellen Sie einen Dienst, um das Skript automatisch im Hintergrund laufen zu lassen.cat
<<EOT | sudo tee /etc/systemd/system/roon-ir-remote.service
[Unit]
Description=Roon IR Remote Service
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${LOGNAME}
Group=${LOGNAME}
WorkingDirectory=/home/${LOGNAME}/roon-ir-remote
ExecStart=/home/${LOGNAME}/.pyenv/versions/roon-ir-remote/bin/python
/home/${LOGNAME}/roon-ir-remote/roon_remote.py
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
Schritt 7: Logs kurz beobachten:journalctl -b -u roon-ir-remote.service -f
Tippen Sie CTRL-C, sobald Sie zufrieden sind, dass alles wie erwartet läuft.Schritt 8: set-roon-zone Skript
installierenEs ist gut, ein Skript zu haben, mit dem man den Roon-Zonennamen später bei Bedarf aktualisieren
kann. Hier die Installation:curl -LO
[https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone](https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone)
sudo install -m 0755 set-roon-zone /usr/local/bin/
rm set-roon-zone
Zur Nutzung loggen Sie sich einfach auf dem Diretta Host Computer ein und tippen:set-roon-zone
Folgen Sie den Anweisungen, um den neuen Namen für Ihre Roon Zone einzugeben. Sie müssen eventuell das
Root-Passwort eingeben, damit die Änderungen wirksam werden.Hinweis: Ein besserer Weg, die Zone zu
setzenWährend dieses Skript perfekt funktioniert, ist die empfohlene Methode zur Änderung der Roon Zone die
Nutzung der AnCaolas Link System Control Webanwendung, detailliert beschrieben in Anhang 4. Die Web-UI
bietet eine dedizierte Seite zum Ansehen und Bearbeiten des Zonennamens von Ihrem Telefon oder Browser
aus.Schritt 9: Profit!  Checkpoint: IR-Setup verifizierenIhre IR-Fernbedienungshardware und -software sollte
nun konfiguriert sein. Um das Setup zu verifizieren, gehen Sie zu Anhang 5 und führen Sie den universellen
System Health Check Befehl auf dem Diretta Host aus.Ihre IR-Fernbedienung sollte nun Roon steuern. Viel
Spaß!12. Anhang 3: Optionaler Purist-ModusEs gibt minimale Netzwerk- und Hintergrundaktivitäten auf dem
Diretta Target Computer, die nicht mit der Musikwiedergabe über das Diretta-Protokoll zusammenhängen. Manche
Nutzer bevorzugen es jedoch, zusätzliche Schritte zu unternehmen, um die Möglichkeit solcher Aktivitäten zu
reduzieren. Wir befinden uns bereits am extremen Rand der Audioleistung, also warum nicht?KRITISCHE WARNUNG:
NUR für das Diretta TargetDas purist-mode Skript und alle Anweisungen in diesem Anhang sind exklusiv für das
Diretta Target gedacht.Installieren oder führen Sie dieses Skript NICHT auf dem Diretta Host aus. Dies würde
die Verbindung des Hosts zu Ihrem Hauptnetzwerk trennen, ihn unerreichbar machen und die Kommunikation mit
Ihrem Roon Core oder Streaming-Diensten unterbinden. Das gesamte System wäre unbrauchbar, bis Sie
Konsolenzugriff (mit physischer Tastatur und Monitor) erlangen, um die Änderungen rückgängig zu
machen.Schritt 1: Das purist-mode Skript installieren (nur auf dem Diretta Target Computer)curl -LO
[https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode](https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode)
sudo install -m 0755 purist-mode /usr/local/bin
rm purist-mode

# Skript zur Anzeige des Purist-Modus-Status beim Login
cat <<'EOT' | sudo tee /etc/profile.d/purist-status.sh
#!/bin/sh
BACKUP_FILE="/etc/nsswitch.conf.purist-bak"

if [ -f "$BACKUP_FILE" ]; then
    echo -e '\n\e[1;32m✅ Purist-Modus ist AKTIV.\e[0m System optimiert für höchste Klangqualität.'
else
    echo -e '\n\e[1;33m⚠️ VORSICHT: Purist-Modus ist DEAKTIVIERT.\e[0m Hintergrundaktivität kann
Klangqualität beeinflussen.'
fi
EOT
Um es auszuführen, loggen Sie sich einfach auf dem Diretta Target ein und tippen purist-mode:purist-mode
Zum Beispiel:[audiolinux@diretta-target ~]$ purist-mode
Dieses Skript erfordert sudo-Rechte. Sie werden evtl. nach einem Passwort gefragt.
tiviere Purist-Modus...
  -> Stoppe Zeitsynchronisationsdienst (chronyd)...
  -> Deaktiviere DNS Lookups...
  -> Entferne Standard-Gateway...

✅ Purist-Modus ist AKTIV.
Hören Sie eine Weile, um zu sehen, ob Sie den Klang bevorzugen (oder den Seelenfrieden).Schritt 2:
Purist-Modus standardmäßig aktivierenWenn Sie entschieden haben, dass Sie den Klang mit aktiviertem
Purist-Modus bevorzugen, machen Sie ihn zum Standard nach jedem Neustart.echo ""
echo "- Deaktiviere Purist-Modus für einen sauberen Zustand"
purist-mode --revert

echo ""
echo "- Erstelle Dienst zum Zurücksetzen auf Standard-Modus bei jedem Boot"
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
echo "- Erstelle Dienst für verzögerte Auto-Aktivierung"
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
echo "- Aktiviere die neuen Dienste"
sudo systemctl daemon-reload
sudo systemctl enable purist-mode-revert-on-boot.service
sudo systemctl enable purist-mode-auto.service
Schritt 3: Einen Wrapper um den menu Befehl installierenViele Funktionen in AudioLinux benötigen
Internetzugriff. Damit alles wie erwartet funktioniert, fügen wir einen Wrapper um den menu Befehl hinzu,
der den Purist-Modus deaktiviert, während Sie das Menü nutzen, und ihn wieder aktiviert, wenn Sie zum
Terminal zurückkehren.if grep -q menu_wrapper ~/.bashrc; then
  :
else
  echo ""
  echo "Füge Wrapper um den menu Befehl hinzu"
  cat <<'EOT' | tee -a ~/.bashrc

# Custom Wrapper für das AudioLinux Menü, um Purist-Modus zu verwalten
menu_wrapper() {
  local was_active=false
  # Prüfe Anfangszustand des Purist-Modus anhand der Backup-Datei.
  if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
    was_active=true
  fi

  # Wenn Purist-Modus aktiv war, temporär für das Menü deaktivieren.
  if [ "$was_active" = true ]; then
    echo "Prüfe Berechtigungen für Purist-Modus Management..."
    sudo -v

    echo "Deaktiviere Purist-Modus vorübergehend für Menü..."
    purist-mode --revert > /dev/null 2>&1 # Revert leise
  fi

  # Den originalen menu Befehl aufrufen
  /usr/bin/menu

  # Wenn Purist-Modus vorher aktiv war, jetzt wieder aktivieren.
  if [ "$was_active" = true ]; then
    echo "Re-aktiviere Purist-Modus..."
    purist-mode > /dev/null 2>&1 # Activate leise
    echo "Purist-Modus ist wieder aktiv."
  fi
}

# Alias für 'menu' Befehl auf unsere neue Wrapper-Funktion setzen
alias menu='menu_wrapper'
# Aliases zum Verwalten des automatischen Purist-Modus Dienstes
alias purist-mode-auto-enable='echo "Aktiviere Purist-Modus beim Boot..."; purist-mode; sudo systemctl
enable purist-mode-auto.service'
alias purist-mode-auto-disable='echo "Deaktiviere Purist-Modus beim Boot..."; purist-mode --revert; sudo
systemctl disable --now purist-mode-auto.service'
EOT
fi

source ~/.bashrc
Die Purist-Modus Zustände verstehenDas Purist-Modus-System ist flexibel gestaltet und erlaubt Ihnen manuelle
Kontrolle oder automatische Aktivierung nach dem Booten. Es operiert in zwei Hauptzuständen:Deaktiviert
(Standard-Modus):Dies ist der normale, voll funktionale Zustand des Diretta Targets. Das Netzwerk-Gateway
ist aktiv, alle Dienste (chronyd, argononed) laufen und das Gerät arbeitet ohne Einschränkungen.Aktiv
(Purist-Modus):Dies ist der optimierte Zustand für kritisches Hören. Das Netzwerk-Gateway wird entfernt, um
Internetverkehr zu verhindern, und nicht-essenzielle Hintergrunddienste (inklusive des Argon ONE Lüfters)
werden gestoppt, um jegliche potenzielle Systemstörung zu minimieren.Diese Zustände werden auf zwei Arten
verwaltet: automatisch beim Booten und manuell über die Kommandozeile.Automatische Kontrolle (Beim
Booten)Der Boot-Prozess ist sicher und vorhersehbar gestaltet, mit einem optionalen automatischen Wechsel in
den Purist-Modus.Zwingendes Zurücksetzen beim Boot: Unabhängig vom Zustand beim Herunterfahren bootet das
Diretta Target immer in den Standard-Modus. Dies ist ein kritisches Feature, das sicherstellt, dass
essenzielle Dienste wie Netzwerkzeitsynchronisation korrekt laufen können.Optionale Auto-Aktivierung: Wenn
Sie das automatische Feature aktiviert haben, wartet das System 60 Sekunden nach dem Booten und wechselt
dann automatisch in den Purist-Modus. Dies bietet ein "Set it and forget it"-Erlebnis für Nutzer, die immer
im optimierten Zustand hören möchten.Manuelle Kontrolle (Interaktive Nutzung)Sie haben jederzeit volle
interaktive Kontrolle über das System.Um den Purist-Modus für eine Hörsession manuell zu aktivieren, loggen
Sie sich auf dem Diretta Target Computer ein und führen aus:purist-mode
Um den Purist-Modus manuell zu deaktivieren und zum Standardbetrieb zurückzukehren, führen Sie
aus:purist-mode --revert
Um das automatische Boot-Verhalten zu steuern, nutzen Sie die Komfort-Aliases auf dem Diretta Target:# Dies
aktiviert die 60-Sekunden Auto-Aktivierung beim nächsten Boot
purist-mode-auto-enable

# Dies deaktiviert die Auto-Aktivierung beim nächsten Boot
purist-mode-auto-disable
13. Anhang 4: Optionale Systemsteuerungs-WeboberflächeDieser Anhang bietet Anweisungen zur Installation
einer einfachen webbasierten Anwendung auf dem Diretta Host. Diese Anwendung bietet eine einfach zu
bedienende Oberfläche, die von einem Telefon oder Tablet aus zugänglich ist, um Schlüsselfunktionen Ihres
Diretta-Systems zu verwalten, einschließlich Purist-Modus auf dem Target und Roon
IR-Fernbedienungseinstellungen auf dem Host.KRITISCHE WARNUNG: Führen Sie diese Schritte sorgfältig
aus.Dieses Setup beinhaltet das Erstellen eines neuen Benutzers und das Modifizieren von
Sicherheitseinstellungen. Folgen Sie den Anweisungen präzise, um sicherzustellen, dass das System sicher und
funktional bleibt.Das Setup ist in zwei Teile gegliedert: Zuerst konfigurieren wir das Diretta Target, um
Befehle sicher zu akzeptieren, und zweitens installieren wir die Webanwendung auf dem Diretta Host. Passen
Sie gut auf, da wir häufig zwischen den Hosts wechseln.Teil 1: Diretta Target KonfigurationAuf dem Diretta
Target erstellen wir einen neuen Benutzer mit sehr eingeschränkten Rechten. Dieser Benutzer darf nur die
spezifischen Befehle ausführen, die zur Verwaltung des Purist-Modus nötig sind.SSH zum Diretta Target:ssh
diretta-target
Neuen Benutzer für die App erstellen:Dieser Befehl erstellt einen neuen Benutzer namens purist-app und sein
Home-Verzeichnis. Eine gültige Shell ist erforderlich, damit nicht-interaktive SSH-Befehle
funktionieren.sudo useradd --create-home --shell /bin/bash purist-app
Sichere Befehlsskripte erstellen:Wir erstellen vier kleine, dedizierte Skripte, die die einzigen Aktionen
sind, die die Web-App ausführen darf. Dies ist ein kritischer Sicherheitsschritt.# Skript, um den aktuellen
Status inklusive Lizenzstatus zu holen
cat <<'EOT' | sudo tee /usr/local/bin/pm-get-status
#!/bin/bash
IS_ACTIVE="false"
IS_AUTO_ENABLED="false"
LICENSE_LIMITED="false"

# Prüfen auf Purist-Modus
if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
  IS_ACTIVE="true"
fi

# Prüfen, ob Auto-Start aktiviert ist
if systemctl is-enabled --quiet purist-mode-auto.service; then
  IS_AUTO_ENABLED="true"
fi

# Prüfen auf Vorhandensein des Diretta Lizenzschlüssels
if ! ls /opt/diretta-alsa-target/ | grep -qv '^diretta'; then
  LICENSE_LIMITED="true"
fi

# Alle Statusflags als einzelnes JSON-Objekt ausgeben
echo "{\"purist_mode_active\": $IS_ACTIVE, \"auto_start_enabled\": $IS_AUTO_ENABLED,
\"license_needs_activation\": $LICENSE_LIMITED}"
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

# Skript erstellen, um den Diretta Dienst neu zu starten
cat <<'EOT' | sudo tee /usr/local/bin/pm-restart-target
#!/bin/bash
# Startet den Diretta ALSA Target Service neu.
# Dieses Skript soll via sudo vom purist-app User aufgerufen werden.
/usr/bin/systemctl restart diretta_alsa_target.service
EOT

# Skript erstellen, um die Diretta Lizenz-URL abzurufen
cat <<'EOT' | sudo tee /usr/local/bin/pm-get-license-url
#!/bin/bash

# Einzige Aufgabe dieses Skripts ist das Lesen der Cache-Datei, die beim Boot erstellt wurde.
readonly CACHE_FILE="/tmp/diretta_license_url.cache"

if [ -s "$CACHE_FILE" ]; then
    # Wenn Cache existiert und Inhalt hat, anzeigen.
    cat "$CACHE_FILE"
else
    # Wenn nicht, hilfreichen Fehler auf stderr ausgeben und beenden.
    echo "Error: License cache not found or is empty." >&2
    exit 1
fi
EOT

# Neue Skripte ausführbar machen
sudo chmod -v +x /usr/local/bin/pm-*
Sudo-Berechtigungen gewähren:Dieser Schritt erlaubt dem purist-app Benutzer, unsere vier neuen Skripte mit
Root-Rechten auszuführen, ohne ein interaktives Terminal zu benötigen.cat <<'EOT' | sudo tee
/etc/sudoers.d/purist-app
# Sudo sagen, dass kein TTY für purist-app nötig ist
Defaults:purist-app !requiretty

# Dem purist-app User erlauben, die spezifischen Steuerungsskripte ohne Passwort auszuführen
purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-status
purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-mode
purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-auto
purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-restart-target
purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-license-url
EOT
Diretta Lizenz-Cache-Datei beim Booten füllenDas Abrufen der Diretta Lizenz-URL benötigt eine
Internetverbindung. Wenn Purist-Modus standardmäßig aktiv ist, kann das Target die URL nie abrufen. Jedoch
haben wir beim Booten den Purist-Modus für 60 Sekunden deaktiviert, um die Uhr zu stellen und auf eine
Diretta Lizenzaktivierung zu prüfen. Wir können dieses Zeitfenster nutzen, um auch die URL abzurufen.#
Skript herunterladen, Rechte setzen und in den Systempfad legen
curl -LO
[https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh](https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh)
sudo install -m 0755 create-diretta-cache.sh /usr/local/bin/
rm create-diretta-cache.sh

# Systemd Drop-in Datei erstellen
sudo mkdir -p /etc/systemd/system/purist-mode-revert-on-boot.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/purist-mode-revert-on-boot.service.d/create-cache.conf
[Service]
ExecStartPost=/usr/local/bin/create-diretta-cache.sh
EOT

# Skript einmal manuell ausführen
sudo /usr/local/bin/create-diretta-cache.sh
Teil 2: Diretta Host KonfigurationNun führen wir auf dem Diretta Host alle Schritte durch, um die
Webanwendung zu installieren und zu konfigurieren. Sie sollten für diesen gesamten Abschnitt als audiolinux
Benutzer eingeloggt sein.SSH zum Diretta Host:ssh diretta-host
Dedizierten SSH Key generieren:Dies erstellt ein neues SSH-Schlüsselpaar speziell für die Web-App. Es wird
keine Passphrase haben.ssh-keygen -t ed25519 -f ~/.ssh/purist_app_key -N "" -C "purist-app-key"
Schlüssel auf das Target kopieren:Dieser Schritt kopiert den Public Key sicher auf das Target.echo "---
Autorisiere den neuen SSH Key auf dem Diretta Target ---"

# Schritt A: Public Key in das Home-Verzeichnis des Targets kopieren
echo "--> Kopiere Public Key zum Target..."
scp -o StrictHostKeyChecking=accept-new ~/.ssh/purist_app_key.pub diretta-target:
Schlüssel auf dem Target autorisieren:ssh diretta-target

Sobald Sie auf dem Target eingeloggt sind, führen Sie dieses Skript aus, um den Schlüssel für den
'purist-app' Benutzer einzurichtenecho "--> Führe Setup-Skript auf dem Target aus..."
set -e
# Public Key aus der Datei lesen, die wir gerade kopiert haben
PUB_KEY=$(cat purist_app_key.pub)

# Sicherstellen, dass das .ssh Verzeichnis existiert und korrekte Rechte hat
sudo mkdir -p /home/purist-app/.ssh
sudo chmod 0700 /home/purist-app/.ssh

# authorized_keys Datei mit den erforderlichen Sicherheitsbeschränkungen erstellen
echo "command=\"sudo
\$SSH_ORIGINAL_COMMAND\",from=\"172.20.0.1\",no-port-forwarding,no-x11-forwarding,no-agent-forwarding,no-pty
${PUB_KEY}" | sudo tee /home/purist-app/.ssh/authorized_keys > /dev/null

# Finale Eigentümerschaft und Rechte setzen
sudo chown -R purist-app:purist-app /home/purist-app/.ssh
sudo chmod 0600 /home/purist-app/.ssh/authorized_keys

# Kopierte Public Key Datei aufräumen
rm purist_app_key.pub

echo "✅ SSH Key wurde erfolgreich auf dem Target autorisiert."
Remote-Befehle manuell testen (Empfohlen):Bevor Sie die Web-App starten, testen Sie jeden Remote-Befehl vom
Terminal des Diretta Hosts, um zu bestätigen, dass das Backend funktioniert.# Status-Befehl testen (sollte
JSON-String zurückgeben)
ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-status'

# Purist-Modus umschalten testen (zweimal ausführen: an, dann aus)
ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-toggle-mode'

# Auto-Start beim Boot umschalten testen (zweimal ausführen: aktivieren, dann deaktivieren)
ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-toggle-auto'

# Abrufen der Diretta Target Lizenz-URL testen
ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-license-url'

# Neustart des Diretta Target Dienstes testen
ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-restart-target'
Python via pyenv installieren auf dem Diretta Host (überspringen Sie dies gerne, wenn Sie es schon für die
IR-Fernbedienung erledigt haben)Installieren Sie pyenv und die neueste stabile Python-Version.#
Build-Abhängigkeiten installieren
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline
util-linux db gdbm sqlite vim jq

# pyenv nur installieren, wenn es nicht bereits installiert ist
if [ ! -d "$HOME/.pyenv" ]; then
  echo "--- Installiere pyenv ---"
  curl -fsSL [https://pyenv.run](https://pyenv.run) | bash
else
  echo "--- pyenv ist bereits installiert. Überspringe Installation. ---"
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

# Datei sourcen, um pyenv in der aktuellen Shell verfügbar zu machen
. ~/.bashrc

# Neueste Python-Version installieren und setzen, falls nicht bereits vorhanden
PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
  echo "--- Installiere Python ${PYVER}. Dies wird einige Minuten dauern... ---"
  pyenv install $PYVER
else
  echo "--- Python ${PYVER} ist bereits installiert. Überspringe Installation. ---"
fi

# Globale Python-Version setzen
pyenv global $PYVER
Hinweis: Es ist normal, dass der Teil Installing Python-3.14.2... ca. 10 Minuten dauert, da Python aus dem
Quellcode kompiliert wird. Geben Sie nicht auf! Entspannen Sie sich bei guter Musik über Ihre neue
Diretta-Zone in Roon, während Sie warten. Sie sollte verfügbar sein, während Python auf dem Host installiert
wird.Avahi und Python-Abhängigkeiten auf dem Diretta Host installieren:Hinweis: OPTIONAL - Wenn Sie mehr als
einen Diretta Host in Ihrem Netzwerk haben, stellen Sie sicher, dass sie eindeutige Namen haben. Sie können
einen Befehl wie den folgenden nutzen, um diesen hier umzubenennen, bevor Sie fortfahren:# Diretta Host
optional umbenennen, falls dies Ihr zweiter Aufbau im selben Netzwerk ist
sudo hostnamectl set-hostname diretta-host2
Dieser Schritt läuft auf dem Diretta Host. Er installiert den Avahi-Daemon und nutzt eine requirements.txt
Datei, um Flask in einer dedizierten virtuellen Umgebung zu installieren.# Avahi für .local Namensauflösung
installieren
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm avahi

# Dynamisch den USB-Ethernet-Interface-Namen finden (z.B. enp... oder enu1...)
USB_INTERFACE=$(ip -o link show | awk -F': ' '/en[pu]/{print $2}')

# Konfigurations-Override erstellen, um Avahi auf das USB-Interface zu isolieren
echo "--- Konfiguriere Avahi für Interface: $USB_INTERFACE ---"
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
echo "--- Richte Python-Umgebung für Web UI ein ---"
# Virtuelle Umgebung erstellen, nur wenn sie nicht existiert
if ! pyenv versions --bare | grep -q "^purist-webui$"; then
  echo "--- Erstelle 'purist-webui' virtuelle Umgebung ---"
  pyenv virtualenv purist-webui
else
  echo "--- 'purist-webui' virtuelle Umgebung existiert bereits ---"
fi
pyenv activate purist-webui
pip install -r ~/purist-mode-webui/requirements.txt
pyenv deactivate
Flask App installieren:Laden Sie das Python-Skript direkt von GitHub in das Anwendungsverzeichnis auf dem
Diretta Host.curl -L
[https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py](https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py)
-o ~/purist-mode-webui/app.py
Port-Binding Fähigkeit gewährenWir müssen der Python-Executable die Erlaubnis geben, auf Port 80 am Diretta
Host zu binden, damit unsere Web-App starten kann.# Paket installieren, das den 'setcap' Befehl bereitstellt
sudo pacman -S --noconfirm --needed libcap

# Den echten Pfad zur Python-Executable finden und alle symbolischen Links auflösen
PYTHON_EXEC=$(readlink -f /home/audiolinux/.pyenv/versions/purist-webui/bin/python)

# Port-Binding Fähigkeit direkt der finalen Python-Executable gewähren
echo "Wende Capability auf echte Datei an: ${PYTHON_EXEC}"
sudo setcap 'cap_net_bind_service=+ep' "$PYTHON_EXEC"
Sudo-Berechtigungen auf dem Host gewähren:Dieser Schritt ist kritisch, um der Webanwendung zu erlauben, die
nötigen Roon-bezogenen Dienste ohne Passwort neu zu starten.cat <<'EOT' | sudo tee
/etc/sudoers.d/webui-restarts
# Der WebUI (läuft als audiolinux) erlauben, benötigte Dienste neu zu starten
audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roon-ir-remote.service
audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roonbridge.service
EOT
sudo chmod 0440 /etc/sudoers.d/webui-restarts
Flask App interaktiv testen:Starten Sie nun die App von der Kommandozeile auf dem Diretta Host, um
sicherzustellen, dass sie korrekt startet.cd ~/purist-mode-webui
pyenv activate purist-webui
python app.py
Sie sollten eine Ausgabe sehen, dass der Flask-Server auf Port 8080 gestartet ist. Greifen Sie von einem
anderen Gerät auf http://diretta-host.local:8080 zu. Wenn es funktioniert, kehren Sie zum SSH-Terminal
zurück und drücken Ctrl+C, um den Server zu stoppen.systemd Service erstellen:Dieser Dienst führt die
Web-App automatisch auf dem Diretta Host aus, unter Verwendung der korrekten Python-Executable aus unserer
pyenv virtuellen Umgebung.cat <<EOT | sudo tee /etc/systemd/system/purist-webui.service
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
Web-App aktivieren und starten:sudo systemctl daemon-reload
sudo systemctl enable --now purist-webui.service
Logs kurz beobachten:journalctl -b -u purist-webui.service -f
Web UI mit der finalen URL testen:Öffnen Sie einen Browser unter http://diretta-host.local und beobachten
Sie die Logs auf Fehler.Tippen Sie CTRL-C, sobald Sie zufrieden sind, dass alles wie erwartet läuft.Zugriff
auf die Web UIAlles erledigt! Öffnen Sie einen Webbrowser auf Ihrem Telefon, Tablet oder Computer, der mit
demselben Netzwerk wie der Diretta Host verbunden ist. Navigieren Sie zur
Haupt-Landingpage:http://diretta-host.localEin Hinweis zu Browser-SicherheitswarnungenWenn Sie
https://www.google.com/search?q=http://diretta-host.local zum ersten Mal besuchen, zeigt Ihr Browser
wahrscheinlich eine Sicherheitswarnung an, dass die Verbindung nicht sicher sei. Das ist erwartet und sicher
zu umgehen. Die Warnung erscheint, weil die Verbindung Standard-HTTP statt verschlüsseltes HTTPS nutzt –
eine bewusste Entscheidung, um den Rechenaufwand auf dem Audiogerät zu minimieren. Da die App nur in Ihrem
privaten Heimnetzwerk läuft und keine sensiblen Daten verarbeitet, können Sie getrost auf "Weiter zur Seite"
klicken.Von der Landingpage aus führt Sie eine Navigationsleiste oben zu den verschiedenen
Bedienfeldern:Home: Die Haupt-Landingpage mit Links zu den verschiedenen Anwendungen.Purist Mode App: Diese
Seite enthält die Steuerungen zum Umschalten des Purist-Modus und dessen Auto-Start-Verhalten auf dem
Diretta Target. Sie aktualisiert sich automatisch alle 30 Sekunden, um den aktuellen Status anzuzeigen. Sie
enthält auch den "Restart Services" Knopf für die Nutzung nach einer Diretta-Lizenzaktivierung.IR Remote
App: Wenn Sie das IR-Fernbedienungs-Setup (Anhang 2) abgeschlossen haben, erscheint dieser Link. Diese Seite
bietet ein einfaches Formular, um den Roon-Zonennamen zu sehen und zu aktualisieren, den Ihre Fernbedienung
steuert. Diese Seite aktualisiert sich nicht automatisch, Sie können sich also Zeit lassen für Ihre
Änderungen.✅ Checkpoint: Web UI Setup verifizierenDie Purist Mode Web UI sollte nun betriebsbereit sein. Um
alle Komponenten dieses komplexen Features zu verifizieren, gehen Sie zu Anhang 5 und führen Sie den
universellen System Health Check Befehl auf Host und Target aus.14. Anhang 5: System-Gesundheitscheck
(Health Checks)Nach Abschluss der Hauptabschnitte dieses Leitfadens ist es eine gute Idee, einen schnellen
Qualitätssicherungs-Check (QA) durchzuführen, um zu verifizieren, dass alles korrekt konfiguriert ist.Wir
haben ein intelligentes Skript erstellt, das automatisch erkennt, ob Sie es auf dem Diretta Host oder dem
Diretta Target ausführen, und den entsprechenden Satz an Prüfungen durchführt.Wie man den Check
ausführtFühren Sie auf Host oder Target den folgenden einzelnen Befehl aus. Er lädt das QA-Skript herunter,
führt es aus und liefert einen detaillierten Bericht über Ihren Systemstatus.curl -fsSL
[https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh](https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh)
| sudo bash
15. Anhang 6: Fortgeschrittenes Echtzeit-LeistungstuningDie folgenden Schritte sind optional, aber empfohlen
für Nutzer, die das absolute Maximum an Leistung aus ihrem Diretta-Setup herausholen wollen. Die Strategie,
basierend auf Ratschlägen von AudioLinux-Autor Piero, besteht darin, die stabilste und elektrisch ruhigste
Umgebung wie möglich auf Host und Target zu schaffen.Dies wird erreicht durch CPU-Isolierung, um spezifische
Prozessorkerne für Audioaufgaben zu reservieren und sie vom Betriebssystem abzuschirmen, sowie durch
sorgfältiges Tuning der Echtzeit-Prioritäten, um sicherzustellen, dass der Audiodatenpfad niemals
unterbrochen wird.Hinweis: Dies ist ein fortgeschrittener Tuning-Prozess. Bitte stellen Sie sicher, dass Ihr
Kern-Diretta-System voll funktionsfähig ist, indem Sie die Sektionen 1-9 des Hauptleitfadens abschließen,
bevor Sie fortfahren. Angemessene Kühlung für beide Raspberry Pi Geräte ist essenziell.Teil 1: Optimierung
des Diretta TargetsDas Ziel für das Target ist es, es zu einem reinen, latenzarmen Audio-Endpunkt zu machen.
Wir werden die Diretta-Anwendung auf einem einzelnen, dedizierten CPU-Kern isolieren und ihr eine hohe, aber
nicht übermäßige Echtzeit-Priorität geben.Schritt 6.1: Einen CPU-Kern für die Audioanwendung isolierenDieser
Schritt widmet einen CPU-Kern exklusiv der Diretta Target Anwendung.SSH zum Diretta Target:ssh diretta-target
AudioLinux Menüsystem betreten:menu
Navigieren Sie zum ISOLATED CPU CORES configuration Menü (unter SYSTEM menu).Deaktivieren Sie vorherige
Einstellungen wie unten gezeigt:Please chose your option:
1) Configure and enable
2) Disable
3) Exit
?
2

ISOLATED CORES has been reset

IRQ balancer was disabled
It can be enabled in Expert menu

PRESS RETURN TO EXIT
Navigieren Sie zurück zum ISOLATED CPU CORES configuration Menü (unter SYSTEM menu). Folgen Sie den
Anweisungen exakt wie unten gezeigt, um Kerne 2 und 3 zu isolieren und die Diretta-Anwendung
zuzuweisen.Please chose your option:
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
Nach Abschluss drücken Sie ENTER, um zum Systemmenü zurückzukehren. Noch nicht neu starten.Eine Anmerkung
zur automatischen IRQ-Affinität: Sie bemerken vielleicht, dass das Skript meldet, dass es auch die end0
Netzwerk-IRQs auf denselben Kern isoliert hat. Das ist kein Fehler, sondern eine intelligente Optimierung.
Das Skript pint die Netzwerk-Interrupts automatisch auf denselben Kern wie die Anwendung, die das Netzwerk
nutzt, und schafft so den effizientesten Datenpfad.Schritt 6.2: Echtzeit-Priorität setzenAls nächstes geben
wir der Diretta-Anwendung eine "nicht zu hohe" Priorität, um sicherzustellen, dass sie flüssig läuft, ohne
die kritischeren USB-Audio-Interrupts zu stören.Ebenfalls unter SYSTEM menu, navigieren Sie zum REALTIME
PRIORITY configuration Menü.Wählen Sie Option 3) Configure IRQ priority.Folgen Sie den Anweisungen, um eine
Standard-IRQ-Priorität sicherzustellenDo you want to set the IRQ priority for each device? (1/2)
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
Wählen Sie Option 4) Configure APPLICATION priority.Folgen Sie den Anweisungen, um eine manuelle Priorität
von 70 zu setzen....
Type Y if you want to edit it
?
[PRESS ENTER]

Here you will configure the max. priority given to audio applications...
?70

Now you can configure your preferred method...
?manual
Nach Bestätigung der Änderungen wählen Sie 5) Exit und kehren zur Kommandozeile zurück.Starten Sie das
Diretta Target neu, damit alle Änderungen wirksam werden.sudo sync && sudo reboot
Teil 2: Optimierung des Diretta HostsDas Ziel für den Host ist es, Roon Bridge und dem Diretta-Dienst
dedizierte Verarbeitungsressourcen zu geben, aber ohne hohe Echtzeit-Prioritäten zu nutzen. CPU-Isolierung
ist hier das mächtigere Werkzeug, da es verhindert, dass Prozesse überhaupt unterbrochen werden.Schritt 6.3:
CPU-Kerne für Audioanwendungen isolierenDieser Schritt widmet zwei CPU-Kerne sowohl Roon Bridge als auch dem
Diretta Host Dienst.SSH zum Diretta Host:ssh diretta-host
AudioLinux Menüsystem betreten:menu
Navigieren Sie zum ISOLATED CPU CORES configuration Menü (unter SYSTEM menu).Deaktivieren Sie vorherige
Einstellungen wie unten gezeigt:Please chose your option:
1) Configure and enable
2) Disable
3) Exit
?
2

ISOLATED CORES has been reset

IRQ balancer was disabled
It can be enabled in Expert menu

PRESS RETURN TO EXIT
Navigieren Sie zurück zum ISOLATED CPU CORES configuration Menü (unter SYSTEM menu). Folgen Sie den
Anweisungen, um Kerne 2 und 3 zu isolieren und die relevanten Anwendungen zuzuweisen.Please chose your option:
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
Nach Abschluss drücken Sie ENTER, um zum Systemmenü zurückzukehren. Noch nicht neu starten.Schritt 6.4:
Anwendungs-Echtzeit-Priorität deaktivierenDa unsere Audioanwendungen auf dedizierten Kernen laufen, müssen
sie nicht mehr um CPU-Zeit konkurrieren. Eine hohe Echtzeit-Priorität zu erzwingen ist nun unnötig und kann
kontraproduktiv sein. Wir werden den Dienst auf dem Host komplett deaktivieren.Ebenfalls unter SYSTEM menu,
navigieren Sie zum REALTIME PRIORITY configuration Menü.Wählen Sie Option 2) Enable/disable APPLICATION
service (rtapp). Dies wird den Dienst sofort deaktivieren.Wählen Sie 5) Exit und kehren zur Kommandozeile
zurück.Starten Sie den Diretta Host neu.sudo sync && sudo reboot
Schritt 6.5: Diretta CycleTime reduzierenMit den Echtzeit-Kernel-Optimierungen kann der Diretta Host nun ein
aggressiveres Paketintervall handhaben, was zu verbesserter Klangqualität führen kann. Dieser letzte Schritt
reduziert den CycleTime Parameter von 800 auf 514 Mikrosekunden. Diese kleinere Zeitlücke zwischen Paketen
stellt sicher, dass alle Inhalte bis DSD256 und DXD (32-bit, 352.8 kHz) nur ein Paket pro Zyklus
benötigen.SSH zum Diretta Host, falls Sie nicht noch eingeloggt sind.Führen Sie folgenden Befehl aus, um die
optimierte Einstellung anzuwenden:cat <<'EOT' | sudo tee /opt/diretta-alsa/setting.inf
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
Starten Sie den Diretta Dienst neu, damit die Änderung wirksam wird:sudo systemctl restart
diretta_alsa.service
✅ Checkpoint: Echtzeit-Tuning verifizierenIhr fortgeschrittenes Echtzeit-Tuning sollte nun abgeschlossen
sein. Um alle Komponenten dieser neuen Konfiguration zu verifizieren, kehren Sie bitte zu Anhang 5 zurück
und führen Sie den universellen System Health Check Befehl auf Host und Target aus.16. Anhang 7:
CPU-Optimierung mit ereignisgesteuerten HooksDieser Anhang bietet eine fortgeschrittene Optimierung, um
System-Jitter und unnötige CPU-Aktivität weiter zu reduzieren.Die Standard-AudioLinux-Konfiguration
beinhaltet Hintergrund-"Timer" (z.B. isolated_app.timer, rtapp.timer), die Tuning-Skripte einmal pro Minute
ausführen. Obwohl effektiv, verursachen diese Timer periodische CPU-Spitzen, was unserem Ziel eines ruhigen,
stabilen Systems widerspricht.Dieser Leitfaden ersetzt dieses "periodische" Verhalten durch ein
"ereignisgesteuertes". Wir werden die Timer deaktivieren und stattdessen systemd Drop-in Dateien nutzen, um
diese Tuning-Skripte nur einmal auszuführen, wenn die Audio-Hauptdienste starten. Dieser "Set it and forget
it"-Ansatz eliminiert die minütlichen CPU-Spitzen vollständig.Teil 1: Optimierung des Diretta TargetsAuf dem
Target deaktivieren wir sowohl isolated_app.timer als auch rtapp.timer und hängen ihre Skripte in den
diretta_alsa_target.service ein.SSH zum Diretta Target:ssh diretta-target
Timer stoppen und deaktivieren:Dieser Befehl stoppt die Timer dauerhaft und entfernt ihre
Auto-Start-Verknüpfungen.sudo systemctl stop isolated_app.timer rtapp.timer
sudo systemctl disable isolated_app.timer rtapp.timer
Systemd Drop-in Hook erstellen:Dieser Befehl erstellt eine neue Konfigurationsdatei, die systemd anweist,
die zwei Skripte auszuführen, nachdem der Hauptdienst diretta_alsa_target.service gestartet ist.#
Verzeichnis erstellen
sudo mkdir -p /etc/systemd/system/diretta_alsa_target.service.d/

# Drop-in Datei erstellen
sudo bash -c 'cat <<EOF > /etc/systemd/system/diretta_alsa_target.service.d/10-local-hooks.conf
[Service]
ExecStartPost=sleep 1.5
ExecStartPost=/opt/scripts/system/isolated_app.sh
ExecStartPost=-/bin/bash /usr/bin/rtapp
EOF'
Hinweis zum Bindestrich (-):Das Präfix - vor dem /bin/bash /usr/bin/rtapp Befehl ist Absicht. Das rtapp
Skript könnte in diesem Kontext fehlschlagen (mit einem Non-Zero Status beenden). Der Bindestrich sagt
systemd, dass es einen "Fehler ignorieren" soll für diesen spezifischen Befehl, damit der Hauptdienst
diretta_alsa_target.service weiterlaufen kann.Systemd neu laden und Dienst neustarten:sudo systemctl
daemon-reload
sudo systemctl restart diretta_alsa_target.service
Änderungen verifizieren:systemctl status diretta_alsa_target.service
In der Ausgabe sollten Sie sehen, dass der Dienst Active: active (running) ist. Sie sollten auch zwei
Process: Zeilen sehen, eine für isolated_app.sh (sollte status=0/SUCCESS zeigen) und eine für rtapp (wird
wahrscheinlich status=1/FAILURE zeigen). Das ist das korrekte und erwartete Ergebnis.Teil 2: Optimierung des
Diretta HostsAuf dem Host deaktivieren wir den isolated_app.timer und hängen sein Skript sowohl in
roonbridge.service als auch diretta_alsa.service ein. Dies stellt sicher, dass die Optimierungen angewendet
werden, egal welcher Dienst zuerst startet.SSH zum Diretta Host:ssh diretta-host
Timer stoppen und deaktivieren:sudo systemctl stop isolated_app.timer
sudo systemctl disable isolated_app.timer
Systemd Drop-in Hooks erstellen:Wir müssen zwei separate Drop-in Dateien erstellen, eine für jeden
Dienst.Für roonbridge.service:# Verzeichnis erstellen
sudo mkdir -p /etc/systemd/system/roonbridge.service.d/

# Drop-in Datei erstellen
sudo bash -c 'cat <<EOF > /etc/systemd/system/roonbridge.service.d/10-local-hooks.conf
[Service]
ExecStartPost=/opt/scripts/system/isolated_app.sh
EOF'
Für diretta_alsa.service:# Verzeichnis erstellen
sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d/

# Drop-in Datei erstellen
sudo bash -c 'cat <<EOF > /etc/systemd/system/diretta_alsa.service.d/10-local-hooks.conf
[Service]
ExecStartPost=/opt/scripts/system/isolated_app.sh
EOF'
Systemd neu laden und Dienste neustarten:sudo systemctl daemon-reload
sudo systemctl restart roonbridge.service
sudo systemctl restart diretta_alsa.service
Änderungen verifizieren:Prüfen Sie den Status beider Dienste.systemctl status roonbridge.service
systemctl status diretta_alsa.service
Bei beiden Diensten sollten Sie Active: active (running) und eine Process: Zeile für isolated_app.sh sehen,
die status=0/SUCCESS zeigt.✅ Checkpoint: CPU-Optimierungen verifizierenIhr System ist nun so optimiert,
dass Tuning-Skripte nur beim Boot laufen, was periodische CPU-Spitzen eliminiert. Um zu verifizieren, dass
diese neue Konfiguration korrekt mit dem Rest des Systems arbeitet, kehren Sie bitte zu Anhang 5 zurück und
führen Sie den universellen System Health Check Befehl auf Host und Target aus.17. Anhang 8: Optionaler
Purist 100Mbps Netzwerk-ModusZiel: Elektrisches Rauschen reduzieren und die Präzision des OS-Schedulers
verbessern, indem die dedizierte Netzwerkverbindung auf 100 Mbps begrenzt und Energy Efficient Ethernet
(EEE) explizit deaktiviert wird.Obwohl kontraintuitiv, kann die Reduzierung der Verbindungsgeschwindigkeit
von 1 Gbit/s auf 100 Mbit/s auf der dedizierten Verbindung (end0) die Klangqualität verbessern. Die
niedrigere Betriebsfrequenz von 100BASE-TX (31,25 MHz vs 62,5 MHz) erzeugt weniger RFI. Zudem verhindert das
Deaktivieren von EEE, dass die Verbindung in Schlafzustände wechselt, was potenzielle Latenzspitzen
("Flapping") eliminiert und felsenfeste Stabilität auf Raspberry Pi 5 Hardware gewährleistet.Hinweis: Sie
sehen möglicherweise "buffer low" Warnungen in den Target Logs (LatencyBuffer fällt auf 1). Dies ist
normales Verhalten aufgrund der erhöhten Serialisierungslatenz der langsameren Verbindung und verursacht
keine hörbaren Aussetzer.Schritt 1: Den Host konfigurieren (Geschwindigkeitslimit)Wir erstellen einen Dienst
auf dem Host, der ihn zwingt, nur 100 Mbps Full Duplex anzubieten. Das Target wird dies automatisch erkennen
und sich anpassen.Restriktionsdienst erstellen: (Nur auf Host ausführen)cat <<'EOT' | sudo tee
/etc/systemd/system/limit-speed-100m.service
[Unit]
Description=Limit end0 advertisement to 100Mbps for Audio Purity
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecCondition=/usr/bin/ip link show end0
# Auto-Neg aktivieren aber strikt auf 100Mbps/Full begrenzen
ExecStart=/usr/bin/ethtool -s end0 speed 100 duplex full autoneg on
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

echo "Dienst aktivieren und starten:"
sudo systemctl daemon-reload
sudo systemctl enable --now limit-speed-100m.service
Schritt 2: Host und Target konfigurieren (EEE deaktivieren)Energy Efficient Ethernet (EEE) kann bei manchen
Hardwarekombinationen zu Verbindungsinstabilität führen. Wir erstellen einen Dienst, um es auf beiden, Host
und Target, explizit zu deaktivieren, um konsistentes Verhalten zu gewährleisten.Deaktivierungsdienst
erstellen: (Auf BEIDEN Host und Target ausführen)cat <<'EOT' | sudo tee
/etc/systemd/system/disable-eee.service
[Unit]
Description=Disable EEE on end0 for Link Stability
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecCondition=/usr/bin/ip link show end0
# EEE explizit deaktivieren (Fehler ignorieren falls vom Treiber nicht unterstützt)
ExecStart=-/usr/bin/ethtool --set-eee end0 eee off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

echo "Dienst aktivieren und starten:"
sudo systemctl daemon-reload
sudo systemctl enable --now disable-eee.service
Schritt 3: Target markieren (Für QA)Um sicherzustellen, dass das Target QA Skript weiß, dass es diese
spezifische Konfiguration validieren soll, erstellen wir eine Markierungsdatei auf dem Target:sudo touch
/etc/diretta-100m
Hinweis zur Wiedergabelatenz:Sie bemerken eventuell eine leichte Erhöhung der Verzögerung zwischen dem
Drücken von "Play" und dem Hören von Musik (bis zu ca. 1 Sekunde). Dies ist erwartetes Verhalten. Durch die
Begrenzung auf 100 Mbps drosseln wir absichtlich den anfänglichen Daten-Burst, um sicherzustellen, dass die
Verbindung auf einer niedrigeren, ruhigeren Frequenz arbeitet. Das System tauscht sofortige Startzeiten
gegen einen stabileren, rauschärmeren Dauerzustand während der Wiedergabe.✅ Checkpoint:
Netzwerkkonfiguration verifizierenIhre dedizierte Netzwerkverbindung ist nun für den "Purist" 100Mbps
Betrieb konfiguriert. Um zu verifizieren, dass der Host-Dienst aktiv ist und das Target die Geschwindigkeit
korrekt ausgehandelt hat (erkannt via Marker-Datei), kehren Sie bitte zu Anhang 5 zurück und führen Sie den
universellen System Health Check Befehl auf Host und Target aus.18. Anhang 9: Optional: Jumbo Frames
OptimierungDieser Abschnitt optimiert den Transport für hohe Bandbreiteneffizienz.Schritt 1: Schnittstellen
vorbereitenWir müssen die Netzwerkschnittstellen temporär auf MTU 9000 zwingen, um Kernel-Support zu
verifizieren und für den Verbindungstest vorzubereiten.Führen Sie dies zuerst auf dem Target, dann auf dem
Host aus:sudo sh -c 'ip link set end0 down; sleep 2; ip link set end0 mtu 9000; ip link set end0 up'
end0_mtu=$(ip link show dev end0 | awk '/mtu/ {print $5}')
if [[ "9000" == "$end0_mtu" ]]; then
  echo "ERFOLG: Kernel unterstützt Jumbo Frames. Weiter zu Schritt 2."
else
  echo "STOP: Ihr Kernel scheint keine Jumbo Frames zu unterstützen."
fi
Wenn Sie "STOP" auf entweder Host oder Target sehen, fahren Sie nicht fort. Ihrem Kernel fehlt der benötigte
Patch.Schritt 2: Automatisierte Target-KonfigurationSSH ins Target (diretta-target) und folgenden Block
einfügen.# 1. Verbindungslimit erkennen (Full vs Baby)
echo "Teste Verbindungskapazität..."
if ping -c 1 -w 1 -M do -s 8972 host &>/dev/null; then
  NEW_MTU=9000
  echo "ERFOLG: Full Jumbo Frames (9000 MTU) unterstützt."
elif ping -c 1 -w 1 -M do -s 2004 host &>/dev/null; then
  NEW_MTU=2032
  echo "ERFOLG: Baby Jumbo Frames (2032 MTU) unterstützt."
else
  echo "FEHLER: Verbindung kann keine Jumbo Frames unterstützen. Setze auf sichere Standards zurück."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Systemnetzwerkkonfiguration anwenden
  echo "Konfiguriere /etc/systemd/network/end0.network..."
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

  # 3. Diretta Config anwenden
  echo "Konfiguriere Diretta Target..."
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
  echo "FERTIG: Target Optimierung komplett."
}

Schritt 3: Automatisierte Host-KonfigurationSSH in den Host (diretta-host) und folgenden Block einfügen. Er
prüft die Verbindung, konfiguriert die permanenten Netzwerkeinstellungen und aktualisiert Diretta.# 1.
Verbindungslimit erkennen (Full vs Baby)
echo "Teste Verbindungskapazität..."
# Der Verbindung einen Moment geben nach dem manuellen MTU Wechsel
sleep 2

if ping -c 1 -w 1 -M do -s 8972 target &>/dev/null; then
  NEW_MTU=9000
  echo "ERFOLG: Full Jumbo Frames (9000 MTU) unterstützt."
elif ping -c 1 -w 1 -M do -s 2004 target &>/dev/null; then
  NEW_MTU=2032
  echo "ERFOLG: Baby Jumbo Frames (2032 MTU) unterstützt."
else
  echo "FEHLER: Verbindung kann keine Jumbo Frames unterstützen. Setze auf sichere Standards zurück."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Systemnetzwerkkonfiguration anwenden
  echo "Konfiguriere /etc/systemd/network/end0.network..."
  cat <<EOF | sudo tee /etc/systemd/network/end0.network
[Match]
Name=end0

[Link]
MTUBytes=$NEW_MTU

[Network]
Address=172.20.0.1/24
EOF
  sudo networkctl reload

  # 3. Diretta Config anwenden
  echo "Konfiguriere Diretta Host..."

  # Immer FlexCycle für Jumbo Frames aktivieren für Stabilität
  sudo sed -i 's/^FlexCycle=.*/FlexCycle=enable/' /opt/diretta-alsa/setting.inf

  # Konditionale CycleTime Optimierung
  if [ "$NEW_MTU" -eq 9000 ]; then
    echo "Optimierung: Full Jumbo Frames erkannt. Entspanne CycleTime auf 1000us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=1000/' /opt/diretta-alsa/setting.inf
  else
    echo "Optimierung: Baby Jumbo Frames erkannt. Setze CycleTime auf 700us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=700/' /opt/diretta-alsa/setting.inf
  fi

  sudo systemctl restart diretta_alsa
  echo "FERTIG: Host Optimierung komplett."
}
Schritt 4: Neustart zum Übernehmen der MTU-ÄnderungenStarten Sie zuerst das Target neu, dann den Host:sudo
sync && sudo reboot
✅ Checkpoint: Netzwerkkonfiguration verifizierenWenn Sie den Jumbo-Frames-Support für Ihre Konfiguration
aktivieren konnten, ist jetzt ein guter Zeitpunkt, zu Anhang 5 zurückzukehren und den universellen System
Health Check Befehl auf Host und Target auszuführen.
