# 基于Django-Hbase 的北京房屋信息系统

# 本课题基于大数据技术，构建了一个利用 HBase 存储与管理租赁房屋相关信息的数据系统。通过高效的数据插入、查询和分析功能，该系统能够满足用户对大量异构数据的存储需求，实现对租赁房源数据的管理。


# 字段信息：
![image](https://github.com/user-attachments/assets/d3b26651-a622-4f32-a862-a8dd6b59902b)
# Hbase的表结构（必要）：

![image](https://github.com/user-attachments/assets/d451b997-54df-4b69-8bf4-c5dacb698e6c)
# hive表结构（非必要）：
![image](https://github.com/user-attachments/assets/355ffcc7-fb9f-4142-b926-18554a571102)
	
# 数据的输入：
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from hbase import Hbase
import csv

# 连接到 Thrift 服务
transport = TSocket.TSocket('localhost', 9090)  # 替换为 HBase Thrift 服务的地址和端口
transport = TTransport.TBufferedTransport(transport)
protocol = TBinaryProtocol.TBinaryProtocol(transport)

# 创建客户端
client = Hbase.Client(protocol)
# 打开连接
transport.open()
# 打开 CSV 文件并读取数据
with open('list.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:

        if len(row) == 0:
            continue

        if len(row) < 9: 
            print(row)
            continue
        row_key = str(row[0]) 
        mutations = [
            Hbase.Mutation(isDelete=False, column='info:host_id', value=str(row[1])),
            Hbase.Mutation(isDelete=False, column='info:latitude', value=str(row[2])),
            Hbase.Mutation(isDelete=False, column='info:longitude', value=str(row[3])),
            Hbase.Mutation(isDelete=False, column='info:price', value=str(row[4])),
            Hbase.Mutation(isDelete=False, column='info:minimum_nights', value=str(row[5])),
            Hbase.Mutation(isDelete=False, column='info:number_of_reviews', value=str(row[6])),
            Hbase.Mutation(isDelete=False, column='info:calculated_host_listings_count', value=str(row[7])),
            Hbase.Mutation(isDelete=False, column='info:availability_365', value=str(row[8])),
        ]
        client.mutateRow('locat', row_key, mutations)

transport.close()

# （1）北京租房信息地图实时查询

1）功能简介

可以对hbase数据库进行高速的实时查询 并在地图上进行显示 获得具体的位置已经房源的信息

2）实现

输入想要的价格和 最短租期即可在地图上展示位置点击可以查看具体信息情况
![173433993587659da0458-ffc1-4bbe-9a3d-1ea8058cd666_img_](https://github.com/user-attachments/assets/4c7807fe-4c5c-43f8-9dc9-b14dfa453d4f)


# （2）北京租房信息实时展示

1）功能简介

对北京租赁信息分析之后展示各种数据价格分布直方图；北京市各区域租房价格分布；北京市各区房屋租赁数量区域分布；北京短租房最短周期分别；北京租房饼图分布；可租时间分布；房屋类型分布

2）实现

主页
![1734339696908c16a1638-2a7f-47c8-bd82-df436b1f1ca1_img_](https://github.com/user-attachments/assets/98fdddea-a174-4ef3-9938-1e8339c9ae6e)
![173433974318223e0951f-6cac-4288-a7cb-e56aeefa1372_img_](https://github.com/user-attachments/assets/dd128703-a854-4484-abab-1ec07e44f143)


