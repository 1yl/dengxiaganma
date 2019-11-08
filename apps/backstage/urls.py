# coding:utf-8
from django.urls import path
from ..backstage.views import *


app_name = 'apps.user'

urlpatterns = [
    # TODO: 初始化
    path('', InitView.as_view()),
    # TODO: 车品牌
    path('bsbrand/', BsGetAllCarBrand.as_view()),
    # TODO: 车系列
    path('bsseries/', BsGetAllCarSeriseByBrand.as_view()),
    # TODO: 车型
    path('bsmodel/', BsGetAllCarModelBySeries.as_view()),
    # TODO: Admin登陆
    path('bslogin/', BsAdminLogin.as_view()),
    # TODO: 添加车品牌
    path('bsbrandadd/', BsAddBrand.as_view()),
    # TODO: 修改车品牌
    path('bsbranddel/', BsDelBrand.as_view()),
    # TODO: 用户详情
    path('bspersoninfo/', BsGetAllPersons.as_view()),
    # TODO: 待审核车辆
    path('bscheckwait/', BsCheckWait.as_view()),
    # TODO: 审核通过
    path('bschecksuccess/', BsCheckSuccess.as_view()),
    # TODO: 审核未通过
    path('bscheckfaile/', BsCheckFaile.as_view()),
    # TODO: 车库表所有车辆
    path('bscheckall/', BsCheckAll.as_view()),
    # TODO: 审核通过车辆
    path('bscheckpass/', BsCheckPass.as_view()),
    # TODO: 审核未通过车辆
    path('bscheckerror/', BsCheckError.as_view()),
    # TODO: 获取活动详情
    path('bsallactivity/', BsGetAllActivity.as_view()),
    # TODO: 获取未开始活动
    path('bsreadyactivity/', BsGetReadyActivity.as_view()),
    # TODO: 获取已开始活动
    path('bsoveractivity/', BsGetOverActivity.as_view()),
]