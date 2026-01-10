Based on Matthew Arndt's tuning guide and this project infrastructure, here is the prioritized, one-by-one testing plan. This sequence focuses on establishing a "Reference Foundation" first, followed by spatial tuning, then tonal density.

---

## Phase 1: The "Reference" Foundation

This phase moves your system from "Fully Adaptive" timing to "Controlled Adaptive" (`semi`) and sets `ThredMode` to a high-coherence value that your isolated cores can handle.

### 1.1 Testing Objectives

* **FlexCycle=semi**: Provides a damped, stable feedback loop that Matthew considers the reference for high-end systems.
* **Preset=Fix**: Prioritizes determinism and tonal saturation for consistent tuning.
* **ThredMode=2048**: Minimizes "thread chatter" and jitter at buffer boundaries.

### 1.2 Implementation (Stage 1)

```bash
# 1. Backup baseline configuration
sudo cp /etc/diretta-alsa.conf /etc/diretta-alsa.conf.bak.stage0_baseline

# 2. Update FlexCycle from 'enable' to 'semi'
sudo sed -i 's/^FlexCycle=enable/FlexCycle=semi/' /etc/diretta-alsa.conf

# 3. Update ThredMode from '1' to '2048'
sudo sed -i 's/^ThredMode=1/ThredMode=2048/' /etc/diretta-alsa.conf

# 4. Add or update Preset to 'Fix'
if ! grep -q "^Preset=" /etc/diretta-alsa.conf; then
    sudo sed -i '/\[global\]/a Preset=Fix' /etc/diretta-alsa.conf
else
    sudo sed -i 's/^Preset=.*/Preset=Fix/' /etc/diretta-alsa.conf
fi

# 5. Restart service
sudo systemctl restart diretta_alsa

```

---

## Phase 2: Spatial Air and Control Loop

This phase target's the "Spatial Axis" by increasing the frequency of host-target synchronization.

### 2.1 Testing Objectives

* **InfoCycle=12000**: Increases control-plane feedback from 100ms down to 12ms. This adds lateral air and increases perceived room scale.
* **Fragment=Balanced**: Swaps the default (likely Optimize) for a mode that allows vocals to breathe more into the space and increases decay width.

### 2.2 Implementation (Stage 2)

```bash
# 1. Backup Stage 1 configuration
sudo cp /etc/diretta-alsa.conf /etc/diretta-alsa.conf.bak.stage1_foundation

# 2. Update InfoCycle to 12000
sudo sed -i 's/^InfoCycle=100000/InfoCycle=12000/' /etc/diretta-alsa.conf

# 3. Add or update Fragment to 'Balanced'
if ! grep -q "^Fragment=" /etc/diretta-alsa.conf; then
    sudo sed -i '/\[global\]/a Fragment=Balanced' /etc/diretta-alsa.conf
else
    sudo sed -i 's/^Fragment=.*/Fragment=Balanced/' /etc/diretta-alsa.conf
fi

# 4. Restart service
sudo systemctl restart diretta_alsa

```

---

## Phase 3: Tonal Density and Weight

This phase adjusts the "harmonic stability" and the physical "weight" of the music.

### 3.1 Testing Objectives

* **syncBufferCount=12**: Increases host-side smoothing. Matthew notes this specifically increases vocal body and reduces harsh edges.
* **LatencyBuffer=76000**: Sets the target-side elastic buffer. This determines how firmly the music "lands" at the DAC, increasing emotional presence.

### 3.2 Implementation (Stage 3)

```bash
# 1. Backup Stage 2 configuration
sudo cp /etc/diretta-alsa.conf /etc/diretta-alsa.conf.bak.stage2_spatial

# 2. Update syncBufferCount from 8 to 12
sudo sed -i 's/^syncBufferCount=8/syncBufferCount=12/' /etc/diretta-alsa.conf

# 3. Update LatencyBuffer from 0 to 76000
sudo sed -i 's/^LatencyBuffer=0/LatencyBuffer=76000/' /etc/diretta-alsa.conf

# 4. Restart service
sudo systemctl restart diretta_alsa

```

---

## Phase 4: CPU Affinity and Clean-up

This final phase aligns Diretta's threads to your isolated cores for maximum determinism.

### 4.1 Testing Objectives

* **CpuSend=2**: Dedicates the audio packet send path to isolated physical core 2.
* **CpuOther=3**: Moves sync and coordination threads to isolated core 3 to prevent them from fighting the audio path.
* **CPULOW=3**: Contains background noise and logging away from the audio path.

### 4.2 Implementation (Stage 4)

```bash
# 1. Backup Stage 3 configuration
sudo cp /etc/diretta-alsa.conf /etc/diretta-alsa.conf.bak.stage3_density

# 2. Update CpuSend
if ! grep -q "^CpuSend=" /etc/diretta-alsa.conf; then
    sudo sed -i '/\[global\]/a CpuSend=2' /etc/diretta-alsa.conf
else
    sudo sed -i 's/^CpuSend=.*/CpuSend=2/' /etc/diretta-alsa.conf
fi

# 3. Update CpuOther
if ! grep -q "^CpuOther=" /etc/diretta-alsa.conf; then
    sudo sed -i '/\[global\]/a CpuOther=3' /etc/diretta-alsa.conf
else
    sudo sed -i 's/^CpuOther=.*/CpuOther=3/' /etc/diretta-alsa.conf
fi

# 4. Update CPULOW
if ! grep -q "^CPULOW=" /etc/diretta-alsa.conf; then
    sudo sed -i '/\[global\]/a CPULOW=3' /etc/diretta-alsa.conf
else
    sudo sed -i 's/^CPULOW=.*/CPULOW=3/' /etc/diretta-alsa.conf
fi

# 5. Restart service
sudo systemctl restart diretta_alsa

```
