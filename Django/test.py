# 导入库
from shapely.geometry import Point, Polygon, shape
import mapclassify
import matplotlib as mpl
import matplotlib.pyplot as plt
import geopandas as gpd
import time  # 导入time库，时间戳
import numpy as np
import pandas as pd
import warnings  # 运行这个代码可以让Python不显示warnings
warnings.filterwarnings("ignore")

# 导入数据
df = pd.read_csv('./TaxiData.tar.gz', header=None)
#给数据命名列, '车号','时间','经度','纬度','空车（1为载客，0为空车）','速度'
df.columns = ['VehicleNum', 'Stime', 'Lng', 'Lat', 'OpenStatus', 'Speed']
df.head(10)  # 查看前10条数据
# 查看数据信息，共计4千多万条数据，占用内存2.1GB
df.info()
# 删除异常轨迹
df = df.sort_values(by=['VehicleNum', 'Stime'])  # 根据车牌号和时间进行排序
# 排序之后一段OD轨迹应为都是0或都是1，但数据中有可能出现前后都是0，突然有一条数据变成1，
# 或者前后都是1，突然变成0。这种异常情况我们是要排除的
df = df[-((df['OpenStatus'].shift() == df['OpenStatus'].shift(-1)) &
          (df['OpenStatus'].shift(-1) != df['OpenStatus']) &
          (df['VehicleNum'].shift(-1) == df['VehicleNum']) &
          (df['VehicleNum'].shift() == df['VehicleNum']))]
# 删去不属于深圳市范围的数据
# 深圳市的大致经纬度范围
lon1 = 113.75194
lon2 = 114.624187
lat1 = 22.447837
lat2 = 22.864748
df_sz = df[(df['Lng'] >= lon1) &
           (df['Lng'] <= lon2) &
           (df['Lat'] >= lat1) &
           (df['Lat'] <= lat2)]
df_sz.head()  # 查看前五条数据
#数据删除了约19万条
df_sz.info()

#创建一列OpenStatus1，它的值是OpenStatus整体往上移一行
df_sz['OpenStatus1'] = df_sz['OpenStatus'].shift(-1)
#创建一列StatusChange，它的值是OpenStatus1减去OpenStatus，表示载客状态的变化
df_sz['StatusChange'] = df_sz['OpenStatus1']-df_sz['OpenStatus']
#提取其中的OD信息
oddata = df_sz[(df_sz['StatusChange']==1)|(df_sz['StatusChange']==-1)&\
(df_sz['VehicleNum'] == df_sz['VehicleNum'].shift(-1))]
oddata = oddata[['VehicleNum', 'Stime', 'Lng', 'Lat', 'StatusChange']]
oddata.columns = ['VehicleNum', 'Stime', 'SLng', 'SLat', 'StatusChange']
oddata['Etime'] = oddata['Stime'].shift(-1)
oddata['ELng'] = oddata['SLng'].shift(-1)
oddata['ELat'] = oddata['SLat'].shift(-1)
oddata = oddata[(oddata['VehicleNum'] == oddata['VehicleNum'].shift(-1))&\
(oddata['StatusChange'] == 1)]
oddata = oddata.drop('StatusChange',axis = 1)
oddata.head()
##Stime 为起点的时间，Etime为终点的时间，也就是乘客下车的时间
##SLng SLat为起点的经纬度，ELng Elat为终点的经纬度
#提取出45万条OD
len(oddata)
#读取深圳底图
sz = gpd.GeoDataFrame.from_file('./sz.json', encoding='utf-8')
sz.plot()

#栅格化代码
import math
#定义一个测试栅格划的经纬度
testlon = 114
testlat = 22.5

#划定栅格划分范围
lon1 = 113.75194
lon2 = 114.624187
lat1 = 22.447837
lat2 = 22.864748

latStart = min(lat1, lat2);
lonStart = min(lon1, lon2);

#定义栅格大小(单位m)
accuracy = 500;

#计算栅格的经纬度增加量大小Lon和Lat
deltaLon = accuracy * 360 / (2 * math.pi * 6371004 * math.cos((lat1 + lat2) * math.pi / 360));
deltaLat = accuracy * 360 / (2 * math.pi * 6371004);

#计算栅格的经纬度编号
LONCOL=divmod(float(testlon) - (lonStart - deltaLon / 2) , deltaLon)[0]
LATCOL=divmod(float(testlat) - (latStart - deltaLat / 2) , deltaLat)[0]

#计算栅格的中心点经纬度
#HBLON = LONCOL*deltaLon + (lonStart - deltaLon / 2)#格子编号*格子宽+起始横坐标-半个格子宽=格子中心横坐标
#HBLAT = LATCOL*deltaLat + (latStart - deltaLat / 2)
#以下为更正，不需要减去半个格子宽
HBLON = LONCOL*deltaLon + lonStart #格子编号*格子宽+起始横坐标=格子中心横坐标
HBLAT = LATCOL*deltaLat + latStart 

#定义空的geopandas表
data = gpd.GeoDataFrame()

#定义空的list，后面循环一次就往里面加东西
LONCOL = []
LATCOL = []
geometry = []
HBLON1 = []
HBLAT1 = []

#计算总共要生成多少个栅格
#lon方向是lonsnum个栅格
lonsnum = int((lon2-lon1)/deltaLon)+1
#lat方向是latsnum个栅格
latsnum = int((lat2-lat1)/deltaLat)+1

for i in range(lonsnum):
    for j in range(latsnum):

        HBLON = i*deltaLon + lonStart 
        HBLAT = j*deltaLat + latStart
        #把生成的数据都加入到前面定义的空list里面
        LONCOL.append(i)
        LATCOL.append(j)
        HBLON1.append(HBLON)
        HBLAT1.append(HBLAT)
        
        #生成栅格的Polygon形状
        HBLON_1 = (i+1)*deltaLon + lonStart
        HBLAT_1 = (j+1)*deltaLat + latStart 
        geometry.append(Polygon([
        (HBLON-deltaLon/2,HBLAT-deltaLat/2),
        (HBLON_1-deltaLon/2,HBLAT-deltaLat/2),
        (HBLON_1-deltaLon/2,HBLAT_1-deltaLat/2),
        (HBLON-deltaLon/2,HBLAT_1-deltaLat/2)]))
        
#为geopandas文件的每一列赋值为刚刚的list
data['LONCOL'] = LONCOL
data['LATCOL'] = LATCOL
data['HBLON'] = HBLON1
data['HBLAT'] = HBLAT1
data['geometry'] = geometry

#筛选出深圳范围的栅格
grid_sz = data[data.intersects(sz.unary_union)]
grid_sz.plot();

#将OD数据并入栅格中

#计算od起终点所属的栅格编号
oddata = oddata[-oddata['Etime'].isnull()]
oddata['SLONCOL'] = ((oddata['SLng']-(lonStart - deltaLon / 2))/deltaLon).astype('int')
oddata['SLATCOL'] = ((oddata['SLat']-(latStart - deltaLat / 2))/deltaLat).astype('int')
oddata['ELONCOL'] = ((oddata['ELng']-(lonStart - deltaLon / 2))/deltaLon).astype('int')
oddata['ELATCOL'] = ((oddata['ELat']-(latStart - deltaLat / 2))/deltaLat).astype('int')
#集计
oddata = oddata.groupby(['SLONCOL','SLATCOL','ELONCOL','ELATCOL'])['VehicleNum'].count().rename('count').reset_index()

#筛选范围内的栅格
oddata = oddata[(oddata['SLONCOL']>=0) & (oddata['SLONCOL']<=lonsnum)&\
(oddata['SLATCOL']>=0) & (oddata['SLATCOL']<=latsnum)&\
(oddata['ELONCOL']>=0) & (oddata['ELONCOL']<=lonsnum)&\
(oddata['ELATCOL']>=0) & (oddata['ELATCOL']<=latsnum)]
#计算栅格的中心点经纬度
oddata['SHBLON'] = oddata['SLONCOL']*deltaLon + lonStart#格子编号*格子宽+起始横坐标=格子中心横坐标
oddata['SHBLAT'] = oddata['SLATCOL']*deltaLat + latStart
oddata['EHBLON'] = oddata['ELONCOL']*deltaLon + lonStart#格子编号*格子宽+起始横坐标=格子中心横坐标
oddata['EHBLAT'] = oddata['ELATCOL']*deltaLat + latStart

#将oddata转换为geodataframe，并生成geometry
oddata = gpd.GeoDataFrame(oddata)
from shapely.geometry import LineString
r = oddata.iloc[0]
oddata['geometry']=oddata.apply(lambda r:LineString([[r['SHBLON'],r['SHBLAT']],[r['EHBLON'],r['EHBLAT']]]),axis = 1)
oddata.plot();

##绘制OD分布图
#创建图框
fig = plt.figure(1,(16,8),dpi = 300)
ax = plt.subplot(111)
plt.sca(ax);

#绘制栅格
grid_sz.plot(ax = ax,edgecolor = (0,0,0,0.8),facecolor = (0,0,0,0),linewidths=0.02);

#绘制深圳的边界
sz_all = gpd.GeoDataFrame()
sz_all['geometry'] = [sz.unary_union]
sz_all.plot(ax = ax,edgecolor = (0,0,0,1),facecolor = (0,0,0,0),linewidths=0.5);
#设置字体 防止乱码
ft = mpl.font_manager.FontProperties(fname='./NotoSansCJK.ttc', size=11)
plt.rcParams['font.sans-serif']=['SimHei']
plt.rcParams['axes.unicode_minus'] = False
plt.title('深圳市出租车OD分布', fontsize=18, verticalalignment='center', horizontalalignment= 'center',fontproperties=ft)
#设置colormap的数据
vmax = oddata['count'].max()
cmapname = 'cool'
cmap = mpl.cm.get_cmap(cmapname);

#绘制OD
oddata.plot(ax = ax,column = 'count',linewidth = 15*(oddata['count']/oddata['count'].max()),cmap = cmap,vmin =0,vmax = vmax,alpha=0.4)

plt.axis('off');
#设定显示范围
ax.set_xlim(113.6,114.8)
ax.set_ylim(22.4,22.9)

#绘制colorbar
plt.imshow([[0,vmax]], cmap=cmap)
cax = plt.axes([0.08, 0.4, 0.02, 0.3])
plt.colorbar(cax=cax)

#保存图片
##plt.savefig(r'深圳市出租车OD分布.jpg',dpi=300)
#显示图
plt.show();

##绘制OD的栅格分布

#以OD起点集计oddata
odcount = oddata.groupby(['SLONCOL','SLATCOL'])['count'].sum().reset_index()
#重命名列以便后面的表连接
odcount.columns = ['LONCOL','LATCOL','count']
#表连接
odcount_grid = pd.merge(grid_sz,odcount,on = ['LONCOL','LATCOL'])

#绘制O点分布图
# import matplotlib
# import matplotlib.pyplot as plt
fig = plt.figure(1,(16,8),dpi = 300)
ax = plt.subplot(111)
plt.sca(ax)

#设置colormap的数据
# import matplotlib
vmax = odcount_grid['count'].max()
cmapname = 'RdYlBu_r'
cmap = mpl.cm.get_cmap(cmapname)

#绘制栅格
odcount_grid.plot(ax = ax,column = 'count',scheme='quantiles',legend=False,cmap='RdYlBu_r',k=9, edgecolor='none',linewidth=0.3,
       legend_kwds={'loc':4,})

#绘制深圳边界
sz_all = gpd.GeoDataFrame()
sz_all['geometry'] = [sz.unary_union]
sz_all.plot(ax = ax,edgecolor = (0,0,0,1),facecolor = (0,0,0,0),linewidths=0.5)
#绘制标题
plt.axis('off')
plt.title('深圳市出租车打车点(O点)分布', fontsize=18, verticalalignment='center', horizontalalignment= 'center',fontproperties=ft )
ax.set_xlim(113.6,114.8)
ax.set_ylim(22.4,22.9)
#绘制colorbar
plt.imshow([[0,vmax]], cmap=cmap)
cax = plt.axes([0.08, 0.4, 0.02, 0.3])
plt.colorbar(cax=cax)
##保存图片
#plt.savefig(r'深圳市出租车打车点分布.jpg',dpi=300)
plt.show()

##绘制OD的栅格分布

#以OD起点集计oddata
odcount2 = oddata.groupby(['ELONCOL','ELATCOL'])['count'].sum().reset_index()
#重命名列以便后面的表连接
odcount.columns = ['LONCOL','LATCOL','count']
#表连接
odcount_grid = pd.merge(grid_sz,odcount,on = ['LONCOL','LATCOL'])
#绘制D点分布图
# import matplotlib
# import matplotlib.pyplot as plt
fig = plt.figure(1,(16,8),dpi = 300)
ax = plt.subplot(111)
plt.sca(ax)

#设置colormap的数据
# import matplotlib
vmax = odcount_grid['count'].max()
cmapname = 'RdYlBu_r'
cmap = mpl.cm.get_cmap(cmapname)

#绘制栅格
odcount_grid.plot(ax = ax,column = 'count',scheme='quantiles',legend=False,cmap='RdYlBu_r',k=9, edgecolor='none',linewidth=0.3,
       legend_kwds={'loc':4,})

#绘制深圳边界
sz_all = gpd.GeoDataFrame()
sz_all['geometry'] = [sz.unary_union]
sz_all.plot(ax = ax,edgecolor = (0,0,0,1),facecolor = (0,0,0,0),linewidths=0.5)
#绘制标题
plt.axis('off')
plt.title('深圳市出租车下车点(D点)分布', fontsize=18, verticalalignment='center', horizontalalignment= 'center',fontproperties=ft )
ax.set_xlim(113.6,114.8)
ax.set_ylim(22.4,22.9)
#绘制colorbar
plt.imshow([[0,vmax]], cmap=cmap)
cax = plt.axes([0.08, 0.4, 0.02, 0.3])
plt.colorbar(cax=cax)
plt.show()

#提取福田区部分地区作为样本，减小数据量
lon1 = 113.98064
lon2 = 114.150815
lat1 = 22.542155
lat2 = 22.580603
df_ft = df[(df['Lng']>=lon1)&\
(df['Lng']<=lon2)&\
(df['Lat']>=lat1)&\
(df['Lat']<=lat2)]
data = df_ft
data

#抽取了大约22%的数据
len(data)

#把数据的每一列上移一行赋值给新的列。新的列名为原列名后面加‘1’
for c in data.columns:
    data[c+'1'] = data[c].shift(-1)
    print(c)

#生成轨迹ID
#删掉车辆id不同的行
data = data[(data['VehicleNum'].astype('int')==data['VehicleNum1'].fillna(0).astype('int'))]
#生成状态变化的列
data['StatusChange'] = data['OpenStatus1']-data['OpenStatus']
#为订单进行编号
data['neworder'] = (data['StatusChange'] == 1).astype('int')
data['orderid'] = data.groupby(['VehicleNum'])['neworder'].cumsum()
#整理数据的列名
data.columns=['VehicleNum', 'Stime', 'SLng', 'SLat', 'OpenStatus', 'Speed',
       'VehicleNum1', 'Etime', 'ELng', 'ELat', 'OpenStatus1', 'Speed1',
       'StatusChange', 'neworder', 'orderid']
data = data.drop(['Stime', 'SLng', 'SLat','Speed','OpenStatus','VehicleNum1','StatusChange', 'neworder' , 'OpenStatus1','Speed1'],axis = 1)
data.columns= ['driver_id', 'timestamp1', 'lon', 'lat','order_id']
df_ft =data

len(df_ft)

df_ft.head()

#将时间转为时间戳形式（运行时间较长，可直接在K-Means聚类部分读取处理好的数据）
#转为时间戳
df_ft['timestamp1'] = df_ft['timestamp1'].astype('datetime64')
from datetime import datetime
# review_date 转为时间戳形式
def time2stamp(cmnttime):   #转时间戳函数
    cmnttime=datetime.strptime(cmnttime,'%Y-%m-%d %H:%M:%S')
    stamp=int(datetime.timestamp(cmnttime))
    return stamp
df_ft['timestamp']=df_ft['timestamp1'].apply(lambda x: time2stamp(str(x)))
df_ft = df_ft.drop(['timestamp1'],axis = 1)

#将wgs84坐标系转换成投影坐标系
import pyproj
import pandas as pd
import numpy as np
p1 = pyproj.Proj(init="epsg:4326")#wgs坐标系统的EPSG Code
p2 = pyproj.Proj(init="epsg:3857")#球体墨卡托——转换投影坐标系统的EPSG Code
df_ft['x'],df_ft['y'] = pyproj.transform(p1, p2,df_ft['lon'], df_ft['lat'])
df_ft['x'] = round(df_ft['x'],2)#整列小数点保留2位
df_ft['y'] = round(df_ft['y'],2)#整列小数点保留2位
##保存数据
##df.to_csv(r'Datatime.csv')

df_ft.fillna(0)  # 填补缺失值

#时间窗划分
stamp1 = 1642737032
stamp1 = int(stamp1)  
time_interval=1200 #时间窗长度  
df_ft['time_id'] = df_ft['timestamp'].apply(lambda x: (x - stamp1)//time_interval) #生成时间窗索引  
#空间网格划分    
left = df_ft['x'].min() #计算左边界    
up = df_ft['y'].max() #计算上边界    
interval=70 #网格单元大小

df_ft['rowid'] = df_ft['y'].apply(lambda x: (up - x) // interval).astype('int') #计算横向索引    
df_ft['colid'] = df_ft['x'].apply(lambda x: (x - left) // interval).astype('int')#计算纵向索引 

df_ft = df_ft.sort_values(by=['driver_id', 'order_id', 'timestamp']).reset_index(drop=True)  
# 将订单id，下移一行，用于判断相邻记录是否属于同一订单  
df_ft['orderFlag'] = df_ft['order_id'].shift(1)  
df_ft['identi'] = (df_ft['orderFlag']==df_ft['order_id'])  
# 将坐标、时间戳下移一行，从而匹配相邻轨迹点  
df_ft['x1'] = df_ft['x'].shift(1)  
df_ft['y1'] = df_ft['y'].shift(1)  
df_ft['timestamp1'] = df_ft['timestamp'].shift(1)
df_ft = df_ft[df_ft['identi']==True]   #将不属于同一订单的轨迹点对删去  
dist = np.sqrt(np.square((df_ft['x'].values-df_ft['x1'].values)) + np.square((df_ft['y'].values-df_ft['y1'].values)))    # 计算相邻轨迹点之间的距离    
time = df_ft['timestamp'].values - df_ft['timestamp1'].values   # 计算相邻轨迹点相差时间  
df_ft['speed'] = dist / time    # 计算速度    
df_ft = df_ft.drop(columns=['x1', 'y1', 'orderFlag', 'timestamp1', 'identi'])   # 删去无用列 

df_ft['speed1'] = df_ft.speed.shift(1)                 # 将速度下移一行
df_ft['timestamp1'] = df_ft.timestamp.shift(1)         # 将时间下移一行
df_ft['identi'] = df_ft.order_id.shift(1)              # 将订单号下移一行
df_ft = df_ft[df_ft.order_id==df_ft.identi]                  # 去除两个订单分界点数据
df_ft.loc[:, 'acc'] = (df_ft.speed1.values - df_ft.speed.values) / (df_ft.timestamp1.values - df_ft.timestamp.values)  #计算加速度
df_ft = df_ft.drop(columns=['speed1', 'timestamp1', 'identi'])  #删除临时字段

orderGrouped = df_ft.groupby(['rowid', 'colid','time_id', 'order_id'])  # 基于时空网格与轨迹id进行分组   
# 网格平均车速  
grouped_speed = orderGrouped.speed.mean().reset_index() # 重索引
grouped_speed = grouped_speed.groupby(['rowid', 'colid', 'time_id'])  
grid_speed = grouped_speed.speed.mean()  
grid_speed = grid_speed.clip(grid_speed.quantile(0.05), grid_speed.quantile(0.95))#去除异常值  
grid_speed.head()

# 网格平均加速度
gridGrouped = df_ft.groupby(['rowid', 'colid','time_id'])
grid_acc = gridGrouped.acc.mean()  
grid_acc.head() 

# 网格流量  
grouped_volume = orderGrouped.speed.last().reset_index()  
grouped_volume = grouped_volume.groupby(['rowid', 'colid', 'time_id'])  
grid_volume = grouped_volume['speed'].size()  
grid_volume = grid_volume.clip(grid_volume.quantile(0.05), grid_volume.quantile(0.95))  
grid_volume.head() 

# 网格车速标准差  
grid_v_std = gridGrouped.speed.std()  
grid_v_std.head()  

# 网格平均停车次数  
stopNum = gridGrouped.speed.agg(lambda x: (x==0).sum())  
grid_stop = pd.concat((stopNum, grid_volume), axis=1)  
grid_stop['stopNum'] = stopNum.values / grid_volume.values  
grid_stop = grid_stop['stopNum']  
grid_stop = grid_stop.clip(0,grid_stop.quantile(0.95))  
grid_stop.head() 

# 合并网格数据
grib_data = pd.concat([grid_speed, grid_acc, grid_volume, grid_v_std, grid_stop], axis=1).reset_index()  
grib_data.columns = ['rowid', 'colid', 'time_id', 'aveSpeed', 'gridAcc', 'volume', 'speed_std', 'stopNum']  
grib_data.head()  

#导入库
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering  
from sklearn.mixture import GaussianMixture  
from sklearn.preprocessing import StandardScaler  

# 读取网格数据  
grib_data = pd.read_csv('./Datafina.csv') 
# 选择特征  
feature = ['stopNum', 'aveSpeed']  

# 数据标准化  
scaler = StandardScaler()  
scaler.fit(grib_data[feature])  
grib_data_nor = scaler.transform(grib_data[feature])  

# K均值聚类  
n = 3  
labels = KMeans(n_clusters=n, random_state=0).fit(grib_data_nor).labels_  

# 输出数据集  
grib_data_labelled = pd.concat((grib_data,   
                         pd.DataFrame(labels, columns = ['labels'])),   
                         axis=1)  

# 可视化聚类结果 
ft = mpl.font_manager.FontProperties(fname='./NotoSansCJK.ttc', size=14)
plt.rcParams['axes.unicode_minus'] = False    
plt.rcParams['font.sans-serif'] = 'SimHei'  
# 读取数据  
grib_df = grib_data_labelled
# 判断各簇实际意义  
grouped = grib_df.groupby(['labels']).mean()['aveSpeed']  
congested = int(grouped.idxmin(axis=0))  
clear = int(grouped.idxmax(axis=0))  
slow = [x for x in [0,1,2] if x not in [congested, clear]][0]  
# 绘图  
fig = plt.figure(figsize=(8,6))  
plt.scatter(grib_df[grib_df['labels']==slow]['aveSpeed'], grib_df[grib_df['labels']==slow]['stopNum'], label='缓行', color='darkorange')  
plt.scatter(grib_df[grib_df['labels']==clear]['aveSpeed'], grib_df[grib_df['labels']==clear]['stopNum'], label='畅通', color='darkgreen')  
plt.scatter(grib_df[grib_df['labels']==congested]['aveSpeed'], grib_df[grib_df['labels']==congested]['stopNum'], label='拥堵', color='firebrick')  
plt.xlim((-0.1,30))  
plt.tick_params(labelsize=18)  
plt.xlabel('速度',fontsize=20,fontproperties=ft)  
plt.ylabel('停车次数',fontsize=20,fontproperties=ft)  
plt.legend(fontsize=18, loc='upper right',prop=ft);

import pandas as pd
import numpy as np
from datetime import datetime
import warnings #运行这个代码可以让Python不显示warnings
warnings.filterwarnings("ignore")

df = pd.read_csv('./kmeans聚类结果.csv') ##读取之前处理好的数据
df.head()#查看数据

df['date'] = 20131022 #生成数据所在的日期
df['date'] = pd.to_datetime(df['date'],format='%Y%m%d')
df.fillna(0, inplace=True)

# 生成特征
def gerData(df, lag):
    
    jar = []
    for i in range(1, lag+1):
        print(i)
        tmp = df.copy()
        tmp['time_id'] = tmp.time_id.values + i # 每次循环生成t-i时间步的数据
        tmp = tmp.set_index(['rowid', 'colid', 'time_id', 'date'])
        jar.append(tmp)
    #将各时间步数据进行拼接
    jar.append(df[['rowid', 'colid', 'time_id', 'date', 'labels']].set_index(['rowid', 'colid', 'time_id', 'date'])) 
    
    return pd.concat(jar, axis=1).reset_index()

used = ['rowid', 'colid', 'time_id',  'aveSpeed', 'gridAcc', 'speed_std', 'labels','date']
dataRaw = df[used] # 筛选标签
data = gerData(dataRaw, 6) # 生成训练数据
data = data.dropna()  # 去除空值

from sklearn.model_selection import train_test_split
#data:需要进行分割的数据集
#random_state:设置随机种子，保证每次运行生成相同的随机数
#test_size:将数据分割成训练集的比例
train_set, test_set_validate = train_test_split(data, test_size=0.2, random_state=42)
test_set, valid_set = train_test_split(test_set_validate, test_size=0.5, random_state=42)

from sklearn.model_selection import train_test_split
line_sen_list =  data.values[:, 4:-1]
label_list = data.values[:, -1]
# 先将1.训练集，2.验证集+测试集，按照8：2进行随机划分
train_x, X_validate_test, train_y, y_validate_test = train_test_split(line_sen_list, label_list, test_size = 0.3, random_state = 42)
# 再将1.验证集，2.测试集，按照1：1进行随机划分
val_x, test_x, val_y, test_y = train_test_split(X_validate_test, y_validate_test, test_size = 0.5, random_state = 42)

# 将数据转为浮点型
train_x= train_x.astype('float64')
test_x=test_x.astype('float64')
train_y=train_y.astype('float64')
test_y=test_y.astype('float64')
val_x=val_x.astype('float64')
val_y=val_y.astype('float64')

#转为训练所用的输入X输出Y
train_x = train_set.values[:, 4:-1]  #输入  
val_x = valid_set.values[:, 4:-1]  
test_x = test_set.values[:, 4:-1]  
train_y = train_set.values[:, -1]  #输出  
test_y = test_set.values[:, -1]  
val_y = valid_set.values[:, -1] 
#转化为张量
#np.any(np.isnan(mat))

train_x= train_x.astype('float64')
test_x=test_x.astype('float64')
train_y=train_y.astype('float64')
test_y=test_y.astype('float64')
val_x=val_x.astype('float64')
val_y=val_y.astype('float64')

# 去除异常值
mins = [np.nanmin(train_x[:, i][train_x[:, i] != -np.inf]) for i in range(train_x.shape[1])]
maxs = [np.nanmax(train_x[:, i][train_x[:, i] != np.inf]) for i in range(train_x.shape[1])]

#一次遍历矩阵的一列，替换+和-无穷
#该列的最大值或最小值
for i in range(train_x.shape[1]):
    train_x[:, i][train_x[:, i] == -np.inf] = mins[i]
    train_x[:, i][train_x[:, i] == np.inf] = maxs[i]
##########################################################
mins = [np.nanmin(val_x[:, i][val_x[:, i] != -np.inf]) for i in range(val_x.shape[1])]
maxs = [np.nanmax(val_x[:, i][val_x[:, i] != np.inf]) for i in range(val_x.shape[1])]

#一次遍历矩阵的一列，替换+和-无穷大
#该列的最大值或最小值
for i in range(val_x.shape[1]):
    val_x[:, i][val_x[:, i] == -np.inf] = mins[i]
    val_x[:, i][val_x[:, i] == np.inf] = maxs[i]
    
##########################################################
mins = [np.nanmin(test_x[:, i][test_x[:, i] != -np.inf]) for i in range(test_x.shape[1])]
maxs = [np.nanmax(test_x[:, i][test_x[:, i] != np.inf]) for i in range(test_x.shape[1])]

#一次遍历矩阵的一列，替换+和-无穷大
#该列的最大值或最小值
for i in range(val_x.shape[1]):
    test_x[:, i][test_x[:, i] == -np.inf] = mins[i]
    test_x[:, i][test_x[:, i] == np.inf] = maxs[i]
        
# 将输入归一化为0和1之间
from sklearn import preprocessing  
scaler = preprocessing.MinMaxScaler()  
train_x = scaler.fit_transform(train_x)  
val_x = scaler.transform(val_x)  
test_x = scaler.transform(test_x)  

import tensorflow as tf  
from tensorflow.keras.layers import Dense  
model = tf.keras.Sequential()  
model.add(Dense(64,activation = 'relu',input_shape=(24,)))  #30为输入维度  
model.add(Dense(128,activation = 'relu'))  
model.add(Dense(128,activation = 'relu'))  
model.add(Dense(64,activation = 'relu'))      
model.add(Dense(3,activation = 'softmax'))
print(model.summary())  #用于观察模型结构和参数数量  

sgd = tf.keras.optimizers.SGD(learning_rate=0.005)  # 定义优化器
model.compile(loss = 'sparse_categorical_crossentropy',optimizer=sgd,metrics=['accuracy']) # 编译模型   

result = model.fit(train_x,train_y,epochs=30,validation_data = (val_x,val_y),batch_size=1024) # 训练模型
model.evaluate(test_x,test_y)  #评估模型

history = result.history

y_hat = model.predict(test_x)

import numpy as np

label_hat = np.argmax(y_hat, axis=1)

predResult = np.hstack((test_set[['rowid', 'colid']].values, label_hat.reshape(-1, 1), test_y.reshape(-1, 1)))

predResult = predResult.astype(int)

rows = predResult[:, 0].max() + 1
cols = predResult[:, 1].max() + 1
matPred = np.ones((rows, cols)) + 2
matTrue = np.ones((rows, cols)) + 2

for i in range(len(predResult)):
    row = predResult[i][0]
    col = predResult[i][1]
    matPred[row, col] = predResult[i][2]
    matTrue[row, col] = predResult[i][3]

matPred = matPred.astype(int)
matTrue = matTrue.astype(int)

###结果对比
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
ft = matplotlib.font_manager.FontProperties(fname='./NotoSansCJK.ttc', size=14)
plt.rcParams['axes.unicode_minus'] = False    
plt.rcParams['font.sans-serif'] = 'SimHei'  

sns.set(font_scale=2)
cmap = cmap = 'PuBu'
ticks = range(5)

##真实值
plt.figure(figsize=(20, 6))
sns.heatmap(matTrue, cmap=cmap, cbar_kws={"ticks":ticks}, xticklabels=False, yticklabels=False)
#ax2.set_title('真实值')
plt.title('真实值', fontsize=18,fontproperties=ft)
##预测值
plt.figure(figsize=(20, 6))
sns.heatmap(matPred, cmap=cmap,  cbar_kws={"ticks":ticks}, xticklabels=False, yticklabels=False)
plt.title('预测值', fontsize=18,fontproperties=ft)

########################################################
#可视化训练结果
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from pylab import mpl
sns.set(style='white')
mpl.rcParams['font.sans-serif'] = ['SimHei'] # 指定默认字体
train_loss = history['loss']
train_acc = history['accuracy']
val_loss = history['val_loss']
val_acc = history['val_accuracy']
#####################
plt.figure(figsize=(7, 5))
plt.plot(range(len(train_loss)), train_loss, linewidth=2.5)
plt.plot(range(len(val_loss)), val_loss, linewidth=2.5)
plt.legend(['训练集误差', '验证集误差'], fontsize=16,prop=ft)
plt.xlabel('迭代次数', fontsize=16,fontproperties=ft)
ax = plt.gca()
ax.xaxis.set_major_locator(MultipleLocator(5))
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(linestyle='--')
plt.show()
###########################
plt.figure(figsize=(7, 5))
plt.plot(range(len(train_acc)), train_acc, linewidth=2.5)
plt.plot(range(len(val_acc)), val_acc, linewidth=2.5)
plt.legend(['训练集准确率', '验证集准确率'], loc='upper right', fontsize=16,prop=ft)
plt.xlabel('迭代次数', fontsize=16,fontproperties=ft)

ax = plt.gca()
ax.xaxis.set_major_locator(MultipleLocator(5))
plt.xticks(fontsize=16)
plt.yticks(fontsize=16)
plt.grid(linestyle='--')
plt.show()

import pandas as pd  
# 读取数据文件 
data = pd.read_csv('./DATASET-C-B.csv')
# 转换数据类型
for c in ['rowid', 'colid', 'time_id']:  
    data[c] = data[c].astype(int)
# 排序
data = data.sort_values(['date', 'rowid', 'colid', 'time_id']).reset_index(drop=True)
data['date'] -= data['date'].min()
data #查看数据

print(len(data[['rowid', 'colid']].drop_duplicates()), # 数据集中包含空间网格数量
      (data.rowid.max() + 1) * (data.colid.max() + 1)) # 空间网格总数
# 输出：2082 3551
print(data.groupby(['rowid', 'colid']).time_id.nunique().mean(), # 数据集中各空间网格平均包含的时间段数量
      data.time_id.max() + 1) # 时间段总数

#可视化流量网格
import matplotlib.pyplot as plt  
import seaborn as sns  
plt.figure(figsize=(12, 8))
sns.heatmap(data.groupby(['rowid', 'colid']).size().reset_index(  
    name='volume').pivot_table('volume', 'rowid', 'colid'), cmap='Blues')
plt.show()  

def grid_recovery(df_, cols=[], lens=[]):  
    '''''修复缺失网格，填充0'''  
    df = df_.copy()  
    lcols = len(cols)  
    llens = len(lens)  
    if lcols != llens: # 确保输入的网格名称与网格长度信息的长度一致  
        raise ValueError(f'Lengths of cols ({lcols}) and lens ({llens}) mismatch.')  
    recovery_df = None
    for c, l in zip(cols, lens):  
        tmp_df = pd.DataFrame({c: range(l)}) # 完整网格  
        tmp_df['flag'] = True # 网格补全标记列 
        if recovery_df is None:  
            recovery_df = tmp_df.copy()  
        else:  
            recovery_df = recovery_df.merge(tmp_df, 'left', 'flag')  
    del recovery_df['flag']  
    df = recovery_df.merge(df, 'left', cols) # 补全所有网格  
    df = df.fillna(0) # 对缺失值补0  
    return df  
NROWS = 53 # 空间网格行数  
NCOLS = 67 # 空间网格列数  
NTIME = 144 # 时间网格数  
NDATE = 30 # 日期网格数
data = grid_recovery(data, ['date', 'rowid', 'colid', 'time_id'], [NDATE, NROWS, NCOLS, NTIME])  
for c in ['labels', 'volume', 'stopNum']:  
    data[c] = data[c].astype(int) # 调整数据类型  

##对数据进行聚合
data['hourid'] = data['time_id'] // 6 # 合并时间网格  
data['new_rowid'] = data.rowid // 2 # 合并空间网格  
data['new_colid'] = data.colid // 2  
volume = data.groupby( # 计算合并网格后各网格的流量  
    ['date', 'new_rowid', 'new_colid', 'hourid']).volume.sum().reset_index()  
volume.columns = ['date', 'rowid', 'colid', 'hourid', 'volume']  
##将顺序排列的历史流量数据整理成网格形式
volume_pivot = volume.pivot_table(  
    index=['date', 'hourid', 'rowid'],  
    columns='colid',  
    values='volume').reset_index() # 网格转换  
volume_pivot['timeseq'] = volume_pivot['date'] * 24 + volume_pivot['hourid'] # 时间序号  
volume_pivot_np = volume_pivot[[c for c in range(34)]].values # 提取流量数值

plt.figure(figsize=(20, 6))
sns.heatmap(volume_pivot_np)
plt.show()  

#生成训练数据，将数据处理成标准格式
import numpy as np
def gen_movie(df, nrows=27, ncols=34, ntime=30*24, win_s=10, win_t=3):  
    n_i = nrows - win_s + 1   # 18
    n_j = ncols - win_s + 1   # 25
    piece = []  
    for t in range(24, ntime):  
        for i in range(n_i):  
            for j in range(n_j):  
                # 周期特征  
                prd_piece = df[t - 24:t - 23, i:i+win_s, j:j+win_s]  
                # 邻近特征  
                nbr_piece = df[t-win_t:t+1, i:i+win_s, j:j+win_s]  
                piece.append(np.vstack([prd_piece, nbr_piece]))  
    return np.stack(piece)  
movie = gen_movie(np.asarray(volume_pivot_np.reshape((30*24, 27, 34)), order='C'))  

##搭建模型，首先定义一个卷积模块，包含卷积层、批归一化层、池化层。
import tensorflow as tf  
from tensorflow import keras  
from tensorflow.keras.layers import Conv2D, BatchNormalization  
from tensorflow.keras.layers import Activation, MaxPooling2D  
from tensorflow.keras.regularizers import l2
# 卷积层
def conv_layer(inputs,  
             num_filters=16,  
             kernel_size=3,  
             strides=1,  
             data_format='channels_first',  
             activation='relu',  
             batch_normalization=True,  
             maxpooling=True,  
             pool_size=2,  
             pool_strides=2):  
    conv = Conv2D(num_filters,  
                 kernel_size=kernel_size,  
                 strides=strides,  
                 padding='same',  
                 data_format=data_format,  
                 kernel_regularizer=l2(1e-4))  
    x = conv(inputs)  # 卷积
    if batch_normalization:
        x = BatchNormalization()(x) # 批归一化
    if activation is not None:
        x = Activation(activation)(x) # 激活函数
    if maxpooling:
        x = MaxPooling2D(pool_size=pool_size,  
                        strides=pool_strides,  
                        data_format=data_format,  
                        padding='same')(x) # 池化
    return x

##定义上采样函数，对特征图尺寸进行还原
from tensorflow.keras.layers import UpSampling2D  
def upsample_layer(inputs,  
                up_size=2,  
                interpolation='nearest',  
                data_format='channels_first'):
    upsample = UpSampling2D(size=up_size,
                    data_format=data_format,
                    interpolation=interpolation)  
    x = upsample(inputs) # 上采样
    return x

##建立完整的卷积神经网络模型
from tensorflow.keras.layers import Input, Flatten, Dense  
from tensorflow.keras.models import Model  
def cnn_model(input_shape):  
    inputs = Input(shape=input_shape)  
    x = conv_layer(inputs, 16, pool_strides=1)  
    x = conv_layer(x, 32, pool_strides=1)  
    x = conv_layer(x, 32, pool_strides=1)  
    x = conv_layer(x, 16)  
    x = upsample_layer(x, 2)  
    x = conv_layer(x, 1, maxpooling=False)  
    y = Flatten(data_format='channels_first')(x)  
    y = Dense(128, activation='relu')(y)  
    y = Dense(128, activation='relu')(y)  
    outputs = Dense(100, activation='relu')(y)  
    # 建立模型  
    model = Model(inputs=inputs, outputs=outputs)  
    return model

import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_absolute_error, mean_squared_error      
from tensorflow.keras.callbacks import EarlyStopping    
SEED = 233  # 随机种子    
np.random.seed(SEED)    
tf.random.set_seed(SEED) 
data_x = np.load('./data_x.npy')    
data_y = np.load('./data_y.npy')    
data_x = data_x.astype('float32')    
data_y = data_y.astype('float32')
data_x = np.moveaxis(data_x, [2, 3], [1, 2])
data_x.shape, data_y.shape

tf.config.list_physical_devices('GPU')
data_x /= 1404 # 归一化  
data_y /= 1404 # 归一化  
train_x, train_y = data_x[:-10800], data_y[:-10800] # 训练集     
test_x, test_y = data_x[-10800:], data_y[-10800:] # 测试集
model = cnn_model(train_x.shape[1:])      
opt = keras.optimizers.Adam(learning_rate=4e-4)      
model.compile(loss='mse',      
              optimizer=opt,      
              metrics=['mae', 'mse'])      
batch_size = 32 # 训练批次大小    
epochs = 20  # 训练轮数    
earlystop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10) # 早停策略
##对模型进行训练，为提高运行速度，仅训练了20轮
model.fit(test_x,
          train_y.reshape(-1, 100),
          batch_size=batch_size,
          epochs=epochs,
          validation_split=0.2,
          callbacks=[earlystop],
          shuffle=True) # 模型训练
predictions_test = model.predict(test_x, batch_size=512)   

from sklearn.metrics import mean_squared_error #均方误差
from sklearn.metrics import mean_absolute_error #平方绝对误差
from sklearn.metrics import r2_score#R square
#调用
mean_squared_error(predictions_test * 1404, test_y.reshape(-1, 100) * 1404)
mean_absolute_error(predictions_test * 1404, test_y.reshape(-1, 100) * 1404)

from sklearn.metrics import r2_score
mae_test = mean_absolute_error(predictions_test * 1404, test_y.reshape(-1, 100) * 1404)    
mse_test = mean_squared_error(predictions_test * 1404, test_y.reshape(-1, 100) * 1404)
R_2_score = r2_score(predictions_test * 1404, test_y.reshape(-1, 100) * 1404)

print(mae_test, mse_test, np.sqrt(mse_test),R_2_score) # 测试集误差   

##选取两个区域网格进行真实值和预测值进行可视化对比
import tensorflow
from matplotlib.font_manager import FontProperties
# 中文字体设置，需根据字体的实际路径修改fname参数
fp = FontProperties(fname='./NotoSansCJK.ttc', size=11)
fig, ax = plt.subplots(2, 2, figsize=(12, 10), dpi=200)
for idx, (axi, volframe) in enumerate(zip(ax.ravel(), [
    predictions_test[44].reshape(10,-1),
    test_y[44],
    predictions_test[36].reshape(10,-1),
    test_y[36],
])):
    sns.heatmap(volframe * 1404, vmin=0, cmap='Blues', ax=axi)
    if idx % 2 == 0:
        axi.set_title('预测值', fontproperties=fp)
    else:
        axi.set_title('真实值', fontproperties=fp)
plt.tight_layout()
plt.show()

import pandas as pd  
# 读取数据文件 
data = pd.read_csv(r'./DATASET-C-B.csv')
# 转换数据类型
for c in ['rowid', 'colid', 'time_id']:  
    data[c] = data[c].astype(int)
# 排序
data = data.sort_values(['date', 'rowid', 'colid', 'time_id']).reset_index(drop=True)
data['date'] -= data['date'].min()

def grid_recovery(df_, cols=[], lens=[]):  
    '''''修复缺失网格，填充0'''  
    df = df_.copy()  
    lcols = len(cols)  
    llens = len(lens)  
    if lcols != llens: # 确保输入的网格名称与网格长度信息的长度一致  
        raise ValueError(f'Lengths of cols ({lcols}) and lens ({llens}) mismatch.')  
    recovery_df = None
    for c, l in zip(cols, lens):  
        tmp_df = pd.DataFrame({c: range(l)}) # 完整网格  
        tmp_df['flag'] = True # 网格补全标记列 
        if recovery_df is None:  
            recovery_df = tmp_df.copy()  
        else:  
            recovery_df = recovery_df.merge(tmp_df, 'left', 'flag')  
    del recovery_df['flag']  
    df = recovery_df.merge(df, 'left', cols) # 补全所有网格  
    df = df.fillna(0) # 对缺失值补0  
    return df  
NROWS = 53 # 空间网格行数  
NCOLS = 67 # 空间网格列数  
NTIME = 144 # 时间网格数  
NDATE = 30 # 日期网格数
data = grid_recovery(data, ['date', 'rowid', 'colid', 'time_id'], [NDATE, NROWS, NCOLS, NTIME])  
for c in ['labels', 'volume', 'stopNum']:  
    data[c] = data[c].astype(int) # 调整数据类型  

data['hourid'] = data['time_id'] // 6 # 合并时间网格  
data['new_rowid'] = data.rowid // 2 # 合并空间网格  
data['new_colid'] = data.colid // 2  
volume = data.groupby( # 计算合并网格后各网格的流量  
    ['date', 'new_rowid', 'new_colid', 'hourid']).volume.sum().reset_index()  
volume.columns = ['date', 'rowid', 'colid', 'hourid', 'volume']  

data['seqid'] = data.date * 144 + data.time_id  
core_data = data.loc[    
    data.new_rowid.eq(10) & data.new_colid.eq(10)    
].reset_index(drop=True) # 提取待预测数据    
ts = core_data.groupby(['seqid']).agg({    
    'volume': 'sum',    
    'aveSpeed': 'mean',    
    'gridAcc': 'mean',    
    'speed_std': 'mean',    
    'hourid': 'mean',    
    'date': 'mean',    
    'time_id': 'mean'    
}).reset_index() # 统计各项特征，建立时间序列

from sklearn.preprocessing import MinMaxScaler    
train_ts = ts[:-5*144].reset_index(drop=True)[[    
    'volume', 'aveSpeed', 'gridAcc', 'speed_std', 'hourid']] # 提取训练集序列    
test_ts = ts[-5*144:].reset_index(drop=True)[[    
    'volume', 'aveSpeed', 'gridAcc', 'speed_std', 'hourid']] # 提取测试集序列    
y_true_test = test_ts.values[..., 0]   # 测试集预测值真值    
scaler = MinMaxScaler()     # 初始化归一化工具    
scaler.fit(train_ts.values) # 读取数据最值信息    
train_ts = pd.DataFrame(scaler.transform(train_ts), columns=train_ts.columns) # 归一化训练集    
test_ts = pd.DataFrame(scaler.transform(test_ts), columns=test_ts.columns)    # 归一化测试集  

##可视化此网格不同特征的时间序列
import matplotlib.pyplot as plt  
import seaborn as sns  

fig,ax = plt.subplots(4, 1, figsize=(10, 6), dpi=200, sharex=True)
for idx, (f, c) in enumerate(zip(['volume', 'aveSpeed', 'gridAcc', 'speed_std'], sns.color_palette('muted'))):
    sns.lineplot(x=ts[:-5*144].index, y=f, data=ts[:-5*144], color=c, ax=ax[idx])
    sns.lineplot(x=ts[-5*144:].index, y=f, data=ts[-5*144:], ax=ax[idx], color=c, alpha=0.2)
    ax[idx].grid()
    if idx == 2:
        ax[idx].set_ylim(-1, 2)
    elif idx == 3:
        ax[idx].set_ylim(-1, 11)

import numpy as np  
from sklearn.model_selection import train_test_split  
# 将时间序列预测转换为监督学习问题. 
def ts_to_supervise(ts, window, forecast):  
    """ 
    ts: 原始时间序列 
    window: 输入时间步数量 
    forecast: 输入时间步数量 
    """  
    past = []   # 存储输入的时间序列值  
    future = [] # 存储输出的时间序列值  
    for i in range(len(ts) - window - forecast + 1):  
        past.append(ts[i:i+window])  
        future.append(ts[i+window:i+window+forecast])  
    return np.stack(past), np.stack(future)  
ts_x, ts_y = ts_to_supervise(pd.concat([train_ts, test_ts]).values, 7*144, 1)  
train_X, test_X, train_y, test_y = train_test_split(    
    ts_x, ts_y, test_size=len(test_ts), shuffle=False) # 测试集划分  

import tensorflow as tf  
from tensorflow.keras.models import Model  
from tensorflow.keras.layers import LSTM, Dense, Input, Bidirectional  
# 设定随机种子  
SEED = 233  
np.random.seed(SEED)  
tf.random.set_seed(SEED)  
# 循环神经网络模型
def rnn_model(input_shape):  
    inputs = Input(shape=input_shape)  
    x = LSTM(8)(inputs)  
    x = Dense(8)(x)  
    x = Dense(1)(x)  
    model = Model(inputs=inputs, outputs=x) # 建立模型  
    return model  
model = rnn_model(train_X.shape[1:]) # 实例化模型 

##模型训练
from tensorflow.keras import optimizers  
from tensorflow.keras.callbacks import EarlyStopping  
batch_size = 16 # 每一训练批次的样本数量  
epochs = 50     # 最大训练轮数  
opt = optimizers.Adam(learning_rate=0.001) # 优化器  
model.compile(loss='mse',  
              optimizer=opt,  
              metrics=['mae', 'mse'])  
early_stopping = EarlyStopping(monitor='val_loss', min_delta=0.001, patience=20) # 早停策略  
history = model.fit(  
    train_X, train_y[..., 0],  
    batch_size=batch_size,  
    epochs=epochs,  
    validation_split=0.15, # 验证集比例  
    use_multiprocessing=True, # 使用多线程  
    callbacks=[early_stopping]) # 训练模型 

##计算测试集误差,模型性能评估
from sklearn.metrics import mean_absolute_error, mean_squared_error  
from sklearn.metrics import r2_score
pred_test = model.predict(test_X) # 预测测试集数据  
inv_test_ts = test_ts.copy()  
inv_test_ts.volume = pred_test  
y_hat_test = scaler.inverse_transform(inv_test_ts)[:, 0] # 还原归一化  
print(mean_absolute_error(y_true_test, y_hat_test),   
      mean_squared_error(y_true_test, y_hat_test),   
      np.sqrt(mean_squared_error(y_true_test, y_hat_test)),
      r2_score(y_true_test, y_hat_test))

from matplotlib.font_manager import FontProperties
fp = FontProperties(fname='./NotoSansCJK.ttc', size=11)

##真实值和预测值可视化
fig,ax = plt.subplots(1, 1, figsize=(10, 2), dpi=200, sharex=True)
c = sns.color_palette('muted')
sns.lineplot(x=ts[:-5*144].index, y='volume', data=ts[:-5*144], color=c[0], ax=ax, label='真实值')
sns.lineplot(x=ts[-5*144:].index, y='volume', data=ts[-5*144:], ax=ax, color=c[0], alpha=0.3)
sns.lineplot(x=ts[-5*144:].index, y=y_hat_test, ax=ax, color=c[1], label='预测值')
ax.legend(prop=fp)
ax.set_xlim(-50, len(ts) + 50)
ax.set_ylabel('流量', fontproperties=fp)
ax.grid()
plt.show()