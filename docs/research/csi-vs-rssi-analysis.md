# RF Sensing Fundamentals: RSSI vs. CSI Comparative Analysis

**NEXUS-PRESENCE: Multi-Node Ambient Wi-Fi Human Presence, Movement & 3D Visualization System**  
**Author:** Uday Kiran Jammula  

---

## 1. Introduction: Wireless RF as an Ambient Sensor

When radio-frequency (RF) waves propagate through an indoor environment, physical objects—including human bodies—act as dielectric boundaries. A human body consists of ~70% water, presenting a high relative permittivity ($\epsilon_r \approx 50$) and conductivity ($\sigma \approx 1.5\text{ S/m}$) at 2.4 GHz. Consequently, when a person moves within the Line-of-Sight (LoS) or first Fresnel zone between Wi-Fi transceivers, they cause:
1. **Shadow fading / Attenuation**: Direct absorption of signal energy.
2. **Multipath scattering**: Reflections, diffractions, and phase shifts that constructively or destructively interfere at the receiver.

NEXUS-PRESENCE harnesses these perturbations using two distinct RF measurement layers: **Received Signal Strength Indication (RSSI)** and **Channel State Information (CSI)**.

---

## 2. Theoretical Comparison

| Property | Received Signal Strength Indication (RSSI) | Channel State Information (CSI) |
| :--- | :--- | :--- |
| **PHY / MAC Layer** | MAC layer scalar | PHY layer complex matrix |
| **Data Granularity** | 1 scalar value per packet (dBm) | 52 to 114 subcarriers (amplitude & phase) per packet |
| **Frequency Resolution** | Integrated over entire 20/40 MHz channel | Discrete per OFDM orthogonal subcarrier |
| **Multipath Sensitivity** | Blind to multipath components; registers only total aggregate sum | Resolves individual multipath reflections and phase rotations |
| **Sensitivity Domain** | Gross whole-body movement (walking, room entry/exit) | Micro-movements (chest displacement, subtle gestures, walking) |
| **Hardware Portability** | Universal (every 802.11 Wi-Fi chip supports RSSI) | Requires specific chip hardware and firmware driver support |
| **Computational Cost** | Very low ($O(1)$ window statistics) | Moderate to high (matrix transforms, phase sanitization) |

---

## 3. Mathematical Foundations

### 3.1 RSSI Log-Distance Path Loss Model
In free space, signal power attenuates according to the Friis transmission formula. In complex multipath indoor environments, the average received signal power is parameterized by the Log-Distance Path Loss (LDPL) model:

$$\text{RSSI}(d) = \text{RSSI}_0 - 10 \cdot n \cdot \log_{10}\left(\frac{d}{d_0}\right) + X_\sigma$$

Where:
- $\text{RSSI}_0$ is the received signal strength at reference distance $d_0 = 1\text{ m}$ (typically $-40$ to $-45\text{ dBm}$).
- $n$ is the path loss exponent ($n \approx 2.0$ in free space, $2.0 - 3.5$ in indoor residential environments).
- $X_\sigma$ is a zero-mean Gaussian random variable representing log-normal shadow fading.

Inverting this equation provides an estimate of Euclidean distance $d$:

$$d = d_0 \cdot 10^{\frac{\text{RSSI}_0 - \text{RSSI}}{10 \cdot n}}$$

### 3.2 Channel State Information (CSI) Channel Matrix
Modern Wi-Fi standards (802.11n/ac/ax) employ Orthogonal Frequency Division Multiplexing (OFDM). In the frequency domain, the received signal $Y(f)$ is related to transmitted signal $X(f)$ by:

$$Y_i = H_i \cdot X_i + N_i$$

Where:
- $i \in [1, K]$ is the subcarrier index ($K=52$ for 20 MHz HT20).
- $H_i$ is the complex Channel Frequency Response (CFR) for subcarrier $i$:

$$H_i = |H_i| e^{j \angle H_i}$$

- $|H_i| = \sqrt{\text{real}_i^2 + \text{imag}_i^2}$ is the subcarrier amplitude.
- $\angle H_i = \arctan2(\text{imag}_i, \text{real}_i)$ is the subcarrier phase.

When a human body traverses the RF environment, each multipath path length changes by $\Delta d_k$, introducing a phase change $\Delta \theta_k = 2\pi \frac{\Delta d_k}{\lambda}$, causing distinct constructive and destructive interference ripples across adjacent subcarrier frequencies.

---

## 4. Scientific Honesty & Realistic Boundaries

1. **Skeleton Reconstruction Limitations**: Neither RSSI nor single-antenna 2.4 GHz ESP32 CSI can reconstruct an anatomical human skeleton. A human skeleton has 206 bones and dozens of kinematic degrees of freedom. A 2.4 GHz RF wave has a wavelength $\lambda \approx 12.5\text{ cm}$. Resolving individual fingers, joints, or spine curvature exceeds the spatial Nyquist limit of ordinary omnidirectional antennas without massive multi-gigahertz phased antenna arrays.
2. **Through-Wall Sensing**: RF waves at 2.4 GHz penetrate standard drywall and wood with ~3 to 6 dB attenuation. However, heavy reinforced concrete, brick, or metal surfaces cause severe attenuation and total reflection.
3. **The Role of the 3D Avatar**: In NEXUS-PRESENCE, the 3D humanoid avatar is an **interactive spatial visualization of mathematically estimated position and velocity**, not an optical sensor scan.

---

## 5. Conclusion & Deployment Strategy

NEXUS-PRESENCE utilizes a dual-engine architecture:
- When target ESP32 hardware supports CSI callback extraction, subcarrier variance and phase differentials enhance sensitivity to fine movement.
- When target nodes run on standard platforms where CSI is disabled or memory-constrained, the system automatically falls back to multi-node sliding-window RSSI tracking without breaking the pipeline.
