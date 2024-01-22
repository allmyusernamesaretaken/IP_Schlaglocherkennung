#!/usr/bin/python3

import roypy


class MyListener(roypy.IDepthDataListener):
    def __init__(self, frames, output):
        super(MyListener, self).__init__()
        self.outputName = output
        self.frameNumber = 0
        self.totalFrames = frames
        self.done = False

    """
    writes the ply file
    """
    def onNewData(self, data):
        numPoints = data.getNumPoints()

        self.frameNumber += 1
        if self.frameNumber == self.totalFrames:
            self.done = True
        #if os.path.exists(str(self.outputName) + ".ply"):
        #    return
        filename = str(self.outputName) + ".ply"
        self.f = open(filename, "w+")
        # ply header
        self.f.write('ply\n')
        self.f.write('format ascii 1.0\n')
        self.f.write('element vertex ' + str(numPoints) + '\n')
        self.f.write('property float x\n')
        self.f.write('property float y\n')
        self.f.write('property float z\n')
        self.f.write('property uchar red\n')
        self.f.write('property uchar green\n')
        self.f.write('property uchar blue\n')
        self.f.write('element face 0\n')
        self.f.write('property list uchar int vertex_index\n')
        self.f.write('end_header\n')

        # Find out the absolute of the amplitude difference
        minAmp = 65535
        maxAmp = 0

        for i in range(numPoints):
            if data.getDepthConfidence(i) > 0:
                if data.getGrayValue(i) < minAmp:
                    minAmp = data.getGrayValue(i)
                elif data.getGrayValue(i) > maxAmp:
                    maxAmp = data.getGrayValue(i)

        rangeDiff = maxAmp - minAmp

        # We don't want to divide by zero if we have no amplitude difference
        if rangeDiff == 0:
            rangeDiff = 1
        for i in range(numPoints):
            pixelColor = 0
            if data.getDepthConfidence(i) > 0:
                # Color the points in the point cloud according to the amplitude
                pixelColor = ((data.getGrayValue(i) - minAmp) / rangeDiff) * 255.0

            # round and remove trailing zeroes
            xString = str(round(data.getX(i), 6))
            xString = xString.rstrip('0').rstrip('.')

            yString = str(round(data.getY(i), 6))
            yString = yString.rstrip('0').rstrip('.')

            zString = str(round(data.getZ(i), 5))
            zString = zString.rstrip('0').rstrip('.')

            self.f.write(xString + " " + yString + " " + zString + " ")

            # Make sure the color is rgb (0-255)
            pixelColor = int(pixelColor)
            self.f.write(str(pixelColor) + " " + str(pixelColor) + " " + str(pixelColor) + "\n")

        self.f.close()


