# 基于Django-Hbase 的北京房屋信息系统

本课题基于大数据技术，构建了一个利用 HBase 存储与管理租赁房屋相关信息的数据系统。通过高效的数据插入、查询和分析功能，该系统能够满足用户对大量异构数据的存储需求，实现对租赁房源数据的管理。
字段信息：
![image](https://github.com/user-attachments/assets/d3b26651-a622-4f32-a862-a8dd6b59902b)
Hbase的表结构（必要）：
![image](https://github.com/user-attachments/assets/d451b997-54df-4b69-8bf4-c5dacb698e6c)
hive表结构（非必要）：
![image](https://github.com/user-attachments/assets/355ffcc7-fb9f-4142-b926-18554a571102)
数据的输入：
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
    next(reader)  # 跳过 CSV 文件的头行
    for row in reader:
        # 跳过空行
        if len(row) == 0:
            continue
        # 确保行数据足够
        if len(row) < 9:  # 根据列的数量来检查
            print(row)
            continue
        row_key = str(row[0])  # 确保 row_key 是字符串类型
        # 创建一个插入数据的 Mutation（可以插入多列）
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
        # 单条插入数据
        client.mutateRow('locat', row_key, mutations)

# 关闭连接
transport.close()
