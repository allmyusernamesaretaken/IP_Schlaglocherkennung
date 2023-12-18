#!/usr/bin/python3

"""
"""

import argparse
import sys
import time
import plyExportListener
import plyAnalyse as pa
from roypy_sample_utils import CameraOpener, add_camera_opener_options


def main():
    file_rrf = "samples/25fps_wagen_box.rrf"
    output = "samples/frame"
    process_pothole(file_rrf, output)


def process_pothole(file_rrf, output):
    export_ply_from_rrf(file_rrf, output)
    pcd = pa.open_ply(output + ".ply")
    pcd = pa.filter_pcd_by_null(pcd)
    pa.visualize_point_cloud(pcd)
    pcd = pa.crop_point_cloud_outside_of_rotated_2d_points(pcd, (-0.3, -0.2), (0, 0.2))
    pcd = pa.remove_outliers(pcd, 10, 0.1) #filter evtl zu agressiv eingestellt
    pcd = pa.rotate_point_cloud_around_axis(pcd, (180, 0, 0))
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


if __name__ == "__main__":
    main()
