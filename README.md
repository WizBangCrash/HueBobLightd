# HueBobLightd
A python version of boblightd for managing hue lights in conjunction
with MrMC LightEffects option (or any other light effects software that uses
the boblightd protocol)

MrMC can be found here: https://mrmc.tv

After spending some time trying out a number of different flavous of boblightd
implementations (hyperion being the most successful). I deciced to write my own
daemon to fully support Philips Hue Lights.
Most other implementations are focussed on fast reacting LED light strips with
dedicated hardware. Hue lights are great and very versatile, but not _'fast'_, so I needed to create a server that would accept the light change requests as fast as they arrive from the device displaying the video content, but deliver them at a speed that would not _upset_ the Hue light bridge.

It's an early stage implementation, but it works. Feel free to try.

## Features

- Configurable port (default: 19333)
- Support for full range of Hue Lights
- Support for Hue light gamuts
- Multi-threaded
- Manages Hue Bridge HTTP request limitations

## Supported Platforms
Written in Python with the aim to support as many platforms as possible.
Has currenlty been tested on; macOS, Windows 7 & 10, Synology DSM 6.1

## Installation
- Requires Python3 and PIP to be installed
- Requires an authorised Hue Bridge username
- A python _wheel_ package can be found in the release directory
  - Install using "pip3 install HueBobLightd"
  - *OR* clone the respository and do do you own thing

### Installation on Synology DSM
The hueboblightd server can be installed an run from a Synology DSM.
Follow the notes and instructions in the _synology_ directory.