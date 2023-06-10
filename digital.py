"""
Generates a square wave with ADALM2000 50% duty cycle at 60hz with 5V amplitude
"""
from time import sleep

import libm2k
import numpy as np
import matplotlib.pyplot as plt

maxV = 5.0  # 5V
frequency = 120.0  # 6Hz
sample_rate = 7500  # Number of samples per second
t = np.linspace(0, 1.0 / frequency, sample_rate, endpoint=False)  # Time array
plotting = True

def square_wave(A, w):
    return A * np.sign(np.sin(2 * np.pi * w * t))


def plot_input(anal_in, duration=1 / sample_rate * 100):
    if not plotting:
        return
    # plot the inputted magnitude
    time_x = np.linspace(0, duration, int(duration * sample_rate))
    V0 = anal_in.getSamples(int(duration * sample_rate))
    plt.plot(time_x, np.array(V0[0]))
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [V]')
    plt.title('Input Voltage vs Time [Analog In Channel 1]')
    plt.show()
    print(duration)


# Open the first available device
devices = libm2k.getAllContexts()

# if no devices are found, exit the program
if len(devices) == 0:
    print("No devices found")
    exit()

board = libm2k.m2kOpen(devices[0])

# # ask if the device is calibrated in console
# print("Is the device calibrated? (y/n)")
# calibrated = input()
#
# # if the device is not calibrated, calibrate it
# if calibrated == "n":
#     board.calibrateADC()
#     board.calibrateDAC()

# open first output channel
dout = board.getDigital()
dout.setSampleRateOut(sample_rate)
dout.setOutputMode(libm2k.DIO_CHANNEL_0, libm2k.DIO_OUTPUT)
dout.enableChannel(0, True)

# open first input channel
ain = board.getAnalogIn()
ain.setSampleRate(sample_rate)
ain.enableChannel(libm2k.ANALOG_IN_CHANNEL_1, True)
ain.setRange(libm2k.ANALOG_IN_CHANNEL_1, -6, 6)

buffer = square_wave(maxV, frequency)  # Square wave array
buffer = (buffer > 0).astype(int)  # Convert to binary
buffer = buffer << 0

#
plt.plot(t, buffer)
plt.xlabel('Time [s]')
plt.ylabel('Amplitude [V]')
plt.title('First Buffer')
plt.show()
# set the waveform generator to output a square wave
dout.push(buffer.tolist())

# console input for magnitude of square wave
plot_input(ain)

while True:
    try:
        print("Enter the percent dimming, Q to quit: ")
        magnitude = input()
        if not magnitude.isalpha() and 0 <= int(magnitude) <= 100:
            new_amplitude = maxV * float(magnitude) / 100
            print("Voltage: {}".format(new_amplitude))
        elif magnitude.upper() == "Q":
            # close the context
            # board.contextClose()
            break
        else:
            print("Invalid input")
            continue

        # set the waveform generator to output a square wave
        dout.stopBufferOut()
        buffer = square_wave(new_amplitude, frequency)
        buffer = (buffer > 0).astype(int)  # Convert to binary
        buffer = buffer << 0
        dout.push(buffer.tolist())

        plot_input(ain)
    except Exception as e:
        print("An error occurred: ", str(e))

plot_input(ain)
dout.stopAcquisition()
dout.enableChannel(0, False)
libm2k.contextClose(board)
