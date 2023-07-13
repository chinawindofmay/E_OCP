# -*- coding: UTF-8 -*-
import numpy as np
import arcpy
from arcpy import env
from arcpy.sa import *
import os

def main(selected_tower_binary_npz_file_path, intersect_every_points_folder, out_path, tower_with_height_points_shp_path, GD_shp, capacity):
    #获取点的KEY_ID;合并；融合；计算字段；面积占比
    arcpy.CheckOutExtension("Spatial")
    in_path1 = out_path
    gdb_path = os.path.join(in_path1,"{}temp.gdb".format(capacity))
    if not os.path.exists(gdb_path):
        arcpy.CreateFileGDB_management(in_path1, "{}temp".format(capacity))
    env.workspace = gdb_path
    env.overwriteOutput = True
    #选点
    A = np.load(selected_tower_binary_npz_file_path)
    field_name = 'se_point'
    arcpy.AddField_management(tower_with_height_points_shp_path, field_name, "Float", "", "", "", "", "NULLABLE",
                              "NON_REQUIRED", "")
    with arcpy.da.UpdateCursor(tower_with_height_points_shp_path, ["KEY_ID", field_name]) as cursor:
        for row in cursor:
            Key_ID = row[0]
            row[1] = A['best_elist_solution'][int(Key_ID)]
            cursor.updateRow(row)
    print("选择点图层")
    BUILD_POINT_shp = gdb_path + "/point"
    arcpy.Select_analysis(tower_with_height_points_shp_path, BUILD_POINT_shp, "\"{}\" = 1".format(field_name))
    #取Intersect文件
    savepath = os.path.join(gdb_path, 'result_intersect_polygon')  # 保存路径
    savepath_Dissolve = os.path.join(gdb_path, 'result_intersect_dis_polygon')  # 看这个面图层即可。
    input_files = []
    with arcpy.da.UpdateCursor(BUILD_POINT_shp, ["KEY_ID"]) as cursor:
        for key in cursor:
            Key_id = key[0]
            path = os.path.join(intersect_every_points_folder, (Key_id + "intersect.shp"))
            try:
                if os.path.exists(path):
                    input_files.append(os.path.join(intersect_every_points_folder, (Key_id + "intersect.shp")))  # 循环加入所有shape文件
            except Exception as e:
                print(path)
    arcpy.Merge_management(inputs=input_files, output=savepath)
    print("合并結束")
    #融合
    print("开始融合")
    arcpy.AddField_management(savepath, "GRIDCODE", "TEXT", "", "", "", "", "NULLABLE",
                              "NON_REQUIRED", "")
    arcpy.CalculateField_management(savepath, "GRIDCODE", "1", "VB", "")

    arcpy.Dissolve_management(savepath, savepath_Dissolve, "GRIDCODE", "", "MULTI_PART", "DISSOLVE_LINES")
    print("融合结束")
    # 计算几何
    print("开始计算面积")
    # arcpy.CalculateField_management(savepath_Dissolve, "Shape_Area", "!shape.area!", "PYTHON_9.3", "")
    # 计算可见面积
    monitor_all_area = 0
    rows = arcpy.da.SearchCursor(savepath_Dissolve, ["Shape_Area"])
    for row in rows:
        solo_area = row[0]
        monitor_all_area += solo_area
    print("可见面积{}平方米".format(monitor_all_area))
    GD_all_area = 0
    arcpy.CalculateField_management(GD_shp, "Shape_Area", "!shape.area!", "PYTHON_9.3", "")
    rows = arcpy.da.SearchCursor(GD_shp, ["Shape_Area"])
    for row in rows:
        solo_area = row[0]
        GD_all_area += solo_area
    print("耕地总面积{}平方米".format(GD_all_area))
    percentage = (monitor_all_area / GD_all_area) * 100
    print("耕地占比为{}%".format(percentage))
    # result_per_save.append(percentage)
    return gdb_path


if __name__ == '__main__':
    root_file_path = r'H:\taji_test\xinbei\out\Three_Layout_scheme\out'
    input_intersect_path = r'H:\taji_test\xinbei\out\intersect'
    point_shp_path = r'H:\taji_test\xinbei\out\Three_Layout_scheme\ori_data\merge_monitor_777.shp'
    GD_shp = r'H:\taji_test\xinbei\out\Three_Layout_scheme\ori_data\GD.shp'
    capacity = 125
    selelct_npz_path = r''
    gdb_path = main(selelct_npz_path, input_intersect_path, root_file_path, point_shp_path, GD_shp, capacity)
