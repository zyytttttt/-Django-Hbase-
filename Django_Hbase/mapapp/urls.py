from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),        # 系统主页
path('price_histogram/', views.price_histogram, name='price_histogram'),                  # 价格分布直方图
    path('district_price_distribution/', views.district_price_distribution, name='district_price_distribution'),  # 区域价格分布
    path('district_rental_quantity/', views.district_rental_quantity, name='district_rental_quantity'),            # 租赁数量分布
    path('shortest_rent_cycle/', views.shortest_rent_cycle, name='shortest_rent_cycle'),                          # 最短租赁周期
    path('rental_pie_chart/', views.rental_pie_chart, name='rental_pie_chart'),                                  # 饼图分布
    path('rental_time_distribution/', views.rental_time_distribution, name='rental_time_distribution'),          # 可租时间分布
    path('house_type_distribution/', views.house_type_distribution, name='house_type_distribution'),            # 房屋类型分布
    path('map/', views.map_view, name='map_view'),  # 地图查询功能
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
