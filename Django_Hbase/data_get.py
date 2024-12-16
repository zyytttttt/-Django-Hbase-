# coding:utf-8
import mysql.connector  #导入mysql的包
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Map, Bar, Pie
import folium
from folium.plugins import FloatImage
import requests
import math
from pyecharts.charts import Line
from pyecharts.charts import Grid
from folium.plugins import HeatMap, FloatImage

# 8317d21e419d292fe5f6797b653366b9
# 8317d21e419d292fe5f6797b653366b9

conn = mysql.connector.connect(host='192.168.88.132', port=3306, user='root', password='123456', database='mydblab')
# 连接数据库
cursor = conn.cursor(buffered=True)  # 开启缓存区
cursor.execute('SELECT * from rent_house ')
rows = cursor.fetchall()
data = pd.DataFrame(rows, columns=cursor.column_names)
conn.commit()  # 提交事务
cursor.close()  # 关闭缓存区
conn.close()  # 关闭连接’

     # 确保 visit_date 列是字符串类
def gd_map(addr):
    para = {'key':'8317d21e419d292fe5f6797b653366b9', 'address': addr}  # key填入自己在高德开放平台上申请的key
    # url = 'https://restapi.amap.com/v3/geocode/geo?parameters'  # 高德地图地理编码API服务地址
    url = f'https://restapi.amap.com/v3/geocode/geo?key={para["key"]}&address={para["address"]}'

    result = requests.get(url)  # GET方式请求
    result = result.json()
    print(result)

    lon_lat = result['geocodes'][0]['location']  # 获取经纬度
    lon_lat = lon_lat.split(",")  # 把经纬度以","为界分割
    lon = float(lon_lat[0])  # 获取的经纬度格式为[经度,纬度]
    lat = float(lon_lat[1])
    print(addr, "的高德标准经纬度为: (", lon, ",", lat, ")")
    return lon, lat  # 返回经纬度(float)

def bdToGaoDe(lon,lat):
    """
    坐标转化
    :param lon:
    :param lat:
    :return:
    """
    PI = 3.14159265358979324 * 3000.0 / 180.0
    x = lon - 0.0065
    y = lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * PI)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * PI)
    lon = z * math.cos(theta)
    lat = z * math.sin(theta)
    return lon,lat
df = pd.read_csv('processed_listings.csv', encoding='gbk')


# 画地图%%%%%%%%%%%%%%%%%%%

# 去除区域名称中的拼音缩写
df['neighbourhood'] = df['neighbourhood'].str.split('/').str[0].str.strip()
# 统计区域出现的次数
neighborhood_counts = df['neighbourhood'].value_counts()
neighborhood_data = {
    "朝阳区": 7473,
    "延庆区": 2107,
    "海淀区": 1926,
    "密云区": 1893,
    "怀柔区": 1739,
    "丰台区": 1658,
    "通州区": 1390,
    "昌平区": 1292,
    "顺义区": 1197,
    "大兴区": 1020,
    "房山区": 927,
    "东城区": 464,
    "西城区": 385,
    "石景山区": 320,
    "门头沟区": 282,
    "平谷区": 245,
}
beijing_districts = list(neighborhood_data.keys())
values = list(neighborhood_data.values())

# 绘制地图
map_chart = Map(init_opts=opts.InitOpts(width="1200px", height="600px"))
map_chart.add("", [list(z) for z in zip(beijing_districts, values)], maptype="北京")
map_chart.set_global_opts(
    title_opts=opts.TitleOpts(title="北京市各区房屋租赁数量分布"),
    visualmap_opts=opts.VisualMapOpts(max_=max(values)),  # 根据实际数据设置最大值
)
map_chart.render("北京市各区房屋租赁数量区域分布.html")


data = [(key, value) for key, value in neighborhood_data.items()]
pie_chart = (
    Pie()
    .add("", data, radius=["30%", "60%"])
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    .set_global_opts(title_opts=opts.TitleOpts(title="北京租房饼图分布", pos_bottom="5%", pos_left="center"))
)
pie_chart.render("北京租房饼图分布.html")
# 画地图&&&&&&&&&&&&&&&&&&&&&&&

# lon, lat = gd_map(addr)  # 调用函数

converted_coords = df.apply(lambda row: bdToGaoDe(row['longitude'], row['latitude']), axis=1)

# Create a new DataFrame with converted coordinates
converted_df = pd.DataFrame(converted_coords.tolist(), columns=['converted_longitude', 'converted_latitude'])

# Concatenate the original DataFrame with the converted DataFrame
df = pd.concat([df, converted_df], axis=1)

# Print the DataFrame with converted coordinates
# print(df[['longitude', 'latitude', 'converted_longitude', 'converted_latitude']])

# 创建地图
m = folium.Map(
    location=[39.903740, 116.393590],  # 中心点经纬度（先纬后经）
    tiles='https://wprd01.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=1&style=7',  # 地图风格
    attr='高德-常规图',  # 地图名称
    zoom_start=15,  # 默认比例尺
    control_scale=True,  # 是否在地图上添加比例尺
    width='100%',  # 地图宽度
)

# 在地图上添加图片
FloatImage('颜色.png', left=88, bottom=8, width=8).add_to(m)
FloatImage('标题.png', left=30, bottom=88, width=40).add_to(m)

# 准备数据
top_ten = df[['converted_latitude', 'converted_longitude']]
heat_data = [[row['converted_latitude'], row['converted_longitude']] for _, row in top_ten.iterrows()]

# 绘制热力图
gradient = {"0.1": "blue",
    "0.2": "cyan",
    "0.4": "lime",
    "0.6": "yellow",
    "0.8": "red",
    "1.0": "maroon",}
HeatMap(heat_data, gradient=gradient, radius=6, blur=5).add_to(m)  # 将 radius 设置为更小的值

# 添加经纬度弹出框
m.add_child(folium.LatLngPopup())

# 保存地图
m.save('高德热力图分别.html')



# 画地图%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# 画折线图

bins = [0, 150, 300, 450, 600, 1000, float('inf')]
labels = ['0-150', '150-300', '300-450', '450-600', '600-1000', '100+']
df['price_group'] = pd.cut(df['price'], bins=bins, labels=labels)

# 统计每个分组内的数据数量
price_distribution = df['price_group'].value_counts().sort_index()

# 使用 ECharts 绘制直方图
bar = (
    Bar()
    .add_xaxis(price_distribution.index.tolist())
    .add_yaxis("价格分布", price_distribution.values.tolist())
    .set_global_opts(
        xaxis_opts=opts.AxisOpts(type_="category"),
        title_opts=opts.TitleOpts(title="价格分布直方图"),
    )
    .render("价格分布直方图.html")
)
minimum_nights_counts = df['minimum_nights'].value_counts().sort_index().reset_index()
minimum_nights_counts.columns = ['minimum_nights', 'count']

# 准备数据
x_data = minimum_nights_counts['minimum_nights'].tolist()
y_data = minimum_nights_counts['count'].tolist()

# 使用 ECharts 绘制折线图
line = (
    Line()
    .add_xaxis(xaxis_data=x_data)
    .add_yaxis(series_name="数量", y_axis=y_data, markpoint_opts=opts.MarkPointOpts(data=[opts.MarkPointItem(type_="max", name="最大值"), opts.MarkPointItem(type_="min", name="最小值")]))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="北京短租房最短周期分别"),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
        xaxis_opts=opts.AxisOpts(name="最短租期"),
        yaxis_opts=opts.AxisOpts(name="数量"),
    )
)

# 标记主要区域
main_area_start = 0  # 假设主要区域起始点为第 5 个数据点
main_area_end = 4   # 假设主要区域结束点为第 10 个数据点
main_area = [(x_data[main_area_start], y_data[main_area_start]), (x_data[main_area_end], y_data[main_area_end])]
line.set_series_opts(
    markarea_opts=opts.MarkAreaOpts(
        data=[
            opts.MarkAreaItem(x=(main_area[0][0], main_area[1][0])),
        ],
        label_opts=opts.LabelOpts(position="inside", color="red")
    )
)

line.render("北京短租房最短周期分别.html")


availability_counts = df['availability_365'].value_counts().sort_index().reset_index()
availability_counts.columns = ['availability', 'count']

# 准备数据
x_data = availability_counts['availability'].tolist()
y_data = availability_counts['count'].tolist()

# 使用 ECharts 绘制柱状图
bar = (
    Bar()
    .add_xaxis(xaxis_data=x_data)
    .add_yaxis(series_name="数量", y_axis=y_data, label_opts=opts.LabelOpts(is_show=False))
    .set_global_opts(title_opts=opts.TitleOpts(title="可租时间分布"))
)
bar.render("可租时间分布.html")


# 统计 room_type 的值及其数量
room_type_counts = df['room_type'].value_counts().reset_index()
room_type_counts.columns = ['room_type', 'count']

# 准备数据
data_pairs = list(zip(room_type_counts['room_type'].tolist(), room_type_counts['count'].tolist()))

# 使用 ECharts 绘制饼图
pie = (
    Pie()
    .add("", data_pairs)
    .set_global_opts(title_opts=opts.TitleOpts(title="房屋类型分布"))
    .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c} ({d}%)"))
)
pie.render("房屋类型分布.html")

# 使用 groupby 函数按区域分组，并计算房价的最大值
# 过滤数据，保留价格在 (0, 100000) 范围内的数据
filtered_df = df[(df['price'] > 500) & (df['price'] < 100000)]

# 计算各区域的房价平均值
average_price_by_neighbourhood = filtered_df.groupby('neighbourhood')['price'].mean()
max_price_by_neighbourhood = filtered_df.groupby('neighbourhood')['price'].max()
min_price_by_neighbourhood = filtered_df.groupby('neighbourhood')['price'].min()
# # 输出结果
# print(average_price_by_neighbourhood)
# print(max_price_by_neighbourhood)
# print(min_price_by_neighbourhood)

neighbourhoods = average_price_by_neighbourhood.index.tolist()
average_prices = average_price_by_neighbourhood.tolist()
max_prices = max_price_by_neighbourhood.tolist()
min_prices = min_price_by_neighbourhood.tolist()

# # 使用 ECharts 绘制柱状图和折线图
# neighbourhoods = average_price_by_neighbourhood.index.tolist()
# average_prices = average_price_by_neighbourhood.tolist()
# max_prices = max_price_by_neighbourhood.tolist()
# min_prices = min_price_by_neighbourhood.tolist()

# 使用 ECharts 绘制柱状图和折线图
bar = (
    Bar()
    .add_xaxis(xaxis_data=neighbourhoods)
    .add_yaxis(series_name="平均价格", y_axis=average_prices, label_opts=opts.LabelOpts(is_show=False))
    .add_yaxis(series_name="最小价格", y_axis=min_prices)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="北京市各区域租房价格分布"),
        xaxis_opts=opts.AxisOpts(name="区域"),
        yaxis_opts=opts.AxisOpts(name="价格"),
    )
)

line = (
    Line()
    .add_xaxis(xaxis_data=neighbourhoods)
    .add_yaxis(series_name="最大价格", y_axis=max_prices)
)

# 将柱状图和折线图合并在一起
grid = (
    Grid(init_opts=opts.InitOpts(width="1200px", height="600px"))
    .add(bar, grid_opts=opts.GridOpts(pos_bottom="60%"))
    .add(line, grid_opts=opts.GridOpts(pos_top="60%"))
)

grid.render("北京市各区域租房价格分布.html")