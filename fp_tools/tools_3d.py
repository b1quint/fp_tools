import threading
import sys

from astropy.io import fits
import numpy as np


class z_repeat(threading.Thread):
    """
    Repeat a data-cube in the spectral direction (Z).
    """
    def __init__(self, _input, _output, n_before=0, n_after=0):
        threading.Thread.__init__(self)

        self.input = _input
        self.output = _output
        self.n_before = n_before
        self.n_after = n_after

    def run(self):

        my_str = '\nRead data from: {0.input:s}\n' + \
                 'Write file to: {0.output:s}\n' + \
                 'Add {0.n_before:d} FSR at the beginning of the cube\n' + \
                 'Add {0.n_after:d} FSR at the end the cube\n'

        print(my_str.format(self))

        # Read data
        data = fits.getdata(self.input)
        hdr = fits.getheader(self.input)

        depth, height, width = data.shape

        # Repeat data
        i = 0
        temp_before = data
        while i < self.n_before:
            temp_before = np.vstack((data, temp_before))
            i += 1

        i = 0
        temp_after = temp_before
        while i < self.n_after:
            temp_after = np.vstack((temp_after, data))
            i += 1

        hdr['CRPIX3'] += self.n_before * depth

        if self.n_before != 0:
            hdr.add_history('Added %i cube copies at the beginning.' %
                            self.n_before)

        if self.n_after != 0:
            hdr.add_history('Added %i cube copies at the end.' %
                            self.n_after)

        # Write file
        fits.writeto(self.output, temp_after, hdr)


class z_cut(threading.Thread):

    def __init__(self, _input, _output, n_begin=None, n_end=None):

        threading.Thread.__init__(self)

        self._input = _input
        self._output = _output
        self.n_begin = n_begin
        self.n_end = n_end

    def run(self):

        data = fits.getdata(self._input)
        header = fits.getheader(self._input)

        if self.n_begin is not None:
            data = data[self.n_begin:]
            header['CRPIX3'] -= (self.n_begin + 1)
        else:
            self.n_begin = 0

        if self.n_end is not None:
            data = data[:self.n_end]
        else:
            self.n_end = self.data.shape[0]

        header.add_history('Cube cut from z = %i to z = %i' %
                           (self.n_begin, self.n_end))

        fits.writeto(self._output, data, header)
