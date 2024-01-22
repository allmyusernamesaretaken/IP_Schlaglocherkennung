#!/usr/bin/python3

# Copyright (C) 2018 Infineon Technologies & pmdtechnologies ag
#
# THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY
# KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

"""This sample shows how to record data to an .rrf file.

This sample uses Royale's feature of stopping after a given number of
frames are captured, therefore the --frames argument is required.
"""

import queue

import roypy


class MyListener(roypy.IRecordStopListener):
    """A simple listener, in which waitForStop() blocks until onRecordingStopped has been called."""

    def __init__(self):
        super(MyListener, self).__init__()
        self.queue = queue.Queue()

    def onRecordingStopped(self, frameCount):
        self.queue.put(frameCount)

    def waitForStop(self):
        frameCount = self.queue.get()
        print("Stopped after capturing {frameCount} frames".format(frameCount=frameCount))

