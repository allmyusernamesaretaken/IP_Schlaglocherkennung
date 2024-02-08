import plyAnalyse as pa
import tof_pothole_analysis as tpa


def main():
    ply_path = r"C:\Users\Max\AppData\Local\4.24.0.1201\python\data\results\188\pothole.ply"
    pcd = pa.open_ply(ply_path)
    pa.visualize_point_cloud(pcd)
    pa.rotate_point_cloud_around_axis(pcd, (45,0,0))
    pa.visualize_point_cloud(pcd)
    tofAnalysis = tpa.TofPotholeAnalysis((918.1, 682.39), (996.25, 724.22),
                                         45, f"data/results",
                                         r"C:\Users\Max\AppData\Local\4.24.0.1201\python\data\results\92",
                                         plyFile=ply_path,
                                         rrfFile=r"C:\Users\Max\AppData\Local\4.24.0.1201\python\data\results\tof_recording.rrf")
    print(tofAnalysis.get_potholes().get_avg_pothole_depth())
    print(tofAnalysis.get_potholes().get_max_pothole_depth())
if __name__ == "__main__":
    main()

