from django.urls import path
from . import views


app_name = "diary"
urlpatterns = [
    path("", views.index, name="index"),
    path("page/create/", views.page_create, name="page_create"),
    path("pages/", views.page_list, name="page_list"),
    path("page/<uuid:id>/", views.page_detail, name="page_detail"),
    path("page/<uuid:id>/update/", views.page_update, name="page_update"),
    path("page/<uuid:id>/putout/", views.page_putout, name="page_putout"),
    path("page/putoutlist", views.page_putoutlist, name="page_putoutlist"),
    path("page/<uuid:id>/delete/", views.page_delete, name="page_delete"),
    path("master_item/", views.master_item, name="master_item"),
    path("master_brand/", views.master_brand, name="master_brand"),
    path("qr/<uuid:id>/", views.QrCreateView.as_view(), name="qr_create"),
    path('page_history/<uuid:pk>/',
         views.PageHistoryView.as_view(), name='page_history'),
]
