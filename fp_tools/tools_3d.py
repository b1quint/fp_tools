import itertools
import logging
import multiprocessing
import threading
import sys

from astropy.io import fits
import numpy as np


# noinspection PyUnusedLocal,PyUnusedLocal
def signal_handler(s, frame):
    sys.exit()


class ZCut(threading.Thread):
    """
    Extract a part of the data-cube in the spectral direction and keeping the
    whole spatial pixels. The header is updated to maintain the calibration
    in the same direction.

    Parameters
    ----------
        _input : str
            The input cube filename.

        _output : str
            The output cube filename.

        n_begin : int
            The channel that will be considered as the first new one
            (inclusive).

        n_end : int
            The channel that will be considered as the last new one
            (exclusive).
    """
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


class ZOversample(threading.Thread):
    """
    Oversample a data-cube in the spectral direction using linear fitting.

    Parameters
    ----------
        _input : str
            The input cube filename

        _output : str
            The output cube filename

        oversample_factor : int
            The oversample factor. In other words, how many points will be added
            for each original point.
    """
    def __init__(self, _input, _output, oversample_factor):

        threading.Thread.__init__(self)

        self.input = _input
        self.output = _output
        self.oversample_factor = oversample_factor

    def run(self):

        # Read data
        data = fits.getdata(self.input)
        header = fits.getheader(self.input)

        # Extract information
        depth, height, width = data.shape

        new_depth = self.oversample_factor * depth # - (self.oversample_factor - 1)
        print(new_depth)

        assert(isinstance(new_depth, int))
        del data

        x = np.arange(header['NAXIS1'], dtype=int)
        y = np.arange(header['NAXIS2'], dtype=int)

        # Keep the terminal alive
        loading = multiprocessing.Process(target=stand_by, name="stand_by")
        loading.start()

        # Create a pool for subprocesses
        p = multiprocessing.Pool(4)
        results = None
        fitter = OverSampler(self.input, new_depth)

        try:
            results = p.map_async(fitter, itertools.product(x, y)).get(99999999)
        except KeyboardInterrupt:
            print('\n\nYou pressed Ctrl+C!')
            print('Leaving now. Bye!\n')
            pass

        # Closing processes
        p.close()
        p.join()
        loading.terminate()

        # Fix header
        keys = ['CDELT3', 'C3_3', 'PHMSAMP']
        for key in keys:
            try:
                header[key] /= self.oversample_factor
            except KeyError:
                print(' {:s} key is not present in the header.'.format(key))

        try:
            header['CRPIX3'] *= self.oversample_factor
        except KeyError:
            print(' {:s} key is not present in the header.'.format('CRPIX3'))

        x = int(header['NAXIS1'])
        y = int(header['NAXIS2'])
        results = np.array(results)
        results = results.reshape((x, y, new_depth))
        results = np.transpose(results, axes=[2, 1, 0])

        fits.writeto(self.output, results, header)


class ZRepeat(threading.Thread):
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
            hdr['CRPIX3'] += (self.n_before * data.shape[0])
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


class OverSampler:

    def __init__(self, filename, new_size):
        """
        Parameter
        ---------
            filename : str
                Relative or absolute path to the file that contains a data-cube
                from where the 2D maps will be extracted through gaussian
                fitting.
        """
        self._filename = filename
        self.new_size = new_size

        # Load the data
        self.data = fits.getdata(self._filename, memmap=True)

    def __call__(self, indexes):
        """
        Parameter
        ---------
            indexes : tuple
                Contains two integers that correspond to the X and Y indexes
                that will be used to extract the spectrum from the data-cube and
                fits a gaussian to this extracted spectrum.
        Returns
        -------
            results : list
                A list containing the numerical values of the three gaussian
                parameters met in the fitting processes `peak`, `mean` and
                `stddev`.
        """
        i, j = indexes

        # Get the usefull information
        s = self.data[:, j, i]

        # Create new Z
        z = np.arange(s.size)
        z_interpolation = np.linspace(0, s.size, self.new_size)

        # Interpolate
        new_s = np.interp(z_interpolation, z, s)

        return new_s


def stand_by(level=logging.NOTSET):
    """
    A silly method that keeps the terminal alive so the user knows that
    this programs is still running. :-)
    """
    from time import sleep

    output = ['/', '-', '\\', '|']
    i = 0

    if level in [logging.NOTSET, logging.WARN, logging.ERROR]:
        return

    while True:
        sys.stdout.write("\r [{:s}]".format(output[i]))
        sys.stdout.flush()
        sleep(0.5)
        i += 1
        i %= 4

    return