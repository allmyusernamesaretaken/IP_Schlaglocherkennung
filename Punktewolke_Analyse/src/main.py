#!/usr/bin/python3
from src.utils.tof import tof_pothole_analysis as tpa
import argparse

def main():
    """"""
    """
    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument("--p1x", type=float, required=True, help="point1x")
    parser.add_argument("--p1y", type=float, required=True, help="point1y")
    parser.add_argument("--p2x", type=float, required=True, help="point2x")
    parser.add_argument("--p2y", type=float, required=True, help="point2y")
    parser.add_argument("--dir", default="", type=str, help="directory")
    parser.add_argument("--create_rrf", default="True", type=str, help="create rrf or use existing one")
    options = parser.parse_args()

    print(options.p1x)
    print(options.p1y)
    print(options.p2x)
    print(options.p2y)
    print(options.dir)
    print(options.create_rrf)
    """


    tofAnalysis = tpa.TofPotholeAnalysis([(-0.4, -3)], [(0.4, -0.5)], 45, "samples", rrfFile="samples/recording.rrf")
    tof_potholes = tofAnalysis.get_potholes()
    for pothole in tof_potholes:
        print("Maximale Tiefe: " + str(pothole.get_max_pothole_depth() * 10 ** 3) + "mm")
        print("durchschnittliche Tiefe: " + str(pothole.get_avg_pothole_depth() * 10 ** 3) + "mm")


if __name__ == "__main__":
    main()