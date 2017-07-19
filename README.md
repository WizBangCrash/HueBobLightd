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
- Support for full range of hue Lights
- Support for hue light gamuts
- Multi-threaded
- Manages hue Bridge HTTP request limitations
- Ability to set light transition time and default brightness
- Ability to restart re-read config file without restarting server

## Changes

* 22nd July 2017: v1.1.0
  * Refactoring to improve code structure
  * SIGHUP signal support to re-read configuration file
  * Lights are validated and ignored if not present on bridge
  * Support for multiple hue bridges 
  * Optional initial "brightness" parameter added
  * Optional "transitiontime" parameter added
* 17th July 2017: v1.0.2 - Initial GitHub release

## Supported Platforms
Written in Python with the aim to support as many platforms as possible.
Has currently been tested on; macOS, Windows 7 & 10, Synology DSM 6.1

## Installation
- Requires Python3 and PIP to be installed
- Requires an authorised hue Bridge username
- A python _wheel_ package can be found in the release directory
  - Install using "pip3 install HueBobLightd"
  - *OR* clone the respository and do do your own thing

### Installation on Synology DSM
The hueboblightd server can be installed an run from a Synology DSM.
Follow the notes and instructions in the _synology_ directory.

# Configuration File
The configuration file is a bit simpler than the standard boblightd.conf as there
are less options supported by the hue lights.
The configuration supports multiple hue bridges for those with _mega_ hue
light networks :-)

``` javascript
{
    /// Socket server details
    ///     port: port number the server will listen on
    ///     address: (optional) IPv4 address the server will listen on
    "server" : {
        "port" : 19333
    },

    /// Tranistion time:
    /// Philips hue lights need time to transition from 1 color
    /// to the next. Here you can choose how long in multiples of 100ms
    /// Valida values: 1 to 10 (default: 3)
    "transitiontime" : 3,

    /// Details of the Hue Bridge
    ///     name: Friendly name used by software for log messages
    ///     address: Domain name or ip address of Bridge
    ///     username: A pre-authorised user name for accessing the Bridge
    ///         For details on creating a user see:
    ///         https://www.developers.meethue.com/documentation/getting-started
    /// bridges is a list of available bridges and the lights assciated with each
    ///
    "bridges" : [
        {
            "name" : "MyHueBridge",
            "address" : "192.168.1.1",
            "username" : "<hue bridge pre-authorised user name>",
            ///
            ///    lights : An array of Hue lights & their screen coordinates
            ///        id : Hur Bridge light id
            ///        name : Hue light name
            ///        gamut : (optional) gamut of light e.g. GamutA, GamutB or GamutC
            ///        brightness : Brightness value: 1-254 (default: 150)
            ///        hscan : left and right values expressed as a percentage
            ///        vscan : top and bottom values expressed as a percentage
            ///    e.g. A light that covers the bottom right quadrant of the display:
            ///        "name" : "right",
            ///        "gamut" : "GamutC"
            ///        "hscan" : { "left" : 50, "right" : 100 },
            ///        "vscan" : { "top" : 50, "bottom" : 100 }
            ///
            "lights" : [
                {
                    "id" : "1",
                    "name" : "RightLight",
                    "gamut" : "GamutA",
                    "brightness" : 100,
                    "hscan" : { "left" : 75, "right" : 100 },
                    "vscan" : { "top" : 50, "bottom" : 100 }
                },
                {
                    "id" : "2",
                    "name" : "LeftLight",
                    "gamut" : "GamutA",
                    "hscan" : { "left" : 0, "right" : 25 },
                    "vscan" : { "top" : 50, "bottom" : 100 }
                },
                {
                    "id" : "7",
                    "name" : "StripLight",
                    "gamut" : "GamutC",
                    "brightness" : 100,
                    "hscan" : { "left" : 25, "right" : 75 },
                    "vscan" : { "top" : 25, "bottom" : 75 }
                }
            ]
        }
    ]
}
```

## License

[MIT](https://github.com/yhirose/vscode-filtertext/blob/master/LICENSE)
