from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Ukaton Mission Python SDK'
LONG_DESCRIPTION = 'Access the Ukaton Missions in python via BLE or UDP'

# Setting up
setup(
    name="UkatonMissionSDK",
    version=VERSION,
    author="Zack Qattan",
    author_email="<zack@ukaton.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'

    keywords=['python', 'ble', 'udp'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
