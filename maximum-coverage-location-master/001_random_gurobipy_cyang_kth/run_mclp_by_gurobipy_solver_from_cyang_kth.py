from mclp_by_gurobipy_solver_from_cyang_kth import *

# The problem is defined as: given N points, find K circles with radius of r to cover as many points as possible.
# Example 1: Select 20 circles with radius of 0.1 to cover 300 points (uniform distribution)
# Generate points in uniform distribution
# points = np.random.rand(Npoints,2)

# Generate points in moon distribution
from sklearn.datasets import make_moons
from scipy.spatial import distance_matrix

M_demand_points = 300
N_provider_points_count = 100
S_radius = 0.2
P_facilities = 20

# 第一步，准备demand_points
# make_moons sklearn 中的函数
# make_moons是一个函数，用于生成数据集。它是sklearn.datasets中的一个函数。
# 它可以用来制作月亮型数据。具体用法如下：make_moons(n_samples=100, shuffle=True, noise=None, random_state=None)
# make_circles
# make_blobs 生成符合正态分布的聚类数据。
demand_points, _ = make_moons(M_demand_points, noise=0.15)
# demand_points, _ = make_blobs(M_demand_points)
# demand_points, _ = make_circles(M_demand_points, noise=0.15)
plot_input(demand_points)

# 第二步，准备provider_points
provider_points = generate_candidate_provider_sites(demand_points, N_provider_points_count)

# 第三步，准备可达关系矩阵
# 调用scipy.spatial的函数
Dij_matrix = distance_matrix(demand_points, provider_points)
mask1 = Dij_matrix <= S_radius
# 得出在范围内的所有Nj关系
Dij_matrix[mask1]=1
Dij_matrix[~mask1]=0

# 第四步，MCLP求解
# Run Case 1
opt_sites,f = mclp_entrance(demand_points, P_facilities,provider_points,Dij_matrix)
# 将结果展示出来
plot_result(demand_points, opt_sites, S_radius)
