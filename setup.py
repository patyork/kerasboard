from setuptools import setup
from setuptools import find_packages


setup(name='KerasBoard',
      version='0.1.0',
      description='Realtime Monitoring, Logging, and Interaction for Keras',
      author='Pat York',
      author_email='pat.york@nevada.unr.edu',
      url='https://github.com/patyork/kerasboard',
      license='MIT',
      install_requires=['keras', 'requests', 'tornado'],
      packages=find_packages())