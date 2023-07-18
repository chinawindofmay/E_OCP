from mclp_ocp_by_gurobipy import *
import numpy as np

#
# def case_changzhou_xinbei():
#     M_demand_points = 8810
#     N_provider_points_count = 480
#     # S_radius = 0.2
#     P_facilities = 100  # Gurobi 7660   贪心 7660.0   # 枚举 7578  # GA 7400
#     # 第一步，准备demand_points
#     # 读取摄像头信息
#     camera_monitor_info = np.load('./ocp_data/price_matrix_488_8810.npz')['list_array'].T
#     camera_monitor_info_small = camera_monitor_info  # [0:2000,:]
#     demand_points = np.arange(0, camera_monitor_info_small.shape[0])  # 行 编号
#     # 第二步，准备provider_points
#     # # 生成摄像头ID
#     provider_points = np.arange(0, camera_monitor_info_small.shape[1])  # 列 编号
#     # 第三步，准备可达关系矩阵
#     Dij_matrix = camera_monitor_info_small
#     # 第四步，MCLP求解
#     # Run Case 1
#     opt_sites, f = mclp_ocp_entrance_no_distance(demand_points, P_facilities, provider_points, Dij_matrix)
#
#
# def case_UniversityNC_all_xzq_with_distance_decay():
#     """
#     全部区域，且考虑距离衰减，采用潜力模型求解
#     潜力模型的结果并没有什么意义，所以暂时放弃，2023年7月18日16:09:59
#     Returns:
#
#     """
#     M_demand_points = 5000
#     N_provider_points_count = 20
#     # S_radius = 100 meters
#     P_facilities = 10  # Gurobi  30:9453     40:12409     50:15008
#     # 第一步，准备demand_points
#     # 读取摄像头信息
#     camera_monitor_info = np.load(r'D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_ocp_cost_matrix_generator\open_data\result_mid\price_matrix_100.npz')['price_matrix_with_distance_reduce_more'].T
#     all_opt_providers_save_path = r'../002_ocp_cost_matrix_generator/open_data/result_mid/all_opt_providers_with_distance_decay_mid.npz'
#
#     camera_monitor_info_mid = camera_monitor_info  # [0:2000,:]
#     demand_points = np.arange(0, camera_monitor_info_mid.shape[0])  # 行 编号
#     # 第二步，准备provider_points
#     # # 生成摄像头ID
#     provider_points = np.arange(0, camera_monitor_info_mid.shape[1])  # 列 编号
#     # 第三步，准备可达关系矩阵
#     Dij_matrix = camera_monitor_info_mid
#     # 第四步，MCLP求解
#     # Run Case 1
#     opt_sites, all_opt_providers, f = mclp_ocp_entrance_with_distance_decay(demand_points, P_facilities, provider_points, Dij_matrix)
#     np.savez(all_opt_providers_save_path, best_elist_solution=all_opt_providers)


# def case_UniversityNC_part_roi_with_distance_decay():
#     """
#     部分的ROI区域，且考虑距离衰减，采用潜力模型求解
#     潜力模型的结果并没有什么意义，所以暂时放弃，2023年7月18日16:09:59
#     Returns:
#
#     """
#     M_demand_points = 5000
#     N_provider_points_count = 20
#     # S_radius = 100 meters
#     P_facilities = 10  # Gurobi  30:9453     40:12409     50:15008
#     # 第一步，准备demand_points
#     # 读取摄像头信息
#     camera_monitor_info = np.load(r'D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_ocp_cost_matrix_generator\open_data\result_mid_part_gd\price_matrix_100.npz')['price_matrix_with_distance_reduce_more'].T
#     all_opt_providers_save_path = r'../002_ocp_cost_matrix_generator/open_data/result_mid_part_gd/all_opt_providers_with_distance_decay_mid.npz'
#
#     camera_monitor_info_mid = camera_monitor_info  # [0:2000,:]
#     demand_points = np.arange(0, camera_monitor_info_mid.shape[0])  # 行 编号
#     # 第二步，准备provider_points
#     # # 生成摄像头ID
#     provider_points = np.arange(0, camera_monitor_info_mid.shape[1])  # 列 编号
#     # 第三步，准备可达关系矩阵
#     Dij_matrix = camera_monitor_info_mid
#     # 第四步，MCLP求解
#     # Run Case 1
#     opt_sites, all_opt_providers, f = mclp_ocp_entrance_with_distance_decay(demand_points, P_facilities, provider_points, Dij_matrix)
#     np.savez(all_opt_providers_save_path, best_elist_solution=all_opt_providers)




def case_UniversityNC_all_xzq_no_distance_decay(BASE_ROOT):
    """
    全部区域，不考虑距离衰减，采用MCLP
    Returns:

    """
    M_demand_points = 5000
    N_provider_points_count = 258
    # S_radius = 100 meters
    P_facilities = 10  # Gurobi  30:9453     40:12409     50:15008
    # 第一步，准备demand_points
    # 读取摄像头信息

    camera_monitor_info = np.load(r'{0}\price_matrix_50.npz'.format(BASE_ROOT))['price_matrix_no_distance_reduce_more'].T
    all_opt_providers_save_path = r'{0}\all_xzq_gurobi_{1}.npz'.format(BASE_ROOT,P_facilities)

    camera_monitor_info_mid = camera_monitor_info  # [0:2000,:]
    demand_points = np.arange(0, camera_monitor_info_mid.shape[0])  # 行 编号
    # 第二步，准备provider_points
    # # 生成摄像头ID
    provider_points = np.arange(0, camera_monitor_info_mid.shape[1])  # 列 编号
    # 第三步，准备可达关系矩阵
    Dij_matrix = camera_monitor_info_mid
    # 第四步，MCLP求解
    # Run Case 1
    opt_sites, all_opt_providers, f = mclp_ocp_entrance_no_distance(demand_points, P_facilities, provider_points, Dij_matrix)
    np.savez(all_opt_providers_save_path, best_elist_solution=all_opt_providers)





def case_UniversityNC_part_roi_no_distance_decay(BASE_ROOT):
    """
        部分的ROI区域，不考虑距离衰减，采用MCLP直接求解
        Returns:

    """
    M_demand_points = 5000
    N_provider_points_count = 258
    # S_radius = 100 meters
    P_facilities = 10  # Gurobi  30:9453     40:12409     50:15008
    # 第一步，准备demand_points
    # 读取摄像头信息

    camera_monitor_info = np.load(r'{0}\price_matrix_50.npz'.format(BASE_ROOT))['price_matrix_no_distance_reduce_more'].T
    all_opt_providers_save_path = r'{0}\part_roi_gurobi_{1}.npz'.format(BASE_ROOT,P_facilities)

    camera_monitor_info_mid = camera_monitor_info  # [0:2000,:]
    demand_points = np.arange(0, camera_monitor_info_mid.shape[0])  # 行 编号
    # 第二步，准备provider_points
    # # 生成摄像头ID
    provider_points = np.arange(0, camera_monitor_info_mid.shape[1])  # 列 编号
    # 第三步，准备可达关系矩阵
    Dij_matrix = camera_monitor_info_mid
    # 第四步，MCLP求解
    # Run Case 1
    opt_sites, all_opt_providers, f = mclp_ocp_entrance_no_distance(demand_points, P_facilities, provider_points, Dij_matrix)
    np.savez(all_opt_providers_save_path, best_elist_solution=all_opt_providers)



if __name__=="__main__":
    # case_changzhou_xinbei()
    BASE_ROOT=r'D:\022_common_code\001_research_code\E_OCP\maximum-coverage-location-master\002_data_OSG_NC'
    BASE_ROOT=r'E:\002code_running\02GeoAI_Sub_Projects\E_OCP\maximum-coverage-location-master\002_data_OSG_NC'
    #all 两种方式
    # case_UniversityNC_all_xzq_with_distance_decay()
    case_UniversityNC_all_xzq_no_distance_decay(BASE_ROOT)

    #part 两种方式
    # case_UniversityNC_part_roi_with_distance_decay()
    case_UniversityNC_part_roi_no_distance_decay(BASE_ROOT)