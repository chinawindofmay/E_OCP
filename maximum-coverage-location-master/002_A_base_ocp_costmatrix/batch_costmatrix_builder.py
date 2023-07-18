# encoding:utf-8
import os

def code_test():
    """
    改进后的稀疏矩阵函数，及一个渔网点可被多个监控点可见
    :return:
    """
    python2_path = r"D:\Python27\ArcGIS10.6\python.exe"
    work_dir = os.path.dirname(__file__)
    sparse_visi = os.path.join(work_dir, "sparse_visibility_automated_procedure_new_mothed.py")

    tower_points_shp = "E:\\002code_running\\02GeoAI_Sub_Projects\\E_OCP\\maximum-coverage-location-master\\002_ocp_cost_matrix_generator\\open_data\\monitor_randpt.shp"
    GD_land_shp = "E:\\002code_running\\02GeoAI_Sub_Projects\\E_OCP\\maximum-coverage-location-master\\002_ocp_cost_matrix_generator\\open_data\\XZQ.shp"
    dem_raster = "E:\\002code_running\\02GeoAI_Sub_Projects\\E_OCP\\maximum-coverage-location-master\\002_ocp_cost_matrix_generator\\open_data\\elev_lid792_1m.tif"
    xzq = "E:\\002code_running\\02GeoAI_Sub_Projects\\E_OCP\\maximum-coverage-location-master\\002_ocp_cost_matrix_generator\\open_data\\XZQ.shp"
    TOWER_HEIGHT = 5
    RIDUS = 50
    FISHNET_CELL_SIZE = 5
    capacity = 100
    out_path = "E:\\002code_running\\02GeoAI_Sub_Projects\\E_OCP\\maximum-coverage-location-master\\002_ocp_cost_matrix_generator\\open_data\\result"

    print(python2_path + " " + sparse_visi + " " + tower_points_shp + " " + GD_land_shp + " " + dem_raster + " " + xzq + " " + str(TOWER_HEIGHT) + " " + str(RIDUS) + " " + str(FISHNET_CELL_SIZE) + " " +  str(capacity) + " " + out_path)
    os.system(
        python2_path + " " + sparse_visi + " " + tower_points_shp + " " + GD_land_shp + " " + dem_raster + " " + xzq + " " + str(TOWER_HEIGHT) + " " + str(RIDUS) + " " + str(FISHNET_CELL_SIZE) + " " +  str(capacity) + " " + out_path)


if __name__=="__main__":
    code_test()