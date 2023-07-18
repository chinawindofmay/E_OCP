# -*- coding: utf-8 -*-
import numpy as np
import os
import arcpy
from arcpy import env
from arcpy.sa import *

def optimization_A(npz_path,tower_visiable_points_npz,capacity):
    print("开始选址")
    tower_visiable_points_npz_file_1000 = np.load(tower_visiable_points_npz)
    A_matrix = tower_visiable_points_npz_file_1000['list_array'].T  # 转置成列为供给点  (8810*488)
    choose_camera = np.zeros((A_matrix.shape[1],))  # 488列，全为0
    cur_visible_area = np.zeros((A_matrix.shape[0],))
    print(A_matrix.shape)
    for i in range(capacity):
        s = np.sum(A_matrix.T + cur_visible_area > 0, axis=1)
        choose_idx = np.argmax(s)
        cur_visible_area += A_matrix.T[choose_idx]
        choose_camera[choose_idx] = 1  # 选择该摄像头区域
        # 选过的点对应的可见区域赋值为0
        A_matrix[:, choose_idx] = 0
    np.savez(npz_path,
             price_matrix_no_distance_reduce_more=choose_camera,
             )
    print(np.count_nonzero(cur_visible_area))   #计算最后选址可见点数
    print("选点个数{}".format(np.sum(choose_camera)))
    print("选址结束")




if __name__ == '__main__':

    # part_roi
    tower_visiable_points_npz = r'D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_data_OSG_NC\result_part_roi\price_matrix_1000.npz'
    capacity_list = [30,40,50,60,70,80,90,100,110]
    capacity = 30
    npz_path = r"D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_data_OSG_NC\result_part_roi\part_roi_GA_{0}.npz".format(capacity)
    optimization_A(npz_path, tower_visiable_points_npz, capacity)

    # all_xzq
    tower_visiable_points_npz = r'D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_data_OSG_NC\result_all_xzq\price_matrix_1000.npz'
    capacity_list = [30,40,50,60,70,80,90,100,110]
    capacity = 30
    npz_path = r"D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_data_OSG_NC\result_all_xzq\all_xzq_GA_{0}.npz".format(capacity)
    optimization_A(npz_path, tower_visiable_points_npz, capacity)



