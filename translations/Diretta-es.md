# Construcción de un enlace Diretta dedicado con AudioLinux en Raspberry Pi

Esta guía proporciona instrucciones detalladas paso a paso para configurar dos dispositivos Raspberry Pi como un Diretta Host y un Diretta Target dedicados. Esta configuración utiliza una conexión Ethernet directa de punto a punto entre los dos dispositivos para lograr el máximo aislamiento de red y rendimiento de audio.

El **Diretta Host** se conectará a su red principal (para acceder a su servidor de música) y también actuará como puerta de enlace para el Target. El **Diretta Target** se conectará únicamente al Host y a su DAC USB o DDC.

## Gestión de versiones

Mi objetivo es mantener esta guía compatible con el enlace de descarga oficial actual de AudioLinux proporcionado por Piero.

**Validación actual:**
Estas instrucciones fueron probadas por última vez con **AudioLinux V5** (Imagen: `audiolinux_pi4-pi5_520`, Versión del menú: `536`).

**Una nota sobre las actualizaciones:**
Debido a que AudioLinux se basa en Arch (una distribución de actualización continua o "rolling release"), una instalación nueva siempre obtendrá el software más reciente. Una vez que su sistema esté funcionando perfectamente, tiene dos opciones:

1.  **Actualizar con frecuencia:** Comprometerse a actualizar al menos mensualmente para poder solucionar pequeños fallos a medida que ocurran.
2.  **Bloquear la configuración (Recomendado):** Si suena de maravilla, no lo toque. ¡Cree una imagen de respaldo y disfrute de la música!

## Una introducción a la arquitectura de referencia de Roon

Bienvenido a la guía definitiva para construir un punto final (endpoint) de transmisión Roon de última generación. Aunque AudioLinux admite otros protocolos, utilizaré Roon como ejemplo para esta instalación. Puede utilizar el sistema de menús del Diretta Host para instalar soporte para otros protocolos, incluidos HQPlayer, Audirvana, DLNA, AirPlay, etc. Antes de sumergirse en las instrucciones paso a paso, es importante entender el "por qué" detrás de este proyecto. Esta introducción explicará el problema que resuelve esta arquitectura, por qué es fundamentalmente superior a muchas alternativas comerciales de alto costo y cómo este proyecto de bricolaje (DIY) representa un camino directo y gratificante para liberar la máxima calidad de sonido de su sistema Roon.

### La paradoja de Roon: Una experiencia potente con una advertencia sonora

Roon es aclamado, casi universalmente, como el sistema de gestión de música más potente y atractivo disponible. Sus ricos metadatos y su impecable experiencia de usuario son insuperables. Sin embargo, esta supremacía funcional se ha visto empañada durante mucho tiempo por una crítica persistente de un sector ruidoso de la comunidad audiófila: que la calidad de sonido de Roon puede verse comprometida, a menudo descrita como "plana, aburrida y sin vida" en comparación con otros reproductores.

Este "Sonido Roon" no es un mito, ni tampoco un fallo en el software de transmisión perfecta (bit-perfect) de Roon. Es un síntoma potencial de la naturaleza potente y de uso intensivo de recursos de Roon. El Core "pesado" de Roon requiere una potencia de procesamiento significativa, lo que a su vez genera ruido eléctrico (RFI/EMI). Cuando la computadora que ejecuta el Roon Core está muy cerca de su sensible conversor digital a analógico (DAC), este ruido puede contaminar la etapa de salida analógica, enmascarando los detalles, reduciendo el escenario sonoro y robando la vitalidad de la música.

---

### Ir más allá de los "parches" hacia una solución fundamental

La propia Roon Labs aboga por una arquitectura de "dos cajas" para resolver este problema principal: separar el exigente **Roon Core** de un **Endpoint** de red ligero (también llamado transporte de transmisión). Este es el primer paso correcto, ya que traslada el procesamiento pesado a una máquina remota, aislando su ruido de su rack de audio.

Sin embargo, incluso en este diseño superior de dos niveles, persiste un problema más sutil. Los protocolos de red estándar, incluido el propio RAAT de Roon, entregan los datos de audio en "ráfagas" intermitentes. Esto obliga a la CPU del endpoint a aumentar constantemente su actividad para procesar estas ráfagas, lo que provoca fluctuaciones rápidas en el consumo de corriente. Estas fluctuaciones generan su propio ruido eléctrico de baja frecuencia justo en el endpoint, el componente más cercano a su DAC.

Los fabricantes de audio de gama alta intentan combatir los *síntomas* de este tráfico de ráfagas con varias soluciones "parche": fuentes de alimentación lineales masivas para manejar mejor los picos de corriente, CPU de consumo ultra bajo para minimizar la intensidad de los picos y etapas de filtrado adicionales para limpiar el ruido resultante. Si bien estas estrategias pueden ayudar, no abordan la causa raíz del ruido: el procesamiento en ráfagas en sí mismo.

Esta guía presenta una solución más elegante y drásticamente más eficaz. En lugar de intentar limpiar el ruido, construiremos una arquitectura que evita que el ruido se genere en primer lugar.

---

### La arquitectura de tres niveles: Roon + Diretta

Este proyecto evoluciona la configuración de dos cajas recomendada por Roon en un sistema definitivo de tres niveles que proporciona múltiples capas compuestas de aislamiento.

1.  **Nivel 1: Roon Core**: Su potente servidor Roon se ejecuta en una máquina dedicada, ubicada lejos de su sala de escucha. Realiza todo el trabajo pesado y su ruido eléctrico se mantiene aislado de su sistema de audio.
2.  **Nivel 2: Diretta Host**: La primera Raspberry Pi de nuestra configuración actúa como el **Diretta Host**. Se conecta a su red principal, recibe la transmisión de audio del Roon Core y luego la transmite en segmentos pequeños y sincronizados con precisión, eliminando la naturaleza en ráfagas de la transmisión original.
3.  **Nivel 3: Diretta Target**: La segunda Raspberry Pi, el **Diretta Target**, se conecta *únicamente* a la Pi Host a través de un cable Ethernet corto, creando un enlace de punto a punto galvánicamente aislado. Recibe el audio del Host y se conecta a su DAC o DDC a través de USB.

### Qué aportan Diretta y AudioLinux

La superioridad de este diseño proviene de dos componentes de software clave que se ejecutan en los dispositivos Raspberry Pi:

* **AudioLinux**: Este es un sistema operativo en tiempo real diseñado específicamente para uso audiófilo. A diferencia de un sistema operativo de propósito general, está optimizado para minimizar las latencias del procesador y el "jitter" del sistema, proporcionando una base estable y de bajo ruido para nuestro endpoint.
* **Diretta**: Este protocolo revolucionario es el ingrediente secreto que resuelve el problema de raíz. Reconoce que las fluctuaciones en la carga de procesamiento del endpoint generan ruido eléctrico de baja frecuencia que puede evadir el filtrado interno de un DAC (definido por su Relación de Rechazo de Fuente de Alimentación, o PSRR) y degradar sutilmente su rendimiento analógico. Para combatir esto, Diretta emplea su modelo "Host-Target", donde el Host envía datos en una transmisión continua y sincronizada de paquetes pequeños y espaciados de manera uniforme. Esto "promedia" la carga de procesamiento en el dispositivo Target, estabilizando su consumo de corriente y minimizando la generación de este perjudicial ruido eléctrico.

La combinación del aislamiento galvánico físico del enlace Ethernet de punto a punto y la eliminación del ruido de procesamiento del protocolo Diretta crea una ruta de señal profundamente limpia hacia su DAC, una que puede superar a soluciones que cuestan miles de dólares.

---

### Un camino gratificante hacia la excelencia sonora

Este proyecto es más que un simple ejercicio técnico; es una forma gratificante de involucrarse con el pasatiempo y tomar el control directo del rendimiento de su sistema. Al construir este "Puente Diretta", no solo está ensamblando componentes; está implementando una arquitectura de última generación que aborda directamente los desafíos centrales del audio digital. Obtendrá una comprensión más profunda de lo que realmente importa para la reproducción digital y será recompensado con un nivel de claridad, detalle y realismo musical de Roon que quizás no creía posible.

Ahora, comencemos.

---

Si se encuentra en los EE. UU., espere pagar alrededor de $320 (más impuestos y envío) para completar la construcción básica, limitada a reproducción de 44.1/48 kHz (para evaluación), más otros €100 para habilitar la reproducción de alta resolución (precios sujetos a cambios):
- Hardware ($240)
- Suscripción de un año a AudioLinux ($79)
- Licencia de Diretta Target (€100)

## Tabla de contenidos
1.  [Requisitos previos](#1-requisitos-previos)
2.  [Preparación inicial de la imagen](#2-preparaci%C3%B3n-inicial-de-la-imagen)
3.  [Configuración del sistema base (Realizar en ambos dispositivos)](#3-configuraci%C3%B3n-del-sistema-base-realizar-en-ambos-dispositivos)
4.  [Actualizaciones del sistema (Realizar en ambos dispositivos)](#4-actualizaciones-del-sistema-realizar-en-ambos-dispositivos)
5.  [Configuración de red de punto a punto](#5-configuraci%C3%B3n-de-red-de-punto-a-punto)
6.  [Acceso SSH cómodo y seguro](#6-acceso-ssh-c%C3%B3modo-y-seguro)
7.  [Optimizaciones comunes del sistema](#7-optimizaciones-comunes-del-sistema)
8.  [Instalación y configuración del software Diretta](#8-instalaci%C3%B3n-y-configuraci%C3%B3n-del-software-diretta)
9.  [Pasos finales e integración con Roon](#9-pasos-finales-e-integraci%C3%B3n-con-roon)
10. [Apéndice 1: Control de ventilador Argon ONE opcional](#10-ap%C3%A9ndice-1-control-de-ventilador-argon-one-opcional)
11. [Apéndice 2: Control remoto IR opcional](#11-ap%C3%A9ndice-2-control-remoto-ir-opcional)
12. [Apéndice 3: Modo purista opcional](#12-ap%C3%A9ndice-3-modo-purista-opcional)
13. [Apéndice 4: Interfaz web de control del sistema opcional](#13-ap%C3%A9ndice-4-interfaz-web-de-control-del-sistema-opcional)
14. [Apéndice 5: Comprobaciones de estado del sistema](#14-ap%C3%A9ndice-5-comprobaciones-de-estado-del-sistema)
15. [Apéndice 6: Ajuste de rendimiento en tiempo real opcional](#15-ap%C3%A9ndice-6-ajuste-de-rendimiento-en-tiempo-real-opcional)
16. [Apéndice 7: Optimizaciones de IRQ e hilos opcionales](#16-ap%C3%A9ndice-7-optimizaciones-de-irq-e-hilos-opcionales)
17. [Apéndice 8: Velocidades de red puristas opcionales](#17-ap%C3%A9ndice-8-velocidades-de-red-puristas-opcionales)
18. [Apéndice 9: Optimización de tramas jumbo opcional](#18-ap%C3%A9ndice-9-optimizaci%C3%B3n-de-tramas-jumbo-opcional)
19. [Apéndice 10: Actualizaciones del sistema opcionales](#19-ap%C3%A9ndice-10-actualizaciones-del-sistema-opcionales)
20. [Apéndice 11: Integración opcional de UPnP](#20-apendice-11-integracion-opcional-de-upnp)

---

### **Cómo usar esta guía**

Esta guía está diseñada para ser lo más sencilla posible, minimizando la necesidad de editar archivos manualmente. El flujo de trabajo principal consistirá en **copiar y pegar** bloques de comandos de este documento directamente en una ventana de terminal conectada a sus dispositivos Raspberry Pi.

Este es el proceso que seguirá para la mayoría de los pasos:

1.  **Conectarse a través de SSH**: Utilizará un cliente SSH en su computadora principal para iniciar sesión en el **Diretta Host** o en el **Diretta Target** según se indique en cada sección.
2.  **Copiar el comando**: En su navegador web, desplace el cursor sobre la esquina superior derecha de un bloque de comandos en esta guía. Aparecerá un **icono de copia**. Haga clic en él para copiar todo el bloque a su portapapeles.
3.  **Pegar y ejecutar**: Pegue los comandos copiados en la ventana de terminal SSH correcta y presione `Enter`.

Los scripts y comandos se han escrito cuidadosamente para ser seguros y evitar errores, incluso si se ejecutan más de una vez. Al seguir este método de copiar y pegar, puede evitar errores tipográficos y de configuración comunes.

---

### Videoguía paso a paso

Aquí tiene un enlace a una serie de videos cortos que explican este proceso:

* [Videoguía de construcción de Diretta con dos computadoras Raspberry Pi](https://youtube.com/playlist?list=PLMl09rJ6zKCk13V-IH_kRKW7FP8Q0_Fw0&si=u_E8rUEhgMiQ4NIb)

---

### 1. Requisitos previos

#### Hardware

A continuación se proporciona una lista completa de materiales. Aunque se pueden sustituir otras piezas, el uso de estos componentes específicos mejora las posibilidades de una construcción exitosa.

**Componentes principales (de [pishop.us](https://www.pishop.us/) o proveedor similar):**
* 2 x [Raspberry Pi 5/1GB](https://www.pishop.us/product/raspberry-pi-5-1gb/)
* 2 x [Carcasa Flirc Raspberry Pi 5](https://www.pishop.us/product/flirc-raspberry-pi-5-case/)
* 2 x [Tarjeta microSDXC A2 de 64 GB](https://www.bhphotovideo.com/c/product/1830849-REG/lexar_lmssipl064g_bnanu_64gb_silver_plus_microsdxc.html)
* 2 x [Fuente de alimentación USB-C oficial de Raspberry Pi de 45 W - Blanco](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)

**Componentes de red requeridos:**
* 1 x [Adaptador Plugable USB 3.0 a Ethernet](https://www.amazon.com/dp/B00AQM8586) (para el Diretta Host)
* 1 x [Cable de red CAT6 corto](https://www.amazon.com/Cable-Matters-Snagless-Ethernet-Internet/dp/B0B57S1G2Y/?th=1) (para el enlace de punto a punto)

**Opcional, pero útil para la resolución de problemas:**
* 1 x [Cable de Micro-HDMI a HDMI estándar (A/M) de 2m, Blanco](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Teclado oficial de Raspberry Pi - Rojo/Blanco](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**Mejoras opcionales:**
* 2 x [Carcasa Argon ONE V3 Raspberry Pi 5](https://www.amazon.com/Argon-ONE-V3-Raspberry-Case/dp/B0CNGSXGT2/) (en lugar de las carcasas Flirc)
* 1 x [Control remoto IR Argon](https://www.amazon.com/Argon-Raspberry-Infrared-Batteries-Included/dp/B091F3XSF6/) (para añadir capacidades de control remoto al Diretta Host)
* 1 x [Receptor IR USB Flirc](https://www.pishop.us/product/flirc-rpi-usb-xbmc-ir-remote-receiver/) (para usar el control remoto IR Argon con el Diretta Host en una carcasa Flirc)
* 1 x [Cable Blue Jeans BJC CAT6a Belden Bonded Pairs 500 MHz](https://www.bluejeanscable.com/store/data-cables/index.htm) (para la conexión de punto a punto entre el Host y el Target)
* 1 x [iFi SilentPower iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (para proporcionar alimentación limpia al Diretta Target)
* 1 x [Cable USB iFi SilentPower Pulsar](https://www.silentpower.tech/products/pulsar-usb) (conexión USB con aislamiento galvánico)
* 1 x [Adaptador de CC de 5.5mm x 2.1mm a USB-C](https://www.amazon.com/5-5mm-Adapter-Female-Convert-Connector/dp/B0CRB7N4GH/) (necesario para adaptar el conector del iPower Elite a la entrada de alimentación USB-C del Diretta Target)
* 1 x [DDC SMSL PO100 PRO](https://www.amazon.com/dp/B0BLYVZCV5) (un conversor digital a digital para DACs que carecen de una buena implementación de entrada USB)
* 1 x [Adaptador inalámbrico USB](https://www.pishop.us/product/raspberry-pi-dual-band-5ghz-2-4ghz-usb-wifi-adapter-with-antenna/) (una conexión cableada es muy preferible y más confiable, pero si no es práctico agregar Ethernet cableada cerca de su sistema de audio, reemplace el adaptador Plugable USB a Ethernet con este adaptador Wi-Fi)
* 1 x [Cable divisor de alimentación](https://www.amazon.com/dp/B01K3ADXX2?th=1) (conecte ambos adaptadores de corriente de 45 W en un solo tomacorriente)

**Componente de audio requerido:**
* 1 x DAC o DDC USB

**Herramientas de construcción requeridas:**
* Laptop o PC de escritorio con Linux, macOS (se recomienda iTerm2, https://iterm2.com/) o Microsoft Windows con [WSL2](https://learn.microsoft.com/es-es/windows/wsl/install)
* Un lector de tarjetas SD o microSD
* Un televisor o pantalla HDMI y un teclado USB (opcional, pero útil para la resolución de problemas)

#### Costos de software y licencias

* **AudioLinux:** Se recomienda una licencia "Unlimited" para los entusiastas, actualmente cuesta **$158** (precios sujetos a cambios). Sin embargo, está bien comenzar con una suscripción de un año, actualmente de **$79**. Ambas opciones permiten la instalación en múltiples dispositivos dentro de la misma ubicación.
* **Diretta Target:** Se requiere una licencia para la reproducción de alta resolución (superior a PCM de 48 kHz) a través del dispositivo Diretta Target y actualmente cuesta **€100**.
    * Puede evaluar el Diretta Target utilizando transmisiones de 44.1/48 kHz durante un período prolongado. Por lo tanto, recomiendo usar la función **Conversión de frecuencia de muestreo** de Roon bajo la configuración DSP de **MUSE** para convertir todo el contenido a 44.1 kHz durante su período de evaluación. Una vez que esté satisfecho, adquiera la licencia de Diretta Target para eliminar la restricción. Deje activada la configuración de conversión de frecuencia de muestreo hasta que reciba el segundo correo electrónico del equipo de Diretta indicando que su hardware ha sido activado en su base de datos.
    * **CRÍTICO:** Esta licencia está *vinculada* al hardware específico de la Raspberry Pi para la que se adquiere. Es fundamental que realice el paso final de la licencia en el hardware exacto que tiene la intención de utilizar permanentemente.
    * Diretta puede ofrecer una licencia de reemplazo única en caso de falla del hardware dentro de los dos primeros años (verifique los términos al momento de la compra). Si cambia el hardware por cualquier otro motivo, se deberá adquirir una nueva licencia.

---

### 2. Preparación inicial de la imagen

1.  **Compra y descarga:** Obtenga la imagen de AudioLinux del [sitio web oficial](https://www.audio-linux.com/). Recibirá un enlace para descargar un archivo `.img.gz` o `.img.xz` por correo electrónico, normalmente dentro de las 24 horas posteriores a la compra.
2.  **Grabar la imagen:** Utilice [Raspberry Pi Imager](https://www.raspberrypi.com/software/) para escribir la imagen de AudioLinux descargada en **ambas** tarjetas microSD.

---

### 3. Configuración del sistema base (Realizar en ambos dispositivos)

Después de grabar la imagen, debe configurar cada Raspberry Pi individualmente para evitar conflictos de red.

Para obtener el mejor rendimiento, esta guía utiliza la Raspberry Pi 5 tanto para el Diretta Target (el dispositivo conectado a su DAC) como para el Diretta Host. Configurará el Host primero.

> **ADVERTENCIA CRÍTICA:** Debido a que ambos dispositivos se graban a partir de la misma imagen exacta, tendrán valores de `machine-id` idénticos. Si enciende ambos dispositivos al mismo tiempo mientras están conectados a la misma red local (LAN), es probable que su servidor DHCP les asigne la misma dirección IP, lo que provocará un conflicto de red.
>
> **Debe realizar el arranque inicial y la configuración de cada dispositivo uno a la vez.**

1.  Inserte la tarjeta microSD en la **primera** Raspberry Pi, conéctela a su red y enciéndala. **Nota:** Si está utilizando la carcasa Argon ONE, es posible que escuche ruido del ventilador. No se preocupe. Una vez que haya terminado con la configuración de Diretta, hay instrucciones en el [Apéndice 1](#10-ap%C3%A9ndice-1-control-de-ventilador-argon-one-opcional) para solucionar el ruido del ventilador.
2.  Complete **toda la Sección 3** para este primer dispositivo.
3.  Una vez el primer dispositivo se haya reiniciado con su nueva configuración única, apáguelo.
4.  Ahora, encienda la **segunda** Raspberry Pi y repita **toda la Sección 3** para ella.

Consulte el recibo de su compra de AudioLinux para obtener el usuario SSH predeterminado y las contraseñas de sudo/root. Tome nota de ellos, ya que los utilizará muchas veces a lo largo de este proceso.

Utilizará el cliente SSH en su computadora local para iniciar sesión en las computadoras RPi a lo largo de este proceso. Este cliente requiere que tenga una forma de encontrar la dirección IP de las computadoras RPi, la cual puede cambiar de un reinicio a otro. La forma más fácil de obtener esta información es desde la interfaz web o aplicación del enrutador de su red doméstica, pero opcionalmente puede instalar la aplicación [fing](https://www.fing.com/app/) en su teléfono inteligente o tableta.

Una vez que tenga la dirección IP de una de sus computadoras RPi, use el cliente SSH en su computadora local para iniciar sesión mediante este proceso. Tome nota del comando `ssh` de ejemplo, ya que utilizará comandos similares a este a lo largo de esta guía.
```bash
cmd=$(cat <<'EOT'
read -rp "Ingrese la dirección de su RPi y presione [entrar]: " RPi_IP_Address
echo 'Recordatorio: la contraseña predeterminada está en su correo electrónico de AudioLinux enviado por Piero'
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 3.1. Regenerar el ID de máquina

El `machine-id` es un identificador único para la instalación del sistema operativo. **Debe** ser diferente para cada dispositivo.

```bash
echo ""
echo "ID de máquina anterior: $(cat /etc/machine-id)"
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
echo "Nuevo ID de máquina: $(cat /etc/machine-id)"
```

#### 3.2. Establecer nombres de host únicos

Establezca un nombre de host (hostname) claro para cada dispositivo para identificarlos fácilmente. **Nota:** Si esta no es su primera construcción utilizando estas instrucciones y ya tiene un par de Diretta Host/Target en su red, considere elegir un nombre diferente para este nuevo Diretta Host, como `diretta-host2`, solo para esta parte. Hacerlo facilitará el acceso a los dos de forma independiente más adelante.

**En su PRIMER dispositivo (el futuro Diretta Host):**
```bash
# On the Diretta Host
sudo hostnamectl set-hostname diretta-host
```

**En su SEGUNDO dispositivo (el futuro Diretta Target):**
```bash
# On the Diretta Target
sudo hostnamectl set-hostname diretta-target
```

**En este punto, apague el dispositivo. Repita los [pasos anteriores](#3-configuraci%C3%B3n-del-sistema-base-realizar-en-ambos-dispositivos) para la segunda Raspberry Pi.**
```bash
sudo sync && sudo poweroff
```

---

### 4. Actualizaciones del sistema (Realizar en ambos dispositivos)

Para los pasos de esta sección, por lo general es más eficiente (y menos confuso) completar toda la Sección 4 en el Diretta Host y luego repetir toda la sección en el Diretta Target.

Cada RPi tiene su propio ID de máquina, por lo que puede encenderlas ahora. Si tiene dos cables de red, es más conveniente conectar ambos a su red doméstica al mismo tiempo para los siguientes pasos, pero de lo contrario puede proceder uno a la vez. **Nota**: es probable que su enrutador les asigne direcciones IP diferentes a las que utilizó inicialmente para iniciar sesión. Asegúrese de utilizar la nueva dirección IP con sus comandos SSH. Aquí tiene un recordatorio:

```bash
cmd=$(cat <<'EOT'
read -rp "Ingrese la (nueva) dirección de su RPi y presione [entrar]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 4.1. Instalar "Chrony" para actualizar el reloj del sistema

El reloj del sistema debe ser preciso antes de que podamos instalar actualizaciones. La Raspberry Pi no tiene batería NVRAM, por lo que el reloj debe ajustarse cada vez que arranca. Esto se hace típicamente conectándose a un servicio de red. Este script se asegurará de que el reloj se configure y se mantenga correcto durante el funcionamiento de la computadora.

```bash
sudo id
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh | sudo bash
sleep 5
chronyc sources
```

#### 4.2. Establecer su zona horaria

```bash
cmd=$(cat <<'EOT'
clear
echo "Bienvenido a la configuración interactiva de la zona horaria."
echo "Primero seleccionará una región y luego una zona horaria específica."

# Permitir al usuario seleccionar una región
PS3="Seleccione un número para su región: "

select region in $(timedatectl list-timezones | grep -F / | cut -d/ -f1 | sort -u); do
  if [[ -n "$region" ]]; then
    echo "Ha seleccionado la región: $region"
    break
  else
    echo "Selección no válida. Inténtelo de nuevo."
  fi
done

echo ""

# Permitir al usuario seleccionar una zona horaria dentro de esa región
PS3="Seleccione un número para su zona horaria: "

select timezone in $(timedatectl list-timezones | grep "^$region/"); do
  if [[ -n "$timezone" ]]; then
    echo "Ha seleccionado la zona horaria: $timezone"
    break
  else
    echo "Selección no válida. Inténtelo de nuevo."
  fi
done

# Establecer la zona horaria seleccionada
echo
echo "Estableciendo la zona horaria a ${timezone}..."
sudo timedatectl set-timezone "$timezone"
echo "✅ Se ha establecido la zona horaria."

# Verificar el cambio
echo
echo "Hora y zona horaria actuales del sistema:"
timedatectl status
EOT
)
bash -c "$cmd"
```

#### 4.3. Instalar utilidades de DNS
Instale el paquete `dnsutils` para que la actualización del **menú** tenga acceso al comando `dig`:
```bash
sudo pacman -S --noconfirm --needed dnsutils
```

#### 4.4. Ejecutar actualizaciones del sistema y del menú

Use el sistema de menús de AudioLinux para realizar todas las actualizaciones. Tenga a mano el correo electrónico de Piero con su usuario y contraseña de descarga de la imagen. Los necesitará para la actualización del menú. Le pedirá **su usuario de actualización del menú**, lo cual es un poco confuso. Está solicitando el nombre de usuario y la contraseña que utilizó para descargar la imagen de instalación de AudioLinux.

1.  Ejecute `menu` en la terminal.
2.  Seleccione **INSTALL/UPDATE menu**.
    ```text
    Verificando la licencia...
    Por favor, introduzca la dirección de correo electrónico utilizada en el momento de la compra
    (Solo se le preguntará una vez)
    ?
    <dirección de correo electrónico utilizada para comprar el soporte de AudioLinux>
    OK
    OK

    Por favor, escriba su usuario de actualización de menú
    ?
    <"user:" de AUDIOLINUX RASPBERRY de su correo electrónico de licencia)>
    Por favor, escriba su contraseña de actualización de menú
    ?
    <"password:" de AUDIOLINUX RASPBERRY de su correo electrónico de licencia)>
    ```
3.  En la siguiente pantalla, seleccione **UPDATE system** y deje que el proceso se complete.
4.  Una vez finalizada la actualización del sistema, seleccione **Update menu** en la misma pantalla para obtener la versión más reciente de los scripts de AudioLinux. *Nota:* Necesitará la dirección de correo electrónico que utilizó para comprar AudioLinux y su nombre de usuario y contraseña de descarga.
5.  Salga del sistema de menús para volver a la terminal.

#### 4.5. Reiniciar
Reinicie para cargar el kernel y otras actualizaciones:
```bash
sudo sync && sudo reboot
```

---

### 5. Configuración de red de punto a punto

En esta sección, crearemos los archivos de configuración de red que activarán el enlace privado dedicado. Para evitar la necesidad de un teclado físico y un monitor (acceso a la consola), realizaremos estos pasos mientras ambos dispositivos sigan conectados a su red local (LAN) principal y sean accesibles a través de SSH.

Si acaba de terminar de actualizar su Diretta Target, haga clic [aquí](https://github.com/dsnyder0pc/rpi-for-roon/blob/main/translations/Diretta-es.md#52-preconfigurar-el-diretta-target) para saltar a los pasos de configuración de la red de punto a punto para el Target.

---
> #### **Una nota sobre la configuración de red: ¿Por qué no un puente simple?**
>
> Los usuarios familiarizados con AudioLinux pueden preguntarse por qué esta guía utiliza scripts específicos para configurar un enlace enrutado de punto a punto con NAT en lugar de utilizar la opción más simple de puente de red disponible en el sistema `menu`. Esta es una elección arquitectónica deliberada realizada para lograr el mayor nivel posible de aislamiento de red.
>
> * Un **puente de red** colocaría al Diretta Target directamente en su red local (LAN) principal, exponiéndolo a todo el tráfico de difusión (broadcast) y multidifusión (multicast) no relacionado de la red.
> * Nuestra **configuración enrutada** crea una subred completamente separada y protegida por un firewall. El Diretta Host protege al Target de toda la actividad de red no esencial, asegurando que el procesador del Target solo maneje la transmisión de audio. Esto minimiza la actividad del sistema y el ruido eléctrico potencial, que es el objetivo final de esta arquitectura purista.
>
> Aunque un puente es funcionalmente más sencillo de configurar, el método enrutado proporciona una base teóricamente superior para el rendimiento de audio al maximizar el aislamiento.
---

#### 5.1. Preconfigurar el Diretta Host

1.  **Crear archivos de red:**
    Cree los siguientes dos archivos en el **Diretta Host**. El archivo `end0.network` establece la IP estática para el futuro enlace de punto a punto. El archivo `usb-uplink.network` asegura que el adaptador Ethernet USB continúe obteniendo una IP de su red local (LAN) principal.

    *Archivo: `/etc/systemd/network/end0.network`*
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

    *Archivo: `/etc/systemd/network/usb-uplink.network`*
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

    **Importante:** Elimine el archivo en.network antiguo si está presente:
    ```bash
    # Eliminar el archivo de red genérico antiguo para evitar conflictos.
    sudo rm -fv /etc/systemd/network/{en,enp,auto,eth}.network
    ```

    Agregue una entrada en /etc/hosts para el Diretta Target:
    ```bash
    HOSTS_FILE="/etc/hosts"
    TARGET_IP="172.20.0.2"
    TARGET_HOST="diretta-target"

    # Agregar una entrada para el Diretta Target si no existe
    if ! grep -q "$TARGET_IP\s\+$TARGET_HOST" "$HOSTS_FILE"; then
      printf "%s\t%s target\n" "$TARGET_IP" "$TARGET_HOST" | sudo tee -a "$HOSTS_FILE"
    fi
    ```

2.  **Habilitar el reenvío de IP:**
    ```bash
    # Habilitarlo para la sesión actual
    sudo sysctl -w net.ipv4.ip_forward=1

    # Hacerlo permanente entre reinicios
    echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ip-forwarding.conf
    ```

3.  **Configurar la traducción de direcciones de red (NAT):**
    ```bash
    # Asegurar que nft esté instalado
    sudo pacman -S --noconfirm --needed nftables

    # Instalar las reglas del firewall y NAT
    cat <<'EOT' | sudo tee /etc/nftables.conf
    #!/usr/sbin/nft -f

    # Flush all old rules from memory
    flush ruleset

    # Create a table named 'ip' (IPv4) called 'my_table'
    table ip my_table {

        # === Rule 2: Port Forwarding (DNAT) ===
        # This chain hooks into the 'prerouting' path for NAT
        chain prerouting {
            type nat hook prerouting priority dstnat;

            # Forward Host port 5101 to Target port 172.20.0.2:5001
            tcp dport 5101 dnat to 172.20.0.2:5001
        }

        # === Rule 3: Allow Forwarded Traffic (FILTER) ===
        # This chain hooks into the 'forward' path for packet filtering
        chain forward {
            type filter hook forward priority 0;

            # By default, drop all forwarded traffic
            policy drop;

            # Allow connections that are already established or related
            ct state established,related accept

            # Allow NEW traffic matching your port forward rule
            ip daddr 172.20.0.2 tcp dport 5001 ct state new accept

            # Allow all other NEW traffic from the Target subnet
            ip saddr 172.20.0.0/24 accept
        }

        # === Rule 1: Internet Access (MASQUERADE) ===
        # This chain hooks into the 'postrouting' path for NAT
        chain postrouting {
            type nat hook postrouting priority 100;

            # NAT (Masquerade) traffic from your subnet going
            # out any interface starting with 'enp', 'enu' or 'wlp'
            ip saddr 172.20.0.0/24 oifname "enp*" masquerade
            ip saddr 172.20.0.0/24 oifname "enu*" masquerade
            ip saddr 172.20.0.0/24 oifname "wlp*" masquerade
        }
    }
    EOT

    # Detener y deshabilitar el antiguo servicio iptables si está presente (2>/dev/null suprime errores si no está presente)
    sudo systemctl disable --now iptables.service 2>/dev/null
    sudo rm /etc/iptables/iptables.rules 2>/dev/null

    # Habilitar y aplicar reglas a través de nft
    sudo systemctl enable --now nftables.service
    ```

4.  **Configurar el adaptador Ethernet USB Plugable**

    El controlador USB predeterminado no admite todas las funciones del adaptador Ethernet Plugable. Para obtener un rendimiento confiable, debemos indicarle al administrador de dispositivos del kernel cómo manejar el dispositivo cuando está conectado:
    ```bash
    cat <<'EOT' | sudo tee /etc/udev/rules.d/99-ax88179a.rules
    ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0b95", ATTR{idProduct}=="1790", ATTR{bConfigurationValue}!="1", ATTR{bConfigurationValue}="1"
    EOT
    sudo udevadm control --reload-rules
    ```

5.  **Corregir el script `update_motd.sh`**

    El script que actualiza el banner de inicio de sesión (`/etc/motd`) no maneja correctamente el caso de tener dos interfaces de red. Esto evita que la pantalla de inicio de sesión se llene de información de dirección IP incorrecta después de los reinicios. El nuevo script a continuación soluciona este problema.
    ```bash
    [ -f /opt/scripts/update/update_motd.sh.dist ] || \
    sudo mv /opt/scripts/update/update_motd.sh /opt/scripts/update/update_motd.sh.dist
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh
    sudo install -m 0755 update_motd.sh /opt/scripts/update/
    rm update_motd.sh
    ```

    Finalmente, apague el Host:
    ```bash
    sudo sync && sudo poweroff
    ```

#### 5.2. Preconfigurar el Diretta Target

**Nota:** Si no ha realizado el [paso 4](#4-actualizaciones-del-sistema-realizar-en-ambos-dispositivos) en el Diretta Target, hágalo [ahora](#4-actualizaciones-del-sistema-realizar-en-ambos-dispositivos), luego regrese aquí.

En el **Diretta Target**, cree el archivo `end0.network`. Esto configura su IP estática y le indica que use el Diretta Host como su puerta de enlace para todo el tráfico de Internet.

*Archivo: `/etc/systemd/network/end0.network`*
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

**Importante:** Elimine el archivo en.network antiguo si está presente:
```bash
# Eliminar el archivo de red genérico antiguo para evitar conflictos.
sudo rm -fv /etc/systemd/network/{en,auto,eth}.network
```

Agregue una entrada en /etc/hosts para el Diretta Host. **Nota:** Incluso si seleccionó un nombre de red diferente para su Diretta Host, es mejor que el Diretta Target conozca a su Host como `diretta-host`.
```bash
HOSTS_FILE="/etc/hosts"
HOST_IP="172.20.0.1"
HOST_NAME="diretta-host"

# Agregar una entrada para el Diretta Host si no existe
if ! grep -q "$HOST_IP\s\+$HOST_NAME" "$HOSTS_FILE"; then
  printf "%s\t%s host\n" "$HOST_IP" "$HOST_NAME" | sudo tee -a "$HOSTS_FILE"
fi
```

> ---
> ### ⚠️ Advertencia crítica de topología: Solo ubicación de filtro aguas arriba (upstream)
>
> Si planea mejorar este proyecto con regeneradores LAN, aisladores galvánicos o filtros (como StackAudio SmoothLAN, iFi SilentPower LAN iSilencer o LAN iPurifier Pro), estos **deben colocarse aguas arriba (upstream) del Diretta Host** (entre su enrutador/conmutador de red principal y el adaptador USB a Ethernet del Host).
>
> **Nunca coloque un filtro de red o un dispositivo de regeneración de reloj activo en el enlace de punto a punto entre el Host y el Target.** Hacerlo casi siempre degradará el rendimiento de audio y puede causar graves regresiones en la conexión.
>
> * **La LAN principal es la fuente primaria de ruido:** La conexión desde su enrutador doméstico o conmutador principal está inundada de interferencia electromagnética (EMI), interferencia de radiofrecuencia (RFI) y tráfico "basura" de difusión (broadcast). Colocar un regenerador *antes* del Host elimina esta contaminación digital en el límite. El Host procesa entonces una transmisión impecable, manteniendo al mínimo absoluto su propio consumo de CPU, fluctuaciones de energía y ruido térmico.
> * **Preservar la temporización de Capa 2:** La introducción de un dispositivo activo en el puente directo de punto a punto interfiere con las restricciones de temporización extremadamente ajustadas de Diretta (`CycleTime` y `syncBufferCount`). Esto perjudica la entrega precisa de las tramas de Capa 2, lo que resulta en menores mejoras sonoras, artefactos de latencia o una falla completa del Target al negociar los cambios de velocidad de red.
> * **El principio de aislamiento en cascada:** El verdadero aislamiento se construye en capas para desacoplar completamente su sensible DAC de la red doméstica:
>   * **Red principal** → `[ Filtro/Regenerador LAN ]` → **Diretta Host** *(Aísla al Host de la red doméstica)*
>   * **Diretta Host** → `[ Cable Ethernet dedicado ]` → **Diretta Target** *(Aislado a través de un enlace de punto a punto y la pila de protocolos)*
> ---

#### 5.3. El cambio de conexión física

> **Advertencia:** Verifique dos veces el contenido de los archivos que acaba de crear. Un error tipográfico podría hacer que un dispositivo sea inaccesible después de reiniciar, lo que requeriría una sesión de consola o volver a grabar la tarjeta SD para solucionarlo.

1.  Una vez que haya verificado los archivos, realice un apagado limpio de **ambos** dispositivos:
    ```bash
    sudo sync && sudo poweroff
    ```
2.  Desconecte ambos dispositivos del conmutador/enrutador de su red local (LAN) principal.
3.  Conecte el **puerto Ethernet integrado** del Diretta Host directamente al **puerto Ethernet integrado** del Diretta Target utilizando un solo cable Ethernet.
4.  Conecte el **adaptador USB a Ethernet** en uno de los puertos USB 3.0 del Diretta Host.
5.  Conecte el **adaptador USB a Ethernet** del Diretta Host al conmutador/enrutador de su red local (LAN) principal.
6.  Encienda ambos dispositivos.

Al arrancar, utilizarán automáticamente las nuevas configuraciones de red. **Nota:** la dirección IP de su Diretta Host probablemente habrá cambiado porque ahora está conectado a su red doméstica a través del adaptador USB a Ethernet. Tendrá que volver a la interfaz web de su enrutador o a la aplicación Fing para encontrar la nueva dirección, que debería ser estable en este punto.

```bash
cmd=$(cat <<'EOT'
read -rp "Ingrese la dirección final de su Diretta Host y presione [entrar]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

Ahora debería poder hacer ping al Target desde el Host:
```bash
echo ""
echo "\$ ping -c 3 172.20.0.2"
ping -c 3 172.20.0.2
```

Además, debería poder iniciar sesión en el Target desde el Host:
```bash
echo ""
echo "\$ ssh target"
ssh -o StrictHostKeyChecking=accept-new target
```

Desde el Target, intentemos hacer ping a un host en Internet para verificar que la conexión está funcionando:
```bash
echo ""
echo "\$ ping -c 3 one.one.one.one"
ping -c 3 one.one.one.one
```

---

### 6. Acceso SSH cómodo y seguro

#### 6.1. El requisito de `ProxyJump`

Ahora que la red está configurada, el **Diretta Target** está en una red aislada (`172.20.0.0/24`) y no se puede acceder a él directamente desde su red local (LAN) principal. La única forma de acceder es "saltando" a través del **Diretta Host**.

La directiva `ProxyJump` en su configuración de SSH local es el método estándar y requerido para lograr esto.

1.  Ejecute este comando en su computadora local (no en la Raspberry Pi). Le solicitará la dirección IP del Diretta Host y luego imprimirá el bloque de configuración exacto que necesita.
```bash
cmd=$(cat <<'EOT'
clear
# --- Script de configuración interactiva de alias SSH ---

SSH_CONFIG_FILE="$HOME/.ssh/config"
SSH_DIR="$HOME/.ssh"

# --- Asegurar que el directorio .ssh y el archivo de configuración existan con los permisos correctos ---
mkdir -p "$SSH_DIR"
chmod 0700 "$SSH_DIR"
touch "$SSH_CONFIG_FILE"
chmod 0600 "$SSH_CONFIG_FILE"

# --- Definir el bloque de configuración global recomendado ---
GLOBAL_SETTINGS=$(cat <<'EOF'
# --- Configuración SSH global recomendada ---
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519

EOF
)

# --- Anteponer la configuración global si no existe ---
if ! grep -q "AddKeysToAgent yes" "$SSH_CONFIG_FILE"; then
  echo "✅ Agregando la configuración SSH global recomendada..."
  # Use a temporary file to prepend the settings
  echo "$GLOBAL_SETTINGS" | cat - "$SSH_CONFIG_FILE" > temp_ssh_config && mv temp_ssh_config "$SSH_CONFIG_FILE"
else
  echo "✅ La configuración SSH global recomendada ya existe. No se realizaron cambios."
fi

# --- Agregar configuraciones de host específicas de Diretta ---
if grep -q "Host diretta-host" "$SSH_CONFIG_FILE"; then
  echo "✅ La configuración SSH para 'diretta-host' ya existe. No se realizaron cambios."
else
  read -rp "Ingrese la dirección IP LAN de su Diretta Host y presione [Enter]: " Diretta_Host_IP

  # Append the new configuration using a heredoc for clarity
  cat <<EOT_HOSTS >> "$SSH_CONFIG_FILE"

# --- Configuración de Diretta (agregada por script) ---
Host diretta-host host
    HostName ${Diretta_Host_IP}
    User audiolinux

Host diretta-target target
    HostName 172.20.0.2
    User audiolinux
    ProxyJump diretta-host
EOT_HOSTS

  echo "✅ Se ha agregado la configuración SSH para 'diretta-host' y 'diretta-target'."
fi

# --- Limpiar StrictHostKeyChecking de versiones anteriores de esta guía ---
# Esto ya no es necesario con la configuración de clave SSH recomendada
if command -v sed >/dev/null; then
    sed -i.bak -e '/StrictHostKeyChecking/d' "$SSH_CONFIG_FILE"
    # Eliminar líneas vacías que puedan haber quedado
    sed -i.bak -e '/^$/N;/^\n$/D' "$SSH_CONFIG_FILE"
    rm -f "${SSH_CONFIG_FILE}.bak"
fi

echo ""
echo "--- Su archivo ~/.ssh/config ahora contiene: ---"
cat "$SSH_CONFIG_FILE"
EOT
)
bash -c "$cmd"
```

2.  **Verificar la conexión:**

Ahora debería poder conectarse a ambos dispositivos utilizando los nuevos alias. Pruebe la conexión con los siguientes comandos:

**Para iniciar sesión en el Diretta Host:**
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-host
```

Escriba `exit` para cerrar la sesión.

**Para iniciar sesión en el Diretta Target:** _(se le solicitará la contraseña dos veces)_
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-target
```
**Nota:** Se le solicitará la contraseña una vez para el diretta-host (el servidor de salto) y una segunda vez para el diretta-target en sí. La siguiente sección reemplazará esto con una autenticación transparente basada en claves.

**Nota:** Puede usar `ssh host` y `ssh target` para abreviar.

#### 6.2. Recomendado: Autenticación segura con claves SSH

Aunque puede utilizar contraseñas, el método más seguro y cómodo es la autenticación por clave pública. Nuestra configuración de SSH automatiza la mayor parte del proceso. Después de una configuración única, podrá iniciar sesión tanto en el Host como en el Target de forma segura sin tener que escribir una contraseña.

**En su computadora local:**

1.  **Crear una clave SSH (si aún no tiene una):**
    La mejor práctica es utilizar un algoritmo moderno como `ed25519`. Cuando se le solicite, ingrese una **frase de contraseña** fuerte y memorable. Esta no es su contraseña de inicio de sesión; es una contraseña que protege el archivo de su clave privada en sí.

    ```bash
    ssh-keygen -t ed25519 -C "audiolinux"
    ```

2.  **Copiar su clave pública a los dispositivos:**
    Estos comandos otorgan de forma segura acceso a su clave en cada dispositivo. El primer comando solicitará la contraseña del Diretta Host. Debido a que eso hace que la conexión al Host sea sin contraseña, el segundo comando solo solicitará la contraseña del Diretta Target.

    ```bash
    echo ""
    ssh-copy-id diretta-host
    echo ""
    ssh-copy-id diretta-target
    ```

3.  **Iniciar sesión de forma segura:**
    Ahora puede conectarse por SSH a sus dispositivos. La primera vez que se conecte a cada uno, se le solicitará la **frase de contraseña** que creó en el Paso 1.

    ```bash
    ssh diretta-host
    ```

      * **En Linux:** Gracias a la configuración `AddKeysToAgent yes`, su clave se agregará al agente SSH para su sesión de terminal actual. No se le volverá a solicitar la frase de contraseña hasta que reinicie o inicie una nueva sesión.

---

### (Opcional) Para una mejor experiencia en Linux

Si es usuario de Linux y desea que la frase de contraseña de su clave SSH persista entre reinicios (similar a la experiencia en macOS), se recomienda encarecidamente instalar `keychain`.

  * **Instalar keychain (Ubuntu/Debian):**

    ```bash
    sudo apt update && sudo apt install keychain
    ```

  * **Configurar su shell:** Agregue la siguiente línea a su `~/.bashrc` (o `~/.zshrc`, `~/.profile`, etc.) para iniciar `keychain` cuando abra una terminal. Le solicitará su frase de contraseña solo una vez, la primera vez que abra una terminal después de un reinicio.

    ```bash
    eval "$(keychain --eval --quiet id_ed25519)"
    ```

  * Recargue su shell abriendo una nueva terminal o ejecutando `source ~/.bashrc`.

Ahora puede conectarse por SSH a ambos dispositivos (`ssh diretta-host`, `ssh diretta-target`) sin que se le solicite una contraseña, autenticado de forma segura por su clave SSH.

---

### 7. Optimizaciones comunes del sistema

Realice estos pasos tanto en el Diretta Host como en el Diretta Target. Si realiza una actualización del `menu` más adelante, deberá volver a aplicar la corrección de `sudoers`.

#### 7.1. Corregir el estado "degradado" de Systemd

En una instalación limpia de AudioLinux, el estado del sistema a menudo se reporta como `degraded`. Esto suele deberse a una inconsistencia inofensiva entre los archivos de grupos del sistema (`/etc/group` y `/etc/gshadow`). El siguiente comando sincroniza de forma segura estos archivos, lo que resuelve el fallo de `shadow.service` y garantiza un estado limpio del sistema.

```bash
sudo grpconv
```

#### 7.2. Corregir la precedencia de reglas de `sudoers`

Una regla predeterminada en el archivo principal `/etc/sudoers` a veces puede anular reglas más específicas necesarias para la interfaz web y otras funciones. Esto puede causar que los comandos que no deberían requerir contraseña soliciten una de forma incorrecta.

El siguiente script corrige de forma segura el orden de las reglas en el archivo `/etc/sudoers` para garantizar que las excepciones específicas se procesen correctamente. El script solo realizará cambios si detecta el orden incorrecto.

```bash
SUDOERS_FILE="/etc/sudoers"
TEMP_SUDOERS=$(mktemp)

# Usar un filtro de Perl para crear una versión corregida del archivo sudoers.
# Este script es idempotente y no cambiará un archivo que ya es correcto.
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

# Validar el nuevo archivo con visudo antes de instalarlo
if [ -s "$TEMP_SUDOERS" ] && sudo visudo -c -f "$TEMP_SUDOERS"; then
    echo "El archivo sudoers pasó la validación. Instalando la versión corregida..."
    # Usar install para establecer los propietarios/permisos correctos y reemplazar el original
    sudo install -m 0440 -o root -g root "$TEMP_SUDOERS" "$SUDOERS_FILE"
else
    echo "ERROR: El archivo sudoers modificado falló la validación. No se realizaron cambios." >&2
fi
rm -f "$TEMP_SUDOERS"
```

#### 7.3. Optimizar el tiempo de arranque
Para evitar un largo retraso en el arranque mientras el sistema espera una conexión de red, deshabilitaremos el servicio "wait-online".
```bash
# Deshabilitar el servicio de espera de red para evitar largos retrasos en el arranque
sudo systemctl disable systemd-networkd-wait-online.service

# Crear una anulación (override) para hacer que el script MOTD espere una ruta predeterminada
sudo mkdir -p /etc/systemd/system/update_motd.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/update_motd.service.d/wait-for-ip.conf
[Service]
ExecStartPre=/bin/sh -c "while [ -z \"$(ip route show default)\" ]; do sleep 0.5; done"
EOT
```

#### 7.4. Crear el script de reparación
El comportamiento predeterminado de Arch Linux es dejar el sistema de archivos /boot en un estado no limpio si la computadora no se apaga limpiamente. Esto suele ser seguro, pero he descubierto que puede crear una condición de carrera al levantar nuestra red privada. Además de eso, es probable que los usuarios desconecten estos dispositivos sin apagarlos primero. Para protegerse contra estos problemas, agregaremos un script alternativo que mantiene limpio el sistema de archivos /boot (que solo se cambia durante las actualizaciones de software).

Este script es seguro de ejecutar tanto de forma automática en el arranque como de forma manual en un sistema activo.
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh
sudo install -m 0755 check-and-repair-boot.sh /usr/local/sbin/
rm check-and-repair-boot.sh
```

#### 7.5. Crear el archivo de servicio `systemd` y habilitar el servicio
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

#### 7.6. Minimizar E/S de disco
Cambie `#Storage=auto` por `Storage=volatile` en `/etc/systemd/journald.conf`
```bash
sudo sed -i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
```

---

### 8. Instalación y configuración del software Diretta

#### 8.1. En el Diretta Target

1.  Conecte su DAC USB a uno de los puertos USB 2.0 negros en el **Diretta Target** y asegúrese de que el DAC esté encendido.
2.  Conéctese por SSH al Target: `ssh diretta-target`.
3.  Configurar la cadena de herramientas del compilador compatible (toolchain)
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```
4.  Ejecute `menu`.
5.  Seleccione **AUDIO extra menu**.
6.  Seleccione **DIRETTA target installation/configuration**. Verá el siguiente menú:
    ```text
    ¿Qué desea hacer?

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
7.  Debe realizar estas acciones en secuencia:
    * Elija **1) Install/update** para instalar el software (responda "Y" a todas las preguntas).
    * Elija **2) Enable/Disable Diretta Target** y habilítelo.
    * Elija **3) Configure Audio card**. El sistema enumerará sus dispositivos de audio disponibles. Ingrese el número de tarjeta correspondiente a su DAC USB.
        ```text
        ?3
        Esta opción configurará el target de DIRETTA para usar una tarjeta específica
        Sus tarjetas disponibles son:

        card 0: AUDIO [SMSL USB AUDIO], device 0: USB Audio [USB Audio]

        Por favor, escriba el número de tarjeta (0,1,2...) que desea utilizar:
        ?0
        ```
    * Elija **4) Edit configuration**. Establezca `AlsaLatency=20` para un Target Raspberry Pi 5 o `AlsaLatency=40` para RPi4.
    * Elija **6) License**. El sistema reproducirá audio de alta resolución (superior a PCM de 44.1 kHz) durante 6 minutos en modo de prueba. Siga el enlace y las instrucciones en pantalla para comprar y aplicar su licencia completa para soporte de alta resolución. Esto requiere el acceso a Internet que configuramos en el paso 5.
        ```text
        El precio de esta licencia de terceros es 100$
        Sin licencia, el Target de DIRETTA funcionará durante 6 min.
        Si ve un enlace, puede usarlo para comprar una licencia
        Si ve en su lugar la palabra 'valid', la licencia se ha aplicado correctamente
        Por favor, espere unos segundos...

        https://www.diretta.link/cgi-bin/target_app_regist.cgi?hash=1fd430fe950936867b31cc084a9dac031ffa7c57c8ba1d5034a1a5219444f441&vender=Audlinux


        La licencia se aplicará en el próximo inicio de DIRETTA target
        Presione cualquier tecla para continuar
        ```
    * Elija **8) Exit**. Siga las instrucciones para volver a la terminal

#### 8.2. En el Diretta Host

1.  Conéctese por SSH al Host: `ssh diretta-host`.

2.  Configurar la cadena de herramientas del compilador compatible (toolchain)
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```

3.  Ejecute `menu`.

4.  Seleccione **AUDIO extra menu**.

5.  Seleccione **DIRETTA host installation/configuration**. Verá el siguiente menú:
    ```text
    ¿Qué desea hacer?

    1) Install/update last version
    2) Enable/Disable Diretta daemon
    3) Set Ethernet interface
    4) Edit configuration
    5) Copy and edit new default configuration
    6) Diretta log
    7) Exit

    ?
    ```

6.  Debe realizar estas acciones en secuencia:
    * Elija **1) Install/update** para instalar el software. (Responda "Y" a todas las preguntas). *(Nota: es posible que vea `error: package 'lld' was not found. No se preocupe, esto se corregirá automáticamente mediante la instalación)*.
    * Elija **2) Enable/Disable Diretta daemon** y habilítelo.
    * Elija **3) Set Ethernet interface**. Es fundamental seleccionar `end0`, la interfaz para el enlace de punto a punto.
        ```text
        ?3
        Sus interfaces Ethernet disponibles son: end0  enu1
        Por favor, escriba el nombre de su interfaz preferida:
        end0
        ```
    * Elija **4) Edit configuration** solo si necesita realizar cambios avanzados. Los pasos anteriores deberían ser suficientes; sin embargo, aquí hay algunas configuraciones optimizadas que quizás desee probar:
        ```text
        ScanOnlineStop=enable
        InfoCycle=80000
        FlexCycle=disable
        CycleTime=800
        periodMin=16
        periodSizeMin=2048
        ```

    * Si solo desea instalar los parámetros optimizados anteriores, puede usar este bloque de comandos:
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
    * Elija **7) Exit**. Siga las instrucciones para volver a la terminal

7.  Crear una anulación (override) para hacer que el servicio de Diretta se reinicie automáticamente en caso de fallo
    ```bash
    sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta_alsa.service.d/restart.conf
    [Service]
    Restart=on-failure
    RestartSec=5
    EOT
    ```

---

### 9. Pasos finales e integración con Roon

1.  Ejecute `menu` si regresó a la terminal después del paso anterior, de lo contrario vaya al **Main menu**.

2.  **Instalar Roon Bridge (en el Host):** Si utiliza Roon, realice los siguientes pasos en el **Diretta Host**:
    * Ejecute `menu`.
    * Seleccione **INSTALL/UPDATE menu**.
    * Seleccione **INSTALL/UPDATE Roonbridge**.
    * La instalación continuará. La instalación puede tardar un minuto o dos.

3.  **Habilitar Roon Bridge (en el Host):**
    * Seleccione **Audio menu** desde el Main menu
    * Seleccione **SHOW audio service**
    * Si no ve **roonbridge** en los servicios habilitados, seleccione **ROONBRIDGE enable/disable**

4.  **Reiniciar ambos dispositivos:** Para un inicio limpio, reinicie tanto el Target como el Host, en ese orden:
    ```bash
    sudo sync && sudo reboot
    ```

5.  **Configurar Roon:**
    * Abra Roon en su dispositivo de control.
    * Vaya a `Settings` -> `Audio`.
    * Bajo `diretta-host`, debería ver su dispositivo. El nombre se basará en su DAC.
    * ¡Haga clic en `Enable`, asígnele un nombre y estará listo para reproducir música!

Su enlace Diretta dedicado ahora está completamente configurado para una reproducción de audio impecable y aislada.
**Nota:** La zona "Limited" para las pruebas de Diretta Target desaparecerá de Roon después de seis minutos de reproducción de música de alta resolución. Esto es normal. En ese punto, deberá comprar una licencia para el Diretta Target. El costo actual es de €100 y la activación puede tardar hasta 48 horas en completarse. Recibirá dos correos electrónicos del equipo de Diretta. El primero es su recibo; el segundo, su notificación de activación. Una vez que reciba el correo electrónico de activación, reinicie su computadora Target para aplicar la activación.

> ---
> ### ✅ Punto de control: Verificar su sistema base
>
> Su sistema base Diretta y Roon ahora debería ser completamente funcional. Para verificar todos los servicios y conexiones, proceda al [**Apéndice 5**](#14-ap%C3%A9ndice-5-comprobaciones-de-estado-del-sistema) y ejecute el comando universal **System Health Check** (Comprobación de estado del sistema) tanto en el Host como en el Target.
>
> ---

---

## 10. Apéndice 1: Control de ventilador Argon ONE opcional
Si decidió utilizar una carcasa Argon ONE para su Raspberry Pi, el script de instalación predeterminado asume que está ejecutando un sistema operativo Debian. Sin embargo, AudioLinux se basa en Arch Linux, por lo que deberá seguir estos pasos en su lugar.

Si está utilizando carcasas Argon ONE tanto para el Diretta Host como para el Target, deberá realizar estos pasos en ambas computadoras.

### Paso 1: Omitir el script `argon1.sh` en el manual
El manual dice que descargue el script argon1.sh de download.argon40.com y lo envíe a `bash`. Esto no funcionará en AudioLinux ya que el script asume un sistema operativo basado en Debian, así que omita este paso y siga los pasos a continuación en su lugar.

### Paso 2: Configurar su sistema:
Estas comandos habilitarán la interfaz I2C y agregarán la `dtoverlay` específica para la carcasa Argon ONE. El script primero intenta descomentar el parámetro `i2c_arm` si está comentado y luego agrega la superposición (overlay) `argonone` si falta, evitando errores y entradas duplicadas.
```bash
BOOT_CONFIG="/boot/config.txt"
I2C_PARAM="dtparam=i2c_arm=on"

# --- Habilitar I2C descomentando la línea si existe ---
if grep -q -F "#$I2C_PARAM" "$BOOT_CONFIG"; then
  echo "Habilitando el parámetro I2C..."
  sudo sed -i -e "s/^#\($I2C_PARAM\)/\1/" "$BOOT_CONFIG"
fi
```

### Paso 3: Configurar permisos de `udev`
```bash
cat <<'EOT' | sudo tee /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c-[0-9]*", MODE="0666"
EOT
```

### Paso 4: Instalar el paquete Argon One
```bash
yay -S argonone-c-git
```

**Nota:** Si el comando anterior falla con errores del compilador, puede intentar este procedimiento manual para corregir e instalar el paquete:
```bash
# Clonar el repositorio del paquete
git clone https://aur.archlinux.org/argonone-c-git.git
cd argonone-c-git

# Descargar el código fuente sin compilar
makepkg -o

# Aplicar parche para corregir error de compilación con GCC 14+
sed -i 's/_timer_thread()/_timer_thread(void *args)/g' src/argonone-c-git/src/event_timer.c

# Compilar e instalar usando el código fuente parcheado
makepkg -e -i --noconfirm

# Limpiar
cd ..
rm -rf argonone-c-git
```

### Paso 5: Cambiar la carcasa Argon ONE de control por hardware a control por software
```bash
sudo pacman -S --noconfirm --needed i2c-tools libgpiod
```

```bash
# Crear anulaciones (overrides) de systemd para cambiar la carcasa al modo de software al arrancar
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

### Paso 6: Habilitar el servicio
```bash
# Recargar el administrador de systemd para leer la nueva configuración
sudo systemctl daemon-reload

# Habilitar el servicio para que se inicie al arrancar
sudo systemctl enable argononed.service
```

### Paso 7: Reiniciar
Finalmente, reinicie su Raspberry Pi para que todos los cambios surtan efecto (Target primero, luego Host):
```bash
sudo sync && sudo reboot
```

Ahora, el ventilador será controlado por el demonio (daemon) y el botón de encendido tendrá funcionalidad completa.

### Paso 8: Verificar el servicio
```bash
systemctl status argononed.service
journalctl -u argononed.service -b
```

### Paso 9: Revisar el modo del ventilador y la configuración:
Para ver los valores de configuración actuales, ejecute el siguiente comando:
```bash
sudo argonone-cli --decode
```

Para ajustar esos valores, debe crear un archivo de configuración. Utilice estos valores para comenzar:
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

Reinicie el servicio para aplicar los nuevos valores de configuración:
```bash
sudo systemctl restart argononed.service
echo ""
echo "Valores de ventilador actualizados:"
sleep 5
sudo argonone-cli --decode
```

Ahora, siéntase libre de ajustar los valores según sea necesario, siguiendo los pasos anteriores.

---

## 11. Apéndice 2: Control remoto IR opcional

Esta guía proporciona instrucciones para instalar y configurar un control remoto IR para controlar Roon. La configuración se divide en dos partes.

  * La **Parte 1** cubre la configuración específica del hardware. Elegirá **una** de las dos opciones dependiendo de si está utilizando el receptor USB Flirc o el receptor incorporado de la carcasa Argon One.
  * La **Parte 2** cubre la configuración del software para el script de control `roon-ir-remote`, que es idéntica para ambas opciones de hardware.

**Nota:** _Solo_ realizará estos pasos en el Diretta Host. El Target no debe usarse para transmitir comandos de control remoto IR al Servidor Roon.

---

### **Parte 1: Configuración del hardware del receptor IR**

*Siga el apéndice para el hardware que esté utilizando.*

#### **Opción 1: Configuración del receptor IR USB Flirc**

1.  **Comprar y programar el dispositivo Flirc:**
    Necesitará el receptor IR USB Flirc, que se puede comprar en su sitio web: [https://flirc.tv/products/flirc-usb-receiver](https://flirc.tv/products/flirc-usb-receiver)

    El dispositivo Flirc debe programarse en una computadora de escritorio utilizando el software GUI de Flirc.

      * Conecte el Flirc a su computadora de escritorio y abra la GUI de Flirc.
      * Vaya a `Controllers` y seleccione `Full Keyboard`.
      * Programe las teclas necesarias para el script (por ejemplo, KEY_UP, KEY_DOWN, KEY_ENTER, etc.) haciendo clic en la tecla en la GUI y luego presionando el botón correspondiente en su control remoto físico.
      * Una vez programado, conecte el Flirc al **Diretta Host**.

2.  **Probar el dispositivo Flirc:**
    Verifique que la Raspberry Pi reconozca el Flirc como un teclado.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Seleccione el dispositivo "Flirc" del menú. Cuando presione los botones de su control remoto, debería ver los eventos de teclado impresos en la pantalla.

3.  Salte a la [Parte 2: Configuración del software del script de control](#parte-2-configuraci%C3%B3n-del-software-del-script-de-control)

---

#### **Opción 2: Configuración del control remoto IR Argon One**

1.  **Habilitar el hardware del receptor IR:**
    Debe habilitar la superposición (overlay) de hardware para el receptor IR de la carcasa Argon One.

      * Este comando agregará de forma segura la superposición de hardware requerida a su archivo `/boot/config.txt`, verificando primero para asegurarse de que no se agregue más de una vez.
        ```bash
        BOOT_CONFIG="/boot/config.txt"
        IR_CONFIG="dtoverlay=gpio-ir,gpio_pin=23"

        # Agregar la superposición de control remoto IR si aún no está allí
        if ! sed 's/#.*//' $BOOT_CONFIG | grep -q -F "$IR_CONFIG"; then
          echo "Habilitando el receptor IR Argon One..."
          sudo sed -i "/# Uncomment this to enable infrared communication./a $IR_CONFIG" /boot/config.txt
        else
          echo "Receptor IR Argon One ya habilitado."
        fi
        ```
      * Se requiere un reinicio para que el cambio de hardware surta efecto.
        ```bash
        sudo sync && sudo reboot
        ```

2.  **Instalar herramientas de IR y habilitar protocolos:**
    Instale `ir-keytable`
    ```bash
    sudo pacman -S --noconfirm v4l-utils
    ```

3.  **Capturar los códigos de escaneo (scancodes) de los botones:**
     Habilite todos los protocolos del kernel para que pueda decodificar las señales de su control remoto. Ejecute la herramienta de prueba para ver el código de escaneo único para cada botón del control remoto.
    ```bash
    sudo ir-keytable -p all
    sudo ir-keytable -t
    ```

    Presione cada botón que desee usar y anote su código de escaneo de la salida del evento `MSC_SCAN` (por ejemplo, `value ca`). Presione `Ctrl+C` cuando termine.

4.  **Crear el archivo de mapa de teclas (keymap):**
    Este archivo asigna los códigos de escaneo a nombres de teclas estándar.

      * Cree un nuevo archivo de mapa de teclas:
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
      * Si los códigos de escaneo en el archivo de ejemplo anterior no coinciden con los que registró, edite el archivo (`sudo nano /etc/rc_keymaps/argon.toml`) y cámbielos para que coincidan.

5.  **Crear un servicio `systemd` para cargar el mapa de teclas:**
    Este servicio cargará su mapa de teclas automáticamente al arrancar.

    Cree un nuevo archivo de servicio y habilite el servicio:
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

6.  **Probar el dispositivo de entrada:**
    Verifique que el sistema esté recibiendo eventos de teclado desde el control remoto IR.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Seleccione el dispositivo `gpio_ir_recv`. Cuando presione los botones en el control remoto, debería ver los eventos de tecla correspondientes.
    Presione `Ctrl+C` cuando haya terminado de probar.

---

### **Parte 2: Configuración del software del script de control**

*Después de configurar su hardware en la Parte 1, siga estos pasos para instalar y configurar el script de control de Python.*

### **Paso 1: Agregar `audiolinux` al grupo `input`**
Esto es necesario para que la cuenta `audiolinux` tenga acceso a los eventos del receptor del control remoto.
```bash
sudo usermod --append --groups input audiolinux
```
Cierre la sesión y vuelva a iniciarla para que este cambio surta efecto. Puede verificarlo con este comando:
```bash
echo ""
echo ""
echo "Comprobando sus membresías de grupo:"
echo "\$ groups"
groups
echo ""
echo "Arriba, debería ver:"
echo "audiolinux realtime video input audio wheel"
```

---

### **Paso 2: Instalar Python a través de `pyenv`**

Instale `pyenv` y la versión estable más reciente de Python.

```bash
# Instalar dependencias de compilación
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

# Instalar pyenv solo si aún no está instalado
if [ ! -d "$HOME/.pyenv" ]; then
  echo "--- Instalando pyenv ---"
  curl -fsSL https://pyenv.run | bash
else
  echo "--- pyenv ya está instalado. Omitiendo la instalación. ---"
fi

# Configurar la shell para pyenv
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

# Cargar el archivo para que pyenv esté disponible en la shell actual
. ~/.bashrc

# Instalar y establecer la versión de Python más reciente solo si aún no está instalada
PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')

if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
    # Obtener la memoria total en MB
    TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

    if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- La RAM física es de ${TOTAL_MEM}MB. Limitando a 1 núcleo para evitar bloqueos. ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
    else
        echo "--- La RAM física es de ${TOTAL_MEM}MB. Procediendo con la compilación paralela. ---"
    fi

    echo "--- Instalando Python ${PYVER}. Esto tardará varios minutos... ---"
    pyenv install "$PYVER"
    [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
else
    echo "--- Python ${PYVER} ya está instalado. ---"
fi

pyenv global "$PYVER"
```

**Nota:** Es normal que la parte `Installing Python-3.14.5...` tarde unos 10 minutos mientras compila Python desde el código fuente. ¡No se rinda! Siéntase libre de relajarse con hermosa música utilizando su nueva zona Diretta en Roon mientras espera. Debería estar disponible mientras Python se instala en el Host.

---

### **Paso 3: Descargar el repositorio del software `roon-ir-remote`**

Clone el repositorio del script y obtenga un parche para manejar correctamente los códigos de teclas por nombre en lugar de por número.

```bash
cd
# Clonar el repositorio si no existe, de lo contrario actualizarlo
if [ ! -d "roon-ir-remote" ]; then
  git clone https://github.com/dsnyder0pc/roon-ir-remote.git
else
  (cd roon-ir-remote && git pull)
fi
```

---

### **Paso 4: Crear el archivo de configuración del entorno de Roon**

Configure el script con sus detalles de Roon. **Nota:** Los códigos `event_mapping` deben coincidir con los nombres de teclas que definió en su configuración de hardware (`KEY_ENTER`, `KEY_VOLUMEUP`, etc.).

```bash
bash <<'EOF'
# --- Inicio del script ---

# Obtener la Zona de Roon y almacenarla en una variable
echo "Ingrese el nombre de su zona de Roon."
echo "IMPORTANTE: Esto debe coincidir exactamente con el nombre de la zona en la aplicación Roon (sensible a mayúsculas/minúsculas)."
# Esta línea es la corrección: < /dev/tty le indica a read que use la terminal
read -rp "Ingrese el nombre de su Zona de Roon: " MY_ROON_ZONE < /dev/tty

# Detectar si se necesita mapeo de Flirc/Teclado
if [ -f "/etc/systemd/system/ir-keymap.service" ]; then
    VOL_UP_CODE="KEY_VOLUMEUP"
    VOL_DOWN_CODE="KEY_VOLUMEDOWN"
    echo "--- Receptor IR estándar detectado. Usando KEY_VOLUMEUP/DOWN. ---"
else
    VOL_UP_CODE="KEY_UP"
    VOL_DOWN_CODE="KEY_DOWN"
    echo "--- Adaptador Flirc/HID detectado. Usando KEY_UP/DOWN para volumen. ---"
fi

# Asegurar que el directorio de destino exista
mkdir -p roon-ir-remote

# Crear el archivo de configuración utilizando un Here Document
# La variable ahora se sustituirá correctamente
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
echo "✅ Archivo de configuración 'roon-ir-remote/app_info.json' creado con éxito."

# --- Fin del script ---
EOF
```

---

### **Paso 5: Preparar y probar `roon-ir-remote`**

Instale las dependencias del script en un entorno virtual y ejecútelo por primera vez.

```bash
cd ~/roon-ir-remote
# Crear el entorno virtual solo si aún no existe
if ! pyenv versions --bare | grep -q "^roon-ir-remote$"; then
  echo "--- Creando el entorno virtual 'roon-ir-remote' ---"
  pyenv virtualenv roon-ir-remote
else
  echo "--- El entorno virtual 'roon-ir-remote' ya existe ---"
fi
pyenv activate roon-ir-remote
pip3 install --upgrade pip
pip3 install -r requirements.txt

python roon_remote.py
```

La primera vez que ejecute el script, debe **autorizar la extensión en Roon** yendo a `Settings` -> `Extensions`.

Con la música reproduciéndose en su nueva zona Diretta Roon, apunte su control remoto IR directamente a la computadora Diretta Host y presione el botón de Reproducir/Pausa (puede ser el botón central en el controlador de 5 direcciones). Pruebe también Siguiente y Anterior. Si no funcionan, compruebe su ventana de terminal en busca de mensajes de error. Una vez que haya terminado de probar, presione `CTRL-C` para salir.

---

### **Paso 6: Crear un servicio de `systemd`**

Cree un servicio para ejecutar el script automáticamente en segundo plano.

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

# Habilitar e iniciar el servicio
sudo systemctl daemon-reload
sudo systemctl enable --now roon-ir-remote.service

# Comprobar el estado
sudo systemctl status roon-ir-remote.service
```

---

### **Paso 7: Observar los registros por un momento:**
```bash
journalctl -b -u roon-ir-remote.service -f
```

Presione `CTRL-C` una vez que esté satisfecho de que las cosas funcionan como se esperaba.

---

### **Paso 8: Instalar el script `set-roon-zone`**
Es bueno tener un script que pueda usar para actualizar el nombre de la zona de Roon más adelante si es necesario. A continuación se explica cómo instalarlo:
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone
sudo install -m 0755 set-roon-zone /usr/local/bin/
rm set-roon-zone
```

Para usarlo, simplemente inicie sesión en la computadora Diretta Host y escriba:
```bash
set-roon-zone
```
Siga las instrucciones para ingresar el nuevo nombre de su Zona de Roon. Es posible que deba ingresar la contraseña de root para que los cambios surtan efecto.

**Nota: Una mejor manera de configurar la zona**
Aunque este script funciona perfectamente, el método recomendado para cambiar la Zona de Roon es utilizar la aplicación web AnCaolas Link System Control, que se detalla en el [Apéndice 4](#13-ap%C3%A9ndice-4-interfaz-web-de-control-del-sistema-opcional). La interfaz web proporciona una página dedicada para ver y editar el nombre de la zona desde su teléfono o navegador.

### **Paso 9: ¡Disfrutar! 📈**

> ---
> ### ✅ Punto de control: Verificar su configuración del control remoto IR
>
> El hardware y el software de su control remoto IR ahora deberían estar configurados. Para verificar la configuración, proceda al [**Apéndice 5**](#14-ap%C3%A9ndice-5-comprobaciones-de-estado-del-sistema) y ejecute el comando universal **System Health Check** (Comprobación de estado del sistema) en el Diretta Host.
>
> ---

Su control remoto IR ahora debería controlar Roon. ¡Disfrute!

---

## 12. Apéndice 3: Modo purista opcional
Hay una actividad de red y de fondo mínima en la computadora Diretta Target que no está relacionada con la reproducción de música utilizando el protocolo Diretta. Sin embargo, algunos usuarios prefieren tomar medidas adicionales para reducir la posibilidad de dicha actividad. Ya estamos en el extremo del rendimiento de audio, así que ¿por qué no?

---
> ADVERTENCIA CRÍTICA: Solo para el Diretta Target
>
> El script `purist-mode` y todas las instrucciones de este apéndice están diseñados exclusivamente para el Diretta Target.
>
> NO instale ni ejecute este script en el Diretta Host. Hacerlo interrumpirá la conexión del Host a su red principal, dejándolo inaccesible e incapaz de comunicarse con su Roon Core o servicios de transmisión. Esto dejaría inoperable todo el sistema hasta que pueda obtener acceso a la consola (con un teclado físico y un monitor) para revertir los cambios.
---

### Paso 1: Instalar el script `purist-mode` **(solo en la computadora Diretta Target)**
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode
sudo install -m 0755 purist-mode /usr/local/bin
rm purist-mode

# Script para mostrar el estado del Modo Purista al iniciar sesión
cat <<'EOT' | sudo tee /etc/profile.d/purist-status.sh
#!/bin/sh
BACKUP_FILE="/etc/nsswitch.conf.purist-bak"

if [ -f "$BACKUP_FILE" ]; then
    echo -e '\n\e[1;32m✅ El Modo Purista está ACTIVO.\e[0m Sistema optimizado para la máxima calidad de sonido.'
else
    echo -e '\n\e[1;33m⚠️ PRECAUCIÓN: El Modo Purista está DESHABILITADO.\e[0m La actividad de fondo puede afectar la calidad del sonido.'
fi
EOT
```

Para ejecutarlo, simplemente inicie sesión en el Diretta Target y escriba `purist-mode`:
```bash
purist-mode
```

Por ejemplo:
```text
[audiolinux@diretta-target ~]$ purist-mode
Este script requiere privilegios de sudo. Es posible que se le solicite una contraseña.
🚀 Activando el Modo Purista...
  -> Deteniendo el servicio de sincronización de tiempo (chronyd)...
  -> Deshabilitando las búsquedas de DNS...
  -> Anulando la puerta de enlace con una ruta de agujero negro (blackhole) de alta prioridad...

✅ El Modo Purista está ACTIVO.
```

Escuche durante un rato para ver si prefiere el sonido (o la tranquilidad).

---

### Step 2: Enable Purist Mode by Default

Si ha decidido que prefiere el sonido con el Modo Purista habilitado, hágalo el valor predeterminado después de cada reinicio.

```bash
echo ""
echo "- Deshabilitando el Modo Purista para asegurar un estado limpio"
purist-mode --revert

echo ""
echo "- Creando el servicio para revertir al Modo Estándar en cada arranque"
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
echo "- Creando el servicio de autoactivación retrasada"
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
echo "- Habilitando los nuevos servicios"
sudo systemctl daemon-reload
sudo systemctl enable purist-mode-revert-on-boot.service
sudo systemctl enable purist-mode-auto.service
```

---

### Step 3: Install a wrapper around the `menu` command
Muchas funciones en AudioLinux requieren acceso a Internet. Para que todo funcione como se espera, agregue un wrapper alrededor del comando `menu` que deshabilite el modo Purista mientras utiliza el menú, y lo habilite de nuevo al salir a la terminal.

```bash
if grep -q menu_wrapper ~/.bashrc; then
  :
else
  echo ""
  echo "Agregando un wrapper alrededor del comando menu"
  cat <<'EOT' | tee -a ~/.bashrc

# Wrapper personalizado para el menú de AudioLinux para gestionar el Modo Purista
menu_wrapper() {
  local was_active=false
  # Comprobar el estado inicial del Modo Purista buscando el archivo de respaldo.
  if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
    was_active=true
  fi

  # Si el Modo Purista estaba activo, revertirlo temporalmente para el menú.
  if [ "$was_active" = true ]; then
    echo "Comprobando credenciales para gestionar el Modo Purista..."
    sudo -v

    echo "Deshabilitando temporalmente el Modo Purista para ejecutar el menú..."
    purist-mode --revert > /dev/null 2>&1 # Revert quietly
  fi

  # Llamar al comando menu original
  /usr/bin/menu

  # Si el Modo Purista estaba activo antes, volver a habilitarlo ahora.
  if [ "$was_active" = true ]; then
    echo "Reactivando el Modo Purista..."
    purist-mode > /dev/null 2>&1 # Activate quietly
    echo "El Modo Purista está activo de nuevo."
  fi
}

# Crear un alias del comando 'menu' a nuestra nueva función wrapper
alias menu='menu_wrapper'
# Alias para gestionar el servicio automático de Modo Purista
alias purist-mode-auto-enable='echo "Habilitando el Modo Purista en el arranque..."; purist-mode; sudo systemctl enable purist-mode-auto.service'
alias purist-mode-auto-disable='echo "Deshabilitando el Modo Purista en el arranque..."; purist-mode --revert; sudo systemctl disable --now purist-mode-auto.service'
EOT
fi

source ~/.bashrc
```

---

### Understanding the Purist Mode States

El sistema del Modo Purista está diseñado para ser flexible, lo que le permite controlarlo manualmente o hacer que se active automáticamente después de que arranque el sistema. Funciona en dos estados principales:

  * **Deshabilitado (Modo Estándar):**
    Este es el estado normal y completamente funcional del Diretta Target. La puerta de enlace de red está activa, todos los servicios (`chronyd`, `argononed`) se están ejecutando y el dispositivo funciona sin restricciones.

  * **Activo (Modo Purista):**
    Este es el estado optimizado para escuchas críticas. Se cae la puerta de enlace de red para evitar el tráfico de Internet, y se detienen los servicios de fondo no esenciales (incluido el ventilador de la carcasa Argon ONE) para minimizar cualquier posible interferencia en el sistema.

Estos estados se gestionan de dos maneras: **automáticamente** en el arranque y **manualmente** a través de la línea de comandos.

#### Automatic Control (On Boot)

El proceso de arranque está diseñado para ser seguro y predecible, con un cambio automatizado opcional al Modo Purista.

1.  **Reversión obligatoria en el arranque:** Independientemente del estado en el que se encontrara al apagarse, el Diretta Target **siempre** arranca primero en **Modo Estándar**. Esta es una característica crítica que garantiza que los servicios esenciales, como la sincronización de la hora de la red, puedan ejecutarse correctamente.

2.  **Autoactivación opcional:** Si ha habilitado la función automática, el sistema esperará 60 segundos después del arranque y luego cambiará automáticamente al **Modo Purista**. Esto proporciona una experiencia de "configurar y olvidar" para los usuarios que siempre prefieren escuchar en el estado optimizado.

#### Manual Control (Interactive Use)

Tiene control interactivo completo sobre el sistema en cualquier momento.

  * Para **activar manualmente** el Modo Purista para una sesión de escucha, inicie sesión en la computadora Diretta Target y ejecute:

    ```bash
    purist-mode
    ```

  * Para **deshabilitar manualmente** el Modo Purista y volver a la operación estándar, ejecute:

    ```bash
    purist-mode --revert
    ```

  * Para controlar el **comportamiento de arranque automático**, utilice los alias de conveniencia en el Diretta Target:

    ```bash
    # Esto habilita la autoactivación de 60 segundos en el próximo arranque
    purist-mode-auto-enable

    # Esto deshabilita la autoactivación en el próximo arranque
    purist-mode-auto-disable
    ```

---

## 13. Apéndice 4: Interfaz web de control del sistema opcional

Este apéndice proporciona instrucciones para instalar una aplicación web sencilla en el Diretta Host. Esta aplicación ofrece una interfaz fácil de usar, accesible desde un teléfono o tableta, para gestionar las funciones clave de su sistema Diretta, incluyendo el Modo Purista en el Target y la configuración de integración del control remoto IR de Roon en el Host.

> **ADVERTENCIA CRÍTICA: Realice estos pasos con cuidado.**
> Esta configuración implica la creación de un nuevo usuario y la modificación de la configuración de seguridad. Siga las instrucciones con precisión para garantizar que el sistema siga siendo seguro y funcional.

La configuración se divide en dos partes: primero, configuramos el **Diretta Target** para aceptar comandos de forma segura, y segundo, instalamos la aplicación web en el **Diretta Host**. Sin embargo, preste atención porque cambiamos de host con frecuencia.

---

### **Parte 1: Configuración del Diretta Target**

En el **Diretta Target**, crearemos un nuevo usuario con permisos muy limitados. A este usuario solo se le permitirá ejecutar los comandos específicos necesarios para gestionar el Modo Purista.

1.  **Conectarse por SSH al Diretta Target:**
    ```bash
    ssh diretta-target
    ```

2.  **Crear un nuevo usuario para la aplicación:**
    Este comando crea un nuevo usuario llamado `purist-app` y su directorio de inicio. Se requiere una shell válida para que los comandos SSH no interactivos funcionen.
    ```bash
    sudo useradd --create-home --shell /bin/bash purist-app
    ```

3.  **Crear scripts de comandos seguros:**
    Crearemos cuatro pequeños scripts dedicados que son las *únicas* acciones que la aplicación web tiene permitido realizar. Este es un paso de seguridad crítico.
    ```bash
    # Script para obtener el estado actual, incluido el estado de la licencia
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

    # Check the validated boot cache for an active evaluation link
    if [ ! -f /tmp/diretta_license_url.cache ] || grep -q "http" /tmp/diretta_license_url.cache; then
      LICENSE_LIMITED="true"
    fi

    # Output all status flags as a single JSON object
    echo "{\"purist_mode_active\": $IS_ACTIVE, \"auto_start_enabled\": $IS_AUTO_ENABLED, \"license_needs_activation\": $LICENSE_LIMITED}"
    EOT

    # Script para alternar el Modo Purista
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-mode
    #!/bin/bash
    if [[ "$1" == "--enforce" ]]; then
        # Absolute enforcement: If it's supposed to be active, re-run
        # the baseline script to clean up any resurrected default routes.
        if [ -f "/etc/nsswitch.conf.purist-bak" ]; then
            /usr/local/bin/purist-mode
        fi
    elif [ -f "/etc/nsswitch.conf.purist-bak" ]; then
        /usr/local/bin/purist-mode --revert
    else
        /usr/local/bin/purist-mode
    fi
    EOT

    # Script para alternar el servicio de arranque automático
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-auto
    #!/bin/bash
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      systemctl disable --now purist-mode-auto.service
    else
      systemctl enable purist-mode-auto.service
    fi
    EOT

    # Crear el script para reiniciar el servicio Diretta
    cat <<'EOT' | sudo tee /usr/local/bin/pm-restart-target
    #!/bin/bash
    # Restarts the Diretta ALSA Target service.
    # This script is intended to be called via sudo by the purist-app user.
    /usr/bin/systemctl restart diretta_alsa_target.service
    EOT

    # Crear el script para obtener la URL de la licencia de Diretta
    cat <<'EOT' | sudo tee /usr/local/bin/pm-get-license-url
    #!/bin/bash

    # La única función de este script es leer el archivo de caché creado en el arranque.
    readonly CACHE_FILE="/tmp/diretta_license_url.cache"

    if [ -s "$CACHE_FILE" ]; then
        # Si la caché existe y tiene contenido, mostrarlo.
        cat "$CACHE_FILE"
    else
        # Si no, imprimir un error útil en stderr y salir.
        echo "Error: La caché de la licencia no se encontró o está vacía." >&2
        exit 1
    fi
    EOT

    # Crear script para establecer la velocidad del enlace
    cat <<'EOT' | sudo tee /usr/local/bin/pm-set-link
    #!/bin/bash
    # Script de perfil para hacer cumplir los límites de enlace físico del Target
    # Refactorizado usando máscaras de publicidad explícitas para evitar bloqueos de hardware

    SPEED="$1"

    if [ "$SPEED" = "10" ]; then
        echo "Programando limitación de 10 Mbps (Super Purista)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x002" >/dev/null 2>&1 < /dev/null &
    elif [ "$SPEED" = "100" ]; then
        echo "Programando limitación de 100 Mbps (Purista)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x008" >/dev/null 2>&1 < /dev/null &
    elif [ "$SPEED" = "1000" ]; then
        echo "Liberando limitaciones. Restaurando el portafolio completo 10/100/1000 (Estándar)..."
        /usr/bin/sh -c "sleep 1 && sudo /usr/bin/ethtool -s end0 advertise 0x03f" >/dev/null 2>&1 < /dev/null &
    else
        echo "Uso: $0 [10|100|1000]"
        exit 1
    fi
    EOT

    # Hacer ejecutables los nuevos scripts
    sudo chmod -v +x /usr/local/bin/pm-*
    ```

4.  **Otorgar permisos de Sudo:**
    Este paso permite al usuario `purist-app` ejecutar nuestros cuatro nuevos scripts con privilegios de root y sin necesidad de una terminal interactiva.
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
    purist-app ALL=(ALL) NOPASSWD: /usr/local/bin/pm-set-link
    EOT
    ```

5.  **Rellenar el archivo de caché de la licencia de Diretta en el arranque**
    Obtener la URL de la licencia de Diretta requiere una conexión a Internet. Si tenemos el Modo Purista habilitado de forma predeterminada, el Target nunca podrá obtener la URL. Sin embargo, en el momento del arranque, tenemos el Modo Purista deshabilitado durante 60 segundos para poder configurar el reloj y comprobar la activación de la licencia de Diretta. También podemos utilizar esa ventana de tiempo para obtener la URL.
    ```bash
    # Descargar el script, establecer los permisos correctos y colocarlo en la ruta del sistema
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh
    sudo install -m 0755 create-diretta-cache.sh /usr/local/bin/
    rm create-diretta-cache.sh

    # Crear un servicio para rellenar la caché del estado de la licencia
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta-cache.service
    [Unit]
    Description=Asynchronous Diretta License Cache Collector
    After=network.target purist-mode-revert-on-boot.service
    Before=purist-mode-auto.service

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    # Block execution cleanly here until the Host replies to a ping
    TimeoutStartSec=infinity
    ExecStartPre=/bin/bash -c "until ping -c 1 -q 172.20.0.1 &>/dev/null; do sleep 2; done"
    ExecStart=/usr/local/bin/create-diretta-cache.sh
    Restart=no

    [Install]
    WantedBy=multi-user.target
    EOT

    # Recargar systemd para aplicar la configuración incorporada (drop-in) actualizada
    sudo rm -rf /etc/systemd/system/purist-mode-revert-on-boot.service.d
    sudo systemctl daemon-reload
    sudo systemctl enable diretta-cache.service

    # Ejecutar el script manualmente una vez
    sudo /usr/local/bin/create-diretta-cache.sh
    ls -l /tmp/diretta_license_url.cache
    ```

---

### **Parte 2: Configuración del Diretta Host**

Ahora, en el **Diretta Host**, realizaremos todos los pasos para instalar y configurar la aplicación web. Debe iniciar sesión como el usuario `audiolinux` para toda esta sección.

1.  **Conectarse por SSH al Diretta Host:**
    ```bash
    ssh diretta-host
    ```

2.  **Generar una clave SSH dedicada:**
    Esto crea un nuevo par de claves SSH específicamente para la aplicación web. No tendrá frase de contraseña.
    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/purist_app_key -N "" -C "purist-app-key"
    ```

3.  **Configurar SSH y copiar la clave al Target:**
    Este paso creará una configuración de SSH y copiará de forma segura la clave pública al Target.
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

    # Copiar la clave pública al directorio de inicio del Target
    echo "--> Copiando la clave pública al Target..."
    scp -o StrictHostKeyChecking=accept-new ~/.ssh/purist_app_key.pub diretta-target:
    ```

4.  **Autorizar la clave en el Target:**
    ```bash
    ssh diretta-target

    ```

    Una vez que haya iniciado sesión en el Target, ejecute este script para configurar la clave para el usuario 'purist-app'.
    ```bash
    echo "--> Ejecutando el script de configuración en el Target..."
    set -e
    # Leer la clave pública del archivo que acabamos de copiar
    PUB_KEY=$(cat purist_app_key.pub)

    # Asegurar que el directorio .ssh exista y tenga los permisos correctos
    sudo mkdir -p /home/purist-app/.ssh
    sudo chmod 0700 /home/purist-app/.ssh

    # Crear el archivo authorized_keys con las restricciones de seguridad requeridas
    echo "command=\"sudo \$SSH_ORIGINAL_COMMAND\",from=\"172.20.0.1\",no-port-forwarding,no-x11-forwarding,no-agent-forwarding,no-pty ${PUB_KEY}" | sudo tee /home/purist-app/.ssh/authorized_keys > /dev/null

    # Establecer los propietarios y permisos finales
    sudo chown -R purist-app:purist-app /home/purist-app/.ssh
    sudo chmod 0600 /home/purist-app/.ssh/authorized_keys

    # Limpiar el archivo de clave pública copiado
    rm purist_app_key.pub

    echo "✅ La clave SSH se ha autorizado correctamente en el Target."
    ```

5.  **Probar manualmente los comandos remotos (Recomendado):**
    Antes de iniciar la aplicación web, pruebe los comandos remotos de solo lectura desde la terminal del **Diretta Host** para confirmar que el backend funciona.
    ```bash
    # Probar el comando de estado (debería devolver una cadena JSON)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-status'

    # Probar el comando para obtener el estado de la licencia.
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-license-url'
    ```

6.  **Instalar Python a través de pyenv** en el **Diretta Host** (siéntase libre de omitir este paso si ya lo hizo para que el control remoto IR funcione)
    Instale `pyenv` y la versión estable más reciente de Python.
    ```bash
    # Instalar dependencias de compilación
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

    # Instalar pyenv solo si aún no está instalado
    if [ ! -d "$HOME/.pyenv" ]; then
      echo "--- Instalando pyenv ---"
      curl -fsSL https://pyenv.run | bash
    else
      echo "--- pyenv ya está instalado. Omitiendo la instalación. ---"
    fi

    # Configurar la shell para pyenv
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

    # Cargar el archivo para que pyenv esté disponible en la shell actual
    . ~/.bashrc

    # Instalar y establecer la versión de Python más reciente solo si aún no está instalada
    PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
    if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
      # Obtener la memoria total en MB
      TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

      if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- La RAM física es de ${TOTAL_MEM}MB. Limitando a 1 núcleo para evitar bloqueos. ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
      else
        echo "--- La RAM física es de ${TOTAL_MEM}MB. Procediendo con la compilación paralela. ---"
      fi

      echo "--- Instalando Python ${PYVER}. Esto tardará varios minutos... ---"
      pyenv install $PYVER
      [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
    else
      echo "--- Python ${PYVER} ya está instalado. ---"
    fi

    pyenv global $PYVER
    ```

    **Nota:** Es normal que la parte `Installing Python-3.14.5...` tarde unos 10 minutos mientras compila Python desde el código fuente. ¡No se rinda! Siéntase libre de relajarse con hermosa música utilizando su nueva zona Diretta en Roon mientras espera. Debería estar disponible mientras Python se instala en el Host.

7.  **Instalar Avahi y las dependencias de Python en el Diretta Host:**

    **Nota:** OPCIONAL - Si tiene más de un Diretta Host en su red, asegúrese de que tengan nombres únicos. Puede utilizar un comando como el siguiente para cambiar el nombre de este antes de continuar:

    ```bash
    # Opcionalmente, cambiar el nombre del Diretta Host si esta es su segunda construcción en la misma red
    sudo hostnamectl set-hostname diretta-host2
    ```

    Este paso se ejecuta en el **Diretta Host**. Instala el demonio Avahi y utiliza un archivo `requirements.txt` para instalar Flask en un entorno virtual dedicado.
    ```bash
    # Instalar Avahi para la resolución de nombres .local
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm avahi

    # Encontrar dinámicamente el nombre de la interfaz Ethernet USB (por ejemplo, enp... o enu1...)
    USB_INTERFACE=$(ip -o link show | awk -F': ' '/en[pu]/{print $2}')

    # Crear una anulación de configuración para Avahi para aislarlo a la interfaz USB
    echo "--- Configurando Avahi para usar la interfaz: $USB_INTERFACE ---"
    sudo mkdir -p /etc/avahi/avahi-daemon.conf.d
    cat <<EOT | sudo tee /etc/avahi/avahi-daemon.conf.d/interface-scoping.conf
    [server]
    allow-interfaces=$USB_INTERFACE
    deny-interfaces=end0
    EOT

    # Habilitar e iniciar el demonio Avahi
    sudo systemctl enable --now avahi-daemon.service

    # Crear el directorio de la aplicación y el archivo de requisitos
    mkdir -p ~/purist-mode-webui
    echo "Flask" > ~/purist-mode-webui/requirements.txt

    # Crear un entorno virtual e instalar dependencias
    echo "--- Configurando el entorno de Python para la interfaz web (Web UI) ---"
    # Crear el entorno virtual solo si aún no existe
    if ! pyenv versions --bare | grep -q "^purist-webui$"; then
      echo "--- Creando el entorno virtual 'purist-webui' ---"
      pyenv virtualenv purist-webui
    else
      echo "--- El entorno virtual 'purist-webui' ya existe ---"
    fi
    pyenv activate purist-webui
    pip install -r ~/purist-mode-webui/requirements.txt
    pyenv deactivate
    ```

8.  **Instalar la aplicación Flask:**
    Descargue el script de Python directamente desde GitHub en el directorio de la aplicación en el **Diretta Host**.
    ```bash
    curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py -o ~/purist-mode-webui/app.py
    ```

9. **Otorgar capacidad de binding (vinculación) de puertos**
    Necesitamos otorgarle al ejecutable de Python permiso para realizar el binding en el puerto 80 del Diretta Host para que nuestra aplicación web pueda iniciarse.
    ```bash
    # Instalar el paquete que proporciona el comando 'setcap'
    sudo pacman -S --noconfirm --needed libcap

    # Encontrar la ruta real al ejecutable de Python, resolviendo todos los enlaces simbólicos
    PYTHON_EXEC=$(readlink -f /home/audiolinux/.pyenv/versions/purist-webui/bin/python)

    # Otorgar la capacidad de binding de puertos directamente al ejecutable de Python final
    echo "Aplicando capacidad al archivo real: ${PYTHON_EXEC}"
    sudo setcap 'cap_net_bind_service=+ep' "$PYTHON_EXEC"
    ```

10. **Otorgar permisos de Sudo en el Host:**
    Este paso es crítico para permitir que la aplicación web reinicie los servicios relacionados con Roon necesarios sin contraseña.
    ```bash
    cat <<'EOT' | sudo tee /etc/sudoers.d/webui-restarts
    # Allow the webui (running as audiolinux) to enforce host profiles and restart services
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl daemon-reload
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roon-ir-remote.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart roonbridge.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart diretta_alsa.service
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/ethtool -s end0 *
    audiolinux ALL=(ALL) NOPASSWD: /usr/bin/mv /tmp/setting.inf.tmp /opt/diretta-alsa/setting.inf
    EOT
    sudo chmod 0440 /etc/sudoers.d/webui-restarts
    ```

11. **Probar la aplicación Flask de forma interactiva:**
    Ahora, ejecute la aplicación desde la línea de comandos en el **Diretta Host** para asegurarse de que se inicie correctamente.
    ```bash
    cd ~/purist-mode-webui
    pyenv activate purist-webui
    python app.py
    ```
    Debería ver una salida que indica que el servidor Flask se ha iniciado en el puerto **8080**. Desde otro dispositivo, acceda a [http://diretta-host.local:8080](http://diretta-host.local:8080). Si funciona, regrese a la terminal SSH y presione `Ctrl+C` para detener el servidor.

12. **Crear el servicio `systemd`:**
    Este servicio ejecutará la aplicación web automáticamente en el **Diretta Host**, utilizando el ejecutable de Python correcto de nuestro entorno virtual `pyenv`.
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

13. **Habilitar e iniciar la aplicación web:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl stop purist-webui.service
    sudo systemctl enable --now purist-webui.service
    ```

14. **Observar los registros por un momento:**
    ```bash
    journalctl -b -u purist-webui.service -f
    ```

15. **Probar la interfaz web con la URL final:**
    Open a browser to [http://diretta-host.local](http://diretta-host.local) y observe los registros en busca de errores.

Presione `CTRL-C` una vez que esté satisfecho de que las cosas funcionan como se esperaba.

---

### **Acceso a la interfaz web (Web UI)**

¡Todo listo! Abra un navegador web en su teléfono, taebleta o computadora conectada a la misma red que el Diretta Host. Navegue a la página de inicio principal:

[http://diretta-host.local](http://diretta-host.local)

---
> **Una nota sobre las advertencias de seguridad del navegador**
> Cuando visite http://diretta-host.local por primera vez, es probable que su navegador muestre una advertencia de seguridad indicando que la conexión no es segura. Esto es de esperar y es seguro de omitir. La advertencia aparece porque la conexión utiliza `HTTP` estándar en lugar de `HTTPS` cifrado, una elección intencional para minimizar la sobrecarga de procesamiento en el dispositivo de audio. Debido a que la aplicación se ejecuta solo en su red doméstica privada y no maneja datos confidenciales, puede hacer clic con confianza en "Continuar al sitio".
---

Desde la página de inicio, una barra de navegación en la parte superior le guiará a los diferentes paneles de control:

* **Home:** La página de inicio principal con enlaces a las diferentes aplicaciones.

* **Purist Mode App:** Esta página contiene los controles para alternar el Modo Purista y su comportamiento de inicio automático en el Diretta Target. Se actualiza automáticamente cada 30 segundos para mostrar el estado actual. También contiene el botón "Restart Services" (Reiniciar servicios) para usar después de la activación de una licencia de Diretta.

* **IR Remote App:** Si ha completado la configuración del control remoto IR (Apéndice 2), aparecerá este enlace. Esta página proporciona un formulario simple para ver y actualizar el nombre de la Zona de Roon que controlará su control remoto. Esta página no se actualiza automáticamente, por lo que puede tomarse todo el tiempo que necesite para realizar sus ediciones.

### 🔗 Nota sobre la funcionalidad completa de la interfaz web (Web UI)

Para desbloquear todas las capacidades de la interfaz web de control del sistema (Web UI), específicamente los ajustes de **Link Speed** (Velocidad de enlace) de red y el interruptor **Super Purist** (Súper Purista), también debe completar las configuraciones de hardware y servicios detalladas en el [**Apéndice 8: Velocidades de red puristas opcionales**](#17-ap%C3%A9ndice-8-velocidades-de-red-puristas-opcionales)[cite: 1]. La interfaz web depende directamente de los scripts, flags y servicios subyacentes establecidos en esa sección para modificar y hacer cumplir con éxito los límites físicos de velocidad de enlace en su conexión de punto a punto[cite: 1].

> ---
> ### ✅ Punto de control: Verificar la configuración de la interfaz web (Web UI)
>
> La interfaz web del Modo Purista ahora debería estar operativa. Para verificar todos los componentes de esta función compleja, proceda al [**Apéndice 5**](#14-ap%C3%A9ndice-5-comprobaciones-de-estado-del-sistema) y ejecute el comando universal **System Health Check** (Comprobación de estado del sistema) tanto en el Host como en el Target.
>
> ---

## 14. Apéndice 5: Comprobaciones de estado del sistema

Después de completar las secciones principales de esta guía, es una buena idea realizar una verificación rápida de control de calidad (QA) para verificar que todo esté configurado correctamente.

Hemos creado un script inteligente que detecta automáticamente si lo está ejecutando en el **Diretta Host** o en el **Diretta Target** y realiza el conjunto de verificaciones correspondiente.

### **Cómo ejecutar la comprobación**

En el Host o en el Target, ejecute el siguiente comando único. Descargará y ejecutará el script de QA, proporcionando un informe detallado del estado de su sistema.

```bash
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh | sudo bash
```

---

## 15. Apéndice 6: Ajuste de rendimiento en tiempo real opcional

Los siguientes pasos son opcionales pero recomendados para los usuarios que buscan extraer el máximo rendimiento absoluto de su configuración de Diretta. La estrategia, basada en el consejo del autor de AudioLinux, Piero, consiste en crear el entorno más estable y eléctricamente silencioso posible tanto en el dispositivo Host como en el Target.

Esto se logra mediante el uso de **aislamiento de CPU** para dedicar núcleos de procesador específicos a tareas de audio, protegiéndolos del sistema operativo, y ajustando cuidadosamente las **prioridades en tiempo real** para garantizar que la ruta de datos de audio nunca se interrumpa.

> **Nota:** Este es un proceso de ajuste avanzado. Asegúrese de que su sistema base Diretta sea completamente funcional completando las secciones 1 a 9 de la guía principal antes de continuar. Es esencial una refrigeración adecuada para ambos dispositivos Raspberry Pi.

---

### **Parte 1: Optimización del Diretta Target**

El objetivo para el Target es convertirlo en un punto final de audio puro y de baja latencia. Aislaremos la aplicación Diretta en un núcleo de CPU único y dedicado y le asignaremos una prioridad en tiempo real alta, pero no excesiva.

#### **Paso 6.1: Aislar un núcleo de CPU para la aplicación de audio**

Este paso dedica un núcleo de CPU exclusivamente a la aplicación Diretta Target.

1.  Conéctese por SSH al Diretta Target:
    ```bash
    ssh diretta-target
    ```
2.  Ingrese al sistema de menús de AudioLinux:
    ```bash
    menu
    ```
3.  Navegue al menú **ISOLATED CPU CORES configuration** (bajo **SYSTEM menu**).

4.  Confirme que los núcleos aislados estén deshabilitados. Si no es así, utilice la opción 3 para deshabilitarlos:
    ```text
    ISOLATED CORES CONFIGURATION
    Esta opción dividirá los núcleos de la CPU en 2 o más conjuntos: uno para servicios de audio, otro para procesos del sistema
    Después puede especificar el conjunto de núcleos de CPU utilizado por cada servicio de audio
    También puede asignar IRQ de audio o de red a núcleos específicos

    Los núcleos aislados están deshabilitados

    Por favor, elija su opción:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    ```

5.  Navegue de nuevo al menú **ISOLATED CPU CORES configuration** (bajo **SYSTEM menu**). Siga las instrucciones exactamente como se muestra a continuación para aislar los **núcleos 2 y 3** y asignarle la aplicación Diretta.
    ```text
    Please chose your option:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    1

    ¿Cuántos grupos desea crear? (1 o más)
    ?1
    Por favor, escriba los núcleos del grupo 1:
    ?2,3

    Escriba el servicio que debe confinarse al grupo 1...
    ?diretta_alsa_target

    Por favor, escriba la dirección (número iSerial) de su(s) tarjeta(s)...
    ?end0
    ```

6.  Una vez finalizado el proceso, salga de nuevo a la terminal.

> **Una nota sobre la afinidad automática de IRQ:** Es posible que note que el script reporta que también ha aislado las IRQ de red `end0` en el mismo núcleo. Esto no es un error, sino una optimización inteligente. El script asocia automáticamente las interrupciones de red al mismo núcleo que la aplicación que utiliza la red, creando la ruta de datos más eficiente posible.

#### **Paso 6.2: Deshabilitar el temporizador heredado `rtapp`**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **Paso 6.3: Reiniciar para aplicar los cambios.**
```bash
sudo sync && sudo reboot
```

---

### **Parte 2: Optimización del Diretta Host**

El objetivo para el Host es dar a los hilos de servicio de Diretta recursos de procesamiento dedicados, pero sin utilizar prioridades altas en tiempo real. El aislamiento de la CPU es una herramienta más potente aquí, ya que evita que los procesos se interrumpan en primer lugar.

#### **Paso 6.4: Aislar núcleos de CPU para aplicaciones de audio**

Este paso dedica dos núcleos de CPU para manejar los hilos de servicio del Diretta Host.

1.  Conéctese por SSH al Diretta Host:
    ```bash
    ssh diretta-host
    ```
2.  Ingrese al sistema de menús de AudioLinux:
    ```bash
    menu
    ```
3.  Navegue al menú **ISOLATED CPU CORES configuration** (bajo **SYSTEM menu**).

4.  Confirme que los núcleos aislados estén deshabilitados. Si no es así, utilice la opción 3 para deshabilitarlos:
    ```text
    ISOLATED CORES CONFIGURATION
    Esta opción dividirá los núcleos de la CPU en 2 o más conjuntos: uno para servicios de audio, otro para procesos del sistema
    Después puede especificar el conjunto de núcleos de CPU utilizado por cada servicio de audio
    También puede asignar IRQ de audio o de red a núcleos específicos

    Los núcleos aislados están deshabilitados

    Por favor, elija su opción:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    ```

5.  Navegue de nuevo al menú **ISOLATED CPU CORES configuration** (bajo **SYSTEM menu**). Siga las instrucciones para aislar los **núcleos 2 y 3** y asignarlos a Diretta ALSA.
    ```text
    Please chose your option:
    1) Configure and enable
    2) Edit configuration (for experts)
    3) Enable/disable (keep configuration)
    4) Exit
    ?
    1

    ¿Cuántos grupos desea crear? (1 o más)
    ?1
    Por favor, escriba los núcleos del grupo 1:
    ?2,3

    Escriba el servicio que debe confinarse al grupo 1...
    ?diretta_alsa

    Por favor, escriba la dirección (número iSerial) de su(s) tarjeta(s)...
    ?end0
    ```

6.  Una vez finalizado el proceso, salga de nuevo a la terminal.

---

#### **Paso 6.5: Deshabilitar el temporizador heredado `rtapp`**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **Paso 6.6: Reiniciar para aplicar los cambios.**
```bash
sudo sync && sudo reboot
```

## 16. Apéndice 7: Optimizaciones de IRQ e hilos opcionales

### Parte 1: Aislamiento de la ruta USB en el Diretta Target
Por defecto, incluso cuando los núcleos de la CPU están aislados, las interrupciones USB aún pueden competir por los recursos en los núcleos "ruidosos" del sistema (0 y 1). Este script identifica dinámicamente el controlador USB específico al que está conectado su DAC y asocia sus interrupciones de hardware a sus núcleos de audio aislados (2 y 3). En la Raspberry Pi 5, los controladores USB son administrados por el chip RP1, lo que nos permite dirigir las interrupciones de hardware a núcleos específicos.

**Nota:** Esta optimización no es aplicable a la Raspberry Pi 4 debido a interrupciones bloqueadas por hardware.

1.  Asegúrese de que su DAC esté encendido y conectado al Target.
2.  Inicie la reproducción de música en el Diretta Target. Esto asegura que el script pueda detectar tráfico de interrupción activo.
3.  Ejecute el siguiente comando en el Diretta Target:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/usb-isolation.sh | sudo bash
    ```
4.  Reinicie para aplicar los cambios:
    ```bash
    sudo sync && sudo reboot
    ```

**Qué hace esto:** El script localiza la ruta activa del DAC (por ejemplo, xhci-hcd:usb1 o xhci-hcd:usb3). Luego agrega el identificador específico a su grupo de aislamiento de AudioLinux para crear una ruta de datos 100% aislada desde la entrada de red hasta la salida USB.

---

### Parte 2: Optimización de hilos en el Diretta Host

Con las optimizaciones del kernel en tiempo real aplicadas, el Diretta Host ahora puede manejar un intervalo de paquetes más agresivo, lo que puede conducir a una mejor calidad de sonido. Este paso final reduce el parámetro `CycleTime` de 800 a 514 microsegundos. Este intervalo de tiempo más pequeño entre paquetes garantiza que todo el contenido hasta DSD256 y DXD (32 bits, 352.8 kHz) requerirá solo un paquete por ciclo. También podemos programar hilos de Diretta en núcleos específicos.

1.  Conéctese por SSH al **Diretta Host** si no ha iniciado sesión todavía.
2.  Ejecute el siguiente comando para aplicar la configuración optimizada:
    ```bash
    cat <<'EOT' | sudo tee /opt/diretta-alsa/setting.inf
    [global]
    Interface=end0
    Broadcast=disable
    ScanOnlineStop=enable
    ScanInterval=
    TargetProfileLimitTime=200
    ThredMode=16
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
3.  Reinicie el servicio de Diretta para que el cambio surta efecto:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart diretta_alsa.service
    ```

> ---
> ### ✅ Punto de control: Verificar su ajuste en tiempo real
>
> Su ajuste avanzado en tiempo real ahora debería estar completo. Para verificar todos los componentes de esta nueva configuración, regrese al [**Apéndice 5**](#14-ap%C3%A9ndice-5-comprobaciones-de-estado-del-sistema) y ejecute el comando universal **System Health Check** (Comprobación de estado del sistema) tanto en el Host como en el Target.
>
> ---

## 17. Apéndice 8: Velocidades de red puristas opcionales

**Objetivo:** Reducir el ruido eléctrico y mejorar la precisión del programador (scheduler) del sistema operativo limitando la velocidad del enlace de red dedicado y deshabilitando explícitamente Energy Efficient Ethernet (EEE).

Aunque parezca contradictorio, reducir la velocidad del enlace de 1 Gbps a 100 Mbps (o incluso a 10 Mbps) en el enlace dedicado (`end0`) puede mejorar la calidad del sonido. La menor frecuencia de funcionamiento de 100BASE-TX (31.25 MHz frente a 62.5 MHz) genera menos RFI. En el caso extremo, bajar la velocidad a 10 Mbps reduce la frecuencia de funcionamiento a 10 MHz. Además, asegurarse de que EEE esté deshabilitado evita que el enlace entre en estados de suspensión, eliminando posibles picos de latencia (flapping) y garantizando una estabilidad sólida en el hardware de la Raspberry Pi 5.

> ---
> ### 🎧 Análisis profundo: Por qué un límite de 10 Mbps restaura la "calma" sonora
>
> Restringir su enlace de audio dedicado a 10 Mbps introduce limitaciones estrictas de formato, limitando su reproducción a **DSD64 nativo** y **PCM de 32 bits/96 kHz**. Sin embargo, para los audiófilos que priorizan la calidad de CD Red Book o los archivos estándar de alta resolución, el compromiso ofrece profundos beneficios sonoros al abordar las causas fundamentales del brillo digital.
>
> * **Frecuencias portadoras drásticamente más bajas:** Gigabit Ethernet estándar funciona con una señal portadora de alta frecuencia de 62.5 MHz (utilizando una codificación multinivel compleja). Bajar a 100 Mbps reduce esto a 31.25 MHz. Descender por completo a un enlace de 10 Mbps (10BASE-T) utiliza un esquema de codificación de Manchester de lo más simple que funciona a una frecuencia portadora nativa de tan solo **10 MHz**. Esta reducción masiva en la frecuencia de funcionamiento disminuye significativamente las emisiones de radiofrecuencia (RFI) generadas dentro del chasis y a lo largo del cable.
> * **Sobrecarga de procesamiento reducida en el Target:** Las redes de gran ancho de banda obligan a la tarjeta de interfaz de red (NIC) y a la CPU a manejar los paquetes de datos con una cadencia rápida y agresiva. Al limitar la velocidad del enlace para que coincida con las demandas reales de los datos de audio estándar, reduce drásticamente el volumen de interrupciones de red que debe procesar el sistema operativo del Target.
> * **Sinergia con la filosofía central de Diretta:** Todo el objetivo del protocolo Diretta es eliminar el procesamiento en ráfagas y estabilizar el consumo de corriente. Una tubería de 10 Mbps actúa como un ecualizador físico para el flujo de datos, evitando los picos de datos de alta velocidad que causan fluctuaciones en la fuente de alimentación.
>
> El resultado de esta constricción "Súper Purista" es una caída instantáneamente reconocible en el piso de ruido digital. Los oyentes reportan con frecuencia un escenario sonoro más amplio y relajado, un seguimiento de transitorios de alta frecuencia más limpio y una sensación general de facilidad y calma analógicas que complementa perfectamente lo que AudioLinux y Diretta intentan lograr.
> ---

> **Nota:** Es posible que vea advertencias de "buffer low" (búfer bajo) en los registros del Target (el `LatencyBuffer` baja a 1). Este es un comportamiento normal debido al aumento de la latencia de serialización del enlace más lento y no causa pérdidas de audio audibles.

### Paso 1: Configurar el Host y el Target (Deshabilitar EEE)

Energy Efficient Ethernet (EEE) puede causar inestabilidad en el enlace en algunas combinaciones de hardware. Crearemos un servicio para deshabilitarlo explícitamente tanto en el Host como en el Target para garantizar un comportamiento constante.

**Crear el servicio de desactivación:** *(Realizar en AMBOS Host y Target)*

```bash
cat <<'EOT' | sudo tee /etc/systemd/system/disable-eee.service
[Unit]
Description=Disable EEE on end0 for Link Stability
After=network.target
BindsTo=sys-subsystem-net-devices-end0.device
After=sys-subsystem-net-devices-end0.device

[Service]
Type=oneshot
# Esperar hasta 5 segundos para que la interfaz se muestre realmente como UP
ExecStartPre=/usr/bin/bash -c 'for i in {1..5}; do if ip link show end0 | grep -q "UP"; then exit 0; fi; sleep 1; done; exit 1'
# Ahora establecer la optimización de hardware
ExecStart=-/usr/bin/ethtool -s end0 advertise 0x03f
ExecStart=-/usr/bin/ethtool --set-eee end0 eee off
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOT

sudo systemctl daemon-reload
sudo systemctl enable --now disable-eee.service
```

### Paso 2: Marcar el Target (Para QA)

Para asegurarse de que el **Script de QA del Target** sepa que debe validar esta configuración específica, cree un archivo marcador en el Target:

```bash
sudo touch /etc/diretta-100m
```

### Paso 3: Configurar el Host (Límite de velocidad)
Crearemos un servicio en el **Host** que lo obligue a anunciar ya sea 10 Mbps o 100 Mbps Full Duplex, dependiendo de si el modo "Súper Purista" está habilitado. El Target detectará automáticamente el cambio de velocidad y se adaptará a él.

**Crear el restricción script y servicio:** *(Realizar en Host únicamente)*
```bash
cat <<'EOT' | sudo tee /usr/local/bin/set-link-speed.sh
#!/bin/bash
# Establecer la velocidad del enlace según el indicador Super Purista de la interfaz web, usando máscaras de publicidad seguras
FLAG_FILE="/home/audiolinux/purist-mode-webui/super_purist.flag"
INTERFACE="end0"

# CRÍTICO: Esperar hasta 60 segundos para que la interfaz física inicialice la capa de enlace del portador
echo "Sincronizando con la capa de enlace físico..."
for i in {1..60}; do
    if [ -f /sys/class/net/$INTERFACE/carrier ] && [ "$(cat /sys/class/net/$INTERFACE/carrier 2>/dev/null)" "==" "1" ]; then
        echo "Capa de enlace físico detectada tras $i segundos."
        break
    fi
    sleep 1
done

# Aplicar la máscara de publicidad según el estado del indicador
if [ -f "$FLAG_FILE" ]; then
    echo "Indicador Super Purista detectado. Anunciando 10 Mbps Full Duplex..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x002
else
    echo "Modo Estándar/Purista. Anunciando hasta 100 Mbps Full Duplex..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x00a
fi

# Gestión de negociación específica por plataforma
if grep -q "Raspberry Pi 4" /proc/device-tree/model 2>/dev/null; then
    echo "Raspberry Pi 4 detectado. Iniciando pulso obligatorio de renegociación de hardware..."
    /usr/bin/ethtool -r $INTERFACE
elif grep -q "Raspberry Pi 5" /proc/device-tree/model 2>/dev/null; then
    echo "Raspberry Pi 5 detectado. Se utiliza el pulso automático interno de phylib; omitiendo reinicio manual."
else
    /usr/bin/ethtool -r $INTERFACE || true
fi

echo "Política de velocidad del enlace finalizada correctamente."
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

echo "Habilitar e iniciar el servicio:"
sudo systemctl daemon-reload
sudo systemctl enable --now limit-speed-100m.service
```

***
> **Nota sobre la latencia de reproducción:**
> Es posible que note un ligero aumento en el retraso entre presionar "Reproducir" y escuchar la música (hasta ~1 segundo). Este es un comportamiento esperado. Al restringir el enlace a 10 o 100 Mbps, estamos limitando intencionalmente la ráfaga de datos inicial para garantizar que la conexión funcione a una frecuencia más baja y silenciosa. El sistema cambia tiempos de inicio instantáneos por un estado estable más constante y con menos ruido durante la reproducción.
***

>
>
> ---
>
> ### ✅ Punto de control: Verificar la configuración de red
>
> Su enlace de red dedicado ahora está configurado para la operación "Purista" de 100 Mbps. Para verificar que el servicio del Host esté activo y que el Target haya negociado correctamente la velocidad (detectada a través del archivo marcador), regrese al [**Apéndice 5**](#14-ap%C3%A9ndice-5-comprobaciones-de-estado-del-sistema) y ejecute el comando universal **System Health Check** (Comprobación de estado del sistema) tanto en el Host como en el Target.
>
> ---

## 18. Apéndice 9: Optimización de tramas jumbo opcional
Este sección optimiza el transporte para alta eficiencia de ancho de banda.

#### **Paso 1:** Preparar interfaces

Debemos forzar temporalmente las interfaces de red a un MTU de 9000 para verificar el soporte del kernel y prepararnos para la prueba de enlace.

**Ejecute esto en el Target primero, luego en el Host:**

```bash
sudo sh -c 'ip link set end0 down; sleep 2; ip link set end0 mtu 9000; ip link set end0 up'
end0_mtu=$(ip link show dev end0 | awk '/mtu/ {print $5}')
if [[ "9000" == "$end0_mtu" ]]; then
  echo "ÉXITO: El kernel admite tramas Jumbo. Proceda al Paso 2."
else
  echo "ALTO: Su kernel no parece admitir tramas Jumbo."
fi
```

*Si ve "ALTO" en **cualquiera** de los dos (Host o Target), no proceda. Su kernel no tiene el parche requerido.*

---

#### **Paso 2:** Configuración automatizada del Target

Conéctese por SSH al Target (`diretta-target`) y pegue el siguiente bloque.

```bash
# 1. Detectar límite de enlace (Completo vs Baby)
echo "Probando la capacidad del enlace..."
if ping -c 1 -w 1 -M "do" -s 8972 host &>/dev/null; then
  NEW_MTU=9000
  echo "ÉXITO: Tramas Jumbo completas (MTU 9000) admitidas."
elif ping -c 1 -w 1 -M "do" -s 2004 host &>/dev/null; then
  NEW_MTU=2032
  echo "ÉXITO: Tramas Jumbo pequeñas (MTU 2032) admitidas."
else
  echo "FALLO: El enlace no admite tramas Jumbo. Revirtiendo a los valores predeterminados seguros."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Aplicar la configuración de red del sistema
  echo "Configurando /etc/systemd/network/end0.network..."
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

  # 3. Aplicar la configuración de Diretta
  echo "Configurando el Diretta Target..."
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
  echo "LISTO: Optimización del Target completada."
}

```

---

#### **Paso 3:** Configuración automatizada del Host

Conéctese por SSH al Host (`diretta-host`) y pegue el siguiente bloque. Probará el enlace, configurará los ajustes permanentes de red y actualizará Diretta.

```bash
# 1. Detectar límite de enlace (Completo vs Baby)
echo "Probando la capacidad del enlace..."
# Dar un momento para que el enlace se estabilice después del cambio manual de MTU
sleep 2

if ping -c 1 -w 1 -M "do" -s 8972 target &>/dev/null; then
  NEW_MTU=9000
  echo "ÉXITO: Tramas Jumbo completas (MTU 9000) admitidas."
elif ping -c 1 -w 1 -M "do" -s 2004 target &>/dev/null; then
  NEW_MTU=2032
  echo "ÉXITO: Tramas Jumbo pequeñas (MTU 2032) admitidas."
else
  echo "FALLO: El enlace no admite tramas Jumbo. Revirtiendo a los valores predeterminados seguros."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Aplicar la configuración de red del sistema
  echo "Configurando /etc/systemd/network/end0.network..."
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

  # 3. Aplicar la configuración de Diretta
  echo "Configurando el Diretta Host..."

  # Habilitar siempre FlexCycle para tramas Jumbo para garantizar la estabilidad
  sudo sed -i 's/^FlexCycle=.*/FlexCycle=enable/' /opt/diretta-alsa/setting.inf

  # Optimización condicional de CycleTime e InfoCycle
  if [ "$NEW_MTU" -eq 9000 ]; then
    echo "Optimización: Tramas Jumbo completas detectadas. Relajando CycleTime a 1000us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=1000/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=100000/' /opt/diretta-alsa/setting.inf
  else
    echo "Optimización: Tramas Jumbo pequeñas detectadas. Estableciendo CycleTime a 700us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=700/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=70000/' /opt/diretta-alsa/setting.inf
  fi

  sudo systemctl restart diretta_alsa
  echo "LISTO: Optimización del Host completada."
}
```

#### **Paso 4:** Reiniciar para aplicar los cambios de MTU
Reinicie el Target primero, luego el Host:
```bash
sudo sync && sudo reboot
```

>
>
> ---
>
> ### ✅ Punto de control: Verificar la configuración de red
>
> Si pudo habilitar el soporte de tramas Jumbo para su configuración, ahora es un buen momento para regresar al [**Apéndice 5**](#14-ap%C3%A9ndice-5-comprobaciones-de-estado-del-sistema) y ejecutar el comando universal **System Health Check** (Comprobación de estado del sistema) tanto en el Host como en el Target.
>
> ---

## 19. Apéndice 10: Actualizaciones del sistema opcionales
Esta sección proporciona orientación sobre la aplicación de actualizaciones al hardware de Raspberry Pi, el sistema operativo AudioLinux y la pila de software Diretta.

#### **Parte 1:** Actualizar el bootloader de Raspberry Pi (Opcional)

La actualización del bootloader (EEPROM) de Raspberry Pi no es obligatoria y conlleva riesgos inherentes. Sin embargo, mantener el firmware actualizado puede ofrecer ventajas como temperaturas de funcionamiento más bajas y secuencias de inicio más limpias debido a las continuas correcciones de errores proporcionadas por la Fundación Raspberry Pi.

*Advertencia: Asegúrese de aplicar siempre la imagen de firmware correcta a la placa correspondiente. Grabar una Raspberry Pi 4 con un bootloader de Raspberry Pi 5 (o viceversa) puede tener consecuencias negativas graves, que van desde daños menores hasta dejar la placa permanentemente inservible (bricked).*

**Verificar la versión actual del bootloader**
Antes de comenzar, conéctese por SSH tanto al Host como al Target y ejecute el siguiente comando para verificar la fecha de lanzamiento de su bootloader actual. Tome nota de estas fechas para poder verificar el éxito de la actualización más adelante.

```bash
vcgencmd bootloader_version
```

*(Busque la fecha en la primera línea de la salida).*

**Preparar el medio de actualización**
Necesitará una tarjeta microSD en blanco, un lector de tarjetas SD y el software oficial Raspberry Pi Imager instalado en su estación de trabajo.

1. Abra Raspberry Pi Imager. Haga clic en **CHOOSE DEVICE** (ELEGIR DISPOSITIVO) y seleccione la placa Raspberry Pi específica que actualizará.

   ![Seleccionar dispositivo Raspberry Pi 5](images/01-rpi-dev.png)

2. Haga clic en **CHOOSE OS** (ELEGIR SO), desplácese hacia abajo en la lista y seleccione **Misc utility images** (Imágenes de utilidades varias).

   ![Seleccionar imágenes de utilidades varias](images/02-rpi-misc.png)

3. Seleccione **Bootloader**. *(Nota: El menú mostrará la familia de Pi que seleccionó en el Paso 1)*.

   ![Seleccionar bootloader para la familia Pi 5](images/03-rpi-bl.png)

4. Seleccione **SD Card Boot** (Arranque desde tarjeta SD).

   ![Seleccionar arranque desde tarjeta SD](images/04-rpi-sd.png)

5. Haga clic en **CHOOSE STORAGE** (ELEGIR ALMACENAMIENTO), seleccione su tarjeta microSD vacía, haga clic en **NEXT** (SIGUIENTE) y escriba la imagen.

*Importante: Si su Target es una Raspberry Pi 5 y su Host es una Raspberry Pi 4 (o cualquier combinación mixta), no puede reutilizar la misma tarjeta de actualización. Debe volver a su computadora y grabar una nueva tarjeta microSD de actualización específicamente para el segundo tipo de placa antes de proceder.*

**Realizar la actualización del hardware**

1. Apague ambos dispositivos de forma segura. Apague el Target primero, luego el Host (`sudo poweroff`).
2. Desconecte los cables de alimentación física de ambas unidades.
3. Retire las tarjetas microSD de arranque principal de cada unidad y guárdelas en un lugar seguro.
4. Inserte con cuidado la tarjeta microSD de actualización recién preparada en la placa (asegúrese de que los contactos dorados miren hacia la parte inferior de la placa Raspberry Pi).
5. Vuelva a conectar la alimentación a la placa.
6. Observe las luces de actividad en la placa. Espere hasta que el LED verde comience a parpadear rápidamente a un ritmo constante y continuo (esto suele tardar unos 10 segundos). El parpadeo constante indica que la grabación de la EEPROM ha finalizado.
7. Desconecte la alimentación de la placa.
8. Retire la tarjeta microSD de actualización y vuelva a insertar su tarjeta microSD de arranque original.
9. Vuelva a conectar la alimentación a los sistemas. **Encienda el Host primero, luego el Target.**

Una vez que los sistemas estén completamente iniciados y sean accesibles, ejecute la verificación de la versión del bootloader en cada computadora una vez más para confirmar que las fechas del bootloader hayan avanzado a la fecha de lanzamiento escrita por el Imager. Si su Host y su Target utilizan diferentes tipos de placa (por ejemplo, RPi4 y RPi5), es probable que las versiones sean diferentes. No pasa nada.

```bash
vcgencmd bootloader_version
```

---

#### **Parte 2:** Actualizar AudioLinux y el software Diretta

El proceso de actualización del sistema requiere una secuencia estricta para garantizar que el kernel personalizado, las cadenas de herramientas de compilación y el demonio ALSA permanezcan perfectamente sincronizados.

#### Ahora, proceda con las actualizaciones
1. Inicie la herramienta de configuración de AudioLinux escribiendo `menu` en el símbolo del sistema.
2. Navegue al **Install/Update menu** y seleccione **UPDATE System**.
3. Mientras esté en el **Install/Update menu**, seleccione **UPDATE menu**.
   *(Nota: Se le solicitará que ingrese la dirección de correo electrónico utilizada para la compra de AudioLinux, junto con el nombre de usuario y la contraseña específicos proporcionados por Piero para descargar la imagen de AudioLinux)*.
4. Seleccione **SELECT/UPDATE kernel**. Elija la versión exacta del kernel recomendada anteriormente en el [**Paso 4**](#44-ejecutar-actualizaciones-del-sistema-y-del-men%C3%BA).
5. Vuelve a aplicar la corrección de `motd` de la [**Sección 5.1**](#51-preconfigurar-el-diretta-host) en el **Host**.
6. Vuelva a aplicar el parche de `sudoers` de la [**Sección 7.2**](#72-corregir-la-precedencia-de-reglas-de-sudoers) en **ambos** (Target y Host).
7. Reinicie el Target primero, seguido del Host.
8. Una vez en línea de nuevo, vuelva a ejecutar el script "Configurar la cadena de herramientas del compilador compatible" del [**Paso 8**](#8-instalaci%C3%B3n-y-configuraci%C3%B3n-del-software-diretta) en **ambos** (Target y Host).
9. En el **Target**, ejecute el paso de instalación/actualización de Diretta detallado en la [**Sección 8.1**](#81-en-el-diretta-target).
10. En el **Host**, ejecute el paso de instalación/actualización de Diretta detallado en la [**Sección 8.2**](#82-en-el-diretta-host).
11. Reinicie el Target primero, seguido del Host.
>
>
> ---
>
> ### ✅ Punto de control: Estado del sistema y pruebas de regresión
>
> Después de completar la secuencia de actualización, debe verificar la estabilidad del flujo de audio para asegurarse de que no ocurrieran regresiones de software o configuración durante la actualización.
>
> 1. Abra Roon, espere a que regrese la zona de red y reproduzca al menos unos segundos de música para verificar el enlace de la capa de transporte y hacer que los contadores de hardware comiencen a moverse.
> 2. Conéctese por SSH al **Target** y revierta temporalmente al Modo Estándar para permitir que los scripts de diagnóstico transmitan tráfico de forma limpia a través de la red:
>    ```bash
>    purist-mode --revert
>    ```
> 3. Ejecute el script universal de control de calidad **System Health Check** (Comprobación de estado del sistema) del [**Apéndice 5**](#14-ap%C3%A9ndice-5-comprobaciones-de-estado-del-sistema) tanto en el Host como en el Target.
> 4. Verifique cuidadosamente el resultado y resuelva cualquier problema de prioridad o afinidad de hilos aislados detectado por el script.
>
> ---

---

#### **Parte 3:** Anular los límites de corriente USB (Solo para Raspberry Pi 5)

Si está utilizando una Raspberry Pi 5 y la alimenta con una fuente de alimentación de terceros premium (por ejemplo, iFi SilentPower Elite 5V o una fuente de alimentación lineal con capacidad de 5A) en lugar de la fuente oficial Raspberry Pi 27W USB-C, la Pi negociará por defecto a un nivel seguro de 5V/3A. Esto restringe el consumo de corriente combinado de los cuatro puertos USB a 600 mA.

Aunque suele ser irrelevante para los transportes de audio puros, si sabe que su Power Supply es capaz de entregar de forma continua al menos 5A a 5V, puede anular esta restricción de forma segura.

**Ejecute este comando para agregar la anulación a su configuración de arranque:**

```bash
if ! grep -q "^usb_max_current_enable=" /boot/config.txt; then
  echo "usb_max_current_enable=1" | sudo tee -a /boot/config.txt
else
  echo "Optimización ya presente en /boot/config.txt. Omitiendo la configuración."
fi
sudo sync && sudo reboot
```

---

## 20. Apéndice 11: Integración opcional de UPnP

**Objetivo:** Habilitar las capacidades de renderizado de medios UPnP/DLNA en el Diretta Host utilizando MPD (Music Player Daemon) y UPMPDCLI, permitiendo la compatibilidad con puntos de control y reproductores ascendentes como Audirvāna, mconnect o BubbleUPnP.

Esta configuración permite al Diretta Host recibir flujos de red UPnP estándar y enrutarlos limpiamente en la capa del controlador ALSA de Diretta sincronizada para su transmisión a través del enlace punto a punto al Target.

> ---
> ### ⚠️ Nota de topología: Realizar solo en el Host
>
> Todos los pasos de instalación y configuración detallados en este apéndice deben ejecutarse exclusivamente en el **Diretta Host**. El Diretta Target sigue siendo un extremo de protocolo minimalista y no requiere ajustes para la reproducción UPnP.
> ---

### Paso 1: Instalar y habilitar MPD y UPMPDCLI

1. Establezca una conexión SSH e inicie sesión en el **Diretta Host**.
2. Inicie la herramienta de configuración de AudioLinux ejecutando:
   ```bash
   menu
   ```
3. Navegue al menú **INSTALL/UPDATE**.
4. Seleccione **INSTALL/UPDATE MPD** y deje que el script de instalación se complete.
5. Regrese a la pantalla de actualización y seleccione **INSTALL/UPDATE UPMPDCLI**, permitiendo que finalice la configuración.
6. Regrese al **Menú principal**, seleccione el **Menú de audio** e ingrese a **SHOW audio service**.
7. Confirme que tanto **mpd** como **upmpdcli** estén activos. Si falta algún servicio en el grupo habilitado, seleccione **MPD enable/disable** o **UPMPDCLI enable/disable** respectivamente para activarlos.
8. Salga del sistema de menús para regresar a la shell del terminal.

### Paso 2: Configurar la salida de audio de MPD

Para dirigir el flujo de audio decodificado de MPD a la canalización de transporte de Diretta, agregue los parámetros de salida ALSA personalizados al final del archivo de configuración de MPD:

```bash
cat <<'EOT' | sudo tee -a /etc/mpd.conf

# === Custom Diretta ALSA Audio Output ===
audio_output {
    type "alsa"
    name "DIRETTA"
    device "hw:0,0"
    auto_resample "no"
    auto_format "no"
    dop "yes"
}
EOT
```

### Paso 3: Configurar el renderizador UPMPDCLI y los parámetros de red

Actualice los parámetros de configuración de UPMPDCLI para definir la configuración correcta de la interfaz de red ascendente y asignar un identificador descriptivo para el descubrimiento por parte de sus aplicaciones de control:

```bash
# 1. Dynamically discover the active LAN uplink interface
UPNP_IFACE=$(ip route show default | awk '{print $5}')

# 2. Verify an interface was found before making changes
if [ -n "$UPNP_IFACE" ]; then
    echo "Found active UPnP uplink interface: $UPNP_IFACE"
    if ! grep -q "# === Custom UPnP Network & Renderer Parameters ===" /etc/upmpdcli.conf; then
        echo "Applying custom UPnP configuration..."
        cat <<EOT | sudo tee -a /etc/upmpdcli.conf

# === Custom UPnP Network & Renderer Parameters ===

# Network interface(s) to use for UPnP (Dynamically Discovered)
upnpiface = ${UPNP_IFACE}

# Media Renderer parameters
# "Friendly Name" for the Media Renderer.
friendlyname = UpMpd-%h

# Specific friendly name for the UPnP/AV Media Renderer.
avfriendlyname = DIRETTA
EOT
    else
        echo "Configuration already exists in /etc/upmpdcli.conf. Updating interface name if changed..."
        sudo sed -i "s/^upnpiface = .*/upnpiface = ${UPNP_IFACE}/" /etc/upmpdcli.conf
    fi
else
    echo "ERROR: Could not programmatically determine the uplink interface." >&2
fi
```

### Paso 4: Reiniciar servicios

Ejecute una recarga de systemd y reinicie ambos demonios en segundo plano para forzar al sistema a inicializar sus anulaciones de configuración:

```bash
sudo systemctl daemon-reload
sudo systemctl restart mpd
sudo systemctl restart upmpdcli
```

> ---
> ### ✅ Punto de control: Verificar el funcionamiento de UPnP
>
> Abra su plataforma de control UPnP/DLNA elegida en un dispositivo remoto conectado a la red. Su sistema debería descubrir el extremo, mostrando **DIRETTA** como una zona de reproducción activa y seleccionable.
>
> Si tiene UPnP instalado y habilitado, ahora es un buen momento para regresar al [**Apéndice 5**](#14-ap%C3%A9ndice-5-comprobaciones-de-estado-del-sistema) y ejecutar el comando universal **System Health Check** (Comprobación de estado del sistema) tanto en el Host como en el Target.
>
> ---
