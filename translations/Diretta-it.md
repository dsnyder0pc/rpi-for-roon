# Creazione di un collegamento Diretta dedicato con AudioLinux su Raspberry Pi

Questa guida fornisce istruzioni dettagliate passo-passo per configurare due dispositivi Raspberry Pi come Diretta Host e Diretta Target dedicati. Questa configurazione utilizza una connessione Ethernet diretta point-to-point tra i due dispositivi per ottenere il massimo isolamento di rete e prestazioni audio.

Il **Diretta Host** si collegherà alla rete principale (per accedere al server musicale) e fungerà anche da gateway per il Target. Il **Diretta Target** si collegherà solo all'Host e al vostro DAC o DDC USB.

## Gestione delle versioni

L'obiettivo è mantenere questa guida compatibile con il link di download ufficiale di AudioLinux attualmente fornito da Piero.

**Validazione attuale:**
Queste istruzioni sono state testate l'ultima volta con **AudioLinux V5** (Immagine: `audiolinux_pi4-pi5_520`, Versione Menu: `536`).

**Nota sugli aggiornamenti:**
Poiché AudioLinux è basato su Arch (una rolling release), una nuova installazione scaricherà sempre l'ultima versione assoluta del software. Una volta che il sistema è configurato e funzionante, avete due scelte:

1.  **Aggiornare frequentemente:** Impegnarsi ad aggiornare almeno mensilmente in modo da poter risolvere piccoli problemi non appena si verificano.
2.  **Bloccare la configurazione (Consigliato):** Se suona bene, non toccarlo. Create un'immagine di backup e godetevi la musica!

## Introduzione all'architettura Roon di riferimento

Benvenuti nella guida definitiva per la costruzione di un endpoint di streaming Roon allo stato dell'arte. Sebbene AudioLinux supporti altri protocolli, per questa build userò Roon come esempio. È possibile utilizzare il sistema di menu sul Diretta Host per installare il supporto per altri protocolli, tra cui HQPlayer, Audirvana, DLNA, AirPlay, ecc. Prima di immergersi nelle istruzioni passo-passo, è importante comprendere il "perché" di questo progetto. Questa introduzione spiegherà il problema che questa architettura risolve, perché è fondamentalmente superiore a molte costose alternative commerciali e come questo progetto fai-da-te rappresenti una via diretta e gratificante per sbloccare la massima qualità sonora dal vostro sistema Roon.

### Il paradosso di Roon: un'esperienza potente con un avvertimento sonoro

Roon è celebrato, quasi universalmente, come il sistema di gestione musicale più potente e coinvolgente disponibile. I suoi ricchi metadati e l'esperienza d'uso fluida sono impareggiabili. Tuttavia, questa supremazia funzionale è da tempo perseguitata da una critica persistente da parte di un segmento esplicito della comunità audiofila: ovvero che la qualità sonora di Roon possa essere compromessa, spesso descritta come "piatta, opaca e priva di vita" rispetto ad altri player.

Questo "Suono Roon" non è un mito, né è un difetto del software bit-perfect di Roon. È un potenziale sintomo della natura potente e ad alta intensità di risorse di Roon. Il Core "pesante" di Roon richiede una potenza di calcolo significativa, che a sua volta genera rumore elettrico (RFI/EMI). Quando il computer che esegue il Roon Core si trova in prossimità del vostro sensibile convertitore digitale-analogico (DAC), questo rumore può contaminare lo stadio di uscita analogico, mascherando i dettagli, restringendo la scena sonora e privando la musica della sua vitalità.

---

### Andare oltre le "soluzioni tampone" verso una soluzione fondamentale

La stessa Roon Labs raccomanda un'architettura "a due telai" per risolvere questo problema primario: separare l'impegnativo **Roon Core** da un leggero **Endpoint** di rete (chiamato anche trasporto di streaming). Questo è il primo passo corretto, in quanto sposta l'elaborazione pesante su una macchina remota, isolando il suo rumore dal rack audio.

Tuttavia, anche in questo design superiore a due livelli, rimane un problema più sottile. I protocolli di rete standard, incluso lo stesso RAAT di Roon, trasmettono i dati audio in "burst" (raffiche) intermittenti. Questo costringe la CPU dell'endpoint a picchi costanti di attività per elaborare queste raffiche, causando rapide fluttuazioni nel consumo di corrente. Queste fluttuazioni generano a loro volta rumore elettrico a bassa frequenza proprio sull'endpoint, il componente più vicino al DAC.

I produttori di audio high-end cercano di combattere i *sintomi* di questo traffico a raffiche con varie soluzioni tampone: enormi alimentatori lineari per gestire meglio i picchi di corrente, CPU a bassissimo consumo per ridurre l'intensità dei picchi e stadi di filtraggio extra per pulire il rumore risultante. Sebbene queste strategie possano aiutare, non affrontano la causa alla radice del rumore: l'elaborazione a raffiche stessa.

Questa guida presenta una soluzione più elegante e decisamente più efficace. Invece di cercare di ripulire il rumore, costruiremo un'architettura che impedisce al rumore di essere generato fin dall'inizio.

---

### L'architettura a tre livelli: Roon + Diretta

Questo progetto evolve la configurazione a due telai raccomandata da Roon in un sistema definitivo a tre livelli che fornisce molteplici strati di isolamento combinati.

1.  **Tier 1: Roon Core**: Il vostro potente server Roon gira su una macchina dedicata, posizionata lontano dalla stanza d'ascolto. Svolge tutto il lavoro pesante e il suo rumore elettrico viene mantenuto isolato dall'impianto audio.
2.  **Tier 2: Diretta Host**: Il primo Raspberry Pi della nostra build funge da **Diretta Host**. Si collega alla rete principale, riceve il flusso audio dal Roon Core e poi lo trasmette in segmenti minuscoli e temporizzati con precisione, eliminando la natura a raffiche del flusso originale.
3.  **Tier 3: Diretta Target**: Il secondo Raspberry Pi, il **Diretta Target**, si collega *solo* all'Host Pi tramite un cavo Ethernet corto, creando un collegamento point-to-point galvanicamente isolato. Riceve l'audio dall'Host e si collega al vostro DAC o DDC tramite USB.

### Cosa offrono Diretta e AudioLinux

La superiorità di questo design deriva da due componenti software chiave in esecuzione sui dispositivi Raspberry Pi:

* **AudioLinux**: Si tratta di un sistema operativo in tempo reale sviluppato appositamente per l'uso audiofilo. A differenza di un OS generico, è ottimizzato per ridurre al minimo le latenze del processore e il "jitter" di sistema, fornendo una base stabile e a basso rumore per il nostro endpoint.
* **Diretta**: Questo protocollo rivoluzionario è l'ingrediente segreto che risolve il problema alla radice. Riconosce che le fluttuazioni nel carico di elaborazione dell'endpoint generano rumore elettrico a bassa frequenza che può eludere il filtraggio interno del DAC (definito dal suo Power Supply Rejection Ratio, o PSRR) e degradare sottilmente le prestazioni analogiche. Per combattere questo fenomeno, Diretta utilizza il modello "Host-Target", in cui l'Host invia i dati in un flusso continuo e sincronizzato di pacchetti piccoli ed equamente distanziati. Questo "bilancia" il carico di elaborazione sul dispositivo Target, stabilizzando il suo consumo di corrente e riducendo al minimo la generazione di questo dannoso rumore elettrico.

La combinazione dell'isolamento galvanico fisico del collegamento Ethernet point-to-point e l'eliminazione del rumore di elaborazione fornita dal protocollo Diretta crea un percorso di segnale estremamente pulito verso il DAC, in grado di superare soluzioni che costano svariate migliaia di euro.

---

### Un percorso gratificante verso l'eccellenza sonora

Questo progetto è molto più di un semplice esercizio tecnico; è un modo gratificante di coltivare questa passione e assumere il controllo diretto delle prestazioni del vostro impianto. Costruendo questo "Diretta Bridge", non vi limiterete ad assemblare componenti, ma implementerete un'architettura allo stato dell'arte che affronta direttamente le sfide fondamentali dell'audio digitale. Acquisirete una comprensione più profonda di ciò che conta davvero per la riproduzione digitale e sarete ricompensati con un livello di chiarezza, dettaglio e realismo musicale da Roon che forse non ritenevate possibile.

Ora, cominciamo.

---

Se vi trovate negli Stati Uniti, prevedete una spesa di circa $320 (più tasse e spedizione) per completare la build di base, limitata alla riproduzione a 44.1/48 kHz (per valutazione), più altri €100 per abilitare la riproduzione ad alta risoluzione (prezzi soggetti a variazioni):
- Hardware ($240)
- Abbonamento di un anno ad AudioLinux ($79)
- Licenza Diretta Target (€100)

## Indice
1.  [Prerequisiti](#1-prerequisiti)
2.  [Preparazione iniziale dell'immagine](#2-preparazione-iniziale-dellimmagine)
3.  [Configurazione di base del sistema (Eseguire su entrambi i dispositivi)](#3-configurazione-di-base-del-sistema-eseguire-su-entrambi-i-dispositivi)
4.  [Aggiornamenti di sistema (Eseguire su entrambi i dispositivi)](#4-aggiornamenti-di-sistema-eseguire-su-entrambi-i-dispositivi)
5.  [Configurazione di rete Point-to-Point](#5-configurazione-di-rete-point-to-point)
6.  [Accesso SSH comodo e sicuro](#6-accesso-ssh-comodo-e-sicuro)
7.  [Ottimizzazioni di sistema comuni](#7-ottimizzazioni-di-sistema-comuni)
8.  [Installazione e configurazione del software Diretta](#8-installazione-e-configurazione-del-software-diretta)
9.  [Fasi finali e integrazione con Roon](#9-fasi-finali-e-integrazione-con-roon)
10. [Appendice 1: Controllo della ventola Argon ONE opzionale](#10-appendice-1-controllo-della-ventola-argon-one-opzionale)
11. [Appendice 2: Telecomando IR opzionale](#11-appendice-2-telecomando-ir-opzionale)
12. [Appendice 3: Purist Mode opzionale](#12-appendice-3-purist-mode-opzionale)
13. [Appendice 4: Web UI di controllo del sistema opzionale](#13-appendice-4-web-ui-di-controllo-del-sistema-opzionale)
14. [Appendice 5: Verifiche dello stato del sistema](#14-appendice-5-verifiche-dello-stato-del-sistema)
15. [Appendice 6: Ottimizzazione delle prestazioni in tempo reale opzionale](#15-appendice-6-ottimizzazione-delle-prestazioni-in-tempo-reale-opzionale)
16. [Appendice 7: Ottimizzazioni IRQ e dei thread opzionali](#16-appendice-7-ottimizzazioni-irq-e-dei-thread-opzionali)
17. [Appendice 8: Velocità di rete Purist opzionale](#17-appendice-8-velocità-di-rete-purist-opzionale)
18. [Appendice 9: Ottimizzazione Jumbo Frames opzionale](#18-appendice-9-ottimizzazione-jumbo-frames-opzionale)
19. [Appendice 10: Aggiornamenti di sistema opzionali](#19-appendice-10-aggiornamenti-di-sistema-opzionali)

---

### **Come usare questa guida**

Questa guida è progettata per essere il più semplice possibile, riducendo al minimo la necessità di modificare manualmente i file. Il flusso di lavoro principale consiste nel **copiare e incollare** i blocchi di comandi da questo documento direttamente in una finestra di terminale collegata ai dispositivi Raspberry Pi.

Ecco il processo da seguire per la maggior parte dei passaggi:

1.  **Connettersi via SSH**: Utilizzerete un client SSH sul computer principale per accedere al **Diretta Host** o al **Diretta Target** come indicato in ciascuna sezione.
2.  **Copiare il comando**: Nel browser web, passate il mouse sull'angolo in alto a destra di un blocco di comandi in questa guida. Apparirà un'**icona di copia**. Cliccate su di essa per copiare l'intero blocco negli appunti.
3.  **Incollare ed eseguire**: Incollate i comandi copiati nella finestra corretta del terminale SSH e premete `Invio`.

I comandi e gli script sono stati scritti con cura per essere sicuri e prevenire errori, anche se eseguiti più di una volta. Seguendo questo metodo di copia-incolla, potrete evitare i comuni errori di battitura e di configurazione.

---

### Video guida passo-passo

Ecco il link a una serie di brevi video che illustrano questo processo:

* [Guida passo-passo per la build Diretta con due computer Raspberry Pi](https://youtube.com/playlist?list=PLMl09rJ6zKCk13V-IH_kRKW7FP8Q0_Fw0&si=u_E8rUEhgMiQ4NIb)

---

### 1. Prerequisiti

#### Hardware

Di seguito viene fornito un elenco completo dei materiali. Sebbene sia possibile sostituire altri componenti, l'utilizzo di queste parti specifiche migliora le possibilità di una build riuscita.

**Componenti principali (da [pishop.us](https://www.pishop.us/) o fornitore simile):**
* 2 x [Raspberry Pi 5/1GB](https://www.pishop.us/product/raspberry-pi-5-1gb/)
* 2 x [Flirc Raspberry Pi 5 Case](https://www.pishop.us/product/flirc-raspberry-pi-5-case/)
* 2 x [64 GB A2 microSDXC Card](https://www.bhphotovideo.com/c/product/1830849-REG/lexar_lmssipl064g_bnanu_64gb_silver_plus_microsdxc.html)
* 2 x [Alimentatore Raspberry Pi 45W USB-C - Bianco](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)

**Componenti di rete richiesti:**
* 1 x [Adattatore da USB3 a Ethernet Plugable](https://www.amazon.com/dp/B00AQM8586) (per il Diretta Host)
* 1 x [Cavo patch Ethernet CAT6 corto](https://www.amazon.com/Cable-Matters-Snagless-Ethernet-Internet/dp/B0B57S1G2Y/?th=1) (per il collegamento point-to-point)

**Opzionale, ma utile per la risoluzione dei problemi:**
* 1 x [Cavo da Micro-HDMI a HDMI standard (A/M), 2m, Bianco](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Tastiera ufficiale Raspberry Pi - Rosso/Bianco](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**Aggiornamenti opzionali:**
* 2 x [Case Argon ONE V3 per Raspberry Pi 5](https://www.amazon.com/Argon-ONE-V3-Raspberry-Case/dp/B0CNGSXGT2/) (in alternativa ai case Flirc)
* 1 x [Telecomando IR Argon](https://www.amazon.com/Argon-Raspberry-Infrared-Batteries-Included/dp/B091F3XSF6/) (per aggiungere capacità di controllo remoto al Diretta Host)
* 1 x [Ricevitore IR USB Flirc](https://www.pishop.us/product/flirc-rpi-usb-xbmc-ir-remote-receiver/) (per utilizzare il telecomando IR Argon con il Diretta Host in un case Flirc)
* 1 x [Blue Jeans BJC CAT6a Belden Bonded Pairs 500 MHz](https://www.bluejeanscable.com/store/data-cables/index.htm) (per il collegamento point-to-point tra Host e Target)
* 1 x [iFi SilentPower iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (per fornire alimentazione pulita al Diretta Target)
* 1 x [Cavo USB iFi SilentPower Pulsar](https://www.silentpower.tech/products/pulsar-usb) (connessione USB con isolamento galvanico)
* 1 x [Adattatore da CC 5.5mm x 2.1mm a USB-C](https://www.amazon.com/5-5mm-Adapter-Female-Convert-Connector/dp/B0CRB7N4GH/) (necessario per adattare lo spinotto dell'iPower Elite all'ingresso di alimentazione USB-C del Diretta Target)
* 1 x [DDC SMSL PO100 PRO](https://www.amazon.com/dp/B0BLYVZCV5) (un convertitore digitale-digitale per DAC privi di una buona implementazione dell'ingresso USB)
* 1 x [Adattatore Wi-Fi USB](https://www.pishop.us/product/raspberry-pi-dual-band-5ghz-2-4ghz-usb-wifi-adapter-with-antenna/) (una connessione cablata è altamente preferibile e più affidabile, ma se l'aggiunta di una rete cablata vicino all'impianto audio fosse impraticabile, sostituite l'adattatore USB-Ethernet Plugable con questo adattatore Wi-Fi)
* 1 x [Cavo sdoppiatore di alimentazione](https://www.amazon.com/dp/B01K3ADXX2?th=1) (per collegare entrambi gli alimentatori da 45W a una singola presa)

**Componente audio richiesto:**
* 1 x DAC o DDC USB

**Strumenti di lavoro richiesti:**
* PC portatile o desktop con Linux, macOS (consigliato iTerm2, https://iterm2.com/) o Microsoft Windows con [WSL2](https://learn.microsoft.com/it-it/windows/wsl/install)
* Un lettore di schede SD o microSD
* Una TV o display HDMI e una tastiera USB (opzionali, ma utili per la risoluzione dei problemi)

#### Costi del software e delle licenze

* **AudioLinux:** Per gli appassionati si consiglia una licenza "Unlimited", attualmente a **$158** (prezzi soggetti a variazioni). Tuttavia, è possibile iniziare con un abbonamento di un anno, attualmente a **$79**. Entrambe le opzioni consentono l'installazione su più dispositivi all'interno della stessa sede.
* **Diretta Target:** È necessaria una licenza per la riproduzione ad alta risoluzione (superiore a 48 kHz PCM) tramite il dispositivo Diretta Target e attualmente costa **€100**.
    * È possibile valutare il Diretta Target utilizzando flussi a 44.1/48 kHz per un periodo di tempo prolungato. Pertanto, durante il periodo di valutazione, si consiglia di utilizzare la funzione **Sample rate conversion** (Conversione della frequenza di campionamento) di Roon nelle impostazioni DSP **MUSE** per convertire tutti i contenuti a 44.1 kHz. Una volta soddisfatti, acquistate la licenza Diretta Target per rimuovere la limitazione. Lasciate attive le impostazioni di conversione della frequenza di campionamento finché non riceverete la seconda e-mail dal team Diretta che indica che il vostro hardware è stato attivato nel loro database.
    * **CRITICO:** Questa licenza è *legata* all'hardware specifico del Raspberry Pi per cui è stata acquistata. È fondamentale eseguire la fase finale di licenza sull'esatto hardware che si intende utilizzare in modo permanente.
    * Diretta può offrire una licenza sostitutiva una tantum in caso di guasto dell'hardware entro i primi due anni (si prega di verificare i termini al momento dell'acquisto). Se si cambia l'hardware per qualsiasi altro motivo, è necessario acquistare una nuova licenza.

---

### 2. Preparazione iniziale dell'immagine

1.  **Acquisto e download:** Ottenete l'immagine AudioLinux dal [sito ufficiale](https://www.audio-linux.com/). Riceverete via e-mail un link per scaricare un file `.img.gz` o `.img.xz`, solitamente entro 24 ore dall'acquisto.
2.  **Scrittura dell'immagine:** Utilizzate [Raspberry Pi Imager](https://www.raspberrypi.com/software/) per scrivere l'immagine di AudioLinux scaricata su **entrambe** le schede microSD.

---

### 3. Configurazione di base del sistema (Eseguire su entrambi i dispositivi)

Dopo la scrittura dell'immagine, è necessario configurare singolarmente ciascun Raspberry Pi per evitare conflitti di rete.

Per ottenere le migliori prestazioni, questa guida utilizza il Raspberry Pi 5 sia per il Diretta Target (il dispositivo collegato al DAC) che per il Diretta Host. Configurerete prima l'Host.

> **AVVERTIMENTO CRITICO:** Poiché entrambi i dispositivi vengono inizializzati con la stessa identica immagine, avranno valori di `machine-id` identici. Se accendete entrambi i dispositivi contemporaneamente mentre sono collegati alla stessa LAN, il vostro server DHCP assegnerà probabilmente loro lo stesso indirizzo IP, causando un conflitto di rete.
>
> **È necessario eseguire l'avvio e la configurazione iniziale per ciascun dispositivo uno alla volta.**

1.  Inserite la scheda microSD nel **primo** Raspberry Pi, collegatelo alla rete e accendetelo. **Nota:** Se state usando il case Argon ONE, potreste sentire del rumore proveniente dalla ventola. Non preoccupatevi. Una volta terminata la configurazione di Diretta, ci sono istruzioni nell'[Appendice 1](#10-appendice-1-controllo-della-ventola-argon-one-opzionale) per gestire il rumore della ventola.
2.  Completate **tutta la Sezione 3** per questo primo dispositivo.
3.  Una volta che il primo dispositivo si è riavviato con la sua nuova configurazione univoca, spegnetelo.
4.  Ora, accendete il **secondo** Raspberry Pi e ripetete **tutta la Sezione 3** per quest'ultimo.

Fate riferimento alla ricevuta dell'acquisto di Audiolinux per l'utente SSH predefinito e le password di sudo/root. Prendete nota, poiché le userete molte volte durante questo processo.

Utilizzerete il client SSH sul vostro computer locale per accedere ai computer RPi durante questo processo. Questo client richiede di trovare l'indirizzo IP dei computer RPi, che potrebbe cambiare da un riavvio all'altro. Il modo più semplice per ottenere questa informazione è dall'interfaccia web o dall'app del router della vostra rete domestica, ma opzionalmente potete installare l'app [fing](https://www.fing.com/app/) sul vostro smartphone o tablet.

Una volta ottenuto l'indirizzo IP di uno dei computer RPi, utilizzate il client SSH sul vostro computer locale per accedere utilizzando questa procedura. Prendete nota del comando `ssh` di esempio, poiché userete comandi simili a questo in tutta la guida.
```bash
cmd=$(cat <<'EOT'
read -rp "Inserisci l'indirizzo del tuo RPi e premi [invio]: " RPi_IP_Address
echo 'Promemoria: la password predefinita si trova nella tua email di AudioLinux da parte di Piero'
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 3.1. Rigenerare il Machine ID

Il `machine-id` è un identificatore univoco per l'installazione del sistema operativo. **Deve** essere diverso per ciascun dispositivo.

```bash
echo ""
echo "Vecchio ID macchina: $(cat /etc/machine-id)"
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
echo "Nuovo ID macchina: $(cat /etc/machine-id)"
```

#### 3.2. Impostare hostname univoci

Impostate un hostname chiaro per ciascun dispositivo per identificarli facilmente. **Nota:** Se questa non è la vostra prima build con queste istruzioni e avete già una coppia Diretta Host/Target sulla vostra rete, prendete in considerazione di scegliere un nome diverso per questo nuovo Diretta Host, come `diretta-host2`, solo per questa parte. Questo renderà più facile accedervi in modo indipendente in seguito.

**Sul vostro PRIMO dispositivo (il futuro Diretta Host):**
```bash
# Sul Diretta Host
sudo hostnamectl set-hostname diretta-host
```

**Sul vostro SECONDO dispositivo (il futuro Diretta Target):**
```bash
# Sul Diretta Target
sudo hostnamectl set-hostname diretta-target
```

**A questo punto, spegnete il dispositivo. Ripetete i [passaggi precedenti](#3-configurazione-di-base-del-sistema-eseguire-su-entrambi-i-dispositivi) per il secondo Raspberry Pi.**
```bash
sudo sync && sudo poweroff
```

---

### 4. Aggiornamenti di sistema (Eseguire su entrambi i dispositivi)

Per i passaggi in questa sezione, di solito è più efficiente (e meno confuso) completare tutta la Sezione 4 sul Diretta Host e poi ripetere l'intera sezione sul Diretta Target.

Ogni RPi ha il proprio machine ID, quindi potete accenderli ora. Se disponete di due cavi di rete, è più comodo collegarli entrambi alla rete domestica contemporaneamente per i passaggi successivi, altrimenti potete procedere uno alla volta. **Nota**: il router assegnerà probabilmente loro indirizzi IP diversi da quello utilizzato inizialmente per l'accesso. Assicuratevi di utilizzare il nuovo indirizzo IP con i comandi SSH. Ecco un promemoria:

```bash
cmd=$(cat <<'EOT'
read -rp "Inserisci il (nuovo) indirizzo del tuo RPi e premi [invio]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 4.1. Installare "Chrony" per aggiornare l'orologio di sistema

L'orologio di sistema deve essere accurato prima di poter installare gli aggiornamenti. Il Raspberry Pi non ha una batteria NVRAM, quindi l'orologio deve essere impostato a ogni avvio. Questo avviene in genere collegandosi a un servizio di rete. Questo script assicurerà che l'orologio sia impostato e rimanga corretto durante il funzionamento del computer.

```bash
sudo id
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh | sudo bash
sleep 5
chronyc sources
```

#### 4.2. Impostare il fuso orario

```bash
cmd=$(cat <<'EOT'
clear
echo "Benvenuto nella configurazione interattiva del fuso orario."
echo "Selezionerai prima una regione, poi un fuso orario specifico."

# Consente all'utente di selezionare una regione
PS3="Seleziona un numero per la tua regione: "

select region in $(timedatectl list-timezones | grep -F / | cut -d/ -f1 | sort -u); do
  if [[ -n "$region" ]]; then
    echo "Hai selezionato la regione: $region"
    break
  else
    echo "Selezione non valida. Riprova."
  fi
done

echo ""

# Consente all'utente di selezionare un fuso orario all'interno di quella regione
PS3="Seleziona un numero per il tuo fuso orario: "

select timezone in $(timedatectl list-timezones | grep "^$region/"); do
  if [[ -n "$timezone" ]]; then
    echo "Hai selezionato il fuso orario: $timezone"
    break
  else
    echo "Selezione non valida. Riprova."
  fi
done

# Imposta il fuso orario selezionato
echo
echo "Impostazione del fuso orario su ${timezone}..."
sudo timedatectl set-timezone "$timezone"
echo "✅ Il fuso orario è stato impostato."

# Verifica la modifica
echo
echo "Ora di sistema e fuso orario correnti:"
timedatectl status
EOT
)
bash -c "$cmd"
```

#### 4.3. Installare DNS Utils
Installate il pacchetto `dnsutils` in modo che l'aggiornamento del **menu** abbia accesso al comando `dig`:
```bash
sudo pacman -S --noconfirm --needed dnsutils
```

#### 4.4. Eseguire gli aggiornamenti di sistema e del menu

Utilizzate il sistema di menu di AudioLinux per eseguire tutti gli aggiornamenti. Tenete a portata di mano l'e-mail di Piero con l'utente e la password per il download dell'immagine. Ne avrete bisogno per l'aggiornamento del menu. Verrà richiesto **il vostro utente per l'aggiornamento del menu**, il che confonde un po'. Viene chiesto il nome utente e la password che avete utilizzato per scaricare l'immagine di installazione di AudioLinux.

1.  Eseguite `menu` nel terminale.
2.  Selezionate **INSTALL/UPDATE menu**.
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
3.  Nella schermata successiva, selezionate **UPDATE system** e lasciate che il processo si completi.
4.  Al termine dell'aggiornamento del sistema, selezionate **Update menu** dalla stessa schermata per ottenere la versione più recente degli script di AudioLinux. *Nota:* Avrete bisogno dell'indirizzo e-mail utilizzato per acquistare AudioLinux e del vostro nome utente e password di download.
5.  Uscite dal sistema di menu per tornare al terminale.

#### 4.5. Riavvio
Riavviate per caricare il kernel e altri aggiornamenti:
```bash
sudo sync && sudo reboot
```

---

### 5. Configurazione di rete Point-to-Point

In questa sezione creeremo i file di configurazione di rete che attiveranno il collegamento privato dedicato. Per evitare la necessità di una tastiera e di un monitor fisici (accesso alla console), eseguiremo questi passaggi mentre entrambi i dispositivi sono ancora collegati alla vostra LAN principale e accessibili tramite SSH.

Se avete appena terminato l'aggiornamento del vostro Diretta Target, fate clic [qui](https://github.com/dsnyder0pc/rpi-for-roon/blob/main/Diretta.md#52-pre-configure-the-diretta-target) per saltare ai passaggi di configurazione della rete point-to-point per il Target.

---
> #### **Nota sulla configurazione di rete: perché non un semplice bridge?**
>
> Gli utenti che hanno familiarità con AudioLinux potrebbero chiedersi perché questa guida utilizzi script specifici per configurare un collegamento point-to-point instradato con NAT anziché utilizzare l'opzione più semplice del bridge di rete disponibile nel sistema `menu`. Si tratta di una scelta architetturale deliberata, effettuata per ottenere il massimo livello possibile di isolamento di rete.
>
> * Un **bridge di rete** posizionerebbe il Diretta Target direttamente sulla vostra LAN principale, esponendolo a tutto il traffico broadcast e multicast di rete non correlato.
> * La nostra **configurazione instradata** crea una subnet completamente separata e protetta da firewall. Il Diretta Host protegge il Target da tutto il traffico di rete non essenziale, garantendo che il processore del Target gestisca solo il flusso audio. Questo riduce al minimo l'attività del sistema e il potenziale rumore elettrico, che è l'obiettivo finale di questa architettura purista.
>
> Sebbene un bridge sia funzionalmente più semplice da configurare, il metodo instradato fornisce una base teoricamente superiore per le prestazioni audio, massimizzando l'isolamento.
---

#### 5.1. Pre-configurare il Diretta Host

1.  **Creare i file di rete:**
    Create i seguenti due file sul **Diretta Host**. Il file `end0.network` imposta l'IP statico per il futuro collegamento point-to-point. Il file `usb-uplink.network` garantisce che l'adattatore Ethernet USB continui a ricevere un IP dalla vostra LAN principale.

    *File: `/etc/systemd/network/end0.network`*
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

    *File: `/etc/systemd/network/usb-uplink.network`*
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

    **Importante:** Rimuovere il vecchio file en.network se presente:
    ```bash
    # Rimuove il vecchio file di rete generico per prevenire conflitti.
    sudo rm -fv /etc/systemd/network/{en,enp,auto,eth}.network
    ```

    Aggiungere una voce in /etc/hosts per il Diretta Target:
    ```bash
    HOSTS_FILE="/etc/hosts"
    TARGET_IP="172.20.0.2"
    TARGET_HOST="diretta-target"

    # Aggiunge una voce per il Diretta Target se non esiste
    if ! grep -q "$TARGET_IP\s\+$TARGET_HOST" "$HOSTS_FILE"; then
      printf "%s\t%s target\n" "$TARGET_IP" "$TARGET_HOST" | sudo tee -a "$HOSTS_FILE"
    fi
    ```

2.  **Abilitare l'IP Forwarding:**
    ```bash
    # Abilita la funzione per la sessione corrente
    sudo sysctl -w net.ipv4.ip_forward=1

    # Rende la modifica permanente ai riavvii
    echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ip-forwarding.conf
    ```

3.  **Configurare il Network Address Translation (NAT):**
    ```bash
    # Assicurarsi che nft sia installato
    sudo pacman -S --noconfirm --needed nftables

    # Installa le regole del firewall e del NAT
    cat <<'EOT' | sudo tee /etc/nftables.conf
    #!/usr/sbin/nft -f

    # Svuota tutte le vecchie regole dalla memoria
    flush ruleset

    # Crea una tabella denominata 'ip' (IPv4) chiamata 'my_table'
    table ip my_table {

        # === Regola 2: Port Forwarding (DNAT) ===
        # Questa catena si aggancia al percorso di 'prerouting' per il NAT
        chain prerouting {
            type nat hook prerouting priority dstnat;

            # Inoltra la porta Host 5101 alla porta Target 172.20.0.2:5001
            tcp dport 5101 dnat to 172.20.0.2:5001
        }

        # === Regola 3: Consenti il traffico inoltrato (FILTER) ===
        # Questa catena si aggancia al percorso di 'forward' per il filtraggio dei pacchetti
        chain forward {
            type filter hook forward priority 0;

            # Per impostazione predefinita, rifiuta (drop) tutto il traffico inoltrato
            policy drop;

            # Consente le connessioni già stabilite o correlate
            ct state established,related accept

            # Consente il NUOVO traffico corrispondente alla regola di port forward
            ip daddr 172.20.0.2 tcp dport 5001 ct state new accept

            # Consente tutto l'altro NUOVO traffico proveniente dalla subnet del Target
            ip saddr 172.20.0.0/24 accept
        }

        # === Regola 1: Accesso a Internet (MASQUERADE) ===
        # Questa catena si aggancia al percorso di 'postrouting' per il NAT
        chain postrouting {
            type nat hook postrouting priority 100;

            # Applica il NAT (Masquerade) al traffico proveniente dalla subnet diretto
            # all'esterno tramite qualsiasi interfaccia che inizia con 'enp', 'enu' o 'wlp'
            ip saddr 172.20.0.0/24 oifname "enp*" masquerade
            ip saddr 172.20.0.0/24 oifname "enu*" masquerade
            ip saddr 172.20.0.0/24 oifname "wlp*" masquerade
        }
    }
    EOT

    # Arresta e disabilita il vecchio servizio iptables se presente (2>/dev/null sopprime gli errori se non presente)
    sudo systemctl disable --now iptables.service 2>/dev/null
    sudo rm /etc/iptables/iptables.rules 2>/dev/null

    # Abilita e applica le regole tramite nft
    sudo systemctl enable --now nftables.service
    ```

4.  **Configurare l'adattatore Ethernet-USB Plugable**

    Il driver USB predefinito non supporta tutte le funzionalità dell'adattatore Ethernet Plugable. Per ottenere prestazioni affidabili, dobbiamo indicare al gestore dei dispositivi del kernel come gestire il dispositivo quando viene collegato:
    ```bash
    cat <<'EOT' | sudo tee /etc/udev/rules.d/99-ax88179a.rules
    ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0b95", ATTR{idProduct}=="1790", ATTR{bConfigurationValue}!="1", ATTR{bConfigurationValue}="1"
    EOT
    sudo udevadm control --reload-rules
    ```

5.  **Correggere lo script `update_motd.sh`**

    Lo script che aggiorna il banner di login (`/etc/motd`) non gestisce correttamente il caso di due interfacce di rete. Questo evita che la schermata di login si riempia di informazioni errate sull'indirizzo IP dopo i riavvii. Il nuovo script qui sotto risolve questo problema.
    ```bash
    [ -f /opt/scripts/update/update_motd.sh.dist ] || \
    sudo mv /opt/scripts/update/update_motd.sh /opt/scripts/update/update_motd.sh.dist
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh
    sudo install -m 0755 update_motd.sh /opt/scripts/update/
    rm update_motd.sh
    ```

    Infine, spegnete l'Host:
    ```bash
    sudo sync && sudo poweroff
    ```

#### 5.2. Pre-configurare il Diretta Target

**Nota:** Se non avete eseguito il [passaggio 4](#4-aggiornamenti-di-sistema-eseguire-su-entrambi-i-dispositivi) sul Diretta Target, fatelo [ora](#4-aggiornamenti-di-sistema-eseguire-su-entrambi-i-dispositivi), quindi tornate qui.

Sul **Diretta Target**, create il file `end0.network`. Questo configura il suo IP statico e gli indica di utilizzare il Diretta Host come gateway per tutto il traffico Internet.

*File: `/etc/systemd/network/end0.network`*
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

**Importante:** Rimuovere il vecchio file en.network se presente:
```bash
# Rimuove il vecchio file di rete generico per prevenire conflitti.
sudo rm -fv /etc/systemd/network/{en,auto,eth}.network
```

Aggiungete una voce in /etc/hosts per il Diretta Host. **Nota:** Anche se avete selezionato un nome di rete diverso per il vostro Diretta Host, è meglio che il Diretta Target riconosca l'Host come `diretta-host`.
```bash
HOSTS_FILE="/etc/hosts"
HOST_IP="172.20.0.1"
HOST_NAME="diretta-host"

# Aggiunge una voce per il Diretta Host se non esiste
if ! grep -q "$HOST_IP\s\+$HOST_NAME" "$HOSTS_FILE"; then
  printf "%s\t%s host\n" "$HOST_IP" "$HOST_NAME" | sudo tee -a "$HOSTS_FILE"
fi
```

> ---
> ### ⚠️ Avvertimento critico sulla topologia: posizionamento dei filtri solo a monte
>
> Se prevedete di migliorare questo progetto con rigeneratori LAN, isolatori galvanici o filtri (come StackAudio SmoothLAN, iFi SilentPower LAN iSilencer o LAN iPurifier Pro), questi **devono essere posizionati a monte del Diretta Host** (tra il router/switch di rete principale e l'adattatore USB-to-Ethernet dell'Host).
>
> **Non posizionate mai un filtro di rete o un dispositivo di reclocking attivo sul collegamento point-to-point tra l'Host e il Target.** Farlo quasi sempre degrada le prestazioni audio e può causare gravi regressioni di connessione.
>
> * **La LAN principale è la fonte primaria di rumore:** Il collegamento dal router di casa o dallo switch principale è inondato di interferenze elettromagnetiche (EMI), interferenze a radiofrequenza (RFI) e traffico broadcast di scarto. Posizionare un rigeneratore *prima* dell'Host elimina questo inquinamento digitale al confine. L'Host elabora quindi un flusso pulito, riducendo al minimo il sovraccarico della propria CPU, le fluttuazioni di alimentazione e il rumore termico.
> * **Preservare la temporizzazione del Layer 2:** L'introduzione di un dispositivo attivo sul bridge point-to-point diretto interferisce con i vincoli temporali estremamente stretti di Diretta (`CycleTime` e `syncBufferCount`). Questo danneggia la consegna precisa dei frame Layer 2, provocando una riduzione della resa sonora, artefatti di latenza o il fallimento completo del Target nel negoziare le variazioni di velocità di rete.
> * **Il principio dell'isolamento a cascata:** Il vero isolamento è costruito a strati per disaccoppiare completamente il vostro sensibile DAC dalla rete domestica:
>   * **Rete principale** → `[ Filtro/Rigeneratore LAN ]` → **Diretta Host** *(Isola l'Host dalla rete domestica)*
>   * **Diretta Host** → `[ Cavo Ethernet dedicato ]` → **Diretta Target** *(Isolato tramite collegamento point-to-point e stack di protocollo)*
> ---

#### 5.3. Modifica del collegamento fisico

> **Attenzione:** Ricontrollate il contenuto dei file appena creati. Un errore di battitura potrebbe rendere un dispositivo inaccessibile dopo il riavvio, richiedendo una sessione di console o la riscrittura dell'immagine sulla scheda SD per risolvere.

1.  Una volta verificati i file, eseguite uno spegnimento pulito di **entrambi** i dispositivi:
    ```bash
    sudo sync && sudo poweroff
    ```
2.  Scollegate entrambi i dispositivi dallo switch/router della LAN principale.
3.  Collegate la **porta Ethernet integrata** del Diretta Host direttamente alla **porta Ethernet integrata** del Diretta Target utilizzando un singolo cavo Ethernet.
4.  Inserite l'**adattatore USB-to-Ethernet** in una delle porte USB 3.0 blu sul computer Diretta Host
5.  Collegate l'**adattatore USB-to-Ethernet** sul Diretta Host allo switch/router della vostra LAN principale.
6.  Accendete entrambi i dispositivi.

Al riavvio, utilizzeranno automaticamente le nuove configurazioni di rete. **Nota:** l'indirizzo IP del vostro Diretta Host sarà probabilmente cambiato perché ora è collegato alla rete domestica tramite l'adattatore USB-to-Ethernet. Dovrete tornare all'interfaccia web del vostro router o all'app Fing per trovare il nuovo indirizzo, che a questo punto dovrebbe essere stabile.

```bash
cmd=$(cat <<'EOT'
read -rp "Inserisci l'indirizzo finale del tuo Host Diretta e premi [invio]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

Ora dovreste essere in grado di effettuare il ping del Target dall'Host:
```bash
echo ""
echo "\$ ping -c 3 172.20.0.2"
ping -c 3 172.20.0.2
```

Inoltre, dovreste essere in grado di accedere al Target dall'Host:
```bash
echo ""
echo "\$ ssh target"
ssh -o StrictHostKeyChecking=accept-new target
```

Dal Target, proviamo a effettuare il ping di un host su Internet per verificar che la connessione funzioni:
```bash
echo ""
echo "\$ ping -c 3 one.one.one.one"
ping -c 3 one.one.one.one
```

---

### 6. Accesso SSH comodo e sicuro

#### 6.1. Il requisito `ProxyJump`

Ora che la rete è configurata, il **Diretta Target** si trova su una rete isolata (`172.20.0.0/24`) e non può essere raggiunto direttamente dalla LAN principale. L'unico modo per accedervi è passare ("saltare") attraverso il **Diretta Host**.

La direttiva `ProxyJump` nella vostra configurazione SSH locale è il metodo standard e richiesto per ottenere questo risultato.

1.  Eseguite questo comando sul vostro computer locale (non sul Raspberry Pi). Vi verrà richiesto l'indirizzo IP del Diretta Host e verrà stampato l'esatto blocco di configurazione necessario.
```bash
cmd=$(cat <<'EOT'
clear
# --- Script interattivo di configurazione dell'alias SSH ---

SSH_CONFIG_FILE="$HOME/.ssh/config"
SSH_DIR="$HOME/.ssh"

# --- Assicurarsi che la directory .ssh e il file di configurazione esistano con i permessi corretti ---
mkdir -p "$SSH_DIR"
chmod 0700 "$SSH_DIR"
touch "$SSH_CONFIG_FILE"
chmod 0600 "$SSH_CONFIG_FILE"

# --- Definisce il blocco delle impostazioni globali raccomandate ---
GLOBAL_SETTINGS=$(cat <<'EOF'
# --- Impostazioni SSH globali raccomandate ---
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519

EOF
)

# --- Aggiunge in testa le impostazioni globali se non esistono ---
if ! grep -q "AddKeysToAgent yes" "$SSH_CONFIG_FILE"; then
  echo "✅ Aggiunta delle impostazioni SSH globali consigliate..."
  # Utilizza un file temporaneo per inserire in testa le impostazioni
  echo "$GLOBAL_SETTINGS" | cat - "$SSH_CONFIG_FILE" > temp_ssh_config && mv temp_ssh_config "$SSH_CONFIG_FILE"
else
  echo "✅ Le impostazioni SSH globali consigliate esistono già. Nessuna modifica apportata."
fi

# --- Aggiunge le configurazioni host specifiche per Diretta ---
if grep -q "Host diretta-host" "$SSH_CONFIG_FILE"; then
  echo "✅ La configurazione SSH per 'diretta-host' esiste già. Nessuna modifica apportata."
else
  read -rp "Inserisci l'indirizzo IP LAN del tuo Host Diretta e premi [Invio]: " Diretta_Host_IP

  # Aggiunge la nuova configurazione usando un heredoc per chiarezza
  cat <<EOT_HOSTS >> "$SSH_CONFIG_FILE"

# --- Configurazione Diretta (aggiunta dallo script) ---
Host diretta-host host
    HostName ${Diretta_Host_IP}
    User audiolinux

Host diretta-target target
    HostName 172.20.0.2
    User audiolinux
    ProxyJump diretta-host
EOT_HOSTS

  echo "✅ La configurazione SSH per 'diretta-host' e 'diretta-target' è stata aggiunta."
fi

# --- Pulisce StrictHostKeyChecking dalle versioni precedenti di questa guida ---
# Questo non è più necessario con la configurazione della chiave SSH raccomandata
if command -v sed >/dev/null; then
    sed -i.bak -e '/StrictHostKeyChecking/d' "$SSH_CONFIG_FILE"
    # Rimuove le righe vuote che potrebbero essere rimaste
    sed -i.bak -e '/^$/N;/^\n$/D' "$SSH_CONFIG_FILE"
    rm -f "${SSH_CONFIG_FILE}.bak"
fi

echo ""
echo "--- Il tuo file ~/.ssh/config ora contiene: ---"
cat "$SSH_CONFIG_FILE"
EOT
)
bash -c "$cmd"
```

2.  **Verificare la connessione:**

Ora dovreste essere in grado di connettervi a entrambi i dispositivi utilizzando i nuovi alias. Testate la connessione con i seguenti comandi:

**Per accedere al Diretta Host:**
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-host
```

Digitate `exit` per disconnettervi.

**Per accedere al Diretta Target:** _(vi verrà chiesta la password due volte)_
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-target
```
**Nota:** La password viene richiesta una volta per il diretta-host (il jump box) e una seconda volta per il diretta-target stesso. La sezione successiva sostituirà questa procedura con un'autenticazione fluida basata su chiavi.

**Nota:** Per abbreviare, potete usare `ssh host` e `ssh target`.

#### 6.2. Consigliato: Autenticazione sicura con chiavi SSH

Anche se è possibile utilizzare le password, il metodo più sicuro e comodo è l'autenticazione tramite chiave pubblica. La nostra configurazione SSH automatizza gran parte del processo. Dopo una configurazione iniziale una tantum, sarete in grado di accedere in modo sicuro sia all'Host che al Target senza digitare una password.

**Sul vostro computer locale:**

1.  **Creare una chiave SSH (se non ne avete già una):**
    La prassi migliore consiste nell'utilizzare un algoritmo moderno come `ed25519`. Quando richiesto, inserite una **passphrase** robusta e facile da ricordare. Questa non è la vostra password di accesso, ma una password che protegge il file della chiave privata stesso.

    ```bash
    ssh-keygen -t ed25519 -C "audiolinux"
    ```

2.  **Copiare la chiave pubblica sui dispositivi:**
    Questi comandi abilitano in modo sicuro l'accesso tramite la vostra chiave a ciascun dispositivo. Il primo comando richiederà la password del Diretta Host. Poiché questo renderà la connessione all'Host priva di password, il secondo comando richiederà solo la password del Diretta Target.

    ```bash
    echo ""
    ssh-copy-id diretta-host
    echo ""
    ssh-copy-id diretta-target
    ```

3.  **Accedere in modo sicuro:**
    Ora potete connettervi via SSH ai vostri dispositivi. La prima volta che vi collegate a ciascuno di essi, vi verrà richiesta la **passphrase** creata al punto 1.

    ```bash
    ssh diretta-host
    ```

      * **Su Linux:** Grazie all'impostazione `AddKeysToAgent yes`, la vostra chiave verrà aggiunta all'agente SSH per la sessione corrente del terminale. Non vi verrà richiesta nuovamente la passphrase fino al riavvio o all'avvio di una nuova sessione di login.

---

### (Opzionale) Per una migliore esperienza su Linux

Se siete utenti Linux e desiderate che la passphrase della chiave SSH persista tra i riavvii (in modo simile all'esperienza su macOS), si consiglia vivamente di installare `keychain`.

  * **Installare keychain (Ubuntu/Debian):**

    ```bash
    sudo apt update && sudo apt install keychain
    ```

  * **Configurare la shell:** Aggiungete la riga seguente al vostro `~/.bashrc` (o `~/.zshrc`, `~/.profile`, ecc.) per avviare `keychain` all'apertura del terminale. Vi verrà richiesta la passphrase solo una volta, alla prima apertura del terminale dopo un riavvio.

    ```bash
    eval "$(keychain --eval --quiet id_ed25519)"
    ```

  * Ricaricate la shell aprendo un nuovo terminale o eseguendo `source ~/.bashrc`.

Ora potete accedere via SSH a entrambi i dispositivi (`ssh diretta-host`, `ssh diretta-target`) senza che vi venga richiesta la password, autenticati in modo sicuro dalla vostra chiave SSH.

---

### 7. Ottimizzazioni di sistema comuni

Eseguite questi passaggi su _entrambi_ i computer Diretta Host e Target. Se successivamente eseguite un aggiornamento del `menu`, dovrete eseguire nuovamente la correzione del file `sudoers`.

#### 7.1. Risolvere lo stato "Degraded" di Systemd

Su una nuova installazione di AudioLinux, lo stato del sistema viene spesso segnalato come `degraded` (degradato). Ciò è solitamente causato da un'incongruenza innocua tra i file dei gruppi del sistema (`/etc/group` e `/etc/gshadow`). Il seguente comando sincronizza in modo sicuro questi file, risolvendo il fallimento di `shadow.service` e garantendo uno stato pulito del sistema.

```bash
sudo grpconv
```

#### 7.2. Correggere la precedenza delle regole in `sudoers`

Una regola predefinita nel file principale `/etc/sudoers` può talvolta sovrascrivere regole più specifiche necessarie per la Web UI e altre funzionalità. Questo può far sì che i comandi che dovrebbero essere eseguiti senza password richiedano erroneamente l'inserimento della stessa.

Il seguente script corregge in modo sicuro l'ordine delle regole nel file `/etc/sudoers` per garantire che le eccezioni specifiche vengano elaborate correttamente. Lo script apporta modifiche solo se rileva l'ordine errato.

```bash
SUDOERS_FILE="/etc/sudoers"
TEMP_SUDOERS=$(mktemp)

# Utilizza un filtro Perl per creare una versione corretta del file sudoers.
# Questo script è idempotente e non modificherà un file che è già corretto.
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

# Convalida il nuovo file con visudo prima dell'installazione
if [ -s "$TEMP_SUDOERS" ] && sudo visudo -c -f "$TEMP_SUDOERS"; then
    echo "Il file sudoers ha superato la convalida. Installazione della versione corretta..."
    # Utilizza install per impostare la proprietà e i permessi corretti e sostituire l'originale
    sudo install -m 0440 -o root -g root "$TEMP_SUDOERS" "$SUDOERS_FILE"
else
    echo "ERRORE: La convalida del file sudoers modificato non è riuscita. Nessuna modifica apportata." >&2
fi
rm -f "$TEMP_SUDOERS"
```

#### 7.3. Ottimizzare i tempi di avvio
Per evitare un lungo ritardo all'avvio mentre il sistema attende una connessione di rete, disabiliteremo il servizio "wait-online".
```bash
# Disabilita il servizio di attesa di rete per prevenire lunghi ritardi all'avvio
sudo systemctl disable systemd-networkd-wait-online.service

# Crea un override per far attendere allo script MOTD una route predefinita
sudo mkdir -p /etc/systemd/system/update_motd.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/update_motd.service.d/wait-for-ip.conf
[Service]
ExecStartPre=/bin/sh -c "while [ -z \"$(ip route show default)\" ]; do sleep 0.5; done"
EOT
```

#### 7.4. Creare lo script di ripristino
Il comportamento predefinito di Arch Linux consiste nel lasciare il filesystem /boot in uno stato non pulito se il computer non viene spento correttamente. Questo è solitamente sicuro, ma ho riscontrato che può creare una race condition durante l'attivazione della nostra rete privata. Inoltre, è probabile che gli utenti scolleghino questi dispositivi senza prima spegnerli. Per proteggerci da questi problemi, aggiungeremo uno script di workaround che mantiene pulito il filesystem /boot (che viene modificato solo durante gli aggiornamenti del software).

Questo script è sicuro da eseguire sia automaticamente all'avvio sia manualmente su un sistema attivo.
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh
sudo install -m 0755 check-and-repair-boot.sh /usr/local/sbin/
rm check-and-repair-boot.sh
```

#### 7.5. Creare il file di servizio `systemd` e abilitare il servizio
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

#### 7.6. Ridurre al minimo l'I/O del disco
Modificate `#Storage=auto` in `Storage=volatile` in `/etc/systemd/journald.conf`
```bash
sudo sed -i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
```

---

### 8. Installazione e configurazione del software Diretta

#### 8.1. Sul Diretta Target

1.  Collegate il vostro DAC USB a una delle porte USB 2.0 nere sul **Diretta Target** e assicuratevi che il DAC sia acceso.
2.  Connettetevi via SSH al Target: `ssh diretta-target`.
3.  Configurare la toolchain del compilatore compatibile
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```
4.  Eseguite `menu`.
5.  Selezionate **AUDIO extra menu**.
6.  Selezionate **DIRETTA target installation/configuration**. Vedrete il seguente menu:
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
7.  Dovreste eseguire queste azioni in sequenza:
    * Scegliete **1) Install/update** per installare il software (rispondete "Y" a tutte le richieste).
    * Scegliete **2) Enable/Disable Diretta Target** e abilitatelo.
    * Scegliete **3) Configure Audio card**. Il sistema elencherà i dispositivi audio disponibili. Inserite il numero della scheda corrispondente al vostro DAC USB.
        ```text
        ?3
        This option will set DIRETTA target to use a specific card
        Your available cards are:

        card 0: AUDIO [SMSL USB AUDIO], device 0: USB Audio [USB Audio]

        Please type the card number (0,1,2...) you want to use:
        ?0
        ```
    * Scegliete **4) Edit configuration**. Impostate `AlsaLatency=20` per un Target Raspberry Pi 5 o `AlsaLatency=40` per RPi4.
    * Scegliete **6) License**. Il sistema riprodurrà audio ad alta risoluzione (superiore a 44.1 kHz PCM) per 6 minuti in modalità di prova. Seguite il link e le istruzioni sullo schermo per acquistare e applicare la licenza completa per il supporto ad alta risoluzione. Questo richiede l'accesso a Internet configurato al punto 5.
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
    * Scegliete **8) Exit**. Seguite le istruzioni per tornare al terminale

#### 8.2. Sul Diretta Host

1.  Connettetevi via SSH all'Host: `ssh diretta-host`.

2.  Configurare la toolchain del compilatore compatibile
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```

3.  Eseguite `menu`.

4.  Selezionate **AUDIO extra menu**.

5.  Selezionate **DIRETTA host installation/configuration**. Vedrete il seguente menu:
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

6.  Dovreste eseguire queste azioni in sequenza:
    * Scegliete **1) Install/update** per installare il software. (rispondete "Y" a tutte le richieste). *(Nota: potreste visualizzare `error: package 'lld' was not found`. Non preoccupatevi, verrà corretto automaticamente dall'installazione)*
    * Scegliete **2) Enable/Disable Diretta daemon** e abilitatelo.
    * Scegliete **3) Set Ethernet interface**. È fondamentale selezionare `end0`, l'interfaccia per il collegamento point-to-point.
        ```text
        ?3
        Your available Ethernet interfaces are: end0  enu1
        Please type the name of your preferred interface:
        end0
        ```
    * Scegliete **4) Edit configuration** solo se dovete apportare modifiche avanzate. I passaggi precedenti dovrebbero essere sufficienti; tuttavia, ecco alcune impostazioni ottimizzate che potreste voler provare:
        ```text
        ScanOnlineStop=enable
        InfoCycle=80000
        FlexCycle=disable
        CycleTime=800
        periodMin=16
        periodSizeMin=2048
        ```

    * Se desiderate solo installare i parametri ottimizzati sopra indicati, potete utilizzare questo blocco di comandi:
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
    * Scegliete **7) Exit**. Seguite le istruzioni per tornare al terminale

7.  Creare un override per fare in modo che il servizio Diretta si riavvii automaticamente in caso di errore
    ```bash
    sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta_alsa.service.d/restart.conf
    [Service]
    Restart=on-failure
    RestartSec=5
    EOT
    ```

---

### 9. Fasi finali e integrazione con Roon

1.  Eseguite `menu` se siete tornati al terminale dopo il passaggio precedente, altrimenti andate al **Menu principale**.

2.  **Installare Roon Bridge (sull'Host):** Se utilizzate Roon, eseguite i seguenti passaggi sul **Diretta Host**:
    * Eseguite `menu`.
    * Selezionate **INSTALL/UPDATE menu**.
    * Selezionate **INSTALL/UPDATE Roonbridge**.
    * L'installazione procederà. L'operazione potrebbe richiedere un minuto o due.

3.  **Abilitare Roon Bridge (sull'Host):**
    * Selezionate **Audio menu** dal Menu principale
    * Selezionate **SHOW audio service**
    * Se non vedete **roonbridge** tra i servizi abilitati, selezionate **ROONBRIDGE enable/disable**

4.  **Riavviare entrambi i dispositivi:** Per una partenza pulita, riavviate sia il Target che l'Host, in quest'ordine:
    ```bash
    sudo sync && sudo reboot
    ```

5.  **Configurare Roon:**
    * Aprite Roon sul vostro dispositivo di controllo.
    * Andate su `Settings` -> `Audio`.
    * Sotto `diretta-host`, dovreste vedere il vostro dispositivo. Il nome si baserà sul DAC.
    * Fate clic su `Enable`, assegnate un nome e siete pronti a riprodurre musica!

Il vostro collegamento Diretta dedicato è ora completamente configurato per una riproduzione audio pura e isolata.
**Nota:** La zona "Limited" per il test del Diretta Target scomparirà da Roon dopo sei minuti di riproduzione musicale ad alta risoluzione. Questo è normale. A quel punto, dovrete acquistare una licenza per il Diretta Target. Il costo è attualmente di €100 e possono essere necessarie fino a 48 ore per il completamento dell'attivazione. Riceverete due e-mail dal team Diretta. La prima è la ricevuta; la seconda è la notifica di attivazione. Una volta ricevuta l'e-mail di attivazione, riavviate il computer Target per rendere attiva la licenza.

> ---
> ### ✅ Checkpoint: Verificare il sistema di base
>
> Il vostro sistema base Diretta e Roon dovrebbe ora essere completamente funzionante. Per verificare tutti i servizi e le connessioni, procedete all'[**Appendice 5**](#14-appendice-5-verifiche-dello-stato-del-sistema) ed eseguite il comando universale di **System Health Check** sia sull'Host che sul Target.
>
> ---

---

## 10. Appendice 1: Controllo della ventola Argon ONE opzionale
Se avete deciso di utilizzare un case Argon ONE per il vostro Raspberry Pi, lo script di installazione predefinito presuppone l'esecuzione di un sistema operativo Debian. Tuttavia, AudioLinux è basato su Arch Linux, quindi dovrete invece seguire questi passaggi.

Se state utilizzando i case Argon ONE sia per il Diretta Host che per il Target, dovrete eseguire questi passaggi su entrambi i computer.

### Passaggio 1: Saltare lo script `argon1.sh` nel manuale
Il manuale indica di scaricare lo script argon1.sh da download.argon40.com e passarlo a `bash`. Questo non funzionerà su AudioLinux poiché lo script presuppone un sistema operativo basato su Debian, quindi saltate questo passaggio e seguite invece i passaggi descritti di seguito.

### Passaggio 2: Configurare il sistema:
Questi comandi abiliteranno l'interfaccia I2C e aggiungeranno il `dtoverlay` specifico per il case Argon ONE. Lo script tenta innanzitutto di decommentare il parametro `i2c_arm` se è commentato e quindi aggiunge l'overlay `argonone` se manca, evitando errori e voci duplicate.
```bash
BOOT_CONFIG="/boot/config.txt"
I2C_PARAM="dtparam=i2c_arm=on"

# --- Abilita l'I2C decommentando la riga se esiste ---
if grep -q -F "#$I2C_PARAM" "$BOOT_CONFIG"; then
  echo "Attivazione del parametro I2C..."
  sudo sed -i -e "s/^#\($I2C_PARAM\)/\1/" "$BOOT_CONFIG"
fi
```

### Passaggio 3: Configurare i permessi di `udev`
```bash
cat <<'EOT' | sudo tee /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c-[0-9]*", MODE="0666"
EOT
```

### Passaggio 4: Installare il pacchetto Argon One
```bash
yay -S argonone-c-git
```

**Nota:** Se il comando precedente fallisce con errori del compilatore, potete provare questa procedura manuale per correggere e installare il pacchetto:
```bash
# Clona il repository del pacchetto
git clone https://aur.archlinux.org/argonone-c-git.git
cd argonone-c-git

# Scarica il codice sorgente senza compilarlo
makepkg -o

# Applica la patch per correggere l'errore di compilazione con GCC 14+
sed -i 's/_timer_thread()/_timer_thread(void *args)/g' src/argonone-c-git/src/event_timer.c

# Compila e installa utilizzando il sorgente corretto tramite la patch
makepkg -e -i --noconfirm

# Pulisce
cd ..
rm -rf argonone-c-git
```

### Passaggio 5: Passare il case Argon ONE dal controllo hardware a quello software
```bash
sudo pacman -S --noconfirm --needed i2c-tools libgpiod
```

```bash
# Crea gli override di systemd per impostare il case in modalità software all'avvio
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

### Passaggio 6: Abilitare il servizio
```bash
# Ricarica il gestore systemd per leggere la nuova configurazione
sudo systemctl daemon-reload

# Abilita il servizio per avviarsi al boot
sudo systemctl enable argononed.service
```

### Passaggio 7: Riavvio
Infine, riavviate il vostro Raspberry Pi affinché tutte le modifiche abbiano effetto (prima il Target, poi l'Host):
```bash
sudo sync && sudo reboot
```

Ora la ventola sarà controllata dal demone e il pulsante di accensione avrà la piena funzionalità.

### Passaggio 8: Verificare il servizio
```bash
systemctl status argononed.service
journalctl -u argononed.service -b
```

### Passaggio 9: Verificare la modalità della ventola e le impostazioni:
Per vedere i valori di configurazione correnti, eseguite il seguente comando:
```bash
sudo argonone-cli --decode
```

Per regolare questi valori, è necessario creare un file di configurazione. Utilizzate questi valori per iniziare:
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

Riavviate il servizio per applicare i nuovi valori di configurazione:
```bash
sudo systemctl restart argononed.service
echo ""
echo "Valori della ventola aggiornati:"
sleep 5
sudo argonone-cli --decode
```

Ora, sentitevi liberi di regolare i valori secondo necessità, seguendo i passaggi sopra descritti.

---

## 11. Appendice 2: Telecomando IR opzionale

Questa guida fornisce le istruzioni per installare e configurare un telecomando IR per controllare Roon. La configurazione è divisa in due parti.

  * **La Parte 1** riguarda la configurazione specifica dell'hardware. Sceglierete **una** delle due appendici a seconda che stiate utilizzando il ricevitore USB Flirc o il ricevitore integrato del case Argon One.
  * **La Parte 2** riguarda la configurazione del software per lo script di controllo `roon-ir-remote`, che è identico per entrambe le opzioni hardware.

**Nota:** Eseguirete questi passaggi _solo_ sul Diretta Host. Il Target non deve essere utilizzato per rilanciare i comandi del telecomando IR al server Roon.

---

### **Parte 1: Configurazione dell'hardware del ricevitore IR**

*Seguite l'appendice relativa all'hardware che state utilizzando.*

#### **Opzione 1: Configurazione del ricevitore IR USB Flirc**

1.  **Acquistare e programmare il dispositivo Flirc:**
    Avrete bisogno del ricevitore IR USB Flirc, acquistabile dal loro sito web: [https://flirc.tv/products/flirc-usb-receiver](https://flirc.tv/products/flirc-usb-receiver)

    Il dispositivo Flirc deve essere programmato su un computer desktop utilizzando il software Flirc GUI.

      * Inserite il Flirc nel computer desktop e aprite la Flirc GUI.
      * Andate su `Controllers` e selezionate `Full Keyboard`.
      * Programmate i tasti necessari per lo script (ad es. KEY_UP, KEY_DOWN, KEY_ENTER, ecc.) facendo clic sul tasto nella GUI e poi premendo il pulsante corrispondente sul vostro telecomando fisico.
      * Una volta programmato, inserite il Flirc nel **Diretta Host**.

2.  **Testare il dispositivo Flirc:**
    Verificate che il Raspberry Pi riconosca il Flirc come una tastiera.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Selezionate il dispositivo "Flirc" dal menu. Quando premerete i pulsanti sul vostro telecomando, dovreste vedere gli eventi di tastiera stampati sullo schermo.

3.  Passate alla [Parte 2: Configurazione del software dello script di controllo](#part-2-control-script-software-setup)

---

#### **Opzione 2: Configurazione del telecomando IR Argon One**

1.  **Abilitare l'hardware del ricevitore IR:**
    Dovete abilitare l'overlay hardware per il ricevitore IR del case Argon One.

      * Questo comando aggiungerà in modo sicuro l'overlay hardware richiesto al file `/boot/config.txt`, controllando prima che non sia già stato inserito più di una volta.
        ```bash
        BOOT_CONFIG="/boot/config.txt"
        IR_CONFIG="dtoverlay=gpio-ir,gpio_pin=23"

        # Aggiunge l'overlay per il telecomando IR se non è già presente
        if ! sed 's/#.*//' $BOOT_CONFIG | grep -q -F "$IR_CONFIG"; then
          echo "Abilitazione del ricevitore IR Argon One..."
          sudo sed -i "/# Uncomment this to enable infrared communication./a $IR_CONFIG" /boot/config.txt
        else
          echo "Ricevitore IR Argon One già abilitato."
        fi
        ```
      * È necessario un riavvio affinché la modifica hardware abbia effetto.
        ```bash
        sudo sync && sudo reboot
        ```

2.  **Installare gli strumenti IR e abilitare i protocolli:**
    Installate `ir-keytable`
    ```bash
    sudo pacman -S --noconfirm v4l-utils
    ```

3.  **Catturare gli scancode dei pulsanti:**
     Abilitate tutti i protocolli del kernel in modo che possa decodificare i segnali dal vostro telecomando. Eseguite lo strumento di test per visualizzare lo scancode univoco di ciascun pulsante del telecomando.
    ```bash
    sudo ir-keytable -p all
    sudo ir-keytable -t
    ```

    Premete ciascun pulsante che intendete utilizzare e annotate lo scancode dall'output dell'evento `MSC_SCAN` (ad es. `value ca`). Premete `Ctrl+C` al termine.

4.  **Creare il file di mappa dei tasti (Keymap):**
    Questo file mappa gli scancode ai nomi standard dei tasti.

      * Create un nuovo file di keymap:
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
      * Se gli scancode nel file di esempio sopra riportato non corrispondono a quelli registrati, modificate il file (`sudo nano /etc/rc_keymaps/argon.toml`) e cambiateli di conseguenza.

5.  **Creare un servizio `systemd` per caricare la Keymap:**
    Questo servizio caricherà automaticamente la vostra keymap all'avvio.

    Create un nuovo file di servizio e abilitatelo:
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

6.  **Testare il dispositivo di input:**
    Verificate che il sistema riceva gli eventi di tastiera dal telecomando IR.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Selezionate il dispositivo `gpio_ir_recv`. Quando premerete i pulsanti sul telecomando, dovreste vedere gli eventi dei tasti corrispondenti.
    Digitate `CTRL-C` al termine del test.

---

### **Parte 2: Configurazione del software dello script di controllo**

*Dopo aver configurato l'hardware nella Parte 1, seguite questi passaggi per installare e configurare lo script di controllo in Python.*

### **Passaggio 1: Aggiungere `audiolinux` al gruppo `input`**
Questo è necessario affinché l'account `audiolinux` abbia acesso agli eventi provenienti dal ricevitore del telecomando.
```bash
sudo usermod --append --groups input audiolinux
```
Disconnettetevi e accedete nuovamente affinché questa modifica abbia effetto. Potete verificare con questo comando:
```bash
echo ""
echo ""
echo "Verifica delle appartenenze ai gruppi in corso:"
echo "\$ groups"
groups
echo ""
echo "Sopra, dovresti vedere:"
echo "audiolinux realtime video input audio wheel"
```

---

### **Passaggio 2: Installare Python tramite `pyenv`**

Installate `pyenv` e l'ultima versione stabile di Python.

```bash
# Installa le dipendenze per la compilazione
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

# Installa pyenv solo se non è già installato
if [ ! -d "$HOME/.pyenv" ]; then
  echo "--- Installazione di pyenv ---"
  curl -fsSL https://pyenv.run | bash
else
  echo "--- pyenv è già installato. Installazione saltata. ---"
fi

# Configura la shell per pyenv
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

# Carica il file in memoria per rendere pyenv disponibile nella shell corrente
. ~/.bashrc

# Installa e imposta la versione più recente di Python solo se non è già installata
PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')

if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
    # Rileva la memoria totale in MB
    TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

    if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- La RAM fisica è di ${TOTAL_MEM}MB. Limitazione a 1 core per prevenire il blocco. ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
    else
        echo "--- La RAM fisica è di ${TOTAL_MEM}MB. Procedendo con la compilazione in parallelo. ---"
    fi

    echo "--- Installazione di Python ${PYVER} in corso. Questa operazione richiederà diversi minuti... ---"
    pyenv install "$PYVER"
    [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
else
    echo "--- Python ${PYVER} è già installato. ---"
fi

pyenv global "$PYVER"
```

**Nota:** È normale che la fase `Installing Python-3.14.5...` richieda circa 10 minuti, poiché compila Python a partire dai sorgenti. Non arrendetevi! Nell'attesa, rilassatevi ascoltando dell'ottima musica utilizzando la vostra nuova zona Diretta in Roon. Dovrebbe essere disponibile mentre Python si installa sull'Host.

---

### **Passaggio 3: Scaricare il repository software `roon-ir-remote`**

Clonate il repository dello script e scaricate una patch per gestire correttamente i keycode tramite nome invece che tramite numero.

```bash
cd
# Clona il repository se non esiste, altrimenti lo aggiorna
if [ ! -d "roon-ir-remote" ]; then
  git clone https://github.com/dsnyder0pc/roon-ir-remote.git
else
  (cd roon-ir-remote && git pull)
fi
```

---

### **Passaggio 4: Creare il file di configurazione dell'ambiente Roon**

Configurate lo script con le informazioni di Roon. **Nota:** I codici in `event_mapping` devono corrispondere ai nomi dei tasti definiti nella configurazione hardware (`KEY_ENTER`, `KEY_VOLUMEUP`, ecc.).

```bash
bash <<'EOF'
# --- Inizio dello script ---

# Rileva la Zona Roon e la memorizza in una variabile
echo "Inserisci il nome della tua zona Roon."
echo "IMPORTANTE: Questo deve corrispondere esattamente al nome della zona nell'app Roon (distinguendo tra maiuscole e minuscole)."
# Questa riga è la correzione: < /dev/tty indica a read di utilizzare il terminale
read -rp "Inserisci il nome della tua Zona Roon: " MY_ROON_ZONE < /dev/tty

# Rileva se è necessaria la mappatura Flirc/Tastiera
if [ -f "/etc/systemd/system/ir-keymap.service" ]; then
    VOL_UP_CODE="KEY_VOLUMEUP"
    VOL_DOWN_CODE="KEY_VOLUMEDOWN"
    echo "--- Ricevitore IR standard rilevato. Utilizzo di KEY_VOLUMEUP/DOWN. ---"
else
    VOL_UP_CODE="KEY_UP"
    VOL_DOWN_CODE="KEY_DOWN"
    echo "--- Adattatore Flirc/HID rilevato. Utilizzo di KEY_UP/DOWN per il volume. ---"
fi

# Assicurarsi che la directory di destinazione esista
mkdir -p roon-ir-remote

# Crea il file di configurazione utilizzando un Here Document
# La variabile verrà ora sostituita correttamente
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
echo "✅ File di configurazione 'roon-ir-remote/app_info.json' creato con successo."

# --- Fine dello script ---
EOF
```

---

### **Passaggio 5: Preparare e testare `roon-ir-remote`**

Installate le dipendenze dello script in un ambiente virtuale ed eseguitelo per la prima volta.

```bash
cd ~/roon-ir-remote
# Crea l'ambiente virtuale solo se non esiste già
if ! pyenv versions --bare | grep -q "^roon-ir-remote$"; then
  echo "--- Creazione dell'ambiente virtuale 'roon-ir-remote' ---"
  pyenv virtualenv roon-ir-remote
else
  echo "--- L'ambiente virtuale 'roon-ir-remote' esiste già ---"
fi
pyenv activate roon-ir-remote
pip3 install --upgrade pip
pip3 install -r requirements.txt

python roon_remote.py
```

La prima volta che eseguite lo script, dovete **autorizzare l'estensione in Roon** andando su `Settings` -> `Extensions`.

Con la musica in riproduzione nella vostra nuova zona Roon Diretta, puntate il telecomando IR direttamente verso il computer Diretta Host e premete il pulsante Riproduci/Pausa (potrebbe essere il pulsante centrale del controller a 5 direzioni). Provate anche Successivo e Precedente. Se non funzionano, verificate la presenza di eventuali messaggi di errore nella finestra del terminale. Al termine del test, digitate `CTRL-C` per uscire.

---

### **Passaggio 6: Creare un servizio `systemd`**

Create un servizio per eseguire lo script automaticamente in background.

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

# Abilita e avvia il servizio
sudo systemctl daemon-reload
sudo systemctl enable --now roon-ir-remote.service

# Verifica lo stato
sudo systemctl status roon-ir-remote.service
```

---

### **Passaggio 7: Monitorare i log per qualche istante:**
```bash
journalctl -b -u roon-ir-remote.service -f
```

Digitate `CTRL-C` una volta verificato che le cose funzionino come previsto.

---

### **Passaggio 8: Installare lo script `set-roon-zone`**
È utile avere uno script per aggiornare il nome della zona Roon in un secondo momento, se necessario. Ecco come installarlo:
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone
sudo install -m 0755 set-roon-zone /usr/local/bin/
rm set-roon-zone
```

Per utilizzarlo, è sufficiente accedere al computer Diretta Host e digitare:
```bash
set-roon-zone
```
Seguite le istruzioni per inserire il nuovo nome per la vostra Roon Zone. Potrebbe essere necessario inserire la password di root per rendere effettive le modifiche.

**Nota: Un modo migliore per impostare la Zona**
Sebbene questo script funzioni perfettamente, il metodo raccomandato per cambiare la Roon Zone consiste nell'utilizzare l'applicazione web di controllo del sistema AnCaolas Link, descritta in dettaglio nell'[Appendice 4](#13-appendice-4-web-ui-di-controllo-del-sistema-opzionale). La Web UI fornisce una pagina dedicata per visualizzare e modificare il nome della zona dal telefono o dal browser.

### **Passaggio 9: Fatto! 📈**

> ---
> ### ✅ Checkpoint: Verificare la configurazione del telecomando IR
>
> L'hardware e il software del vostro telecomando IR dovrebbero ora essere configurati. Per verificare l'installazione, procedete all'[**Appendice 5**](#14-appendice-5-verifiche-dello-stato-del-sistema) ed eseguite il comando universale di **System Health Check** sul Diretta Host.
>
> ---

Il vostro telecomando IR dovrebbe ora controllare Roon. Buon divertimento!

---

## 12. Appendice 3: Purist Mode opzionale
Sul computer Diretta Target l'attività di rete e di background non correlata alla riproduzione musicale tramite il protocollo Diretta è minima. Tuttavia, alcuni utenti preferiscono adottare misure aggiuntive per ridurre al minimo la possibilità di tale attività. Siamo già all'estremo limite delle prestazioni audio, quindi perché no?

---
> AVVERTIMENTO CRITICO: SOLO per il Diretta Target
>
> Lo script `purist-mode` e tutte le istruzioni in questa appendice sono progettati esclusivamente per il Diretta Target.
>
> NON installate o eseguite questo script sul Diretta Host. Farlo interromperà la connessione dell'Host alla vostra rete principale, rendendolo irraggiungibile e incapace di comunicare con il Roon Core o i servizi di streaming. Questo renderebbe l'intero sistema inutilizzabile finché non si otterrà l'accesso alla console (con tastiera e monitor fisici) per ripristinare le modifiche.
---

### Passaggio 1: Installare lo script `purist-mode` **(solo sul computer Diretta Target)**
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode
sudo install -m 0755 purist-mode /usr/local/bin
rm purist-mode

# Script per mostrare lo stato di Purist Mode al login
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

Per eseguirlo, basta accedere al Diretta Target e digitare `purist-mode`:
```bash
purist-mode
```

Ad esempio:
```text
[audiolinux@diretta-target ~]$ purist-mode
This script requires sudo privileges. You may be prompted for a password.
🚀 Activating Purist Mode...
  -> Stopping time synchronization service (chronyd)...
  -> Disabling DNS lookups...
  -> Overriding gateway with high-priority blackhole route...

✅ Purist Mode is ACTIVE.
```

Ascoltate per un po' per vedere se preferite il suono (o la tranquillità mentale).

---

### Passaggio 2: Abilitare Purist Mode per impostazione predefinita

Se avete deciso che preferite il suono con la modalità Purist abilitata, impostatela come predefinita dopo ogni riavvio.

```bash
echo ""
echo "- Disabilitazione della modalità Purist per garantire uno stato pulito"
purist-mode --revert

echo ""
echo "- Creazione del servizio per ripristinare la modalità Standard a ogni avvio"
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
echo "- Creazione del servizio di attivazione automatica ritardata"
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
echo "- Abilitazione dei nuovi servizi"
sudo systemctl daemon-reload
sudo systemctl enable purist-mode-revert-on-boot.service
sudo systemctl enable purist-mode-auto.service
```

---

### Passaggio 3: Installare un wrapper per il comando `menu`
Molte funzioni in AudioLinux richiedono l'accesso a Internet. Per fare in modo che tutto funzioni come previsto, aggiungete un wrapper al comando `menu` che disabiliti la modalità Purist mentre si utilizza il menu, abilitandola nuovamente all'uscita per tornare al terminale.

```bash
if grep -q menu_wrapper ~/.bashrc; then
  :
else
  echo ""
  echo "Aggiunta di un wrapper attorno al comando menu"
  cat <<'EOT' | tee -a ~/.bashrc

# Wrapper personalizzato per il menu di AudioLinux per gestire la modalità Purist
menu_wrapper() {
  local was_active=false
  # Verifica lo stato iniziale della modalità Purist cercando il file di backup.
  if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
    was_active=true
  fi

  # Se la modalità Purist era attiva, ripristina temporaneamente per il menu.
  if [ "$was_active" = true ]; then
    echo "Verifica delle credenziali per gestire la modalità Purist in corso..."
    sudo -v

    echo "Disabilitazione temporanea della modalità Purist per eseguire il menu..."
    purist-mode --revert > /dev/null 2>&1 # Ripristina silenziosamente
  fi

  # Chiama il comando menu originale
  /usr/bin/menu

  # Se la modalità Purist era attiva prima, riabilitala ora.
  if [ "$was_active" = true ]; then
    echo "Riattivazione della modalità Purist in corso..."
    purist-mode > /dev/null 2>&1 # Attiva silenziosamente
    echo "La modalità Purist è di nuovo attiva."
  fi
}

# Crea un alias per il comando 'menu' che punta alla nostra nuova funzione wrapper
alias menu='menu_wrapper'
# Alias per gestire il servizio automatico di Purist Mode
alias purist-mode-auto-enable='echo "Abilitazione della modalità Purist in fase di avvio..."; purist-mode; sudo systemctl enable purist-mode-auto.service'
alias purist-mode-auto-disable='echo "Disabilitazione della modalità Purist in fase di avvio..."; purist-mode --revert; sudo systemctl disable --now purist-mode-auto.service'
EOT
fi

source ~/.bashrc
```

---

### Comprendere gli stati della modalità Purist

Il sistema Purist Mode è progettato per essere flessibile, consentendo di controllarlo manualmente o di attivarlo automaticamente dopo l'avvio del sistema. Funziona in due stati principali:

  * **Disabilitato (Standard Mode):**
    Questo è lo stato normale e completamente funzionale del Diretta Target. Il gateway di rete è attivo, tutti i servizi (`chronyd`, `argononed`) sono in esecuzione e il dispositivo funziona senza limitazioni.

  * **Attivo (Purist Mode):**
    Questo è lo stato ottimizzato per l'ascolto critico. Il gateway di rete viene disattivato per impedire il traffico Internet e i servizi di background non essenziali (compresa la ventola Argon ONE) vengono arrestati per ridurre al minimo ogni potenziale interferenza di sistema.

Questi stati sono gestiti in due modi: **automaticamente** all'avvio e **manualmente** tramite riga di comando.

#### Controllo automatico (All'avvio)

Il processo di avvio è progettato per essere sicuro e prevedibile, con un passaggio automatico opzionale alla modalità Purist.

1.  **Ripristino obbligatorio all'avvio:** Indipendentemente dallo stato in cui si trovava al momento dello spegnimento, il Diretta Target si avvia **sempre** prima in **Standard Mode**. Questa è una caratteristica fondamentale che garantisce il corretto funzionamento di servizi essenziali come la sincronizzazione dell'ora di rete.

2.  **Attivazione automatica opzionale:** Se avete abilitato la funzione automatica, il sistema attenderà 60 secondi dopo l'avvio e passerà automaticamente a **Purist Mode**. Questo offre un'esperienza immediata per gli utenti che preferiscono ascoltare sempre nello stato ottimizzato.

#### Controllo manuale (Uso interattivo)

Avete il pieno controllo interattivo del sistema in qualsiasi momento.

  * Per **attivare manualmente** la modalità Purist per una sessione di ascolto, accedete al computer Diretta Target ed eseguite:

    ```bash
    purist-mode
    ```

  * Per **disattivare manualmente** la modalità Purist e tornare al funzionamento standard, eseguite:

    ```bash
    purist-mode --revert
    ```

  * Per controllare il **comportamento di avvio automatico**, utilizzate gli alias di utilità sul Diretta Target:

    ```bash
    # Abilita l'attivazione automatica dopo 60 secondi al prossimo avvio
    purist-mode-auto-enable

    # Disabilita l'attivazione automatica al prossimo avvio
    purist-mode-auto-disable
    ```

---

## 13. Appendice 4: Web UI di controllo del sistema opzionale

Questa appendice fornisce le istruzioni per installare una semplice applicazione web sul Diretta Host. Questa applicazione fornisce un'interfaccia facile da usare, accessibile da telefono o tablet, per gestire le funzionalità chiave del vostro sistema Diretta, tra cui la modalità Purist sul Target e le impostazioni di integrazione del telecomando Roon IR sull'Host.

> **AVVERTIMENTO CRITICO: Eseguite questi passaggi con cura.**
> Questa configurazione comporta la creazione di un nuovo utente e la modifica delle impostazioni di sicurezza. Seguite attentamente le istruzioni per garantire che il sistema rimanga sicuro e funzionante.

La configurazione è divisa in due parti: prima configuriamo il **Diretta Target** per accettare i comandi in modo sicuro, poi installiamo l'applicazione web sul **Diretta Host**. Tuttavia, prestate attenzione perché passeremo frequentemente da un host all'altro.

---

### **Parte 1: Configurazione del Diretta Target**

Sul **Diretta Target** creeremo un nuovo utente con permessi molto limitati. Questo utente potrà solo eseguire i comandi specifici necessari per gestire la modalità Purist.

1.  **Connettersi via SSH al Diretta Target:**
    ```bash
    ssh diretta-target
    ```

2.  **Creare un nuovo utente per l'app:**
    Questo comando crea un nuovo utente chiamato `purist-app` e la sua directory home. Per il funzionamento dei comandi SSH non interattivi è richiesta una shell valida.
    ```bash
    sudo useradd --create-home --shell /bin/bash purist-app
    ```

3.  **Creare script di comando sicuri:**
    Creeremo quattro piccoli script dedicati che sono le *uniche* azioni che l'app web è autorizzata a compiere. Questo è un passaggio fondamentale per la sicurezza.
    ```bash
    # Script per ottenere lo stato corrente, incluso lo stato della licenza
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-status
    #!/bin/bash
    IS_ACTIVE="false"
    IS_AUTO_ENABLED="false"
    LICENSE_LIMITED="false"

    # Verifica la modalità Purist
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
      IS_ACTIVE="true"
    fi

    # Verifica se l'avvio automatico è abilitato
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      IS_AUTO_ENABLED="true"
    fi

    # Verifica la cache di avvio validata per un link di valutazione attivo
    if [ ! -f /tmp/diretta_license_url.cache ] || grep -q "http" /tmp/diretta_license_url.cache; then
      LICENSE_LIMITED="true"
    fi

    # Genera in output tutti i flag di stato come un singolo oggetto JSON
    echo "{\"purist_mode_active\": $IS_ACTIVE, \"auto_start_enabled\": $IS_AUTO_ENABLED, \"license_needs_activation\": $LICENSE_LIMITED}"
    EOT

    # Script per attivare/disattivare la modalità Purist
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-mode
    #!/bin/bash
    if [[ "$1" == "--enforce" ]]; then
        # Applicazione assoluta: se si suppone sia attivo, esegui nuovamente
        # lo script di base per ripulire eventuali route predefinite ripristinate.
        if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
            /usr/local/bin/purist-mode
        fi
    elif [ -f "/etc/nsswitch.conf.purist-bak" ]; then
        /usr/local/bin/purist-mode --revert
    else
        /usr/local/bin/purist-mode
    fi
    EOT

    # Script per attivare/disattivare il servizio di avvio automatico
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-auto
    #!/bin/bash
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      systemctl disable --now purist-mode-auto.service
    else
      systemctl enable purist-mode-auto.service
    fi
    EOT

    # Crea lo script per riavviare il servizio Diretta
    cat <<'EOT' | sudo tee /usr/local/bin/pm-restart-target
    #!/bin/bash
    # Riavvia il servizio Diretta ALSA Target.
    # Questo script è destinato ad essere chiamato tramite sudo dall'utente purist-app.
    /usr/bin/systemctl restart diretta_alsa_target.service
    EOT

    # Crea lo script per recuperare l'URL della licenza Diretta
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-license-url
    #!/bin/bash

    # L'unico compito di questo script è leggere il file di cache creato all'avvio.
    readonly CACHE_FILE="/tmp/diretta_license_url.cache"

    if [ -s "$CACHE_FILE" ]; then
        # Se la cache esiste ed ha contenuto, lo visualizza.
        cat "$CACHE_FILE"
    else
        # In caso contrario, stampa un errore utile su stderr ed esce.
        echo "Errore: Cache della licenza non trovata o vuota." >&2
        exit 1
    fi
    EOT

    # Crea lo script per impostare la velocità del collegamento
    cat <<'EOT' | sudo tee /usr/local/bin/pm-set-link
    #!/bin/bash
    # Script di profilo per imporre i limiti del collegamento fisico del Target
    # Rifattorizzato utilizzando maschere di advertisement esplicite per prevenire deadlock hardware

    SPEED="$1"

    if [ "$SPEED" = "10" ]; then
        echo "Pianificazione della limitazione a 10 Mbps (Super Purist)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x002" >/dev/null 2>&1 < /dev/null &
    elif [ "$SPEED" = "100" ]; then
        echo "Pianificazione della limitazione a 100 Mbps (Purist)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x008" >/dev/null 2>&1 < /dev/null &
    elif [ "$SPEED" = "1000" ]; then
        echo "Rilascio delle limitazioni. Ripristino del portafoglio completo 10/100/1000 (Standard)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x03f" >/dev/null 2>&1 < /dev/null &
    else
        echo "Utilizzo: $0 [10|100|1000]"
        exit 1
    fi
    EOT

    # Rende i nuovi script eseguibili
    sudo chmod -v +x /usr/local/bin/pm-*
    ```

4.  **Concedere i permessi di Sudo:**
    Questo passaggio consente all'utente `purist-app` di eseguire i nostri quattro nuovi script con privilegi di root e senza la necessità di un terminale interattivo.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/purist-app
    # Indica a sudo di non richiedere una TTY per l'utente purist-app
    Defaults:purist-app !requiretty

    # Consente all'utente purist-app di eseguire gli specifici script di controllo senza password
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-status
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-mode
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-auto
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-restart-target
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-license-url
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-set-link
    EOT
    ```

5.  **Popolare il file di cache della licenza Diretta all'avvio**
    Il recupero dell'URL della licenza Diretta richiede una connessione a Internet. Se la modalità Purist è abilitata per impostazione predefinita, il Target non sarà mai in grado di recuperare l'URL. Tuttavia, all'avvio, la modalità Purist viene disabilitata per 60 secondi al fine di impostare l'orologio e verificare l'attivazione della licenza Diretta. Possiamo sfruttare questa finestra temporale anche per recuperare l'URL.
    ```bash
    # Scarica lo script, imposta i permessi corretti e lo posiziona nel percorso di sistema
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh
    sudo install -m 0755 create-diretta-cache.sh /usr/local/bin/
    rm create-diretta-cache.sh

    # Crea un servizio per popolare la cache dello stato della licenza
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta-cache.service
    [Unit]
    Description=Asynchronous Diretta License Cache Collector
    After=network.target purist-mode-revert-on-boot.service
    Before=purist-mode-auto.service

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    # Blocca l'esecuzione in modo pulito qui finché l'Host non risponde a un ping
    TimeoutStartSec=infinity
    ExecStartPre=/bin/bash -c "until ping -c 1 -q 172.20.0.1 &>/dev/null; do sleep 2; done"
    ExecStart=/usr/local/bin/create-diretta-cache.sh
    Restart=no

    [Install]
    WantedBy=multi-user.target
    EOT

    # Ricarica systemd per applicare la configurazione drop-in aggiornata
    sudo rm -rf /etc/systemd/system/purist-mode-revert-on-boot.service.d
    sudo systemctl daemon-reload
    sudo systemctl enable diretta-cache.service

    # Esegue lo script manualmente una volta
    sudo /usr/local/bin/create-diretta-cache.sh
    ls -l /tmp/diretta_license_url.cache
    ```

---

### **Parte 2: Configurazione del Diretta Host**

Ora, sul **Diretta Host**, eseguiremo tutti i passaggi per installare e configurare l'applicazione web. Dovreste aver effettuato l'accesso come utente `audiolinux` per tutta questa sezione.

1.  **Connettersi via SSH al Diretta Host:**
    ```bash
    ssh diretta-host
    ```

2.  **Generare una chiave SSH dedicata:**
    Questo crea una nuova coppia di chiavi SSH specificamente per l'app web. Non avrà passphrase.
    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/purist_app_key -N "" -C "purist-app-key"
    ```

3.  **Configurare SSH e copiare la chiave sul Target:**
    Questo passaggio creerà una configurazione SSH e copierà in modo sicuro la chiave pubblica sul Target.
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

    # Copia la chiave pubblica nella directory home del Target
    echo "--> Copia della chiave pubblica sul Target in corso..."
    scp -o StrictHostKeyChecking=accept-new ~/.ssh/purist_app_key.pub diretta-target:
    ```

4.  **Autorizzare la chiave sul Target:**
    ```bash
    ssh diretta-target

    ```

    Una volta effettuato l'accesso al Target, eseguite questo script per configurare la chiave per l'utente 'purist-app'
    ```bash
    echo "--> Esecuzione dello script di configurazione sul Target in corso..."
    set -e
    # Legge la chiave pubblica dal file appena copiato
    PUB_KEY=$(cat purist_app_key.pub)

    # Assicurarsi che la directory .ssh esista e disponga dei permessi corretti
    sudo mkdir -p /home/purist-app/.ssh
    sudo chmod 0700 /home/purist-app/.ssh

    # Crea il file authorized_keys con le restrizioni di sicurezza richieste
    echo "command=\"sudo \$SSH_ORIGINAL_COMMAND\",from=\"172.20.0.1\",no-port-forwarding,no-x11-forwarding,no-agent-forwarding,no-pty ${PUB_KEY}" | sudo tee /home/purist-app/.ssh/authorized_keys > /dev/null

    # Imposta la proprietà e i permessi finali
    sudo chown -R purist-app:purist-app /home/purist-app/.ssh
    sudo chmod 0600 /home/purist-app/.ssh/authorized_keys

    # Pulisce il file della chiave pubblica copiato
    rm purist_app_key.pub

    echo "✅ La chiave SSH è stata autorizzata con successo sul Target."
    ```

5.  **Testare manualmente i comandi remoti (Consigliato):**
    Prima di avviare l'app web, testate i comandi remoti di sola lettura dal terminale del **Diretta Host** per confermare che il backend stia funzionando.
    ```bash
    # Test dello Status Command (dovrebbe restituire una stringa JSON)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-status'

    # Test del comando per il recupero dello stato della licenza.
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-license-url'
    ```

6.  **Installare Python via pyenv** sul **Diretta Host** (potete saltare questo passaggio se lo avete già fatto per far funzionare il telecomando IR)
    Installate `pyenv` e l'ultima versione stabile di Python.
    ```bash
    # Installa le dipendenze per la compilazione
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

    # Installa pyenv solo se non è già installato
    if [ ! -d "$HOME/.pyenv" ]; then
      echo "--- Installazione di pyenv ---"
      curl -fsSL https://pyenv.run | bash
    else
      echo "--- pyenv è già installato. Installazione saltata. ---"
    fi

    # Configura la shell per pyenv
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

    # Carica il file in memoria per rendere pyenv disponibile nella shell corrente
    . ~/.bashrc

    # Installa e imposta la versione più recente di Python solo se non è già installata
    PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
    if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
      # Rileva la memoria totale in MB
      TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

      if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- La RAM fisica è di ${TOTAL_MEM}MB. Limitazione a 1 core per prevenire il blocco. ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
      else
        echo "--- La RAM fisica è di ${TOTAL_MEM}MB. Procedendo con la compilazione in parallelo. ---"
      fi

      echo "--- Installazione di Python ${PYVER} in corso. Questa operazione richiederà diversi minuti... ---"
      pyenv install $PYVER
      [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
    else
      echo "--- Python ${PYVER} è già installato. ---"
    fi

    pyenv global $PYVER
    ```

    **Nota:** È normale che la fase `Installing Python-3.14.5...` richieda circa 10 minuti, poiché compila Python a partire dai sorgenti. Non arrendetevi! Nell'attesa, rilassatevi ascoltando dell'ottima musica utilizzando la vostra nuova zona Diretta in Roon. Dovrebbe essere disponibile mentre Python si installa sull'Host.

7.  **Installare Avahi e le dipendenze di Python sul Diretta Host:**

    **Nota:** OPZIONALE - Se disponete di più di un Diretta Host sulla vostra rete, assicuratevi che abbiano nomi univoci. Potete utilizzare un comando come il seguente per rinominare questo prima di procedere:

    ```bash
    # Facoltativamente, rinomina il Diretta Host se questa è la seconda build sulla stessa rete
    sudo hostnamectl set-hostname diretta-host2
    ```

    Questo passaggio viene eseguito sul **Diretta Host**. Installa il demone Avahi e utilizza un file `requirements.txt` per installare Flask in un ambiente virtuale dedicato.
    ```bash
    # Installa Avahi per la risoluzione dei nomi .local
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm avahi

    # Rileva dinamicamente il nome dell'interfaccia Ethernet USB (ad es. enp... o enu1...)
    USB_INTERFACE=$(ip -o link show | awk -F': ' '/en[pu]/{print $2}')

    # Crea un override di configurazione per Avahi per isolarlo sull'interfaccia USB
    echo "--- Configurazione di Avahi per utilizzare l'interfaccia: $USB_INTERFACE ---"
    sudo mkdir -p /etc/avahi/avahi-daemon.conf.d
    cat <<EOT | sudo tee /etc/avahi/avahi-daemon.conf.d/interface-scoping.conf
    [server]
    allow-interfaces=$USB_INTERFACE
    deny-interfaces=end0
    EOT

    # Abilita e avvia il demone Avahi
    sudo systemctl enable --now avahi-daemon.service

    # Crea la directory dell'applicazione e il file requirements
    mkdir -p ~/purist-mode-webui
    echo "Flask" > ~/purist-mode-webui/requirements.txt

    # Crea un ambiente virtuale e installa le dipendenze
    echo "--- Configurazione dell'ambiente Python per l'interfaccia Web UI ---"
    # Crea l'ambiente virtuale solo se non esiste già
    if ! pyenv versions --bare | grep -q "^purist-webui$"; then
      echo "--- Creazione dell'ambiente virtuale 'purist-webui' ---"
      pyenv virtualenv purist-webui
    else
      echo "--- L'ambiente virtuale 'purist-webui' esiste già ---"
    fi
    pyenv activate purist-webui
    pip install -r ~/purist-mode-webui/requirements.txt
    pyenv deactivate
    ```

8.  **Installare la Flask App:**
    Scaricate lo script Python direttamente da GitHub nella directory dell'applicazione sul **Diretta Host**.
    ```bash
    curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py -o ~/purist-mode-webui/app.py
    ```

9. **Concedere le capacità di Port-Binding**
    Dobbiamo concedere all'eseguibile Python il permesso di effettuare il bind alla porta 80 sul Diretta Host affinché la nostra web app possa avviarsi.
    ```bash
    # Installa il pacchetto che fornisce il comando 'setcap'
    sudo pacman -S --noconfirm --needed libcap

    # Trova il percorso reale dell'eseguibile Python, risolvendo tutti i collegamenti simbolici
    PYTHON_EXEC=$(readlink -f /home/audiolinux/.pyenv/versions/purist-webui/bin/python)

    # Concede la capacità di port-binding direttamente all'eseguibile Python finale
    echo "Applicazione della capability al file reale: ${PYTHON_EXEC}"
    sudo setcap 'cap_net_bind_service=+ep' "$PYTHON_EXEC"
    ```

10. **Concedere i permessi di Sudo sull'Host:**
    Questo passaggio è fondamentale per consentire all'applicazione web di riavviare i servizi necessari relativi a Roon senza inserire una password.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/webui-restarts
    # Consente alla webui (in esecuzione come audiolinux) di applicare i profili host e riavviare i servizi
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl daemon-reload
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roon-ir-remote.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roonbridge.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart diretta_alsa.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/ethtool -s end0 *
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/mv /tmp/setting.inf.tmp /opt/diretta-alsa/setting.inf
    EOT
    sudo chmod 0440 /etc/sudoers.d/webui-restarts
    ```

11. **Testare la Flask App in modo interattivo:**
    Ora, eseguite l'applicazione dalla riga di comando sul **Diretta Host** per assicurarvi che si avvii correttamente.
    ```bash
    cd ~/purist-mode-webui
    pyenv activate purist-webui
    python app.py
    ```
    Dovreste vedere un output che indica che il server Flask si è avviato sulla porta **8080**. Da un altro dispositivo, accedete a [http://diretta-host.local:8080](http://diretta-host.local:8080). Se funziona, tornate al terminale SSH e premete `Ctrl+C` per arrestare il server.

12. **Creare il servizio `systemd`:**
    Questo servizio eseguirà automaticamente l'applicazione web sul **Diretta Host**, utilizzando l'eseguibile Python corretto dal nostro ambiente virtuale `pyenv`.
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

13. **Abilitare e avviare la Web App:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl stop purist-webui.service
    sudo systemctl enable --now purist-webui.service
    ```

14. **Monitorare i log per qualche istante:**
    ```bash
    journalctl -b -u purist-webui.service -f
    ```

15. **Testare la Web UI con l'URL finale:**
    Aprite un browser all'indirizzo [http://diretta-host.local](http://diretta-host.local) e monitorate i log alla ricerca di eventuali errori.

Digitate `CTRL-C` una volta verificato che le cose funzionino come previsto.

---

### **Accedere alla Web UI**

È tutto pronto! Aprite un browser web sul vostro telefono, tablet o computer collegato alla stessa rete del Diretta Host. Navigate verso la pagina principale:

[http://diretta-host.local](http://diretta-host.local)

---
> **Nota sugli avvisi di sicurezza del browser**
> Quando visitate per la prima volta http://diretta-host.local, il vostro browser mostrerà probabilmente un avviso di sicurezza indicando che la connessione non è sicura. Questo è previsto e sicuro da ignorare. L'avviso compare perché la connessione utilizza il protocollo standard `HTTP` invece di quello crittografato `HTTPS`, una scelta intenzionale per ridurre al minimo il sovraccarico di elaborazione sul dispositivo audio. Poiché l'applicazione viene eseguita solo all'interno della vostra rete domestica privata e non gestisce dati sensibili, potete fare clic con sicurezza su "Procedi sul sito" (o equivalente del vostro browser).
---

Dalla pagina principale, una barra di navigazione in alto vi guiderà ai diversi pannelli di controllo:

* **Home:** La pagina principale con i collegamenti alle diverse applicazioni.

* **Purist Mode App:** Questa pagina contiene i controlli per attivare/disattivare la modalità Purist e il suo comportamento di avvio automatico sul Diretta Target. Si aggiorna automaticamente ogni 30 secondi per mostrare lo stato corrente. Contiene anche il pulsante "Restart Services" da utilizzare dopo l'attivazione della licenza Diretta.

* **IR Remote App:** Se avete completato la configurazione del telecomando IR (Appendice 2), apparirà questo link. Questa pagina fornisce un semplice modulo per visualizzare e aggiornare il nome della Zona Roon che il vostro telecomando controllerà. Questa pagina non si aggiorna automaticamente, in modo da poter effettuare le modifiche con tutto il tempo necessario.

### 🔗 Nota sulla piena funzionalità della Web UI

Per sbloccare tutte le funzionalità della Web UI di controllo del sistema — in particolare la regolazione della velocità di collegamento di rete (**Link Speed**) e l'attivazione della modalità **Super Purist** — dovete completare anche le configurazioni hardware e dei servizi dettagliate nell'[**Appendice 8: Velocità di rete Purist opzionale**](#17-appendice-8-velocità-di-rete-purist-opzionale)[cite: 1]. L'interfaccia web si affida direttamente agli script, ai flag e ai servizi sottostanti stabiliti in quella sezione per modificare e imporre con successo i limiti della velocità di collegamento fisico sulla connessione point-to-point[cite: 1].

> ---
> ### ✅ Checkpoint: Verificare la configurazione della Web UI
>
> La Web UI per la modalità Purist dovrebbe ora essere operativa. Per verificar tutti i componenti di questa complessa funzionalità, procedete all'[**Appendice 5**](#14-appendice-5-verifiche-dello-stato-del-sistema) ed eseguite il comando universale di **System Health Check** sia sull'Host che sul Target.
>
> ---

## 14. Appendice 5: Verifiche dello stato del sistema

Dopo aver completato le sezioni principali di questa guida, è buona norma eseguire un rapido controllo di garanzia della qualità (QA) per verificare che tutto sia configurato correttamente.

Abbiamo creato uno script intelligente che rileva automaticamente se lo si sta eseguendo sul **Diretta Host** o sul **Diretta Target** ed esegue il set di controlli appropriato.

### **Come eseguire il controllo**

Su uno dei due Host o Target, eseguite il seguente singolo comando. Scaricherà ed eseguirà lo script di QA, fornendo un report dettagliato sullo stato del sistema.

```bash
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh | sudo bash
```

---

## 15. Appendice 6: Ottimizzazione delle prestazioni in tempo reale opzionale

I passaggi seguenti sono opzionali ma consigliati per gli utenti che desiderano ottenere le prestazioni massime assolute dalla propria configurazione Diretta. La strategia, basata sui consigli dell'autore di AudioLinux Piero, consiste nel creare l'ambiente più stabile ed elettricamente silenzioso possibile sia sull'Host che sul Target.

Questo risultato si ottiene utilizzando l'**isolamento della CPU** (CPU isolation) per dedicare core specifici del processore alle attività audio, schermandoli dal sistema operativo, e regolando attentamente le **priorità in tempo reale** (realtime priorities) per garantire che il percorso dei dati audio non venga mai interrotto.

> **Nota:** Questo è un processo di ottimizzazione avanzato. Assicuratevi che il vostro sistema base Diretta sia completamente funzionante completando le sezioni 1-9 della guida principale prima di procedere. È essenziale un raffreddamento adeguato per entrambi i dispositivi Raspberry Pi.

---

### **Parte 1: Ottimizzazione del Diretta Target**

L'obiettivo per il Target è renderlo un endpoint audio puro e a bassa latenza. Isoleremo l'applicazione Diretta su un singolo core CPU dedicato e gli assegneremo una priorità in tempo reale elevata, ma non eccessiva.

#### **Passaggio 6.1: Isolare un core CPU per l'applicazione audio**

Questo passaggio dedica un core della CPU esclusivamente all'applicazione Diretta Target.

1.  Connettetevi via SSH al Diretta Target:
    ```bash
    ssh diretta-target
    ```
2.  Accedete al sistema di menu di AudioLinux:
    ```bash
    menu
    ```
3.  Navigate al menu **ISOLATED CPU CORES configuration** (sotto **SYSTEM menu**).

4.  Confermate che i core isolati siano disabilitati. In caso contrario, utilizzate l'opzione 3 per disabilitarli:
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

5.  Tornate al menu **ISOLATED CPU CORES configuration** (sotto **SYSTEM menu**). Seguite le istruzioni esattamente come mostrato di seguito per isolare i **core 2 e 3** e assegnare ad essi l'applicazione Diretta.
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

6.  Al termine del processo, uscite per tornare al terminale.

> **Nota sull'affinità automatica degli IRQ:** Potreste notare che lo script segnala di aver isolato anche gli IRQ di rete di `end0` sullo stesso core. Questo non è un bug, ma un'ottimizzazione intelligente. Lo script assegna automaticamente gli interrupt di rete allo stesso core dell'applicazione che utilizza la rete, creando il percorso dati più efficiente possibile.

#### **Passaggio 6.2: Disabilitare il timer legacy `rtapp`**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **Passaggio 6.3: Riavviare per applicare le modifiche.**
```bash
sudo sync && sudo reboot
```

---

### **Parte 2: Ottimizzazione del Diretta Host**

L'obiettivo per l'Host è fornire ai thread del servizio Diretta risorse di elaborazione dedicate, ma senza utilizzare priorità realtime elevate. L'isolamento della CPU è uno strumento più potente in questo caso, poiché impedisce l'interruzione dei processi fin dall'inizio.

#### **Passaggio 6.4: Isolare i core CPU per le applicazioni audio**

Questo passaggio dedica due core CPU alla gestione dei thread del servizio Diretta Host.

1.  Connettetevi via SSH al Diretta Host:
    ```bash
    ssh diretta-host
    ```
2.  Accedete al sistema di menu di AudioLinux:
    ```bash
    menu
    ```
3.  Navigate al menu **ISOLATED CPU CORES configuration** (sotto **SYSTEM menu**).

4.  Confermate che i core isolati siano disabilitati. In caso contrario, utilizzate l'opzione 3 per disabilitarli:
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

5.  Tornate al menu **ISOLATED CPU CORES configuration** (sotto **SYSTEM menu**). Seguite le istruzioni per isolare i **core 2 e 3** e assegnarli a Diretta ALSA.
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

6.  Al termine del processo, uscite per tornare al terminale.

---

#### **Passaggio 6.5: Disabilitare il timer legacy `rtapp`**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **Passaggio 6.6: Riavviare per applicare le modifiche.**
```bash
sudo sync && sudo reboot
```

## 16. Appendice 7: Ottimizzazioni IRQ e dei thread opzionali

### Parte 1: Isolamento del percorso USB del Diretta Target
Per impostazione predefinita, anche quando i core della CPU sono isolati, gli interrupt USB possono ancora competere per le risorse sui core di sistema "rumorosi" (0 e 1). Questo script identifica dinamicamente il controller USB specifico a cui è collegato il vostro DAC e assegna i suoi interrupt hardware ai core audio isolati (2 e 3). Sul Raspberry Pi 5, i controller USB sono gestiti dal chip RP1, il che ci consente di indirizzare gli interrupt hardware verso core specifici.

**Nota:** Questa ottimizzazione non è applicabile al Raspberry Pi 4 a causa degli interrupt bloccati dall'hardware.

1.  Assicuratevi che il vostro DAC sia acceso e collegato al Target.
2.  Avviate la riproduzione musicale sul Diretta Target. Questo assicura che lo script possa rilevare il traffico di interrupt attivo.
3.  Eseguite il seguente comando sul Diretta Target:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/usb-isolation.sh | sudo bash
    ```
4.  Riavviate per applicare le modifiche:
    ```bash
    sudo sync && sudo reboot
    ```

**Cosa fa lo script:** Rileva il percorso del DAC attivo (ad es. xhci-hcd:usb1 o xhci-hcd:usb3). Quindi aggiunge l'identificatore specifico al vostro gruppo di isolamento AudioLinux per creare un percorso dati isolato al 100% dall'ingresso di rete all'uscita USB.

---

### Parte 2: Ottimizzazione dei thread del Diretta Host

Grazie alle ottimizzazioni del kernel in tempo reale, il Diretta Host può ora gestire un intervallo di pacchetti più aggressivo, il che può portare a un miglioramento della qualità del suono. Quest'ultima fase riduce il parametro `CycleTime` da 800 a 514 microsecondi. Questo intervallo di tempo più ridotto tra i pacchetti garantisce che tutti i contenuti fino a DSD256 e DXD (32-bit, 352.8 kHz) richiedano solo un pacchetto per ciclo. Possiamo anche pianificare i thread di Diretta su core specifici.

1.  Connettetevi via SSH al **Diretta Host** se non avete già effettuato l'accesso.
2.  Eseguite il seguente comando per applicare l'impostazione ottimizzata:
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
3.  Riavviate il servizio Diretta affinché la modifica abbia effetto:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart diretta_alsa.service
    ```

> ---
> ### ✅ Checkpoint: Verificare l'ottimizzazione in tempo reale
>
> La vostra ottimizzazione avanzata in tempo reale dovrebbe ora essere completata. Per verificare tutti i componenti di questa nuova configurazione, tornate all'[**Appendice 5**](#14-appendice-5-verifiche-dello-stato-del-sistema) ed eseguite il comando universale di **System Health Check** sia sull'Host che sul Target.
>
> ---

## 17. Appendice 8: Velocità di rete Purist opzionale

**Obiettivo:** Ridurre il rumore elettrico e migliorare la precisione dello scheduler dell'OS limitando la velocità del collegamento di rete dedicato e disabilitando esplicitamente l'Energy Efficient Ethernet (EEE).

Sebbene possa apparire controintuitivo, ridurre la velocità dal valore di 1 Gbps a 100 Mbps (o anche a 10 Mbps) sul collegamento dedicato (`end0`) può migliorare la qualità sonora. La minore frequenza operativa di 100BASE-TX (31.25 MHz rispetto a 62.5 MHz) genera meno RFI. All'estremo, abbassare la velocità a 10 Mbps riduce la frequenza portante a soli 10 MHz. Inoltre, garantire che l'EEE sia disabilitato impedisce al collegamento di entrare in stati di sospensione, eliminando potenziali picchi di latenza (flapping) e garantendo una stabilità incrollabile sull'hardware di Raspberry Pi 5.

> ---
> ### 🎧 Deep Dive: Perché un limite di 10 Mbps ripristina la "calma" sonora
>
> Limitare il collegamento audio dedicato a 10 Mbps introduce rigide limitazioni di formato, ponendo un limite massimo alla riproduzione a **DSD64 nativo** e **PCM a 32-bit/96 kHz**. Tuttavia, per gli audiofili che danno priorità alla qualità CD (redbook) o ai file standard ad alta risoluzione, il compromesso offre profondi benefici sonori affrontando le cause alla radice dell'asprezza digitale.
>
> * **Frequenze portanti drasticamente inferiori:** La rete Gigabit Ethernet standard funziona con un segnale portante ad alta frequenza di 62.5 MHz (utilizzando una complessa codifica multilivello). Scendere a 100 Mbps riduce questo valore a 31.25 MHz. Scendere fino a un collegamento a 10 Mbps (10BASE-T) utilizza un semplicissimo schema di codifica Manchester con una frequenza portante nativa di soli **10 MHz**. Questa enorme riduzione della frequenza operativa riduce in modo significativo le emissioni di radiofrequenza (RFI) generate all'interno dello chassis e lungo il cavo.
> * **Riduzione del sovraccarico di elaborazione sul Target:** Le reti ad alta larghezza di banda costringono la scheda di rete (NIC) e la CPU a gestire i pacchetti di dati a un ritmo rapido e aggressivo. Limitando la velocità del collegamento per adattarla alle reali esigenze dei dati audio standard, si riduce drasticamente il volume di interrupt di rete che il sistema operativo del Target deve elaborare.
> * **Sinergia con la filosofia di fondo di Diretta:** L'intero obiettivo del protocollo Diretta è eliminare l'elaborazione a raffiche e stabilizzare il consumo di corrente. Una linea a 10 Mbps funge da equalizzatore fisico per il flusso di dati, prevenendo i picchi di trasmissione dati ad alta velocità che causano fluttuazioni nell'alimentatore.
>
> Il risultato di questa restrizione "Super Purist" è un calo immediatamente riconoscibile del rumore di fondo digitale. Gli ascoltatori riferiscono frequentemente una scena sonora più ampia e rilassata, un tracciamento dei transitori ad alta frequenza più pulito e un senso generale di naturalezza e calma analogica che si integra perfettamente con ciò che AudioLinux e Diretta stanno cercando di ottenere.
> ---

> **Nota:** Potreste visualizzare avvisi di "buffer low" nei log del Target (con il `LatencyBuffer` che scende a 1). Questo è un comportamento normale dovuto alla maggiore latenza di serializzazione del collegamento più lento e non causa interruzioni audio udibili.

### Passaggio 1: Configurare Host e Target (Disabilitare EEE)

L'Energy Efficient Ethernet (EEE) può causare instabilità del collegamento su alcune combinazioni di hardware. Creeremo un servizio per disabilitarlo esplicitamente sia sull'Host che sul Target per garantire un comportamento coerente.

**Creare il servizio di disabilitazione:** *(Eseguire su ENTRAMBI Host e Target)*

```bash
cat <<'EOT' | sudo tee /etc/systemd/system/disable-eee.service
[Unit]
Description=Disable EEE on end0 for Link Stability
After=network.target
BindsTo=sys-subsystem-net-devices-end0.device
After=sys-subsystem-net-devices-end0.device

[Service]
Type=oneshot
# Attende fino a 5 secondi affinché l'interfaccia si mostri effettivamente come UP
ExecStartPre=/usr/bin/bash -c 'for i in {1..5}; do if ip link show end0 | grep -q "UP"; then exit 0; fi; sleep 1; done; exit 1'
# Ora imposta l'ottimizzazione dell'hardware
ExecStart=-/usr/bin/ethtool -s end0 advertise 0x03f
ExecStart=-/usr/bin/ethtool --set-eee end0 eee off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

sudo systemctl daemon-reload
sudo systemctl enable --now disable-eee.service
```

### Passaggio 2: Contrassegnare il Target con un flag (per QA)

Per garantire che lo **script QA del Target** sappia convalidare questa specifica configurazione, create un file marcatore sul Target:

```bash
sudo touch /etc/diretta-100m
```

### Passaggio 3: Configurare l'Host (limite di velocità)
Creeremo un servizio sull'**Host** che lo costringe ad annunciare (*advertise*) 10 Mbps o 100 Mbps in Full Duplex, a seconda che la modalità "Super Purist" sia abilitata o meno. Il Target rileverà automaticamente la variazione di velocità e si adeguerà.

**Creare lo script e il servizio di restrizione:** *(Eseguire solo sull'Host)*
```bash
cat <<'EOT' | sudo tee /usr/local/bin/set-link-speed.sh
#!/bin/bash
# Imposta la velocità del collegamento in base al flag della web UI Super Purist utilizzando maschere di advertisement sicure
FLAG_FILE="/home/audiolinux/purist-mode-webui/super_purist.flag"
INTERFACE="end0"

# CRITICO: Attendere fino a 60 secondi affinché l'interfaccia fisica inizializzi il carrier del link layer
echo "Sincronizzazione con il livello di collegamento fisico..."
for i in {1..60}; do
    if [ -f /sys/class/net/$INTERFACE/carrier ] && [ "$(cat /sys/class/net/$INTERFACE/carrier 2>/dev/null)" "==" "1" ]; then
        echo "Livello di collegamento fisico rilevato dopo $i secondi."
        break
    fi
    sleep 1
done

# Applica la maschera di advertisement in base allo stato del flag
if [ -f "$FLAG_FILE" ]; then
    echo "Rilevato flag Super Purist. Annuncio di 10 Mbps Full Duplex..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x002
else
    echo "Modalità Standard/Purist. Annuncio fino a 100 Mbps Full Duplex..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x00a
fi

# Gestione della negoziazione specifica per la piattaforma
if grep -q "Raspberry Pi 4" /proc/device-tree/model 2>/dev/null; then
    echo "Rilevato Raspberry Pi 4. Attivazione dell'impulso obbligatorio di rinegoziazione hardware..."
    /usr/bin/ethtool -r $INTERFACE
elif grep -q "Raspberry Pi 5" /proc/device-tree/model 2>/dev/null; then
    echo "Rilevato Raspberry Pi 5. Affidamento all'impulso automatico interno di phylib; ripristino manuale saltato."
else
    /usr/bin/ethtool -r $INTERFACE || true
fi

echo "Politica sulla velocità del collegamento finalizzata con successo."
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

echo "Abilita e avvia il servizio:"
sudo systemctl daemon-reload
sudo systemctl enable --now limit-speed-100m.service
```

***
> **Nota sulla latenza di riproduzione:**
> Potreste notare un leggero aumento del ritardo tra la pressione di "Play" e l'ascolto della musica (fino a circa 1 secondo). Questo è un comportamento previsto. Limitando il collegamento a 10 o 100 Mbps, limitiamo intenzionalmente la raffica (*burst*) iniziale di dati per garantire che la connessione funzioni a una frequenza inferiore e più silenziosa. Il sistema scambia tempi di avvio istantanei con uno stato stazionario più stabile e a minor rumore durante la riproduzione.
***

>
>
> ---
>
> ### ✅ Checkpoint: Verificare la configurazione di rete
>
> Il vostro collegamento di rete dedicato è ora configurato per il funzionamento "Purist" a 100 Mbps. Per verificare che il servizio sull'Host sia attivo e che il Target abbia negoziato correttamente la velocità (rilevata tramite il file marcatore), tornate all'[**Appendice 5**](#14-appendice-5-verifiche-dello-stato-del-sistema) ed eseguite il comando universale di **System Health Check** sia sull'Host che sul Target.
>
> ---

## 18. Appendice 9: Ottimizzazione Jumbo Frames opzionale
Questa sezione ottimizza il trasporto per un'efficienza a banda elevata.

#### **Passaggio 1:** Preparare le interfacce

Dobbiamo forzare temporaneamente le interfacce di rete a una MTU di 9000 per verificare il supporto del kernel e preparare il test del collegamento.

**Eseguite questo prima sul Target, poi sull'Host:**

```bash
sudo sh -c 'ip link set end0 down; sleep 2; ip link set end0 mtu 9000; ip link set end0 up'
end0_mtu=$(ip link show dev end0 | awk '/mtu/ {print $5}')
if [[ "9000" == "$end0_mtu" ]]; then
  echo "SUCCESSO: Il kernel supporta i Jumbo frame. Procedere al passaggio 2."
else
  echo "STOP: Il tuo kernel non sembra supportare i Jumbo frame."
fi
```

*Se visualizzate "STOP" su **uno dei due** Host o Target, non procedete. Nel vostro kernel manca la patch richiesta.*

---

#### **Passaggio 2:** Configurazione automatizzata del Target

Accedete via SSH al Target (`diretta-target`) e incollate il seguente blocco.

```bash
# 1. Rileva il limite del collegamento (Full vs Baby)
echo "Test della capacità del collegamento in corso..."
if ping -c 1 -w 1 -M "do" -s 8972 host &>/dev/null; then
  NEW_MTU=9000
  echo "SUCCESSO: Jumbo frame completi (9000 MTU) supportati."
elif ping -c 1 -w 1 -M "do" -s 2004 host &>/dev/null; then
  NEW_MTU=2032
  echo "SUCCESSO: Baby Jumbo frame (2032 MTU) supportati."
else
  echo "FALLITO: Il collegamento non può supportare i Jumbo frame. Ripristino dei valori predefiniti sicuri."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Applica la configurazione di rete del sistema
  echo "Configurazione di /etc/systemd/network/end0.network..."
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

  # 3. Applica la configurazione di Diretta
  echo "Configurazione di Diretta Target in corso..."
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
  echo "FATTO: Ottimizzazione del Target completata."
}

```

---

#### **Passaggio 3:** Configurazione automatizzata dell'Host

Accedete via SSH all'Host (`diretta-host`) e incollate il seguente blocco. Questo analizzerà il collegamento, configurerà le impostazioni di rete permanenti e aggiornerà Diretta.

```bash
# 1. Rileva il limite del collegamento (Full vs Baby)
echo "Test della capacità del collegamento in corso..."
# Lascia al collegamento un momento per stabilizzarsi dopo la modifica manuale della MTU
sleep 2

if ping -c 1 -w 1 -M "do" -s 8972 target &>/dev/null; then
  NEW_MTU=9000
  echo "SUCCESSO: Jumbo frame completi (9000 MTU) supportati."
elif ping -c 1 -w 1 -M "do" -s 2004 target &>/dev/null; then
  NEW_MTU=2032
  echo "SUCCESSO: Baby Jumbo frame (2032 MTU) supportati."
else
  echo "FALLITO: Il collegamento non può supportare i Jumbo frame. Ripristino dei valori predefiniti sicuri."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Applica la configurazione di rete del sistema
  echo "Configurazione di /etc/systemd/network/end0.network..."
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

  # 3. Applica la configurazione di Diretta
  echo "Configurazione di Diretta Host in corso..."

  # Abilita sempre FlexCycle per i Jumbo Frame per garantire la stabilità
  sudo sed -i 's/^FlexCycle=.*/FlexCycle=enable/' /opt/diretta-alsa/setting.inf

  # Ottimizzazione condizionale di CycleTime e InfoCycle
  if [ "$NEW_MTU" -eq 9000 ]; then
    echo "Ottimizzazione: Rilevati Jumbo frame completi. Allentamento del CycleTime a 1000us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=1000/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=100000/' /opt/diretta-alsa/setting.inf
  else
    echo "Ottimizzazione: Rilevati Baby Jumbo frame. Impostazione del CycleTime a 700us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=700/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=70000/' /opt/diretta-alsa/setting.inf
  fi

  sudo systemctl restart diretta_alsa
  echo "FATTO: Ottimizzazione dell'Host completata."
}
```

#### **Passaggio 4:** Riavviare per applicare le modifiche della MTU
Riavviate prima il Target, poi l'Host:
```bash
sudo sync && sudo reboot
```

>
>
> ---
>
> ### ✅ Checkpoint: Verificare la configurazione di rete
>
> Se siete stati in grado di abilitare il supporto per i Jumbo Frame per la vostra configurazione, questo è un buon momento per tornare all'[**Appendice 5**](#14-appendice-5-verifiche-dello-stato-del-sistema) ed eseguire il comando universale di **System Health Check** sia sull'Host che sul Target.
>
> ---

## 19. Appendice 10: Aggiornamenti di sistema opzionali
Questa sezione fornisce indicazioni sull'applicazione degli aggiornamenti all'hardware del Raspberry Pi, al sistema operativo AudioLinux e allo stack software Diretta.

#### **Parte 1:** Aggiornare il bootloader del Raspberry Pi (Opzionale)

L'aggiornamento del bootloader (EEPROM) del Raspberry Pi non è richiesto e comporta rischi intrinseci. Tuttavia, mantenere aggiornato il firmware può offrire vantaggi come temperature di esercizio più basse e sequenze di avvio più pulite grazie alle continue correzioni di bug fornite dalla Raspberry Pi Foundation.

*Attenzione: Assicuratevi di applicare sempre l'immagine del firmware corretta alla scheda corrispondente. Eseguire il flash di un Raspberry Pi 4 con il bootloader di un Raspberry Pi 5 (o viceversa) può portare a gravi conseguenze negative, fino al blocco permanente (bricking) della scheda.*

**Verificare la versione attuale del bootloader**
Prima di iniziare, accedete via SSH sia all'Host che al Target ed eseguite il comando seguente per verificare la data di rilascio del bootloader corrente. Annotate queste date per poter verificare in seguito che l'aggiornamento sia andato a buon fine.

```bash
vcgencmd bootloader_version
```

*(Cercate la data nella prima riga dell'output).*

**Preparare il supporto per l'aggiornamento**
Avrete bisogno di una scheda microSD vuota, di un lettore di schede SD e del software ufficiale Raspberry Pi Imager installato sulla vostra workstation.

1. Aprite Raspberry Pi Imager. Fate clic su **SCEGLI DISPOSITIVO** (CHOOSE DEVICE) e selezionate la scheda Raspberry Pi specifica che andrete ad aggiornare.

   ![Selezionate il dispositivo Raspberry Pi 5](images/01-rpi-dev.png)

2. Fate clic su **SCEGLI OS** (CHOOSE OS), scorrete l'elenco verso il basso e selezionate **Utility e utility di sistema** (Misc utility images).

   ![Selezionate Utility e utility di sistema](images/02-rpi-misc.png)

3. Selezionate **Bootloader**. *(Nota: il menu mostrerà la famiglia di Pi selezionata al passaggio 1).*

   ![Selezionate Bootloader per la famiglia Pi 5](images/03-rpi-bl.png)

4. Selezionate **Avvio da scheda SD** (SD Card Boot).

   ![Selezionate Avvio da scheda SD](images/04-rpi-sd.png)

5. Fate clic su **SCEGLI ARCHIVIAZIONE** (CHOOSE STORAGE), selezionate la scheda microSD vuota, fate clic su **AVANTI** (NEXT) e scrivete l'immagine.

*Importante: Se il vostro Target è un Raspberry Pi 5 e il vostro Host è un Raspberry Pi 4 (or qualsiasi altra combinazione mista), non potete riutilizzare la stessa scheda di aggiornamento. Dovete tornare al vostro computer ed eseguire il flash di una nuova scheda microSD di aggiornamento specifica per il secondo tipo di scheda prima di procedere.*

**Eseguire l'aggiornamento dell'hardware**

1. Spegnete in sicurezza entrambe le macchine. Spegnete prima il Target, poi l'Host (`sudo poweroff`).
2. Scollegate i cavi di alimentazione fisici da entrambe le unità.
3. Rimuovete le schede microSD di avvio principali da ciascuna unità e mettetele da parte in sicurezza.
4. Inserite con cautela la scheda microSD di aggiornamento appena preparata nella scheda (assicuratevi che i contatti dorati siano rivolti verso il lato inferiore della scheda Raspberry Pi).
5. Ricollegate l'alimentazione alla scheda.
6. Osservate i LED di attività sulla scheda. Attendete finché il LED verde non inizia a lampeggiare rapidamente a un ritmo costante e continuo (solitamente richiede circa 10 secondi). Il lampeggio costante indica che la scrittura della EEPROM è completata.
7. Scollegate l'alimentazione dalla scheda.
8. Rimuovete la scheda microSD di aggiornamento e reinserite la scheda microSD di avvio originale.
9. Ricollegate l'alimentazione ai sistemi. **Accendete prima l'Host, poi il Target.**

Una volta che i sistemi sono completamente avviati e accessibili, eseguite ancora una volta il controllo della versione del bootloader su ciascun computer per confermare che le date del bootloader siano avanzate alla data di rilascio scritta dall'Imager. Se l'Host e il Target utilizzano tipi di schede diversi (ad es. RPi4 e RPi5), le versioni saranno probabilmente differenti. Va bene così.

```bash
vcgencmd bootloader_version
```

---

#### **Parte 2:** Aggiornare AudioLinux e il software Diretta

Il processo di aggiornamento del sistema richiede una sequenza rigorosa per garantire che il kernel personalizzato, le toolchain di compilazione e il demone ALSA rimangano perfettamente sincronizzati.

#### Ora, procedete con gli aggiornamenti
1. Avviate lo strumento di configurazione di AudioLinux digitando `menu` al prompt dei comandi.
2. Navigate fino al menu **Install/Update menu** e selezionate **UPDATE System**.
3. Rimanendo nel menu **Install/Update menu**, selezionate **UPDATE menu**.
   *(Nota: vi verrà richiesto di inserire l'indirizzo e-mail utilizzato per l'acquisto di AudioLinux, insieme al nome utente e alla password specifici forniti da Piero per scaricare l'immagine di AudioLinux).*
4. Selezionate **SELECT/UPDATE kernel**. Scegliete l'esatta versione del kernel raccomandata in precedenza al [**Passaggio 4**](#44-run-system-and-menu-updates).
5. Riapplicate la correzione del `motd` descritta nella [**Sezione 5.1**](#51-pre-configure-the-diretta-host) sull'**Host**.
6. Riapplicate la patch `sudoers` descritta nella [**Sezione 7.2**](#72-correct-sudoers-rule-precedence) su **entrambi** il Target e l'Host.
7. Riavviate prima il Target, seguito dall'Host.
8. Una volta tornati online, eseguite nuovamente lo script "Configurare la toolchain del compilatore compatibile" dal [**Passaggio 8**](#8-installazione-e-configurazione-del-software-diretta) su **entrambi** il Target e l'Host.
9. Sul **Target**, eseguite il passaggio di installazione/aggiornamento di Diretta dettagliato nella [**Sezione 8.1**](#81-on-the-diretta-target).
10. Sull'**Host**, eseguite il passaggio di installazione/aggiornamento di Diretta dettagliato nella [**Sezione 8.2**](#82-on-the-diretta-host).
11. Riavviate prima il Target, seguito dall'Host.
>
>
> ---
>
> ### ✅ Checkpoint: Stato del sistema e test di regressione
>
> Dopo aver completato la sequenza di aggiornamento, è necessario verificare la stabilità della pipeline audio per assicurarsi che non si siano verificate regressioni del software o della configurazione durante l'aggiornamento.
>
> 1. Aprite Roon, attendete il ripristino della zona di rete e riproducete almeno qualche secondo di musica per verificare il collegamento del transport layer e far muovere i contatori hardware.
> 2. Accedete via SSH al **Target** e ripristinate temporaneamente la modalità Standard per consentire agli script diagnostici di far transitare il traffico in modo pulito sulla rete:
>    ```bash
>    purist-mode --revert
>    ```
> 3. Eseguite lo script QA universale **System Health Check** dall'[**Appendice 5**](#14-appendice-5-verifiche-dello-stato-del-sistema) su **entrambi** l'Host e il Target.
> 4. Verificate attentamente l'output e risolvete eventuali problemi isolati di affinità dei thread o di priorità rilevati dallo script.
>
> ---

---

#### **Parte 3:** Sovrascrivere i limiti di corrente USB (Solo Raspberry Pi 5)

Se state utilizzando un Raspberry Pi 5 e lo alimentate con un alimentatore di terze parti di qualità (ad es. iFi SilentPower Elite 5V o un alimentatore lineare in grado di erogare 5A) anziché con l'alimentatore ufficiale Raspberry Pi 27W USB-C, il Pi eseguirà di default una negoziazione di sicurezza a 5V/3A. Questo limita il consumo di corrente combinato su tutte e quattro le porte USB a 600mA.

Sebbene sia solitamente irrilevante per i trasporti audio puri, se sapete che il vostro alimentatore è in grado di erogare continuamente almeno 5A a 5V, potete bypassare questa restrizione in sicurezza.

**Eseguite questo comando per aggiungere l'override alla configurazione di avvio:**

```bash
if ! grep -q "^usb_max_current_enable=" /boot/config.txt; then
  echo "usb_max_current_enable=1" | sudo tee -a /boot/config.txt
else
  echo "Ottimizzazione già presente in /boot/config.txt. Configurazione saltata."
fi
sudo sync && sudo reboot
```

---
