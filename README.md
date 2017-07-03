
  Here are some tools that astronomers can use to deal with Fabry-Perot data.
  This is not yet a first version and new features will be added.

# Requirements

  This package uses Python 2.7 and the `astroconda` environment. If you do not
  have Anaconda installed in your computer yet, please, check the
  [Official Anaconda Webpage](https://www.continuum.io/downloads)
  with its documentation.

  The `astroconda` documentation is also online and can be found in the
  [Astroconda WebPage](https://astroconda.readthedocs.io/en/latest/).

# Get the source code

  You can download `fp_tools` using the link at the top of this page or clone
  it. The current release version is v0.2.2 and can be downloaded in the link
  below.

  * https://github.com/b1quint/fp_tools/archive/0.2.2.zip

  * https://github.com/b1quint/fp_tools/archive/0.2.2.tar.gz  

# Install

  Install the package using `pip` inside the `astroconda` VirtualEnv. To do so,
  open a terminal and do the following:
  
    $ cd /path/to/fp_tools  
    $ source activate astroconda  # activate the VirtualEnv
    $ pip install . --force-reinstall -I
    
  The `--force-reinstall` and the `-I` flags are needed only if you 
  are updating the code. If not, you can ommit them.

# Run 

  After installing the `fp_repeat` and the `fp_cut` will be available
  anywhere in your system, **as long as you have the `astroconda` VirtualEnv
  activated**. To check how to use them, simply use the conventional help:
  
    $ fp_repeat --help
    
  or
  
    $ fp_repeat -h
    
  For example, give the user the following output:
  
    Repeats a data-cube [N] times.

    positional arguments:
      input_cube           Input cube.
      output_cube          Output cube.

    optional arguments:
      -h, --help           show this help message and exit
      --n_before N_BEFORE  Add 'n' copies of the cube in its beginning (affects
                       header).
      --n_after N_AFTER    Add 'n' copies of the cube in its end (affects header).
  
# Any problem?

  If you have any problem downloading/installing `fp_tools` you can 
  either contact me (bquint at ctio dot noao dot edu) or create an Issue. 
  The second way is prefered so I can have a track of all the problems (and
  so other users).
  
  To create an issue, simply [click here](https://github.com/b1quint/fp_tools/issues/new).
