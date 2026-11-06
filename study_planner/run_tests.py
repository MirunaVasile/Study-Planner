import unittest
import sys

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = loader.discover('teste')

    runner = unittest.TextTestRunner(stream=sys.stdout, verbosity=2)
    runner.run(suite)