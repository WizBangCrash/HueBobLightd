# HueBobLightd
A python version of boblightd for managing hue lights in conjunction
with [MrMC](https://mrmc.tv) LightEffects option (or any other light effects software that uses
the boblightd protocol)


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
Has currently been tested on; macOS, Windows 7 & 10, Synology DSM 6.1

## Installation
- Requires Python3 and PIP to be installed
- Requires an authorised Hue Bridge username
- A python _wheel_ package can be found in the release directory
  - Install using "pip3 install HueBobLightd"
  - *OR* clone the respository and do do you own thing

### Installation on Synology DSM
The hueboblightd server can be installed an run from a Synology DSM.
Follow the notes and instructions in the _synology_ directory.

# Configuration File
The configuration file is a bit simpler than the standard boblightd.conf as there
are less options supported by the Hue lights.

<<<<<<< HEAD
``` json
=======
'''json
>>>>>>> c4e3f90414f2b7309e8158565c72683e32d08173
{
    /// Socket server details
    ///     port: port number the server will listen on
    ///     address: (optional) IPv4 address the server will listen on
    "server" : {
        "port" : 19333
    },

    /// Details of the Hue Bridge
    ///     name: Friendly name used by software for log messages
    ///     address: Domain name or ip address of Bridge
    ///     username: A pre-authorised user name for accessing the Bridge
    ///         For details on creating a user see:
    ///         https://www.developers.meethue.com/documentation/getting-started
    "hueBridge" : {
        "name" : "MyHueBridge",
        "address" : "192.168.1.1",
        "username" : "<hue bridge pre-authorised user name>"
    },
    /*
        lights : An array of Hue lights and the screen coordinates they cover
            id : Hur Bridge light id
            name : Hue light name
            gamut : (optional) gamut of light e.g. GamutA, GamutB or GamutC
            hscan : left and right values expressed as a percentage
            vscan : top and bottom values expressed as a percentage
        e.g. A light that covers the bottom right quadrant of the display:
            "name" : "right",
            "gamut" : "GamutC"
            "hscan" : { "left" : 50, "right" : 100 },
            "vscan" : { "top" : 50, "bottom" : 100 }
    */
    "lights" : [
        {
            "id" : "1",
            "name" : "RightLight",
            "gamut" : "GamutA",
            "hscan" : { "left" : 75, "right" : 100 },
            "vscan" : { "top" : 65, "bottom" : 100 }
        },
        {
            "id" : "2",
            "name" : "LeftLight",
            "gamut" : "GamutA",
            "hscan" : { "left" : 0, "right" : 25 },
            "vscan" : { "top" : 65, "bottom" : 100 }
        },
        {
            "id" : "7",
            "name" : "StripLight",
            "gamut" : "GamutC",
            "hscan" : { "left" : 0, "right" : 100 },
            "vscan" : { "top" : 0, "bottom" : 20 }
        }
    ]
}
<<<<<<< HEAD
```
=======
'''
>>>>>>> c4e3f90414f2b7309e8158565c72683e32d08173
