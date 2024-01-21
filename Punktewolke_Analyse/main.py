#!/usr/bin/python3
import tof_pothole_analysis as tpa


def main():
    tofAnalysis = tpa.TofPotholeAnalysis([(-0.4, -3)], [(0.4, -0.5)], 45, "samples", rrfFile="samples/recording.rrf")
    tof_potholes = tofAnalysis.get_potholes()
    for pothole in tof_potholes:
        print("Maximale Tiefe: " + str(pothole.get_max_pothole_depth() * 10 ** 3) + "mm")
        print("durchschnittliche Tiefe: " + str(pothole.get_avg_pothole_depth() * 10 ** 3) + "mm")


if __name__ == "__main__":
    main()
