# setup.py
from setuptools import setup, find_packages
import os

# Function to recursively include all files in the 'drive' directory
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('zlg_can/drive')

setup(
    name='python-can-zlgcan',
    version='2.1.0',
    packages=find_packages(),
    install_requires=[
        'python-can'
    ],
    entry_points={
        'can.interface': [
            'zlgcan = zlg_can.zlgcan_backend:ZLGCANBus'
        ]
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='ZLGCAN backend for python-can',
    url='https://github.com/yourusername/python-can-zlgcan',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    package_data={
        'zlg_can': extra_files,
    },
    include_package_data=True,
)