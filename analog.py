"""
Failed Attempt
Generates a square wave with ADALM2000 50% duty cycle at 60hz with 5V amplitude
"""
import libm2k
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp


class Analog:
    def __init__(self, maxV=2.5, minV=0., frequency=200, sample_rate=70000, plotting=False, cyclic=False):
        devices = libm2k.getAllContexts()

        # if no devices are found, exit the program
        if len(devices) == 0:
            print("No devices found")
            exit()
        # Open the first available device
        self.board = libm2k.m2kOpen(devices[0])
        # Connect to analog output
        self.aout = self.board.getAnalogOut()
        self.aout.setCyclic(cyclic)
        self.aout.setSampleRate(0, sample_rate)
        self.aout.enableChannel(0, True)
        # Connect to analog input
        self.ain = self.board.getAnalogIn()
        self.ain.setSampleRate(sample_rate)
        self.ain.enableChannel(libm2k.ANALOG_IN_CHANNEL_1, True)
        self.ain.setRange(libm2k.ANALOG_IN_CHANNEL_1, -6, 6)

        self.maxV = maxV
        self.minV = minV
        self.currentV = maxV
        self.frequency = frequency  # 6Hz
        self.sample_rate = sample_rate  # Number of samples per second
        self.t = np.linspace(0, 1.0 / self.frequency, int(self.sample_rate / self.frequency),
                             endpoint=False)  # Time array
        self.plotting = plotting
        self.cyclic = cyclic

    def square_wave(self, A, w):
        return A * np.sign(np.sin(2 * np.pi * w * self.t))

    def plot_input(self):
        # plot analog input 0
        if not self.plotting:
            return
        duration = 1 / self.frequency * 5000
        # plot the inputted magnitude
        time_x = np.linspace(0, duration, int(duration * self.sample_rate))
        V0 = self.ain.getSamples(int(duration * self.sample_rate))
        plt.plot(time_x, np.array(V0[0]))
        plt.xlabel('Time [s]')
        plt.ylabel('Amplitude [V]')
        plt.title('Input Voltage vs Time [Analog In Channel 1]')
        plt.show()

    def update(self, V):
        """
        Updates the waveform generator to output a square wave with the given parameters
        :param anal_out: analog output
        :param anal_in: analog input
        :param V: voltage peak to peak
        :param w: frequency
        :return: none
        """
        # anal_out.cancelBuffer(0)
        self.currentV = V
        buffer_ = self.square_wave(V, self.frequency)
        self.aout.push([buffer_.tolist()])
        self.plot_input()
        # plt.plot(t, buffer_)
        # plt.show()

    def raw_update(self, V, event):
        """
        Updates the waveform generator to output a square wave with the given parameters
        NEEDED because buffer blanking
        :param anal_out: analog output
        :param anal_in: analog input
        :param V: voltage peak to peak
        :param w: frequency
        :return: none
        """
        # anal_out.cancelBuffer(0)
        self.currentV = V
        buffer_ = self.square_wave(V, self.frequency)
        while not event.is_set():
            if self.aout.isPushDone():
                self.aout.push([buffer_.tolist()])

    def start(self):
        # # Open the first available device
        # devices = libm2k.getAllContexts()
        #
        # # if no devices are found, exit the program
        # if len(devices) == 0:
        #     print("No devices found")
        #     exit()
        #
        # board = libm2k.m2kOpen(devices[0])

        # # ask if the device is calibrated in console
        # print("Is the device calibrated? (y/n)")
        # calibrated = input()
        #
        # # if the device is not calibrated, calibrate it
        # if calibrated == "n":
        #     board.calibrateADC()
        #     board.calibrateDAC()

        # # open first output channel
        # aout = board.getAnalogOut()
        # aout.setCyclic(True)
        # aout.setSampleRate(0, sample_rate)
        # aout.enableChannel(0, True)
        #
        # # open first input channel
        # ain = board.getAnalogIn()
        # ain.setSampleRate(sample_rate)
        # ain.enableChannel(libm2k.ANALOG_IN_CHANNEL_1, True)
        # ain.setRange(libm2k.ANALOG_IN_CHANNEL_1, -6, 6)

        # initialize the waveform generator
        buffer = self.square_wave(self.maxV, self.frequency)
        self.aout.push([buffer.tolist()])
        self.plot_input()

    def stop(self):
        self.aout.stop()
        self.aout.enableChannel(0, False)
        libm2k.contextClose(self.board)

    def voltage_listner(self, V, event):
        while True:
            if V != self.currentV:
                self.currentV = V
                return


if __name__ == "__main__":
    an = Analog()
    an.start()
    while True:
        try:
            print("Enter the percent dimming, Q to quit: ")
            magnitude = input()
            if not magnitude.isalpha() and 0 <= int(magnitude) <= 100:
                new_amplitude = mp.Value((an.maxV - an.minV) * float(magnitude) / 100 + an.minV)
                print("Voltage: {}".format(new_amplitude))
            elif magnitude.upper() == "Q":
                # close the context
                # board.contextClose()
                break
            else:
                print("Invalid input")
                continue

            # set the waveform generator to output a square wave
            # aout.cancelBuffer(0)
            # buffer = square_wave(new_amplitude, frequency)
            # aout.push([buffer.tolist()])

            an.update(new_amplitude)

            # multithreading
            # event = mp.Event()
            #
            # p1 = mp.Process(target=an.voltage_listner, args=(new_amplitude))
            # p2 = mp.Process(target=an.raw_update, args=(event, new_amplitude))
            # p1.start()
            # p2.start()
            # p1.join()
            # p2.join()

        except Exception as e:
            print("An error occurred: ", str(e))

    an.stop()
