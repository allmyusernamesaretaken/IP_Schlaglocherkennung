#!/usr/bin/python3
import tof_pothole_analysis as tpa
import argparse


def save_text(text, output_path):
    with open(output_path, "a") as file:
        file.write(text)


def main():
    """"""

    parser = argparse.ArgumentParser(usage=__doc__)
    parser.add_argument("--p1x", type=float, required=True, help="point1x")
    parser.add_argument("--p1y", type=float, required=True, help="point1y")
    parser.add_argument("--p2x", type=float, required=True, help="point2x")
    parser.add_argument("--p2y", type=float, required=True, help="point2y")
    parser.add_argument("--dir", default="", type=str, help="directory")
    parser.add_argument("--counter", type=int, required=True, help="counter")
    parser.add_argument("--index", type=int, default=0, help="image id")
    parser.add_argument("--create_rrf", action="store_true", default=False, help="create rrf or use existing one")
    parser.add_argument("--angle", default=90, type=float, help="angle of camera")
    options, _ = parser.parse_known_args()

    if options.create_rrf:
        tofAnalysis = tpa.TofPotholeAnalysis((options.p1x, options.p1y), (options.p2x, options.p2y),
                                             options.angle, f"data/results/{options.counter}", options.dir)
    else:
        tofAnalysis = tpa.TofPotholeAnalysis((options.p1x, options.p1y), (options.p2x, options.p2y),
                                             options.angle, options.dir, options.dir + str(options.counter),
                                             rrfFile="data/results/recording.rrf")
    pothole = tofAnalysis.get_potholes()
    save_text(f"Average Pothole Depth {options.index}: {pothole.get_avg_pothole_depth()}\n",
              f"data/results/{options.counter}/result.txt")
    save_text(f"Max Pothole Depth {options.index}: {pothole.get_max_pothole_depth()}\n",
              f"data/results/{options.counter}/result.txt")
    print("Maximale Tiefe: " + str(pothole.get_max_pothole_depth() * 10 ** 3) + "mm")
    print("durchschnittliche Tiefe: " + str(pothole.get_avg_pothole_depth() * 10 ** 3) + "mm")


if __name__ == "__main__":
    main()
