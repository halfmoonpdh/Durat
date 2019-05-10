from django.urls import path
from . import views

app_name = "brat"

urlpatterns = [
    path('', views.home, name="home"),
    path('signup/', views.SignUp.as_view(), name="signup"),
    path('home/', views.home, name="home"),
    path('home/admin/', views.admin, name="admin"),
    path('home/temp/', views.temp, name="temp"),
    path('home/admin_derestrict/', views.admin_derestrict, name="admin_derestrict"),
    path('home/admin/all_document', views.admin_all_document, name="admin_all_document"),
    path('home/admin/month_rate', views.admin_month_rate, name="admin_month_rate"),
    path('home/listcreate/', views.listcreate, name="listcreate"),
    path('home/<str:taging_list_title>/', views.datalist, name="datalist"),
    path('home/<str:taging_list_title>/create/', views.create, name="create"),
    path('home/<str:taging_list_title>/create_to_file/', views.create_to_file, name="createtofile"),
    path('home/<str:taging_list_title>/listrename/', views.listrename, name="listrename"),
    path('home/<str:taging_list_title>/listdelete/', views.listdelete, name="listdelete"),
    path('home/<str:taging_list_title>/<int:taging_data_id>/', views.detail, name="detail"),
    path('home/<str:taging_list_title>/<int:taging_data_id>/rename/', views.datarename, name="datarename"),
    path('home/<str:taging_list_title>/<int:taging_data_id>/edit/', views.dataedit, name="dataedit"),
    path('home/<str:taging_list_title>/<int:taging_data_id>/delete/', views.datadelete, name="datadelete"),
    path('home/<str:taging_list_title>/<int:taging_data_id>/autoannotation/', views.autoannotation, name="autoannotation"),
    path('home/<str:taging_list_title>/<int:taging_data_id>/datarate/', views.datarate, name="datarate"),
    path('home/<str:taging_list_title>/<int:taging_data_id>/different_user/', views.different_user, name="different_user"),
    path('home/<str:taging_list_title>/<int:taging_data_id>/userratemodify/confirm/', views.userratemodify_confirm, name="userratemodify_confirm"),
    path('home/<str:taging_list_title>/<int:taging_data_id>/<int:tag_number>/tagedit/', views.tagedit, name="tagedit"),
]