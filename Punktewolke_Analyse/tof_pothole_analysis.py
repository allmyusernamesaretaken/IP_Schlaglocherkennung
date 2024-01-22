import argparse
import sys
import time
import plyExportListener as plyExportListener
import rrfRecordListener as rrfRecordListener
import plyAnalyse as pa
from roypy_sample_utils import CameraOpener, add_camera_opener_options
from sample_camera_info import print_camera_info


class Pothole:
    def __init__(self, max_depth, average_depth):
        self.max_depth = max_depth
        self.average_depth = average_depth

    def get_max_pothole_depth(self):
        return self.max_depth

    def get_avg_pothole_depth(self):
        return self.average_depth


class TofPotholeAnalysis:
    """
    Class to analyze potholes by taking an image with a tof camera and calculating the depth of the pothole.
    """

    def __init__(self, p1_2d, p2_2d, angle, directory_rrf="", directory_ply="", threshold=0, plyFile=None, rrfFile=None):
        """
        :param p1_2d: first point of the rectangle in which the pothole is located
        :param p2_2d: second point of the rectangle in which the pothole is located
        :param angle: angle of the rectangle in which the pothole is located
        :param directory_rrf: directory_rrf where the files will be stored
        :param threshold: threshold for the depth of the pothole
        :param plyFile: path to the ply file. If given will not create a new one
        :param rrfFile: path to the rrf file. If given will not create a new one
        """
        self.angle = angle
        self.directory_rrf = directory_rrf
        self.directory_ply = directory_ply
        self.threshold = threshold
        self.plyFile = plyFile
        self.rrfFile = rrfFile

        if self.rrfFile is None:
            self.__record_rrf()
        if self.plyFile is None:
            self.__create_ply()

        max_depth, avg_depth = self.__process_ply(p1_2d, p2_2d, angle)
        self.pothole = Pothole(max_depth, avg_depth)

    def __record_rrf(self):
        """
        Record a rrf file with the tof camera.
        """
        frames = 1
        self.rrfFile = self.directory_rrf + "/tof_recording.rrf"
        parser = argparse.ArgumentParser(usage=__doc__)
        add_camera_opener_options(parser)
        parser.add_argument("--frames", default=frames, type=int,
                            help="duration to capture data (number of frames)")
        parser.add_argument("--output", default=self.rrfFile, type=str, help="filename to record to")
        parser.add_argument("--skipFrames", type=int, default=0, help="frameSkip argument for the API method")
        parser.add_argument("--skipMilliseconds", type=int, default=0, help="msSkip argument for the API method")
        options, _ = parser.parse_known_args()

        opener = CameraOpener(options)
        cam = opener.open_camera()
        cam.setUseCase("MODE_9_5FPS_1520")  # TODO ggf. anderen UseCase verwenden, sollte aber eigentlich passen
        print_camera_info(cam)

        listener = rrfRecordListener.MyListener()
        cam.registerRecordListener(listener)
        cam.startCapture()

        try:
            cam.startRecording(options.output, options.frames, options.skipFrames, options.skipMilliseconds)
        except:
            print("There was an error creating the file.")
            sys.exit(1)  # TODO ggf sinnvolle Fehlerbehandlung, wenn Kamera nicht geöffnet werden kann.
            # eine möglichkeit wäre, einen Fehler zurückzugeben, welcher sagt, dass das Schlagloch nicht analysiert
            # werden konnte

        seconds = options.frames * (options.skipFrames + 1) / cam.getFrameRate()
        if options.skipMilliseconds:
            timeForSkipping = options.frames * options.skipMilliseconds / 1000
            seconds = int(max(seconds, timeForSkipping))

        print("Capturing with the camera running at {rate} frames per second".format(rate=cam.getFrameRate()))
        print("This is expected to take around {seconds} seconds".format(seconds=seconds))

        listener.waitForStop()  # warte bis aufnahme fertig ist
        cam.stopCapture()
        print("created rrf file at: " + self.rrfFile)

    def __create_ply(self):
        """
        Create a ply file from a rrf file.
        """
        self.plyFile = self.directory_ply + "/pothole.ply"
        parser = argparse.ArgumentParser()
        add_camera_opener_options(parser)
        parser.add_argument("--output", type=str, default=self.directory_ply + "/pothole", help="name of the output file")
        options, _ = parser.parse_known_args()
        options.rrf = self.rrfFile
        opener = CameraOpener(options)

        try:
            cam = opener.open_camera()
        except:
            print("could not open Camera Interface")
            sys.exit(1)  # TODO ggf sinnvolle Fehlerbehandlung, wenn rrf File nicht geöffnet werden kann.

        replay = cam.asReplay()
        print("Framecount : ", replay.frameCount())  # should be 1 in our case

        # make sure the recording is sending the data on maximum speed and doesn't repeat
        replay.useTimestamps(False)
        replay.loop(False)

        listener = plyExportListener.MyListener(1, options.output)

        cam.registerDataListener(listener)
        cam.startCapture()

        # wait for onNewData to be called
        while not listener.done:
            time.sleep(1)
        cam.stopCapture()
        print("created ply file at: " + self.plyFile)

    def __process_ply(self, p1, p2, angle):
        """
        Process a ply file.
        """
        pcd = pa.open_ply(self.plyFile)
        pcd = pa.filter_pcd_by_null(pcd)

        p1_scaled = pa.convert_2d_points_to_3d_scale(p1)
        p2_scaled = pa.convert_2d_points_to_3d_scale(p2)
        pcd = pa.crop_point_cloud_outside_of_rotated_2d_points(pcd, p1, p2, angle=angle)
        pcd = pa.remove_outliers(pcd, 10, 0.1)  # TODO filter evtl zu aggressiv eingestellt (livetest)
        # pa.visualize_point_cloud(pcd)
        pcd_floor = pa.calculate_street_plane_least_square_distance(pcd)
        max_depth = pa.calculate_max_pothole_depth(pcd, pcd_floor, 1)
        average_depth = pa.calculate_average_pothole_depth(pcd, pcd_floor, 1)
        return max_depth, average_depth

    def get_potholes(self):
        return self.pothole
