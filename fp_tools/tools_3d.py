import threading

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

        # Read data
        data = fits.getdata(self.input)
        hdr = fits.getheader(self.input)

        # Update header
        hdr['CRPIX3'] += (self.n_before * data.shape[0]) + 1

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
            header['CRPIX3'] -= self.n_begin

        if self.n_end is not None:
            data = data[:self.n_end]

        fits.writeto(self._output, data, header)
