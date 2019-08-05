"""Provides a class to plot positions and voltages for birefringent filter scans."""

import multiprocessing

import matplotlib.pyplot as plt


class BirefringentFilterScanPlotProcess(multiprocessing.Process):
    def __init__(self, positions, voltages, smoothed_data, maxima, old_pos, best_pos, using_new_pos, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.positions = positions
        self.voltages = voltages
        self.smoothed_data = smoothed_data
        self.maxima = maxima
        self.old_pos = old_pos
        self.best_pos = best_pos
        self.using_new_pos = using_new_pos

    def run(self):
        self.plot_birefringent_scan(self.positions, self.voltages, self.smoothed_data)
        self.plot_birefringent_selection(self.old_pos, self.best_pos)
        self.plot_birefringent_maxima(self.positions[self.maxima], self.smoothed_data[self.maxima])
        self.add_bifi_scan_legend()
        plt.show()

    def plot_birefringent_scan(self, positions, voltages, smoothed_voltages):
        plt.figure()
        plt.cla()
        plt.title('Power Diode Voltage vs. BiFi Motor Position')
        plt.xlim(positions[0], positions[-1])
        plt.xlabel('Position')
        plt.ylabel('Voltage (V)')
        plt.plot(positions, voltages)
        plt.plot(positions, smoothed_voltages)

    def plot_birefringent_maxima(self, positions, voltages):
        plt.plot(positions, voltages, 'r*')

    def plot_birefringent_selection(self, old_pos, new_pos):
        plt.axvline(old_pos, 0, 1, color='r', linestyle='--')
        if self.using_new_pos:
            plt.axvline(new_pos, 0, 1, color='r', linestyle='-')

    def add_bifi_scan_legend(self):
        names = ['Raw', 'Smoothed', 'Old Pos']
        if self.using_new_pos:
            names.append('New Pos')
        plt.legend(names, loc='upper left')
