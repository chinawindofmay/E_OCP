from mclp_ocp_by_gurobipy import *
import numpy as np


def case_changzhou_xinbei():
    M_demand_points = 8810
    N_provider_points_count = 480
    # S_radius = 0.2
    P_facilities = 100  # Gurobi 7660   贪心 7660.0   # 枚举 7578  # GA 7400
    # 第一步，准备demand_points
    # 读取摄像头信息
    camera_monitor_info = np.load('./ocp_data/price_matrix_488_8810.npz')['list_array'].T
    camera_monitor_info_small = camera_monitor_info  # [0:2000,:]
    demand_points = np.arange(0, camera_monitor_info_small.shape[0])  # 行 编号
    # 第二步，准备provider_points
    # # 生成摄像头ID
    provider_points = np.arange(0, camera_monitor_info_small.shape[1])  # 列 编号
    # 第三步，准备可达关系矩阵
    Dij_matrix = camera_monitor_info_small
    # 第四步，MCLP求解
    # Run Case 1
    opt_sites, f = mclp_entrance(demand_points, P_facilities, provider_points, Dij_matrix)



def case_University_of_North_Carolina_all():
    M_demand_points = 258
    N_provider_points_count = 20966
    # S_radius = 50 meters
    P_facilities = 50  # Gurobi  30:9453     40:12409     50:15008
    # 第一步，准备demand_points
    # 读取摄像头信息
    camera_monitor_info = np.load('./ocp_data/price_matrix_258_20966.npz')['list_array'].T
    camera_monitor_info_small = camera_monitor_info  # [0:2000,:]
    demand_points = np.arange(0, camera_monitor_info_small.shape[0])  # 行 编号
    # 第二步，准备provider_points
    # # 生成摄像头ID
    provider_points = np.arange(0, camera_monitor_info_small.shape[1])  # 列 编号
    # 第三步，准备可达关系矩阵
    Dij_matrix = camera_monitor_info_small
    # 第四步，MCLP求解
    # Run Case 1
    opt_sites, f = mclp_entrance(demand_points, P_facilities, provider_points, Dij_matrix)



def case_University_of_North_Carolina_all_with_distance_decay():
    M_demand_points = 258
    N_provider_points_count = 20966
    # S_radius = 50 meters
    P_facilities = 50  # Gurobi  30:9453     40:12409     50:15008
    # 第一步，准备demand_points
    # 读取摄像头信息
    camera_monitor_info = np.load(r'E:\002code_running\02GeoAI_Sub_Projects\E_OCP\maximum-coverage-location-master\002_ocp_cost_matrix_generator\open_data\result\price_matrix_50.npz')['list_array'].T
    camera_monitor_info_small = camera_monitor_info  # [0:2000,:]
    demand_points = np.arange(0, camera_monitor_info_small.shape[0])  # 行 编号
    # 第二步，准备provider_points
    # # 生成摄像头ID
    provider_points = np.arange(0, camera_monitor_info_small.shape[1])  # 列 编号
    # 第三步，准备可达关系矩阵
    Dij_matrix = camera_monitor_info_small
    # 第四步，MCLP求解
    # Run Case 1
    opt_sites, f = mclp_entrance(demand_points, P_facilities, provider_points, Dij_matrix)


def case_University_of_North_Carolina_part():
    M_demand_points = 258
    N_provider_points_count = 9653
    # S_radius = 50 meters
    P_facilities = 50  # Gurobi  30:7147     40:8254     50:8893
    # 第一步，准备demand_points
    # 读取摄像头信息
    camera_monitor_info = np.load('./ocp_data/price_matrix_258_9653_part.npz')['list_array'].T
    camera_monitor_info_small = camera_monitor_info  # [0:2000,:]
    demand_points = np.arange(0, camera_monitor_info_small.shape[0])  # 行 编号
    # 第二步，准备provider_points
    # # 生成摄像头ID
    provider_points = np.arange(0, camera_monitor_info_small.shape[1])  # 列 编号
    # 第三步，准备可达关系矩阵
    Dij_matrix = camera_monitor_info_small
    # 第四步，MCLP求解
    # Run Case 1
    opt_sites, f = mclp_entrance(demand_points, P_facilities, provider_points, Dij_matrix)


# case_changzhou_xinbei()
# case_University_of_North_Carolina_all()
case_University_of_North_Carolina_part()