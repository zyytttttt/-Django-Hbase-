# coding:utf-8
import pandas as pd
import folium
import math
import happybase
# 创建 HBase 客户端连接

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
# 查询 price 和 minimum_nights
def query_hbase(price=None, min_nights=None):
    connection = happybase.Connection('192.168.88.132')
    connection.open()
    filters = []

    if price is not None:
        price_filter = "SingleColumnValueFilter('info', 'price', =, 'binary:{0}')".format(str(price))
        filters.append(price_filter)

    if min_nights is not None:
        min_nights_filter = "SingleColumnValueFilter('info', 'minimum_nights', =, 'binary:{0}')".format(str(min_nights))
        filters.append(min_nights_filter)

    # 拼接过滤条件字符串
    filter_str = " AND ".join(filters) if filters else None

    table = connection.table('locat')
    rows = table.scan(filter=filter_str)

    result = []
    for row in rows:
        result.append(row)

    return result
price=int(input("输入你的预期价格："))
min_nights=int(input("min_nights:"))
# 进行查询
df = pd.DataFrame([{
    'id': row[0],  # row[0] 是行键
    'longitude': float(row[1][b'info:longitude']),
    'latitude': float(row[1][b'info:latitude']),
    'price': float(row[1][b'info:price']),
    'minimum_nights': int(row[1][b'info:minimum_nights'])
} for row in query_hbase(price, min_nights)])
print(df)
if df.empty:
    print("No results found for the given price and minimum nights. Exiting the program.")
    exit()  # 停止程序执行
# 执行坐标转换
converted_coords = df.apply(lambda row: bdToGaoDe(row['longitude'], row['latitude']), axis=1)

# 创建一个新的 DataFrame 包含转换后的坐标
converted_df = pd.DataFrame(converted_coords.tolist(), columns=['converted_longitude', 'converted_latitude'])

# 将原始 DataFrame 和转换后的 DataFrame 合并
df = pd.concat([df, converted_df], axis=1)

# 打印包含转换后坐标的 DataFrame
print(df[['longitude', 'latitude', 'converted_longitude', 'converted_latitude']])

# 创建一个 folium 地图
m = folium.Map(
    location=[39.903740, 116.393590],  # 地图的初始中心位置
    tiles='https://wprd01.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=7',
    attr='高德-常规图',
    zoom_start=15
)

# 添加标记
for _, row in df.iterrows():
    folium.Marker(
        location=[row['converted_latitude'], row['converted_longitude']],
        popup=f"ID: {row['id']}, Price: {row['price']}, Min Nights: {row['minimum_nights']}",
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

# 显示地图
m.save("map_with_markers.html")  # 将地图保存为 HTML 文件
