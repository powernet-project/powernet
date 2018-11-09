"""
    Setup a listener for Philips hue lightbulb changes
"""
from __future__ import print_function

__author__ = 'Jonathan G. & Gustavo C.'
__copyright__ = 'Stanford University'
__version__ = '0.2'
__email__ = 'jongon@stanford.edu'
__status__ = 'Prototype'

def initialize_home_hub():
    print('Soon we\'ll have everything up and running')


if __name__ == '__main__':
    try:
        initialize_home_hub()
    except Exception as exc:
        print('Uh-oh we had an exception', exc)