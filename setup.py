#!/usr/bin/env python

import os
import shutil
from pathlib import Path
from setuptools import setup
from setuptools import find_packages
from setuptools.command.install import install
import subprocess

directory = os.path.abspath(os.path.dirname(__file__))

config_directory = os.path.join(str(Path.home()), '.config/cimage')
Path(config_directory).mkdir(parents=True, exist_ok=True)
config_path = os.path.join(config_directory, 'config')
if not os.path.exists(config_path):
    shutil.copyfile(os.path.join(directory, 'config.py'), config_path)

with open(os.path.join(directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='cimage',
      version='1.0',
      description='Command Line Image Viewer Written in Python',
      author='Göktuğ Karakaşlı',
      license='MIT',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/goktug97/cimage',
      packages=['image_size'],
      package_dir={'cimage': '.'},
      py_modules=[os.path.splitext(os.path.basename(path))[0]
                  for path in ['cimage', 'config']],
      entry_points={
              'console_scripts': [
                  'cimage = cimage:main',
              ]
          },
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: Linux",
      ],
      install_requires=[
          'ueberzug',
      ],
      python_requires='>=3.6',
      include_package_data=True)
