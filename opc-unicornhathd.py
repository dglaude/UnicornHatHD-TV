#!/usr/bin/python
#
# Open Pixel Control protocol (Fadecandy) for Pimoroni Unicorn Hat HD
#
# Display up to 16 by 16 RGB pixels, but can be limited to the first 9 lines to match 16:9 TV aspect ratio
#
# Original code from Artnet-server from PaulWebster with support for Mote and Unicorn HAT with Artnet and OPC protocol
# License: MIT
from __future__ import print_function

# This could be replaced by Unicorn Hat HD simulator if the hardware is missing
import unicornhathd as unicorn
    
from twisted.internet import protocol, endpoints
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor

### Avoiding numpy for no reason (seems only used for np.array_equal to compare request to previous request)
# import numpy as np

import sys
if sys.version_info[0] < 3:
    oldPython = True
else:
    oldPython = False

# 16x16 grid
x_max = 16 
y_max = 16

# Adjust the LED brightness as needed.
unicorn.brightness(1)

class OPC(protocol.Protocol):
    # Parse Open Pixel Control protocol. See http://openpixelcontrol.org/
    parseState = 0
    pktChannel = 0
    pktCommand = 0
    pktLength = 0
    pktCount = 0
    pixelCount = 0
    pixelLimit = 0
### Avoiding numpy for no reason (seems only used for np.array_equal to compare request to previous request)
#    lastSet = []    # Hold copy of last set of LEDs sent
    MAX_LEDS = x_max * y_max

    def dataReceived(self, data):
        if oldPython:
            rawbytes = map(ord, data) ## need to work on this to make it safe for Python 2 and 3
        else:
            rawbytes = data ## "map" changed in Python3 - in theory list(map()) should have worked but did not

        OPC.pktCount += 1
        #print("len(rawbytes) %d" % len(rawbytes))
        #print("Packet count %d" % OPC.pktCount)
        #print(rawbytes)

### Avoiding numpy for no reason (seems only used for np.array_equal to compare request to previous request)
#        if (np.array_equal(OPC.lastSet, rawbytes)):
#            # New data is same as last so skip it to save work since LEDs retain last value
#            i = len(rawbytes)    # Set to force skip of processing below
#            # print("Same data as before")
#        else:
#            OPC.lastSet = rawbytes    # Assume this set will be sent
#            i = 0    # Force this set to be processed
        i = 0		# Avoiding numpy for no reason (seems already needed in Unicorn Hat HD)
       
        while (i < len(rawbytes)):
            #print("parseState %d i %d" % (OPC.parseState, i))
            if (OPC.parseState == 0):   # get OPC.pktChannel
                OPC.pktChannel = rawbytes[i]
                i += 1
                OPC.parseState += 1
            elif (OPC.parseState == 1): # get OPC.pktCommand
                OPC.pktCommand = rawbytes[i]
                i += 1
                OPC.parseState += 1
            elif (OPC.parseState == 2): # get OPC.pktLength.highbyte
                OPC.pktLength = rawbytes[i] << 8
                i += 1
                OPC.parseState += 1
            elif (OPC.parseState == 3): # get OPC.pktLength.lowbyte
                OPC.pktLength |= rawbytes[i]
                i += 1
                OPC.parseState += 1
                OPC.pixelCount = 0
                OPC.pixelLimit = min(3*OPC.MAX_LEDS, OPC.pktLength)
                #print("OPC.pktChannel %d OPC.pktCommand %d OPC.pktLength %d OPC.pixelLimit %d" % \
                #    (OPC.pktChannel, OPC.pktCommand, OPC.pktLength, OPC.pixelLimit))
                if (OPC.pktLength > 3*OPC.MAX_LEDS):
                    print("Received pixel packet exeeds size of buffer! Data discarded.")
                if (OPC.pixelLimit == 0):
                    OPC.parseState = 0
            elif (OPC.parseState == 4):
                copyBytes = min(OPC.pixelLimit - OPC.pixelCount, len(rawbytes) - i)
                if (copyBytes > 0):
                    OPC.pixelCount += copyBytes
                    #print("OPC.pixelLimit %d OPC.pixelCount %d copyBytes %d" % \
                    #        (OPC.pixelLimit, OPC.pixelCount, copyBytes))
                    if ((OPC.pktCommand == 0) and (OPC.pktChannel <= 1)):
                        x = 1
                        y = 1
                        iLimit = i + copyBytes
                        while ((i < iLimit) and (y <= y_max)):
                            #print("i %d" % (i))
                            r = rawbytes[i]
                            i += 1
                            g = rawbytes[i]
                            i += 1
                            b = rawbytes[i]
                            i += 1
                            #print("x %d y %d r %d g %d b %d" % (x,y,r,g,b))
                            # unicorn.set_pixel(x-1, y-1, r, g, b)
                            unicorn.set_pixel(16-x, y-1, r, g, b)

                            x += 1
                            if (x > x_max):
                                x = 1
                                y += 1

                        if (OPC.pixelCount >= OPC.pixelLimit):
                            unicorn.show()
                    else:
                        i += copyBytes
                    if (OPC.pixelCount == OPC.pktLength):
                        OPC.parseState = 0
                    else:
                        OPC.parseState += 1
            elif (OPC.parseState == 5):
                discardBytes = min(OPC.pktLength - OPC.pixelLimit, len(rawbytes) - i)
                print("discardBytes %d" % (discardBytes))
                OPC.pixelCount += discardBytes
                i += discardBytes
                if (OPC.pixelCount >= OPC.pktLength):
                    OPC.parseState = 0
                if (discardBytes == 0):
                    OPC.parseState = 0
                    print("Unexpected 0 bytes to discard")
            else:
                print("Invalid OPC.parseState %d" % (OPC.parseState))


class OPCFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return OPC()

endpoints.serverFromString(reactor, "tcp:7890").listen(OPCFactory())
reactor.run()

