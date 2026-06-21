# Construindo um Link Diretta Dedicado com AudioLinux no Raspberry Pi

Este guia fornece instruções abrangentes, passo a passo, para configurar dois dispositivos Raspberry Pi como Host Diretta e Target Diretta dedicados. Esta configuração usa uma conexão Ethernet direta ponto a ponto entre os dois dispositivos para o máximo em isolamento de rede e desempenho de áudio.

O **Host Diretta** se conectará à sua rede principal (para acessar o seu servidor de música) e também funcionará como um gateway para o Target. O **Target Diretta** se conectará apenas ao Host e ao seu DAC ou DDC USB.

## Gerenciamento de Versões

Meu objetivo é manter este guia compatível com o link de download oficial atual do AudioLinux fornecido pelo Piero.

**Validação Atual:**
Estas instruções foram testadas pela última vez com o **AudioLinux V5** (Imagem: `audiolinux_pi4-pi5_520`, Versão do Menu: `536`).

**Uma Nota sobre Atualizações:**
Como o AudioLinux é baseado no Arch (um rolling release), uma instalação limpa sempre obterá a versão mais recente do software. Assim que seu sistema estiver soando de forma sublime, você tem duas opções:

1.  **Atualizar Frequentemente:** Comprometa-se a atualizar pelo menos mensalmente para que você possa corrigir pequenas falhas à medida que elas ocorram.
2.  **Deixar Como Está (Recomendado):** Se o som estiver ótimo, não mexa. Crie uma imagem de backup e aproveite a música!

## Uma Introdução à Arquitetura Roon de Referência

Bem-vindo ao guia definitivo para construir um endpoint de streaming Roon de última geração. Embora o AudioLinux suporte outros protocolos, usarei o Roon como exemplo para esta construção. Você pode usar o sistema de menus no Host Diretta para instalar o suporte para outros protocolos, incluindo HQPlayer, Audirvana, DLNA, AirPlay, etc. Antes de mergulhar nas instruções passo a passo, é importante entender o "porquê" por trás deste projeto. Esta introdução explicará o problema que esta arquitetura resolve, por que ela é fundamentalmente superior a muitas alternativas comerciais de alto custo e como este projeto DIY representa um caminho direto e recompensador para desbloquear a melhor qualidade de som do seu sistema Roon.

### O Paradoxo do Roon: Uma Experiência Poderosa com uma Ressalva Sônica

O Roon é celebrado, quase universalmente, como o sistema de gerenciamento de música mais poderoso e envolvente disponível. Seus metadados ricos e experiência de usuário contínua são inigualáveis. No entanto, essa supremacia funcional tem sido acompanhada por uma crítica persistente de um segmento expressivo da comunidade audiófila: a de que a qualidade de som do Roon pode ser comprometida, frequentemente descrita como "plana, sem brilho e sem vida" em comparação com outros players.

Esse "Som Roon" não é um mito, nem é uma falha no software bit-perfect do Roon. É um sintoma potencial da natureza poderosa e intensiva em recursos do Roon. O Core "pesado" do Roon requer poder de processamento significativo, o que por sua vez gera ruído elétrico (RFI/EMI). Quando o computador que executa o Roon Core está muito próximo do seu conversor digital-analógico (DAC) sensível, esse ruído pode contaminar o estágio de saída analógico, mascarando detalhes, encolhendo o palco sonoro e roubando a vitalidade da música.

---

### Indo Além de "Quebra-Galhos" para uma Solução Fundamental

A própria Roon Labs defende uma arquitetura de "duas caixas" para resolver este problema principal: separar o exigente **Roon Core** de um **Endpoint** de rede leve (também chamado de transporte de streaming). Este é o primeiro passo correto, pois transfere o processamento pesado para uma máquina remota, isolando seu ruído do seu rack de áudio.

No entanto, mesmo neste design superior de duas camadas, um problema mais sutil permanece. Os protocolos de rede padrão, incluindo o próprio RAAT do Roon, entregam dados de áudio em "rajadas" intermitentes. Isso força a CPU do endpoint a ter picos constantes de atividade para processar essas rajadas, causando flutuações rápidas no consumo de corrente. Essas flutuações geram seu próprio ruído elétrico de baixa frequência bem no endpoint — o componente mais próximo do seu DAC.

Fabricantes de áudio high-end tentam combater os *sintomas* desse tráfego em rajadas com várias soluções paliativas: fontes de alimentação lineares de alta capacidade para lidar melhor com os picos de corrente, CPUs de consumo ultra-baixo para minimizar a intensidade dos picos e estágios extras de filtragem para limpar o ruído resultante. Embora essas estratégias possam ajudar, elas não abordam a causa raiz do ruído: o próprio processamento em rajadas.

Este guia apresenta uma solução mais elegante e dramaticamente mais eficaz. Em vez de tentar limpar o ruído, construiremos uma arquitetura que evita que o ruído seja gerado em primeiro lugar.

---

### A Arquitetura de Três Camadas: Roon + Diretta

Este projeto evolui a configuração de duas caixas recomendada pelo Roon para um sistema definitivo de três camadas que fornece múltiplas camadas compostas de isolamento.

1.  **Camada 1: Roon Core**: Seu poderoso servidor Roon roda em uma máquina dedicada, colocada longe da sua sala de audição. Ele faz todo o trabalho pesado, e seu ruído elétrico é mantido isolado do seu sistema de áudio.
2.  **Camada 2: Host Diretta**: O primeiro Raspberry Pi em nossa montagem atua como o **Host Diretta**. Ele se conecta à sua rede principal, recebe o fluxo de áudio do Roon Core e depois o transmite em segmentos minúsculos e precisamente cronometrados, eliminando a natureza em rajadas do fluxo original.
3.  **Camada 3: Target Diretta**: O segundo Raspberry Pi, o **Target Diretta**, se conecta *apenas* ao Pi Host através de um cabo Ethernet curto, criando um link ponto a ponto galvanicamente isolado. Ele recebe o áudio do Host e se conecta ao seu DAC ou DDC via USB.

### O que o Diretta e o AudioLinux Trazem para a Mesa

A superioridade deste design vem de dois componentes de software fundamentais em execução nos dispositivos Raspberry Pi:

* **AudioLinux**: Este é um sistema operacional de tempo real desenvolvido especificamente para uso audiófilo. Diferente de um SO de uso geral, ele é otimizado para minimizar latências de processador e "jitter" do sistema, fornecendo uma base estável e de baixo ruído para o nosso endpoint.
* **Diretta**: Este protocolo inovador é o ingrediente secreto que resolve o problema raiz. Ele reconhece que flutuações na carga de processamento do endpoint geram ruído elétrico de baixa frequência que pode escapar da filtragem interna de um DAC (conforme definido por sua Taxa de Rejeição de Fonte de Alimentação, ou PSRR) e degradar sutilmente seu desempenho analógico. Para combater isso, o Diretta emprega seu modelo "Host-Target", no qual o Host envia dados em um fluxo contínuo e sincronizado de pacotes pequenos e uniformemente espaçados. Isso "suaviza a média" da carga de processamento no dispositivo Target, estabilizando seu consumo de corrente e minimizando a geração desse ruído elétrico pernicioso.

A combinação do isolamento galvânico físico do link Ethernet ponto a ponto e a eliminação do ruído de processamento do protocolo Diretta cria um caminho de sinal profundamente limpo para o seu DAC — que pode superar soluções que custam milhares de dólares.

---

### Um Caminho Recompensador para a Excelência Sônica

Este projeto é mais do que apenas um exercício técnico; é uma maneira recompensadora de se envolver com o hobby e assumir o controle direto sobre o desempenho do seu sistema. Ao construir esta "Ponte Diretta", você não está apenas montando componentes; você está implementando uma arquitetura de ponta que aborda os principais desafios do áudio digital diretamente. Você obterá uma compreensão mais profunda do que realmente importa para a reprodução digital e será recompensado com um nível de clareza, detalhes e realismo musical do Roon que você talvez não achasse possível.

Agora, vamos começar.

---

Se você estiver localizado nos EUA, espere pagar cerca de $320 (mais impostos e frete) para concluir a montagem básica, limitada à reprodução de 44.1/48 kHz (para avaliação), além de outros €100 para ativar a reprodução de alta resolução (preços sujeitos a alterações):
- Hardware ($240)
- Assinatura de um ano do AudioLinux ($79)
- Licença do Diretta Target (€100)

## Índice
1.  [Pré-requisitos](#1-pr%C3%A9-requisitos)
2.  [Preparação Inicial da Imagem](#2-prepara%C3%A7%C3%A3o-inicial-da-imagem)
3.  [Configuração Central do Sistema (Executar em Ambos os Dispositivos)](#3-configura%C3%A7%C3%A3o-central-do-sistema-executar-em-ambos-os-dispositivos)
4.  [Atualizações do Sistema (Executar em Ambos os Dispositivos)](#4-atualiza%C3%A7%C3%B5es-do-sistema-executar-em-ambos-os-dispositivos)
5.  [Configuração de Rede Ponto a Ponto](#5-configura%C3%A7%C3%A3o-de-rede-ponto-a-ponto)
6.  [Acesso SSH Conveniente e Seguro](#6-acesso-ssh-conveniente-e-seguro)
7.  [Otimizações Comuns do Sistema](#7-otimiza%C3%A7%C3%B5es-comuns-do-sistema)
8.  [Instalação e Configuração do Software Diretta](#8-instala%C3%A7%C3%A3o-e-configura%C3%A7%C3%A3o-do-software-diretta)
9.  [Etapas Finais e Integração com o Roon](#9-etapas-finais-e-integra%C3%A7%C3%A3o-com-o-roon)
10. [Apêndice 1: Controle de Ventoinha Argon ONE Opcional](#10-ap%C3%AAndice-1-controle-de-ventoinha-argon-one-opcional)
11. [Apêndice 2: Controle Remoto IR Opcional](#11-ap%C3%AAndice-2-controle-remoto-ir-opcional)
12. [Apêndice 3: Modo Purista Opcional](#12-ap%C3%AAndice-3-modo-purista-opcional)
13. [Apêndice 4: Interface Web Opcional de Controle do Sistema](#13-ap%C3%AAndice-4-interface-web-opcional-de-controle-do-sistema)
14. [Apêndice 5: Verificações de Saúde do Sistema](#14-ap%C3%AAndice-5-verifica%C3%A7%C3%B5es-de-sa%C3%BAde-do-sistema)
15. [Apêndice 6: Ajuste Opcional de Desempenho em Tempo Real](#15-ap%C3%AAndice-6-ajuste-opcional-de-desempenho-em-tempo-real)
16. [Apêndice 7: Otimizações Opcionais de IRQ e Threads](#16-ap%C3%AAndice-7-otimiza%C3%A7%C3%B5es-opcionais-de-irq-e-threads)
17. [Apêndice 8: Velocidades Opcionais de Rede Purista](#17-ap%C3%AAndice-8-velocidades-opcionais-de-rede-purista)
18. [Apêndice 9: Otimização de Jumbo Frames Opcional](#18-ap%C3%AAndice-9-otimiza%C3%A7%C3%A3o-de-jumbo-frames-opcional)
19. [Apêndice 10: Atualizações do Sistema Opcionais](#19-ap%C3%AAndice-10-atualiza%C3%A7%C3%B5es-do-sistema-opcionais)

---

### **Como Usar Este Guia**

Este guia foi projetado para ser o mais simples possível, minimizando a necessidade de edição manual de arquivos. O fluxo de trabalho principal será **copiar e colar** blocos de comando deste documento diretamente em uma janela de terminal conectada aos seus dispositivos Raspberry Pi.

Aqui está o processo que você seguirá para a maioria das etapas:

1.  **Conectar via SSH**: Você usará um cliente SSH em seu computador principal para fazer login no **Host Diretta** ou no **Target Diretta**, conforme instruído em cada seção.
2.  **Copiar o Comando**: Em seu navegador web, passe o cursor sobre o canto superior direito de um bloco de comando neste guia. Um **ícone de cópia** aparecerá. Clique nele para copiar todo o bloco para a sua área de transferência.
3.  **Colar e Executar**: Cole os comandos copiados na janela correta do terminal SSH e pressione `Enter`.

Os scripts e comandos foram cuidadosamente escritos para serem seguros e evitar erros, mesmo se executados mais de uma vez. Seguindo este método de copiar e colar, você pode evitar erros de digitação e de configuração comuns.

---

### Demonstração em Vídeo

Aqui está um link para uma série de vídeos curtos que demonstram este processo:

* [Demonstração da Montagem do Diretta com Dois Computadores Raspberry Pi](https://youtube.com/playlist?list=PLMl09rJ6zKCk13V-IH_kRKW7FP8Q0_Fw0&si=u_E8rUEhgMiQ4NIb)

---

### 1. Pré-requisitos

#### Hardware

Uma lista completa de materiais é fornecida abaixo. Embora outras partes possam ser substituídas, o uso desses componentes específicos aumenta as chances de uma montagem bem-sucedida.

**Componentes Principais (da [pishop.us](https://www.pishop.us/) ou fornecedor semelhante):**
* 2 x [Raspberry Pi 5/1GB](https://www.pishop.us/product/raspberry-pi-5-1gb/)
* 2 x [Gabinete Flirc Raspberry Pi 5](https://www.pishop.us/product/flirc-raspberry-pi-5-case/)
* 2 x [Cartão microSDXC A2 de 64 GB](https://www.bhphotovideo.com/c/product/1830849-REG/lexar_lmssipl064g_bnanu_64gb_silver_plus_microsdxc.html)
* 2 x [Fonte de Alimentação USB-C Raspberry Pi 45W - Branca](https://www.pishop.us/product/raspberry-pi-45w-usb-c-power-supply-white/)

**Componentes de Rede Necessários:**
* 1 x [Adaptador Plugable USB3 para Ethernet](https://www.amazon.com/dp/B00AQM8586) (para o Host Diretta)
* 1 x [Cabo de Conexão Ethernet CAT6 Curto](https://www.amazon.com/Cable-Matters-Snagless-Ethernet-Internet/dp/B0B57S1G2Y/?th=1) (para o link ponto a ponto)

**Opcional, mas útil para solução de problemas:**
* 1 x [Cabo Micro-HDMI para HDMI Padrão (A/M), 2m, Branco](https://www.pishop.us/product/micro-hdmi-to-standard-hdmi-a-m-2m-cable-white/)
* 1 x [Teclado Oficial do Raspberry Pi - Vermelho/Branco](https://www.pishop.us/product/raspberry-pi-official-keyboard-red-white/)

**Upgrades Opcionais:**
* 2 x [Gabinete Argon ONE V3 Raspberry Pi 5](https://www.amazon.com/Argon-ONE-V3-Raspberry-Case/dp/B0CNGSXGT2/) (em vez dos gabinetes Flirc)
* 1 x [Controle Remoto IR Argon](https://www.amazon.com/Argon-Raspberry-Infrared-Batteries-Included/dp/B091F3XSF6/) (para adicionar recursos de controle remoto ao Host Diretta)
* 1 x [Receptor IR USB Flirc](https://www.pishop.us/product/flirc-rpi-usb-xbmc-ir-remote-receiver/) (para usar o Controle Remoto IR Argon com o Host Diretta em um Gabinete Flirc)
* 1 x [Blue Jeans BJC CAT6a Belden Bonded Pairs 500 MHz](https://www.bluejeanscable.com/store/data-cables/index.htm) (para a conexão ponto a ponto entre Host e Target)
* 1 x [iFi SilentPower iPower Elite](https://www.amazon.com/gp/product/B08S622SM7/) (para fornecer energia limpa ao Target Diretta)
* 1 x [Cabo USB iFi SilentPower Pulsar](https://www.silentpower.tech/products/pulsar-usb) (conexão USB com isolamento galvânico)
* 1 x [Adaptador DC 5.5mm x 2.1mm para USB C](https://www.amazon.com/5-5mm-Adapter-Female-Convert-Connector/dp/B0CRB7N4GH/) (necessário para adaptar o plugue do iPower Elite para a entrada de energia USB C do Target Diretta)
* 1 x [SMSL PO100 PRO DDC](https://www.amazon.com/dp/B0BLYVZCV5) (um conversor digital para digital para DACs que não possuem uma boa implementação de entrada USB)
* 1 x [Adaptador Wireless USB](https://www.pishop.us/product/raspberry-pi-dual-band-5ghz-2-4ghz-usb-wifi-adapter-with-antenna/) (uma conexão cabeada é altamente preferível e mais confiável, mas se a adição de Ethernet cabeada perto do seu sistema de áudio for impraticável, substitua o adaptador Plugable USB para Ethernet por este adaptador Wi-Fi)
* 1 x [Cabo Divisor de Energia](https://www.amazon.com/dp/B01K3ADXX2?th=1) (conecte ambos os adaptadores de energia de 45W em uma única tomada)

**Componente de Áudio Necessário:**
* 1 x USB DAC ou DDC

**Ferramentas de Montagem Necessárias:**
* Laptop ou PC desktop executando Linux, macOS (iTerm2, https://iterm2.com/, recomendado) ou Microsoft Windows com [WSL2](https://learn.microsoft.com/en-us/windows/wsl/install)
* Um leitor de cartão SD ou microSD
* Uma TV ou tela HDMI e teclado USB (opcional, mas útil para solução de problemas)

#### Custos de Software e Licenciamento

* **AudioLinux:** Uma licença "Ilimitada" é recomendada para entusiastas, atualmente custa **$158** (preços sujeitos a alterações). No entanto, não há problema em começar com uma assinatura de um ano, atualmente **$79**. Ambas as opções permitem a instalação em múltiplos dispositivos no mesmo local.
* **Diretta Target:** É necessária uma licença para reprodução em alta resolução (superior a 48 kHz PCM) através do dispositivo Diretta Target e atualmente custa **€100**.
    * Você pode avaliar o Diretta Target usando fluxos de 44.1/48 kHz por um período prolongado de tempo. Portanto, recomendo usar o recurso de **Conversão de taxa de amostragem** do Roon nas configurações de DSP **MUSE** para converter todo o conteúdo para 44.1 kHz durante o período de avaliação. Quando estiver satisfeito, compre a licença do Diretta Target para remover a restrição. Deixe as configurações de conversão de taxa de amostragem ativas até receber o segundo e-mail da equipe do Diretta indicando que seu hardware foi ativado no banco de dados deles.
    * **CRÍTICO:** Esta licença está *bloqueada* ao hardware específico do Raspberry Pi para o qual foi adquirida. É essencial que você execute a etapa final de licenciamento no hardware exato que pretende usar permanentemente.
    * O Diretta pode oferecer uma licença de substituição única para falha de hardware nos primeiros dois anos (verifique os termos no momento da compra). Se você alterar o hardware por qualquer outro motivo, uma nova licença deverá ser adquirida.

---

### 2. Preparação Inicial da Imagem

1.  **Comprar e Baixar:** Obtenha a imagem do AudioLinux no [site oficial](https://www.audio-linux.com/). Você receberá um link para baixar um arquivo `.img.gz` ou `.img.xz` por e-mail, normalmente dentro de 24 horas após a compra.
2.  **Gravar a Imagem:** Use o [Raspberry Pi Imager](https://www.raspberrypi.com/software/)) para gravar a imagem baixada do AudioLinux em **ambos** os cartões microSD.

---

### 3. Configuração Central do Sistema (Executar em Ambos os Dispositivos)

Após a gravação, você deve configurar cada Raspberry Pi individualmente para evitar conflitos de rede.

Para obter o melhor desempenho, este guia usa o Raspberry Pi 5 tanto para o Diretta Target (o dispositivo conectado ao seu DAC) quanto para o Diretta Host. Você configurará o Host primeiro.

> **AVISO CRÍTICO:** Como ambos os dispositivos são gravados a partir da mesma imagem, eles terão valores de `machine-id` idênticos. Se você ligar ambos os dispositivos ao mesmo tempo enquanto estiverem conectados à mesma LAN, seu servidor DHCP provavelmente atribuirá a eles o mesmo endereço IP, causando um conflito de rede.
>
> **Você deve realizar a inicialização e a configuração inicial de cada dispositivo, um de cada vez.**

1.  Insira o cartão microSD no **primeiro** Raspberry Pi, conecte-o à sua rede e ligue-o. **Nota:** Se você estiver usando o gabinete Argon ONE, poderá ouvir ruído da ventoinha. Não se preocupe. Depois de concluir a configuração do Diretta, há instruções no [Apêndice 1](#10-ap%C3%AAndice-1-controle-de-ventoinha-argon-one-opcional) para lidar com o ruído da ventoinha.
2.  Conclua **toda a Seção 3** para este primeiro dispositivo.
3.  Assim que o primeiro dispositivo for reiniciado com sua nova configuração exclusiva, desligue-o.
4.  Agora, ligue o **segundo** Raspberry Pi e repita **toda a Seção 3** para ele.

Consulte o recibo da sua compra do Audiolinux para obter o usuário SSH padrão e as senhas de sudo/root. Faça uma anotação delas, pois você as usará muitas vezes ao longo deste processo.

Você usará o cliente SSH em seu computador local para fazer login nos computadores RPi durante todo esse processo. Esse cliente exige que você tenha uma maneira de encontrar o endereço IP dos computadores RPi, que pode mudar de uma reinicialização para outra. A maneira mais fácil de obter essas informações é na interface web ou aplicativo do roteador da sua rede doméstica, mas você também pode instalar o aplicativo [fing](https://www.fing.com/app/) no seu smartphone ou tablet.

Depois de obter o endereço IP de um de seus computadores RPi, use o cliente SSH em seu computador local para fazer login usando este processo. Anote o comando `ssh` de exemplo, pois você usará comandos semelhantes a este ao longo deste guia.
```bash
cmd=$(cat <<'EOT'
read -rp "Insira o endereço do seu RPi e pressione [enter]: " RPi_IP_Address
echo 'Lembrete: a senha padrão está no seu e-mail do AudioLinux do Piero'
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 3.1. Regenerar o Machine ID

O `machine-id` é um identificador exclusivo para a instalação do SO. Ele **deve** ser diferente para cada dispositivo.

```bash
echo ""
echo "Old Machine ID: $(cat /etc/machine-id)"
sudo rm /etc/machine-id
sudo systemd-machine-id-setup
echo "New Machine ID: $(cat /etc/machine-id)"
```

#### 3.2. Configurar Hostnames Exclusivos

Defina um hostname claro para cada dispositivo para identificá-los facilmente. **Nota:** Se esta não for a sua primeira montagem usando estas instruções e você já tiver um par Diretta Host/Target em sua rede, considere selecionar um nome diferente para este novo Diretta Host, como `diretta-host2`, apenas para esta parte. Fazer isso facilitará o acesso aos dois de forma independente mais tarde.

**Em seu PRIMEIRO dispositivo (o futuro Host Diretta):**
```bash
# No Host Diretta
sudo hostnamectl set-hostname diretta-host
```

**Em seu SEGUNDO dispositivo (o futuro Target Diretta):**
```bash
# No Target Diretta
sudo hostnamectl set-hostname diretta-target
```

**Neste ponto, desligue o dispositivo. Repita as [etapas acima](#3-configura%C3%A7%C3%A3o-central-do-sistema-executar-em-ambos-os-dispositivos) para o segundo Raspberry Pi.**
```bash
sudo sync && sudo poweroff
```

---

### 4. Atualizações do Sistema (Executar em Ambos os Dispositivos)

Para as etapas desta seção, geralmente é mais eficiente (e menos confuso) concluir toda a Seção 4 no Host Diretta e depois repetir toda a seção no Target Diretta.

Cada RPi tem seu próprio machine ID, então você pode ligá-los agora. Se você tiver dois cabos de rede, é mais conveniente conectar ambos à sua rede doméstica ao mesmo tempo para as próximas etapas, mas caso contrário, você pode prosseguir um de cada vez. **Nota**: seu roteador provavelmente atribuirá a eles endereços IP diferentes daquele que você usou para fazer login inicialmente. Certifique-se de usar o novo endereço IP com seus comandos SSH. Aqui está um lembrete:

```bash
cmd=$(cat <<'EOT'
read -rp "Insira o (novo) endereço do seu RPi e pressione [enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

#### 4.1. Instalar o "Chrony" para atualizar o relógio do sistema

O relógio do sistema precisa estar preciso antes de podermos instalar as atualizações. O Raspberry Pi não tem bateria NVRAM, por isso o relógio deve ser configurado cada vez que ele inicializa. Isso normalmente é feito conectando-se a um serviço de rede. Este script garantirá que o relógio seja configurado e permaneça correto durante a operação do computador.

```bash
sudo id
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_chrony.sh | sudo bash
sleep 5
chronyc sources
```

#### 4.2. Configurar o seu Fuso Horário

```bash
cmd=$(cat <<'EOT'
clear
echo "Bem-vindo à configuração interativa de fuso horário."
echo "Você primeiro selecionará uma região e depois um fuso horário específico."

# Permitir que o usuário selecione uma região
PS3="Por favor, selecione um número para a sua região: "

select region in $(timedatectl list-timezones | grep -F / | cut -d/ -f1 | sort -u); do
  if [[ -n "$region" ]]; then
    echo "Você selecionou a região: $region"
    break
  else
    echo "Seleção inválida. Por favor, tente novamente."
  fi
done

echo ""

# Permitir que o usuário selecione um fuso horário dentro dessa região
PS3="Por favor, selecione um número para o seu fuso horário: "

select timezone in $(timedatectl list-timezones | grep "^$region/"); do
  if [[ -n "$timezone" ]]; then
    echo "Você selecionou o fuso horário: $timezone"
    break
  else
    echo "Seleção inválida. Por favor, tente novamente."
  fi
done

# Configurar o fuso horário selecionado
echo
echo "Configurando o fuso horário para ${timezone}..."
sudo timedatectl set-timezone "$timezone"
echo "✅ O fuso horário foi configurado."

# Verificar a alteração
echo
echo "Fuso horário e hora atual do sistema:"
timedatectl status
EOT
)
bash -c "$cmd"
```

#### 4.3. Instalar DNS Utils
Instale o pacote `dnsutils` para que a atualização do **menu** tenha acesso ao comando `dig`:
```bash
sudo pacman -S --noconfirm --needed dnsutils
```

#### 4.4. Executar Atualizações do Sistema e do Menu

Use o sistema de menus do AudioLinux para realizar todas as atualizações. Tenha em mãos o e-mail do Piero com seu usuário e senha de download da imagem. Você precisará deles para a atualização do menu. Ele solicitará seu **usuário de atualização de menu**, o que é um pouco confuso. Ele está solicitando o nome de usuário e a senha que você usou para baixar a imagem de instalação do AudioLinux.

1.  Execute `menu` no terminal.
2.  Selecione **INSTALL/UPDATE menu**.
    ```text
    Verifying license...
    Please enter the email address used at the time of purchase
    (You will only be asked once)
    ?
    <endereço de e-mail usado para comprar o suporte do AudioLinux>
    OK
    OK

    Please type your menu update user
    ?
    <AUDIOLINUX RASPBERRY "user:" do seu e-mail de licença)>
    Please type your menu update password
    ?
    <AUDIOLINUX RASPBERRY "password:" do seu e-mail de licença)>
    ```
3.  Na próxima tela, selecione **UPDATE system** e deixe o processo ser concluído.
4.  Após a conclusão da atualização do sistema, selecione **Update menu** na mesma tela para obter a versão mais recente dos scripts do AudioLinux. *Nota:* Você precisará do endereço de e-mail que usou para comprar o AudioLinux e de seu nome de usuário e senha de download.
5.  Saia do sistema de menus para voltar ao terminal.

#### 4.5. Reiniciar
Reinicie para carregar o kernel e outras atualizações:
```bash
sudo sync && sudo reboot
```

---

### 5. Configuração de Rede Ponto a Ponto

Nesta seção, criaremos os arquivos de configuração de rede que ativarão o link privado dedicado. Para evitar a necessidade de um teclado e monitor físicos (acesso ao console), realizaremos essas etapas enquanto ambos os dispositivos ainda estão conectados à sua LAN principal e acessíveis via SSH.

Se você acabou de atualizar o seu Diretta Target, clique [aqui](https://github.com/dsnyder0pc/rpi-for-roon/blob/main/Diretta.md#52-pre-configure-the-diretta-target) para pular para as etapas de configuração de rede ponto a ponto para o Target.

---
> #### **Uma Nota sobre Configuração de Rede: Por que não uma Bridge Simples?**
>
> Usuários familiarizados com o AudioLinux podem se perguntar por que este guia usa scripts específicos para configurar um link ponto a ponto roteado com NAT em vez de usar a opção de bridge de rede mais simples disponível no sistema de `menu`. Esta é uma escolha de arquitetura deliberada feita para alcançar o mais alto nível possível de isolamento de rede.
>
> * Uma **bridge de rede** colocaria o Diretta Target diretamente na sua LAN principal, expondo-o a todo o tráfego de broadcast e multicast de rede não relacionado.
> * Nossa **configuração roteada** cria uma sub-rede completamente separada e protegida por firewall. O Host Diretta protege o Target de toda a comunicação de rede não essencial, garantindo que o processador do Target processe apenas o fluxo de áudio. Isso minimiza a atividade do sistema e o ruído elétrico potencial, que é o objetivo final desta arquitetura purista.
>
> Embora uma bridge seja funcionalmente mais simples de configurar, o método roteado fornece uma base teoricamente superior para o desempenho de áudio ao maximizar o isolamento.
---

#### 5.1. Pré-configurar o Host Diretta

1.  **Criar Arquivos de Rede:**
    Crie os dois arquivos a seguir no **Host Diretta**. O arquivo `end0.network` define o IP estático para o futuro link ponto a ponto. O arquivo `usb-uplink.network` garante que o adaptador Ethernet USB continue a obter um IP da sua LAN principal.

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

    **Important:** Remover o arquivo de rede genérico antigo para evitar conflitos:
    ```bash
    # Remover o arquivo de rede genérico antigo para evitar conflitos.
    sudo rm -fv /etc/systemd/network/{en,enp,auto,eth}.network
    ```

    Adicionar uma entrada /etc/hosts para o Diretta Target:
    ```bash
    HOSTS_FILE="/etc/hosts"
    TARGET_IP="172.20.0.2"
    TARGET_HOST="diretta-target"

    # Adicionar uma entrada para o Diretta Target se ela não existir
    if ! grep -q "$TARGET_IP\s\+$TARGET_HOST" "$HOSTS_FILE"; then
      printf "%s\t%s target\n" "$TARGET_IP" "$TARGET_HOST" | sudo tee -a "$HOSTS_FILE"
    fi
    ```

2.  **Ativar o Encaminhamento de IP:**
    ```bash
    # Ativar para a sessão atual
    sudo sysctl -w net.ipv4.ip_forward=1

    # Tornar permanente entre as reinicializações
    echo "net.ipv4.ip_forward=1" | sudo tee /etc/sysctl.d/99-ip-forwarding.conf
    ```

3.  **Configurar Network Address Translation (NAT):**
    ```bash
    # Garantir que o nft esteja instalado
    sudo pacman -S --noconfirm --needed nftables

    # Instalar regras de firewall e NAT
    cat <<'EOT' | sudo tee /etc/nftables.conf
    #!/usr/sbin/nft -f

    # Limpar todas as regras antigas da memória
    flush ruleset

    # Criar uma tabela chamada 'ip' (IPv4) denominada 'my_table'
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

    # Parar e desativar o serviço iptables antigo se presente (2>/dev/null suppresses errors if not present)
    sudo systemctl disable --now iptables.service 2>/dev/null
    sudo rm /etc/iptables/iptables.rules 2>/dev/null

    # Ativar e aplicar regras via nft
    sudo systemctl enable --now nftables.service
    ```

4.  **Configurar o Adaptador USB para Ethernet Plugable**

    O driver USB padrão não suporta todos os recursos do adaptador Ethernet Plugable. Para obter um desempenho confiável, precisamos dizer ao gerenciador de dispositivos do kernel como lidar com o dispositivo quando ele for conectado:
    ```bash
    cat <<'EOT' | sudo tee /etc/udev/rules.d/99-ax88179a.rules
    ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0b95", ATTR{idProduct}=="1790", ATTR{bConfigurationValue}!="1", ATTR{bConfigurationValue}="1"
    EOT
    sudo udevadm control --reload-rules
    ```

5.  **Corrigir o script update_motd.sh**

    O script que atualiza o banner de login (`/etc/motd`) não lida corretamente com o caso de duas interfaces de rede. Isso evita que a tela de login fique desorganizada com informações de endereço IP incorretas após as reinicializações. O novo script abaixo resolve esse problema.
    ```bash
    [ -f /opt/scripts/update/update_motd.sh.dist ] || \
    sudo mv /opt/scripts/update/update_motd.sh /opt/scripts/update/update_motd.sh.dist
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/update_motd.sh
    sudo install -m 0755 update_motd.sh /opt/scripts/update/
    rm update_motd.sh
    ```

    Por fim, desligue o Host:
    ```bash
    sudo sync && sudo poweroff
    ```

#### 5.2. Pré-configurar o Target Diretta

**Nota:** Se você não realizou a [etapa 4](#4-atualiza%C3%A7%C3%B5es-do-sistema-executar-em-ambos-os-dispositivos) no Target Diretta, faça isso [agora](#4-atualiza%C3%A7%C3%B5es-do-sistema-executar-em-ambos-os-dispositivos) e depois retorne aqui.

No **Target Diretta**, crie o arquivo `end0.network`. Isso configura seu IP estático e diz para usar o Host Diretta como seu gateway para todo o tráfego de internet.

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

**Importante:** Remover o arquivo en.network antigo, se presente:
```bash
# Remover o arquivo de rede genérico antigo para evitar conflitos.
sudo rm -fv /etc/systemd/network/{en,auto,eth}.network
```

Adicione uma entrada no /etc/hosts para o Host Diretta. **Nota:** Mesmo que você tenha selecionado um nome de rede diferente para o seu Host Diretta, é melhor que o Target Diretta conheça o seu Host como `diretta-host`.
```bash
HOSTS_FILE="/etc/hosts"
HOST_IP="172.20.0.1"
HOST_NAME="diretta-host"

# Adicionar uma entrada para o Diretta Host se ela não existir
if ! grep -q "$HOST_IP\s\+$HOST_NAME" "$HOSTS_FILE"; then
  printf "%s\t%s host\n" "$HOST_IP" "$HOST_NAME" | sudo tee -a "$HOSTS_FILE"
fi
```

> ---
> ### ⚠️ Aviso Crítico de Topologia: Apenas Posicionamento de Filtro a Montante
>
> Se você planeja aprimorar este projeto com regeneradores LAN, isoladores galvânicos ou filtros (como o StackAudio SmoothLAN, iFi SilentPower LAN iSilencer ou LAN iPurifier Pro), eles **devem ser colocados a montante do Host Diretta** (entre o switch/roteador principal da sua rede e o adaptador USB para Ethernet do Host).
>
> **Nunca coloque um filtro de rede ou dispositivo de reclocking ativo no link ponto a ponto entre o Host e o Target.** Fazer isso quase sempre degradará o desempenho do áudio e pode causar sérias regressões de conexão.
>
> * **A LAN Principal é a Fonte Primária de Ruído:** A conexão do seu roteador doméstico ou switch principal está inundada com interferência eletromagnética (EMI), interferência de radiofrequência (RFI) e tráfego de "lixo" de broadcast. Colocar um regenerador *antes* do Host elimina essa poluição digital no limite. O Host então processa um fluxo limpo, mantendo sua própria sobrecarga de CPU, flutuações de energia e ruído térmico no mínimo absoluto.
> * **Preservando o Tempo da Camada 2:** A introdução de um dispositivo ativo na ponte ponto a ponto direta interfere nas restrições de tempo ultra-precisas do Diretta (`CycleTime` e `syncBufferCount`). Isso prejudica a entrega precisa dos frames de Camada 2, resultando em retornos sonoros reduzidos, artefatos de latência ou falha completa do Target em negociar mudanças de velocidade de rede.
> * **O Princípio do Isolamento em Cascata:** O verdadeiro isolamento é construído em camadas para desacoplar completamente o seu DAC sensível da rede doméstica:
>   * **Rede Principal** → `[ LAN Filter/Regenerator ]` → **Host Diretta** *(Isola o Host da rede doméstica)*
>   * **Host Diretta** → `[ Dedicated Ethernet Cable ]` → **Target Diretta** *(Isolado via link ponto a ponto e a pilha de protocolos)*
> ---

#### 5.3. A Mudança de Conexão Física

> **Aviso:** Verifique novamente o conteúdo dos arquivos que você acabou de criar. Um erro de digitação pode tornar um dispositivo inacessível após a reinicialização, exigindo uma sessão de console ou a regravação do cartão SD para corrigir.

1.  Depois de verificar os arquivos, realize um desligamento limpo de **ambos** os dispositivos:
    ```bash
    sudo sync && sudo poweroff
    ```
2.  Desconecte ambos os dispositivos do switch/roteador principal da sua LAN.
3.  Conecte a **porta Ethernet integrada** do Host Diretta diretamente à **porta Ethernet integrada** do Target Diretta usando um único cabo Ethernet.
4.  Conecte o **adaptador USB para Ethernet** em uma das portas azuis USB 3.0 do computador Host Diretta
5.  Conecte o **adaptador USB para Ethernet** do Host Diretta ao switch/roteador principal da sua LAN.
6.  Ligue ambos os dispositivos.

Ao inicializar, eles usarão automaticamente as novas configurações de rede. **Nota:** o endereço IP do seu Host Diretta provavelmente terá mudado porque agora está conectado à sua rede doméstica através do adaptador USB para Ethernet. Você terá que retornar à interface web do seu roteador ou ao aplicativo Fing para encontrar o novo endereço, que deve estar estável neste ponto.

```bash
cmd=$(cat <<'EOT'
read -rp "Insira o endereço final do seu Host Diretta e pressione [enter]: " RPi_IP_Address
echo '$' ssh "audiolinux@${RPi_IP_Address}"
ssh -o StrictHostKeyChecking=accept-new "audiolinux@${RPi_IP_Address}"
EOT
)
bash -c "$cmd"
```

Agora você deve ser capaz de fazer ping no Target a partir do Host:
```bash
echo ""
echo "\$ ping -c 3 172.20.0.2"
ping -c 3 172.20.0.2
```

Além disso, você deve ser capaz de fazer login no Target a partir do Host:
```bash
echo ""
echo "\$ ssh target"
ssh -o StrictHostKeyChecking=accept-new target
```

A partir do Target, vamos tentar fazer ping em um host na Internet para verificar se a conexão está funcionando:
```bash
echo ""
echo "\$ ping -c 3 one.one.one.one"
ping -c 3 one.one.one.one
```

---

### 6. Acesso SSH Conveniente e Seguro

#### 6.1. O Requisito ProxyJump

Agora que a rede está configurada, o **Diretta Target** está em uma rede isolada (`172.20.0.0/24`) e não pode ser acessado diretamente da sua LAN principal. A única maneira de acessá-lo é dar um "salto" (jump) através do **Host Diretta**.

A diretiva `ProxyJump` na sua configuração SSH local é o método padrão e necessário para conseguir isso.

1.  Execute este comando no seu computador local (não no Raspberry Pi). Ele solicitará o endereço IP do Host Diretta e, em seguida, imprimirá o bloco de configuração exato que você precisa.
```bash
cmd=$(cat <<'EOT'
clear
# --- Script de Configuração Interativa de Alias SSH ---

SSH_CONFIG_FILE="$HOME/.ssh/config"
SSH_DIR="$HOME/.ssh"

# --- Garantir que o diretório .ssh e o arquivo de configuração existam com as permissões corretas ---
mkdir -p "$SSH_DIR"
chmod 0700 "$SSH_DIR"
touch "$SSH_CONFIG_FILE"
chmod 0600 "$SSH_CONFIG_FILE"

# --- Definir o bloco de configurações globais recomendado ---
GLOBAL_SETTINGS=$(cat <<'EOF'
# --- Recommended Global SSH Settings ---
Host *
    AddKeysToAgent yes
    IdentityFile ~/.ssh/id_ed25519

EOF
)

# --- Preceder configurações globais se elas não existirem ---
if ! grep -q "AddKeysToAgent yes" "$SSH_CONFIG_FILE"; then
  echo "✅ Adicionando configurações SSH globais recomendadas..."
  # Use a temporary file to prepend the settings
  echo "$GLOBAL_SETTINGS" | cat - "$SSH_CONFIG_FILE" > temp_ssh_config && mv temp_ssh_config "$SSH_CONFIG_FILE"
else
  echo "✅ As configurações SSH globais recomendadas já existem. Nenhuma alteração feita."
fi

# --- Adicionar configurações de host específicas do Diretta ---
if grep -q "Host diretta-host" "$SSH_CONFIG_FILE"; then
  echo "✅ A configuração SSH para 'diretta-host' já existe. Nenhuma alteração feita."
else
  read -rp "Insira o endereço IP da LAN do seu Host Diretta e pressione [Enter]: " Diretta_Host_IP

  # Append the new configuration using a heredoc for clarity
  cat <<EOT_HOSTS >> "$SSH_CONFIG_FILE"

# --- Diretta Configuration (added by script) ---
Host diretta-host host
    HostName ${Diretta_Host_IP}
    User audiolinux

Host diretta-target target
    HostName 172.20.0.2
    User audiolinux
    ProxyJump diretta-host
EOT_HOSTS

  echo "✅ A configuração SSH para 'diretta-host' e 'diretta-target' foi adicionada."
fi

# --- Limpar StrictHostKeyChecking de versões anteriores deste guia ---
# Isso não é mais necessário com a configuração recomendada de chave SSH
if command -v sed >/dev/null; then
    sed -i.bak -e '/StrictHostKeyChecking/d' "$SSH_CONFIG_FILE"
    # Remove empty lines that might be left over
    sed -i.bak -e '/^$/N;/^\n$/D' "$SSH_CONFIG_FILE"
    rm -f "${SSH_CONFIG_FILE}.bak"
fi

echo ""
echo "--- Seu arquivo ~/.ssh/config agora contém: ---"
cat "$SSH_CONFIG_FILE"
EOT
)
bash -c "$cmd"
```

2.  **Verificar a Conexão:**

Você deve ser capaz de se conectar a ambos os dispositivos usando os novos aliases. Teste a conexão com os seguintes comandos:

**Para fazer login no Host Diretta:**
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-host
```

Digite `exit` para sair.

**Para fazer login no Target Diretta:** _(será solicitada a senha duas vezes)_
```bash
ssh -o StrictHostKeyChecking=accept-new diretta-target
```
**Nota:** Será solicitada a senha uma vez para o diretta-host (o jump box) e uma segunda vez para o próprio diretta-target. A próxima seção substituirá isso por autenticação contínua baseada em chave.

**Nota:** Você pode usar `ssh host` e `ssh target` de forma abreviada.

#### 6.2. Recomendado: Autenticação Segura com Chaves SSH

Embora você possa usar senhas, o método mais seguro e conveniente é a autenticação por chave pública. Nossa configuração SSH automatiza a maior parte do processo. Após uma configuração única, você poderá fazer login no Host e no Target com segurança, sem digitar uma senha.

**Em seu computador local:**

1.  **Criar uma Chave SSH (se você ainda não tiver uma):**
    A melhor prática é usar um algoritmo moderno como `ed25519`. Quando solicitado, insira uma frase secreta (passphrase) forte e memorável. Esta não é a sua senha de login; é uma senha que protege o próprio arquivo de chave privada.

    ```bash
    ssh-keygen -t ed25519 -C "audiolinux"
    ```

2.  **Copiar sua Chave Pública para os Dispositivos:**
    Esses comandos concedem à sua chave acesso seguro a cada dispositivo. O primeiro comando solicitará a senha do Host Diretta. Como isso torna a conexão com o Host sem senha, o segundo comando solicitará apenas a senha do Target Diretta.

    ```bash
    echo ""
    ssh-copy-id diretta-host
    echo ""
    ssh-copy-id diretta-target
    ```

3.  **Fazer Login com Segurança:**
    Agora você pode acessar seus dispositivos via SSH. A primeira vez que você se conectar a cada um, será solicitada a **frase secreta** (passphrase) que você criou na Etapa 1.

    ```bash
    ssh diretta-host
    ```

      * **No Linux:** Graças à configuração `AddKeysToAgent yes`, sua chave será adicionada ao agente SSH para a sua sessão de terminal atual. Você não precisará digitar a frase secreta novamente até reiniciar ou iniciar uma nova sessão de login.

---

### (Opcional) Para uma Experiência Linux Aprimorada

Se você é um usuário Linux e deseja que a frase secreta da sua chave SSH persista após as reinicializações (semelhante à experiência no macOS), instalar o `keychain` é altamente recomendado.

  * **Instalar o keychain (Ubuntu/Debian):**

    ```bash
    sudo apt update && sudo apt install keychain
    ```

  * **Configurar o seu shell:** Adicione a seguinte linha ao seu `~/.bashrc` (ou `~/.zshrc`, `~/.profile`, etc.) para iniciar o `keychain` quando você abrir um terminal. Ele solicitará sua frase secreta apenas uma vez, na primeira vez que você abrir um terminal após uma reinicialização.

    ```bash
    eval "$(keychain --eval --quiet id_ed25519)"
    ```

  * Recarregue seu shell abrindo um novo terminal ou executando `source ~/.bashrc`.

Você pode acessar ambos os dispositivos via SSH (`ssh diretta-host`, `ssh diretta-target`) sem que uma senha seja solicitada, autenticado com segurança por sua chave SSH.

---

### 7. Otimizações Comuns do Sistema

Por favor, execute estas etapas em _ambos_ os computadores Host e Target Diretta. Se você fizer uma atualização de `menu` posteriormente, terá que executar novamente a correção do `sudoers`.

#### 7.1. Corrigir o Estado "Degraded" do Systemd

Em uma instalação limpa do AudioLinux, o status do sistema é frequentemente relatado como `degraded` (degradado). Isso geralmente é causado por uma inconsistência inofensiva entre os arquivos de grupo do sistema (`/etc/group` e `/etc/gshadow`). O comando a seguir sincroniza com segurança esses arquivos, o que resolve a falha do `shadow.service` e garante um estado limpo do sistema.

```bash
sudo grpconv
```

#### 7.2. Corrigir a Precedência da Regra do `sudoers`

Uma regra padrão no arquivo principal `/etc/sudoers` às vezes pode substituir regras mais específicas necessárias para a interface web e outros recursos. Isso pode fazer com que comandos que deveriam ser sem senha solicitem incorretamente uma senha.

O script a seguir corrige com segurança a ordem das regras no arquivo `/etc/sudoers` para garantir que exceções específicas sejam processadas corretamente. O script só fará alterações se detectar a ordem incorreta.

```bash
SUDOERS_FILE="/etc/sudoers"
TEMP_SUDOERS=$(mktemp)

# Usar um filtro Perl para criar uma versão corrigida do arquivo sudoers.
# Este script é idempotente e não alterará um arquivo que já esteja correto.
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

# Validar o novo arquivo com o visudo antes de instalar
if [ -s "$TEMP_SUDOERS" ] && sudo visudo -c -f "$TEMP_SUDOERS"; then
    echo "O arquivo sudoers passou na validação. Instalando a versão corrigida..."
    # Usar o comando install para definir a propriedade/permissões corretas e substituir o original
    sudo install -m 0440 -o root -g root "$TEMP_SUDOERS" "$SUDOERS_FILE"
else
    echo "ERRO: O arquivo sudoers modificado falhou na validação. Nenhuma alteração foi feita." >&2
fi
rm -f "$TEMP_SUDOERS"
```

#### 7.3. Otimizar o Tempo de Inicialização
Para evitar um longo atraso de inicialização enquanto o sistema aguarda por uma conexão de rede, desativaremos o serviço "wait-online".
```bash
# Desativar o serviço de espera de rede para evitar longos atrasos de inicialização
sudo systemctl disable systemd-networkd-wait-online.service

# Criar uma substituição para fazer o script MOTD esperar por uma rota padrão
sudo mkdir -p /etc/systemd/system/update_motd.service.d
cat <<'EOT' | sudo tee /etc/systemd/system/update_motd.service.d/wait-for-ip.conf
[Service]
ExecStartPre=/bin/sh -c "while [ -z \"$(ip route show default)\" ]; do sleep 0.5; done"
EOT
```

#### 7.4. Criar o Script de Reparo
O comportamento padrão do Arch Linux é deixar o sistema de arquivos `/boot` em um estado sujo se o computador não for desligado corretamente. Isso geralmente é seguro, mas descobri que pode criar uma condição de corrida ao subir nossa rede privada. Além disso, os usuários costumam desconectar esses dispositivos da tomada sem desligá-los primeiro. Para proteger contra esses problemas, adicionaremos um script de contorno que mantém limpo o sistema de arquivos `/boot` (que só é alterado durante as atualizações de software).

Este script é seguro para ser executado tanto automaticamente na inicialização quanto manualmente em um sistema ativo.
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/check-and-repair-boot.sh
sudo install -m 0755 check-and-repair-boot.sh /usr/local/sbin/
rm check-and-repair-boot.sh
```

#### 7.5. Criar o Arquivo de Serviço do `systemd` e Habilitar o Serviço
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

#### 7.6. Minimizar E/S de Disco
Altere `#Storage=auto` para `Storage=volatile` em `/etc/systemd/journald.conf`
```bash
sudo sed -i 's/^#Storage=auto/Storage=volatile/' /etc/systemd/journald.conf
```

---

### 8. Instalação e Configuração do Software Diretta

#### 8.1. No Target Diretta

1.  Conecte seu DAC USB a uma das portas pretas USB 2.0 no **Target Diretta** e certifique-se de que o DAC esteja ligado.
2.  Acesse o Target via SSH: `ssh diretta-target`.
3.  Configurar Toolchain de Compilador Compatível
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```
4.  Execute `menu`.
5.  Selecione **AUDIO extra menu**.
6.  Selecione **DIRETTA target installation/configuration**. Você verá o seguinte menu:
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
7.  Você deve realizar estas ações em sequência:
    * Escolha **1) Install/update** para instalar o software (responda "Y" para todas as solicitações).
    * Escolha **2) Enable/Disable Diretta Target** e habilite-o.
    * Escolha **3) Configure Audio card**. O sistema listará seus dispositivos de áudio disponíveis. Insira o número da placa correspondente ao seu DAC USB.
        ```text
        ?3
        This option will set DIRETTA target to use a specific card
        Your available cards are:

        card 0: AUDIO [SMSL USB AUDIO], device 0: USB Audio [USB Audio]

        Please type the card number (0,1,2...) you want to use:
        ?0
        ```
    * Escolha **4) Edit configuration**. Defina `AlsaLatency=20` para um Target Raspberry Pi 5 ou `AlsaLatency=40` para RPi4.
    * Escolha **6) License**. O sistema reproduzirá áudio de alta resolução (superior a 44.1 kHz PCM) por 6 minutos em modo de teste. Siga o link e as instruções na tela para adquirir e aplicar sua licença completa para suporte a alta resolução. Isso requer o acesso à internet que configuramos na etapa 5.
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
    * Escolha **8) Exit**. Siga as instruções para voltar ao terminal

#### 8.2. No Host Diretta

1.  Acesse o Host via SSH: `ssh diretta-host`.

2.  Configurar Toolchain de Compilador Compatível
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/setup_diretta_compiler.sh | sudo bash
    ```

3.  Execute `menu`.

4.  Selecione **AUDIO extra menu**.

5.  Selecione **DIRETTA host installation/configuration**. Você verá o seguinte menu:
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

6.  Você deve realizar estas ações em sequência:
    * Escolha **1) Install/update** para instalar o software (responda "Y" para todas as solicitações). *(Nota: você pode ver `error: package 'lld' was not found`. Não se preocupe, isso será corrigido automaticamente pela instalação)*
    * Escolha **2) Enable/Disable Diretta daemon** e habilite-o.
    * Escolha **3) Set Ethernet interface**. É crítico selecionar `end0`, a interface para o link ponto a ponto.
        ```text
        ?3
        Your available Ethernet interfaces are: end0  enu1
        Please type the name of your preferred interface:
        end0
        ```
    * Escolha **4) Edit configuration** apenas se precisar fazer alterações avançadas. As etapas anteriores devem ser suficientes; no entanto, aqui estão algumas configurações ajustadas que você pode querer experimentar:
        ```text
        ScanOnlineStop=enable
        InfoCycle=80000
        FlexCycle=disable
        CycleTime=800
        periodMin=16
        periodSizeMin=2048
        ```

    * Se você quiser apenas instalar os parâmetros ajustados acima, pode usar este bloco de comandos:
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
    * Escolha **7) Exit**. Siga as instruções para voltar ao terminal

7.  Criar uma substituição para fazer o serviço Diretta reiniciar automaticamente em caso de falha
    ```bash
    sudo mkdir -p /etc/systemd/system/diretta_alsa.service.d
    cat <<'EOT' | sudo tee /etc/systemd/system/diretta_alsa.service.d/restart.conf
    [Service]
    Restart=on-failure
    RestartSec=5
    EOT
    ```

---

### 9. Etapas Finais e Integração com o Roon

1.  Execute `menu` se você tiver saído para o terminal após a etapa anterior, caso contrário, vá para o **Main menu**.

2.  **Instalar o Roon Bridge (no Host):** Se você usa o Roon, execute as seguintes etapas no **Host Diretta**:
    * Execute `menu`.
    * Selecione **INSTALL/UPDATE menu**.
    * Selecione **INSTALL/UPDATE Roonbridge**.
    * A instalação prosseguirá. A instalação pode levar um ou dois minutos.

3.  **Habilitar o Roon Bridge (no Host):**
    * Selecione **Audio menu** a partir do Main menu.
    * Selecione **SHOW audio service**.
    * Se não vir o **roonbridge** sob os serviços ativados, selecione **ROONBRIDGE enable/disable**.

4.  **Reiniciar Ambos os Dispositivos:** Para um início limpo, reinicie tanto o Target quanto o Host, nessa ordem:
    ```bash
    sudo sync && sudo reboot
    ```

5.  **Configurar o Roon:**
    * Abra o Roon no seu dispositivo de controle.
    * Vá em `Settings` -> `Audio`.
    * Sob `diretta-host`, você deverá ver seu dispositivo. O nome será baseado no seu DAC.
    * Clique em `Enable`, dê um nome e você estará pronto para reproduzir música!

Seu link Diretta dedicado agora está totalmente configurado para uma reprodução de áudio pura e isolada.
**Nota:** A zona "Limited" para teste do Diretta Target desaparecerá do Roon após seis minutos de reprodução de música em alta resolução. Isso é normal. Nesse ponto, você precisará adquirir uma licença para o Diretta Target. O custo atualmente é de €100 e a ativação pode levar até 48 horas para ser concluída. Você receberá dois e-mails da equipe do Diretta. O primeiro é o seu recibo; o segundo, a sua notificação de ativação. Assim que receber o e-mail de ativação, reinicie o computador Target para aplicar a ativação.

> ---
> ### ✅ Ponto de Controle: Verificar seu Sistema Central
>
> Seu sistema core Diretta e Roon deve estar totalmente funcional agora. Para verificar todos os serviços e conexões, por favor, prossiga para o [**Apêndice 5**](#14-ap%C3%AAndice-5-verifica%C3%A7%C3%B5es-de-sa%C3%BAde-do-sistema) e execute o comando universal de **Verificação de Saúde do Sistema** em ambos o Host e o Target.
>
> ---

---

## 10. Apêndice 1: Controle de Ventoinha Argon ONE Opcional
Se você decidiu usar um gabinete Argon ONE para o seu Raspberry Pi, o script do instalador padrão assume que você está executando um SO Debian. No entanto, o Audiolinux é baseado no Arch Linux, então você terá que seguir estas etapas.

Se você estiver usando gabinetes Argon ONE tanto para o Host quanto para o Target Diretta, precisará executar estas etapas em ambos os computadores.

### Passo 1: Pular o script argon1.sh do manual
O manual diz para baixar o script `argon1.sh` de `download.argon40.com` e passá-lo para o `bash`. Isso não funcionará no Audiolinux, pois o script assume um SO baseado em Debian, então pule esta etapa e siga as etapas abaixo.

### Passo 2: Configurar o seu sistema:
Esses comandos ativarão a interface I2C e adicionarão o `dtoverlay` específico para o gabinete Argon ONE. O script primeiro tenta descomentar o parâmetro `i2c_arm` se ele estiver comentado e, em seguida, adiciona o overlay `argonone` se ele estiver ausente, evitando erros e entradas duplicadas.
```bash
BOOT_CONFIG="/boot/config.txt"
I2C_PARAM="dtparam=i2c_arm=on"

# --- Enable I2C by uncommenting the line if it exists ---
if grep -q -F "#$I2C_PARAM" "$BOOT_CONFIG"; then
  echo "Ativando o parâmetro I2C..."
  sudo sed -i -e "s/^#\($I2C_PARAM\)/\1/" "$BOOT_CONFIG"
fi
```

### Passo 3: Configurar as permissões do udev
```bash
cat <<'EOT' | sudo tee /etc/udev/rules.d/99-i2c.rules
KERNEL=="i2c-[0-9]*", MODE="0666"
EOT
```

### Passo 4: Instalar o Pacote Argon One
```bash
yay -S argonone-c-git
```

**Nota:** Se o comando acima falhar com erros de compilador, você pode tentar este procedimento manual para corrigir e instalar o pacote:
```bash
# Clonar o repositório do pacote
git clone https://aur.archlinux.org/argonone-c-git.git
cd argonone-c-git

# Baixar o código-fonte sem compilar
makepkg -o

# Aplicar patch para corrigir erro de compilação com GCC 14+
sed -i 's/_timer_thread()/_timer_thread(void *args)/g' src/argonone-c-git/src/event_timer.c

# Compilar e instalar usando o código-fonte patcheado
makepkg -e -i --noconfirm

# Limpar
cd ..
rm -rf argonone-c-git
```

### Passo 5: Mudar o gabinete Argon ONE de controle de hardware para software
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

### Passo 6: Habilitar o Serviço
```bash
# Recarregar o gerenciador do systemd para ler a nova configuração
sudo systemctl daemon-reload

# Habilitar o serviço para iniciar na inicialização
sudo systemctl enable argononed.service
```

### Passo 7: Reiniciar
Por fim, reinicie o seu Raspberry Pi para que todas as alterações tenham efeito (Target primeiro, depois o Host):
```bash
sudo sync && sudo reboot
```

Agora, a ventoinha será controlada pelo daemon, e o botão de energia terá funcionalidade total.

### Passo 8: Verificar o serviço
```bash
systemctl status argononed.service
journalctl -u argononed.service -b
```

### Passo 9: Revisar o Modo e as Configurações da Ventoinha:
Para ver os valores de configuração atuais, execute o seguinte comando:
```bash
sudo argonone-cli --decode
```

Para ajustar esses valores, você deve criar um arquivo de configuração. Use estes valores para começar:
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

Reinicie o serviço para aplicar os novos valores de configuração:
```bash
sudo systemctl restart argononed.service
echo ""
echo "Valores de ventoinha atualizados:"
sleep 5
sudo argonone-cli --decode
```

Agora, sinta-se à vontade para ajustar os valores conforme necessário, seguindo as etapas acima.

---

## 11. Apêndice 2: Controle Remoto IR Opcional

Este guia fornece instruções para instalar e configurar um controle remoto IR para controlar o Roon. A configuração é dividida em duas partes.

  * **Parte 1** cobre a configuração específica do hardware. Você escolherá **uma** das duas opções, dependendo se está usando o receptor USB Flirc ou o receptor integrado do gabinete Argon One.
  * **Parte 2** cobre a configuração do software para o script de controle `roon-ir-remote`, que é idêntica para ambas as opções de hardware.

**Nota:** Você executará estas etapas _apenas_ no Host Diretta. O Target não deve ser usado para retransmitir comandos de controle remoto IR para o Roon Server.

---

### **Parte 1: Configuração de Hardware do Receptor IR**

*Siga a seção correspondente ao hardware que você está usando.*

#### **Opção 1: Configuração do Receptor IR USB Flirc**

1.  **Comprar e Programar o Dispositivo Flirc:**
    Você precisará do Receptor IR USB Flirc, que pode ser adquirido em seu site: [https://flirc.tv/products/flirc-usb-receiver](https://flirc.tv/products/flirc-usb-receiver)

    O dispositivo Flirc deve ser programado em um computador desktop usando o software Flirc GUI.

      * Conecte o Flirc ao seu computador desktop e abra a GUI do Flirc.
      * Vá em `Controllers` e selecione `Full Keyboard`.
      * Programe as teclas necessárias para o script (por exemplo, KEY_UP, KEY_DOWN, KEY_ENTER, etc.) clicando na tecla na GUI e pressionando o botão correspondente no seu controle remoto físico.
      * Uma vez programado, conecte o Flirc no **Host Diretta**.

2.  **Testar o Dispositivo Flirc:**
    Verifique se o Raspberry Pi reconhece o Flirc como um teclado.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Selecione o dispositivo "Flirc" no menu. Quando você pressionar botões no seu controle remoto, deverá ver os eventos de teclado impressos na tela.

3.  Pule para a [Parte 2: Configuração do Software do Script de Controle](#parte-2-configura%C3%A7%C3%A3o-do-software-do-script-de-controle)

---

#### **Opção 2: Configuração do Controle Remoto IR Argon One**

1.  **Habilitar o Hardware do Receptor IR:**
    Você deve habilitar o overlay de hardware para o receptor IR do gabinete Argon One.

      * Este comando adicionará com segurança o overlay de hardware necessário ao seu arquivo `/boot/config.txt`, verificando primeiro para garantir que não seja adicionado mais de uma vez.
        ```bash
        BOOT_CONFIG="/boot/config.txt"
        IR_CONFIG="dtoverlay=gpio-ir,gpio_pin=23"

        # Adicionar overlay de controle remoto IR se ainda não estiver lá
        if ! sed 's/#.*//' $BOOT_CONFIG | grep -q -F "$IR_CONFIG"; then
          echo "Ativando o Receptor IR do Argon One..."
          sudo sed -i "/# Uncomment this to enable infrared communication./a $IR_CONFIG" /boot/config.txt
        else
          echo "Receptor IR do Argon One já ativado."
        fi
        ```
      * É necessária uma reinicialização para que a alteração de hardware entre em vigor.
        ```bash
        sudo sync && sudo reboot
        ```

2.  **Instalar Ferramentas de IR e Habilitar Protocolos:**
    Instalar o `ir-keytable`
    ```bash
    sudo pacman -S --noconfirm v4l-utils
    ```

3.  **Capturar os Scancodes dos Botões:**
     Habilite todos os protocolos do kernel para que ele possa decodificar os sinais do seu controle remoto. Execute a ferramenta de teste para ver o scancode exclusivo de cada botão do controle remoto.
    ```bash
    sudo ir-keytable -p all
    sudo ir-keytable -t
    ```

    Pressione cada botão que deseja usar e anote seu scancode a partir da saída do evento `MSC_SCAN` (por exemplo, `value ca`). Pressione `Ctrl+C` quando terminar.

4.  **Criar o Arquivo de Keymap:**
    Este arquivo mapeia os scancodes para nomes de teclas padrão.

      * Crie um novo arquivo de keymap:
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
      * Se os scancodes no arquivo de exemplo acima não corresponderem aos que você registrou, edite o arquivo (`sudo nano /etc/rc_keymaps/argon.toml`) e altere-os para corresponder.

5.  **Criar um Serviço systemd para Carregar o Keymap:**
    Este serviço carregará seu keymap automaticamente na inicialização.

    Crie um novo arquivo de serviço e habilite o serviço:
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

6.  **Testar o Dispositivo de Entrada:**
    Verifique se o sistema está recebendo eventos de teclado do controle remoto IR.

    ```bash
    sudo pacman -S --noconfirm evtest
    sudo evtest
    ```

    Selecione o dispositivo `gpio_ir_recv`. Quando você pressionar os botões no controle remoto, deverá ver os eventos de tecla correspondentes.
    Digite `CTRL-C` quando terminar de testar.

---

### **Parte 2: Configuração do Software do Script de Controle**

*Após configurar o seu hardware na Parte 1, siga estas etapas para instalar e configurar o script de controle em Python.*

### **Passo 1: Adicionar `audiolinux` ao grupo `input`**
Isso é necessário para que a conta `audiolinux` tenha acesso aos eventos do receptor do controle remoto.
```bash
sudo usermod --append --groups input audiolinux
```
Faça logout e login novamente para que essa alteração entre em vigor. Você pode verificar com este comando:
```bash
echo ""
echo ""
echo "Verificando suas associações de grupo:"
echo "\$ groups"
groups
echo ""
echo "Acima, você deve ver:"
echo "audiolinux realtime video input audio wheel"
```

---

### **Passo 2: Instalar o Python via `pyenv`**

Instale o `pyenv` e a versão estável mais recente do Python.

```bash
# Instalar dependências de compilação
sudo pacman -Syu --noconfirm
sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

# Instalar o pyenv apenas se ainda não estiver instalado
if [ ! -d "$HOME/.pyenv" ]; then
  echo "--- Instalando o pyenv ---"
  curl -fsSL https://pyenv.run | bash
else
  echo "--- O pyenv já está instalado. Pulando a instalação. ---"
fi

# Configurar o shell para o pyenv
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

# Carregar o arquivo para disponibilizar o pyenv no shell atual
. ~/.bashrc

# Instalar e configurar a versão mais recente do Python apenas se ainda não estiver instalada
PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')

if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
    # Obter a memória total em MB
    TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

    if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- A RAM física é de ${TOTAL_MEM}MB. Limitando a 1 núcleo para evitar travamento. ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
    else
        echo "--- A RAM física é de ${TOTAL_MEM}MB. Prosseguindo com compilação paralela. ---"
    fi

    echo "--- Instalando o Python ${PYVER}. Isso levará alguns minutos... ---"
    pyenv install "$PYVER"
    [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
else
    echo "--- O Python ${PYVER} já está instalado. ---"
fi

pyenv global "$PYVER"
```

**Nota:** É normal que a parte `Installing Python-3.14.5...` leve cerca de 10 minutos, pois compila o Python a partir do código-fonte. Não desista! Sinta-se à vontade para relaxar com uma bela música usando sua nova zona Diretta no Roon enquanto espera. Ela deve estar disponível enquanto o Python está sendo instalado no Host.

---

### **Passo 3: Baixar o Repositório de Software `roon-ir-remote`**

Clone o repositório do script e obtenha um patch para lidar corretamente com os keycodes por nome em vez de por número.

```bash
cd
# Clonar o repositório se ele não existir, caso contrário, atualizá-lo
if [ ! -d "roon-ir-remote" ]; then
  git clone https://github.com/dsnyder0pc/roon-ir-remote.git
else
  (cd roon-ir-remote && git pull)
fi
```

---

### **Passo 4: Criar o Arquivo de Configuração de Ambiente do Roon**

Configure o script com os detalhes do seu Roon. **Nota:** Os códigos de `event_mapping` devem corresponder aos nomes de teclas que você definiu na configuração do seu hardware (`KEY_ENTER`, `KEY_VOLUMEUP`, etc.).

```bash
bash <<'EOF'
# --- Início do Script ---

# Obter a Zona do Roon e armazená-la em uma variável
echo "Insira o nome da sua zona do Roon."
echo "IMPORTANTE: Isso deve corresponder exatamente ao nome da zona no aplicativo Roon (diferencia maiúsculas de minúsculas)."
# Esta linha é a correção: < /dev/tty diz ao read para usar o terminal
read -rp "Insira o nome da sua Zona do Roon: " MY_ROON_ZONE < /dev/tty

# Detectar se o mapeamento do Flirc/Teclado é necessário
if [ -f "/etc/systemd/system/ir-keymap.service" ]; then
    VOL_UP_CODE="KEY_VOLUMEUP"
    VOL_DOWN_CODE="KEY_VOLUMEDOWN"
    echo "--- Receptor IR padrão detectado. Usando KEY_VOLUMEUP/DOWN. ---"
else
    VOL_UP_CODE="KEY_UP"
    VOL_DOWN_CODE="KEY_DOWN"
    echo "--- Adaptador Flirc/HID detectado. Usando KEY_UP/DOWN para volume. ---"
fi

# Garantir que o diretório de destino exista
mkdir -p roon-ir-remote

# Criar o arquivo de configuração usando um Here Document
# A variável agora será substituída corretamente
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

# --- End of Script ---
EOF
```

---

### **Passo 5: Preparar e Testar o `roon-ir-remote`**

Instale as dependências do script em um ambiente virtual e execute-o pela primeira vez.

```bash
cd ~/roon-ir-remote
# Criar o ambiente virtual apenas se ainda não existir
if ! pyenv versions --bare | grep -q "^roon-ir-remote$"; then
  echo "--- Criando ambiente virtual 'roon-ir-remote' ---"
  pyenv virtualenv roon-ir-remote
else
  echo "--- o ambiente virtual 'roon-ir-remote' já existe ---"
fi
pyenv activate roon-ir-remote
pip3 install --upgrade pip
pip3 install -r requirements.txt

python roon_remote.py
```

A primeira vez que você executar o script, deverá **autorizar a extensão no Roon** acessando `Settings` -> `Extensions`.

Com a música tocando na sua nova zona Diretta Roon, aponte o seu controle remoto IR diretamente para o computador Host Diretta e pressione o botão Play/Pause (pode ser o botão central do controle de 5 direções). Tente também Próximo e Anterior. Se não estiverem funcionando, verifique a janela do terminal para ver se há mensagens de erro. Quando terminar de testar, digite `CTRL-C` para sair.

---

### **Passo 6: Criar um Serviço systemd**

Crie um serviço para executar o script automaticamente em segundo plano.

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

# Habilitar e iniciar o serviço
sudo systemctl daemon-reload
sudo systemctl enable --now roon-ir-remote.service

# Verificar o status
sudo systemctl status roon-ir-remote.service
```

---

### **Passo 7: Acompanhar os logs por um momento:**
```bash
journalctl -b -u roon-ir-remote.service -f
```

Digite `CTRL-C` assim que estiver satisfeito que as coisas estão funcionando como esperado.

---

### **Passo 8: Instalar o script `set-roon-zone`**
É bom ter um script que você possa usar para atualizar o nome da zona do Roon mais tarde, se necessário. Veja como instalá-lo:
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/set-roon-zone
sudo install -m 0755 set-roon-zone /usr/local/bin/
rm set-roon-zone
```

Para usá-lo, basta fazer login no computador Host Diretta e digitar:
```bash
set-roon-zone
```
Siga as instruções para inserir o novo nome para sua Zona do Roon. Pode ser necessário digitar a senha do root para que as alterações entrem em vigor.

**Nota: Uma Maneira Melhor de Configurar a Zona**
Embora este script funcione perfeitamente, o método recomendado para alterar a Zona do Roon é usar o aplicativo web AnCaolas Link System Control, detalhado no [Apêndice 4](#13-ap%C3%AAndice-4-interface-web-opcional-de-controle-do-sistema). A interface web fornece uma página dedicada para visualizar e editar o nome da zona a partir do seu telefone ou navegador.

### **Passo 9: Aproveite! 📈**

> ---
> ### ✅ Ponto de Controle: Verificar sua Configuração de Controle Remoto IR
>
> O hardware e o software do seu Controle Remoto IR devem estar configurados agora. Para verificar a configuração, prossiga para o [**Apêndice 5**](#14-ap%C3%AAndice-5-verifica%C3%A7%C3%B5es-de-sa%C3%BAde-do-sistema) e execute o comando de **Verificação de Saúde do Sistema** universal no Host Diretta.
>
> ---

Seu controle remoto IR agora deve controlar o Roon. Aproveite!

---

## 12. Apêndice 3: Modo Purista Opcional
Existe uma atividade mínima de rede e de segundo plano no computador Diretta Target que não esteja relacionada à reprodução de música usando o protocolo Diretta. No entanto, alguns usuários preferem tomar medidas extras para reduzir a possibilidade de tal atividade. Já estamos no limite extremo do desempenho de áudio, então por que não?

---
> AVISO CRÍTICO: Apenas para o Target Diretta
>
> O script `purist-mode` e todas as instruções deste apêndice foram projetados exclusivamente para o Target Diretta.
>
> NÃO instale ou execute este script no Host Diretta. Fazer isso cortará a conexão do Host com a sua rede principal, tornando-o inacessível e incapaz de se comunicar com o seu Roon Core ou serviços de streaming. Isso tornará todo o sistema inoperante até que você consiga acesso físico ao console (com teclado e monitor físicos) para reverter as alterações.
---

### Passo 1: Instalar o script purist-mode (apenas no computador Target Diretta)
```bash
curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode
sudo install -m 0755 purist-mode /usr/local/bin
rm purist-mode

# Script for showing Purist Mode status on login
cat <<'EOT' | sudo tee /etc/profile.d/purist-status.sh
#!/bin/sh
BACKUP_FILE="/etc/nsswitch.conf.purist-bak"

if [ -f "$BACKUP_FILE" ]; then
    echo -e '\n\e[1;32m✅ O Modo Purista está ATIVO.\e[0m Sistema otimizado para a máxima qualidade de som.'
else
    echo -e '\n\e[1;33m⚠️ CUIDADO: O Modo Purista está DESATIVADO.\e[0m A atividade de segundo plano pode afetar a qualidade do som.'
fi
EOT
```

Para executá-lo, basta fazer login no Target Diretta e digitar `purist-mode`:
```bash
purist-mode
```

Por exemplo:
```text
[audiolinux@diretta-target ~]$ purist-mode
Este script requer privilégios de sudo. Você pode ser solicitado a digitar uma senha.
🚀 Ativando o Modo Purista...
  -> Parando o serviço de sincronização de tempo (chronyd)...
  -> Desabilitando consultas DNS...
  -> Substituindo o gateway por uma rota blackhole de alta prioridade...

✅ O Modo Purista está ATIVO.
```

Ouça por um tempo para ver se prefere o som (ou a paz de espírito).

---

### Passo 2: Habilitar o Modo Purista por Padrão

Se você decidiu que prefere o som com o Modo Purista ativado, torne-o o padrão após cada reinicialização.

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

### Passo 3: Instalar um wrapper em torno do comando `menu`
Muitas funções no AudioLinux requerem acesso à Internet. Para manter as coisas funcionando conforme o esperado, adicione um wrapper em torno do comando `menu` que desativa o modo Purista enquanto você estiver usando o menu, ativando-o novamente quando você sair para o terminal.

```bash
if grep -q menu_wrapper ~/.bashrc; then
  :
else
  echo ""
  echo "Adicionando um wrapper em torno do comando menu"
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

### Entendendo os Estados do Modo Purista

O sistema do Modo Purista foi projetado para ser flexível, permitindo que você o controle manualmente ou que ele seja ativado automaticamente após a inicialização do sistema. Ele opera em dois estados principais:

  * **Desativado (Modo Padrão):**
    Este é o estado normal e totalmente funcional do Diretta Target. O gateway de rede está ativo, todos os serviços (`chronyd`, `argononed`) estão em execução e o dispositivo funciona sem restrições.

  * **Ativo (Modo Purista):**
    Este é o estado otimizado para audição crítica. O gateway de rede é desativado para evitar tráfego de internet e serviços de segundo plano não essenciais (incluindo a ventoinha do Argon ONE) são parados para minimizar qualquer interferência potencial no sistema.

Esses estados são gerenciados de duas maneiras: **automaticamente** na inicialização e **manualmente** via linha de comando.

#### Controle Automático (Na Inicialização)

O processo de inicialização foi projetado para ser seguro e previsível, com uma mudança automatizada opcional para o Modo Purista.

1.  **Reversão Obrigatória na Inicialização:** Independentemente do estado em que estava quando foi desligado, o Diretta Target **sempre** inicializa no **Modo Padrão** primeiro. Este é um recurso crítico que garante que serviços essenciais, como a sincronização de tempo de rede, possam ser executados corretamente.

2.  **Auto-Ativação Opcional:** Se você ativou o recurso automático, o sistema aguardará 60 segundos após a inicialização e, em seguida, mudará automaticamente para o **Modo Purista**. Isso fornece uma experiência de "configurar e esquecer" para usuários que sempre preferem ouvir no estado otimizado.

#### Controle Manual (Uso Interativo)

Você tem controle interativo total sobre o sistema a qualquer momento.

  * Para **ativar manualmente** o Modo Purista para uma sessão de audição, faça login no computador Target Diretta e execute:

    ```bash
    purist-mode
    ```

  * Para **desativar manualmente** o Modo Purista e retornar à operação padrão, execute:

    ```bash
    purist-mode --revert
    ```

  * Para controlar o **comportamento automático de inicialização**, use os aliases de conveniência no Diretta Target:

    ```bash
    # This enables the 60-second auto-activation on the next boot
    purist-mode-auto-enable

    # This disables the auto-activation on the next boot
    purist-mode-auto-disable
    ```

---

## 13. Apêndice 4: Interface Web Opcional de Controle do Sistema

Este apêndice fornece instruções para instalar um aplicativo simples baseado na web no Host Diretta. Este aplicativo fornece uma interface fácil de usar, acessível a partir de um telefone ou tablet, para gerenciar os principais recursos do seu sistema Diretta, incluindo o Modo Purista no Target e as configurações de integração do Controle Remoto IR do Roon no Host.

> **AVISO CRÍTICO: Realize estas etapas com cuidado.**
> Esta configuração envolve a criação de um novo usuário e a modificação de configurações de segurança. Siga as instruções precisamente para garantir que o sistema permaneça seguro e funcional.

A configuração é dividida em duas partes: primeiro, configuramos o **Diretta Target** para aceitar comandos com segurança e, segundo, instalamos o aplicativo web no **Host Diretta**. No entanto, preste atenção porque alternamos entre hosts com frequência.

---

### **Parte 1: Configuração do Diretta Target**

No **Diretta Target**, criaremos um novo usuário com permissões muito limitadas. Este usuário só poderá executar os comandos específicos necessários para gerenciar o Modo Purista.

1.  **Acesse o Diretta Target via SSH:**
    ```bash
    ssh diretta-target
    ```

2.  **Criar um Novo Usuário para o Aplicativo:**
    Este comando cria um novo usuário chamado `purist-app` e seu diretório home. Um shell válido é necessário para que os comandos SSH não interativos funcionem.
    ```bash
    sudo useradd --create-home --shell /bin/bash purist-app
    ```

3.  **Criar Scripts de Comando Seguros:**
    Criaremos quatro pequenos scripts dedicados que são as *únicas* ações que o aplicativo web tem permissão de realizar. Esta é uma etapa de segurança crítica.
    ```bash
    # Script to get the current status, including license state
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

    # Script to toggle Purist Mode
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

    # Script to toggle the auto-start service
    cat <<'EOT' | sudo tee /usr/local/bin/pm-toggle-auto
    #!/bin/bash
    if systemctl is-enabled --quiet purist-mode-auto.service; then
      systemctl disable --now purist-mode-auto.service
    else
      systemctl enable purist-mode-auto.service
    fi
    EOT

    # Create the script to restart the Diretta service
    cat <<'EOT' | sudo tee /usr/local/bin/pm-restart-target
    #!/bin/bash
    # Restarts the Diretta ALSA Target service.
    # This script is intended to be called via sudo by the purist-app user.
    /usr/bin/systemctl restart diretta_alsa_target.service
    EOT

    # Create the script to fetch the Diretta License URL
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

    # Create script to set the link speed
    cat <<'EOT' | sudo tee /usr/local/bin/pm-set-link
    #!/bin/bash
    # Profile script to enforce Target physical link boundaries
    # Refactored using explicit advertisement masks to prevent hardware deadlocks

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

    # Tornar os novos scripts executáveis
    sudo chmod -v +x /usr/local/bin/pm-*
    ```

4.  **Conceder Permissões de Sudo:**
    Esta etapa permite que o usuário `purist-app` execute nossos quatro novos scripts com privilégios de root e sem a necessidade de um terminal interativo.
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

5.  **Preencher o Arquivo de Cache de Licença do Diretta no Momento da Inicialização**
    A busca pela URL de Licença do Diretta requer uma conexão com a Internet. Se tivermos o Modo Purista ativado por padrão, o Target nunca poderá buscar a URL. No entanto, no momento da inicialização, temos o Modo Purista desativado por 60 segundos para acertar o relógio e verificar a ativação da Licença do Diretta. Podemos usar essa janela de tempo para buscar a URL também.
    ```bash
    # Download the script, set correct permissions, and place it in the system path
    curl -LO https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/create-diretta-cache.sh
    sudo install -m 0755 create-diretta-cache.sh /usr/local/bin/
    rm create-diretta-cache.sh

    # Create a service for populating the license status cache
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

    # Recarregar o systemd para aplicar a configuração drop-in atualizada
    sudo rm -rf /etc/systemd/system/purist-mode-revert-on-boot.service.d
    sudo systemctl daemon-reload
    sudo systemctl enable diretta-cache.service

    # Prosseguir e executar o script manualmente uma vez
    sudo /usr/local/bin/create-diretta-cache.sh
    ls -l /tmp/diretta_license_url.cache
    ```

---

### **Parte 2: Configuração do Host Diretta**

Agora, no **Host Diretta**, realizaremos todas as etapas para instalar e configurar o aplicativo web. Você deve estar logado como o usuário `audiolinux` durante toda esta seção.

1.  **Acesse o Host Diretta via SSH:**
    ```bash
    ssh diretta-host
    ```

2.  **Gerar uma Chave SSH Dedicada:**
    Isso cria um novo par de chaves SSH especificamente para o aplicativo web. Ele não terá frase secreta (passphrase).
    ```bash
    ssh-keygen -t ed25519 -f ~/.ssh/purist_app_key -N "" -C "purist-app-key"
    ```

3.  **Configurar SSH e Copiar a Chave para o Target:**
    Esta etapa criará uma configuração SSH e copiará com segurança a chave pública para o Target.
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

    # Copiar a chave pública para o diretório home do Target
    echo "--> Copiando a chave pública para o Target..."
    scp -o StrictHostKeyChecking=accept-new ~/.ssh/purist_app_key.pub diretta-target:
    ```

4.  **Autorizar a Chave no Target:**
    ```bash
    ssh diretta-target

    ```

    Uma vez logado no Target, execute este script para configurar a chave para o usuário 'purist-app'
    ```bash
    echo "--> Executando o script de configuração no Target..."
    set -e
    # Ler a chave pública do arquivo que acabamos de copiar
    PUB_KEY=$(cat purist_app_key.pub)

    # Garantir que o diretório .ssh exista e tenha as permissões corretas
    sudo mkdir -p /home/purist-app/.ssh
    sudo chmod 0700 /home/purist-app/.ssh

    # Criar o arquivo authorized_keys com as restrições de segurança exigidas
    echo "command=\"sudo \$SSH_ORIGINAL_COMMAND\",from=\"172.20.0.1\",no-port-forwarding,no-x11-forwarding,no-agent-forwarding,no-pty ${PUB_KEY}" | sudo tee /home/purist-app/.ssh/authorized_keys > /dev/null

    # Definir proprietário e permissões finais
    sudo chown -R purist-app:purist-app /home/purist-app/.ssh
    sudo chmod 0600 /home/purist-app/.ssh/authorized_keys

    # Limpar o arquivo de chave pública copiado
    rm purist_app_key.pub

    echo "✅ A chave SSH foi autorizada com sucesso no Target."
    ```

5.  **Testar Manualmente os Comandos Remotos (Recomendado):**
    Antes de iniciar o aplicativo web, teste os comandos remotos somente leitura a partir do terminal do **Host Diretta** para confirmar que o backend está funcionando.
    ```bash
    # Testar o comando de status (deve retornar uma string JSON)
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-status'

    # Testar o comando para buscar o status da licença.
    ssh -i ~/.ssh/purist_app_key purist-app@diretta-target '/usr/local/bin/pm-get-license-url'
    ```

6.  **Instalar o Python via pyenv** no **Host Diretta** (sinta-se à vontade para pular esta etapa se já fez isso para fazer o Controle Remoto IR funcionar)
    Instale o `pyenv` e a versão estável mais recente do Python.
    ```bash
    # Instalar dependências de compilação
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm --needed base-devel git zlib bzip2 xz expat libffi openssl ncurses readline util-linux db gdbm sqlite vim jq

    # Instalar o pyenv apenas se ainda não estiver instalado
    if [ ! -d "$HOME/.pyenv" ]; then
      echo "--- Instalando pyenv ---"
      curl -fsSL https://pyenv.run | bash
    else
      echo "--- o pyenv já está instalado. Pulando a instalação. ---"
    fi

    # Configurar o shell para o pyenv
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

    # Carregar o arquivo para disponibilizar o pyenv no shell atual
    . ~/.bashrc

    # Instalar e configurar a versão mais recente do Python apenas se ainda não estiver instalada
    PYVER=$(pyenv install --list | grep -E '^\s{2}3\.[0-9]+\.[0-9]+$' | tail -n 1 | tr -d ' ')
    if ! pyenv versions --bare | grep -q "^${PYVER}$"; then
      # Obter a memória total em MB
      TOTAL_MEM=$(awk '/^MemTotal:/ {print int($2/1024)}' /proc/meminfo)

      if [ "$TOTAL_MEM" -lt 1900 ]; then
        echo "--- A RAM física é de ${TOTAL_MEM}MB. Limitando a 1 núcleo para evitar travamento. ---"
        export MAKE_OPTS="-j1"
        export MAKEFLAGS="-j1"
        mkdir -p "$HOME/pyenv_build_scratch"
        export TMPDIR="$HOME/pyenv_build_scratch"
      else
        echo "--- A RAM física é de ${TOTAL_MEM}MB. Prosseguindo com compilação paralela. ---"
      fi

      echo "--- Instalando o Python ${PYVER}. Isso levará alguns minutos... ---"
      pyenv install $PYVER
      [ -n "$TMPDIR" ] && [ -d "$TMPDIR" ] && rm -rf "$TMPDIR"
    else
      echo "--- O Python ${PYVER} já está instalado. ---"
    fi

    pyenv global $PYVER
    ```

    **Nota:** É normal que a parte `Installing Python-3.14.5...` leve cerca de 10 minutos, pois compila o Python a partir do código-fonte. Não desista! Sinta-se à vontade para relaxar com uma bela música usando sua nova zona Diretta no Roon enquanto espera. Ela deve estar disponível enquanto o Python está sendo instalado no Host.

7.  **Instalar o Avahi e as Dependências do Python no Host Diretta:**

    **Nota: OPCIONAL** - Se você tiver mais de um Host Diretta em sua rede, certifique-se de que eles tenham nomes exclusivos. Você pode usar um comando como o seguinte para renomear este antes de prosseguir:

    ```bash
    # Opcionalmente renomear o Host Diretta se esta for a sua segunda montagem na mesma rede
    sudo hostnamectl set-hostname diretta-host2
    ```

    Esta etapa é executada no **Host Diretta**. Ela instala o daemon do Avahi e usa um arquivo `requirements.txt` para instalar o Flask em um ambiente virtual dedicado.
    ```bash
    # Instalar o Avahi para resolução de nomes .local
    sudo pacman -Syu --noconfirm
    sudo pacman -S --noconfirm avahi

    # Encontrar dinamicamente o nome da interface Ethernet USB (ex., enp... ou enu1...)
    USB_INTERFACE=$(ip -o link show | awk -F': ' '/en[pu]/{print $2}')

    # Criar uma substituição de configuração para o Avahi para isolá-lo na interface USB
    echo "--- Configurando o Avahi para usar a interface: $USB_INTERFACE ---"
    sudo mkdir -p /etc/avahi/avahi-daemon.conf.d
    cat <<EOT | sudo tee /etc/avahi/avahi-daemon.conf.d/interface-scoping.conf
    [server]
    allow-interfaces=$USB_INTERFACE
    deny-interfaces=end0
    EOT

    # Habilitar e iniciar o daemon do Avahi
    sudo systemctl enable --now avahi-daemon.service

    # Criar o diretório da aplicação e o arquivo de requisitos
    mkdir -p ~/purist-mode-webui
    echo "Flask" > ~/purist-mode-webui/requirements.txt

    # Criar um ambiente virtual e instalar dependências
    echo "--- Configurando o ambiente Python para a Interface Web ---"
    # Criar o ambiente virtual apenas se ainda não existir
    if ! pyenv versions --bare | grep -q "^purist-webui$"; then
      echo "--- Criando ambiente virtual 'purist-webui' ---"
      pyenv virtualenv purist-webui
    else
      echo "--- o ambiente virtual 'purist-webui' já existe ---"
    fi
    pyenv activate purist-webui
    pip install -r ~/purist-mode-webui/requirements.txt
    pyenv deactivate
    ```

8.  **Instalar o Aplicativo Flask:**
    Baixe o script Python diretamente do GitHub para o diretório da aplicação no **Host Diretta**.
    ```bash
    curl -L https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/purist-mode-webui.py -o ~/purist-mode-webui/app.py
    ```

9. **Conceder Capacidade de Ligação de Porta (Port-Binding)**
    Precisamos dar permissão ao executável Python para se ligar à porta 80 no Host Diretta para que nosso aplicativo web possa iniciar.
    ```bash
    # Instalar o pacote que fornece o comando 'setcap'
    sudo pacman -S --noconfirm --needed libcap

    # Encontrar o caminho real para o executável do Python, resolvendo todos os links simbólicos
    PYTHON_EXEC=$(readlink -f /home/audiolinux/.pyenv/versions/purist-webui/bin/python)

    # Conceder a capacidade de ligação de porta (port-binding) diretamente ao executável Python final
    echo "Aplicando capacidade ao arquivo real: ${PYTHON_EXEC}"
    sudo setcap 'cap_net_bind_service=+ep' "$PYTHON_EXEC"
    ```

10. **Conceder Permissões de Sudo no Host:**
    Esta etapa é crítica para permitir que o aplicativo web reinicie os serviços necessários relacionados ao Roon sem uma senha.
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

11. **Testar o Aplicativo Flask Interativamente:**
    Agora, execute o aplicativo a partir da linha de comando no **Host Diretta** para garantir que ele inicie corretamente.
    ```bash
    cd ~/purist-mode-webui
    pyenv activate purist-webui
    python app.py
    ```
    Você deverá ver uma saída indicando que o servidor Flask foi iniciado na porta **8080**. A partir de outro dispositivo, acesse [http://diretta-host.local:8080](http://diretta-host.local:8080). Se funcionar, retorne ao terminal SSH e pressione `Ctrl+C` para parar o servidor.

12. **Criar o Serviço do systemd:**
    Este serviço executará o aplicativo web automaticamente no **Host Diretta**, usando o executável Python correto de nosso ambiente virtual `pyenv`.
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

13. **Habilitar e Iniciar o Aplicativo Web:**
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl stop purist-webui.service
    sudo systemctl enable --now purist-webui.service
    ```

14. **Acompanhar os logs por um momento:**
    ```bash
    journalctl -b -u purist-webui.service -f
    ```

15. **Testar a interface web com a URL final:**
    Open a browser to [http://diretta-host.local](http://diretta-host.local) and watch the logs for any errors.

Digite `CTRL-C` assim que estiver satisfeito que as coisas estão funcionando como esperado.

---

### **Acessar a Interface Web**

Tudo pronto! Abra um navegador web no seu telefone, tablet ou computador conectado à mesma rede que o Host Diretta. Navegue até a página principal:

[http://diretta-host.local](http://diretta-host.local)

---
> **Uma Nota sobre Avisos de Segurança do Navegador**
> Ao visitar http://diretta-host.local pela primeira vez, seu navegador provavelmente exibirá um aviso de segurança informando que a conexão não é segura. Isso é esperado e seguro de contornar. O aviso aparece porque a conexão usa `HTTP` padrão em vez de `HTTPS` criptografado, uma escolha intencional para minimizar a sobrecarga de processamento no dispositivo de áudio. Como o aplicativo roda apenas em sua rede doméstica privada e não manipula dados confidenciais, você pode clicar com confiança em "Continuar para o site".
---

A partir da página principal, uma barra de navegação no topo o guará para os diferentes painéis de controle:

* **Home:** A página principal com links para as diferentes aplicações.

* **Purist Mode App:** Esta página contém os controles para alternar o Modo Purista e seu comportamento de inicialização automática no Target Diretta. Ela se atualiza automaticamente a cada 30 segundos para mostrar o status atual. Também contém o botão "Restart Services" (Reiniciar Serviços) para uso após a ativação da licença do Diretta.

* **IR Remote App:** Se você concluiu a configuração do controle remoto IR (Apêndice 2), este link aparecerá. Esta página fornece um formulário simples para visualizar e atualizar o nome da Zona do Roon que seu controle remoto controlará. Esta página não se atualiza automaticamente, então você pode levar o tempo que precisar para fazer suas edições.

### 🔗 Nota sobre a Funcionalidade Completa da Interface Web

Para desbloquear os recursos completos da Interface Web de Controle do Sistema — especificamente os ajustes de **Velocidade de Link** de rede e a alternância do modo **Super Purista** — você também deve concluir as configurações de hardware e serviço detalhadas no [**Apêndice 8: Velocidades Opcionais de Rede Purista**](#17-ap%C3%AAndice-8-velocidades-opcionais-de-rede-purista). A interface web depende diretamente dos scripts, flags e serviços subjacentes estabelecidos nessa seção para modificar e impor com sucesso os limites físicos de velocidade de link em sua conexão ponto a ponto.

> ---
> ### ✅ Ponto de Controle: Verificar sua Configuração da Interface Web
>
> A Interface Web do Modo Purista deve estar operacional agora. Para verificar todos os componentes deste recurso complexo, prossiga para o [**Apêndice 5**](#14-ap%C3%AAndice-5-verifica%C3%A7%C3%B5es-de-sa%C3%BAde-do-sistema) e execute o comando de **Verificação de Saúde do Sistema** universal no Host e no Target.
>
> ---

## 14. Apêndice 5: Verificações de Saúde do Sistema

Depois de concluir as seções principais deste guia, é uma boa ideia executar uma rápida verificação de garantia de qualidade (QA) para verificar se tudo está configurado corretamente.

Criamos um script inteligente que detecta automaticamente se você o está executando no **Host Diretta** ou no **Target Diretta** e realiza o conjunto apropriado de verificações.

### **Como Executar a Verificação**

No Host ou no Target, execute o seguinte comando único. Ele baixará e executará o script de QA, fornecendo um relatório detalhado do status do seu sistema.

```bash
curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/main/scripts/qa.sh | sudo bash
```

---

## 15. Apêndice 6: Ajuste Opcional de Desempenho em Tempo Real

As etapas a seguir são opcionais, mas recomendadas para usuários que buscam extrair o máximo desempenho absoluto de sua configuração Diretta. A estratégia, baseada nos conselhos do autor do AudioLinux, Piero, é criar o ambiente mais estável e eletricamente silencioso possível nos dispositivos Host e Target.

Isso é alcançado usando o **isolamento de CPU** para dedicar núcleos de processador específicos para tarefas de áudio, blindando-os do sistema operacional, e ajustando cuidadosamente as **prioridades em tempo real** para garantir que o caminho dos dados de áudio nunca seja interrompido.

> **Nota:** Este é um processo de ajuste avançado. Certifique-se de que seu sistema Diretta principal esteja totalmente funcional, concluindo as seções 1 a 9 do guia principal antes de prosseguir. O resfriamento adequado para ambos os dispositivos Raspberry Pi é essencial.

---

### **Parte 1: Otimizando o Diretta Target**

O objetivo para o Target é torná-lo um endpoint de áudio puro e de baixa latência. Isolaremos a aplicação Diretta em um único núcleo de CPU dedicado e daremos a ela uma prioridade em tempo real alta, mas não excessiva.

#### **Passo 6.1: Isolar um Núcleo de CPU para a Aplicação de Áudio**

Esta etapa dedica um núcleo de CPU exclusivamente à aplicação Diretta Target.

1.  Acesse o Diretta Target via SSH:
    ```bash
    ssh diretta-target
    ```
2.  Entre no sistema de menus do AudioLinux:
    ```bash
    menu
    ```
3.  Navegue até o menu **ISOLATED CPU CORES configuration** (em **SYSTEM menu**).

4.  Confirme se o isolamento de núcleos está desativado. Caso contrário, use a opção 3 para desativá-lo:
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

5.  Navegue de volta para o menu **ISOLATED CPU CORES configuration** (em **SYSTEM menu**). Siga as instruções exatamente como mostrado abaixo para isolar os **núcleos 2 e 3** e atribuir a aplicação Diretta a eles.
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

6.  Após a conclusão do processo, saia de volta para o terminal.

> **Uma Nota sobre Afinidade de IRQ Automática:** Você pode notar que o script relata que também isolou as IRQs de rede `end0` para o mesmo núcleo. Isso não é um bug, mas uma otimização inteligente. O script fixa automaticamente as interrupções de rede no mesmo núcleo da aplicação que usa a rede, criando o caminho de dados mais eficiente possível.

#### **Passo 6.2: Desativar o timer rtapp legado**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **Passo 6.3: Reiniciar para aplicar as alterações.**
```bash
sudo sync && sudo reboot
```

---

### **Parte 2: Otimizando o Host Diretta**

O objetivo para o Host é dar às threads de serviço do Diretta recursos de processamento dedicados, mas sem usar prioridades altas em tempo real. O isolamento de CPU é uma ferramenta mais poderosa aqui, pois evita que os processos sejam interrompidos em primeiro lugar.

#### **Passo 6.4: Isolar Núcleos de CPU para Aplicações de Áudio**

Esta etapa dedica dois núcleos de CPU para lidar com as threads de serviço do Host Diretta.

1.  Acesse o Host Diretta via SSH:
    ```bash
    ssh diretta-host
    ```
2.  Entre no sistema de menus do AudioLinux:
    ```bash
    menu
    ```
3.  Navegue até o menu **ISOLATED CPU CORES configuration** (em **SYSTEM menu**).

4.  Confirme se o isolamento de núcleos está desativado. Caso contrário, use a opção 3 para desativá-lo:
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

5.  Navegue de volta para o menu **ISOLATED CPU CORES configuration** (em **SYSTEM menu**). Siga as instruções para isolar os **núcleos 2 e 3** e alocá-los para o Diretta ALSA.
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

6.  Após a conclusão do processo, saia de volta para o terminal.

---

#### **Passo 6.5: Desativar o timer rtapp legado**
```bash
sudo systemctl stop rtapp.timer
sudo systemctl disable rtapp.timer
```

#### **Passo 6.6: Reiniciar para aplicar as alterações.**
```bash
sudo sync && sudo reboot
```

## 16. Apêndice 7: Otimizações Opcionais de IRQ e Threads

### Parte 1: Isolamento do Caminho USB do Target Diretta
Por padrão, mesmo quando os núcleos da CPU estão isolados, as interrupções USB ainda podem competir por recursos nos núcleos de sistema "ruidosos" (0 e 1). Este script identifica dinamicamente o controlador USB específico ao qual seu DAC está conectado e fixa suas interrupções de hardware aos núcleos de áudio isolados (2 e 3). No Raspberry Pi 5, os controladores USB são gerenciados pelo chip RP1, o que nos permite direcionar as interrupções de hardware para núcleos específicos.

**Nota:** Esta otimização não é aplicável ao Raspberry Pi 4 devido a interrupções bloqueadas por hardware.

1.  Certifique-se de que seu DAC esteja ligado e conectado ao Target.
2.  Inicie a reprodução de música para o Target Diretta. Isso garante que o script possa detectar o tráfego de interrupções ativo.
3.  Execute o seguinte comando no Target Diretta:
    ```bash
    curl -fsSL https://raw.githubusercontent.com/dsnyder0pc/rpi-for-roon/refs/heads/main/scripts/usb-isolation.sh | sudo bash
    ```
4.  Reinicie para aplicar as alterações:
    ```bash
    sudo sync && sudo reboot
    ```

**O que isso faz:** O script localiza o caminho ativo do DAC (por exemplo, `xhci-hcd:usb1` ou `xhci-hcd:usb3`). Em seguida, adiciona o identificador específico ao seu grupo de isolamento do AudioLinux para criar um caminho de dados 100% isolado, desde a entrada de rede até a saída USB.

---

### Parte 2: Otimização de Threads do Host Diretta

Com as otimizações de kernel em tempo real implementadas, o Host Diretta agora pode lidar com um intervalo de pacotes mais agressivo, o que pode levar a uma melhor qualidade de som. Esta etapa final reduz o parâmetro `CycleTime` de 800 para 514 microssegundos. Esse intervalo de tempo menor entre os pacotes garante que todo o conteúdo até DSD256 e DXD (32 bits, 352.8 kHz) exigirá apenas um pacote por ciclo. Também podemos agendar as threads do Diretta para núcleos específicos.

1.  Acesse o **Host Diretta** via SSH se ainda não estiver logado.
2.  Execute o seguinte comando para aplicar a configuração otimizada:
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
3.  Reinicie o serviço Diretta para que a alteração entre em vigor:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart diretta_alsa.service
    ```

> ---
> ### ✅ Ponto de Controle: Verificar seu Ajuste em Tempo Real
>
> Seu ajuste avançado em tempo real deve estar concluído agora. Para verificar todos os componentes desta nova configuração, por favor, retorne ao [**Apêndice 5**](#14-ap%C3%AAndice-5-verifica%C3%A7%C3%B5es-de-sa%C3%BAde-do-sistema) e execute o comando de **Verificação de Saúde do Sistema** universal no Host e no Target.
>
> ---

## 17. Apêndice 8: Velocidades Opcionais de Rede Purista

**Objetivo:** Reduzir o ruído elétrico e melhorar a precisão do agendador do SO limitando a velocidade do link de rede dedicado e desativando explicitamente a Energy Efficient Ethernet (EEE).

Embora contra-intuitivo, reduzir a velocidade do link de 1 Gbps para 100 Mbps (ou até 10 Mbps) no link dedicado (`end0`) pode melhorar a qualidade do som. A frequência de operação mais baixa de 100BASE-TX (31.25 MHz vs 62.5 MHz) gera menos RFI. No extremo, diminuir a velocidade para 10 Mbps reduz a frequência do transmissor para 10 MHz. Além disso, garantir que o EEE esteja desativado evita que o link entre em estados de suspensão, eliminando potenciais picos de latência (oscilação) e garantindo uma estabilidade sólida no hardware do Raspberry Pi 5.

> ---
> ### 🎧 Análise Aprofundada: Por que um Limite de 10 Mbps Restaura a "Calma" Sônica
>
> Restringir o seu link de áudio dedicado a 10 Mbps introduz limitações estritas de formato — limitando a sua reprodução a **DSD64 Nativo** e **PCM de 32 bits/96 kHz**. No entanto, para audiófilos que priorizam a qualidade de CD redbook ou arquivos padrão de alta resolução, a troca traz profundos benefícios sônicos ao abordar as causas raiz da aspereza digital.
>
> * **Frequências de Portadora Drasticamente Mais Baixas:** A Ethernet Gigabit padrão opera em um sinal portador de alta frequência de 62.5 MHz (usando codificação multinível complexa). Reduzir para 100 Mbps diminui isso para 31.25 MHz. Dar o passo final para um link de 10 Mbps (10BASE-T) utiliza um esquema de codificação Manchester incrivelmente simples, rodando a uma frequência portadora nativa de apenas **10 MHz**. Essa redução massiva na frequência de operação diminui significativamente as emissões de radiofrequência (RFI) geradas dentro do gabinete e ao longo do cabo.
> * **Sobrecarga de Processamento Reduzida no Target:** Redes de alta largura de banda forçam a placa de interface de rede (NIC) e a CPU a lidar com pacotes de dados em uma cadência rápida e agressiva. Ao limitar a velocidade do link para corresponder às demandas reais dos dados de áudio padrão, você reduz drasticamente o volume de interrupções de rede que o sistema operacional do Target deve processar.
> * **Sinergia com a Filosofia Central do Diretta:** Todo o objetivo do protocolo Diretta é eliminar o processamento em rajadas e estabilizar o consumo de corrente. Um canal de 10 Mbps age como um equalizador físico para o fluxo de dados, evitando os picos de dados de alta velocidade que causam flutuações na fonte de alimentação.
>
> O resultado desta constrição "Super Purista" é uma queda instantaneamente reconhecível no piso de ruído digital. Os ouvintes frequentemente relatam um palco sonoro mais amplo e relaxado, rastreamento de transientes de alta frequência mais limpo e uma sensação geral de facilidade e calma analógica que complementa perfeitamente o que o AudioLinux e o Diretta estão tentando alcançar.
> ---

**Nota:** Você pode ver avisos de "buffer low" nos logs do Target (`LatencyBuffer` caindo para 1). Este é um comportamento normal devido ao aumento da latência de serialização do link mais lento e não causa interrupções audíveis.

### Passo 1: Configurar Host e Target (Desativar EEE)

A Energy Efficient Ethernet (EEE) pode causar instabilidade no link em algumas combinações de hardware. Criaremos um serviço para desativá-la explicitamente tanto no Host quanto no Target para garantir um comportamento consistente.

**Criar o serviço de desativação:** _(Executar em AMBOS o Host e o Target)_

```bash
cat <<'EOT' | sudo tee /etc/systemd/system/disable-eee.service
[Unit]
Description=Disable EEE on end0 for Link Stability
After=network.target
BindsTo=sys-subsystem-net-devices-end0.device
After=sys-subsystem-net-devices-end0.device

[Service]
Type=oneshot
# Wait up to 5 seconds for the interface to actually show as UP
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

### Passo 2: Marcar o Target (Para QA)

Para garantir que o **Script de QA do Target** saiba que deve validar esta configuração específica, crie um arquivo marcador no Target:

```bash
sudo touch /etc/diretta-100m
```

### Passo 3: Configurar o Host (Limite de Velocidade)
Criaremos um serviço no **Host** que o força a anunciar 10 Mbps ou 100 Mbps Full Duplex, dependendo se o modo "Super Purista" está ativado. O Target detectará automaticamente a mudança de velocidade e corresponderá a ela.

**Criar o script e serviço de restrição:** _(Executar apenas no Host)_
```bash
cat <<'EOT' | sudo tee /usr/local/bin/set-link-speed.sh
#!/bin/bash
# Set link speed based on the Super Purist web UI flag using safe advertisement masks
FLAG_FILE="/home/audiolinux/purist-mode-webui/super_purist.flag"
INTERFACE="end0"

# CRITICAL: Wait up to 60 seconds for the physical interface to initialize carrier link layer
echo "Synchronizing with physical link layer..."
for i in {1..60}; do
    if [ -f /sys/class/net/$INTERFACE/carrier ] && [ "$(cat /sys/class/net/$INTERFACE/carrier 2>/dev/null)" "==" "1" ]; then
        echo "Physical link layer detected after $i seconds."
        break
    fi
    sleep 1
done

# Apply the advertisement mask based on flag state
if [ -f "$FLAG_FILE" ]; then
    echo "Super Purist flag detected. Advertising 10 Mbps Full Duplex..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x002
else
    echo "Standard/Purist mode. Advertising up to 100 Mbps Full Duplex..."
    /usr/bin/ethtool -s $INTERFACE advertise 0x00a
fi

# Platform-specific negotiation handling
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

echo "Habilitar e iniciar o serviço:"
sudo systemctl daemon-reload
sudo systemctl enable --now limit-speed-100m.service
```

***
> **Nota sobre Latência de Reprodução:**
> Você pode notar um pequeno aumento no atraso entre pressionar "Play" e ouvir a música (até ~1 segundo). Este é um comportamento esperado. Ao restringir o link para 10 ou 100 Mbps, estamos limitando intencionalmente a rajada inicial de dados para garantir que a conexão opere em uma frequência mais baixa e silenciosa. O sistema está trocando tempos de início instantâneos por um estado estável mais constante e de menor ruído durante a reprodução.
***

>
>
> ---
>
> ### ✅ Ponto de Controle: Verificar a Configuração de Rede
>
> Seu link de rede dedicado está agora configurado para a operação "Purista" de 100 Mbps. Para verificar se o serviço do Host está ativo e se o Target negociou corretamente a velocidade (detectado por meio do arquivo marcador), por favor, retorne ao [**Apêndice 5**](#14-ap%C3%AAndice-5-verifica%C3%A7%C3%B5es-de-sa%C3%BAde-do-sistema) e execute o comando de **Verificação de Saúde do Sistema** universal no Host e no Target.
>
> ---

## 18. Apêndice 9: Otimização de Jumbo Frames Opcional
Esta seção otimiza o transporte para eficiência de alta largura de banda.

#### **Passo 1:** Preparar as Interfaces

Devemos forçar temporariamente as interfaces de rede para MTU 9000 para verificar o suporte do kernel e preparar para o teste do link.

**Execute isso primeiro no Target e depois no Host:**

```bash
sudo sh -c 'ip link set end0 down; sleep 2; ip link set end0 mtu 9000; ip link set end0 up'
end0_mtu=$(ip link show dev end0 | awk '/mtu/ {print $5}')
if [[ "9000" == "$end0_mtu" ]]; then
  echo "SUCESSO: O kernel suporta Jumbo frames. Prossiga para o Passo 2."
else
  echo "PARAR: O seu kernel não parece suportar Jumbo frames."
fi
```

*Se você vir "PARAR" no Host **ou** no Target, não prossiga. O seu kernel não possui o patch necessário.*

---

#### **Passo 2:** Configuração Automatizada do Target

Acesse o Target via SSH (`diretta-target`) e cole o seguinte bloco.

```bash
# 1. Detectar Limite do Link (Full vs Baby)
echo "Testando a Capacidade do Link..."
if ping -c 1 -w 1 -M "do" -s 8972 host &>/dev/null; then
  NEW_MTU=9000
  echo "SUCESSO: Full Jumbo Frames (MTU 9000) suportados."
elif ping -c 1 -w 1 -M "do" -s 2004 host &>/dev/null; then
  NEW_MTU=2032
  echo "SUCESSO: Baby Jumbo Frames (MTU 2032) suportados."
else
  echo "FALHA: O link não suporta Jumbo Frames. Revertendo para os padrões seguros."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Aplicar Configuração de Rede do Sistema
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

  # 3. Aplicar Configuração do Diretta
  echo "Configurando o Target Diretta..."
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
  echo "CONCLUÍDO: Otimização do Target concluída."
}

```

---

#### **Passo 3:** Configuração Automatizada do Host

Acesse o Host via SSH (`diretta-host`) e cole o seguinte bloco. Ele testará o link, configurará as definições permanentes de rede e atualizará o Diretta.

```bash
# 1. Detectar Limite do Link (Full vs Baby)
echo "Testando a Capacidade do Link..."
# Dar um momento para o link se estabilizar após a alteração manual do MTU
sleep 2

if ping -c 1 -w 1 -M "do" -s 8972 target &>/dev/null; then
  NEW_MTU=9000
  echo "SUCESSO: Full Jumbo Frames (MTU 9000) suportados."
elif ping -c 1 -w 1 -M "do" -s 2004 target &>/dev/null; then
  NEW_MTU=2032
  echo "SUCESSO: Baby Jumbo Frames (MTU 2032) suportados."
else
  echo "FALHA: O link não suporta Jumbo Frames. Revertendo para os padrões seguros."
  sudo ip link set end0 mtu 1500
  false
fi && {
  # 2. Aplicar Configuração de Rede do Sistema
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

  # 3. Aplicar Configuração do Diretta
  echo "Configurando o Host Diretta..."

  # Sempre ativar o FlexCycle para Jumbo Frames para garantir estabilidade
  sudo sed -i 's/^FlexCycle=.*/FlexCycle=enable/' /opt/diretta-alsa/setting.inf

  # Otimização condicional do CycleTime e InfoCycle
  if [ "$NEW_MTU" -eq 9000 ]; then
    echo "Otimização: Full Jumbo Frames detectados. Relaxando o CycleTime para 1000us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=1000/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=100000/' /opt/diretta-alsa/setting.inf
  else
    echo "Otimização: Baby Jumbo Frames detectados. Definindo o CycleTime para 700us."
    sudo sed -i 's/^CycleTime=.*/CycleTime=700/' /opt/diretta-alsa/setting.inf
    sudo sed -i 's/^InfoCycle=.*/InfoCycle=70000/' /opt/diretta-alsa/setting.inf
  fi

  sudo systemctl restart diretta_alsa
  echo "CONCLUÍDO: Otimização do Host concluída."
}
```

#### **Passo 4:** Reiniciar para Aplicar as Alterações de MTU
Reinicie primeiro o Target, depois o Host:
```bash
sudo sync && sudo reboot
```

>
>
> ---
>
> ### ✅ Ponto de Controle: Verificar a Configuração de Rede
>
> Se você conseguiu habilitar o suporte a Jumbo frames para a sua configuração, agora é um bom momento para retornar ao [**Apêndice 5**](#14-ap%C3%AAndice-5-verifica%C3%A7%C3%B5es-de-sa%C3%BAde-do-sistema) e executar o comando de **Verificação de Saúde do Sistema** universal no Host e no Target.
>
> ---

## 19. Apêndice 10: Atualizações do Sistema Opcionais
Esta seção fornece orientações sobre como aplicar atualizações ao hardware do Raspberry Pi, ao sistema operacional AudioLinux e à pilha de software do Diretta.

#### **Parte 1:** Atualizar o Bootloader do Raspberry Pi (Opcional)

A atualização do bootloader (EEPROM) do Raspberry Pi não é necessária e traz riscos inerentes. No entanto, manter o firmware atualizado pode oferecer vantagens como temperaturas operacionais mais baixas e sequências de inicialização mais limpas devido às contínuas correções de bugs fornecidas pela Raspberry Pi Foundation.

*Aviso: Certifique-se de aplicar apenas a imagem de firmware correta à placa correspondente. Gravar em um Raspberry Pi 4 o bootloader de um Raspberry Pi 5 (ou vice-versa) pode resultar em graves consequências negativas, inclusive inutilizando permanentemente a placa.*

**Verificar a Versão Atual do Bootloader**
Antes de começar, acesse o Host e o Target via SSH e execute o seguinte comando para verificar a data de lançamento do seu bootloader atual. Anote essas datas para poder verificar o sucesso da atualização mais tarde.

```bash
vcgencmd bootloader_version
```

*(Procure a data na primeira linha da saída).*

**Preparar a Mídia de Atualização**
Você precisará de um cartão microSD em branco, um leitor de cartão SD e o software oficial Raspberry Pi Imager instalado na sua estação de trabalho.

1. Abra o Raspberry Pi Imager. Clique em **CHOOSE DEVICE** e selecione a placa Raspberry Pi específica que você atualizará.

   ![Selecionar Dispositivo Raspberry Pi 5](images/01-rpi-dev.png)

2. Clique em **CHOOSE OS**, role a lista para baixo e selecione **Misc utility images**.

   ![Selecionar Misc Utility Images](images/02-rpi-misc.png)

3. Selecione **Bootloader**. *(Nota: O menu exibirá a família Pi que você selecionou no Passo 1).*

   ![Selecionar Bootloader para a Família Pi 5](images/03-rpi-bl.png)

4. Selecione **SD Card Boot**.

   ![Selecionar SD Card Boot](images/04-rpi-sd.png)

5. Clique em **CHOOSE STORAGE**, selecione o seu cartão microSD em branco, clique em **NEXT** e grave a imagem.

*Importante: Se o seu Target for um Raspberry Pi 5 e seu Host for um Raspberry Pi 4 (ou qualquer combinação mista), você não poderá reutilizar o mesmo cartão de atualização. Você deve retornar ao seu computador e gravar um novo cartão microSD de atualização especificamente para o segundo tipo de placa antes de prosseguir.*

**Realizar a Atualização de Hardware**

1. Desligue ambas as máquinas com segurança. Desligue primeiro o Target, depois o Host (`sudo poweroff`).
2. Desconecte os cabos de alimentação física de ambas as unidades.
3. Remova os cartões microSD de inicialização principais de cada unidade e guarde-os em local seguro.
4. Insira cuidadosamente o cartão microSD de atualização recém-preparado na placa (certifique-se de que os contatos dourados estejam voltados para a parte inferior da placa Raspberry Pi).
5. Reconecte a alimentação à placa.
6. Observe as luzes de atividade na placa. Aguarde até que o LED verde comece a piscar rapidamente em um ritmo constante e contínuo (isso geralmente leva cerca de 10 segundos). As piscadas constantes indicam que a gravação da EEPROM está concluída.
7. Desconecte a alimentação da placa.
8. Remova o cartão microSD de atualização e reinsira o seu cartão microSD de inicialização original.
9. Reconecte a alimentação aos sistemas. **Ligue primeiro o Host, depois o Target.**

Assim que os sistemas estiverem totalmente inicializados e acessíveis, execute a verificação da versão do bootloader em cada computador mais uma vez para confirmar se as datas do bootloader avançaram para a data de lançamento gravada pelo Imager. Se o seu Host e Target usarem tipos de placa diferentes (por exemplo, RPi4 e RPi5), as versões provavelmente serão diferentes. Sem problemas.

```bash
vcgencmd bootloader_version
```

---

#### **Parte 2:** Atualizar o AudioLinux e o Software do Diretta

O processo de atualização do sistema requer uma sequência estrita para garantir que o kernel personalizado, as toolchains de compilação e o daemon ALSA permaneçam perfeitamente sincronizados.

#### Agora, prossiga com as atualizações
1. Inicie a ferramenta de configuração do AudioLinux digitando `menu` no prompt de comando.
2. Navegue até o **Install/Update menu** e selecione **UPDATE System**.
3. Enquanto ainda estiver no **Install/Update menu**, selecione **UPDATE menu**.
   *(Nota: Você será solicitado a inserir o endereço de e-mail usado para a compra do seu AudioLinux, junto com o nome de usuário e a senha específicos fornecidos pelo Piero para baixar a imagem do AudioLinux).*
4. Selecione **SELECT/UPDATE kernel**. Escolha a versão exata do kernel recomendada anteriormente no [**Passo 4**](#44-executar-atualiza%C3%A7%C3%B5es-do-sistema-e-do-menu).
5. Reaplique a correção do `motd` da [**Seção 5.1**](#51-pr%C3%A9-configurar-o-host-diretta) no **Host**.
6. Reaplique o patch do `sudoers` da [**Seção 7.2**](#72-corrigir-a-preced%C3%AAncia-da-regra-do-sudoers) em **ambos** o Target e o Host.
7. Reinicie primeiro o Target, seguido pelo Host.
8. Assim que estiver online novamente, execute novamente o script "Configurar Toolchain de Compilador Compatível" do [**Passo 8**](#8-instala%C3%A7%C3%A3o-e-configura%C3%A7%C3%A3o-do-software-diretta) em **ambos** o Target e o Host.
9. No **Target**, execute a etapa de Instalação/Atualização do Diretta detalhada na [**Seção 8.1**](#81-no-target-diretta).
10. No **Host**, execute a etapa de Instalação/Atualização do Diretta detalhada na [**Seção 8.2**](#82-no-host-diretta).
11. Reinicie primeiro o Target, seguido pelo Host.
>
>
> ---
>
> ### ✅ Ponto de Controle: Saúde do Sistema e Teste de Regressão
>
> Após concluir a sequência de atualização, você deve verificar a estabilidade do fluxo de áudio para garantir que nenhuma regressão de software ou configuração tenha ocorrido durante o upgrade.
>
> 1. Abra o Roon, aguarde o retorno da zona de rede e reproduza pelo menos alguns segundos de música para verificar o link da camada de transporte e colocar os contadores de hardware em movimento.
> 2. Acesse o **Target** via SSH e reverta temporariamente para o Modo Padrão para permitir que os scripts de diagnóstico enviem tráfego de forma limpa pela rede:
>    ```bash
>    purist-mode --revert
>    ```
> 3. Execute o script de QA universal de **Verificação de Saúde do Sistema** do [**Apêndice 5**](#14-ap%C3%AAndice-5-verifica%C3%A7%C3%B5es-de-sa%C3%BAde-do-sistema) em **ambos** o Host e o Target.
> 4. Verifique cuidadosamente a saída e resolva quaisquer problemas isolados de afinidade de thread ou prioridade detectados pelo script.
>
> ---

---

#### **Parte 3:** Sobrescrever os Limites de Corrente USB (Apenas Raspberry Pi 5)

Se você está utilizando um Raspberry Pi 5 e alimentando-o com uma fonte premium de terceiros (ex: iFi SilentPower Elite 5V ou uma Fonte de Alimentação Linear capaz de fornecer 5A) em vez da fonte oficial USB-C de 27W do Raspberry Pi, o Pi adotará por padrão uma negociação segura de 5V/3A. Isso restringe o consumo combinado de corrente em todas as quatro portas USB a 600mA.

Embora geralmente irrelevante para transportes purificados de áudio, se você sabe que sua fonte de alimentação é capaz de fornecer continuamente pelo menos 5A a 5V, pode contornar essa restrição com segurança.

**Execute este comando para anexar a substituição (override) à sua configuração de inicialização:**

```bash
if ! grep -q "^usb_max_current_enable=" /boot/config.txt; then
  echo "usb_max_current_enable=1" | sudo tee -a /boot/config.txt
else
  echo "Otimização já presente em /boot/config.txt. Pulando a configuração."
fi
sudo sync && sudo reboot
```

---
