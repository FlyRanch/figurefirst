Installation
=============
* To get access to the very latest features and bugfixes, clone figurefirst from
  github::
      
      $ git clone https://github.com/FlyRanch/figurefirst.git
      
  Now you can install figurefirst from the source::
      
      $ python setup.py install

  To install the inkscape extensions you will need to copy the .inx and .py files from the ``inkscape_extensions directory`` to the appropriate path for inkscape extensions on your system. This is probably ``~/.config/inkscape/extensions/`` on linux/osx or ``C:\Program Files\Inkscape\share\extensions`` on windows.

Requrements
===========

Figurefirst depends on:

* Python 2.7 or Python 3.x
* numpy
* matplotlib