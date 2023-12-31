import copy

import open3d as o3d
import numpy as np
import math


def visualize_point_cloud(pcd):
    """
    visualisiert die Punktwolke mit eingezeichneten Koordinatenachsen
    :param pcd:
    """
    coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])  # r=x g=y b=z
    visualizer = o3d.visualization.Visualizer()
    visualizer.create_window()
    visualizer.add_geometry(pcd)
    visualizer.add_geometry(coord_frame)
    visualizer.run()
    visualizer.destroy_window()


def write_pcd_to_file(pcd, filename):
    o3d.io.write_point_cloud(filename, pcd)


def filter_pcd_by_null(pcd):
    """
    filtert alle Punkte mit den Koordinaten (0,0,0) aus der Punktwolke
    :param pcd:
    :return: gefilterte Punktwolke
    """
    points = np.asarray(pcd.points)
    indices_to_keep = np.all(points != (0, 0, 0), axis=1)
    return pcd.select_by_index(np.where(indices_to_keep)[0])


def open_ply(file_path):
    return o3d.io.read_point_cloud(file_path)


def scale_2d_pixels_to_3d_size():
    """
    skaliert einen in pixel angegebenen Punkt aus einem 2d Bild in den Maßstab der 3d Punktwolke
    :return: skalierten 2d Punkt
    """
    # TODO  implementieren
    pass


def crop_point_cloud_outside_of_rotated_2d_points(pcd, p1, p2, padding_x=0, padding_y=0, angle=0):
    """
    schneidet die Punktwolke auf die angegebenen Grenzen zu. Falls die Kamera nicht senkrecht nach unten ausgedrichtet
    ist, kann ein Winkel angegeben werden, welcher beim zuschneiden berücksichtigt wird.
    :param pcd: Punktewolke
    :param p1: 2D Punkt
    :param p2: 2D Punkt
    :param padding_x: padding um ungenauigkeiten bei der Übertragung von 2d auf 3d punkte auszugleichen
    :param padding_y: padding um ungenauigkeiten bei der Übertragung von 2d auf 3d punkte auszugleichen
    :param angle:
    :return: zugeschnittene und ausgerichtete Punktewolke
    """
    pcd_yolo = o3d.geometry.PointCloud()
    yolo_points = np.asarray(((p1[0], 0, p1[1]), (p2[0], 0, p2[1])))
    pcd_yolo.points = o3d.utility.Vector3dVector(yolo_points)

    # print(np.asarray(pcd_yolo.points))
    rotate_point_cloud_around_axis(pcd_yolo, (0, 0, angle))
    rotate_point_cloud_around_axis(pcd, (0, angle, 0))

    # print(np.asarray(pcd_yolo.points))
    p1 = np.asarray(pcd_yolo.points)[0]
    p2 = np.asarray(pcd_yolo.points)[1]
    p_min = (min(p1[0], p2[0]), min(p1[2], p2[2]), -100)
    p_max = (max(p1[0], p2[0]), max(p1[2], p2[2]), 100)

    # print(p_min, " ", p_max)
    # visualize_point_cloud(pcd)
    # visualize_point_cloud(pcd_yolo)
    return crop_point_cloud_outside_of_box(pcd, p_min, p_max)


def crop_point_cloud_outside_of_angled_box(pcd, p1, p2, padding_x=0, padding_y=0, angle=0):
    """
    unfertige funktion !!!nicht benutzen!!!
    :param pcd:
    :param p1:
    :param p2:
    :param padding_x:
    :param padding_y:
    :param angle:
    :return:
    """
    angle = math.radians(angle)
    v1 = (0, 1, 0)
    if math.cos(angle) != 0:
        v1_0 = -1
        v1_1 = math.sqrt((1 / (math.cos(angle) ** 2) - 1))
        v1_2 = 0
        v1 = (v1_0, v1_1, v1_2)

    points = np.asarray(pcd.points)
    min_x = points[:, 0] > p1[0]
    min_y = points[:, 1] > p1[1]
    min_z = points[:, 2] > p1[2]

    max_x = points[:, 0] < p2[0]
    max_y = points[:, 1] < p2[1]
    max_z = points[:, 2] < p2[2]

    comb_mask = min_x & min_y & min_z & max_x & max_y & max_z
    pcd.points = o3d.utility.Vector3dVector(points[comb_mask])  # normals and colors are unchanged
    return pcd


def crop_point_cloud_outside_of_box(pcd, min, max):
    """
    Schneidet die Punktwolke auf die angegebenen Grenzen zu
    :param pcd: Punktewolke
    :param min: punkt mit minimalen x,y,z wert
    :param max: punkt mit maximalen x,y,z wert
    :return: zugeschnittene Punktwolke
    """
    points = np.asarray(pcd.points)
    min_x = points[:, 0] > min[0]
    min_y = points[:, 1] > min[1]
    min_z = points[:, 2] > min[2]

    max_x = points[:, 0] < max[0]
    max_y = points[:, 1] < max[1]
    max_z = points[:, 2] < max[2]

    comb_mask = min_x & min_y & min_z & max_x & max_y & max_z
    pcd.points = o3d.utility.Vector3dVector(points[comb_mask])  # normals and colors are unchanged
    return pcd


def crop_point_cloud_outside_of_2d_points(pcd, p1, p2, padding_x=0, padding_y=0):
    """
    erstellt einen "Turm" mit x/y breite/teife vom Rechteck, welches p1 und p2 aufziehen und z = höhe = 0bis(-100)
    """
    p_min = (min(p1[0], p2[0]) - padding_x, min(p1[1], p2[1]) - padding_y, -100)
    p_max = (max(p1[0], p2[0]) + padding_x, max(p1[1], p2[1]) + padding_y, 1)
    return crop_point_cloud_outside_of_box(pcd, p_min, p_max)


def calc_maximum_distance(pcd, dim):
    """
    Berechnet die maximale Differenz zwischen den Werten der Dimension dim
    :param pcd:
    :param dim:
    :return: maximale Differenz
    """
    points = np.asarray(pcd.points)
    # Extrahiere die Werte
    values = points[:, dim]
    # Berechne die maximale Differenz zwischen den Y-Werten
    max_difference = np.max(values) - np.min(values)
    return max_difference


def visualize_plane_by_points(point_cloud, point1, point2, point3):
    """
    Erstelle eine TriangleMesh aus den drei Punkten und zeichne diese zusammen mit der Punktwolke
    """
    vertices = np.array([point1, point2, point3])
    triangles = np.array([[0, 1, 2]])
    plane_mesh = o3d.geometry.TriangleMesh()
    plane_mesh.vertices = o3d.utility.Vector3dVector(vertices)
    plane_mesh.triangles = o3d.utility.Vector3iVector(triangles)

    coord_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=0.1, origin=[0, 0, 0])  # r=x g=y b=z
    # Zeichne die Punktwolke und die Ebene
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    vis.add_geometry(point_cloud)
    vis.add_geometry(plane_mesh)
    vis.add_geometry(coord_frame)

    vis.run()
    vis.destroy_window()


def rotate_point_cloud_around_axis(point_cloud, rotation_degrees):
    """
    Rotiert die Punktwolke um alle Achsen um die in rotation_degrees angegebenen Grad
    rotiert zuerst um x, dann um y, dann um z
    :param point_cloud:
    :param rotation_degrees:
    :return: die rotierte Punktwolke
    """
    # grad zu radiant
    rotation_radians = np.radians(rotation_degrees)

    # rotationsmatrizen für die jeweiligen Achsen

    # x-Achse
    rotation_matrix0 = np.array([[1, 0, 0],
                                 [0, np.cos(rotation_radians[0]), -np.sin(rotation_radians[0])],
                                 [0, np.sin(rotation_radians[0]), np.cos(rotation_radians[0])]])

    # z-Achse
    rotation_matrix1 = np.array([[np.cos(rotation_radians[1]), 0, np.sin(rotation_radians[1])],
                                 [0, 1, 0],
                                 [-np.sin(rotation_radians[1]), 0, np.cos(rotation_radians[1])]])
    rotation_matrix2 = np.array([[np.cos(rotation_radians[2]), -np.sin(rotation_radians[2]), 0],
                                 [np.sin(rotation_radians[2]), np.cos(rotation_radians[2]), 0],
                                 [0, 0, 1]])
    # Punktewolke rotieren
    rotated_point_cloud = point_cloud.rotate(rotation_matrix0, center=(0, 0, 0))
    rotated_point_cloud = point_cloud.rotate(rotation_matrix1, center=(0, 0, 0))
    rotated_point_cloud = point_cloud.rotate(rotation_matrix2, center=(0, 0, 0))
    return rotated_point_cloud


def remove_outliers(pcd, neighbors=20, radius=2.0):
    """
    Anwenden des Statistical Outlier Removal Filters
    entfernt alle punkte, welche im radius nicht mind Anzahl radius hat
    """
    cl, ind = pcd.remove_statistical_outlier(nb_neighbors=neighbors, std_ratio=radius)
    return pcd.select_by_index(ind)


def downsample(pcd, voxel_size=0.01):
    """
    Anwenden des Voxel-Downsampling-Filters. Unterteilt in einzelne würfel und erstellt einen durchschnittlichen punkt
    """
    downsampled_point_cloud = pcd.voxel_down_sample(voxel_size=voxel_size)
    return downsampled_point_cloud


def create_normal_vector_with_points(point1, point2, point3):
    """
    Berechnet die Normale der Ebene anhand von drei Punkten
    :param point1:
    :param point2:
    :param point3:
    :return: normalenvektor, d
    """
    # berechne die normale der ebene
    normal = np.cross(point2 - point1, point3 - point1)
    # berechne die d-Komponente der Ebenengleichung
    d = normal[0] * point1[0] + normal[1] * point1[1] + normal[2] * point1[2]
    return normal, d


def calculate_distance_to_plane(normal, d, point):
    """
    Berechnet die Distanz des Punktes zur Ebene (Hessesche Normalform)
    :param normal:
    :param d:
    :param point:
    :return: distanz des Punktes zur Ebene
    """
    distance = (normal[0] * point[0] + normal[1] * point[1] + normal[2] * point[2] - d) / math.sqrt(
        normal[0] ** 2 + normal[1] ** 2 + normal[2] ** 2)
    return distance


def calculate_street_plane(pcd):
    """
    Berechnet die Ebene der Straße
    :param pcd: punktwolke
    :return: normale der ebene, d-komponente der ebene
    """
    # kopiere die punktwolke
    reduced_pcd = copy.deepcopy(pcd)
    # Reduziere die Punktwolke
    reduced_pcd = remove_outliers(reduced_pcd)
    reduced_pcd = downsample(reduced_pcd, 0.01)
    points_reduced_pcd = np.asarray(reduced_pcd.points)
    # Finde den Punkt mit dem kleinsten x-Wert
    p_min = points_reduced_pcd[np.argmin(points_reduced_pcd[:, 0] + points_reduced_pcd[:, 1])]
    # Finde den Punkt mit dem größten x-Wert
    p_max = points_reduced_pcd[np.argmax(points_reduced_pcd[:, 0] + points_reduced_pcd[:, 1])]
    # finde die x-max z-min ecke
    p_min_max = points_reduced_pcd[np.argmax(points_reduced_pcd[:, 0] - points_reduced_pcd[:, 1])]

    # Berechne die Normale der Ebene
    normal, d = create_normal_vector_with_points(p_min, p_max, p_min_max)
    visualize_plane_by_points(pcd, p_min, p_max, p_min_max)
    return normal, d


def calculate_max_pothole_depth(pcd):
    """
    Berechnet die maximale Tiefe eines Schlaglochs.
    Bei dieser Funktion ist eine gewisse ungenauigkeit der Koordinatenachsen akzeptabel.
    :param pcd: punktwolke
    :return: maximale tiefe des schlaglochs
    """
    # Berechne die Normale der Ebene
    normal, d = calculate_street_plane(pcd)
    # berechne die maximale Distanz aller Punkte zur Ebene
    points_pcd = np.asarray(pcd.points)
    max_distance = 0
    for point in points_pcd:
        distance = calculate_distance_to_plane(normal, d, point)
        if abs(distance) > max_distance:
            max_distance = abs(distance)
    return max_distance


def calculate_average_pothole_depth(pcd, threshold=5):
    """
    Berechnet die durchschnittliche Tiefe eines Schlaglochs herbei werden alle Punkte betrachtet, welche eine größere
    distanz haben als maximale distanz / threshold.
    Bei dieser Funktion ist eine gewisse ungenauigkeit der Koordinatenachsen akzeptabel.
    :param threshold:
    :param pcd: punktwolke
    :return: durchschnittliche Tiefe des schlaglochs
    """
    # Berechne die Normale der Ebene
    normal, d = calculate_street_plane(pcd)
    # berechne die maximale Distanz aller Punkte zur Ebene
    points = np.asarray(pcd.points)
    max_distance = 0
    for point in points:
        distance = calculate_distance_to_plane(normal, d, point)
        if abs(distance) > max_distance:
            max_distance = abs(distance)

    distance_threshold = max_distance - max_distance / threshold
    added_points = 0
    distance = 0
    for point in points:
        if abs(calculate_distance_to_plane(normal, d, point)) > distance_threshold:
            added_points += 1
            distance += abs(calculate_distance_to_plane(normal, d, point))
    return distance / added_points


def level_plane(point_cloud, iterate=5.0, plane=0):
    """
    Bringt die Punktwolke in eine Ebene. Es wird der Durchschnitt der y-koordinatenwerte genommen und die ebene
    in 2 ebene Ebenen aufgeteilt. Welche punkte in die obene/untere ebene gehören wird durch die parameter plane und
    iterate bestimmt. Die Funktion funktioniert nur, wenn die Punktwolke sehr genau zu der x/z Ebene ausgerichtet ist.
    :param point_cloud:
    :param iterate:
    :param plane:
    :return: die gelevelte Punktwolke
    """
    # Konvertiere die Punktwolke in ein NumPy-Array
    points = np.asarray(point_cloud.points)
    plane = 2 - plane
    # Berechne den maximalen und minimalen Z-Wert
    max_v = np.max(points[:, plane])
    min_v = np.min(points[:, plane])

    # Berechne Annäherung threshold min fäche
    mid_v = (max_v + min_v * iterate) / (1 + iterate)
    #################
    # Berechne den Durchschnitt der y-Koordinaten aller Punkte unterhalb der Mitte
    mask_lower = points[:, plane] < mid_v
    average_z = np.mean(points[mask_lower, plane])

    # Ändere die y-Koordinaten aller Punkte unterhalb der Mitte zum Durchschnittswert
    points[mask_lower, plane] = average_z

    #################
    # nBerechne Annäherung threshold max fäche
    nth_estimate = (max_v * iterate + min_v) / (iterate + 1)
    # Berechne den Durchschnitt der y-Koordinaten aller Punkte oberhalb der Mitte
    mask_upper = points[:, plane] >= nth_estimate
    average_z = np.mean(points[mask_upper, plane])

    # Ändere die y-Koordinaten aller Punkte oberhalb der Mitte zum Durchschnittswert
    points[mask_upper, plane] = average_z

    # Aktualisiere die Punktwolke
    modified_point_cloud = o3d.geometry.PointCloud()
    modified_point_cloud.points = o3d.utility.Vector3dVector(points)

    return modified_point_cloud


"""
testn sind Funktionen, welche veranschaulichen, wie die Funktionen verwendet werden können
"""


def test1():
    # print(math.sqrt((1 / (math.cos(math.pi/4)**2) - 1)))
    ply_file_path = "57.ply"
    pcd = open_ply(ply_file_path)
    pcd = filter_pcd_by_null(pcd)
    visualize_point_cloud(pcd)
    pcd_removed_outliers = remove_outliers(pcd)
    # visualize_point_cloud(pcd_removed_outliers)
    # pcd = downsample(pcd)
    visualize_point_cloud(pcd)
    crop_point_cloud_outside_of_2d_points(pcd, [-0.5, -0.25], [-0.1, 0.25], 0, 0)
    visualize_point_cloud(pcd)

    print(calc_maximum_distance(pcd, 2) * 10 ** 3, " mm")

    rotated_pcd = rotate_point_cloud_around_axis(pcd, (0, 0, 90))
    visualize_point_cloud(rotated_pcd)

    pcd = level_plane(pcd, 10, 0)
    visualize_point_cloud(pcd)

    print(calc_maximum_distance(pcd, 2) * 10 ** 3, " mm")


def test2():
    ply_file_path = "1-1.ply"
    pcd = open_ply(ply_file_path)
    pcd = filter_pcd_by_null(pcd)
    visualize_point_cloud(pcd)
    crop_point_cloud_outside_of_rotated_2d_points(pcd, (-3, -1), (-1, 1), 0.2, 0, -42)
    visualize_point_cloud(pcd)
    print(calc_maximum_distance(pcd, 2) * 10 ** 3, " mm")
    pcd = level_plane(pcd, 10, 0)
    visualize_point_cloud(pcd)
    level_plane(pcd)
    print(calc_maximum_distance(pcd, 2) * 10 ** 3, " mm")


def test3():
    ply_file_path = "57.ply"
    pcd = open_ply(ply_file_path)
    pcd = filter_pcd_by_null(pcd)
    crop_point_cloud_outside_of_2d_points(pcd, [-0.5, -0.25], [-0.1, 0.25], 0, 0)
    visualize_point_cloud(pcd)
    print(calculate_max_pothole_depth(pcd) * 10 ** 3, " mm")
    level_plane(pcd)
    print(calc_maximum_distance(pcd, 2) * 10 ** 3, " mm")


def test4():
    ply_file_path = "1-1.ply"
    pcd = open_ply(ply_file_path)
    pcd = filter_pcd_by_null(pcd)

    crop_point_cloud_outside_of_rotated_2d_points(pcd, (-3, -1), (-1, 1), 0.2, 0, -50)
    visualize_point_cloud(pcd)
    print(calculate_max_pothole_depth(pcd) * 10 ** 3, " mm")
    print(calculate_average_pothole_depth(pcd) * 10 ** 3, " mm")
    print(calc_maximum_distance(pcd, 2) * 10 ** 3, " mm")
    level_plane(pcd)
    visualize_point_cloud(pcd)
    print(calc_maximum_distance(pcd, 2) * 10 ** 3, " mm")


if __name__ == "__main__":
    test4()
