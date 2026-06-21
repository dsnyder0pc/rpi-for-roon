# Construction d'une liaison Diretta dédiée avec AudioLinux sur Raspberry Pi

Ce guide fournit des instructions complètes, étape par étape, pour configurer deux appareils Raspberry Pi en tant que Host Diretta et Target Diretta dédiés. Cette configuration utilise une connexion Ethernet directe point à point entre les deux appareils pour obtenir une isolation réseau et des performances audio absolues.

Le **Host Diretta** se connectera à votre réseau principal (pour accéder à votre serveur de musique) et fera également office de passerelle pour le Target. Le **Target Diretta** se connectera uniquement au Host et à votre DAC USB ou DDC.

## Gestion des versions

Mon objectif est de maintenir ce guide compatible avec le lien de téléchargement officiel actuel d'AudioLinux fourni par Piero.

**Validation actuelle :**
Ces instructions ont été testées pour la dernière fois avec **AudioLinux V5** (Image : `audiolinux_pi4-pi5_520`, Version du menu : `536`).

**Note concernant les mises à jour :**
Comme AudioLinux est basé sur Arch (une rolling release), une nouvelle installation téléchargera toujours les logiciels les plus récents. Une fois que votre système fonctionne à merveille, vous avez deux choix :

1.  **Mettre à jour fréquemment :** Engagez-vous à effectuer des mises à jour au moins une fois par mois afin de corriger les petites pannes au fur et à mesure.
2.  **Figer le système (Recommandé) :** Si le son est excellent, n'y touchez plus. Créez une image de sauvegarde et profitez de la musique !

## Une introduction à l'architecture de référence Roon

Bienvenue dans le guide ultime pour construire un point de terminaison de streaming Roon à la pointe de la technologie. Bien qu'AudioLinux prenne en charge d'autres protocoles, j'utiliserai Roon comme exemple pour cette configuration. Vous pouvez utiliser le système de menus du Host Diretta pour installer la prise en charge d'autres protocoles, notamment HQPlayer, Audirvana, DLNA, AirPlay, etc. Avant de vous plonger dans les instructions étape par étape, il est important de comprendre le « pourquoi » de ce projet. Cette introduction expliquera le problème que cette architecture résout, pourquoi elle est fondamentalement supérieure à de nombreuses alternatives commerciales coûteuses, et comment ce projet DIY représente une voie directe et gratifiante pour libérer la qualité sonore ultime de votre système Roon.

### Le paradoxe Roon : une expérience puissante avec une mise en garde sonore

Roon est célébré, presque universellement, comme le système de gestion musicale le plus puissant et le plus captivant du marché. Ses métadonnées riches et son expérience utilisateur fluide sont inégalées. Cependant, cette suprématie fonctionnelle est depuis longtemps talonnée par une critique persistante d'une partie vocale de la communauté audiophile : la qualité sonore de Roon serait compromise, souvent décrite comme « plate, terne et sans vie » par rapport à d'autres lecteurs.

Ce « son Roon » n'est pas un mythe, ni un défaut du logiciel bit-perfect de Roon. C'est le symptôme potentiel de la nature puissante et gourmande en ressources de Roon. Le Core « lourd » de Roon nécessite une puissance de traitement importante, ce qui génère du bruit électrique (RFI/EMI). Lorsque l'ordinateur exécutant le Core Roon se trouve à proximité de votre convertisseur numérique-analogique (DAC) sensible, ce bruit peut contaminer l'étage de sortie analogique, masquant les détails, réduisant la scène sonore et privant la musique de sa vitalité.

---

### Aller au-delà des « pansements » vers une solution fondamentale

Roon Labs lui-même préconise une architecture à « deux châssis » pour résoudre ce problème principal : séparer le **Roon Core** exigeant d'un **Endpoint** réseau léger (également appelé transport réseau). C'est la première étape correcte, car elle délègue le traitement lourd à une machine distante, isolant son bruit de votre rack audio.

Cependant, même dans cette conception supérieure à deux niveaux, un problème plus subtil subsiste. Les protocoles réseau standard, y compris le RAAT propre à Roon, transmettent les données audio par « rafales » intermittentes. Cela force le processeur du endpoint à augmenter constamment son activité pour traiter ces rafales, provoquant des fluctuations rapides de la consommation de courant. Ces fluctuations génèrent leur propre bruit électrique à basse fréquence directement au niveau du endpoint — le composant le plus proche de votre DAC.

Les fabricants d'appareils audio haut de gamme tentent de combattre les *symptômes* de ce trafic par rafales avec diverses solutions de type « simples palliatifs » : des alimentations linéaires massives pour mieux gérer les pics de courant, des processeurs ultra-basse consommation pour minimiser l'intensité des pics, et des étages de filtrage supplémentaires pour nettoyer le bruit résultant. Bien que ces stratégies puissent aider, elles ne s'attaquent pas à la cause profonde du bruit : le traitement par rafales lui-même.

Ce guide présente une solution plus élégante et considérablement plus efficace. Au lieu d'essayer de nettoyer le bruit, nous allons construire une architecture qui l'empêche d'être généré en premier lieu.

---

### L'architecture à trois niveaux : Roon + Diretta

Ce projet fait évoluer la configuration à deux châssis recommandée par Roon vers un système ultime à trois niveaux, offrant de multiples couches d'isolation cumulées.

1.  **Niveau 1 : Roon Core** : Votre puissant serveur Roon fonctionne sur une machine dédiée, placée loin de votre pièce d'écoute. Il se charge de tout le travail lourd, et son bruit électrique reste isolé de votre système audio.
2.  **Niveau 2 : Host Diretta** : Le premier Raspberry Pi de notre configuration fait office de **Host Diretta**. Il se connecte à votre réseau principal, reçoit le flux audio du Roon Core, puis le transmet sous forme de minuscules segments cadencés avec précision, éliminant ainsi le caractère par rafales du flux d'origine.
3.  **Niveau 3 : Target Diretta** : Le deuxième Raspberry Pi, le **Target Diretta**, se connecte *uniquement* au Host Pi via un court câble Ethernet, créant une liaison point à point isolée galvaniquement. Il reçoit l'audio du Host et se connecte à votre DAC ou DDC via USB.

### Ce que Diretta et AudioLinux apportent

La supériorité de cette conception provient de deux composants logiciels clés fonctionnant sur les appareils Raspberry Pi :

* **AudioLinux** : Il s'agit d'un système d'exploitation en temps réel conçu spécifiquement pour un usage audiophile. Contrairement à un système d'exploitation généraliste, il est optimisé pour minimiser les latences du processeur et le « jitter » du système, offrant une base stable et silencieuse pour notre endpoint.
* **Diretta** : Ce protocole révolutionnaire est la recette secrète qui résout le problème à la racine. Il reconnaît que les fluctuations de la charge de traitement du endpoint génèrent un bruit électrique à basse fréquence qui peut contourner le filtrage interne d'un DAC (défini par son taux de rejet de l'alimentation, ou PSRR) et dégrader subtilement ses performances analogiques. Pour lutter contre cela, Diretta utilise son modèle « Host-Target », où le Host envoie des données dans un flux continu et synchronisé de petits paquets régulièrement espacés. Cela permet de « lisser » la charge de traitement sur le Target, de stabiliser sa consommation de courant et de minimiser la génération de ce bruit électrique pernicieux.

La combinaison de l'isolation galvanique physique de la liaison Ethernet point à point et de l'élimination du bruit de traitement par le protocole Diretta crée un chemin de signal profondément propre vers votre DAC — capable de surclasser des solutions coûtant plusieurs milliers d'euros.

---

### Une voie gratifiante vers l'excellence sonore

Ce projet est plus qu'un simple exercice technique ; c'est un moyen gratifiant de s'impliquer dans notre passion et de prendre le contrôle direct des performances de votre système. En construisant ce « Pont Diretta », vous n'assemblez pas seulement des composants ; vous mettez en œuvre une architecture de pointe qui s'attaque de front aux défis fondamentaux de l'audio numérique. Vous acquerrez une compréhension plus approfondie de ce qui compte réellement pour la lecture numérique et serez récompensé par un niveau de clarté, de détail et de réalisme musical avec Roon que vous n'auriez peut-être pas cru possible.

Maintenant, commençons.

---

Si vous êtes situé aux États-Unis, comptez environ 320 $ (hors taxes et frais de port) pour réaliser la configuration de base, limitée à une lecture à 44,1/48 kHz (pour évaluation), plus 100 € supplémentaires pour activer la lecture haute résolution (tarifs sujets à modification) :
- Matériel (240 $)
- Abonnement d'un an à AudioLinux (79 $)
- Licence Diretta Target (100 €)

## Table des matières
1.  [Prérequis](#1-prérequis)
2.  [Préparation initiale de l'image](#2-préparation-initiale-de-limage)
3.  [Configuration du système de base (À effectuer sur les deux appareils)](#3-configuration-du-système-de-base-à-effectuer-sur-les-deux-appareils)
4.  [Mises à jour du système (À effectuer sur les deux appareils)](#4-mises-à-jour-du-système-à-effectuer-sur-les-deux-appareils)
5.  [Configuration réseau point à point](#5-configuration-réseau-point-à-point)
6.  [Accès SSH pratique et sécurisé](#6-accès-ssh-pratique-et-sécurisé)
7.  [Optimisations système courantes](#7-optimisations-système-courantes)
8.  [Installation et configuration du logiciel Diretta](#8-installation-et-configuration-du-logiciel-diretta)
9.  [Étapes finales et intégration Roon](#9-étapes-finales-et-intégration-roon)
10. [Annexe 1 : Contrôle optionnel du ventilateur Argon ONE](#10-annexe-1--contrôle-optionnel-du-ventilateur-argon-one)
11. [Annexe 2 : Télécommande IR optionnelle](#11-annexe-2--télécommande-ir-optionnelle)
12. [Annexe 3 : Mode puriste optionnel](#12-annexe-3--mode-puriste-optionnel)
13. [Annexe 4 : Interface Web optionnelle de contrôle du système](#13-annexe-4--interface-web-optionnelle-de-contrôle-du-système)
14. [Annexe 5 : Vérifications de l'état du système](#14-annexe-5--system-health-checks-vérifications-de-létat-du-système)
15. [Annexe 6 : Optimisation optionnelle des performances en temps réel](#15-annexe-6--optimisation-optionnelle-des-performances-en-temps-réel)
16. [Annexe 7 : Optimisations optionnelles des IRQ et des threads](#16-annexe-7--optimisations-optionnelles-des-irq-et-des-threads)
17. [Annexe 8 : Vitesses réseau puristes optionnelles](#17-annexe-8--vitesses-réseau-puristes-optionnelles)
18. [Annexe 9 : Optimisation optionnelle des trames Jumbo](#18-annexe-9--optimisation-optionnelle-des-jumbo-frames)
19. [Annexe 10 : Mises à jour système optionnelles](#19-annexe-10--facultatif--mises-à-jour-du-système)

---

### **Comment utiliser ce guide**

Ce guide est conçu pour être aussi simple que possible, en minimisant le besoin d'éditer manuellement des fichiers. Le flux de travail principal consistera à **copier et coller** des blocs de commandes depuis ce document directement dans une fenêtre de terminal connectée à vos appareils Raspberry Pi.

Voici le processus que vous suivrez pour la plupart des étapes :

1.  **Connexion via SSH** : Vous utiliserez un client SSH sur votre ordinateur principal pour vous connecter soit au **Host Diretta**, soit au **Target Diretta**, comme indiqué dans chaque section.
2.  **Copier la commande** : Dans votre navigateur Web, survolez le coin supérieur droit d'un bloc de commandes dans ce guide. Une **icône de copie** apparaîtra. Cliquez dessus pour copier l'intégralité du bloc dans votre presse-papiers.
3.  **Coller et exécuter** : Collez les commandes copiées dans la bonne fenêtre de terminal SSH et appuyez sur `Entrée`.

Les scripts et commandes ont été soigneusement rédigés pour être sûrs et éviter les erreurs, même s'ils sont exécutés plus d'une fois. En suivant cette méthode de copier-coller, vous pouvez éviter les fautes de frappe et les erreurs de configuration courantes.

---

### Tutoriel vidéo

Voici un lien vers une série de courtes vidéos présentant ce processus :

* [Diretta Build Walkthrough with Two Raspberry Pi Computers (en anglais)](https://youtube.com/playlist?list=PLMl09rJ6zKCk13V-IH_kRKW7FP8Q0_Fw0&si=u_E8rUEhgMiQ4NIb)

---

### 1. Prérequis

#### Matériel

Une liste complète des composants est fournie ci-dessous. Bien que d'autres pièces puissent être substituées, l'utilisation de ces composants spécifiques augmente les chances de réussite de la configuration.

**Composants principaux (provenant de [pishop.us](https://www.pishop.us/) ou d'un fournisseur similaire) :**
* 2 x [Raspberry Pi 5/1GB](https://www.pishop.us/product/raspberry-pi-5-1gb/)
* 2 x [Boîtier Flirc Raspberry Pi 5](https://www.pishop.us/product/flirc-raspberry-pi-5-case/)
* 2 x [Carte microSDXC 64 Go A2](https://www.bhphotovideo.com/c/product/1830849-REG/lexar_lmssipl064g_bnanu_64gb_silver_plus_microsdxc.html)
* 2 x [Alimentation Raspberry Pi 45W USB-C - Blanche](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)

**Composants réseau requis :**
* 1 x [Adaptateur Plugable USB3 vers Ethernet](https://www.amazon.com/dp/B00AQM8586) (pour le Host Diretta)
* 1 x [Câble de brassage Ethernet CAT6 court](https://www.amazon.com/Cable-Matters-Snagless-Ethernet-Internet/dp/B0B57S1G2Y/?th=1) (pour la liaison point à point)

**Optionnel, mais utile pour le dépannage :**
* 1 x [Câble Micro-HDMI vers HDMI standard (A/M), 2m, Blanc](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Clavier officiel Raspberry Pi - Rouge/Blanc](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**Mises à niveau optionnelles :**
* 2 x [Boîtier Argon ONE V3 Raspberry Pi 5](https://www.amazon.com/Argon-ONE-V3-Raspberry-Case/dp/B0CNGSXGT2/) (au lieu des boîtiers Flirc)
* 1 x [Télécommande IR Argon](https://www.amazon.com/Argon-Raspberry-Infrared-Batteries-Included/dp/B091F3XSF6/) (pour ajouter des fonctionnalités de télécommande au Host Diretta)
* 1 x [Récepteur IR USB Flirc](https://www.pishop.us/product/flirc-rpi-usb-xbmc-ir-remote-receiver/) (pour utiliser la télécommande IR Argon avec le Host Diretta dans un boîtier Flirc)
* 1 x [Câble Blue Jeans BJC CAT6a Belden Bonded Pairs 500 MHz](https://www.bluejeanscable.com/store/data-cables/index.htm) (pour la connexion point à point entre Host et Target)
* 1 x [iFi SilentPower iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (pour fournir une alimentation propre au Target Diretta)
* 1 x [Câble USB iFi SilentPower Pulsar](https://www.silentpower.tech/products/pulsar-usb) (connexion USB avec isolation galvanique)
* 1 x [Adaptateur DC 5.5mm x 2.1mm vers USB C](https://www.amazon.com/5-5mm-Adapter-Female-Convert-Connector/dp/B0CRB7N4GH/) (nécessaire pour adapter la fiche de l'iPower Elite à l'entrée d'alimentation USB C du Target Diretta)
* 1 x [SMSL PO100 PRO DDC](https://www.amazon.com/dp/B0BLYVZCV5) (un convertisseur numérique-numérique pour les DAC qui manquent d'une bonne implémentation d'entrée USB)
* 1 x [Adaptateur sans fil USB](https://www.pishop.us/product/raspberry-pi-dual-band-5ghz-2-4ghz-usb-wifi-adapter-with-antenna/) (une connexion filaire est fortement préférable et plus fiable, mais si l'ajout d'une connexion Ethernet filaire près de votre système audio n'est pas pratique, remplacez l'adaptateur Plugable USB vers Ethernet par cet adaptateur Wi-Fi)
* 1 x [Cordon répartiteur d'alimentation](https://www.amazon.com/dp/B01K3ADXX2?th=1) (branchez les deux adaptateurs secteur 45W sur une seule prise)

**Composant audio requis :**
* 1 x DAC USB ou DDC

**Outils d'installation requis :**
* Ordinateur portable ou de bureau exécutant Linux, macOS (iTerm2, https://iterm2.com/, recommandé) ou Microsoft Windows avec [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
* Un lecteur de carte SD ou microSD
* Un téléviseur ou un écran HDMI et un clavier USB (optionnels, mais utiles pour le dépannage)

#### Coûts des logiciels et des licences

* **AudioLinux :** Une licence « Unlimited » est recommandée pour les passionnés, au tarif actuel de **158 $** (prix sujet à modification). Toutefois, il est possible de débuter avec un abonnement d'un an, actuellement à **79 $**. Les deux options permettent une installation sur plusieurs appareils au sein d'un même emplacement.
* **Target Diretta :** Une licence est requise pour la lecture haute résolution (supérieure à 48 kHz PCM) via le Target Diretta et coûte actuellement **100 €**.
    * Vous pouvez évaluer le Target Diretta à l'aide de flux 44.1/48 kHz sur une période prolongée. Par conséquent, je recommande d'utiliser la fonctionnalité de **Conversion de taux d'échantillonnage** (Sample rate conversion) de Roon dans les paramètres DSP de **MUSE** afin de convertir tout le contenu à 44.1 kHz pendant votre période d'évaluation. Une fois satisfait, achetez la licence Target Diretta pour lever la restriction. Laissez les paramètres de conversion activés jusqu'à ce que vous receviez le second e-mail de l'équipe Diretta indiquant que votre matériel a été activé dans leur base de données.
    * **CRUCIAL :** Cette licence est *liée* au matériel spécifique du Raspberry Pi pour lequel elle a été achetée. Il est essentiel que vous effectuiez l'étape finale d'attribution de licence sur le matériel exact que vous prévoyez d'utiliser de manière permanente.
    * Diretta peut proposer une licence de remplacement unique en cas de panne matérielle au cours des deux premières années (veuillez vérifier les conditions au moment de l'achat). Si vous changez de matériel pour toute autre raison, une nouvelle licence devra être achetée.

---

### 2. Préparation initiale de l'image

1.  **Achat et téléchargement :** Obtenez l'image d'AudioLinux sur le [site officiel](https://www.audio-linux.com/). Vous recevrez un lien de téléchargement pour un fichier `.img.gz` ou `.img.xz` par e-mail, généralement dans les 24 heures suivant l'achat.
2.  **Flasher l'image :** Utilisez [Raspberry Pi Imager](https://www.raspberrypi.com/software/) pour écrire l'image AudioLinux téléchargée sur **les deux** cartes microSD.

---

### 3. Configuration du système de base (À effectuer sur les deux appareils)

Après le flashage, vous devez configurer chaque Raspberry Pi individuellement pour éviter les conflits réseau.

Pour de meilleures performances, ce guide utilise le Raspberry Pi 5 pour le Target Diretta (l'appareil connecté à votre DAC) et le Host Diretta. Vous configurerez le Host en premier.

> **AVERTISSEMENT CRUCIAL :** Étant donné que les deux appareils sont flashés à partir de la même image, ils auront des valeurs `machine-id` identiques. Si vous allumez les deux appareils en même temps alors qu'ils sont connectés au même réseau local, votre serveur DHCP leur attribuera probablement la même adresse IP, provoquant un conflit réseau.
>
> **Vous devez effectuer le premier démarrage et la configuration de chaque appareil l'un après l'autre.**

1.  Insérez la carte microSD dans le **premier** Raspberry Pi, connectez-le à votre réseau et allumez-le. **Note :** Si vous utilisez le boîtier Argon ONE, vous risquez d'entendre le bruit du ventilateur. Ne vous inquiétez pas. Une fois la configuration de Diretta terminée, des instructions sont disponibles dans l'[Annexe 1](#10-annexe-1--contrôle-optionnel-du-ventilateur-argon-one) pour y remédier.
2.  Effectuez **toute la Section 3** pour ce premier appareil.
3.  Une fois que le premier appareil a redémarré avec sa nouvelle configuration unique, éteignez-le.
4.  Maintenant, allumez le **second** Raspberry Pi et répétez **toute la Section 3** pour celui-ci.

Veuillez vous référer au reçu de votre achat Audiolinux pour connaître l'utilisateur SSH par défaut et les mots de passe sudo/root. Notez-les précieusement car vous les utiliserez de nombreuses fois tout au long de ce processus.

Vous utiliserez le client SSH de votre ordinateur local pour vous connecter aux Raspberry Pi tout au long de ce processus. Ce client nécessite que vous puissiez trouver l'adresse IP des Raspberry Pi, qui peut changer d'un redémarrage à l'autre. Le moyen le plus simple d'obtenir cette information est d'utiliser l'interface Web ou l'application de votre routeur domestique, mais vous pouvez également installer l'application [fing](https://www.fing.com/app/) sur votre smartphone ou tablette.

Une fois que vous avez l'adresse IP de l'un de vos Raspberry Pi, utilisez le client SSH de votre ordinateur local pour vous connecter en suivant ce processus. Prenez note de l'exemple de commande `ssh`, car vous utiliserez des commandes similaires tout au long de ce guide.
```bash
cmd=$(cat <<'EOT'
read -rp "Entrez l'adresse de votre RPi et appuyez sur [entrée] : " RPi_IP_Address
echo 'Rappel : le mot de passe par défaut se trouve dans votre e-mail AudioLinux de Piero'
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 3.1. Régénérer le Machine ID

Le `machine-id` est un identifiant unique pour l'installation de l'OS. Il **doit** être différent pour chaque appareil.

```bash
echo ""
echo "Ancien identifiant de machine : $(cat /etc/machine-id)"
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
echo "Nouvel identifiant de machine : $(cat /etc/machine-id)"
```

#### 3.2. Définir des Hostnames uniques

Définissez un hostname clair pour chaque appareil afin de l'identifier facilement. **Note :** S'il ne s'agit pas de votre première configuration avec ces instructions et que vous possédez déjà un couple Host/Target Diretta sur votre réseau, envisagez de choisir un nom différent pour ce nouveau Host Diretta, comme `diretta-host2`, juste pour cette étape. Cela facilitera l'accès indépendant aux deux appareils plus tard.

**Sur votre PREMIER appareil (le futur Host Diretta):**
```bash
# Sur le Host Diretta
sudo hostnamectl set-hostname diretta-host
```

**Sur votre SECOND appareil (le futur Target Diretta):**
```bash
# Sur le Target Diretta
sudo hostnamectl set-hostname diretta-target
```

**À ce stade, éteignez l'appareil. Répétez les [étapes ci-dessus](#3-configuration-du-système-de-base-à-effectuer-sur-les-deux-appareils) pour le second Raspberry Pi.**
```bash
sudo sync && sudo poweroff
```

---

### 4. Mises à jour du système (À effectuer sur les deux appareils)

Pour les étapes de cette section, il est généralement plus efficace (et moins déroutant) de terminer toute la Section 4 sur le Host Diretta, puis de répéter l'intégralité de la section sur le Target Diretta.

Chaque Raspberry Pi possède désormais son propre Machine ID, vous pouvez donc les allumer maintenant. Si vous disposez de deux câbles réseau, il est plus pratique de les connecter tous les deux à votre réseau domestique en même temps pour les étapes suivantes, mais vous pouvez également procéder un par un. **Note :** Votre routeur leur attribuera probablement des adresses IP différentes de celle utilisée initialement. Veillez à utiliser la nouvelle adresse IP avec vos commandes SSH. Voici un rappel :

```bash
cmd=$(cat <<'EOT'
read -rp "Entrez la (nouvelle) adresse de votre RPi et appuyez sur [entrée] : " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 4.1. Installer « Chrony » pour mettre à jour l'horloge système

L'horloge système doit être exacte avant de pouvoir installer des mises à jour. Le Raspberry Pi n'ayant pas de batterie NVRAM, l'horloge doit être réglée à chaque démarrage. Cela se fait généralement en se connectant à un service réseau. Ce script s'assurera que l'horloge est réglée et reste correcte pendant le fonctionnement de l'ordinateur.

```bash
sudo id
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh | sudo bash
sleep 5
chronyc sources
```

#### 4.2. Définir votre fuseau horaire

```bash
cmd=$(cat <<'EOT'
clear
echo "Bienvenue dans la configuration interactive du fuseau horaire."
echo "Vous sélectionnerez d'abord une région, puis un fuseau horaire spécifique."

# Permettre à l'utilisateur de sélectionner une région
PS3="Veuillez sélectionner un numéro pour votre région : "

select region in $(timedatectl list-timezones | grep -F / | cut -d/ -f1 | sort -u); do
  if [[ -n "$region" ]]; then
    echo "Vous avez sélectionné la région : $region"
    break
  else
    echo "Sélection invalide. Veuillez réessayer."
  fi
done

echo ""

# Permettre à l'utilisateur de sélectionner un fuseau horaire dans cette région
PS3="Veuillez sélectionner un numéro pour votre fuseau horaire : "

select timezone in $(timedatectl list-timezones | grep "^$region/"); do
  if [[ -n "$timezone" ]]; then
    echo "Vous avez sélectionné le fuseau horaire : $timezone"
    break
  else
    echo "Sélection invalide. Veuillez réessayer."
  fi
done

# Définir le fuseau horaire sélectionné
echo
echo "Configuration du fuseau horaire sur ${timezone}..."
sudo timedatectl set-timezone "$timezone"
echo "✅ Le fuseau horaire a été configuré."

# Vérifier le changement
echo
echo "Heure et fuseau horaire actuels du système :"
timedatectl status
EOT
)
bash -c "$cmd"
```

#### 4.3. Installer les DNS Utils
Installez le paquet `dnsutils` afin que la mise à jour du **menu** ait accès à la commande `dig` :
```bash
sudo pacman -S --noconfirm --needed dnsutils
```

#### 4.4. Exécuter les mises à jour du système et du menu

Utilisez le système de menus d'AudioLinux pour effectuer toutes les mises à jour. Munissez-vous de l'e-mail de Piero contenant votre identifiant et mot de passe de téléchargement de l'image. Vous en aurez besoin pour la mise à jour du menu. Il vous sera demandé **« your menu update user »**, ce qui est un peu déroutant : il s'agit de l'identifiant et du mot de passe que vous avez utilisés pour télécharger l'image d'installation d'AudioLinux.

1.  Exécutez `menu` dans le terminal.
2.  Sélectionnez **INSTALL/UPDATE menu**.
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
3.  Sur l'écran suivant, sélectionnez **UPDATE system** et laissez le processus se terminer.
4.  Une fois la mise à jour du système terminée, sélectionnez **Update menu** sur le même écran pour obtenir la dernière version des scripts AudioLinux. *Note :* Vous aurez besoin de l'adresse e-mail utilisée pour l'achat d'AudioLinux ainsi que de votre identifiant et mot de passe de téléchargement.
5.  Quittez le système de menus pour revenir au terminal.

#### 4.5. Redémarrer
Redémarrer pour charger le noyau et les autres mises à jour :
```bash
sudo sync && sudo reboot
```

---

### 5. Configuration réseau point à point

Dans cette section, nous allons créer les fichiers de configuration réseau qui activeront la liaison privée dédiée. Pour éviter d'avoir besoin d'un clavier et d'un écran physiques (accès console), nous effectuerons ces étapes pendant que les deux appareils sont encore connectés à votre réseau local principal et accessibles via SSH.

Si vous venez de terminer la mise à jour de votre Target Diretta, cliquez [ici](https://github.com/dsnyder0pc/rpi-for-roon/blob/main/Diretta.md#52-pre-configure-the-diretta-target) pour passer directement aux étapes de configuration réseau point à point pour le Target.

---
> #### **Note concernant la configuration réseau : Pourquoi pas un simple pont (bridge) ?**
>
> Les utilisateurs habitués à AudioLinux peuvent se demander pourquoi ce guide utilise des scripts spécifiques pour configurer une liaison point à point routée avec NAT plutôt que d'utiliser l'option de pont réseau (bridge) plus simple disponible dans le système de `menu`. Il s'agit d'un choix architectural délibéré visant à obtenir le niveau d'isolation réseau le plus élevé possible.
>
> * Un **pont réseau (bridge)** placerait le Target Diretta directement sur votre réseau local principal, l'exposant à tout le trafic broadcast et multicast réseau non pertinent.
> * Notre **configuration routée** crée un sous-réseau pare-feu complètement distinct. Le Host Diretta protège le Target de tous les bavardages réseau non essentiels, garantissant que le processeur du Target traite uniquement le flux audio. Cela minimise l'activité du système et le bruit électrique potentiel, ce qui est le but ultime de cette architecture puriste.
>
> Bien qu'un pont soit fonctionnellement plus simple à mettre en place, la méthode routée offre une base théoriquement supérieure pour les performances audio en maximisant l'isolation.
---

#### 5.1. Préconfigurer le Host Diretta

1.  **Créer les fichiers réseau :**
    Créez les deux fichiers suivants sur le **Host Diretta**. Le fichier `end0.network` définit l'adresse IP statique pour la future liaison point à point. Le fichier `usb-uplink.network` garantit que l'adaptateur Ethernet USB continue d'obtenir une adresse IP à partir de votre réseau local principal.

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

    **Important:** Supprimez l'ancien fichier en.network si present:
    ```bash
    # Supprimer l'ancien fichier réseau générique pour éviter les conflits.
    sudo rm -fv /etc/systemd/network/{en,enp,auto,eth}.network
    ```

    Ajouter une entrée dans `/etc/hosts` pour le Target Diretta :
    ```bash
    HOSTS_FILE="/etc/hosts"
    TARGET_IP="172.20.0.2"
    TARGET_HOST="diretta-target"

    # Ajouter une entrée pour le Target Diretta si elle n'existe pas
    if ! grep -q "$TARGET_IP\s\+$TARGET_HOST" "$HOSTS_FILE"; then
      printf "%s\t%s target\n" "$TARGET_IP" "$TARGET_HOST" | sudo tee -a "$HOSTS_FILE"
    fi
    ```

2.  **Activer le transfert IP (IP Forwarding) :**
    ```bash
    # L'activer pour la session en cours
    sudo sysctl -w net.ipv4.ip_forward=1

    # Le rendre permanent après les redémarrages
    echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ip-forwarding.conf
    ```

3.  **Configurer la traduction d'adresses réseau (NAT) :**
    ```bash
    # S'assurer que nft is installed
    sudo pacman -S --noconfirm --needed nftables

    # Installer les règles de pare-feu et de NAT
    cat <<'EOT' | sudo tee /etc/nftables.conf
    #!/usr/sbin/nft -f

    # Vider toutes les anciennes règles de la mémoire
    flush ruleset

    # Créer une table nommée 'ip' (IPv4) appelée 'my_table'
    table ip my_table {

        # === Règle 2 : Redirection de port (DNAT) ===
        # Cette chaîne s'accroche au chemin 'prerouting' pour le NAT
        chain prerouting {
            type nat hook prerouting priority dstnat;

            # Rediriger le port 5101 du Host vers le port 172.20.0.2:5001 du Target
            tcp dport 5101 dnat to 172.20.0.2:5001
        }

        # === Règle 3 : Autoriser le trafic redirigé (FILTER) ===
        # Cette chaîne s'accroche au chemin 'forward' pour le filtrage de paquets
        chain forward {
            type filter hook forward priority 0;

            # Par défaut, rejeter (drop) tout le trafic transféré
            policy drop;

            # Autoriser les connexions déjà établies ou apparentées
            ct state established,related accept

            # Autoriser le NOUVEAU trafic correspondant à votre règle de redirection
            ip daddr 172.20.0.2 tcp dport 5001 ct state new accept

            # Autoriser tout autre NOUVEAU trafic provenant du sous-réseau du Target
            ip saddr 172.20.0.0/24 accept
        }

        # === Règle 1 : Accès Internet (MASQUERADE) ===
        # Cette chaîne s'accroche au chemin 'postrouting' pour le NAT
        chain postrouting {
            type nat hook postrouting priority 100;

            # Masquer (NAT) le trafic provenant de votre sous-réseau sortant
            # par n'importe quelle interface commençant par 'enp', 'enu' ou 'wlp'
            ip saddr 172.20.0.0/24 oifname "enp*" masquerade
            ip saddr 172.20.0.0/24 oifname "enu*" masquerade
            ip saddr 172.20.0.0/24 oifname "wlp*" masquerade
        }
    }
    EOT

    # Arrêter et désactiver l'ancien service iptables s'il est présent (2>/dev/null supprime les erreurs s'il n'existe pas)
    sudo systemctl disable --now iptables.service 2>/dev/null
    sudo rm /etc/iptables/iptables.rules 2>/dev/null

    # Activer et appliquer les règles via nft
    sudo systemctl enable --now nftables.service
    ```

4.  **Configurer l'adaptateur USB vers Ethernet Plugable**

    Le pilote USB par défaut ne prend pas en charge toutes les fonctionnalités de l'adaptateur Ethernet Plugable. Pour obtenir des performances fiables, nous devons indiquer au gestionnaire de périphériques du noyau comment gérer l'appareil lorsqu'il est branché :
    ```bash
    cat <<'EOT' | sudo tee /etc/udev/rules.d/99-ax88179a.rules
    ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0b95", ATTR{idProduct}=="1790", ATTR{bConfigurationValue}!="1", ATTR{bConfigurationValue}="1"
    EOT
    sudo udevadm control --reload-rules
    ```

5.  **Corriger le script `update_motd.sh`**

    Le script qui met à jour la bannière de connexion (`/etc/motd`) ne gère pas correctement le cas de deux interfaces réseau. Cela évite que l'écran de connexion ne soit encombré d'informations d'adresse IP incorrectes après les redémarrages. Le nouveau script ci-dessous résout ce problème.
    ```bash
    [ -f /opt/scripts/update/update_motd.sh.dist ] || \
    sudo mv /opt/scripts/update/update_motd.sh /opt/scripts/update/update_motd.sh.dist
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh
    sudo install -m 0755 update_motd.sh /opt/scripts/update/
    rm update_motd.sh
    ```

    Enfin, éteignez le Host :
    ```bash
    sudo sync && sudo poweroff
    ```

#### 5.2. Préconfigurer le Target Diretta

**Note :** Si vous n'avez pas effectué l'[étape 4](#4-mises-à-jour-du-système-à-effectuer-sur-les-deux-appareils) sur le Target Diretta, faites-le [maintenant](#4-mises-à-jour-du-système-à-effectuer-sur-les-deux-appareils), puis revenez ici.

Sur le **Target Diretta**, créez le fichier `end0.network`. Cela configure son adresse IP statique et lui indique d'utiliser le Host Diretta comme passerelle pour tout le trafic Internet.

*Fichier : `/etc/systemd/network/end0.network`*
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

**Important :** Supprimez l'ancien fichier en.network s'il est présent :
```bash
# Supprimer l'ancien fichier réseau générique pour éviter les conflits.
sudo rm -fv /etc/systemd/network/{en,auto,eth}.network
```

Ajoutez une entrée /etc/hosts pour le Host Diretta. **Note :** Même si vous avez sélectionné un nom de réseau différent pour votre Host Diretta, il est préférable que le Target Diretta connaisse votre Host sous le nom de `diretta-host`.
```bash
HOSTS_FILE="/etc/hosts"
HOST_IP="172.20.0.1"
HOST_NAME="diretta-host"

# Ajouter une entrée pour le Host Diretta s'il n'existe pas
if ! grep -q "$HOST_IP\s\+$HOST_NAME" "$HOSTS_FILE"; then
  printf "%s\t%s host\n" "$HOST_IP" "$HOST_NAME" | sudo tee -a "$HOSTS_FILE"
fi
```

> ---
> ### ⚠️ Avertissement critique sur la topologie : Placement des filtres en amont uniquement
>
> Si vous prévoyez d'améliorer ce projet avec des régénérateurs LAN, des isolateurs galvaniques ou des filtres (tels que le StackAudio SmoothLAN, l'iFi SilentPower LAN iSilencer ou le LAN iPurifier Pro), ils **doivent être placés en amont du Host Diretta** (entre votre switch/routeur réseau principal et l'adaptateur USB vers Ethernet du Host).
>
> **Ne placez jamais de filtre réseau ou d'appareil de resynchronisation (reclocking) actif sur la liaison point à point entre le Host et le Target.** Cela dégraderait presque toujours les performances audio et pourrait provoquer de graves régressions de connexion.
>
> * **Le LAN principal est la principale source de bruit :** La connexion depuis votre routeur domestique ou votre switch principal est inondée d'interférences électromagnétiques (EMI), d'interférences radioélectriques (RFI) et de trafic de diffusion ("junk traffic") indésirable. Placer un régénérateur *avant* le Host élimine cette pollution numérique à la frontière. Le Host traite ensuite un flux propre, réduisant ainsi au minimum sa propre charge CPU, ses fluctuations de puissance et son bruit thermique.
> * **Préservation du timing de la Couche 2 (Layer 2) :** L'introduction d'un appareil actif sur le pont direct point à point interfère avec les contraintes de timing ultra-strictes de Diretta (`CycleTime` et `syncBufferCount`). Cela nuit à la livraison précise des trames de Couche 2, entraînant une diminution des gains sonores, des artefacts de latence ou un échec complet du Target à négocier les changements de vitesse réseau.
> * **Le principe de l'isolation en cascade :** Une véritable isolation est construite en couches pour découpler complètement votre DAC sensible du réseau domestique :
>   * **Réseau principal** → `[ LAN Filter/Regenerator ]` → **Host Diretta** *(Isole le Host du réseau domestique)*
>   * **Host Diretta** → `[ Câble Ethernet dédié ]` → **Target Diretta** *(Isolé via la liaison point à point et la pile de protocoles)*
> ---

#### 5.3. Modification de la connexion physique

> **Avertissement :** Vérifiez deux fois le contenu des fichiers que vous venez de créer. Une erreur de frappe pourrait rendre un appareil inaccessible après le redémarrage, nécessitant une session console ou un reflashage de la carte SD pour le réparer.

1.  Une fois que vous avez vérifié les fichiers, effectuez un arrêt propre des **deux** appareils :
    ```bash
    sudo sync && sudo poweroff
    ```
2.  Déconnectez les deux appareils de votre switch/routeur LAN principal.
3.  Connectez le **port Ethernet intégré** du Host Diretta directement au **port Ethernet intégré** du Target Diretta à l'aide d'un seul câble Ethernet.
4.  Branchez l'**adaptateur USB vers Ethernet** sur l'un des ports USB 3.0 bleus de l'ordinateur Host Diretta.
5.  Connectez l'**adaptateur USB vers Ethernet** du Host Diretta à votre switch/routeur LAN principal.
6.  Allumez les deux appareils.

Au démarrage, ils utiliseront automatiquement les nouvelles configurations réseau. **Note :** l'adresse IP de votre Host Diretta a probablement changé car il est maintenant connecté à votre réseau domestique via l'adaptateur USB vers Ethernet. Vous devrez retourner sur l'interface web de votre routeur ou utiliser l'application Fing pour trouver la nouvelle adresse, qui devrait être stable à ce stade.

```bash
cmd=$(cat <<'EOT'
read -rp "Entrez l'adresse finale de votre Host Diretta et appuyez sur [entrée] : " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

Vous devriez maintenant pouvoir pinger le Target depuis le Host :
```bash
echo ""
echo "\$ ping -c 3 172.20.0.2"
ping -c 3 172.20.0.2
```

De plus, vous devriez pouvoir vous connecter au Target depuis le Host :
```bash
echo ""
echo "\$ ssh target"
ssh -o StrictHostKeyChecking=accept-new target
```

Depuis le Target, essayons de pinger un hôte sur Internet pour vérifier que la connexion fonctionne :
```bash
echo ""
echo "\$ ping -c 3 one.one.one.one"
ping -c 3 one.one.one.one
```

---

### 6. Accès SSH pratique et sécurisé

#### 6.1. L'exigence du `ProxyJump`

Maintenant que le réseau est configuré, le **Target Diretta** se trouve sur un réseau isolé (`172.20.0.0/24`) et ne peut pas être atteint directement depuis votre réseau local principal. La seule façon d'y accéder est de passer ("jump") par le **Host Diretta**.

La directive `ProxyJump` dans votre configuration SSH locale est la méthode standard et requise pour y parvenir.

1.  Exécutez cette commande sur votre ordinateur local (pas sur le Raspberry Pi). Elle vous demandera l'adresse IP du Host Diretta, puis affichera le bloc de configuration exact dont vous avez besoin.
```bash
cmd=$(cat <<'EOT'
clear
# --- Script de configuration interactive des alias SSH ---

SSH_CONFIG_FILE="$HOME/.ssh/config"
SSH_DIR="$HOME/.ssh"

# --- S'assurer que le répertoire .ssh et le fichier config existent avec les permissions correctes ---
mkdir -p "$SSH_DIR"
chmod 0700 "$SSH_DIR"
touch "$SSH_CONFIG_FILE"
chmod 0600 "$SSH_CONFIG_FILE"

# --- Définir le bloc de paramètres globaux recommandé ---
GLOBAL_SETTINGS=$(cat <<'EOF'
# --- Paramètres SSH globaux recommandés ---
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519

EOF
)

# --- Préfixer les paramètres globaux s'ils n'existent pas ---
if ! grep -q "AddKeysToAgent yes" "$SSH_CONFIG_FILE"; then
  echo "✅ Ajout des paramètres SSH globaux recommandés..."
  # Utiliser un fichier temporaire pour ajouter les paramètres au début
  echo "$GLOBAL_SETTINGS" | cat - "$SSH_CONFIG_FILE" > temp_ssh_config && mv temp_ssh_config "$SSH_CONFIG_FILE"
else
  echo "✅ Les paramètres SSH globaux recommandés existent déjà. Aucune modification apportée."
fi

# --- Ajouter les configurations d'hôte spécifiques à Diretta ---
if grep -q "Host diretta-host" "$SSH_CONFIG_FILE"; then
  echo "✅ La configuration SSH pour 'diretta-host' existe déjà. Aucune modification apportée."
else
  read -rp "Entrez l'adresse IP LAN de votre Host Diretta et appuyez sur [Entrée] : " Diretta_Host_IP

  # Ajouter la nouvelle configuration en utilisant un heredoc pour plus de clarté
  cat <<EOT_HOSTS >> "$SSH_CONFIG_FILE"

# --- Configuration Diretta (ajoutée par le script) ---
Host diretta-host host
    HostName ${Diretta_Host_IP}
    User audiolinux

Host diretta-target target
    HostName 172.20.0.2
    User audiolinux
    ProxyJump diretta-host
EOT_HOSTS

  echo "✅ La configuration SSH pour 'diretta-host' et 'diretta-target' a été ajoutée."
fi

# --- Nettoyer StrictHostKeyChecking des anciennes versions de ce guide ---
# Ce n'est plus nécessaire avec la configuration de clé SSH recommandée
if command -v sed >/dev/null; then
    sed -i.bak -e '/StrictHostKeyChecking/d' "$SSH_CONFIG_FILE"
    # Supprimer les lignes vides qui pourraient subsister
    sed -i.bak -e '/^$/N;/^\n$/D' "$SSH_CONFIG_FILE"
    rm -f "${SSH_CONFIG_FILE}.bak"
fi

echo ""
echo "--- Votre fichier ~/.ssh/config contient désormais : ---"
cat "$SSH_CONFIG_FILE"
EOT
)
bash -c "$cmd"
```

2.  **Vérifier la connexion :**

Vous devriez maintenant pouvoir vous connecter aux deux appareils à l'aide des nouveaux alias. Testez la connexion avec les commandes suivantes :

**Pour vous connecter au Host Diretta :**
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-host
```

Tapez `exit` pour vous déconnecter.

**Pour vous connecter au Target Diretta :** _(le mot de passe vous sera demandé deux fois)_
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-target
```
**Note :** Le mot de passe vous est demandé une première fois pour diretta-host (la passerelle / jump box) et une seconde fois pour diretta-target lui-même. La section suivante remplacera cela par une authentification par clé transparente.

**Note :** Vous pouvez utiliser `ssh host` and `ssh target` pour faire court.

#### 6.2. Recommandé : Authentification sécurisée par clés SSH

Bien que vous puissiez utiliser des mots de passe, la méthode la plus sécurisée et la plus pratique est l'authentification par clé publique. Notre configuration SSH automatise la majeure partie du processus. Après une configuration unique, vous pourrez vous connecter au Host et au Target en toute sécurité, sans avoir à saisir de mot de passe.

**Sur votre ordinateur local :**

1.  **Créer une clé SSH (si vous n'en avez pas déjà une) :**
    Il est recommandé d'utiliser un algorithme moderne comme `ed25519`. Lorsque vous y êtes invité, saisissez une **phrase de passe** (passphrase) robuste et mémorable. Il ne s'agit pas de votre mot de passe de connexion, mais d'un mot de passe protégeant votre fichier de clé privée lui-même.

    ```bash
    ssh-keygen -t ed25519 -C "audiolinux"
    ```

2.  **Copier votre clé publique sur les appareils :**
    Ces commandes autorisent de manière sécurisée l'accès de votre clé à chaque appareil. La première commande demandera le mot de passe du Host Diretta. Comme cela rend la connexion au Host sans mot de passe, la deuxième commande ne demandera que le mot de passe du Target Diretta.

    ```bash
    echo ""
    ssh-copy-id diretta-host
    echo ""
    ssh-copy-id diretta-target
    ```

3.  **Se connecter en toute sécurité :**
    Vous pouvez maintenant vous connecter en SSH à vos appareils. La première fois que vous vous connecterez à chacun d'eux, il vous sera demandé la **phrase de passe** que vous avez créée à l'étape 1.

    ```bash
    ssh diretta-host
    ```

      * **Sous Linux :** Grâce au paramètre `AddKeysToAgent yes`, votre clé sera ajoutée à l'agent SSH pour votre session de terminal actuelle. La phrase de passe ne vous sera plus demandée jusqu'au redémarrage ou jusqu'à l'ouverture d'une nouvelle session.

---

### (Optionnel) Pour une meilleure expérience Linux

Si vous utilisez Linux et souhaitez que la phrase de passe de votre clé SSH persiste après les redémarrages (similaire à l'expérience sur macOS), l'installation de `keychain` est fortement recommandée.

  * **Installer keychain (Ubuntu/Debian) :**

    ```bash
    sudo apt update && sudo apt install keychain
    ```

  * **Configurer votre shell :** Ajoutez la ligne suivante à votre fichier `~/.bashrc` (ou `~/.zshrc`, `~/.profile`, etc.) pour démarrer `keychain` lorsque vous ouvrez un terminal. Il ne vous demandera votre phrase de passe qu'une seule fois, la première fois que vous ouvrirez un terminal après un redémarrage.

    ```bash
    eval "$(keychain --eval --quiet id_ed25519)"
    ```

  * Rechargez votre shell en ouvrant un nouveau terminal ou en exécutant `source ~/.bashrc`.

Vous pouvez désormais vous connecter en SSH aux deux appareils (`ssh diretta-host`, `ssh diretta-target`) sans mot de passe, authentifié de manière sécurisée par votre clé SSH.

---

### 7. Optimisations système courantes

Veuillez effectuer ces étapes sur le Host *et* le Target Diretta. Si vous effectuez une mise à jour via `menu` plus tard, vous devrez réexécuter le correctif `sudoers`.

#### 7.1. Corriger l'état « dégradé » (degraded) de systemd

Sur une nouvelle installation d'AudioLinux, l'état du système est souvent signalé comme `degraded` (dégradé). Cela est généralement causé par une incohérence inoffensive entre les fichiers de groupes du système (`/etc/group` et `/etc/gshadow`). La commande suivante synchronise ces fichiers en toute sécurité, ce qui résout l'échec de `shadow.service` et garantit un état système propre.

```bash
sudo grpconv
```

#### 7.2. Corriger la priorité des règles `sudoers`

Une règle par défaut dans le fichier principal `/etc/sudoers` peut parfois remplacer des règles plus spécifiques requises pour l'interface web et d'autres fonctionnalités. Cela peut amener des commandes qui devraient être sans mot de passe à en demander un de manière incorrecte.

Le script suivant corrige en toute sécurité l'ordre des règles dans le fichier `/etc/sudoers` pour garantir que les exceptions spécifiques sont traitées correctement. Le script n'effectuera des modifications que s'il détecte un ordre incorrect.

```bash
SUDOERS_FILE="/etc/sudoers"
TEMP_SUDOERS=$(mktemp)

# Utiliser un filtre Perl pour créer une version corrigée du fichier sudoers.
# Ce script est idempotent et ne modifiera pas un fichier déjà correct.
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

# Valider le nouveau fichier avec visudo avant l'installation
if [ -s "$TEMP_SUDOERS" ] && sudo visudo -c -f "$TEMP_SUDOERS"; then
    echo "Le fichier sudoers a été validé avec succès. Installation de la version corrigée..."
    # Utiliser install pour définir les propriétaires/permissions corrects et remplacer l'original
    sudo install -m 0440 -o root -g root "$TEMP_SUDOERS" "$SUDOERS_FILE"
else
    echo "ERREUR : La validation du fichier sudoers modifié a échoué. Aucune modification n'a été apportée." >&2
fi
rm -f "$TEMP_SUDOERS"
```

#### 7.3. Optimiser le temps de démarrage
Pour éviter un long délai de démarrage pendant que le système attend une connexion réseau, nous allons désactiver le service « wait-online ».
```bash
# Désactiver le service d'attente réseau pour éviter de longs délais de démarrage
sudo systemctl disable systemd-networkd-wait-online.service

# Créer une surcharge pour que le script MOTD attende une route par défaut
sudo mkdir -p /etc/systemd/system/update_motd.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/update_motd.service.d/wait-for-ip.conf
[Service]
ExecStartPre=/bin/sh -c "while [ -z \"$(ip route show default)\" ]; do sleep 0.5; done"
EOT
```

#### 7.4. Créer le script de réparation
Le comportement par défaut d'Arch Linux est de laisser le système de fichiers /boot dans un état incorrect si l'ordinateur n'est pas arrêté proprement. C'est généralement sans danger, mais j'ai constaté que cela peut créer une condition de concurrence lors du démarrage de notre réseau privé. De plus, les utilisateurs ont tendance à débrancher ces appareils sans les éteindre au préalable. Pour se prémunir de ces problèmes, nous allons ajouter un script de contournement qui maintient propre le système de fichiers /boot (qui n'est modifié que lors des mises à jour logicielles).

Ce script peut être exécuté en toute sécurité, à la fois automatiquement au démarrage et manuellement sur un système en cours d'exécution.
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh
sudo install -m 0755 check-and-repair-boot.sh /usr/local/sbin/
rm check-and-repair-boot.sh
```

#### 7.5. Créer le fichier de service `systemd` et activer le service
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

#### 7.6. Minimiser les E/S disque
Remplacer `#Storage=auto` par `Storage=volatile` dans `/etc/systemd/journald.conf`
```bash
sudo sed -i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
```

---

### 8. Installation et configuration du logiciel Diretta

#### 8.1. Sur le Target Diretta

1.  Connectez votre DAC USB à l'un des ports USB 2.0 noirs sur le **Target Diretta** et assurez-vous que le DAC est sous tension.
2.  Connectez-vous en SSH au Target : `ssh diretta-target`.
3.  Configurer la chaîne de compilation (compiler toolchain) compatible
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```
4.  Exécutez `menu`.
5.  Sélectionnez **AUDIO extra menu**.
6.  Sélectionnez **DIRETTA target installation/configuration**. Vous verrez le menu suivant :
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
7.  Vous devez effectuer ces actions dans l'ordre :
    * Choisissez **1) Install/update** pour installer le logiciel (répondez « Y » à toutes les invites).
    * Choisissez **2) Enable/Disable Diretta Target** et activez-le.
    * Choisissez **3) Configure Audio card**. Le système listera vos périphériques audio disponibles. Saisissez le numéro de carte correspondant à votre DAC USB.
        ```text
        ?3
        This option will set DIRETTA target to use a specific card
        Your available cards are:

        card 0: AUDIO [SMSL USB AUDIO], device 0: USB Audio [USB Audio]

        Please type the card number (0,1,2...) you want to use:
        ?0
        ```
    * Choisissez **4) Edit configuration**. Réglez `AlsaLatency=20` pour un Target Raspberry Pi 5 ou `AlsaLatency=40` pour un RPi4.
    * Choisissez **6) License**. Le système lira de l'audio haute résolution (supérieur à 44,1 kHz PCM) pendant 6 minutes en mode d'évaluation. Suivez le lien et les instructions à l'écran pour acheter et appliquer votre licence complète pour la prise en charge de la haute résolution. Cela nécessite l'accès Internet que nous avons configuré à l'étape 5.
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
    * Choisissez **8) Exit**. Suivez les invites pour revenir au terminal

#### 8.2. Sur le Host Diretta

1.  Connectez-vous en SSH au Host : `ssh diretta-host`.

2.  Configurer la chaîne de compilation (compiler toolchain) compatible
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```

3.  Exécutez `menu`.

4.  Sélectionnez **AUDIO extra menu**.

5.  Sélectionnez **DIRETTA host installation/configuration**. Vous verrez le menu suivant :
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

6.  Vous devez effectuer ces actions dans l'ordre :
    * Choisissez **1) Install/update** pour installer le logiciel (répondez « Y » à toutes les invites). *(Note : vous pourriez voir `error: package 'lld' was not found`. Ne vous inquiétez pas, cela sera corrigé automatiquement par l'installation)*
    * Choisissez **2) Enable/Disable Diretta daemon** et activez-le.
    * Choisissez **3) Set Ethernet interface**. Il est crucial de sélectionner `end0`, l'interface pour la liaison point à point.
        ```text
        ?3
        Your available Ethernet interfaces are: end0  enu1
        Please type the name of your preferred interface:
        end0
        ```
    * Choisissez **4) Edit configuration** uniquement si vous devez effectuer des modifications avancées. Les étapes précédentes devraient suffire ; cependant, voici quelques paramètres optimisés que vous pourriez souhaiter essayer :
        ```text
        ScanOnlineStop=enable
        InfoCycle=80000
        FlexCycle=disable
        CycleTime=800
        periodMin=16
        periodSizeMin=2048
        ```

    * Si vous souhaitez simplement installer les paramètres optimisés ci-dessus, vous pouvez utiliser ce bloc de commande :
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
    * Choisissez **7) Exit**. Suivez les invites pour revenir au terminal

7.  Créer une surcharge pour redémarrer automatiquement le service Diretta en cas de défaillance
    ```bash
    sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta_alsa.service.d/restart.conf
    [Service]
    Restart=on-failure
    RestartSec=5
    EOT
    ```

---

### 9. Étapes finales et intégration Roon

1.  Exécutez `menu` si vous êtes revenu au terminal après l'étape précédente, sinon allez au **Main menu** (Menu principal).

2.  **Installer Roon Bridge (sur le Host) :** Si vous utilisez Roon, effectuez les étapes suivantes sur le **Host Diretta** :
    * Exécutez `menu`.
    * Sélectionnez **INSTALL/UPDATE menu**.
    * Sélectionnez **INSTALL/UPDATE Roonbridge**.
    * L'installation va se poursuivre. L'installation peut prendre une minute ou deux.

3.  **Activer Roon Bridge (sur le Host) :**
    * Sélectionnez **Audio menu** depuis le Main menu (Menu principal)
    * Sélectionnez **SHOW audio service**
    * Si vous ne voyez pas **roonbridge** sous les services activés, sélectionnez **ROONBRIDGE enable/disable**

4.  **Redémarrer les deux appareils :** Pour un démarrage propre, redémarrez le Target et le Host, dans cet ordre :
    ```bash
    sudo sync && sudo reboot
    ```

5.  **Configurer Roon :**
    * Ouvrez Roon sur votre périphérique de contrôle.
    * Allez dans `Settings` -> `Audio` (Paramètres -> Audio).
    * Sous `diretta-host`, vous devriez voir votre appareil. Le nom sera basé sur votre DAC.
    * Cliquez sur `Enable` (Activer), donnez-lui un nom, et vous êtes prêt à écouter de la musique !

Votre liaison Diretta dédiée est maintenant entièrement configurée pour une lecture audio pure et isolée.
**Note :** La zone « Limited » pour le test du Target Diretta disparaîtra de Roon après six minutes de lecture de musique haute résolution. C'est tout à fait normal. À ce stade, vous devrez acheter une licence pour le Target Diretta. Le coût est actuellement de 100 € et l'activation peut prendre jusqu'à 48 hours. Vous recevrez deux e-mails de l'équipe Diretta. Le premier est votre reçu ; le second, votre notification d'activation. Une fois l'e-mail d'activation reçu, redémarrez votre ordinateur Target pour appliquer l'activation.

> ---
> ### ✅ Checkpoint : Vérifiez votre système de base
>
> Votre système Diretta et Roon de base devrait maintenant être pleinement opérationnel. Pour vérifier tous les services et connexions, veuillez vous rendre à l'[**Annexe 5**](#14-annexe-5--system-health-checks-vérifications-de-létat-du-système) et exécuter la commande universelle **System Health Check** sur le Host et le Target.
>
> ---

---

## 10. Annexe 1 : Contrôle optionnel du ventilateur Argon ONE
Si vous avez décidé d'utiliser un boîtier Argon ONE pour votre Raspberry Pi, le script d'installation par défaut suppose que vous utilisez un système d'exploitation Debian. Cependant, Audiolinux est basé sur Arch Linux, vous devrez donc suivre ces étapes à la place.

Si vous utilisez des boîtiers Argon ONE pour le Host et le Target Diretta, vous devrez effectuer ces étapes sur les deux ordinateurs.

### Étape 1 : Ignorer le script `argon1.sh` dans le manuel
Le manuel indique de télécharger le script argon1.sh depuis download.argon40.com et de le rediriger vers `bash`. Cela ne fonctionnera pas sur Audiolinux car le script suppose un système d'exploitation basé sur Debian, ignorez donc cette étape et suivez les étapes ci-dessous à la place.

### Étape 2 : Configurer votre système :
Ces commandes activeront l'interface I2C et ajouteront le `dtoverlay` spécifique pour le boîtier Argon ONE. Le script tente d'abord de décommenter le paramètre `i2c_arm` s'il est commenté, puis ajoute l'overlay `argonone` s'il est manquant, évitant ainsi les erreurs et les entrées en double.
```bash
BOOT_CONFIG="/boot/config.txt"
I2C_PARAM="dtparam=i2c_arm=on"

# --- Activer l'I2C en décommentant la ligne si elle existe ---
if grep -q -F "#$I2C_PARAM" "$BOOT_CONFIG"; then
  echo "Enabling I2C parameter..."
  sudo sed -i -e "s/^#\($I2C_PARAM\)/\1/" "$BOOT_CONFIG"
fi
```

### Étape 3 : Configurer les permissions `udev`
```bash
cat <<'EOT' | sudo tee /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c-[0-9]*", MODE="0666"
EOT
```

### Étape 4 : Installer le paquet Argon One
```bash
yay -S argonone-c-git
```

**Note :** Si la commande ci-dessus échoue avec des erreurs de compilation, vous pouvez essayer cette procédure manuelle pour corriger et installer le paquet :
```bash
# Cloner le dépôt du paquet
git clone https://aur.archlinux.org/argonone-c-git.git
cd argonone-c-git

# Télécharger le code source sans compiler
makepkg -o

# Appliquer le patch pour corriger l'erreur de compilation avec GCC 14+
sed -i 's/_timer_thread()/_timer_thread(void *args)/g' src/argonone-c-git/src/event_timer.c

# Compiler et installer à l'aide de la source patchée
makepkg -e -i --noconfirm

# Nettoyer
cd ..
rm -rf argonone-c-git
```

### Étape 5 : Basculer le boîtier Argon ONE du contrôle matériel au contrôle logiciel
```bash
sudo pacman -S --noconfirm --needed i2c-tools libgpiod
```

```bash
# Créer des surcharges systemd pour basculer le boîtier en mode logiciel au démarrage
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

### Étape 6 : Activer le service
```bash
# Recharger le gestionnaire systemd pour lire la nouvelle configuration
sudo systemctl daemon-reload

# Activer le service pour démarrer au boot
sudo systemctl enable argononed.service
```

### Étape 7 : Redémarrer
Enfin, redémarrez votre Raspberry Pi pour que tous les changements prennent effet (le Target en premier, puis le Host) :
```bash
sudo sync && sudo reboot
```

Désormais, le ventilateur sera contrôlé par le démon, et le bouton d'alimentation sera pleinement fonctionnel.

### Étape 8 : Vérifier le service
```bash
systemctl status argononed.service
journalctl -u argononed.service -b
```

### Étape 9 : Vérifier le mode de ventilation et les paramètres :
Pour voir les valeurs de configuration actuelles, exécutez la commande suivante :
```bash
sudo argonone-cli --decode
```

Pour ajuster ces valeurs, vous devez créer un fichier de configuration. Utilisez ces valeurs pour commencer :
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

Redémarrez le service pour appliquer les nouvelles valeurs de configuration :
```bash
sudo systemctl restart argononed.service
echo ""
echo "Valeurs mises à jour du ventilateur :"
sleep 5
sudo argonone-cli --decode
```

À présent, n'hésitez pas à ajuster les valeurs selon vos besoins, en suivant les étapes ci-dessus.

---

## 11. Annexe 2 : Télécommande IR optionnelle

Ce guide fournit des instructions pour installer et configurer une télécommande IR afin de contrôler Roon. La configuration est divisée en deux parties.

  * **La partie 1** concerne la configuration matérielle. Vous choisirez **l'une** des deux options selon que vous utilisez le récepteur USB Flirc ou le récepteur intégré du boîtier Argon One.
  * **La partie 2** concerne la configuration logicielle du script de contrôle `roon-ir-remote`, identique pour les deux options matérielles.

**Note :** Vous n'effectuerez ces étapes *que* sur le Host Diretta. Le Target ne doit pas être utilisé pour relayer les commandes de la télécommande IR vers Roon Server.

---

### **Partie 1 : Configuration matérielle du récepteur IR**

*Suivez l'annexe correspondant au matériel que vous utilisez.*

#### **Option 1 : Configuration du récepteur IR USB Flirc**

1.  **Acheter et programmer l'appareil Flirc :**
    Vous aurez besoin du récepteur IR USB Flirc, qui peut être acheté sur leur site web : [https://flirc.tv/products/flirc-usb-receiver](https://flirc.tv/products/flirc-usb-receiver)

    L'appareil Flirc doit être programmé sur un ordinateur de bureau à l'aide du logiciel Flirc GUI.

      * Branchez le Flirc sur votre ordinateur de bureau et ouvrez Flirc GUI.
      * Allez dans `Controllers` (Contrôleurs) et sélectionnez `Full Keyboard` (Clavier complet).
      * Programmez les touches nécessaires pour le script (par ex., KEY_UP, KEY_DOWN, KEY_ENTER, etc.) en cliquant sur la touche dans l'interface graphique, puis en appuyant sur le bouton correspondant de votre télécommande physique.
      * Une fois programmé, branchez le Flirc sur le **Host Diretta**.

2.  **Tester l'appareil Flirc :**
    Vérifiez que le Raspberry Pi reconnaît le Flirc comme un clavier.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Sélectionnez le périphérique « Flirc » dans le menu. Lorsque vous appuyez sur les boutons de votre télécommande, vous devriez voir les événements clavier s'afficher à l'écran.

3.  Passez à la [Partie 2 : Configuration logicielle du script de contrôle](#part-2-control-script-software-setup)

---

#### **Option 2 : Configuration de la télécommande IR Argon One**

1.  **Activer le matériel du récepteur IR :**
    Vous devez activer l'overlay matériel pour le récepteur IR du boîtier Argon One.

      * Cette commande ajoutera en toute sécurité l'overlay matériel requis à votre fichier `/boot/config.txt`, après avoir vérifié qu'il n'y figure pas déjà.
        ```bash
        BOOT_CONFIG="/boot/config.txt"
        IR_CONFIG="dtoverlay=gpio-ir,gpio_pin=23"

        # Ajouter l'overlay de la télécommande IR s'il n'y est pas déjà
        if ! sed 's/#.*//' $BOOT_CONFIG | grep -q -F "$IR_CONFIG"; then
          echo "Activation du récepteur IR Argon One..."
          sudo sed -i "/# Uncomment this to enable infrared communication./a $IR_CONFIG" /boot/config.txt
        else
          echo "Le récepteur IR Argon One est déjà activé."
        fi
        ```
      * Un redémarrage est nécessaire pour que la modification matérielle prenne effet.
        ```bash
        sudo sync && sudo reboot
        ```

2.  **Installer les outils IR et activer les protocoles :**
    Installez `ir-keytable`
    ```bash
    sudo pacman -S --noconfirm v4l-utils
    ```

3.  **Capturer les scancodes des boutons :**
     Activez tous les protocoles du noyau afin qu'il puisse décoder les signaux de votre télécommande. Exécutez l'outil de test pour voir le scancode unique de chaque bouton.
    ```bash
    sudo ir-keytable -p all
    sudo ir-keytable -t
    ```

    Appuyez sur chaque bouton que vous souhaitez utiliser et notez son scancode à partir de la sortie de l'événement `MSC_SCAN` (par ex., `value ca`). Appuyez sur `Ctrl+C` lorsque vous avez terminé.

4.  **Créer le fichier de configuration des touches (Keymap) :**
    Ce fichier associe les scancodes à des noms de touches standards.

      * Créez un nouveau fichier keymap :
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
      * Si les codes de balayage (scancodes) dans l'exemple de fichier ci-dessus ne correspondent pas à ceux que vous avez enregistrés, modifiez le fichier (`sudo nano /etc/rc_keymaps/argon.toml`) et changez-les pour qu'ils correspondent.

5.  **Créer un service `systemd` pour charger la configuration des touches (Keymap) :**
    Ce service chargera automatiquement votre keymap au démarrage.

    Créez un nouveau fichier de service et activez le service :
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

6.  **Tester le périphérique d'entrée :**
    Vérifiez que le système reçoit bien les événements clavier de la télécommande IR.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Sélectionnez le périphérique `gpio_ir_recv`. Lorsque vous appuyez sur les boutons de la télécommande, vous devriez voir les événements de touches correspondants.
    Tapez `CTRL-C` lorsque vous avez terminé les tests.

---

### **Partie 2 : Configuration logicielle du script de contrôle**

*Après avoir configuré votre matériel dans la partie 1, suivez ces étapes pour installer et configurer le script de contrôle Python.*

### **Étape 1 : Ajouter `audiolinux` au groupe `input`**
Cela est nécessaire pour que le compte `audiolinux` ait accès aux événements du récepteur de la télécommande.
```bash
sudo usermod --append --groups input audiolinux
```
Déconnectez-vous et reconnectez-vous pour que cette modification prenne effet. Vous pouvez vérifier avec cette commande :
```bash
echo ""
echo ""
echo "Vérification de vos appartenances aux groupes :"
echo "\$ groups"
groups
echo ""
echo "Ci-dessus, vous devriez voir :"
echo "audiolinux realtime video input audio wheel"
```

---

### **Étape 2 : Installer Python via `pyenv`**

Installez `pyenv` et la dernière version stable de Python.

```bash
# Installer les dépendances de compilation
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

# Installer pyenv uniquement s'il n'est pas déjà installé
if [ ! -d "$HOME/.pyenv" ]; then
  echo "--- Installation de pyenv ---"
  curl -fsSL https://pyenv.run | bash
else
  echo "--- pyenv est déjà installé. Installation ignorée. ---"
fi

# Configurer le shell pour pyenv
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

# Charger le fichier pour rendre pyenv disponible dans le shell actuel
. ~/.bashrc

# Installer et définir la dernière version de Python uniquement si elle n'est pas déjà installée
PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')

if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
    # Obtenir la mémoire totale en Mo
    TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

    if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- La RAM physique est de ${TOTAL_MEM}Mo. Limitation à 1 cœur pour éviter tout blocage. ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
    else
        echo "--- La RAM physique est de ${TOTAL_MEM}Mo. Poursuite de la compilation en parallèle. ---"
    fi

    echo "--- Installation de Python ${PYVER}. Cela va prendre plusieurs minutes... ---"
    pyenv install "$PYVER"
    [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
else
    echo "--- Python ${PYVER} est déjà installé. ---"
fi

pyenv global "$PYVER"
```

**Note :** Il est normal que l'étape `Installing Python-3.14.5...` prenne environ 10 minutes car elle compile Python à partir des sources. N'abandonnez pas ! N'hésitez pas à vous détendre en écoutant de la belle musique sur votre nouvelle zone Diretta dans Roon pendant que vous attendez. Elle devrait être disponible pendant l'installation de Python sur le Host.

---

### **Étape 3 : Télécharger le dépôt du logiciel `roon-ir-remote`**

Clonez le dépôt du script et récupérez un patch pour gérer correctement les codes de touches par nom plutôt que par numéro.

```bash
cd
# Cloner le dépôt s'il n'existe pas, sinon le mettre à jour
if [ ! -d "roon-ir-remote" ]; then
  git clone https://github.com/dsnyder0pc/roon-ir-remote.git
else
  (cd roon-ir-remote && git pull)
fi
```

---

### **Étape 4 : Créer le fichier de configuration de l'environnement Roon**

Configurez le script avec vos informations Roon. **Note :** Les codes de `event_mapping` doivent correspondre aux noms de touches que vous avez définis dans votre configuration matérielle (`KEY_ENTER`, `KEY_VOLUMEUP`, etc.).

```bash
bash <<'EOF'
# --- Début du script ---

# Obtenir la zone Roon et la stocker dans une variable
echo "Saisissez le nom de votre zone Roon."
echo "IMPORTANT : Cela doit correspondre exactement au nom de la zone dans l'application Roon (sensible à la casse)."
# Cette ligne est la correction : < /dev/tty indique à read d'utiliser le terminal
read -rp "Entrez le nom de votre zone Roon : " MY_ROON_ZONE < /dev/tty

# Détecter si le mappage Flirc/Keyboard est nécessaire
if [ -f "/etc/systemd/system/ir-keymap.service" ]; then
    VOL_UP_CODE="KEY_VOLUMEUP"
    VOL_DOWN_CODE="KEY_VOLUMEDOWN"
    echo "--- Récepteur IR standard détecté. Utilisation de KEY_VOLUMEUP/DOWN. ---"
else
    VOL_UP_CODE="KEY_UP"
    VOL_DOWN_CODE="KEY_DOWN"
    echo "--- Adaptateur Flirc/HID détecté. Utilisation de KEY_UP/DOWN pour le volume. ---"
fi

# S'assurer que le répertoire cible existe
mkdir -p roon-ir-remote

# Créer le fichier de configuration à l'aide d'un Here Document
# La variable va maintenant être correctement substituée
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
echo "✅ Fichier de configuration 'roon-ir-remote/app_info.json' créé avec succès."

# --- Fin du script ---
EOF
```

---

### **Étape 5 : Préparer et tester `roon-ir-remote`**

Installez les dépendances du script dans un environnement virtuel et exécutez-le pour la première fois.

```bash
cd ~/roon-ir-remote
# Créer l'environnement virtuel uniquement s'il n'existe pas déjà
if ! pyenv versions --bare | grep -q "^roon-ir-remote$"; then
  echo "--- Création de l'environnement virtuel 'roon-ir-remote' ---"
  pyenv virtualenv roon-ir-remote
else
  echo "--- L'environnement virtuel 'roon-ir-remote' existe déjà ---"
fi
pyenv activate roon-ir-remote
pip3 install --upgrade pip
pip3 install -r requirements.txt

python roon_remote.py
```

La première fois que vous exécutez le script, vous devez **autoriser l'extension dans Roon** en allant dans `Settings` -> `Extensions` (Paramètres -> Extensions).

Pendant que de la musique est lue dans votre nouvelle zone Diretta Roon, pointez votre télécommande IR directement vers l'ordinateur Host Diretta et appuyez sur le bouton Lecture/Pause (qui peut être le bouton central du contrôleur à 5 directions). Essayez également Suivant et Précédent. Si cela ne fonctionne pas, vérifiez si votre fenêtre de terminal affiche des messages d'erreur. Une fois que vous avez terminé les tests, tapez `CTRL-C` pour quitter.

---

### **Étape 6 : Créer un service `systemd`**

Créez un service pour exécuter le script automatiquement en arrière-plan.

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

# Activer et démarrer le service
sudo systemctl daemon-reload
sudo systemctl enable --now roon-ir-remote.service

# Vérifier le statut
sudo systemctl status roon-ir-remote.service
```

---

### **Étape 7 : Surveiller les journaux pendant un court instant :**
```bash
journalctl -b -u roon-ir-remote.service -f
```

Tapez `CTRL-C` une fois que vous êtes convaincu que tout fonctionne comme prévu.

---

### **Étape 8 : Installer le script `set-roon-zone`**
Il est utile de disposer d'un script permettant de mettre à jour le nom de la zone Roon plus tard si nécessaire. Voici comment l'installer :
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone
sudo install -m 0755 set-roon-zone /usr/local/bin/
rm set-roon-zone
```

Pour l'utiliser, connectez-vous simplement à l'ordinateur Host Diretta et tapez :
```bash
set-roon-zone
```
Suivez les invites pour saisir le nouveau nom de votre zone Roon. Vous devrez peut-être saisir le mot de passe root pour que les modifications prennent effet.

**Note : Une meilleure méthode pour configurer la zone**
Bien que ce script fonctionne parfaitement, la méthode recommandée pour modifier la zone Roon est d'utiliser l'application web AnCaolas Link System Control, détaillée dans l'[Annexe 4](#13-annexe-4--interface-web-optionnelle-de-contrôle-du-système). L'interface web fournit une page dédiée pour visualiser et modifier le nom de la zone depuis votre téléphone ou votre navigateur.

### **Étape 9 : Profitez-en ! 📈**

> ---
> ### ✅ Checkpoint : Vérifiez la configuration de votre télécommande IR
>
> Le matériel et le logiciel de votre télécommande IR devraient maintenant être configurés. Pour vérifier la configuration, rendez-vous à l'[**Annexe 5**](#14-annexe-5--system-health-checks-vérifications-de-létat-du-système) et exécutez la commande universelle **System Health Check** sur le Host Diretta.
>
> ---

Votre télécommande IR devrait maintenant contrôler Roon. Profitez-en bien !

---

## 12. Annexe 3 : Mode puriste optionnel
Il y a très peu d'activité réseau et d'arrière-plan sur l'ordinateur Target Diretta qui ne soit pas liée à la lecture de musique utilisant le protocole Diretta. Cependant, certains utilisateurs préfèrent prendre des mesures supplémentaires pour réduire le risque d'une telle activité. Nous sommes déjà à l'extrême limite des performances audio, alors pourquoi s'en priver ?

---
> AVERTISSEMENT CRITIQUE : Pour le Target Diretta UNIQUEMENT
>
> Le script `purist-mode` et toutes les instructions de cette annexe sont conçus exclusivement pour le Target Diretta.
>
> N'installez pas et n'exécutez pas ce script sur le Host Diretta. Cela couperait la connexion du Host à votre réseau principal, le rendant inaccessible et incapable de communiquer avec votre Roon Core ou vos services de streaming. Cela rendrait l'ensemble du système inutilisable jusqu'à ce que vous puissiez obtenir un accès console (avec un clavier et un écran physiques) pour annuler les modifications.
---

### Étape 1 : Installer le script `purist-mode` **(uniquement sur l'ordinateur Target Diretta)**
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode
sudo install -m 0755 purist-mode /usr/local/bin
rm purist-mode

# Script pour afficher le statut du Mode Puriste lors de la connexion
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

Pour l'exécuter, connectez-vous simplement au Target Diretta et tapez `purist-mode` :
```bash
purist-mode
```

Par exemple :
```text
[audiolinux@diretta-target ~]$ purist-mode
This script requires sudo privileges. You may be prompted for a password.
🚀 Activating Purist Mode...
  -> Stopping time synchronization service (chronyd)...
  -> Disabling DNS lookups...
  -> Overriding gateway with high-priority blackhole route...

✅ Purist Mode is ACTIVE.
```

Écoutez pendant un moment pour voir si vous préférez le son (ou la tranquillité d'esprit).

---

### Étape 2 : Activer le Mode Puriste par défaut

Si vous avez décidé que vous préférez le son lorsque le Mode Puriste est activé, faites-en le choix par défaut après chaque redémarrage.

```bash
echo ""
echo "- Désactivation du Purist Mode pour garantir un état propre"
purist-mode --revert

echo ""
echo "- Création du service pour revenir au Standard Mode à chaque démarrage"
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
echo "- Création du service d'auto-activation différée"
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
echo "- Activation des nouveaux services"
sudo systemctl daemon-reload
sudo systemctl enable purist-mode-revert-on-boot.service
sudo systemctl enable purist-mode-auto.service
```

---

### Étape 3 : Installer un wrapper autour de la commande `menu`
De nombreuses fonctions d'AudioLinux nécessitent un accès Internet. Pour que tout fonctionne comme prévu, ajoutez un wrapper autour de la commande `menu` qui désactive le mode Puriste pendant que vous utilisez le menu, puis le réactive lorsque vous quittez pour revenir au terminal.

```bash
if grep -q menu_wrapper ~/.bashrc; then
  :
else
  echo ""
  echo "Ajouter un wrapper autour de la commande menu"
  cat <<'EOT' | tee -a ~/.bashrc

# Custom wrapper pour le menu AudioLinux afin de gérer le Mode Puriste
menu_wrapper() {
  local was_active=false
  # Vérifier l'état initial du Mode Puriste en recherchant le fichier de sauvegarde.
  if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
    was_active=true
  fi

  # Si le Mode Puriste était actif, l'annuler temporairement pour le menu.
  if [ "$was_active" = true ]; then
    echo "Vérification des identifiants pour gérer le Purist Mode..."
    sudo -v

    echo "Désactivation temporaire du Purist Mode pour exécuter menu..."
    purist-mode --revert > /dev/null 2>&1 # Revert quietly
  fi

  # Appeler la commande menu d'origine
  /usr/bin/menu

  # Si le Mode Puriste était actif auparavant, le réactiver maintenant.
  if [ "$was_active" = true ]; then
    echo "Réactivation du Purist Mode..."
    purist-mode > /dev/null 2>&1 # Activate quietly
    echo "Le Purist Mode est de nouveau actif."
  fi
}

# Associer la commande 'menu' par alias à notre nouvelle fonction wrapper
alias menu='menu_wrapper'
# Alias pour gérer le service automatique du Mode Puriste
alias purist-mode-auto-enable='echo "Activation du Purist Mode au démarrage..."; purist-mode; sudo systemctl enable purist-mode-auto.service'
alias purist-mode-auto-disable='echo "Désactivation du Purist Mode au démarrage..."; purist-mode --revert; sudo systemctl disable --now purist-mode-auto.service'
EOT
fi

source ~/.bashrc
```

---

### Comprendre les états du Mode Puriste

Le système du Mode Puriste est conçu pour être flexible, vous permettant de le contrôler manuellement ou de l'activer automatiquement après le démarrage du système. Il fonctionne selon deux états principaux :

  * **Désactivé (Mode Standard) :**
    Il s'agit de l'état normal et pleinement fonctionnel du Target Diretta. La passerelle réseau est active, tous les services (`chronyd`, `argononed`) sont en cours d'exécution et l'appareil fonctionne sans restrictions.

  * **Actif (Mode Puriste) :**
    C'est l'état optimisé pour une écoute attentive. La passerelle réseau est coupée pour empêcher le trafic Internet, et les services d'arrière-plan non essentiels (y compris le ventilateur de l'Argon ONE) sont arrêtés pour minimiser toute interférence système potentielle.

Ces états sont gérés de deux manières : **automatiquement** au démarrage et **manuellement** via la ligne de commande.

#### Contrôle automatique (au démarrage)

Le processus de démarrage est conçu pour être sûr et prévisible, avec une bascule automatisée optionnelle vers le Mode Puriste.

1.  **Annulation obligatoire au démarrage :** Quel que soit l'état dans lequel il se trouvait lors de l'arrêt, le Target Diretta démarre **toujours** en **Mode Standard** en premier. C'est une fonctionnalité essentielle qui garantit le bon fonctionnement des services indispensables, tels que la synchronisation temporelle du réseau.

2.  **Activation automatique optionnelle :** Si vous avez activé la fonctionnalité automatique, le système attendra 60 secondes après le démarrage, puis basculera automatiquement en **Mode Puriste**. Cela offre une expérience simplifiée (« configurez et oubliez ») pour les utilisateurs qui préfèrent toujours écouter dans l'état optimisé.

#### Contrôle manuel (utilisation interactive)

Vous disposez d'un contrôle interactif complet sur le système à tout moment.

  * Pour **activer manuellement** le Mode Puriste lors d'une session d'écoute, connectez-vous à l'ordinateur Target Diretta et exécutez :

    ```bash
    purist-mode
    ```

  * Pour **désactiver manuellement** le Mode Puriste et revenir au fonctionnement standard, exécutez :

    ```bash
    purist-mode --revert
    ```

  * Pour contrôler le **comportement au démarrage automatique**, utilisez les alias pratiques sur le Target Diretta :

    ```bash
    # Cela active l'activation automatique de 60 secondes au prochain démarrage
    purist-mode-auto-enable

    # Cela désactive l'activation automatique au prochain démarrage
    purist-mode-auto-disable
    ```

---

## 13. Annexe 4 : Interface Web optionnelle de contrôle du système

Cette annexe fournit des instructions pour installer une application web simple sur le Host Diretta. Cette application offre une interface facile à utiliser, accessible depuis un téléphone ou une tablette, pour gérer les fonctionnalités clés de votre système Diretta, notamment le Mode Puriste sur le Target et les paramètres d'intégration de la télécommande IR Roon sur le Host.

> **AVERTISSEMENT CRITIQUE : Effectuez ces étapes avec précaution.**
> Cette configuration implique la création d'un nouvel utilisateur et la modification de paramètres de sécurité. Suivez scrupuleusement les instructions pour garantir que le système reste sécurisé et fonctionnel.

La configuration est divisée en deux parties : d'abord, nous configurons le **Target Diretta** pour accepter les commandes de manière sécurisée, et ensuite, nous installons l'application web sur le **Host Diretta**. Cependant, soyez attentif car nous basculons fréquemment d'un hôte à l'autre.

---

### **Partie 1 : Configuration du Target Diretta**

Sur le **Target Diretta**, nous allons créer un nouvel utilisateur avec des privilèges très limités. Cet utilisateur sera uniquement autorisé à exécuter les commandes spécifiques requises pour gérer le Mode Puriste.

1.  **Connectez-vous en SSH au Target Diretta :**
    ```bash
    ssh diretta-target
    ```

2.  **Créer un nouvel utilisateur pour l'application :**
    Cette commande crée un nouvel utilisateur nommé `purist-app` et son répertoire personnel. Un shell valide est requis pour le fonctionnement des commandes SSH non interactives.
    ```bash
    sudo useradd --create-home --shell /bin/bash purist-app
    ```

3.  **Créer des scripts de commande sécurisés :**
    Nous allons créer quatre petits scripts dédiés qui constituent les *seules* actions que l'application web est autorisée à effectuer. Il s'agit d'une étape de sécurité critique.
    ```bash
    # Script pour obtenir le statut actuel, y compris l'état de la licence
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-status
    #!/bin/bash
    IS_ACTIVE="false"
    IS_AUTO_ENABLED="false"
    LICENSE_LIMITED="false"

    # Vérifier le Mode Puriste
    if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
      IS_ACTIVE="true"
    fi

    # Vérifier si le démarrage automatique est activé
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      IS_AUTO_ENABLED="true"
    fi

    # Vérifier le cache de démarrage validé pour un lien d'évaluation actif
    if [ ! -f /tmp/diretta_license_url.cache ] || grep -q "http" /tmp/diretta_license_url.cache; then
      LICENSE_LIMITED="true"
    fi

    # Renvoyer tous les indicateurs de statut sous forme d'un seul objet JSON
    echo "{\"purist_mode_active\": $IS_ACTIVE, \"auto_start_enabled\": $IS_AUTO_ENABLED, \"license_needs_activation\": $LICENSE_LIMITED}"
    EOT

    # Script pour basculer le Mode Puriste
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-mode
    #!/bin/bash
    if [[ "$1" == "--enforce" ]]; then
        # Application stricte : s'il est censé être actif, réexécuter
        # le script de base pour nettoyer toute route par défaut ressuscitée.
        if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
            /usr/local/bin/purist-mode
        fi
    elif [ -f "/etc/nsswitch.conf.purist-bak" ]; then
        /usr/local/bin/purist-mode --revert
    else
        /usr/local/bin/purist-mode
    fi
    EOT

    # Script pour basculer le service de démarrage automatique
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-auto
    #!/bin/bash
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      systemctl disable --now purist-mode-auto.service
    else
      systemctl enable purist-mode-auto.service
    fi
    EOT

    # Créer le script pour redémarrer le service Diretta
    cat <<'EOT' | sudo tee /usr/local/bin/pm-restart-target
    #!/bin/bash
    # Redémarre le service Diretta ALSA Target.
    # Ce script est destiné à être appelé via sudo par l'utilisateur purist-app.
    /usr/bin/systemctl restart diretta_alsa_target.service
    EOT

    # Créer le script pour récupérer l'URL de licence Diretta
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-license-url
    #!/bin/bash

    # La seule tâche de ce script est de lire le fichier cache créé au démarrage.
    readonly CACHE_FILE="/tmp/diretta_license_url.cache"

    if [ -s "$CACHE_FILE" ]; then
        # Si le cache existe et contient des données, les afficher.
        cat "$CACHE_FILE"
    else
        # Sinon, afficher une erreur utile sur stderr et quitter.
        echo "Erreur : Cache de licence introuvable ou vide." >&2
        exit 1
    fi
    EOT

    # Créer le script pour définir la vitesse de la liaison
    cat <<'EOT' | sudo tee /usr/local/bin/pm-set-link
    #!/bin/bash
    # Script de profil pour appliquer les limites physiques de la liaison du Target
    # Refactorisé en utilisant des masques d'annonce explicites pour éviter les blocages matériels

    SPEED="$1"

    if [ "$SPEED" = "10" ]; then
        echo "Planification du bridage à 10 Mbps (Super Purist)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x002" >/dev/null 2>&1 < /dev/null &
    elif [ "$SPEED" = "100" ]; then
        echo "Planification du bridage à 100 Mbps (Purist)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x008" >/dev/null 2>&1 < /dev/null &
    elif [ "$SPEED" = "1000" ]; then
        echo "Libération des bridages. Restauration de la gamme complète 10/100/1000 (Standard)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x03f" >/dev/null 2>&1 < /dev/null &
    else
        echo "Usage: $0 [10|100|1000]"
        exit 1
    fi
    EOT

    # Rendre les nouveaux scripts exécutables
    sudo chmod -v +x /usr/local/bin/pm-*
    ```

4.  **Accorder des permissions sudo :**
    Cette étape permet à l'utilisateur `purist-app` d'exécuter nos quatre nouveaux scripts avec des privilèges root et sans avoir besoin d'un terminal interactif.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/purist-app
    # Indiquer à sudo de ne pas requérir de TTY pour l'utilisateur purist-app
    Defaults:purist-app !requiretty

    # Autoriser l'utilisateur purist-app à exécuter les scripts de contrôle spécifiques sans mot de passe
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-status
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-mode
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-toggle-auto
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-restart-target
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-get-license-url
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-set-link
    EOT
    ```

5.  **Remplir le fichier de cache de licence Diretta au démarrage**
    La récupération de l'URL de licence Diretta nécessite une connexion Internet. Si le Mode Puriste est activé par défaut, le Target ne pourra jamais récupérer l'URL. Cependant, au démarrage, le Mode Puriste est désactivé pendant 60 secondes afin de régler l'horloge et de vérifier l'activation de la licence Diretta. Nous pouvons également profiter de ce créneau pour récupérer l'URL.
    ```bash
    # Télécharger le script, définir les permissions correctes et le placer dans le chemin système
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh
    sudo install -m 0755 create-diretta-cache.sh /usr/local/bin/
    rm create-diretta-cache.sh

    # Créer un service pour remplir le cache d'état de la licence
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta-cache.service
    [Unit]
    Description=Asynchronous Diretta License Cache Collector
    After=network.target purist-mode-revert-on-boot.service
    Before=purist-mode-auto.service

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    # Bloquer proprement l'exécution ici jusqu'à ce que le Host réponde à un ping
    TimeoutStartSec=infinity
    ExecStartPre=/bin/bash -c "until ping -c 1 -q 172.20.0.1 &>/dev/null; do sleep 2; done"
    ExecStart=/usr/local/bin/create-diretta-cache.sh
    Restart=no

    [Install]
    WantedBy=multi-user.target
    EOT

    # Recharger systemd pour prendre en compte la configuration personnalisée mise à jour
    sudo rm -rf /etc/systemd/system/purist-mode-revert-on-boot.service.d
    sudo systemctl daemon-reload
    sudo systemctl enable diretta-cache.service

    # Exécuter manuellement le script une fois
    sudo /usr/local/bin/create-diretta-cache.sh
    ls -l /tmp/diretta_license_url.cache
    ```

---

### **Partie 2 : Configuration du Host Diretta**

Maintenant, sur le **Host Diretta**, nous allons effectuer toutes les étapes pour installer et configurer l'application web. Vous devez être connecté en tant qu'utilisateur `audiolinux` pour l'ensemble de cette section.

1.  **Connectez-vous en SSH au Host Diretta :**
    ```bash
    ssh diretta-host
    ```

2.  **Générer une clé SSH dédiée :**
    Cela crée une nouvelle paire de clés SSH spécifiquement pour l'application web. Elle n'aura pas de phrase de passe.
    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/purist_app_key -N "" -C "purist-app-key"
    ```

3.  **Configurer SSH et copier la clé sur le Target :**
    Cette étape va créer une configuration SSH et copier la clé publique sur le Target de manière sécurisée.
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

    # Copier la clé publique dans le répertoire personnel du Target
    echo "--> Copie de la clé publique vers la Target..."
    scp -o StrictHostKeyChecking=accept-new ~/.ssh/purist_app_key.pub diretta-target:
    ```

4.  **Autoriser la clé sur le Target :**
    ```bash
    ssh diretta-target

    ```

    Une fois connecté au Target, exécutez ce script pour configurer la clé pour l'utilisateur 'purist-app'
    ```bash
    echo "--> Exécution du script de configuration sur la Target..."
    set -e
    # Lire la clé publique depuis le fichier que nous venons de copier
    PUB_KEY=$(cat purist_app_key.pub)

    # S'assurer que le répertoire .ssh existe et a les permissions correctes
    sudo mkdir -p /home/purist-app/.ssh
    sudo chmod 0700 /home/purist-app/.ssh

    # Créer le fichier authorized_keys avec les restrictions de sécurité requises
    echo "command=\"sudo \$SSH_ORIGINAL_COMMAND\",from=\"172.20.0.1\",no-port-forwarding,no-x11-forwarding,no-agent-forwarding,no-pty ${PUB_KEY}" | sudo tee /home/purist-app/.ssh/authorized_keys > /dev/null

    # Définir les propriétaires et permissions finaux
    sudo chown -R purist-app:purist-app /home/purist-app/.ssh
    sudo chmod 0600 /home/purist-app/.ssh/authorized_keys

    # Nettoyer le fichier de clé publique copié
    rm purist_app_key.pub

    echo "✅ La clé SSH a été autorisée avec succès sur la Target."
    ```

5.  **Tester manuellement les commandes à distance (recommandé) :**
    Avant de démarrer l'application web, testez les commandes distantes en lecture seule à partir du terminal du **Host Diretta** pour confirmer que le backend fonctionne.
    ```bash
    # Tester la commande de statut (devrait renvoyer une chaîne JSON)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-status'

    # Tester la commande pour récupérer l'état de la licence.
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-license-url'
    ```

6.  **Installer Python via pyenv** sur le **Host Diretta** (n'hésitez pas à ignorer cette étape si vous l'avez déjà fait pour faire fonctionner la télécommande IR)
    Installez `pyenv` et la dernière version stable de Python.
    ```bash
    # Installer les dépendances de compilation
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

    # Installer pyenv uniquement s'il n'est pas déjà installé
    if [ ! -d "$HOME/.pyenv" ]; then
      echo "--- Installation de pyenv ---"
      curl -fsSL https://pyenv.run | bash
    else
      echo "--- pyenv is already installed. Installation ignorée. ---"
    fi

    # Configurer le shell pour pyenv
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

    # Charger le fichier pour rendre pyenv disponible dans le shell actuel
    . ~/.bashrc

    # Installer et définir la dernière version de Python uniquement si elle n'est pas déjà installée
    PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
    if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
      # Obtenir la mémoire totale en Mo
      TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

      if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- La RAM physique est de ${TOTAL_MEM}Mo. Limitation à 1 cœur pour éviter tout blocage. ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
      else
        echo "--- La RAM physique est de ${TOTAL_MEM}Mo. Poursuite de la compilation en parallèle. ---"
      fi

      echo "--- Installation de Python ${PYVER}. Cela va prendre plusieurs minutes... ---"
      pyenv install $PYVER
      [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
    else
      echo "--- Python ${PYVER} est déjà installé. ---"
    fi

    pyenv global $PYVER
    ```

    **Note :** Il est normal que l'étape `Installing Python-3.14.5...` prenne environ 10 minutes car elle compile Python à partir des sources. N'abandonnez pas ! N'hésitez pas à vous détendre en écoutant de la belle musique sur votre nouvelle zone Diretta dans Roon pendant que vous attendez. Elle devrait être disponible pendant l'installation de Python sur le Host.

7.  **Installer Avahi et les dépendances Python sur le Host Diretta :**

    **Note :** OPTIONNEL - Si vous avez plus d'un Host Diretta sur votre réseau, veuillez vous assurer qu'ils ont des noms uniques. Vous pouvez utiliser une commande comme la suivante pour renommer celui-ci avant de continuer :

    ```bash
    # Renommer éventuellement le Host Diretta s'il s'agit de votre deuxième configuration sur le même réseau
    sudo hostnamectl set-hostname diretta-host2
    ```

    Cette étape s'exécute sur le **Host Diretta**. Elle installe le démon Avahi et utilise un fichier `requirements.txt` pour installer Flask dans un environnement virtuel dédié.
    ```bash
    # Installer Avahi pour la résolution de noms en .local
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm avahi

    # Trouver dynamiquement le nom de l'interface Ethernet USB (par ex., enp... ou enu1...)
    USB_INTERFACE=$(ip -o link show | awk -F': ' '/en[pu]/{print $2}')

    # Créer une surcharge de configuration pour Avahi afin de l'isoler sur l'interface USB
    echo "--- Configuration d'Avahi pour utiliser l'interface : $USB_INTERFACE ---"
    sudo mkdir -p /etc/avahi/avahi-daemon.conf.d
    cat <<EOT | sudo tee /etc/avahi/avahi-daemon.conf.d/interface-scoping.conf
    [server]
    allow-interfaces=$USB_INTERFACE
    deny-interfaces=end0
    EOT

    # Activer et démarrer le démon Avahi
    sudo systemctl enable --now avahi-daemon.service

    # Créer le répertoire de l'application et le fichier des exigences (requirements)
    mkdir -p ~/purist-mode-webui
    echo "Flask" > ~/purist-mode-webui/requirements.txt

    # Créer un environnement virtuel et installer les dépendances
    echo "--- Configuration de l'environnement Python pour l'interface Web ---"
    # Créer l'environnement virtuel uniquement s'il n'existe pas déjà
    if ! pyenv versions --bare | grep -q "^purist-webui$"; then
      echo "--- Création de l'environnement virtuel 'purist-webui' ---"
      pyenv virtualenv purist-webui
    else
      echo "--- L'environnement virtuel 'purist-webui' existe déjà ---"
    fi
    pyenv activate purist-webui
    pip install -r ~/purist-mode-webui/requirements.txt
    pyenv deactivate
    ```

8.  **Installer l'application Flask :**
    Téléchargez le script Python directement depuis GitHub dans le répertoire de l'application sur le **Host Diretta**.
    ```bash
    curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py -o ~/purist-mode-webui/app.py
    ```

9. **Accorder la capacité de liaison aux ports (Port-Binding)**
    Nous devons accorder à l'exécutable Python la permission de se lier au port 80 sur le Host Diretta pour que notre application web démarre.
    ```bash
    # Installer le paquet qui fournit la commande 'setcap'
    sudo pacman -S --noconfirm --needed libcap

    # Trouver le chemin réel vers l'exécutable Python, en résolvant tous les liens symboliques
    PYTHON_EXEC=$(readlink -f /home/audiolinux/.pyenv/versions/purist-webui/bin/python)

    # Accorder la capacité de liaison aux ports directement à l'exécutable Python final
    echo "Application de la capability au fichier réel : ${PYTHON_EXEC}"
    sudo setcap 'cap_net_bind_service=+ep' "$PYTHON_EXEC"
    ```

10. **Accorder des privilèges sudo sur le Host :**
    Cette étape est essentielle pour permettre à l'application web de redémarrer les services liés à Roon requis sans mot de passe.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/webui-restarts
    # Autoriser l'interface web (s'exécutant en tant qu'audiolinux) à appliquer les profils d'hôte et à redémarrer les services
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl daemon-reload
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roon-ir-remote.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roonbridge.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart diretta_alsa.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/ethtool -s end0 *
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/mv /tmp/setting.inf.tmp /opt/diretta-alsa/setting.inf
    EOT
    sudo chmod 0440 /etc/sudoers.d/webui-restarts
    ```

11. **Tester l'application Flask de manière interactive :**
    À présent, lancez l'application depuis la ligne de commande sur le **Host Diretta** pour vous assurer qu'elle démarre correctement.
    ```bash
    cd ~/purist-mode-webui
    pyenv activate purist-webui
    python app.py
    ```
    Vous devriez voir un message indiquant que le serveur Flask a démarré sur le port **8080**. Depuis un autre appareil, accédez à [http://diretta-host.local:8080](http://diretta-host.local:8080). Si cela fonctionne, revenez au terminal SSH et appuyez sur `Ctrl+C` pour arrêter le serveur.

12. **Créer le service `systemd` :**
    Ce service exécutera automatiquement l'application web sur le **Host Diretta**, en utilisant l'exécutable Python approprié de notre environnement virtuel `pyenv`.
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

13. **Activer et démarrer l'application web :**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl stop purist-webui.service
    sudo systemctl enable --now purist-webui.service
    ```

14. **Surveiller les journaux pendant un moment :**
    ```bash
    journalctl -b -u purist-webui.service -f
    ```

15. **Tester l'interface web avec l'URL finale :**
    Ouvrez un navigateur sur [http://diretta-host.local](http://diretta-host.local) et surveillez les journaux pour détecter d'éventuelles erreurs.

Tapez `CTRL-C` une fois que vous êtes convaincu que tout fonctionne comme prévu.

---

### **Accéder à l'interface Web**

Vous y êtes presque ! Ouvrez un navigateur web sur votre téléphone, votre tablette ou votre ordinateur connecté au même réseau que le Host Diretta. Accédez à la page d'accueil principale :

[http://diretta-host.local](http://diretta-host.local)

---
> **Note sur les avertissements de sécurité des navigateurs**
> Lorsque vous visitez http://diretta-host.local pour la première fois, votre navigateur affichera probablement un avertissement de sécurité indiquant que la connexion n'est pas sécurisée. C'est tout à fait normal et vous pouvez l'ignorer en toute sécurité. L'avertissement apparaît parce que la connexion utilise le protocole `HTTP` standard au lieu du `HTTPS` chiffré, un choix intentionnel pour minimiser la charge de traitement sur l'appareil audio. Comme l'application s'exécute uniquement sur votre réseau domestique privé et ne gère aucune donnée sensible, vous pouvez cliquer en toute confiance sur « Continuer vers le site ».
---

Depuis la page d'accueil, une barre de navigation en haut vous guidera vers les différents panneaux de contrôle :

* **Home (Accueil) :** La page d'accueil principale avec des liens vers les différentes applications.

* **Purist Mode App :** Cette page contient les commandes pour basculer le Mode Puriste et son comportement de démarrage automatique sur le Target Diretta. Elle se rafraîchit automatiquement toutes les 30 secondes pour afficher l'état actuel. Elle contient également le bouton « Restart Services » (Redémarrer les services) à utiliser après l'activation d'une licence Diretta.

* **IR Remote App :** Si vous avez terminé la configuration de la télécommande IR (Annexe 2), ce lien apparaîtra. Cette page fournit un formulaire simple pour afficher et mettre à jour le nom de la zone Roon que votre télécommande contrôlera. Cette page ne se rafraîchit pas automatiquement, vous pouvez donc prendre tout le temps nécessaire pour effectuer vos modifications.

### 🔗 Note sur la fonctionnalité complète de l'interface Web

Pour déverrouiller toutes les capacités de l'interface web de contrôle du système — en particulier les ajustements de la vitesse de liaison réseau (**Link Speed**) et le basculement vers **Super Purist** —, vous devez également effectuer les configurations matérielles et de services détaillées dans l'[**Annexe 8 : Vitesses réseau puristes optionnelles**](#17-annexe-8--vitesses-réseau-puristes-optionnelles)[cite: 1]. L'interface web s'appuie directement sur les scripts, indicateurs et services sous-jacents établis dans cette section pour modifier et appliquer avec succès les limites de vitesse de liaison physique sur votre connexion point à point[cite: 1].

> ---
> ### ✅ Checkpoint : Vérifiez la configuration de votre interface Web
>
> L'interface web du Mode Puriste devrait maintenant être opérationnelle. Pour vérifier tous les composants de cette fonctionnalité complexe, rendez-vous à l'[**Annexe 5**](#14-annexe-5--system-health-checks-vérifications-de-létat-du-système) et exécutez la commande universelle **System Health Check** sur le Host et le Target.
>
> ---

## 14. Annexe 5 : System Health Checks (Vérifications de l'état du système)

Après avoir terminé les sections majeures de ce guide, il est conseillé de lancer un test rapide d'assurance qualité (QA) pour vérifier que tout est configuré correctement.

Nous avons créé un script intelligent qui détecte automatiquement si vous l'exécutez sur le **Host Diretta** ou le **Target Diretta** et effectue la série de vérifications appropriée.

### **Comment exécuter la vérification**

Sur le Host ou le Target, exécutez la commande unique suivante. Elle téléchargera et exécutera le script de QA, fournissant un rapport détaillé de l'état de votre système.

```bash
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh | sudo bash
```

---

## 15. Annexe 6 : Optimisation optionnelle des performances en temps réel

Les étapes suivantes sont facultatives mais recommandées pour les utilisateurs cherchant à extraire les performances maximales absolues de leur configuration Diretta. La stratégie, basée sur les conseils de l'auteur d'AudioLinux Piero, consiste à créer l'environnement le plus stable et le plus silencieux possible sur le plan électrique sur le Host et le Target.

Ceci est réalisé en utilisant l'**isolation des processeurs (CPU isolation)** pour dédier des cœurs de processeur spécifiques aux tâches audio, les protégeant du système d'exploitation, et en ajustant soigneusement les **priorités temps réel (realtime priorities)** pour garantir que le chemin des données audio n'est jamais interrompu.

> **Note :** Il s'agit d'un processus d'optimisation avancé. Veuillez vous assurer que votre système Diretta de base est pleinement fonctionnel en complétant les sections 1 à 9 du guide principal avant de continuer. Un refroidissement adéquat pour les deux Raspberry Pi est essentiel.

---

### **Partie 1 : Optimisation du Target Diretta**

L'objectif pour le Target est d'en faire un point de terminaison audio pur à faible latence. Nous allons isoler l'application Diretta sur un seul cœur de processeur dédié et lui attribuer une priorité temps réel élevée, mais non excessive.

#### **Étape 6.1 : Isoler un cœur de processeur pour l'application audio**

Cette étape dédie un cœur de processeur exclusivement à l'application Target Diretta.

1.  Connectez-vous en SSH au Target Diretta :
    ```bash
    ssh diretta-target
    ```
2.  Entrez dans le système de menu d'AudioLinux :
    ```bash
    menu
    ```
3.  Naviguez vers le menu **ISOLATED CPU CORES configuration** (sous **SYSTEM menu**).

4.  Confirmez que l'isolation des cœurs est désactivée. Si ce n'est pas le cas, utilisez l'option 3 pour la désactiver :
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

5.  Revenez au menu **ISOLATED CPU CORES configuration** (sous **SYSTEM menu**). Suivez les invites exactement comme indiqué ci-dessous pour isoler les **cœurs 2 et 3** et y affecter l'application Diretta.
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

6.  Une fois le processus terminé, revenez au terminal.

> **Note sur l'affinité automatique des interruptions (IRQ) :** Vous remarquerez peut-être que le script indique qu'il a également isolé les requêtes d'interruption (IRQ) réseau de `end0` sur le même cœur. Il ne s'agit pas d'un bug, mais d'une optimisation intelligente. Le script associe automatiquement les interruptions réseau au même cœur que l'application utilisant le réseau, créant ainsi le chemin de données le plus efficace possible.

#### **Étape 6.2 : Désactiver l'ancien minuteur `rtapp`**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **Étape 6.3 : Redémarrer pour appliquer les modifications.**
```bash
sudo sync && sudo reboot
```

---

### **Partie 2 : Optimisation du Host Diretta**

L'objectif pour le Host est de donner aux threads du service Diretta des ressources de traitement dédiées, mais sans utiliser de priorités temps réel élevées. L'isolation des processeurs est un outil plus puissant ici, car elle empêche tout d'abord les processus d'être interrompus.

#### **Étape 6.4 : Isoler des cœurs de processeur pour les applications audio**

Cette étape dédie deux cœurs de processeur à la gestion des threads du service Host Diretta.

1.  Connectez-vous en SSH au Host Diretta :
    ```bash
    ssh diretta-host
    ```
2.  Entrez dans le système de menu d'AudioLinux :
    ```bash
    menu
    ```
3.  Naviguez vers le menu **ISOLATED CPU CORES configuration** (sous **SYSTEM menu**).

4.  Confirmez que l'isolation des cœurs est désactivée. Si ce n'est pas le cas, utilisez l'option 3 pour la désactiver :
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

5.  Revenez au menu **ISOLATED CPU CORES configuration** (sous **SYSTEM menu**). Suivez les invites pour isoler les **cœurs 2 et 3** et les allouer à Diretta ALSA.
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

6.  Une fois le processus terminé, revenez au terminal.

---

#### **Étape 6.5 : Désactiver l'ancien minuteur `rtapp`**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **Étape 6.6 : Redémarrer pour appliquer les modifications.**
```bash
sudo sync && sudo reboot
```

## 16. Annexe 7 : Optimisations optionnelles des IRQ et des threads

### Partie 1 : Isolation du chemin USB du Target Diretta
Par défaut, même lorsque des cœurs de processeur sont isolés, les interruptions USB peuvent toujours entrer en concurrence pour les ressources sur les cœurs système « bruyants » (0 et 1). Ce script identifie de manière dynamique le contrôleur USB spécifique auquel votre DAC est connecté et attribue ses interruptions matérielles à vos cœurs audio isolés (2 et 3). Sur le Raspberry Pi 5, les contrôleurs USB sont gérés par la puce RP1, ce qui nous permet d'orienter les interruptions matérielles vers des cœurs spécifiques.

**Note :** Cette optimisation n'est pas applicable au Raspberry Pi 4 en raison d'interruptions verrouillées au niveau matériel.

1.  Assurez-vous que votre DAC est sous tension et connecté au Target.
2.  Démarrez la lecture de musique vers le Target Diretta. Cela permet au script de détecter le trafic d'interruption actif.
3.  Exécutez la commande suivante sur le Target Diretta :
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/usb-isolation.sh | sudo bash
    ```
4.  Redémarrerez pour appliquer les modifications :
    ```bash
    sudo sync && sudo reboot
    ```

**Ce que cela fait :** Le script localise le chemin actif du DAC (par ex., xhci-hcd:usb1 ou xhci-hcd:usb3). Il ajoute ensuite l'identifiant spécifique à votre groupe d'isolation AudioLinux pour créer un chemin de données isolé à 100 %, de l'entrée réseau à la sortie USB.

---

### Partie 2 : Optimisation des threads du Host Diretta

Grâce aux optimisations du noyau en temps réel, le Host Diretta peut désormais gérer un intervalle de paquets plus agressif, ce qui peut améliorer la qualité sonore. Cette dernière étape réduit le paramètre `CycleTime` de 800 à 514 microsecondes. Cet écart de temps plus court entre les paquets garantit que tous les contenus jusqu'au DSD256 et au DXD (32 bits, 352.8 kHz) ne nécessiteront qu'un seul paquet par cycle. Nous pouvons également planifier les threads Diretta sur des cœurs spécifiques.

1.  Connectez-vous en SSH au **Host Diretta** si ce n'est pas déjà fait.
2.  Exécutez la commande suivante pour appliquer le paramètre optimisé :
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
3.  Redémarrez le service Diretta pour que la modification prenne effet :
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart diretta_alsa.service
    ```

> ---
> ### ✅ Checkpoint : Vérifiez votre optimisation en temps réel
>
> Votre optimisation avancée en temps réel devrait maintenant être terminée. Pour vérifier tous les composants de cette nouvelle configuration, veuillez retourner à l'[**Annexe 5**](#14-annexe-5--system-health-checks-vérifications-de-létat-du-système) et exécuter la commande universelle **System Health Check** sur le Host et le Target.
>
> ---

## 17. Annexe 8 : Vitesses réseau puristes optionnelles

**Objectif :** Réduire le bruit électrique et améliorer la précision de l'ordonnanceur de l'OS en limitant la vitesse de liaison du réseau dédié et en désactivant explicitement l'Energy Efficient Ethernet (EEE).

Bien que cela soit contre-intuitif, réduire la vitesse de la liaison de 1 Gbps à 100 Mbps (ou même 10 Mbps) sur la liaison dédiée (`end0`) peut améliorer la qualité sonore. La fréquence de fonctionnement inférieure de 100BASE-TX (31,25 MHz contre 62,5 MHz) génère moins de perturbations radioélectriques (RFI). À l'extrême, abaisser la vitesse à 10 Mbps réduit la fréquence porteuse à seulement 10 MHz. De plus, s'assurer que l'EEE est désactivé empêche la liaison d'entrer en état de veille, éliminant ainsi les pics de latence potentiels (flapping) et garantissant une stabilité absolue sur le matériel Raspberry Pi 5.

> ---
> ### 🎧 Deep Dive : Pourquoi une limite à 10 Mbps restaure le « calme » sonore
>
> Restreindre votre liaison audio dédiée à 10 Mbps introduit des limitations de format — limitant votre lecture au **DSD64 natif** et au **PCM 32 bits/96 kHz**. Cependant, pour les audiophiles qui privilégient la qualité CD standard (Red Book) ou les fichiers haute résolution classiques, ce compromis apporte des avantages sonores profonds en s'attaquant aux causes profondes de la dureté numérique.
>
> * **Fréquences porteuses considérablement réduites :** L'Ethernet Gigabit standard fonctionne avec un signal porteur haute fréquence de 62,5 MHz (utilisant un encodage multi-niveaux complexe). Passer à 100 Mbps abaisse cette valeur à 31,25 MHz. Descendre jusqu'à une liaison de 10 Mbps (10BASE-T) utilise un schéma d'encodage de Manchester très simple fonctionnant à une fréquence porteuse native de seulement **10 MHz**. Cette réduction massive de la fréquence de fonctionnement diminue de manière significative les émissions radioélectriques (RFI) générées à l'intérieur du boîtier et le long du câble.
> * **Charge de traitement réduite sur le Target :** Les réseaux à large bande passante forcent la carte d'interface réseau (NIC) et le processeur à traiter les paquets de données à une cadence rapide et agressive. En limitant la vitesse de liaison pour correspondre aux besoins réels des données audio standard, vous réduisez considérablement le volume d'interruptions réseau que le système d'exploitation du Target doit traiter.
> * **Synergie avec la philosophie fondamentale de Diretta :** Tout l'objectif du protocole Diretta est d'éliminer le traitement par rafales et de stabiliser la consommation de courant. Une liaison à 10 Mbps agit comme un égaliseur physique pour le flux de données, évitant les pics de données à haute vitesse qui provoquent des fluctuations d'alimentation électrique.
>
> Le résultat de cette restriction « Super Puriste » est une baisse instantanément perceptible du bruit de fond numérique. Les auditeurs signalent fréquemment une scène sonore plus large et plus détendue, un suivi plus propre des transitoires haute fréquence, et un sentiment général de douceur et de sérénité analogique qui complète parfaitement les objectifs d'AudioLinux et de Diretta.
> ---

> **Note :** Vous pourriez voir des avertissements de mémoire tampon basse (« buffer low ») dans les journaux du Target (le `LatencyBuffer` tombant à 1). Il s'agit d'un comportement normal dû à l'augmentation de la latence de sérialisation de la liaison plus lente, et cela ne provoque pas de coupures audio perceptibles.

### Étape 1 : Configurer le Host et le Target (désactiver l'EEE)

L'Energy Efficient Ethernet (EEE) peut provoquer une instabilité de la liaison sur certaines combinaisons matérielles. Nous allons créer un service pour le désactiver explicitement sur le Host **et** le Target afin de garantir un comportement cohérent.

**Créer le service de désactivation :** *(À effectuer sur le Host ET le Target)*

```bash
cat <<'EOT' | sudo tee /etc/systemd/system/disable-eee.service
[Unit]
Description=Disable EEE on end0 for Link Stability
After=network.target
BindsTo=sys-subsystem-net-devices-end0.device
After=sys-subsystem-net-devices-end0.device

[Service]
Type=oneshot
# Attendre jusqu'à 5 secondes pour que l'interface apparaisse comme active (UP)
ExecStartPre=/usr/bin/bash -c 'for i in {1..5}; do if ip link show end0 | grep -q "UP"; then exit 0; fi; sleep 1; done; exit 1'
# Configurer maintenant l'optimisation matérielle
ExecStart=-/usr/bin/ethtool -s end0 advertise 0x03f
ExecStart=-/usr/bin/ethtool --set-eee end0 eee off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

sudo systemctl daemon-reload
sudo systemctl enable --now disable-eee.service
```

### Étape 2 : Marquer le Target (pour la QA)

Pour s'assurer que le **script de QA du Target** sache valider cette configuration spécifique, créez un fichier marqueur sur le Target :

```bash
sudo touch /etc/diretta-100m
```

### Étape 3 : Configurer le Host (Limite de vitesse)
Nous allons créer un service sur le **Host** qui le force à négocier *soit* 10 Mbps, soit 100 Mbps en Full Duplex, selon que le mode « Super Puriste » est activé ou non. Le Target détectera automatiquement le changement de vitesse et s'y adaptera.

**Créer le script et le service de restriction :** *(À effectuer sur le Host uniquement)*
```bash
cat <<'EOT' | sudo tee /usr/local/bin/set-link-speed.sh
#!/bin/bash
# Définir la vitesse de la liaison en fonction de l'indicateur Super Purist de l'interface web à l'aide de masques de négociation sécurisés
FLAG_FILE="/home/audiolinux/purist-mode-webui/super_purist.flag"
INTERFACE="end0"

# CRITICAL: Attendre jusqu'à 60 secondes pour que l'interface physique initialise la couche de liaison porteuse
echo "Synchronisation avec la couche de liaison physique..."
for i in {1..60}; do
    if [ -f /sys/class/net/$INTERFACE/carrier ] && [ "$(cat /sys/class/net/$INTERFACE/carrier 2>/dev/null)" "==" "1" ]; then
        echo "Couche de liaison physique détectée après $i secondes."
        break
    fi
    sleep 1
done

# Appliquer le masque de négociation en fonction de l'état de l'indicateur
if [ -f "$FLAG_FILE" ]; then
    echo "Indicateur Super Purist détecté. Annonce de 10 Mbps Full Duplex..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x002
else
    echo "Mode Standard/Purist. Annonce jusqu'à 100 Mbps Full Duplex..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x00a
fi

# Gestion de la négociation spécifique à la plateforme
if grep -q "Raspberry Pi 4" /proc/device-tree/model 2>/dev/null; then
    echo "Raspberry Pi 4 détecté. Déclenchement de l'impulsion de renégociation matérielle obligatoire..."
    /usr/bin/ethtool -r $INTERFACE
elif grep -q "Raspberry Pi 5" /proc/device-tree/model 2>/dev/null; then
    echo "Raspberry Pi 5 détecté. Impulsion automatique phylib interne utilisée ; réinitialisation manuelle ignorée."
else
    /usr/bin/ethtool -r $INTERFACE || true
fi

echo "Politique de vitesse de liaison finalisée avec succès."
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

echo "Activer et démarrer le service :"
sudo systemctl daemon-reload
sudo systemctl enable --now limit-speed-100m.service
```

***
> **Note sur la latence de lecture :**
> Vous remarquerez peut-être une légère augmentation du délai entre le moment où vous appuyez sur « Play » et celui où vous entendez la musique (jusqu'à environ 1 seconde). C'est un comportement attendu. En restreignant la liaison à 10 ou 100 Mbps, nous limitons intentionnellement le flux de données initial pour garantir que la connexion fonctionne à une fréquence plus basse et plus silencieuse. Le système troque des temps de démarrage instantanés contre un état stable plus régulier et moins bruyant pendant la lecture.
***

>
>
> ---
>
> ### ✅ Checkpoint : Vérifiez la configuration réseau
>
> Votre liaison réseau dédiée est maintenant configurée pour un fonctionnement « Puriste » à 100 Mbps. Pour vérifier que le service du Host est actif et que le Target a correctement négocié la vitesse (détectée via le fichier marqueur), veuillez retourner à l'[**Annexe 5**](#14-annexe-5--system-health-checks-vérifications-de-létat-du-système) et exécuter la commande universelle **System Health Check** sur le Host et le Target.
>
> ---

## 18. Annexe 9 : Optimisation optionnelle des Jumbo Frames
Cette section optimise le transport pour une efficacité maximale de la bande passante.

#### **Étape 1 :** Préparer les interfaces

Nous devons forcer temporairement les interfaces réseau à un MTU de 9000 pour vérifier la prise en charge par le noyau et préparer le test de liaison.

**Exécutez ceci sur le Target en premier, puis sur le Host :**

```bash
sudo sh -c 'ip link set end0 down; sleep 2; ip link set end0 mtu 9000; ip link set end0 up'
end0_mtu=$(ip link show dev end0 | awk '/mtu/ {print $5}')
if [[ "9000" == "$end0_mtu" ]]; then
  echo "SUCCÈS : Le noyau prend en charge les trames Jumbo. Passez à l'étape 2."
else
  echo "STOP : Votre noyau ne semble pas prendre en charge les trames Jumbo."
fi
```

*Si vous voyez « STOP » sur le Host **ou** le Target, ne continuez pas. Votre noyau ne dispose pas du patch requis.*

---

#### **Étape 2 :** Configuration automatisée du Target

Connectez-vous en SSH au Target (`diretta-target`) et collez le bloc suivant.

```bash
# 1. Détecter la limite de la liaison (Full vs Baby)
echo "Test de la capacité de la liaison..."
if ping -c 1 -w 1 -M "do" -s 8972 host &>/dev/null; then
  NEW_MTU=9000
  echo "SUCCÈS : Trames Jumbo complètes (MTU 9000) prises en charge."
elif ping -c 1 -w 1 -M "do" -s 2004 host &>/dev/null; then
  NEW_MTU=2032
  echo "SUCCÈS : Trames Baby Jumbo (MTU 2032) prises en charge."
else
  echo "ÉCHEC : La liaison ne peut pas prendre en charge les trames Jumbo. Retour aux valeurs par défaut sécurisées."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Appliquer la configuration réseau du système
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

  # 3. Appliquer la configuration de Diretta
  echo "Configuration de Diretta Target..."
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
  echo "TERMINÉ : Optimisation de la Target terminée."
}

```

---

#### **Étape 3 :** Configuration automatisée du Host

Connectez-vous en SSH au Host (`diretta-host`) et collez le bloc suivant. Il testera la liaison, configurera les paramètres réseau permanents et mettra à jour Diretta.

```bash
# 1. Détecter la limite de la liaison (Full vs Baby)
echo "Test de la capacité de la liaison..."
# Laisser le temps à la liaison de se stabiliser après le changement manuel de MTU
sleep 2

if ping -c 1 -w 1 -M "do" -s 8972 target &>/dev/null; then
  NEW_MTU=9000
  echo "SUCCÈS : Trames Jumbo complètes (MTU 9000) prises en charge."
elif ping -c 1 -w 1 -M "do" -s 2004 target &>/dev/null; then
  NEW_MTU=2032
  echo "SUCCÈS : Trames Baby Jumbo (MTU 2032) prises en charge."
else
  echo "ÉCHEC : La liaison ne peut pas prendre en charge les trames Jumbo. Retour aux valeurs par défaut sécurisées."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Appliquer la configuration réseau du système
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

  # 3. Appliquer la configuration de Diretta
  echo "Configuration de Diretta Host..."

  # Toujours activer FlexCycle pour les Jumbo Frames afin de garantir la stabilité
  sudo sed -i 's/^FlexCycle=.*/FlexCycle=enable/' /opt/diretta-alsa/setting.inf

  # Optimisation conditionnelle du CycleTime et de l'InfoCycle
  if [ "$NEW_MTU" -eq 9000 ]; then
    echo "Optimisation : Trames Jumbo complètes détectées. Assouplissement du CycleTime à 1000us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=1000/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=100000/' /opt/diretta-alsa/setting.inf
  else
    echo "Optimisation : Trames Baby Jumbo détectées. Configuration du CycleTime sur 700us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=700/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=70000/' /opt/diretta-alsa/setting.inf
  fi

  sudo systemctl restart diretta_alsa
  echo "TERMINÉ : Optimisation du Host terminée."
}
```

#### **Étape 4 :** Redémarrer pour appliquer les modifications de MTU
Redémarrez le Target en premier, puis le Host :
```bash
sudo sync && sudo reboot
```

>
>
> ---
>
> ### ✅ Checkpoint : Vérifiez la configuration réseau
>
> Si vous avez pu activer la prise en charge des Jumbo Frames pour votre configuration, c'est le bon moment pour retourner à l'[**Annexe 5**](#14-annexe-5--system-health-checks-vérifications-de-létat-du-système) et exécuter la commande universelle **System Health Check** sur le Host et le Target.
>
> ---

## 19. Annexe 10 : Facultatif : Mises à jour du système
Cette section fournit des conseils sur l'application des mises à jour au matériel Raspberry Pi, au système d'exploitation AudioLinux et à la pile logicielle Diretta.

#### **Partie 1 :** Mettre à jour le chargeur de démarrage (bootloader) du Raspberry Pi (facultatif)

La mise à jour du chargeur de démarrage (bootloader / EEPROM) du Raspberry Pi n'est pas requise et comporte des risques inhérents. Cependant, maintenir le micrologiciel (firmware) à jour peut offrir des avantages tels que des températures de fonctionnement plus basses et des séquences de démarrage plus propres grâce aux corrections de bugs continues fournies par la Fondation Raspberry Pi.

*Avertissement : Assurez-vous de n'appliquer que l'image de micrologiciel correcte correspondant à la carte concernée. Flasher un Raspberry Pi 4 avec un chargeur de démarrage de Raspberry Pi 5 (ou vice-versa) peut avoir de graves conséquences négatives, pouvant aller jusqu'à rendre la carte définitivement inutilisable (bricked).*

**Vérifier la version actuelle du chargeur de démarrage**
Avant de commencer, connectez-vous en SSH au Host et au Target, puis exécutez la commande suivante pour vérifier la date de publication de votre chargeur de démarrage actuel. Notez ces dates afin de pouvoir vérifier la réussite de la mise à jour plus tard.

```bash
vcgencmd bootloader_version
```

*(Recherchez la date sur la première ligne de la sortie).*

**Préparer le support de mise à jour**
Vous aurez besoin d'une carte microSD vierge, d'un lecteur de carte SD et du logiciel officiel Raspberry Pi Imager installé sur votre station de travail.

1. Ouvrez Raspberry Pi Imager. Cliquez sur **CHOOSE DEVICE** (Choisir l'appareil) et sélectionnez la carte Raspberry Pi spécifique que vous allez mettre à jour.

   ![Sélectionner l'appareil Raspberry Pi 5](images/01-rpi-dev.png)

2. Cliquez sur **CHOOSE OS** (Choisir l'OS), faites défiler la liste et sélectionnez **Misc utility images** (Images utilitaires diverses).

   ![Sélectionner les images utilitaires diverses](images/02-rpi-misc.png)

3. Sélectionnez **Bootloader** (Chargeur de démarrage). *(Note : Le menu affichera la famille Pi que vous avez sélectionnée à l'étape 1).*

   ![Sélectionner le chargeur de démarrage pour la famille Pi 5](images/03-rpi-bl.png)

4. Sélectionnez **SD Card Boot** (Démarrage sur carte SD).

   ![Sélectionner le démarrage sur carte SD](images/04-rpi-sd.png)

5. Cliquez sur **CHOOSE STORAGE** (Choisir le stockage), sélectionnez votre carte microSD vierge, cliquez sur **NEXT** (Suivant), puis écrivez l'image.

*Important : Si votre Target est un Raspberry Pi 5 et votre Host est un Raspberry Pi 4 (ou toute autre combinaison mixte), vous ne pouvez pas réutiliser la même carte de mise à jour. Vous devez retourner sur votre ordinateur et flasher une nouvelle carte microSD de mise à jour spécifiquement pour le second type de carte avant de continuer.*

**Effectuer la mise à jour matérielle**

1. Arrêtez proprement les deux machines. Arrêtez le Target en premier, puis le Host (`sudo poweroff`).
2. Débranchez les câbles d'alimentation physique des deux appareils.
3. Retirez les cartes microSD de démarrage principales de chaque appareil et mettez-les de côté en toute sécurité.
4. Insérez délicatement la carte microSD de mise à jour fraîchement préparée dans la carte (assurez-vous que les contacts dorés font face à la face inférieure de la carte Raspberry Pi).
5. Rebranchez l'alimentation de la carte.
6. Observez les voyants d'activité sur la carte. Attendez que la LED verte commence à clignoter rapidement à un rythme régulier et continu (cela prend généralement environ 10 secondes). Le clignotement régulier indique que le flashage de l'EEPROM est terminé.
7. Débranchez l'alimentation de la carte.
8. Retirez la carte microSD de mise à jour et réinsérez votre carte microSD de démarrage d'origine.
9. Rebranchez l'alimentation des systèmes. **Allumez le Host en premier, puis le Target.**

Une fois les systèmes entièrement démarrés et accessibles, exécutez à nouveau la vérification de la version du chargeur de démarrage sur chaque ordinateur pour confirmer que les dates du chargeur de démarrage correspondent à la date de publication écrite par l'Imager. Si votre Host et votre Target utilisent des types de cartes différents (par ex., RPi4 et RPi5), les versions seront probablement différentes. C'est normal.

```bash
vcgencmd bootloader_version
```

---

#### **Partie 2 :** Mettre à jour AudioLinux et le logiciel Diretta

Le processus de mise à jour du système nécessite une séquence stricte pour garantir que le noyau personnalisé, les chaînes de compilation (toolchains) et le démon ALSA restent parfaitement synchronisés.

#### Maintenant, procédez aux mises à jour
1. Lancez l'outil de configuration AudioLinux en tapant `menu` à l'invite de commande.
2. Naviguez vers le **Install/Update menu** et sélectionnez **UPDATE System**.
3. Tout en restant dans le **Install/Update menu**, sélectionnez **UPDATE menu**.
   *(Note : Vous devrez saisir l'adresse e-mail utilisée lors de votre achat d'AudioLinux, ainsi que le nom d'utilisateur et le mot de passe spécifiques fournis par Piero pour le téléchargement de l'image d'AudioLinux).*
4. Sélectionnez **SELECT/UPDATE kernel**. Choisissez la version exacte du noyau recommandée précédemment à l'[**Étape 4**](#44-run-system-and-menu-updates).
5. Réappliquez le correctif `motd` de la [**Section 5.1**](#51-pre-configure-the-diretta-host) sur le **Host**.
6. Réappliquez le correctif `sudoers` de la [**Section 7.2**](#72-correct-sudoers-rule-precedence) sur le Target **et** le Host.
7. Redémarrez le Target en premier, puis le Host.
8. Une fois de retour en ligne, réexécutez le script « Configure Compatible Compiler Toolchain » de l'[**Étape 8**](#8-installation-et-configuration-du-logiciel-diretta) sur le Target **et** le Host.
9. Sur le **Target**, exécutez l'étape d'installation/mise à jour de Diretta détaillée à la [**Section 8.1**](#81-on-the-diretta-target).
10. Sur le **Host**, exécutez l'étape d'installation/mise à jour de Diretta détaillée à la [**Section 8.2**](#82-on-the-diretta-host).
11. Redémarrez le Target en premier, puis le Host.
>
>
> ---
>
> ### ✅ Checkpoint : État du système et tests de régression
>
> Après après avoir terminé la séquence de mise à jour, vous devez vérifier la stabilité du flux audio pour vous assurer qu'aucune régression logicielle ou de configuration ne s'est produite lors de la mise à niveau.
>
> 1. Ouvrez Roon, attendez que la zone réseau revienne, et lancez la lecture d'au moins quelques secondes de musique pour vérifier la liaison de la couche de transport et faire fonctionner les compteurs matériels.
> 2. Connectez-vous en SSH au **Target** et revenez temporairement en Mode Standard pour permettre aux scripts de diagnostic de faire passer le trafic proprement sur le câble :
>    ```bash
>    purist-mode --revert
>    ```
> 3. Exécutez le script universel de QA **System Health Check** de l'[**Annexe 5**](#14-annexe-5--system-health-checks-vérifications-de-létat-du-système) sur le Host **et** le Target.
> 4. Vérifiez attentivement la sortie et résolvez tout problème d'affinité ou de priorité des threads isolés détecté par le script.
>
> ---

---

#### **Partie 3 :** Forcer les limites de courant USB (Raspberry Pi 5 uniquement)

Si vous utilisez un Raspberry Pi 5 et l'alimentez avec une alimentation tierce haut de gamme (par ex., iFi SilentPower Elite 5V ou une alimentation linéaire capable de fournir 5 A) plutôt qu'avec l'alimentation USB-C officielle Raspberry Pi de 27 W, le Pi se négociera par défaut sur un mode sécurisé de 5 V / 3 A. Cela limite la consommation combinée de courant sur les quatre ports USB à 600 mA.

Bien que cela soit généralement sans conséquence pour les transports audio purs, si vous savez que votre alimentation est capable de fournir en continu au moins 5 A sous 5 V, vous pouvez contourner cette restriction en toute sécurité.

**Exécutez cette commande pour ajouter la surcharge à votre configuration de démarrage (boot configuration) :**

```bash
if ! grep -q "^usb_max_current_enable=" /boot/config.txt; then
  echo "usb_max_current_enable=1" | sudo tee -a /boot/config.txt
else
  echo "Optimisation déjà présente dans /boot/config.txt. Configuration ignorée."
fi
sudo sync && sudo reboot
```

---
