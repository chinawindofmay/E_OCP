"""

Python implementation of the maximum coverage location problem.

The program randomly generates a set of candidate sites, among 
which the K optimal candidates are selected. The optimization 
problem is solved by integer programming. 

Author: Can Yang
Date: 2019-11-22

MIT License

Copyright (c) 2019 Can Yang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""


import numpy as np

import gurobipy as GRBP
# from gurobipy import *
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon, Point
from numpy import random

def generate_candidate_provider_sites(demand_points, N_provider_points_count=100):
    '''
    Generate M candidate sites with the convex hull of a point set
    Input:
        points: a Numpy array with shape of (N,2)
        M: the number of candidate sites to generate
    Return:
        sites: a Numpy array with shape of (M,2)
    '''
    hull = ConvexHull(demand_points)
    polygon_points = demand_points[hull.vertices]
    poly = Polygon(polygon_points)
    min_x, min_y, max_x, max_y = poly.bounds
    provider_sites = []
    while len(provider_sites) < N_provider_points_count:
        random_point = Point([random.uniform(min_x, max_x),
                             random.uniform(min_y, max_y)])
        if (random_point.within(poly)):
            provider_sites.append(random_point)
    return np.array([(p.x,p.y) for p in provider_sites])

def mclp_ocp_entrance_no_distance(demand_points, P_facilities_count, provider_points, Dij_matrix):
    """
    Solve maximum covering location problem
    Input:
        demand_points: input points, Numpy array in shape of [M,2]
        P_facilities_count: the number of sites to select
        S_radius: the radius of circle
        provider_points: the candidate sites, Numpy array in shape of [N,2]
        the ConvexHull wrapped by the polygon
    Return:
        opt_sites: locations K optimal sites, Numpy array in shape of [P,2]
        f: the optimal value of the objective function
    """
    # 打印元信息
    print('----- Configurations -----')
    print('  Number of demand_points %g' % demand_points.shape[0])
    print('  P_facilities_count %g' % P_facilities_count)
    print('  provider_points %g' % provider_points.shape[0])
    print('  Dij_matrix ', Dij_matrix.shape[0], Dij_matrix.shape[1])

    import time
    start = time.time()
    # 第0步，输入，条件数据准备
    J = provider_points.shape[0]
    I = demand_points.shape[0]

    # Build model
    # 如果您想使用gurobipy进行整数规划，可以使用
    # 第1步：GRBP.Model()
    # 第2步：Model.addVar()函数来添加变量
    # 第3步：使用Model.addConstr()函数来添加约束条件
    # 第4步：使用Model.setObjective()
    # 第5步：执行优化求解

    # 第一步，初始化模型，函数来设置目标函数。
    mclpmodel = GRBP.Model()
    # Add variables
    x = {}
    y = {}
    # 第二步添加求解变量，需求点集合，yi，都是二值的；
    for i in range(I):
      y[i] = mclpmodel.addVar(vtype=GRBP.GRB.BINARY, name="y%d" % i)
    # 第二步添加求解变量，供给点集合，xj，都是二值的；
    for j in range(J):
      x[j] = mclpmodel.addVar(vtype=GRBP.GRB.BINARY, name="x%d" % j)
    mclpmodel.update()
    # 第三步添加约束函数，Add constraints，这里是总量约束
    mclpmodel.addConstr(GRBP.quicksum(x[j] for j in range(J)) == P_facilities_count)
    # 第二步添加求解变量，Add constraints，这里是最大覆盖约束.
    # 关键是在这里，如果\textbf{需求点$i$的可达供给点集合实际建设结果}等于0，说明需求点$i$没有被服务覆盖，此时\underline{将$y_i$设置为0}，
    # 会影响目标函数值的大小
    for i in range(I): #对于所有的i，都添加一个约束
        # mclpmodel.addConstr(GRBP.quicksum(x[j] for j in np.where(Dij_matrix[i]==1)[0]) >= y[i])   #可达供给点集合Ni中所有对象加和与yi直接关系  01绝对覆盖关系的时候
        mclpmodel.addConstr(GRBP.quicksum(x[j] for j in np.where(Dij_matrix[i]>0)[0]) >= y[i])   #可达供给点集合Ni中所有对象加和与yi直接关系  概率覆盖关系的时候
    # 第四步，目标函数，设置目标函数，ai*yi，且为最大
    mclpmodel.setObjective(GRBP.quicksum(y[i]for i in range(I)),GRBP.GRB.MAXIMIZE)
    mclpmodel.setParam('OutputFlag', 0)
    # 第五步，执行优化求解，执行优化计算，主要是用到了
    mclpmodel.optimize()
    end = time.time()
    print('----- Output -----')
    print('  Running time : %s seconds' % float(end-start))
    print('  Optimal coverage points: %g' % mclpmodel.objVal)

    # 第0步，输出优化结果，主要要的是xj==1的情况
    solution = []
    if mclpmodel.status == GRBP.GRB.Status.OPTIMAL:
        for v in mclpmodel.getVars():
            # print v.varName,v.x
            if v.x==1 and v.varName[0]=="x":
               solution.append(int(v.varName[1:]))  # int(v.varName[1:])对应为1的点的序号，如X24,则是24
    opt_sites = provider_points[solution]  #provider_points存储的是经纬度坐标值，这样筛选到了建设点的经纬度坐标值
    all_opt_providers=np.zeros(J,dtype=int)
    all_opt_providers[opt_sites]=1
    return opt_sites,all_opt_providers,mclpmodel.objVal


def mclp_ocp_entrance_with_distance_decay(demand_points, P_facilities_count, provider_points, Dij_matrix):
    """
    Solve maximum covering location problem
    Input:
        demand_points: input points, Numpy array in shape of [M,2]
        P_facilities_count: the number of sites to select
        S_radius: the radius of circle
        provider_points: the candidate sites, Numpy array in shape of [N,2]
        the ConvexHull wrapped by the polygon
    Return:
        opt_sites: locations K optimal sites, Numpy array in shape of [P,2]
        f: the optimal value of the objective function
    """
    # 打印元信息
    print('----- Configurations -----')
    print('  Number of demand_points %g' % demand_points.shape[0])
    print('  P_facilities_count %g' % P_facilities_count)
    print('  provider_points %g' % provider_points.shape[0])
    print('  Dij_matrix ', Dij_matrix.shape[0], Dij_matrix.shape[1])

    import time
    start = time.time()
    # 第0步，输入，条件数据准备
    J = provider_points.shape[0]
    I = demand_points.shape[0]

    # Build model
    # 如果您想使用gurobipy进行整数规划，可以使用
    # 第1步：GRBP.Model()
    # 第2步：Model.addVar()函数来添加变量
    # 第3步：使用Model.addConstr()函数来添加约束条件
    # 第4步：使用Model.setObjective()
    # 第5步：执行优化求解

    # 第一步，初始化模型，函数来设置目标函数。
    mclpmodel = GRBP.Model()

    # Add variables
    x = {}
    y = {}
    # 第二步添加求解变量，需求点集合，yi，都是二值的；
    for i in range(I):
      y[i] = mclpmodel.addVar(vtype=GRBP.GRB.BINARY, name="y%d" % i)
    # 第二步添加求解变量，供给点集合，xj，都是二值的；
    for j in range(J):
      x[j] = mclpmodel.addVar(vtype=GRBP.GRB.BINARY, name="x%d" % j)
    mclpmodel.update()
    # 第三步添加约束函数，Add constraints，这里是总量约束
    mclpmodel.addConstr(GRBP.quicksum(x[j] for j in range(J)) == P_facilities_count)
    # 第二步添加求解变量，Add constraints，这里是最大覆盖约束.
    # 关键是在这里，如果\textbf{需求点$i$的可达供给点集合实际建设结果}等于0，说明需求点$i$没有被服务覆盖，此时\underline{将$y_i$设置为0}，
    # 会影响目标函数值的大小
    for i in range(I): #对于所有的i，都添加一个约束
        # mclpmodel.addConstr(GRBP.quicksum(x[j] for j in np.where(Dij_matrix[i]==1)[0]) >= y[i])   #可达供给点集合Ni中所有对象加和与yi直接关系  01绝对覆盖关系的时候
        mclpmodel.addConstr(GRBP.quicksum(x[j] for j in np.where(Dij_matrix[i]>0)[0]) >= y[i])   #可达供给点集合Ni中所有对象加和与yi直接关系  概率覆盖关系的时候
    # 第四步，目标函数，设置目标函数，ai*yi，且为最大
    # mclpmodel.setObjective(GRBP.quicksum(y[i]for i in range(I)),GRBP.GRB.MAXIMIZE)
    # ——————————————————————————————————————BEGIN将ai增加到目标函数中去，原来的OCP中忽略了每个质心点（需求点）的需求急迫程度，周鑫鑫，2023年7月14日09:18:26—————
    # 主要参考2SFCA可达性模型中的潜力模型，
    # 先通过Dij_matrix，构建潜力模型，计算得到每个需求点的ai可达性
    # 考虑到0是不可见，需要将其转为一个很大的数字，减少影响
    Dij_matrix_copy = Dij_matrix.copy()
    Dij_matrix_copy[Dij_matrix_copy == 0] = 1000000
    # 考虑到需求点有可能离候选供给点非常近，从而导致求商结果非常大，需要将<10的赋值为10
    Dij_matrix_copy[Dij_matrix_copy < 10] = 10
    VJ = np.sum(100 / Dij_matrix_copy, axis=0)  # 压缩成一行，即是将每列求和
    AI = np.sum(100 / (Dij_matrix_copy * VJ), axis=1)  # 压缩成一列，即将每行求和，得到ai
    mclpmodel.setObjective(GRBP.quicksum(AI[i]*y[i]for i in range(I)),GRBP.GRB.MAXIMIZE)   # 考虑到可达性差异
    # ——————————————————————————————————————END，周鑫鑫，2023年7月14日09:18:37————————————————————————————————————————————————————————————
    mclpmodel.setParam('OutputFlag', 0)
    # 第五步，执行优化求解，执行优化计算，主要是用到了
    mclpmodel.optimize()
    end = time.time()
    print('----- Output -----')
    print('  Running time : %s seconds' % float(end-start))
    print('  Optimal coverage points: %g' % mclpmodel.objVal)

    # 第0步，输出优化结果，主要要的是xj==1的情况
    solution = []
    if mclpmodel.status == GRBP.GRB.Status.OPTIMAL:
        for v in mclpmodel.getVars():
            # print v.varName,v.x
            if v.x==1 and v.varName[0]=="x":
               solution.append(int(v.varName[1:]))  # int(v.varName[1:])对应为1的点的序号，如X24,则是24
    opt_sites = provider_points[solution]  #provider_points存储的是经纬度坐标值，这样筛选到了建设点的经纬度坐标值
    all_opt_providers=np.zeros(J,dtype=int)
    all_opt_providers[opt_sites]=1
    return opt_sites,all_opt_providers,mclpmodel.objVal

def plot_input(points):
    '''
    Plot the result
    Input:
        points: input points, Numpy array in shape of [N,2]
        opt_sites: locations K optimal sites, Numpy array in shape of [K,2]
        radius: the radius of circle
    '''
    from matplotlib import pyplot as plt
    fig = plt.figure(figsize=(8,8))
    plt.scatter(points[:,0],points[:,1],c='C0')
    ax = plt.gca()
    ax.axis('equal')
    ax.tick_params(axis='both',left=False, top=False, right=False,
                       bottom=False, labelleft=False, labeltop=False,
                       labelright=False, labelbottom=False)
    plt.show()

def plot_result(points,opt_sites,radius):
    '''
    Plot the result
    Input:
        points: input points, Numpy array in shape of [N,2]
        opt_sites: locations K optimal sites, Numpy array in shape of [K,2]
        radius: the radius of circle
    '''
    from matplotlib import pyplot as plt
    fig = plt.figure(figsize=(8,8))
    plt.scatter(points[:,0],points[:,1],c='C0')
    ax = plt.gca()
    plt.scatter(opt_sites[:,0],opt_sites[:,1],c='C1',marker='+')
    for site in opt_sites:
        circle = plt.Circle(site, radius, color='C1',fill=False,lw=2)
        ax.add_artist(circle)
    ax.axis('equal')
    ax.tick_params(axis='both',left=False, top=False, right=False,
                       bottom=False, labelleft=False, labeltop=False,
                       labelright=False, labelbottom=False)

    plt.show()
