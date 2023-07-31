import json
from urllib.request import urlopen
import urllib
import math
import pandas as pd

def find_route(s1,s2,t1,t2):
    # /directionlite/v1/walking
    s1 = str(s1)
    s2 = str(s2)
    t1 = str(t1)
    t2 = str(t2)

    a1=r"http://api.map.baidu.com/directionlite/v1/walking?"
    a2=r"origin="+s1+","+s2
    a3=r"&destination="+t1+","+t2
    a4=r"&ak="
    ak=[]
    a5=r"&coord_type=wgs84"
    a6=r"&steps_info=1"

    url=a1+a2+a3+a4+ak[ct_ak]+a5+a6

    b = urlopen(url)
    data=b.read() 
    c = data.decode("utf-8")
    result = json.loads(c)
    # print(result)

    return result


from geopy.distance import geodesic

def point_to_segment_distance(point_lat, point_lon, segment_start_lat, segment_start_lon, segment_end_lat, segment_end_lon):
    # 将经纬度转换为球面坐标
    point = (point_lat, point_lon)
    segment_start = (segment_start_lat, segment_start_lon)
    segment_end = (segment_end_lat, segment_end_lon)

    # 计算点到线段两个端点的距离
    distance_start = geodesic(point, segment_start).meters
    distance_end = geodesic(point, segment_end).meters
    
    # 计算点到线段的垂直投影点

    dist = geodesic(segment_start, segment_end).meters
    if dist == 0:
        return distance_start
    p = (dist + distance_end + distance_start) / 2
    area =( p*(p-dist)*(p-distance_start)*(p-distance_end))**0.5
    d = area * 2 / dist

    l1 = (distance_start**2 - d ** 2) ** 0.5
    l2 = (distance_end**2 - d ** 2) ** 0.5

    if abs(l1 + l2 - dist) < 0.1:
        return d
    else:
        return min(distance_start, distance_end)


x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)

def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret
def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]
def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]
def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)

def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]
def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return [lng, lat]
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]
def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)

def haversine_distance(lat1, lon1, lat2, lon2):
    # 将经纬度转换为弧度
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # 使用haversine公式计算距离
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c * 1000  # 6371是地球半径，以米为单位计算距离
    return distance


# 住区数据
file_path_residential = 'path/to/residential.xlsx' 
raw_data_residential = pd.read_excel(file_path_residential, header=0)  

data_residential = raw_data_residential.values

residential_indexs = data_residential[:, 0]
residential_lons = data_residential[:, 1]
residential_lats = data_residential[:, 2]
print(len(residential_indexs))
print(residential_lats[0])

# 设施数据

# 10 / 5分钟生活圈
facility_time = 10

file_path_facility = 'path/to/market.xlsx' 
raw_data_facility = pd.read_excel(file_path_facility, header=0)  

data_facility = raw_data_facility.values

facility_indexs = data_facility[:, 0]
print(len(facility_indexs))
facility_lons = data_facility[:, 2]
print(facility_lons[0])
facility_lats = data_facility[:, 3]
print(facility_lats[0])

# v 视障 m 肢障手动轮椅 me 肢障电动轮椅

v_time = -1 # 到达时间，单位 分钟 超过15min为-1
m_time = -1
me_time = -1

# 能够到达的社区和设施序号对
reachable = {} # 健全人
v_reachable = {}
m_reachable = {}
me_reachable = {}

# 被阻断或减速后超时的社区和设施路线
v_blocked = {}
m_blocked = {}
me_blocked = {}

# 直线距离过长
straight_dist = {}

# 算路后全程时间过长
v_too_long = {}
m_too_long = {}
me_too_long = {}

# 出行时间的系数
movement_index = 1.24 / 0.69
electric_movement_index = 1.24 / 0.89
visual_index = 1.24 / 0.92

# 断点到路径的缓冲区半径 米
buffer = 30

# 处理阻断信息
movement_block_file = 'path/to/movement_block.xlsx' 
movement_slowdown_file = 'path/to/movement_slowdown.xlsx' 
visual_block_file = 'path/to/visual_block.xlsx' 
vraw_data = pd.read_excel(visual_block_file, header=0)  

vdata = vraw_data.values

vblock_lons = vdata[:, 2]
vblock_lats = vdata[:, 3]
print(len(vblock_lons))

mraw_data = pd.read_excel(movement_block_file, header=0)  

mdata = mraw_data.values

mblock_lons = mdata[:, 2]
mblock_lats = mdata[:, 3]
print(len(mblock_lons))


msraw_data = pd.read_excel(movement_slowdown_file, header=0)  

msdata = msraw_data.values

msblock_lons = msdata[:, 2]
msblock_lats = msdata[:, 3]
print(len(msblock_lons))

exit_flag = False # api用完退出外层循环
api_count = 0 # 统计api

for i in range(5):
    if (exit_flag): 
        break
    # 住区循环 len(residential_indexs)
    print("residential", i)
    res_index = i
    s1 = residential_lats[i]
    s2 = residential_lons[i]

    for j in range(len(facility_indexs)):
        if i in v_reachable and i in m_reachable and i in me_reachable:
            continue
        # 设施循环 len(facility_indexs)
        fac_index = j
        t1 = facility_lats[j]
        t2 = facility_lons[j]

        straight_distance = haversine_distance(s1, s2, t1, t2)
        if straight_distance > 700:  ## 剪枝 1500? 1200?
            # print(i, j, straight_distance, "straight distance too far")
            if i not in straight_dist:
                straight_dist[i]=[j]
            else:
                straight_dist[i].append(j)
            continue
        
        try:
            # 找路
            # print(s1, s2, t1, t2)
            route = find_route(s1,s2,t1,t2)
            api_count += 1
            # print(route)
            
            # 处理路线信息
            steps = route["result"]["routes"][0]["steps"]
            # print( type(steps))
            original_duration = int(route["result"]["routes"][0]["duration"]) / 60

            if original_duration <= 10:
                if i not in reachable:
                    reachable[i] = j
            

        except Exception as e:
            print(e)
            print("end at", i, j)
            print("count api", api_count)
            # print("number of reachable", len(v_reachable))
            # print("blocked", len(v_blocked))
            # print("too long", len(v_too_long))
            # print("reachable", v_reachable)
            # print("blocked", v_blocked)
            # print("number of reachable", len(m_reachable))
            # print("blocked", len(m_blocked))
            # print("too long", len(m_too_long))
            # print("reachable", m_reachable)
            # print("blocked", m_blocked)
            # print("number of reachable", len(me_reachable))
            # print("blocked", len(me_blocked))
            # print("too long", len(me_too_long))
            # print("reachable", me_reachable)
            # print("blocked", me_blocked)
            # print("straight dist", len(straight_dist))
            exit_flag = True
            break

        else:
            if i not in v_reachable:
                # 视障计算
                v_time = original_duration * visual_index ## 
                if v_time > facility_time:
                    # 超时
                    if i not in v_too_long:
                        v_too_long[i]=[j]
                    else:
                        v_too_long[i].append(j)
                    # print(i, j, time, original_duration, "route too long")
                else:
                    block_index = 0

                    for k in range(len(vblock_lons)): ##
                        # visual_block ##
                        b1 = vblock_lons[k] ##
                        b2 = vblock_lats[k] ##

                        distance = buffer * 2 # 初始值设为大于缓冲量半径的值

                        for step in steps:
                            s1 = float(step["start_location"]["lat"])
                            s2 = float(step["start_location"]["lng"])

                            t1 = float(step["end_location"]["lat"])
                            t2 = float(step["end_location"]["lng"])
                            # print("*************************************************")
                            # print(s1, s2, t1, t2)
                            s2, s1 = bd09_to_wgs84(s2, s1)
                            t2, t1 = bd09_to_wgs84(t2, t1)

                            distance = min(distance, point_to_segment_distance(b2, b1, s1, s2, t1, t2))

                        if distance <= buffer:
                            v_time = -1
                            # print("distance", distance)
                            block_index = k
                            break
                    if v_time == -1:
                        # 路线被阻挡
                        # print(i, j, v_time,original_duration, block_index, "blocked")
                        if i not in v_blocked:
                            v_blocked[i]=[j]
                        else:
                            v_blocked[i].append(j)
                    elif v_time > facility_time:
                        # print(i, j, v_time, original_duration,"route too long")
                        if i not in v_too_long:
                            v_too_long[i]=[j]
                        else:
                            v_too_long[i].append(j)
                    elif v_time <= facility_time:
                        print(i, j, v_time, original_duration, "reachable route")
                        if i not in v_reachable:
                            v_reachable[i]=[j]
                        else:
                            v_reachable[i].append(j)
            if i not in m_reachable:
                # 肢障计算
                m_time = original_duration ## 
                if m_time > facility_time:
                    # 超时
                    if i not in m_too_long:
                        m_too_long[i]=[j]
                    else:
                        m_too_long[i].append(j)
                    # print(i, j, time, original_duration, "route too long")
                else:
                    block_index = 0

                    for k in range(len(mblock_lons)): ##
                        # movement block ##
                        b1 = mblock_lons[k] ##
                        b2 = mblock_lats[k] ##

                        distance = buffer * 2 # 初始值设为大于缓冲量半径的值

                        for step in steps:
                            s1 = float(step["start_location"]["lat"])
                            s2 = float(step["start_location"]["lng"])

                            t1 = float(step["end_location"]["lat"])
                            t2 = float(step["end_location"]["lng"])
                            # print("*************************************************")
                            # print(s1, s2, t1, t2)
                            s2, s1 = bd09_to_wgs84(s2, s1)
                            t2, t1 = bd09_to_wgs84(t2, t1)

                            distance = min(distance, point_to_segment_distance(b2, b1, s1, s2, t1, t2))

                        if distance <= buffer:
                            m_time = -1
                            # print("distance ", distance)
                            block_index = k
                            break
                    if m_time == -1:
                        # 路线被阻挡
                        # print(i, j, m_time,original_duration, block_index, "blocked")
                        if i not in m_blocked:
                            m_blocked[i]=[j]
                        else:
                            m_blocked[i].append(j)
                    elif m_time > facility_time:
                        # print(i, j, m_time, original_duration,"route too long")
                        if i not in m_too_long:
                            m_too_long[i]=[j]
                        else:
                            m_too_long[i].append(j)
                    else:
                        # 肢障阻速
                        for p in range(len(msblock_lons)): ##
                            # movement slowdown block ##
                            b1 = msblock_lons[p] ##
                            b2 = msblock_lats[p] ##

                            distance = buffer * 2 # 初始值设为大于缓冲量半径的值

                            for step in steps:
                                s1 = float(step["start_location"]["lat"])
                                s2 = float(step["start_location"]["lng"])

                                t1 = float(step["end_location"]["lat"])
                                t2 = float(step["end_location"]["lng"])
                                # print("*************************************************")
                                # print(s1, s2, t1, t2)
                                s2, s1 = bd09_to_wgs84(s2, s1)
                                t2, t1 = bd09_to_wgs84(t2, t1)

                                distance = min(distance, point_to_segment_distance(b2, b1, s1, s2, t1, t2))

                            if distance <= buffer:
                                m_time = movement_index * original_duration
                                print("distance", distance)
                                break
                        if m_time < facility_time:
                            print(i, j, m_time, original_duration, "reachable route")
                            if i not in m_reachable:
                                m_reachable[i]=[j]
                            else:
                                m_reachable[i].append(j)
                        else:
                            # print("slowed down by block, m_time = ", m_time)
                            if i not in m_blocked:
                                m_blocked[i]=[j]
                            else:
                                m_blocked[i].append(j)
            if i not in me_reachable:
                # 肢障电动轮椅计算
                me_time = original_duration ## 
                if me_time > facility_time:
                    # 超时
                    if i not in me_too_long:
                        me_too_long[i]=[j]
                    else:
                        me_too_long[i].append(j)
                    # print(i, j, time, original_duration, "route too long")
                else:
                    block_index = 0

                    for k in range(len(mblock_lons)): ##
                        # movement block ##
                        b1 = mblock_lons[k] ##
                        b2 = mblock_lats[k] ##

                        distance = buffer * 2 # 初始值设为大于缓冲量半径的值

                        for step in steps:
                            s1 = float(step["start_location"]["lat"])
                            s2 = float(step["start_location"]["lng"])

                            t1 = float(step["end_location"]["lat"])
                            t2 = float(step["end_location"]["lng"])
                            # print("*************************************************")
                            # print(s1, s2, t1, t2)
                            s2, s1 = bd09_to_wgs84(s2, s1)
                            t2, t1 = bd09_to_wgs84(t2, t1)

                            distance = min(distance, point_to_segment_distance(b2, b1, s1, s2, t1, t2))

                        if distance <= buffer:
                            me_time = -1
                            # print("distance ", distance)
                            block_index = k
                            break
                    if me_time == -1:
                        # 路线被阻挡
                        # print(i, j, me_time,original_duration, block_index, "blocked")
                        if i not in me_blocked:
                            me_blocked[i]=[j]
                        else:
                            me_blocked[i].append(j)
                    elif me_time > facility_time:
                        # print(i, j, me_time, original_duration,"route too long")
                        if i not in me_too_long:
                            me_too_long[i]=[j]
                        else:
                            me_too_long[i].append(j)
                    else:
                        # 肢障阻速
                        for p in range(len(msblock_lons)): ##
                            # movement slowdown block ##
                            b1 = msblock_lons[p] ##
                            b2 = msblock_lats[p] ##

                            distance = buffer * 2 # 初始值设为大于缓冲量半径的值

                            for step in steps:
                                s1 = float(step["start_location"]["lat"])
                                s2 = float(step["start_location"]["lng"])

                                t1 = float(step["end_location"]["lat"])
                                t2 = float(step["end_location"]["lng"])
                                # print("*************************************************")
                                # print(s1, s2, t1, t2)
                                s2, s1 = bd09_to_wgs84(s2, s1)
                                t2, t1 = bd09_to_wgs84(t2, t1)

                                distance = min(distance, point_to_segment_distance(b2, b1, s1, s2, t1, t2))

                            if distance <= buffer:
                                me_time = electric_movement_index * original_duration
                                print("distance", distance)
                                break
                        if me_time < facility_time:
                            print(i, j, me_time, original_duration, "reachable route")
                            if i not in me_reachable:
                                me_reachable[i]=[j]
                            else:
                                me_reachable[i].append(j)
                        else:
                            print("slowed down by block, me_time = ", me_time)
                            if i not in me_blocked:
                                me_blocked[i]=[j]
                            else:
                                me_blocked[i].append(j)

        
print("count api", api_count)
print("视障")
print("number of reachable", len(v_reachable))
print("blocked", len(v_blocked))
print("too long", len(v_too_long))
print("reachable", v_reachable)
# print("blocked", v_blocked)

print("肢障手动轮椅")
print("number of reachable", len(m_reachable))
print("blocked", len(m_blocked))
print("too long", len(m_too_long))
print("reachable", m_reachable)
# print("blocked", m_blocked)

print("肢障电动轮椅")
print("number of reachable", len(me_reachable))
print("blocked", len(me_blocked))
print("too long", len(me_too_long))
print("reachable", me_reachable)
# print("blocked", me_blocked)
print("straight dist", len(straight_dist))

print("健全人", len(reachable), reachable)