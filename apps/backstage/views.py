# coding:utf-8
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from ..utils.common import Common
from django_redis import get_redis_connection
import json, random
from ..utils import signtools
from ..utils import redistools
from ..utils.verifyphone import VerifyPhone
from ..utils.redistools import RedisTools
from ..utils.pictools import PictureParsing, ImageParsing, LicenceParsing, LicenseParsing, ModelPasing
from ..user.models import *
from django.contrib.auth.hashers import make_password, check_password
import time, datetime, os
from rest_framework.pagination import PageNumberPagination
from ..backstage.serializer import BrandSerializer, SeriseSerializer, ModelSerializer, UserSerializer, CarBarnSerializer, ActivitySerializer
from django.core import serializers

# basedir = os.path.abspath(os.path.dirname(__file__))


# Create your views here.
# TODO：初始化
class InitView(APIView):
    def get(self, request):
        return Response("111")

# TODO: 分页功能自定义类
class MyPageNumberPagination(PageNumberPagination):
    # 默认每页显示的数据条数
    page_size = 10
    # 获取 url 参数中设置的每页显示数据条数
    page_size_query_param = 'size'
    # 最大支持的每页显示的数据条数
    max_page_size = 10
    # 获取 url 参数中传入的页码 key
    page_query_param = 'page'


# TODO: 我的车库
class BsMycars(APIView):
    def get(self, request):
        # 用户手机号
        pid = request.GET.get("pid")
        print(pid)
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取用户车库
        carbarn_list = CarBarn.objects.filter(car_person_id=user_obj.id)
        lis = []
        for i in carbarn_list:
            # 获取单车辆车型
            single_model_obj = CarModel.objects.filter(id=i.car_model_id)
            # 根据车型获取车的详细信息
            # 车品牌  车系列
            # brand_id  series_id
            single_brand_obj = CarBrand.objects.filter(id=single_model_obj[0].brand_id)
            single_series_obj = CarSeries.objects.filter(id=single_model_obj[0].series_id)
            if single_model_obj[0].price == '':
                price = ''
            else:
                price = single_model_obj[0].price.split('-')[1]
            dic = {
                "car_id": i.id,
                "car_brand_name": single_brand_obj[0].name,
                "car_series_name": single_series_obj[0].name,
                "car_model_name": single_model_obj[0].name,
                "car_price": price,
                "car_initial": single_brand_obj[0].initial,
                "car_image_filename": single_brand_obj[0].image_filename,
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))

    # 车辆信息
    def post(self, request):
        # 车辆id
        car_id = request.data.get("car_id")
        # 车辆信息
        car_obj = CarBarn.objects.filter(id=car_id).first()
        # 获取单车辆车型
        single_model_obj = CarModel.objects.filter(id=car_obj.car_model_id).first()
        # 根据车型获取车的详细信息
        single_brand_obj = CarBrand.objects.filter(id=single_model_obj.brand_id).first()
        single_series_obj = CarSeries.objects.filter(id=single_model_obj.series_id).first()
        if single_model_obj.price == '':
            price = ''
        else:
            price = single_model_obj.price.split('-')[1]
        dic = {
            "car_id": car_id,
            "car_brand_name": single_brand_obj.name,
            "car_series_name": single_series_obj.name,
            "car_model_name": single_model_obj.name,
            "car_price": price,
            "car_initial": single_brand_obj.initial,
            "car_image_filename": single_brand_obj.image_filename,
        }
        return Response(Common.tureReturn(Common, data=dic))

    # 添加车辆（修改）
    def put(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取车辆型号
        car_model_name = request.data.get("car_model_name")
        # 根据车辆型号获取车辆对象
        single_model_obj = CarModel.objects.filter(name=car_model_name).first()
        # 保存车辆信息至我的车库
        CarBarn.objects.create(car_model_id=single_model_obj.id, car_person_id=user_obj.id)
        # 获取行驶证
        driver_licence = request.data.get("driver_licence")
        # 用户行驶证后缀
        licence_suffix = request.data.get("licence_suffix")
        if driver_licence != '' and licence_suffix != '':
            img = LicenceParsing(driver_licence, licence_suffix)
            user_obj.driver_licence = img
        # 获取驾驶证
        driver_license = request.data.get("driver_license")
        # 用户驾驶证后缀
        license_suffix = request.data.get("license_suffix")
        if driver_licence != '' and licence_suffix != '':
            img = LicenseParsing(driver_license, license_suffix)
            user_obj.driver_license = img
        # 判断该用户是否已存在驾驶证和行驶证
        user_obj.save()
        return Response(Common.tureReturn(Common, data='添加车辆成功'))

    # 删除车库中指定车辆
    def delete(self, request):
        # 车辆id
        # car_id = request.data.get("car_id")
        car_id = request.GET.get("car_id")
        print(car_id)
        # 车辆信息
        car_obj = CarBarn.objects.filter(id=car_id).first()
        print(car_obj)
        car_obj.delete()
        return Response(Common.tureReturn(Common, data='删除车辆成功'))


# TODO: 获取所有车型
class BsGetAllCarBrand(APIView):
    def post(self, request):
        all_brand_objects = CarBrand.objects.all()
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=all_brand_objects, request=request, view=self)
        # 实例化对象
        ser = BrandSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            dic = {
                "brand_id": i["id"],
                "name": i["name"],
                "initial": i["initial"],
                "image_filename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(i["image_filename"]),
            }
            lis.append(dic)
        lis[0]["number"] = all_brand_objects.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 根据某一车型获取该车型系列
class BsGetAllCarSeriseByBrand(APIView):
    def post(self, request):
        car_brand_id = request.data.get("car_brand_id")
        car_series_list = CarSeries.objects.filter(brand_id=car_brand_id)
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=car_series_list, request=request, view=self)
        # 实例化对象
        ser = SeriseSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            carbrand_obj = CarBrand.objects.filter(id=i["brand"]).first()
            data = {
                "series_id": i["id"],
                "brand_id": carbrand_obj.id,
                "series_name": i["name"],
                "brand_name": carbrand_obj.name,
                "initial": carbrand_obj.initial,
                "image_filename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(carbrand_obj.image_filename),
            }
            lis.append(data)
        lis[0]["number"] = car_series_list.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 根据某一车系和车品牌获取该车型
class BsGetAllCarModelBySeries(APIView):
    def post(self, request):
        car_series_id = request.data.get("car_series_id")
        car_brand_id = request.data.get("car_brand_id")
        car_model_list = CarModel.objects.filter(brand_id=car_brand_id, series_id=car_series_id)
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=car_model_list, request=request, view=self)
        # 实例化对象
        ser = ModelSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            carbrand_obj = CarBrand.objects.filter(id=i["brand"]).first()
            carseries_obj = CarSeries.objects.filter(id=i["series"]).first()
            data = {
                "model_id": i["id"],
                "series_id": carseries_obj.id,
                "brand_id": carbrand_obj.id,
                "series_name": carseries_obj.name,
                "brand_name": carbrand_obj.name,
                "initial": carbrand_obj.initial,
                "image_filename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(carbrand_obj.image_filename),
                "model_name": i["name"],
                "price": i["price"]
            }
            lis.append(data)
        lis[0]["number"] = car_model_list.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: Admin登录
class BsAdminLogin(APIView):
    def post(self, request):
        uname = request.data.get("username")
        upwd = request.data.get("password")
        if uname == "admin" and upwd == "admin":
            return Response(Common.tureReturn(Common, data=True))
        else:
            return Response(Common.falseReturn(Common, data=False))


# TODO: 添加车品牌
class BsAddBrand(APIView):
    def post(self, request):
        model_name = request.data.get("model_name")
        brand_obj = CarBrand.objects.filter(name=model_name).first()
        if not brand_obj:
            model_initial = request.data.get("model_initial")
            # 车标
            base64 = request.data.get("base64")
            type = request.data.get("type")
            if base64 != '' and type:
                img = ModelPasing(base64, type)
            else:
                img = ""
            CarBrand.objects.create(name=model_name, initial=model_initial, image_filename=img)
            return Response(Common.tureReturn(Common, data="添加成功"))
        else:
            return Response(Common.falseReturn(Common, data="添加失败,该品牌已存在"))


# TODO: 修改车品牌
class BsDelBrand(APIView):
    def post(self, request):
        model_id = request.data.get("model_id")
        new_model_name = request.data.get("new_model_name")
        car_logo = request.data.get("car_logo")
        print(car_logo)
        print(model_id)
        print(new_model_name)
        brand_new_obj = CarBrand.objects.filter(name=new_model_name).first()
        brand_obj = CarBrand.objects.filter(id=model_id).first()
        if brand_obj.name == new_model_name or not brand_new_obj:
            model_initial = request.data.get("model_initial")
            # 车标
            # car_logo = request.data.get("car_logo")
            base64 = request.data.get("base64")
            type = request.data.get("type")
            print(car_logo)
            # for i in car_logo:
            # if i["base64"] != '' and i["type"]:
            if base64 != '' and type != '':
                img = ModelPasing(base64, type)
                brand_obj.image_filename = img
            brand_obj.name = new_model_name
            brand_obj.initial = model_initial
            brand_obj.save()
            return Response(Common.tureReturn(Common, data="修改成功"))
        else:
            return Response(Common.falseReturn(Common, data="修改失败,该品牌已存在"))


# TODO: 获取用户详情
class BsGetAllPersons(APIView):
    def post(self, request):
        all_user_objects = User.objects.all()
        print(all_user_objects)
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=all_user_objects, request=request, view=self)
        # 实例化对象
        ser = UserSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            dic = {
                # 主键
                "user_id": i["id"],
                # 用户昵称
                "username": i["username"],
                # 头像
                "img_head": "http://52.80.194.137:8001/dxgm/image/{0}".format(i["img_head"]),
                # 手机号
                "phone": i["phone"],
                # 注册时间
                "add_time": i["add_time"],
                # 最近登录时间
                "use_time": i["use_time"],
                # 出生日期
                "born_time": i["born_time"],
                # 性别
                "sex": i["sex"],
                # 职业
                "job": i["job"],
                # 地区
                "area": i["area"],
                # # 行驶证
                # "driver_licence": "http://52.80.194.137:8001/dxgm/driver_licence/{0}".format(i["driver_licence"]),
                # # 驾驶证
                # "driver_license": "http://52.80.194.137:8001/dxgm/driver_license/{0}".format(i["driver_license"]),
                # 星座
                "sign": i["sign"],
                # 点数
                "coin": i["coin"],
                # 颜值
                "face_score": i["face_score"]
            }
            lis.append(dic)
        lis[0]["number"] = all_user_objects.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 车库表所有车辆
class BsCheckAll(APIView):
    def post(self, request):
        # 获取用户车库
        carbarn_list = CarBarn.objects.all()
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=carbarn_list, request=request, view=self)
        # 实例化对象
        ser = CarBarnSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            # 获取单车辆车型
            single_model_obj = CarModel.objects.filter(id=i["car_model"])
            # 根据车型获取车的详细信息
            # 车品牌  车系列
            # brand_id  series_id
            single_brand_obj = CarBrand.objects.filter(id=single_model_obj[0].brand_id)
            single_series_obj = CarSeries.objects.filter(id=single_model_obj[0].series_id)
            # # # 获取用户对象
            user_obj = User.objects.filter(id=i["car_person"]).first()
            if single_model_obj[0].price == '':
                price = ''
            else:
                price = single_model_obj[0].price.split('-')[1]
            print(i)
            print(i["driver_licence"])
            dic = {

                # 用户昵称
                "user_name": user_obj.username,
                # 车辆主键id
                "car_id": i["id"],
                # 车品牌名称
                "car_brand_name": single_brand_obj[0].name,
                # 车系列名称
                "car_series_name": single_series_obj[0].name,
                # 车型名称
                "car_model_name": single_model_obj[0].name,
                # 车价格
                "car_price": price,
                # 车首写字母
                "car_initial": single_brand_obj[0].initial,
                # 车标图片
                "car_image_filename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(
                    single_brand_obj[0].image_filename),
                # 车行驶证
                "driver_licence": "http://52.80.194.137:8001/dxgm/driver_licence/{0}".format(i["driver_licence"]),
                # 车驾驶证
                "driver_license": "http://52.80.194.137:8001/dxgm/driver_license/{0}".format(i["driver_license"]),
                # 车状态 0：待审核
                "check_status": i["check_status"],
                # 审核情况
                "false_result": i["false_result"]
            }
            lis.append(dic)
        lis[0]["number"] = carbarn_list.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 待审核车辆
class BsCheckWait(APIView):
    def post(self, request):
        # 获取用户车库
        carbarn_list = CarBarn.objects.filter(check_status='0')
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=carbarn_list, request=request, view=self)
        # 实例化对象
        ser = CarBarnSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            # 获取单车辆车型
            single_model_obj = CarModel.objects.filter(id=i["car_model"])
            # 根据车型获取车的详细信息
            # 车品牌  车系列
            # brand_id  series_id
            single_brand_obj = CarBrand.objects.filter(id=single_model_obj[0].brand_id)
            single_series_obj = CarSeries.objects.filter(id=single_model_obj[0].series_id)
            # # # 获取用户对象
            user_obj = User.objects.filter(id=i["car_person"]).first()
            if single_model_obj[0].price == '':
                price = ''
            else:
                price = single_model_obj[0].price.split('-')[1]

            dic = {
                # 用户昵称
                "user_name": user_obj.username,
                # 车辆主键id
                "car_id": i["id"],
                # 车品牌名称
                "car_brand_name": single_brand_obj[0].name,
                # 车系列名称
                "car_series_name": single_series_obj[0].name,
                # 车型名称
                "car_model_name": single_model_obj[0].name,
                # 车价格
                "car_price": price,
                # 车首写字母
                "car_initial": single_brand_obj[0].initial,
                # 车标图片
                "car_image_filename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(
                    single_brand_obj[0].image_filename),
                # 车行驶证
                "driver_licence": "http://52.80.194.137:8001/dxgm/driver_licence/{0}".format(i["driver_licence"]),
                # 车驾驶证
                "driver_license": "http://52.80.194.137:8001/dxgm/driver_license/{0}".format(i["driver_license"]),
                # 车状态 0：待审核
                "check_status": i["check_status"],
                # 审核情况
                "false_result": i["false_result"]
            }
            lis.append(dic)
        lis[0]["number"] = carbarn_list.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 审核通过车辆
class BsCheckPass(APIView):
    def post(self, request):
        # 获取用户车库
        carbarn_list = CarBarn.objects.filter(check_status='1')
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=carbarn_list, request=request, view=self)
        # 实例化对象
        ser = CarBarnSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            # 获取单车辆车型
            single_model_obj = CarModel.objects.filter(id=i["car_model"])
            # 根据车型获取车的详细信息
            # 车品牌  车系列
            # brand_id  series_id
            single_brand_obj = CarBrand.objects.filter(id=single_model_obj[0].brand_id)
            single_series_obj = CarSeries.objects.filter(id=single_model_obj[0].series_id)
            # # # 获取用户对象
            user_obj = User.objects.filter(id=i["car_person"]).first()
            if single_model_obj[0].price == '':
                price = ''
            else:
                price = single_model_obj[0].price.split('-')[1]
            dic = {
                # 用户昵称
                "user_name": user_obj.username,
                # 车辆主键id
                "car_id": i["id"],
                # 车品牌名称
                "car_brand_name": single_brand_obj[0].name,
                # 车系列名称
                "car_series_name": single_series_obj[0].name,
                # 车型名称
                "car_model_name": single_model_obj[0].name,
                # 车价格
                "car_price": price,
                # 车首写字母
                "car_initial": single_brand_obj[0].initial,
                # 车标图片
                "car_image_filename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(
                    single_brand_obj[0].image_filename),
                # 车行驶证
                "driver_licence": "http://52.80.194.137:8001/dxgm/driver_licence/{0}".format(i["driver_licence"]),
                # 车驾驶证
                "driver_license": "http://52.80.194.137:8001/dxgm/driver_license/{0}".format(i["driver_license"]),
                # 车状态 0：待审核
                "check_status": i["check_status"],
                # 审核情况
                "false_result": i["false_result"]
            }
            lis.append(dic)
        lis[0]["number"] = carbarn_list.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 审核未通过车辆
class BsCheckError(APIView):
    def post(self, request):
        # 获取用户车库
        carbarn_list = CarBarn.objects.filter(check_status='2')
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=carbarn_list, request=request, view=self)
        # 实例化对象
        ser = CarBarnSerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            # 获取单车辆车型
            single_model_obj = CarModel.objects.filter(id=i["car_model"])
            # 根据车型获取车的详细信息
            # 车品牌  车系列
            # brand_id  series_id
            single_brand_obj = CarBrand.objects.filter(id=single_model_obj[0].brand_id)
            single_series_obj = CarSeries.objects.filter(id=single_model_obj[0].series_id)
            # # # 获取用户对象
            user_obj = User.objects.filter(id=i["car_person"]).first()
            if single_model_obj[0].price == '':
                price = ''
            else:
                price = single_model_obj[0].price.split('-')[1]
            dic = {
                # 用户昵称
                "user_name": user_obj.username,
                # 车辆主键id
                "car_id": i["id"],
                # 车品牌名称
                "car_brand_name": single_brand_obj[0].name,
                # 车系列名称
                "car_series_name": single_series_obj[0].name,
                # 车型名称
                "car_model_name": single_model_obj[0].name,
                # 车价格
                "car_price": price,
                # 车首写字母
                "car_initial": single_brand_obj[0].initial,
                # 车标图片
                "car_image_filename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(
                    single_brand_obj[0].image_filename),
                # 车行驶证
                "driver_licence": "http://52.80.194.137:8001/dxgm/driver_licence/{0}".format(i["driver_licence"]),
                # 车驾驶证
                "driver_license": "http://52.80.194.137:8001/dxgm/driver_license/{0}".format(i["driver_license"]),
                # 车状态 0：待审核
                "check_status": i["check_status"],
                # 审核情况
                "false_result": i["false_result"]
            }
            lis.append(dic)
        lis[0]["number"] = carbarn_list.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 审核通过
class BsCheckSuccess(APIView):
    def post(self, request):
        # 用户车辆id
        car_id = request.data.get("car_id")
        # print(pid)
        # 获取车辆对象
        carbarn_obj = CarBarn.objects.filter(id=car_id).first()
        carbarn_obj.check_status = '1'
        carbarn_obj.false_result = '审核通过'
        carbarn_obj.save()
        return Response(Common.tureReturn(Common, data='审核通过'))


# TODO: 审核失败
class BsCheckFaile(APIView):
    def post(self, request):
        # 用户车辆id
        car_id = request.data.get("car_id")
        # 失败原因
        false_result = request.data.get("false_result")
        # 获取车辆对象
        carbarn_obj = CarBarn.objects.filter(id=car_id).first()
        carbarn_obj.check_status = '2'
        carbarn_obj.false_result = '审核失败,'+false_result
        carbarn_obj.save()
        return Response(Common.tureReturn(Common, data='审核失败'))


# TODO: 获取未开始活动
class BsGetReadyActivity(APIView):
    def post(self, request):
        # 获取现在的时间
        now = datetime.datetime.now()
        all_activity_objects = Activity.objects.filter(activity_time__gt=now).order_by('activity_time')
        print(all_activity_objects)
        if len(all_activity_objects) > 0:
            # 实例化分页对象, 获取数据库中的分页数据
            pagination_class = MyPageNumberPagination()
            page_list = pagination_class.paginate_queryset(queryset=all_activity_objects, request=request, view=self)
            # 实例化对象
            ser = ActivitySerializer(instance=page_list, many=True)  # 可允许多个
            lis = []
            for i in ser.data:
                like_obj = Like.objects.filter(id=i["activity_name"]).first()
                user_obj = User.objects.filter(id=i["activity_issue"]).first()
                topic_obj = Topic.objects.filter(id=i["topic_name"]).first()
                carbarn_obj = CarBarn.objects.filter(id=i["activity_car"]).first()
                carmodel_obj = CarModel.objects.filter(id=carbarn_obj.car_model_id).first()

                print(i["activity_time"])
                dic = {
                    # 主键
                    "activity_id": i["id"],
                    # 活动昵称
                    "username": like_obj.likename,
                    # 话题名称
                    "topic_name": topic_obj.topic_name,
                    # 活动类型种类(单人/多人)
                    "activity_kind": i["activity_kind"],
                    # 活动发布人
                    "activity_issue": user_obj.username,
                    # 活动时间
                    "activity_time": i["activity_time"],
                    # 活动出发地
                    "activity_area_start": i["activity_area_start"],
                    # 活动目的地
                    "activity_area_end": i["activity_area_end"],
                    # 活动参与人群性别
                    "activity_person_sex": i["activity_person_sex"],
                    # 活动参与人群数量
                    "activity_person_num": i["activity_person_num"],
                    # 活动携带人数
                    "activity_person_take": i["activity_person_take"],
                    # 活动参与点数
                    "activity_coin_take": i["activity_coin_take"],
                    # 我的出行车辆
                    "activity_car": carmodel_obj.name,
                    # 发布时间
                    "activity_create_time": i["activity_create_time"]
                }
                lis.append(dic)
            lis[0]["number"] = all_activity_objects.count()
            return Response(Common.tureReturn(Common, data=lis))
        else:
            return Response(Common.tureReturn(Common, data=[]))


        # TODO: 获取已开始活动
class BsGetOverActivity(APIView):
    def post(self, request):
        # 获取现在的时间
        now = datetime.datetime.now()
        all_activity_objects = Activity.objects.filter(activity_time__lt=now).order_by('-activity_time')
        print(all_activity_objects)
        if len(all_activity_objects) > 0:
            # 实例化分页对象, 获取数据库中的分页数据
            pagination_class = MyPageNumberPagination()
            page_list = pagination_class.paginate_queryset(queryset=all_activity_objects, request=request, view=self)
            # 实例化对象
            ser = ActivitySerializer(instance=page_list, many=True)  # 可允许多个
            lis = []
            for i in ser.data:
                like_obj = Like.objects.filter(id=i["activity_name"]).first()
                user_obj = User.objects.filter(id=i["activity_issue"]).first()
                topic_obj = Topic.objects.filter(id=i["topic_name"]).first()
                carbarn_obj = CarBarn.objects.filter(id=i["activity_car"]).first()
                carmodel_obj = CarModel.objects.filter(id=carbarn_obj.car_model_id).first()

                print(i["activity_time"])
                dic = {
                    # 主键
                    "activity_id": i["id"],
                    # 活动昵称
                    "username": like_obj.likename,
                    # 话题名称
                    "topic_name": topic_obj.topic_name,
                    # 活动类型种类(单人/多人)
                    "activity_kind": i["activity_kind"],
                    # 活动发布人
                    "activity_issue": user_obj.username,
                    # 活动时间
                    "activity_time": i["activity_time"],
                    # 活动出发地
                    "activity_area_start": i["activity_area_start"],
                    # 活动目的地
                    "activity_area_end": i["activity_area_end"],
                    # 活动参与人群性别
                    "activity_person_sex": i["activity_person_sex"],
                    # 活动参与人群数量
                    "activity_person_num": i["activity_person_num"],
                    # 活动携带人数
                    "activity_person_take": i["activity_person_take"],
                    # 活动参与点数
                    "activity_coin_take": i["activity_coin_take"],
                    # 我的出行车辆
                    "activity_car": carmodel_obj.name,
                    # 发布时间
                    "activity_create_time": i["activity_create_time"]
                }
                lis.append(dic)
            lis[0]["number"] = all_activity_objects.count()
            return Response(Common.tureReturn(Common, data=lis))
        else:
            return Response(Common.tureReturn(Common, data=[]))



# TODO: 获取活动详情
class BsGetAllActivity(APIView):
    def post(self, request):
        all_activity_objects = Activity.objects.all()
        print(all_activity_objects)
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=all_activity_objects, request=request,
                                                       view=self)
        # 实例化对象
        ser = ActivitySerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            like_obj = Like.objects.filter(id=i["activity_name"]).first()
            user_obj = User.objects.filter(id=i["activity_issue"]).first()
            topic_obj = Topic.objects.filter(id=i["topic_name"]).first()
            carbarn_obj = CarBarn.objects.filter(id=i["activity_car"]).first()
            carmodel_obj = CarModel.objects.filter(id=carbarn_obj.car_model_id).first()

            print(i["activity_time"])
            dic = {
                # 主键
                "activity_id": i["id"],
                # 活动昵称
                "username": like_obj.likename,
                # 话题名称
                "topic_name": topic_obj.topic_name,
                # 活动类型种类(单人/多人)
                "activity_kind": i["activity_kind"],
                # 活动发布人
                "activity_issue": user_obj.username,
                # 活动时间
                "activity_time": i["activity_time"],
                # 活动出发地
                "activity_area_start": i["activity_area_start"],
                # 活动目的地
                "activity_area_end": i["activity_area_end"],
                # 活动参与人群性别
                "activity_person_sex": i["activity_person_sex"],
                # 活动参与人群数量
                "activity_person_num": i["activity_person_num"],
                # 活动携带人数
                "activity_person_take": i["activity_person_take"],
                # 活动参与点数
                "activity_coin_take": i["activity_coin_take"],
                # 我的出行车辆
                "activity_car": carmodel_obj.name,
                # 发布时间
                "activity_create_time": i["activity_create_time"]
            }
            lis.append(dic)
        lis[0]["number"] = all_activity_objects.count()
        return Response(Common.tureReturn(Common, data=lis))

        # model_id = request.data.get("model_id")
        # new_model_name = request.data.get("new_model_name")
        # car_logo = request.data.get("car_logo")
        # print(car_logo)
        # print(model_id)
        # print(new_model_name)
        # brand_new_obj = CarBrand.objects.filter(name=new_model_name).first()
        # brand_obj = CarBrand.objects.filter(id=model_id).first()
        # if brand_obj.name == new_model_name or not brand_new_obj:
        #     model_initial = request.data.get("model_initial")
        #     # 车标
        #     # car_logo = request.data.get("car_logo")
        #     base64 = request.data.get("base64")
        #     type = request.data.get("type")
        #     print(car_logo)
        #     # for i in car_logo:
        #     # if i["base64"] != '' and i["type"]:
        #     if base64 != '' and type != '':
        #         img = ModelPasing(base64, type)
        #         brand_obj.image_filename = img
        #     brand_obj.name = new_model_name
        #     brand_obj.initial = model_initial
        #     brand_obj.save()
        #     return Response(Common.tureReturn(Common, data="修改成功"))
        # else:
        #     return Response(Common.falseReturn(Common, data="修改失败,该品牌已存在"))
        #
        # # 获取用户车库
        # carbarn_list = CarBarn.objects.filter(car_person_id=user_obj.id)
        # lis = []
        # for i in carbarn_list:
        #     # 获取单车辆车型
        #     single_model_obj = CarModel.objects.filter(id=i.car_model_id)
        #     # 根据车型获取车的详细信息
        #     # 车品牌  车系列
        #     # brand_id  series_id
        #     single_brand_obj = CarBrand.objects.filter(id=single_model_obj[0].brand_id)
        #     single_series_obj = CarSeries.objects.filter(id=single_model_obj[0].series_id)
        #     if single_model_obj[0].price == '':
        #         price = ''
        #     else:
        #         price = single_model_obj[0].price.split('-')[1]
        #     dic = {
        #         "car_id": i.id,
        #         "car_brand_name": single_brand_obj[0].name,
        #         "car_series_name": single_series_obj[0].name,
        #         "car_model_name": single_model_obj[0].name,
        #         "car_price": price,
        #         "car_initial": single_brand_obj[0].initial,
        #         "car_image_filename": single_brand_obj[0].image_filename,
        #         "driver_licence": "http://52.80.194.137:8001/dxgm/driver_licence/{0}".format(i.driver_licence),
        #         "driver_license": "http://52.80.194.137:8001/dxgm/driver_license/{0}".format(i.driver_license),
        #         "check_status": i.check_status
        #     }
        #     lis.append(dic)
        # return Response(Common.tureReturn(Common, data=lis))