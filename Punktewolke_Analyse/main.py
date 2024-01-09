#!/usr/bin/python3

"""
record a rrf recording, export its first frame to a ply file and then analyse the ply file regarding the pothole depth
"""

import argparse
import sys
import time
import plyExportListener
import rrfRecordListener
import plyAnalyse as pa
from roypy_sample_utils import CameraOpener, add_camera_opener_options
from sample_camera_info import print_camera_info


def main():
    rrf_recording = "samples/recording.rrf"
    output = "samples/frame"
    #record_rrf(rrf_recording)
    export_ply_from_rrf(rrf_recording, output)
    process_ply(output)


def process_ply(plyFile):
    pcd = pa.open_ply(plyFile + ".ply")
    pa.visualize_point_cloud(pcd)
    pcd = pa.filter_pcd_by_null(pcd)
    pcd = pa.crop_point_cloud_outside_of_rotated_2d_points(pcd, (-0.2, 1), (0.4, 3), angle=45)
    pcd = pa.remove_outliers(pcd, 10, 0.1)  # filter evtl zu agressiv eingestellt
    pa.visualize_point_cloud(pcd)
    print("Maximale Tiefe: " + str(pa.calculate_max_pothole_depth(pcd) * 10 ** 3) + "mm")
    print("durchschnittliche Tiefe: " + str(pa.calculate_average_pothole_depth(pcd) * 10 ** 3) + "mm")


def export_ply_from_rrf(rrf, output="frame"):
    # ich hab das mit den arguments nicht so ganz gerafft funktioniert so aber
    parser = argparse.ArgumentParser()
    add_camera_opener_options(parser)
    parser.add_argument("--output", type=str, default=output, help="name of the output file")
    options = parser.parse_args()
    options.rrf = rrf
    opener = CameraOpener(options)

    try:
        cam = opener.open_camera()
    except:
        print("could not open Camera Interface")
        sys.exit(1)

    # retrieve the interface that is available for recordings
    replay = cam.asReplay()
    print("Framecount : ", replay.frameCount())

    # make sure the recording is sending the data oqn maximum speed and doesn't repeat
    replay.useTimestamps(False)
    replay.loop(False)

    l = plyExportListener.MyListener(1, options.output)

    cam.registerDataListener(l)
    cam.startCapture()

    # wait for onNewData to be called
    while not l.done:
        time.sleep(1)
    cam.stopCapture()
    print("Done")


def record_rrf(output, frames=1, skipFrames=0, skipMilliseconds=0):
    parser = argparse.ArgumentParser(usage=__doc__)
    add_camera_opener_options(parser)
    parser.add_argument("--frames", default=frames, type=int,
                        help="duration to capture data (number of frames)")
    parser.add_argument("--output", default=output, type=str, help="filename to record to")
    parser.add_argument("--skipFrames", type=int, default=0, help="frameSkip argument for the API method")
    parser.add_argument("--skipMilliseconds", type=int, default=0, help="msSkip argument for the API method")
    options = parser.parse_args()


    opener = CameraOpener(options)
    cam = opener.open_camera()
    cam.setUseCase("MODE_9_5FPS_1520")
    print_camera_info(cam)

    l = rrfRecordListener.MyListener()
    cam.registerRecordListener(l)
    cam.startCapture()

    try:
        cam.startRecording(options.output, options.frames, options.skipFrames, options.skipMilliseconds);
    except:
        print("There was an error creating the file.")
        sys.exit(1)

    seconds = options.frames * (options.skipFrames + 1) / cam.getFrameRate()
    if options.skipMilliseconds:
        timeForSkipping = options.frames * options.skipMilliseconds / 1000
        seconds = int(max(seconds, timeForSkipping))

    print("Capturing with the camera running at {rate} frames per second".format(rate=cam.getFrameRate()))
    print("This is expected to take around {seconds} seconds".format(seconds=seconds))

    l.waitForStop()  # warte bis aufnahme fertig ist

    cam.stopCapture()
    print("created rrf file")


if __name__ == "__main__":
    main()
