from django.shortcuts import render
import pandas as pd
import math
import happybase
import folium
import os
from django.conf import settings
from django.shortcuts import render

def home(request):
    """
    系统主页
    """
    return render(request, 'mapapp/home.html')

def price_histogram(request):
    """价格分布直方图"""
    return render(request, 'mapapp/价格分布直方图.html')

def district_price_distribution(request):
    """北京市各区域租房价格分布"""
    return render(request, 'mapapp/北京市各区域租房价格分布.html')

def district_rental_quantity(request):
    """北京市各区房屋租赁数量区域分布"""
    return render(request, 'mapapp/北京市各区房屋租赁数量区域分布.html')

def shortest_rent_cycle(request):
    """北京短租房最短周期分别"""
    return render(request, 'mapapp/北京短租房最短周期分别.html')

def rental_pie_chart(request):
    """北京租房饼图分布"""
    return render(request, 'mapapp/北京租房饼图分布.html')

def rental_time_distribution(request):
    """可租时间分布"""
    return render(request, 'mapapp/可租时间分布.html')

def house_type_distribution(request):
    """房屋类型分布"""
    return render(request, 'mapapp/房屋类型分布.html')

def bdToGaoDe(lon, lat):
    """
    坐标转化
    :param lon: 经度
    :param lat: 纬度
    :return: 转换后的经纬度
    """
    PI = 3.14159265358979324 * 3000.0 / 180.0
    x = lon - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * PI)
    lon = z * math.cos(theta)
    lat = z * math.sin(theta)
    return lon, lat

def query_hbase(price=None, min_nights=None):
    # 创建 HBase 客户端连接
    connection = happybase.Connection('192.168.88.132')
    connection.open()
    filters = []

    if price is not None:
        price_filter = "SingleColumnValueFilter('info', 'price', =, 'binary:{0}')".format(str(price))
        filters.append(price_filter)

    if min_nights is not None:
        min_nights_filter = "SingleColumnValueFilter('info', 'minimum_nights', =, 'binary:{0}')".format(str(min_nights))
        filters.append(min_nights_filter)

    filter_str = " AND ".join(filters) if filters else None

    table = connection.table('locat')
    rows = table.scan(filter=filter_str)

    result = []
    for row in rows:
        result.append(row)

    return result

def map_view(request):
    # 默认值
    price = 200
    min_nights = 3

    if request.method == 'POST':
        # 获取用户提交的数据，并进行类型转换
        try:
            price = int(request.POST.get('price', price))  # 默认值为当前的 price
            min_nights = int(request.POST.get('min_nights', min_nights))  # 默认值为当前的 min_nights
        except ValueError:
            pass  # 如果转换失败，继续使用默认值

    # 查询 HBase 数据
    df = pd.DataFrame([{
        'id': row[0],
        'longitude': float(row[1][b'info:longitude']),
        'latitude': float(row[1][b'info:latitude']),
        'price': float(row[1][b'info:price']),
        'minimum_nights': int(row[1][b'info:minimum_nights'])
    } for row in query_hbase(price=price, min_nights=min_nights)])

    if df.empty:
        return render(request, 'mapapp/no_results.html')  # 如果没有结果，返回一个无结果页面

    # 执行坐标转换
    converted_coords = df.apply(lambda row: bdToGaoDe(row['longitude'], row['latitude']), axis=1)
    converted_df = pd.DataFrame(converted_coords.tolist(), columns=['converted_longitude', 'converted_latitude'])
    df = pd.concat([df, converted_df], axis=1)
    print(df[['longitude', 'latitude', 'converted_longitude', 'converted_latitude']])

    # 创建 folium 地图
    m = folium.Map(
        location=[39.903740, 116.393590],  # 地图的初始中心位置
        tiles='https://wprd01.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=7',
        attr='高德-常规图',
        zoom_start=15
    )

    for _, row in df.iterrows():
        folium.Marker(
            location=[row['converted_latitude'], row['converted_longitude']],
            popup=f"ID: {row['id']}, Price: {row['price']}, Min Nights: {row['minimum_nights']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    # 保存地图文件到静态目录
    map_file_path = os.path.join(settings.BASE_DIR, 'static', 'map_with_markers.html')
    m.save(map_file_path)

    # 渲染页面，并传递生成的地图路径和当前参数
    return render(request, 'mapapp/map_view.html', {'map_html': '/static/map_with_markers.html', 'price': price, 'min_nights': min_nights})
