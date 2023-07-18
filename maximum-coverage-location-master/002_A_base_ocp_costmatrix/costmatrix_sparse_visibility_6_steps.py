# -*- coding: utf-8 -*-
import arcpy
from arcpy import env
from arcpy.sa import *
import pandas as pd
import numpy as np
import time
import math
import os, sys

arcpy.env.overwriteOutput = True
work_dir = os.path.split(os.path.realpath(__file__))[0]
end = ""
out_path = ""

def step1_dem_height_extra_for_monitor(tower_points_shp, dem_raster, monitor_with_extra_height_shp):
    print ("提取高程值至点开始！！！！！！！！！！！！！！！！！！！！！！！！！！！1")
    tower_points_shp = tower_points_shp  # 基站原始shp
    dem_raster = dem_raster  # DEM
    # Check out the ArcGIS Spatial Analyst extension license
    print("正在执行 “提取高程值” 操作")
    arcpy.CheckOutExtension("Spatial")  # 设置许可
    # Execute ExtractValuesToPoints 提取高程信息
    ExtractValuesToPoints(tower_points_shp, dem_raster, monitor_with_extra_height_shp, "INTERPOLATE", "VALUE_ONLY")
    print("提取高程值完毕！！！！！")
    arcpy.AddField_management(monitor_with_extra_height_shp, "KEY_ID", "TEXT", "", "", "", "", "NULLABLE",
                              "NON_REQUIRED", "")
    arcpy.CalculateField_management(monitor_with_extra_height_shp, "KEY_ID", "!FID!", "PYTHON", "")


def step2_generate_every_point_visibility_shp(root_file_path, save_out_point_shp, farm_land_shp, dem_raster,
                                              tower_height_fieldname, ridus):
    print ("每一个点的可见性分析开始！！！！！！！！！！！！！！！！")
    env.workspace = root_file_path
    farm_land_shp = farm_land_shp
    dem_raster = dem_raster
    save_out_point_shp = save_out_point_shp
    # out_path_1 = os.path.join(root_file_path, 'out')
    # if not os.path.exists(out_path_1):
    #     os.mkdir(out_path_1)
    temp_test = os.path.join(root_file_path, "temp")
    if os.path.exists(temp_test):
        pass
    else:
        os.mkdir(temp_test)
    # 游标
    rows = arcpy.da.SearchCursor(save_out_point_shp, ["KEY_ID"])
    all_count = arcpy.GetCount_management(save_out_point_shp)
    update_status_num = 50.0 / float(int(all_count.getOutput(0)))
    i = 0
    for row in rows:
        try:
            strTDYT = row[0]
            print("{0}####".format(str(i)))
            # Process: 筛选
            solopoint_shp = os.path.join(temp_test, "{}.shp".format(strTDYT))
            # print(solopoint_shp)
            arcpy.Select_analysis(save_out_point_shp, solopoint_shp, "\"KEY_ID\" ='{}'".format(strTDYT))
            # 可见性分析  耗时
            print("开始执行可见性分析")
            save_outvisibility_raster = os.path.join(temp_test, "{}".format(strTDYT))
            # algOutput = os.path.join(temp_test,"aglout{}".format(strTDYT))
            algOutput = ""
            tower_height_fieldname = tower_height_fieldname
            ridus = ridus
            arcpy.CheckOutExtension("3D")
            arcpy.Visibility_3d(dem_raster, solopoint_shp, save_outvisibility_raster, algOutput, "FREQUENCY", "ZERO",
                                "1", "FLAT_EARTH", "0.13", "", "RASTERVALU", tower_height_fieldname, "", ridus, "", "",
                                "", "")
            print("可见性分析结束")
            MakeRas_visibil1 = "MakeRas_visibil1"  #新栅格图层的名称
            # arcpy.Int_3d(save_outvisibility_raster)   这里始终无效
            arcpy.MakeRasterLayer_management(in_raster=save_outvisibility_raster, out_rasterlayer=MakeRas_visibil1,
                                             where_clause="\"VALUE\" > 0", envelope=save_outvisibility_raster, band_index=1)

            # 栅格转面  耗时
            print("开始进行栅格转面")
            save_visi_shape = os.path.join(temp_test, "{}visi_shape.shp".format(strTDYT))
            arcpy.RasterToPolygon_conversion(MakeRas_visibil1, save_visi_shape, "SIMPLIFY", "")

            # ---------------------BEGIN增加一段判断逻辑，如果gridcode=0的也被转出来了，需要筛选掉---------------------
            # Execute MakeFeatureLayer
            temp_polygon_Layer='temp_polygon_Layer'
            arcpy.MakeFeatureLayer_management(save_visi_shape, temp_polygon_Layer)
            # Execute SelectLayerByAttribute to determine which features to delete
            arcpy.SelectLayerByAttribute_management(temp_polygon_Layer, "NEW_SELECTION",
                                                    "\"GRIDCODE\" = 0")
            # Execute GetCount and if some features have been selected, then
            #  execute DeleteFeatures to remove the selected features.
            if int(arcpy.GetCount_management(temp_polygon_Layer).getOutput(0)) > 0:
                arcpy.DeleteFeatures_management(temp_polygon_Layer)
            # ---------------------END结束筛选掉------周鑫鑫增加 2023年7月13日20:19:10------------------------------

            intersect_test = os.path.join(env.workspace,"intersect")
            if os.path.exists(intersect_test):
                pass
            else:
                os.mkdir(intersect_test)
            # 相交，这部分耗时
            print("开始相交分析")
            save_intersect_shp = os.path.join(intersect_test, "{}intersect.shp".format(strTDYT))

            # Process: 相交
            arcpy.Intersect_analysis([farm_land_shp, save_visi_shape], save_intersect_shp, "ALL", 1.5, "INPUT")
            # 添加字段，使ID对应
            arcpy.AddField_management(save_intersect_shp, "KEY_ID", "TEXT", "", "", "1000", "", "NULLABLE",
                                      "NON_REQUIRED", "")
            # 计算字段
            arcpy.CalculateField_management(save_intersect_shp, "KEY_ID", "{}".format(strTDYT), "PYTHON", "")
            i += 1
        except Exception as e:
            print('Error:', e)


def step3_apppend_visi_shp_into_one_file_old(appeend_stand_shp):
    """
    原有增加到01intersect.shp中的代码
    后来韩佩佩重新写了，放到一个新的图层中，这样便于后期的可视化
    """
    print("追加开始！！！！！！！！！！！！！！！！")
    appeend_stand_shp = appeend_stand_shp
    intersect_test = os.path.join(os.path.dirname(appeend_stand_shp))
    arcpy.DeleteField_management(appeend_stand_shp, "FID_1visi_")
    file_list = os.listdir(intersect_test)
    for file in file_list:
        if file.endswith(".shp"):
            f = file.split('.')[0].index('i')
            strTDYT = file.split('.')[0][:f]
            path = os.path.join(intersect_test, file)
            path = path.replace('/', '\\')
            # print path
            if appeend_stand_shp in path:
                pass
            else:
                if path == appeend_stand_shp:
                    pass
                else:
                    arcpy.DeleteField_management(path, "FID_{}visi_".format(strTDYT))
                    arcpy.DeleteField_management(path, "FID_{}visi".format(strTDYT))
                    arcpy.DeleteField_management(path, "FID_{}vis".format(strTDYT))
                    arcpy.Append_management("{}".format(path), appeend_stand_shp, "TEST", "", "")  # test是映射方案


def step3_apppend_visi_shp_into_one_file(intersect_dir_path):
    print("合并开始！！！！！！！！！！！！！！！！")
    merge_shp_path = os.path.join(intersect_dir_path,'merge_all.shp')
    input_files = []
    file_list = os.listdir(intersect_dir_path)
    for i_file in file_list:
        if i_file.endswith('.shp'):
            solo_shp_path = os.path.join(intersect_dir_path,i_file)
            f = i_file.split('.')[0].index('i')
            strTDYT = i_file.split('.')[0][:f]
            arcpy.DeleteField_management(solo_shp_path, "FID_{}visi_".format(strTDYT))
            arcpy.DeleteField_management(solo_shp_path, "FID_{}visi".format(strTDYT))
            arcpy.DeleteField_management(solo_shp_path, "FID_{}vis".format(strTDYT))
            input_files.append(solo_shp_path)
    arcpy.Merge_management(inputs=input_files, output=merge_shp_path)
    return merge_shp_path

def step4_bulid_fishnet_centre_points(inRaster, XZQ, fishnet_cell_size):
    # out_des = arcpy.Describe(inRaster)
    out_des = arcpy.Describe(XZQ)
    print ("开始建立渔网！！！！！！！！！！！！！！")
    fisnnet_dir = os.path.join(env.workspace,"fishnet")
    if os.path.exists(fisnnet_dir):
        pass
    else:
        os.mkdir(fisnnet_dir)
    fishnet_shp = os.path.join(fisnnet_dir, "fishnet.shp")
    fishnet_label_shp = os.path.join(fisnnet_dir, "fishnet_label.shp")
    # #创建渔网
    arcpy.CreateFishnet_management(fishnet_shp, str(out_des.extent.XMin) + " " + str(out_des.extent.YMin),
                                   str(out_des.extent.XMin) + " " + str(out_des.extent.YMin + 10),
                                   fishnet_cell_size, fishnet_cell_size, "", "",
                                   str(out_des.extent.XMax) + " " + str(out_des.extent.YMax),
                                   "LABELS",
                                   XZQ, "POLYGON")
    print("开始剪裁")
    # #裁剪
    fishnet_cut_shp = fisnnet_dir + "/zhixin.shp"
    arcpy.Clip_analysis(fishnet_label_shp, XZQ, fishnet_cut_shp, "")


def step5_create_price_matrix_from_visi_shp_file_and_centre_points(zhixin_shp, appeend_stand_shp,
                                                                   price_matrix_save_file,
                                                                   monitor_with_extra_height_shp):
    print("开始建立矩阵")
    # 相交
    print ("开始相交分析")
    intersect_shp = os.path.join(os.path.dirname(zhixin_shp), "intersect.shp")
    # # Process: 相交
    arcpy.Intersect_analysis([zhixin_shp, appeend_stand_shp], intersect_shp, "ALL", "", "INPUT")
    # print ("相交结束")
    # 对zhixin_shp图层，寻找FID_zhixin的最大编号值
    # 逐条遍历feature，找到FID_zhixin的最大编号值
    FID_zhixin_xls = os.path.join(os.path.dirname(zhixin_shp), "cacu_zhixin.xls")
    arcpy.TableToExcel_conversion(intersect_shp, FID_zhixin_xls, "NAME", "CODE")
    s = pd.read_excel(FID_zhixin_xls, index_col=None)
    data = s['FID_zhixin']
    FID_max = data.max()   #  FID_zhixin的最大编号值，而非现有含重复的质心点总数量
    TOWER_COUNT = 0
    all_tower_rows = arcpy.da.SearchCursor(monitor_with_extra_height_shp, ["KEY_ID"])   # 从塔的点层数据中查找到KEY_ID   可以增加的逻辑，查询到xy

    # 获取候选点总数量
    TOWER_COUNT=len(all_tower_rows)
    for row in all_tower_rows:
        TOWER_COUNT += 1
    print("候选点总数{}".format(TOWER_COUNT))
    #初始化矩阵
    price_matrix = np.zeros([TOWER_COUNT, FID_max + 1], dtype=int)
    # intersect_shp的生成的步骤
    # 首先对候选点赋值塔高度，得到monitor_with_extra_height_shp点图层，会用到DEM，得到的是每个塔点位基座的海拔高度，增加KEY_ID字段；
    # 开始遍历monitor_with_extra_height_shp中的每一个点，
    #   进行可视域分析，输入数据包括：monitor_with_extra_height_shp中的每一个点、DEM、布设高度参数，输出数据是：栅格
    #   选取不为0的栅格，生成矢量面
    #   矢量面与耕地相交分析，得到可见耕地；
    #   对可见耕地增加KEY_ID字段，赋值塔ID字段；
    #   输出可见耕地shp数据
    # 可见耕地shp合并，变成一个SHP图层，此时会存在多个重叠在一起的面
    # 基于ZXQ生成fishnet及质心点图层；
    # 质心图层与可见耕地合并图层做相交，得到了intersect_shp，会自动生成FID_zhixin字段（前提这个zhixin.shp名字保持不变），一个面与一个点相交一次会得到一个相交点，因此会存在同一位置多个相交点，其中记录了FID_zhixin，可覆盖塔的KEY_ID；
    # 求取FID_zhixin最大编号、塔数量，用于初始化代价矩阵
    # 查询，给代价矩阵赋值；

    # 此处增加一个说明：intersect_shp中存的是所有的可见的质心点（重复存）。
    # 同一个位置的质心点如果被多个塔看到的话，会重复存储为多个点对象，这样的话，可以实现多个KEY_ID的记录。
    zhixin_rows = arcpy.da.SearchCursor(intersect_shp, ["FID_zhixin", "KEY_ID"])  # 查找出可见点的ID号及对应的TowerID号 可以增加的逻辑，查询到xy
    for row in zhixin_rows:
        FID_zhixin = row[0]
        TOWER_KEY_ID = row[1]
        # 可以增加的逻辑，增加两个XY之间的欧式求距离，以此作为反距离权重。
        price_matrix[int(TOWER_KEY_ID)][FID_zhixin] = 1
    # 去除全零行操作，及去除冗余列
    idx = np.argwhere(np.all(price_matrix[..., :] == 0, axis=0))
    price_matrix1 = np.delete(price_matrix, idx, axis=1)
    np.savez(price_matrix_save_file, list_array=price_matrix1)

def step5_create_price_matrix_with_distance_decay_from_visi_shp_file_and_centre_points(zhixin_shp, appeend_stand_shp,
                                                                   price_matrix_save_file,
                                                                    RIDUS,
                                                                   monitor_with_extra_height_shp):
    print("开始建立矩阵")
    # 相交
    print("开始相交分析")
    intersect_shp = os.path.join(os.path.dirname(zhixin_shp), "intersect.shp")
    # # Process: 相交
    arcpy.Intersect_analysis([zhixin_shp, appeend_stand_shp], intersect_shp, "ALL", "", "INPUT")
    # print ("相交结束")
    # 对zhixin_shp图层，寻找FID_zhixin的最大编号值
    # 逐条遍历feature，找到FID_zhixin的最大编号值
    zhixin_rows = arcpy.da.SearchCursor(intersect_shp,
                                        ["Shape", "FID_zhixin", "KEY_ID"])
    FID_max=0
    for row in zhixin_rows:
        FID_zhixin = int(row[1])
        if FID_zhixin>FID_max:
            FID_max=FID_zhixin

    # FID_zhixin_xls = os.path.join(os.path.dirname(zhixin_shp), "cacu_zhixin.xls")
    # arcpy.TableToExcel_conversion(intersect_shp, FID_zhixin_xls, "NAME", "CODE")
    # s = pd.read_excel(FID_zhixin_xls, index_col=None)
    # data = s['FID_zhixin']
    # FID_max = data.max()  # FID_zhixin的最大编号值，而非现有含重复的质心点总数量

    TOWER_COUNT = 0
    all_tower_rows = arcpy.da.SearchCursor(monitor_with_extra_height_shp,
                                           ["Shape","KEY_ID"])  # 从塔的点层数据中查找到KEY_ID   可以增加的逻辑，查询到xy
    # 获取候选点总数量、tower的坐标和ID，存在到dictionary中。
    # TOWER_COUNT = len(all_tower_rows)
    towers_dic={}
    for row in all_tower_rows:
        TOWER_COUNT += 1
        shape_tower = row[0]
        KEY_ID_tower = row[1]
        towers_dic[KEY_ID_tower]=shape_tower  # 先存起来，便于后面求距离使用。

    print("候选点总数{}".format(TOWER_COUNT))
    print("质心点最大编号{}".format(FID_max))
    # 初始化矩阵
    price_matrix_with_distance = np.zeros([TOWER_COUNT, FID_max + 1], dtype=float)
    price_matrix_no_distance = np.zeros([TOWER_COUNT, FID_max + 1], dtype=int)


    # 此处增加一个说明：intersect_shp中存的是所有的可见的质心点（重复存）。
    # 同一个位置的质心点如果被多个塔看到的话，会重复存储为多个点对象，这样的话，可以实现多个KEY_ID的记录。
    zhixin_rows = arcpy.da.SearchCursor(intersect_shp,
                                        ["Shape", "FID_zhixin", "KEY_ID"])  # 查找出可见点的ID号及对应的TowerID号 可以增加的逻辑，查询到xy
    for row in zhixin_rows:
        shape_zhixin = row[0]
        FID_zhixin = row[1]
        TOWER_KEY_ID = row[2]
        # 可以增加的逻辑，增加两个XY之间的欧式求距离，以此作为反距离权重。
        # 查询到对应KEY_ID的x和y
        shape_tower=towers_dic[TOWER_KEY_ID]
        distance=math.sqrt((shape_tower[0]-shape_zhixin[0])**2+(shape_tower[1]-shape_zhixin[1])**2)
        price_matrix_with_distance[int(TOWER_KEY_ID)][FID_zhixin] = distance    #直接将距离存入
        price_matrix_no_distance[int(TOWER_KEY_ID)][FID_zhixin]=1   #没有距离的类型
    # 去除全零行操作，  即没有任何联系的点  ？？？？   这样做的话，后期如何从npz文件复原回去
    # 没有问题,因为存在zhixin点不是从0开始的情况；
    idx = np.argwhere(np.all(price_matrix_with_distance[..., :] == 0, axis=0))
    price_matrix_with_distance_reduce_more = np.delete(price_matrix_with_distance, idx, axis=1)
    price_matrix_no_distance_reduce_more = np.delete(price_matrix_no_distance, idx, axis=1)

    # soft_price_matrix= np.zeros(shape=price_matrix1.shape, dtype=float)
    # ## 考虑到增加反距离权重后，整体的数值会变得很小。需要再做归一化处理，还不能这样操作，这样会有问题,会导致没有0的情况。
    # for j in range(price_matrix1.shape[1]):
    #     row_max = np.max(price_matrix1[:,j])
    #     x_exp = np.exp(price_matrix1[:,j])
    #     x_sum = np.sum(x_exp)
    #     s = x_exp / x_sum
    #     soft_price_matrix[:,j]=s

    np.savez(price_matrix_save_file,
             price_matrix_with_distance_reduce_more=price_matrix_with_distance_reduce_more,
             price_matrix_no_distance_reduce_more=price_matrix_no_distance_reduce_more)
    # np.savez(soft_price_matrix_save_file, list_array=soft_price_matrix)




def create_spatial_price_matrix(
        root_file_path,
        tower_points_shp,
        dem_raster,
        farm_land_shp,
        monitor_with_extra_height_shp,
        TOWER_HEIGHT,
        RIDUS,
        appeend_stand_shp,
        intersect_dir_path,
        xzq,
        FISHNET_CELL_SIZE,
        zhixin_shp,
        price_matrix_save_file,
        soft_price_matrix_save_file):
    start = time.time()
    # 提取高程值到基站点上
    step1_dem_height_extra_for_monitor(tower_points_shp, dem_raster, monitor_with_extra_height_shp)
    # 生成每个点的可见区域，并与目标图层相交，这一个步骤的计算量最大，主要逐个点操作
    step2_generate_every_point_visibility_shp(root_file_path, monitor_with_extra_height_shp, farm_land_shp, dem_raster,
                                              TOWER_HEIGHT, RIDUS)
    # 将所有可见区域追加到一个文件中，作废。
    # step3_apppend_visi_shp_into_one_file_old(appeend_stand_shp)
    # 将所有可见区域追加到一个文件中，merge_all.shp中
    out_merge_shp_path = step3_apppend_visi_shp_into_one_file(intersect_dir_path)
    # #生成fishnet和中心点
    step4_bulid_fishnet_centre_points(dem_raster, xzq, FISHNET_CELL_SIZE)

    # 将fishnet中心点与可见性所有图斑做叠加分析，然后构建代价矩阵
    # step5_create_price_matrix_from_visi_shp_file_and_centre_points(zhixin_shp, appeend_stand_shp,
    #                                                                price_matrix_save_file,
    #                                                                monitor_with_extra_height_shp)

    # 增加了distance decay的方式
    step5_create_price_matrix_with_distance_decay_from_visi_shp_file_and_centre_points(zhixin_shp, out_merge_shp_path,
                                                                   price_matrix_save_file,
                                                                   RIDUS,
                                                                   monitor_with_extra_height_shp)

    end = time.time()
    print("生成可视性分析的代价矩阵的运行耗时{}秒".format(end - start))
"""
主函数入口
"""
def entance(tower_points_shp, dem_raster, intersect_dir_path, xzq, GD_land_shp, out_path, TOWER_HEIGHT, RIDUS, FISHNET_CELL_SIZE,
            appeend_stand_shp, zhixin_shp, price_matrix_save_file, soft_price_matrix_save_file):
    root_file_path = out_path
    monitor_with_extra_height_shp = "{}\\monitor_with_extra_height_shp.shp".format(root_file_path)
    create_spatial_price_matrix(root_file_path,
                                tower_points_shp,
                                dem_raster,
                                GD_land_shp,
                                monitor_with_extra_height_shp,
                                TOWER_HEIGHT,
                                RIDUS,
                                appeend_stand_shp,
                                intersect_dir_path,
                                xzq,
                                FISHNET_CELL_SIZE,
                                zhixin_shp,
                                price_matrix_save_file,
                                soft_price_matrix_save_file)

# def debugger_test_small():
#     """
#     候选点数量3个，塔高5米，半径50米，网格尺寸5米；
#     Returns:
#
#     """
#     tower_points_shp = r"D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_ocp_cost_matrix_generator\open_data\monitor_randpt_small.shp"
#     GD_land_shp = r"D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_ocp_cost_matrix_generator\open_data\XZQ.shp"
#     dem_raster = r"D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_ocp_cost_matrix_generator\open_data\elev_lid792_1m.tif"
#     xzq = r"D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_ocp_cost_matrix_generator\open_data\XZQ.shp"
#     TOWER_HEIGHT = 5
#     RIDUS = 50
#     FISHNET_CELL_SIZE = 5
#     capacity = 100
#     out_path = r"D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_ocp_cost_matrix_generator\open_data\result_small"
#
#     if os.path.exists(out_path):
#         pass
#     else:
#         os.mkdir(out_path)
#     env.workspace = out_path
#
#     intersect_dir_path = "{}\\intersect".format(out_path)
#     appeend_stand_shp = "{}\\intersect\\1intersect.shp".format(out_path)
#     zhixin_shp = "{}\\fishnet\\zhixin.shp".format(out_path)
#     price_matrix_save_file = "{}\\price_matrix_{}.npz".format(out_path, RIDUS)
#     soft_price_matrix_save_file = "{}\\soft_price_matrix_{}.npz".format(out_path, RIDUS)
#
#     entance(tower_points_shp, dem_raster, intersect_dir_path, xzq, GD_land_shp, out_path, TOWER_HEIGHT, RIDUS, FISHNET_CELL_SIZE,
#             int(capacity), appeend_stand_shp, zhixin_shp, price_matrix_save_file,
#             soft_price_matrix_save_file)
#     print("success")

def debugger_all_xzq(BASE_ROOT):
    """
    全域，候选点数量258个，塔高5米，半径50米，网格尺寸5米；
    Returns:
    """
    tower_points_shp = r"{0}\monitor_randpt.shp".format(BASE_ROOT)
    roi_land_shp = r"{0}\XZQ.shp".format(BASE_ROOT)
    dem_raster = r"{0}\elev_lid792_1m.tif".format(BASE_ROOT)
    xzq = r"{0}\XZQ.shp".format(BASE_ROOT)
    TOWER_HEIGHT = 5
    RIDUS = 50
    FISHNET_CELL_SIZE = 5
    out_path = r"{0}\result_all_xzq".format(BASE_ROOT)

    if os.path.exists(out_path):
        pass
    else:
        os.mkdir(out_path)
    env.workspace = out_path

    intersect_dir_path = "{}\\intersect".format(out_path)
    appeend_stand_shp = "{}\\intersect\\1intersect.shp".format(out_path)
    zhixin_shp = "{}\\fishnet\\zhixin.shp".format(out_path)
    price_matrix_save_file = "{}\\price_matrix_{}.npz".format(out_path, RIDUS)
    soft_price_matrix_save_file = "{}\\soft_price_matrix_{}.npz".format(out_path, RIDUS)

    entance(tower_points_shp, dem_raster, intersect_dir_path, xzq, roi_land_shp, out_path, TOWER_HEIGHT, RIDUS, FISHNET_CELL_SIZE
            , appeend_stand_shp, zhixin_shp, price_matrix_save_file,
            soft_price_matrix_save_file)
    print("success")




def debugger_part_roi(BASE_ROOT):
    """
    ROI区域，候选点数量258个，塔高5米，半径50米，网格尺寸5米；
    Returns:
    """
    tower_points_shp = r"{0}\monitor_randpt.shp".format(BASE_ROOT)
    GD_land_shp = r"{0}\land.shp".format(BASE_ROOT)
    dem_raster = r"{0}\elev_lid792_1m.tif".format(BASE_ROOT)
    xzq = r"{0}\XZQ.shp".format(BASE_ROOT)
    TOWER_HEIGHT = 5
    RIDUS = 50
    FISHNET_CELL_SIZE = 5
    out_path = r"{0}\result_part_roi".format(BASE_ROOT)

    if os.path.exists(out_path):
        pass
    else:
        os.mkdir(out_path)
    env.workspace = out_path

    intersect_dir_path = "{}\\intersect".format(out_path)
    appeend_stand_shp = "{}\\intersect\\1intersect.shp".format(out_path)
    zhixin_shp = "{}\\fishnet\\zhixin.shp".format(out_path)
    price_matrix_save_file = "{}\\price_matrix_{}.npz".format(out_path, RIDUS)
    soft_price_matrix_save_file = "{}\\soft_price_matrix_{}.npz".format(out_path, RIDUS)

    entance(tower_points_shp, dem_raster, intersect_dir_path, xzq, GD_land_shp, out_path, TOWER_HEIGHT, RIDUS, FISHNET_CELL_SIZE,
             appeend_stand_shp, zhixin_shp, price_matrix_save_file,
            soft_price_matrix_save_file)
    print("success")


def batch_enter():
    global out_path, env
    tower_points_shp = sys.argv[1]
    GD_land_shp = sys.argv[2]
    dem_raster = sys.argv[3]
    xzq = sys.argv[4]
    TOWER_HEIGHT = sys.argv[5]
    RIDUS = sys.argv[6]
    FISHNET_CELL_SIZE = sys.argv[7]
    capacity = sys.argv[8]
    out_path = sys.argv[9]
    if os.path.exists(out_path):
        pass
    else:
        os.mkdir(out_path)
    env.workspace = out_path
    appeend_stand_shp = "{}\\intersect\\1intersect.shp".format(out_path)
    zhixin_shp = "{}\\fishnet\\zhixin.shp".format(out_path)
    price_matrix_save_file = "{}\\price_matrix_{}.npz".format(out_path, RIDUS)
    soft_price_matrix_save_file = "{}\\soft_price_matrix_{}.npz".format(out_path, RIDUS)
    create_spatial_price_matrix(tower_points_shp, dem_raster, xzq, GD_land_shp, out_path, TOWER_HEIGHT, RIDUS, FISHNET_CELL_SIZE,
                       int(capacity), appeend_stand_shp, zhixin_shp, price_matrix_save_file,
                       soft_price_matrix_save_file)
    print("success")
    # create()


if __name__ == "__main__":
    BASE_ROOT=r'D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_data_OSG_NC'
    BASE_ROOT=r'E:\002code_running\02GeoAI_Sub_Projects\E_OCP\maximum-coverage-location-master\002_data_OSG_NC'
    #----------------编码思路说明BEGIN：周鑫鑫  2023年7月13日20:33:36--------------------------------
    # intersect_shp的生成的步骤
    # 首先对候选点赋值塔高度，得到monitor_with_extra_height_shp点图层，会用到DEM，得到的是每个塔点位基座的海拔高度，增加KEY_ID字段；
    # 开始遍历monitor_with_extra_height_shp中的每一个点，
    #   进行可视域分析，输入数据包括：monitor_with_extra_height_shp中的每一个点、DEM、布设高度参数，输出数据是：栅格
    #   选取不为0的栅格，生成矢量面
    #   矢量面与耕地相交分析，得到可见耕地；
    #   对可见耕地增加KEY_ID字段，赋值塔ID字段；
    #   输出可见耕地shp数据
    # 可见耕地shp合并，变成一个SHP图层，此时会存在多个重叠在一起的面
    # 基于ZXQ生成fishnet及质心点图层；
    # 质心图层与可见耕地合并图层做相交，得到了intersect_shp，会自动生成FID_zhixin字段（前提这个zhixin.shp名字保持不变），一个面与一个点相交一次会得到一个相交点，因此会存在同一位置多个相交点，其中记录了FID_zhixin，可覆盖塔的KEY_ID；
    # 求取FID_zhixin最大编号、塔数量，用于初始化代价矩阵
    # 查询，给代价矩阵赋值；
    # ----------------编码思路说明END：周鑫鑫  2023年7月13日20:33:36--------------------------------

    # 生成全域的代价矩阵，不考虑ROI
    debugger_all_xzq(BASE_ROOT)

    # 生成ROI的代价矩阵，考虑ROI
    # debugger_part_roi(BASE_ROOT)


    # 给外面批量调用的；
    # batch_enter()


