# Calibration Procedure

The purpose of this calibration procedure is to experimentally determine the proportionality constant k for the magnetic brake power law equation (P = k · ω²). This is achieved by performing a series of controlled deceleration tests, ensuring results are accurate, repeatable, and dominated by the magnetic braking effect.

## Principle
When the flywheel is allowed to coast, its deceleration is caused by the sum of all retarding power components:
```
P_total = P_magnetic + P_bearing + P_air
```

To ensure the characterization of the magnetic brake, tests are conducted at high rotational speeds where:

* **P_magnetic** is large (proportional to speed, ω).

* **P_air** is small (proportional to ω², but negligible at these speeds).

* **P_bearing** is very small and approximately constant.

By conducting the test between high RPMs (750 RPM to 300 RPM), the deceleration is dominated by the magnetic brake, minimizing the relative error introduced by bearing friction.

Hence starting with the fundamental definition of power as the rate of change of energy:


$$ P = \frac{\Delta E}{\Delta t} $$

>Here, the energy change ΔE is the change in rotational kinetic energy.

$$= \frac{\frac{1}{2} I \omega_a^2 - \frac{1}{2} I \omega_b^2}{\Delta t}$$

$$= \frac{\frac{1}{2}  (\omega_a + \omega_b)(\omega_a - \omega_b) I}{\Delta t}$$

$$= \frac{I \omega_{avg} \Delta\omega}{\Delta t} \quad \cdots (1)$$
***
Since flywheel is has a fairly thick rim, with nost weight concentrated at the edges, we'll approximate the moment of inertia (I) to that of a solid disk:
$$I = \frac{1}{2} m r^2$$

$m = 6 \, \text{kg}$

$r = 140 \, \text{mm} = 0.14 \, \text{m}$

$\therefore I = 0.0588 \, \text{kg} \cdot \text{m}^2$
***

>The initial and final rotational speeds must be in the standard unit of radians per second (rad/s):

*Initial Speed,* $\omega_a = 750 \, \text{rpm} = 78.54 \, \text{rad/s}$

*Final Speed,* $\omega_b = 300 \, \text{rpm} = 31.42 \, \text{rad/s}$

$\therefore \omega_{avg} = 54.98 \, \text{rad/s}$, $\Delta\omega = 47.12 \, \text{rad/s}$



$$\text{From equation 1, power required to coast, } P = \frac{152.33}{\Delta t} \quad \cdots (2)$$
> the total change in rotational kinetic energy (ΔE) is calculated as **152.33 Joules**.
***

#### Deriving the Constant 'k'

Given the two expressions for Power (P):

$P =k \cdot \omega_{avg}^2 = \frac{152.33}{\Delta t}$


$k = \frac{152.33}{\Delta t \cdot \omega_{avg}^2}$

$k = \frac{152.33}{\Delta t \cdot (54.98)^2} = \frac{152.33}{\Delta t \cdot 3022.8}$

$k \approx \frac{0.050394}{\Delta t}$

> The units of **k** are $kg \cdot m^2/s$.

***


## Pre-Calibration Setup
Before beginning the calibration, we need to prepare the bike and the Raspberry Pi Pico to take accurate readings.

### Prepare the Pico:

If this is your first time using the Pico, follow the official getting started guide to install the MicroPython firmware and connect to your computer.

1. Power the Pico by plugging it into your computer's USB port.

2.  Access the Drivetrain:

    - Ensure the bike is not plugged into the power outlet
    - Remove the bike's pedals from their cranks.
    - Using a Phillips-head screwdriver, remove the plastic shell to expose the flywheel, belt, and internal components.

3. Test the Reed Switch:

    - Locate the reed switch that currently measures pedal cadence.
    - Disconnect its two terminals from the bike's main console.
    - Connect the two terminals to the Pico's GND and GPIO9 pins, respectively.
    - Open the `reed-cadence-core.py` file on your computer and run it on the Pico.
    - As you rotate the pedals, the Pico's logs should display the current cadence.
        ```
        Exercise Bike RPM Monitor with Averaging
        ========================================
        Practical RPM range: 0-120 RPM
        Press Ctrl+C to stop

        RPM:  72.4
        RPM:  69.8
        RPM:  71.5
        ```
4. Flywheel Sensor Mounting

   - Relocate the Sensor: Unscrew the reed switch from its pedal position and use tape to mount it to the bike's frame near the flywheel.
   - Relocate the Magnet: Remove the magnet from the pedal crank wheel and mount it on one of the flywheel's spokes. Place the magnet as close to the reed switch as practically possible without touching it.
   - Reduce Interference (Optional): To prevent stray magnetic fields from triggering the reed switch, you can wrap it with one or two layers of aluminum foil.
   - Final Check: Run the `reed-wheel-core.py` file on the Pico. As you rotate the pedals, the flywheel will spin, and the Pico's logs should display the flywheel's RPM.
        ```
        Exponential Smoothing RPM Monitor
        =================================
        Press Ctrl+C to stop

        RPM:   522.6
        RPM:   334.8
        RPM:   746.2
        ```

### The Coast-Down Test Procedure
With the flywheel sensor in place, you are ready to begin the core calibration test for each resistance level.

1. Set the Resistance: Connect the bike's power and set the resistance level to **1**.

2. Start the Test: Run the `reed-wheel-calibration.py` file on the Pico.

3. Perform Run 1:

   - Pedal until the flywheel's RPM exceeds **800 RPM**.

   - Stop pedaling. The flywheel will begin to slow down.

   - When the RPM hits **750**, a timer will start. The timer will stop when the RPM hits **300**. This is a single run.

   - The program will prompt you to begin the next run.

   - Complete the Test: Repeat this procedure for a total of five runs at resistance **level 1**.
   <img src="demo.gif" alt="Demo GIF" width="726" height="718">

   - Record Data: At the end of the **five** runs, the program will display the time for each run. Record these values in a spreadsheet.

   - Repeat for all Levels: Increase the resistance to the next **level (2-15)** and repeat the entire coast-down test procedure. You may repeat the test at any given level several times to ensure you get consistent values.


