# DIY Power Meter for the Decathlon EB140

<details>
<summary>⚠️ IMPORTANT: DISCLAIMER - READ BEFORE PROCEEDING </summary>
By choosing to proceed, you acknowledge and agree to the following:

1. **Educational / Non-Commercial Use Only:** This project and its documentation are provided for educational, non-commercial use only. It is intended to demonstrate engineering principles and for personal experimentation. You agree not to use this information for any commercial purpose.

2. **Intellectual Property:** This project involves reverse-engineering a commercial product. All trademarks and copyrights associated with the Decathlon EB140 are the property of their respective owners. This project is not affiliated with, endorsed by, or sponsored by Decathlon or any of its subsidiaries. The aim is to share knowledge, not to infringe upon any intellectual property rights.

3. **Not Professional Advice:** This documentation is not professional advice.

4. **Inherent Risks:** You understand the risks involved in working with electrical systems and mechanical equipment. You assume full and complete responsibility for your own safety and the safety of your property.

5. **No Warranty:** This project is provided "AS IS" without any warranty of any kind, express or implied. 

6. **No Liability:** In no event shall the author(s) or creator(s) of this project be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this information, even if advised of the possibility of such damage.

7. **Accuracy:** While efforts are made to ensure accuracy, I cannot guarantee that the information is error-free or complete.

8. **Warranty Void:** Tapping into the electronics of your Decathlon EB140 will almost certainly void its manufacturer's warranty. Proceed at your own risk.

9. **Safety First:** You are solely responsible for verifying all wiring with a multimeter, ensuring safe electrical connections, and securing all components before operating the modified equipment.

If you are not comfortable with these risks, do not proceed with this project.

</details>

## Overview
This project details the process of building a custom power meter for the Decathlon EB140 exercise bike.

By leveraging the bike's existing sensors and applying a physics-based model, we can build a somewhat accurate, real-time power meter (displaying watts and cadence).

The final system should be be a non-invasive, low-cost solution that broadcasts data via Bluetooth Low Energy (BLE), and integrates seamlessly with fitness apps like Zwift and Wahoo.

## Core Principles
### Model
The exercise bike, like most around this price point, utilizes a spoked cast-iron flywheel; slowed by a permanent magnet eddy-current brake. The gap between the magnet and the flywheel's rim determines the strength of the resistance effect generated in the wheel and hence felt at the pedals by the rider. Therefore the bike's resistance levels 1-15 correspond to this gap; controlled by a positional potentiometer.

 The project's design is based on the first law of thermodynamics (conservation of energy). When the flywheel is maintained at a constant rotational speed, *most* mechanical power input by the user is dissipated as heat through the braking system. By characterizing the power dissipation of the magnetic brake, we can directly approximate user power output.
> ignoring friction in the bearings, and temperature effects on the magnet

This braking power is proportional to the square of the speed of the flywheel.
```
P ∝ ω² => P = k · ω²
```
We will determine this *k* constant and store it in a two-dimensional lookup table that's mapped to the bike's resistance setting. This table will be created during a one-time calibration step.

### Hardware Setup: Non-Invasive and Safe
The system is designed to "listen in" on the bike's signals without modifying its core hardware.

- **Microcontroller:** Raspberry Pi Pico W. Chosen for its low cost, powerful processor, built-in ADC (to read the analog potentiometer), and wireless capabilities (for data streaming).

- **Power Supply:** The system will be powered directly from the bike's internal 9V DC input. This ensures the power meter turns on and off automatically with the bike.
  Critical Safety Note: A DC-DC buck converter is mandatory to step down the bike's 9V supply to a stable 5V for the Pico. Never connect the bike's 9V directly to the Pico, as it will be damaged. Always verify the output voltage with a multimeter.

- **Sensors & Data Acquisition:** We reuse the bike's existing sensors:
    - Potentiometer Signal: To read the resistance level (as a voltage).
    - Reed Switch Signal: To measure the flywheel's RPM during caliberation and then the pedal cadence during operation.

- **Components List:**

  * Raspberry Pi Pico 2WH
  * DC-DC Converter
  * Alligator Clip Jumpers
  * Multimeter

### Software and Operation
**Firmware:** The Pico will be programmed using MicroPython for ease of development.

Two-Phase Process:

1. Calibration Mode: A script guides the user through a coast-down test to populate the 2D brake power lookup table and calculate the flywheel's moment of inertia.

2. Operation Mode: The main script runs in a loop, reading sensor values, calculating total power, and making this data available.

**Data Output:** The Pico will broadcast the data via bluetooth, using the standard BLE service specifications for Cycling Power, and Cycling Speed & Cadence.
