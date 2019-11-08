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
from ..utils.publishtools import postActivity
from ..utils.pictools import PictureParsing, ImageParsing, LicenceParsing, LicenseParsing, Parsing
from ..user.models import *
from django.contrib.auth.hashers import make_password, check_password
import datetime, time
import time
from rest_framework.pagination import PageNumberPagination
from dengxiaganma.settings import WEB_HOST_NAME, WEB_IMAGE_SERVER_PATH, WEB_PICTURE_SERVER_PATH, \
    WEB_LICENCE_SERVER_PATH, WEB_LICENSE_SERVER_PATH, WEB_ACTIVITY_SERVER_PATH, WEB_MODEL_BJ_PATH
from ..user.serializer import ActivitySerializer
from rongcloud.rongcloud import RongCloud
import requests
import base64
import urllib
import urllib3
import math

rc = RongCloud('cpj2xarlct5cn', 'HjPcGQPfnC')
# from rongcloud.user import RCUser
# from rongcloud.base import RongCloudBase
# from rongcloud.message import Message

# 人脸识别
import base64
import json
import requests


# 人脸颜值测试
class BaiduPicIndentify(APIView):
    def __init__(self):
        self.AK = "cf75KhDFAbmqHjZEYYhUbKGc&client"
        self.SK = "67G5iBvU2rlEN8IxFSIn4SvmniNHWyHT"
        # self.img_src = '/var/codelion/picture/1568268285.jpg'
        # self.img_src = '/var/codelion/picture/1567496919.jpg'
        # self.img_src = '/var/codelion/picture/1567476284.jpg'
        # self.img_src = '/var/codelion/picture/1568274308.jpg'
        # self.img_src = '/var/codelion/picture/1568274731.jpg'
        self.img_src = '/var/codelion/picture/1568275002.png'
        self.headers = {
            "Content-Type": "application/json; charset=UTF-8"
        }

    def get_accessToken(self):
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' + self.AK + '&client_secret=' + self.SK
        response = requests.get(host, headers=self.headers)
        json_result = json.loads(response.text)
        return json_result['access_token']

    def img_to_BASE64(slef, path):
        with open(path, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            return base64_data

    def detect_face(self,img):
        # 人脸检测与属性分析
        # img_BASE64 = self.img_to_BASE64(self.img_src)
        img_BASE64 = self.img_to_BASE64("/var/codelion/picture/{0}".format(img))

        ''
        print(img_BASE64)
        # img_BASE64 = bs
        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        post_data = {
            "image": img_BASE64,
            "image_type": "BASE64",
            "face_field": "gender,age,beauty,gender,race,expression",
            "face_type": "LIVE"
        }
        access_token = self.get_accessToken()
        request_url = request_url + "?access_token=" + access_token
        response = requests.post(url=request_url, data=post_data, headers=self.headers)
        json_result = json.loads(response.text)
        print(json_result)
        if json_result['error_msg'] != 'pic not has face':
            data = {
                "beauty": json_result['result']['face_list'][0]['beauty']
            }
            print("图片中包含人脸数：", json_result['result']['face_num'])
            print("图片中包含人物年龄：", json_result['result']['face_list'][0]['age'])
            print("图片中包含人物颜值评分：", json_result['result']['face_list'][0]['beauty'])
            print("图片中包含人物性别：", json_result['result']['face_list'][0]['gender']['type'])
            print("图片中包含人物种族：", json_result['result']['face_list'][0]['race']['type'])
            print("图片中包含人物表情：", json_result['result']['face_list'][0]['expression']['type'])
            return data

    def post(self, request):
        pid = request.data.get("pid")
        user_obj = User.objects.filter(id=pid).first()
        print(user_obj)
        base64 = request.data.get("base64")
        print(base64)
        type = request.data.get("type")
        print(type)
        # print(bs)
        img = Parsing(base64, type, WEB_ACTIVITY_SERVER_PATH)
        baiduDetect = BaiduPicIndentify()
        data = baiduDetect.detect_face(img)
        print(data)
        if int(data["beauty"]) <= 40:
            data["beauty"] = str(int(data["beauty"]) + 35)
        elif int(data["beauty"]) <= 60:
            data["beauty"] = str(int(data["beauty"]) + 15)
        else:
            data["beauty"] = data["beauty"]
        user_obj.face_score = data["beauty"]
        user_obj.save()
        return Response(Common.tureReturn(Common, data=data))



# Create your views here.
# TODO：初始化
class InitView(APIView):
    def get(self, request):
        # res = rc.get_user().register("rc_id_4", "zhangsan", "https://www.baidu.com/img/bg_logo1.png?where=super")
        # RongCloudBase()
        # m = Message()
        # content = {'content': ' 李传平', 'extra': ''}
        # rep = rc.get_message().get_private().send(from_user_id='rc_id_1', to_user_ids='rc_id_2', object_name='RC:TxtMsg', content=content)
        # print(rep)
        host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=' \
               'cf75KhDFAbmqHjZEYYhUbKGc&client_secret=67G5iBvU2rlEN8IxFSIn4SvmniNHWyHT'
        header = {'Content-Type': 'application/json; charset=UTF-8'}
        response1 = requests.post(url=host, headers=header)  # <class 'requests.models.Response'>
        json1 = response1.json()  # <class 'dict'>
        print(json1)
        access_token = json1['access_token']

        request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        filepath = '/var/codelion/picture/1568268285.jpg'
        # 二进制方式打开图片文件
        f = open(filepath, 'rb')
        img = base64.b64encode(f.read())

        params = {"face_fields": "age,beauty,expression,faceshape,gender,glasses,landmark,race,qualities", "image": img,
                  "max_face_num": 5}
        params = urllib.parse.urlencode(params).encode(encoding='UTF8')

        access_token = access_token
        request_url = request_url + "?access_token=" + access_token
        request = urllib.request.Request(url=request_url, data=params)
        print(request)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib.request.urlopen(request)
        content = response.read()
        if content:
            print(content)



        # # 转换图片格式
        # filepath = '/var/codelion/picture/1568268285.jpg'
        # f = open(r'%s' % filepath, 'rb')
        # pic = base64.b64encode(f.read())
        # f.close()
        # base64s = str(pic, 'utf-8')
        # # print(base64s)
        # # 访问人脸检测api
        # request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
        # params = {"image": base64, "image_type": "BASE64", "face_field": "faceshape,facetype,beauty,"}
        # header = {'Content-Type': 'application/json'}
        # request_url = request_url + "?access_token=" + access_token
        # response1 = requests.post(url=request_url, data=params, headers=header)  # <class 'requests.models.Response'>
        # json1 = response1.json()  # <class 'dict'>
        # print(json1)
        # print("颜值评分为")
        # print(json1["result"]["face_list"][0]['beauty'], '分/100分')

        return Response(Common.falseReturn(Common, data="111"))


# TODO: 日期
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj,datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)

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


# TODO: 发送验证码
class SendSMSView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        # 发送验证码
        """
        sms_code = "%06d" % random.randint(0, 999999)
        # 创建redis连接对象（'verify_codes'表示settings文件中redis配置的选择）
        redis_conn = get_redis_connection("verify_codes")
        # 使用管道
        # print(redis_conn)
        pl = redis_conn.pipeline()
        # 存储短信验证码至redis数据库
        pl.setex("sms_%s" % phone, redistools.SMS_CODE_REDIS_EXPIRES, sms_code)
        # 记录用户发送短信的频次
        pl.setex('send_flag_%s' % phone, redistools.SEND_SMS_CODE_INTERVAL, 1)
        # 指令传递，将数据写入redis
        pl.execute()
        """
        sms_code = RedisTools().linkredis(phone=phone)
        print(sms_code)
        # 获取该号码在redis中的频次
        send_flag = RedisTools().redis_conn.get('send_flag_%s' % phone)
        if int(send_flag) > 1:
            return Response({"msg": "操作太过频繁！", "status": '0'})
        else:
            # 发送短信验证码
            try:
                vp = VerifyPhone(phone=phone, sms_code=sms_code)
                res = vp.send_sms()
                return Response(Common.tureReturn(Common, data=res))
            except Exception as e:
                print(e)
                return Response(Common.falseReturn(Common, data='发送失败'))

# TODO: 用户手机注册
class RegistView(APIView):
    def post(self, request):
        """
        获取json数据
        phone = request.data
        return Response(phone)
        return Response(Common.tureReturn(Common, data=phone))
        """
        phone = request.data.get("phone")
        print(type(phone))
        sms_code = request.data.get("sms_code")
        # 判断用户是否已经注册
        user_obj = User.objects.filter(phone=phone).first()
        if not user_obj:
            # 连接redi
            link_redis = RedisTools()
            # 获取redis中sms_phone的值
            redis_sms_phone = link_redis.redis_conn.get("sms_%s" % phone)
            print(type(redis_sms_phone))
            print(redis_sms_phone)
            # 如果sms_phone不存在
            if not redis_sms_phone:
                return Response(Common.falseReturn(Common, data='验证码已过期'))
            else:
                redis_sms_phone = str(redis_sms_phone, encoding='utf-8')
                # sms_phone存在，判断验证码是否匹配
                if redis_sms_phone != sms_code:
                    # 不匹配
                    return Response(Common.falseReturn(Common, data='验证失败'))
                else:
                    # 匹配
                    add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(str(phone)[5:])
                    # 初始密码手机后6位加密（django哈希加密）
                    password = make_password(str(phone)[5:])
                    print(password)
                    print(len(password))
                    User.objects.create(phone=phone, password=password, add_time=add_time, state_info='0')
                    return Response(Common.tureReturn(Common, data='注册成功'))
        else:
            return Response(Common.falseReturn(Common, data='用户已注册'))


# TODO: 用户手机验证登录
class LoginPhoneView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        sms_code = request.data.get("sms_code")
        # 验证码校验,连接redi
        link_redis = RedisTools()
        # 获取redis中sms_phone的值
        redis_sms_phone = link_redis.redis_conn.get("sms_%s" % phone)
        # 如果sms_phone不存在
        if not redis_sms_phone:
            return Response(Common.falseReturn(Common, data='验证码已过期'))
        else:
            redis_sms_phone = str(redis_sms_phone, encoding='utf-8')
            # sms_phone存在，判断验证码是否匹配
            if redis_sms_phone != sms_code:
                # 不匹配
                return Response(Common.falseReturn(Common, data='验证失败'))
            else:
                # 匹配,判断用户是否已经存在
                user_obj = User.objects.filter(phone=phone).first()
                # 用户不存在
                if not user_obj:
                    add_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    # 初始密码手机后6位加密（django哈希加密）
                    password = make_password(str(phone)[5:])
                    User.objects.create(phone=phone, password=password, add_time=add_time, state_info='0')
                    user_obj = User.objects.filter(phone=phone).first()
                    data = {
                        "pid": user_obj.id,
                        "details": '首次登陆成功'
                    }
                    return Response(Common.tureReturn(Common, data=data))
                # 用户存在
                else:
                    # 修改最后一次登陆时间
                    user_obj.use_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    user_obj.save()
                    if user_obj.state_info == '0':
                        data = {
                            "pid": user_obj.id,
                            "details": '登陆成功,信息未完善'
                        }
                        return Response(Common.tureReturn(Common, data=data))
                    else:
                        data = {
                            "pid": user_obj.id,
                            "details": '登陆成功,信息已完善'
                        }
                        return Response(Common.tureReturn(Common, data=data))

# TODO： 用户密码登录
class LoginPwdView(APIView):
    def post(self, request):
        phone = request.data.get("phone")
        password = request.data.get("password")
        # 查找是否存在该用户
        user_obj = User.objects.filter(phone=phone).first()
        # 存在即验证密码
        if user_obj:
            # 用户存在且密码正确
            if check_password(password, user_obj.password):
                # 修改最后一次登陆时间
                user_obj.use_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                user_obj.save()
                if user_obj.state_info == '0':
                    data = {
                        "pid": user_obj.id,
                        "details": '登陆成功,信息未完善'
                    }
                    return Response(Common.tureReturn(Common, data=data))
                else:
                    data = {
                        "pid": user_obj.id,
                        "details": '登陆成功,信息已完善'
                    }
                    return Response(Common.tureReturn(Common, data=data))
            # 用户存在密码不正确
            else:
                return Response(Common.falseReturn(Common, data='密码有误，登陆失败'))
        # 不存在则提示用户注册
        else:
            return Response(Common.falseReturn(Common, data='用户不存在，登陆失败'))


# TODO: 忘了密码-用户密码修改
class UpdatePwdView(APIView):
    def post(self, request):
        pid = request.data.get("pid")
        sms_code = request.data.get("sms_code")
        new_pwd = request.data.get("new_pwd")
        # 验证码校验,连接redi
        link_redis = RedisTools()
        # 获取redis中sms_phone的值
        redis_sms_phone = link_redis.redis_conn.get("sms_%s" % phone)
        # 如果sms_phone不存在
        if not redis_sms_phone:
            return Response(Common.falseReturn(Common, data='验证码已过期'))
        else:
            redis_sms_phone = str(redis_sms_phone, encoding='utf-8')
            # sms_phone存在，判断验证码是否匹配
            if redis_sms_phone != sms_code:
                # 不匹配
                return Response(Common.falseReturn(Common, data='验证失败'))
            else:
                # 匹配,判断用户是否已经存在
                user_obj = User.objects.filter(id=pid).first()
                # 用户不存在
                if not user_obj:
                    return Response(Common.falseReturn(Common, data='该用户未注册'))
                # 用户存在
                else:
                    # 密码加密
                    password = make_password(new_pwd)
                    # 更改密码
                    user_obj.password = password
                    # 修改最后一次登陆时间
                    user_obj.use_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    user_obj.save()
                    if user_obj.state_info == '0':
                        return Response(Common.tureReturn(Common, data='该用户信息未完善'))
                    else:
                        return Response(Common.tureReturn(Common, data='该用户信息已完善'))


# TODO: 首次登陆完善信息
class EditInfoFirst(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 用户头像
        img_head = request.data.get("img_head")
        # 用户头像后缀
        suffix = request.data.get("suffix")
        # 用户昵称
        nike = request.data.get("nike")
        # 用户性别
        sex = request.data.get("sex")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 头像处理
        if img_head != '' and suffix != '':
            img = ImageParsing(img_head, suffix)
            user_obj.img_head = img
            user_obj.sex = sex
            user_obj.username = nike
            user_obj.state_info = '1'
            res = rc.get_user().register("rc_id_{0}".format(pid), nike, "http://52.80.194.137:8001/dxgm/image/{0}".format(img))
            user_obj.token = res["token"]
            user_obj.save()
            return Response(Common.tureReturn(Common, data='保存成功'))
        else:
            return Response(Common.falseReturn(Common, data='保存失败'))


# TODO: 发布照片至照片墙
class PublishPic(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 照片 [{"base64": "xxx", "type": "jpg"}, ...]
        picture = request.data.get("picture")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        for i in picture:
            if i["base64"] != '' and i["type"]:
                # img = PictureParsing(i["base64"], i["type"])
                img = Parsing(i["base64"], i["type"], WEB_MODEL_BJ_PATH)
            else:
                img = ''
            create_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            BJImage.objects.create(user_id=user_obj.id, image=img, create_time=create_time)
        return Response(Common.tureReturn(Common, data='照片上传成功'))


# TODO: 点击更换头像
class ChangeHeadImg(APIView):
    def put(self, request):
        # 获取用户手机号
        pid = request.data.get("pid")
        # 获取用户头像
        headimg = request.data.get("headimg")
        # 用户头像后缀
        suffix = request.data.get("suffix")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 头像处理
        if headimg != '' and suffix != '':
            img = ImageParsing(headimg, suffix)
            user_obj.img_head = img
            user_obj.save()
            return Response(Common.tureReturn(Common, data='头像更换成功'))
        else:
            return Response(Common.falseReturn(Common, data='头像未更换'))


# TODO: 编辑个人信息
class EditInfo(APIView):
    def post(self, request):
        # print(request.data.get('headimg'))
        pid = request.data.get("pid")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        print(obj)
        nike = request.data.get("nike")
        sex = request.data.get("sex")
        birthday = request.data.get("birthday")
        job = request.data.get("job")
        area = request.data.get("area")
        like = request.data.get("like")
        headimg = request.data.get('headimg')
        print(nike, sex, birthday, job, area, like)
        # print(headimg)
        if birthday != '':
            # 日期str 转 datetime
            birthday = datetime.datetime.strptime(birthday, '%Y-%m-%d %H:%M:%S')
            # 保存用户信息
            obj.born_time = birthday
            # 星座处理
            # datetime 转 str
            birthday = birthday.strftime('%Y-%m-%d')
            # 用-分割学生的出生日期，获取年月日
            birth = datetime.datetime.strptime(birthday, '%Y-%m-%d')
            res = signtools.person_sign(birth.month, birth.day)
            obj.sign = res
            print(obj.sign)
        # 头像处理
        if headimg["base64"] != '' and headimg["type"] != '':
            img = ImageParsing(headimg["base64"], headimg["type"])
            obj.img_head = img
        # 先删除所有与phone的关系
        obj.fan.clear()
        # 可能存在多个爱好
        for i in like:
            # 1.互动聊天  2.美食咖啡  3.唱歌泡吧  4.运动户外  5.电影展览
            # 增加
            obj.fan.add(i)
        obj.username = nike
        obj.sex = sex
        obj.job = job
        obj.area = area
        obj.coin = "2000"
        obj.state_info = '2'
        obj.save()
        print(obj)
        print(obj.sign)
        return Response(Common.tureReturn(Common, data='保存成功'))


# TODO: 获取编辑信息
class GetEditInfo(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        print(pid)
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        img_head = user_obj.img_head
        # http:188.131.183.84/dxgm/picture/
        img_head_url = "http://52.80.194.137:8001/dxgm/image/{0}".format(img_head)
        # 用户昵称
        user_nike = user_obj.username
        # 用户性别
        user_sex = user_obj.sex
        # 用户生日
        user_born = user_obj.born_time
        # datetime 转 str
        user_born = user_born.strftime('%Y-%m-%d')
        # 用户职业
        user_job = user_obj.job
        # 用户地区
        user_area = user_obj.area
        # 喜好
        user_fan = user_obj.fan.all()
        fan_lis = []
        if len(user_fan) > 0:
            for i in user_fan:
                fan_lis.append(i.id)
        data = {
            "img_head_url": img_head_url,
            "user_nike": user_nike,
            "user_sex": user_sex,
            "user_born": user_born,
            "user_job": user_job,
            "user_area": user_area,
            "user_fan": fan_lis,
        }
        print(data)
        return Response(Common.tureReturn(Common, data=data))

# TODO: 个人页(含关注、粉丝、黑名单)
class PersonalPage(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 关注人数
        print(pid)
        print(user_obj)
        focus_num = UserRelation.objects.filter(user_id_id=pid).count()
        print(focus_num)
        # focus_num = 1
        # 粉丝人数
        fans_num = UserRelation.objects.filter(follower_id_id=user_obj.id).count()
        # fans_num = 1
        # 黑名单人数
        blacklist_num = BlackList.objects.filter(third_person_id=user_obj.id).count()
        # blacklist_num = 1
        # datetime 转 str
        user_obj.born_time = user_obj.born_time.strftime('%Y-%m-%d')
        print(user_obj.born_time)
        # 用-分割学生的出生日期，获取年月日
        if user_obj.born_time != '':
            birth = datetime.datetime.strptime(user_obj.born_time, '%Y-%m-%d')
            print(333)
            print(birth)
            # 获取今天的日期
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            # 分割今天的日期获取年月日
            now = datetime.datetime.strptime(now, '%Y-%m-%d')
            print(now.month)
            print(birth.month)
            print(now.day)
            print(birth.day)
            # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
            if now.month < birth.month:
                print(1)
                age = now.year - birth.year - 1
            # 如果学生月份比今天小，他过生日了，则年份相减
            elif now.month > birth.month:
                print(2)
                age = now.year - birth.year
            # 如果月份相等，学生日比今天大，他没过生日
            elif now.month == birth.month and now.day < birth.day:
                print(3)
                age = now.year - birth.year - 1
            # 如果月份相等，学生日比今天小，他过生日了
            else:
                # now.month == birth.month and now.day > birth.day:
                print(4)
                age = now.year - birth.year

        else:
            age = ''
        # 头像
        # print(user_obj.img_head)
        img_head_url = "http://52.80.194.137:8001/dxgm/image/{0}".format(user_obj.img_head)
        print(age)
        data = {
            "username": user_obj.username,
            "sex": user_obj.sex,
            "job": user_obj.job,
            "area": user_obj.area,
            "focus_num": focus_num,
            "sign": user_obj.sign,
            "head_img": img_head_url,
            "age": age,
            "fans_num": fans_num,
            "blacklist_num": blacklist_num,
            "coin": user_obj.coin,
            "token": user_obj.token,
            "face_score": user_obj.face_score,
        }
        print(data)
        return Response(Common.tureReturn(Common, data=data))

# TODO: 关注
class AddFocus(APIView):
    # 添加关注
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.data.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 关注表添加记录
        UserRelation.objects.create(user_id_id=user_obj.id, follower_id_id=id)
        return Response(Common.tureReturn(Common, data='添加关注'))

    # 取消关注
    def delete(self, request):
        # 用户手机号
        pid = request.GET.get("pid")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.GET.get("id")
        print(pid, id)
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 关注表删除记录
        UserRelation.objects.filter(user_id_id=user_obj.id, follower_id_id=id).delete()
        return Response(Common.tureReturn(Common, data='取消关注'))


# TODO: 黑名单
class AddBlackList(APIView):
    # 添加黑名单
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.data.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 将第三人称加入黑名单
        BlackList.objects.create(first_person_id=user_obj.id, third_person_id=id)
        # 第一人称关注第三人称
        i_care = UserRelation.objects.filter(user_id_id=user_obj.id, follower_id_id=id).first()
        # 第一人称被第三人称关注
        be_focused = UserRelation.objects.filter(user_id_id=id, follower_id_id=user_obj.id).first()
        # 加入黑名单即解除双方关注关系
        if i_care and be_focused:
            # 双方关注
            i_care.delete()
            be_focused.delete()
        elif be_focused:
            # 被关注
            be_focused.delete()
        elif i_care:
            # 我关注
            i_care.delete()
        return Response(Common.tureReturn(Common, data='加入黑名单'))


    # 移除黑名单
    def delete(self, request):
        # 用户手机号
        pid = request.GET.get("pid")
        # # 被关注ID 谁发布的活动  发布的时候  记录下id号
        id = request.GET.get("id")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 黑名单表删除记录
        BlackList.objects.filter(first_person_id=user_obj.id, third_person_id=id).delete()
        return Response(Common.tureReturn(Common, data='移除黑名单'))


# TODO: 我的关注
class MyFocus(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取我的关注人员信息
        myfocus_lis = UserRelation.objects.filter(user_id_id=user_obj.id)
        lis = []
        for i in myfocus_lis:
            myfocus_obj = User.objects.filter(id=i.follower_id_id).first()
            print(myfocus_obj)
            # 根据出生年月计算年龄
            # datetime 转 str
            myfocus_obj.born_time = myfocus_obj.born_time.strftime('%Y-%m-%d')
            # 用-分割学生的出生日期，获取年月日
            birth = datetime.datetime.strptime(myfocus_obj.born_time, '%Y-%m-%d')
            # 获取今天的日期
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            # 分割今天的日期获取年月日
            now = datetime.datetime.strptime(now, '%Y-%m-%d')
            # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
            if now.month < birth.month:
                age = now.year-birth.year-1
            # 如果学生月份比今天小，他过生日了，则年份相减
            if now.month > birth.month:
                age = now.year-birth.year
            # 如果月份相等，学生日比今天大，他没过生日
            if now.month == birth.month and now.day < birth.day:
                age = now.year-birth.year-1
            # 如果月份相等，学生日比今天小，他过生日了
            if now.month == birth.month and now.day > birth.day:
                age = now.year-birth.year
            dic = {
                "id": myfocus_obj.id,
                "username": myfocus_obj.username,
                "sex": myfocus_obj.sex,
                "age": age,
                "head_img": "http://52.80.194.137:8001/dxgm/image/{0}".format(myfocus_obj.img_head),
                "job": myfocus_obj.job,
                "focus_state": "已关注"
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 我的粉丝
class MyFans(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取关注我的人员信息
        focusme_lis = UserRelation.objects.filter(follower_id_id=user_obj.id)
        lis = []
        for i in focusme_lis:
            focusme_obj = User.objects.filter(id=i.user_id_id).first()
            # 根据出生年月计算年龄
            # datetime 转 str
            focusme_obj.born_time = focusme_obj.born_time.strftime('%Y-%m-%d')
            # 用-分割学生的出生日期，获取年月日
            birth = datetime.datetime.strptime(focusme_obj.born_time, '%Y-%m-%d')
            # 获取今天的日期
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            # 分割今天的日期获取年月日
            now = datetime.datetime.strptime(now, '%Y-%m-%d')
            # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
            if now.month < birth.month:
                age = now.year - birth.year - 1
            # 如果学生月份比今天小，他过生日了，则年份相减
            if now.month > birth.month:
                age = now.year - birth.year
            # 如果月份相等，学生日比今天大，他没过生日
            if now.month == birth.month and now.day < birth.day:
                age = now.year - birth.year - 1
            # 如果月份相等，学生日比今天小，他过生日了
            if now.month == birth.month and now.day > birth.day:
                age = now.year - birth.year
            # 获取我的粉丝关注状态（关注/互相关注）
            togather = UserRelation.objects.filter(follower_id_id=focusme_obj.id).first()
            if togather:
                focus_state = "互相关注"
            else:
                focus_state = "关注"
            dic = {
                "id": focusme_obj.id,
                "username": focusme_obj.username,
                "sex": focusme_obj.sex,
                "age": age,
                "job": focusme_obj.job,
                "head_img": "http://52.80.194.137:8001/dxgm/image/{0}".format(focusme_obj.img_head),
                "focus_state": focus_state
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 我的黑名单
class MyBlackList(APIView):
    def post(self, request):
        # 用户手机号
        pid = request.data.get("pid")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取我的黑名单人员信息
        black_list = BlackList.objects.filter(first_person_id=user_obj.id)
        lis = []
        for i in black_list:
            black_obj = User.objects.filter(id=i.third_person_id).first()
            # 根据出生年月计算年龄
            # datetime 转 str
            black_obj.born_time = black_obj.born_time.strftime('%Y-%m-%d')
            # 用-分割学生的出生日期，获取年月日
            birth = datetime.datetime.strptime(black_obj.born_time, '%Y-%m-%d')
            # 获取今天的日期
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            # 分割今天的日期获取年月日
            now = datetime.datetime.strptime(now, '%Y-%m-%d')
            # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
            if now.month < birth.month:
                age = now.year - birth.year - 1
            # 如果学生月份比今天小，他过生日了，则年份相减
            if now.month > birth.month:
                age = now.year - birth.year
            # 如果月份相等，学生日比今天大，他没过生日
            if now.month == birth.month and now.day < birth.day:
                age = now.year - birth.year - 1
            # 如果月份相等，学生日比今天小，他过生日了
            if now.month == birth.month and now.day > birth.day:
                age = now.year - birth.year
            dic = {
                "id": black_obj.id,
                "username": black_obj.username,
                "sex": black_obj.sex,
                "age": age,
                "job": black_obj.job,
                "head_img": "http://52.80.194.137:8001/dxgm/image/{0}".format(black_obj.img_head),
                "black_state": "移除"
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))


# # TODO: 条件筛选
# class ConditionFilter(APIView):
#     def get(self, request):
#         # 用户手机号
#         phone = request.data.get("phone")
#         # 获取用户对象
#         user_obj = User.objects.filter(phone=phone).first()
#         # 获取兴趣(['1','2'])
#         like_list = request.data.get("like")
#         sex = request.data.get("sex")
#         person_num = request.data.get("person_num")
#         person_start = request.data.get("person_start")
#         # (['20', '99'])
#         age_list = request.data.get("age_list")
#         face_score_list = request.data.get("face_score_list")
#         time_list = request.data.get("time_list")
#         distance_list = request.data.get("distance_list")


# TODO: 我的车库
class Mycars(APIView):
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
                # 审核状态
                "check_status": i.check_status,
                # 行驶证
                "driver_licence": i.driver_licence,
                # 驾驶证
                "driver_license": i.driver_license
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
        carbarn_obj = CarBarn.objects.last()
        # 获取行驶证
        driver_licence = request.data.get("driver_licence")
        # 用户行驶证后缀
        licence_suffix = request.data.get("licence_suffix")
        if driver_licence != '' and licence_suffix != '':
            img = LicenceParsing(driver_licence, licence_suffix)
            carbarn_obj.driver_licence = img
        # 获取驾驶证
        driver_license = request.data.get("driver_license")
        # 用户驾驶证后缀
        license_suffix = request.data.get("license_suffix")
        if driver_licence != '' and licence_suffix != '':
            img = LicenseParsing(driver_license, license_suffix)
            carbarn_obj.driver_license = img
        # 判断该用户是否已存在驾驶证和行驶证
        carbarn_obj.check_status = '待审核'
        carbarn_obj.save()
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


# TODO: 行驶证上传
class UploadLicence(APIView):
    def put(self, request):
        # 获取用户手机号
        pid = request.data.get("pid")
        # 获取用户行驶证
        licence = request.data.get("licence")
        # 用户行驶证后缀
        suffix = request.data.get("suffix")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 行驶证处理
        if licence != '' and suffix != '':
            img = LicenceParsing(licence, suffix)
            user_obj.driver_licence = img
            user_obj.save()
            return Response(Common.tureReturn(Common, data='行驶证上传成功'))
        else:
            return Response(Common.falseReturn(Common, data='行驶证未上传'))


# TODO: 驾驶证上传
class UploadLicense(APIView):
    def put(self, request):
        # 获取用户手机号
        pid = request.data.get("pid")
        # 获取用户驾驶证
        license = request.data.get("license")
        # 用户驾驶证后缀
        suffix = request.data.get("suffix")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 驾驶证处理
        if license != '' and suffix != '':
            img = LicenseParsing(license, suffix)
            user_obj.driver_license = img
            user_obj.save()
            return Response(Common.tureReturn(Common, data='驾驶证上传成功'))
        else:
            return Response(Common.falseReturn(Common, data='驾驶证未上传'))

# # TODO: 发布邀约
# class IssueInvitation(APIView):
#     def get(self, request):
#         like_list = Like.objects.all()
#         lis = []
#         for i in like_list:
#             lis.append(i.likename)
#         return Response(Common.tureReturn(Common, data=lis))


# TODO: 发布活动点击单人或者多人跳转活动发布页面时话题的读取
class TopicExist(APIView):
    def post(self, request):
        # 获取发布人手机号
        pid = request.data.get("pid")
        # 获取该用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取发布人所发表的话题（最近4条）
        all_topic_list = Topic.objects.filter(topic_user_id=user_obj.id)
        list1 = []
        if len(all_topic_list) >= 4:
            all_topic_list=all_topic_list[-4:]
            for i in all_topic_list:
                list1.append(i.topic_name)
        elif len(all_topic_list) == 3:
            for i in all_topic_list:
                list1.append(i.topic_name)
                list1.extend(["#中国有14亿护旗手"])
        elif len(all_topic_list) == 2:
            for i in all_topic_list:
                list1.append(i.topic_name)
                list1.extend(["#中国有14亿护旗手","#在田子坊的酒吧偶遇"])
        elif len(all_topic_list) == 1:
            for i in all_topic_list:
                list1.append(i.topic_name)
                list1.extend(["#中国有14亿护旗手","#在田子坊的酒吧偶遇","#清吧约一波"])
        else:
            list1.extend(["#中国有14亿护旗手","#在田子坊的酒吧偶遇","#清吧约一波","#KTV麦霸"])
        return Response(Common.tureReturn(Common, data=list1))


# TODO: 唱歌泡吧
class SingingBar(APIView):
    # 活动发布
    def post(self, request):
        # 调用基类
        res = postActivity(request)
        if res != True:
            return Response(Common.tureReturn(Common, data=res))
        else:
            return Response(Common.tureReturn(Common, data='唱歌泡吧活动发布成功'))

    # 活动编辑
    def put(self, request):
        # 调用基类
        pass


# TODO: 互动聊天
class ChatInteraction(APIView):
    # 活动发布
    def post(self, request):
        # 调用基类
        res = postActivity(request)
        if res == False:
            return Response(Common.tureReturn(Common, data='服务状态异常'))
        else:
            return Response(Common.tureReturn(Common, data='互动聊天活动发布成功'))

    # 活动编辑
    def put(self, request):
        # 调用基类
        pass

# TODO: 美食咖啡
class GourmetCoffee(APIView):
    # 活动发布
    def post(self, request):
        # 调用基类
        res = postActivity(request)
        if res == False:
            return Response(Common.tureReturn(Common, data='服务状态异常'))
        else:
            return Response(Common.tureReturn(Common, data='美食咖啡活动发布成功'))


# TODO: 运动户外
class SportsOutdoors(APIView):
    # 活动发布
    def post(self, request):
        # 调用基类
        res = postActivity(request)

        if res == False:
            return Response(Common.tureReturn(Common, data='服务状态异常'))
        else:
            return Response(Common.tureReturn(Common, data='运动户外活动发布成功'))
    
# TODO: 电影展览
class FilmFair(APIView):
    # 活动发布
    def post(self, request):
        # 调用基类
        res = postActivity(request)
        if res == False:
            return Response(Common.tureReturn(Common, data='服务状态异常'))
        else:
            return Response(Common.tureReturn(Common, data='电影展览活动发布成功'))



# TODO: 他的主页
class HisHomePage(APIView):
    def post(self, request):
        # 获取他的id
        his_id = request.data.get("id")
        # 获取我的主键id
        pid = request.data.get("pid")
        # 获取他这个人的对象
        his_obj = User.objects.filter(id=his_id).first()
        # 获取他这个人的图片
        Image_list = BJImage.objects.filter(user_id=his_obj.id)
        # 获取我的关注人员信息
        myfocus_exist = UserRelation.objects.filter(user_id_id=pid, follower_id_id=his_id).first()
        if myfocus_exist:
            focus_status = '0'
        else:
            focus_status = '1'
        # 计算年龄
        # datetime 转 str
        his_obj.born_time = his_obj.born_time.strftime('%Y-%m-%d')
        # 用-分割学生的出生日期，获取年月日
        birth = datetime.datetime.strptime(his_obj.born_time, '%Y-%m-%d')
        # 获取今天的日期
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        # 分割今天的日期获取年月日
        now = datetime.datetime.strptime(now, '%Y-%m-%d')
        # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
        if now.month < birth.month:
            age = now.year - birth.year - 1
        # 如果学生月份比今天小，他过生日了，则年份相减
        if now.month > birth.month:
            age = now.year - birth.year
        # 如果月份相等，学生日比今天大，他没过生日
        if now.month == birth.month and now.day < birth.day:
            age = now.year - birth.year - 1
        # 如果月份相等，学生日比今天小，他过生日了
        if now.month == birth.month and now.day > birth.day:
            age = now.year - birth.year
        # 相册
        list1 = []
        if len(Image_list) > 0:
            for i in Image_list:
                list1.append(i.image)
        # 背景图片
        if len(Image_list) > 0:
            back_img = "http://52.80.194.137:8001/dxgm/bj_picture/{0}".format(Image_list.last().image)
        else:
            back_img = ''
        # 他的邀约 即 他发布的活动
        all_activities = Activity.objects.filter(activity_issue_id=his_id)
        list2 = []
        if len(all_activities) > 0:
            for j in all_activities:
                print(j)
                ac_name = Like.objects.filter(id=j.activity_name_id).first().likename
                to_name = Topic.objects.filter(id=j.topic_name_id).first().topic_name
                dic = {
                    "ac_id": j.id,
                    # 活动话题
                    "ac_name": ac_name,
                    # 活动名称
                    "total": to_name,
                }
                list2.append(dic)
        # 他参与的话题
        top_list = Topic.objects.filter(topic_user_id=his_id)
        list3 = []
        if len(top_list) > 0:
            for z in top_list:
                result = z.topic_join.all()
                if len(result) > 0:
                    list3.append(z.topic_name)
        # 可能出现信息未完善
        data = {
            # 头像
            "img_head": "http://52.80.194.137:8001/dxgm/image/{0}".format(his_obj.img_head),
            # 背景图片(默认最后一张)
            "back_img": back_img,
            # 昵称
            "nike_name": his_obj.username,
            # 关注情况（关注/取消关注）(0代表取消关注）
            "focus_status": focus_status,
            "user_sex": his_obj.sex,
            "user_age": age,
            "user_job": his_obj.job,
            "user_area": his_obj.area,
            "pic_list": list1,
            "ac_invite": list2,
            "topic_list": list3,
            # "userAgent": userAgent
        }
        return Response(Common.tureReturn(Common, data=data))


# TODO: 获取所有车型
class GetAllCarBrand(APIView):
    def get(self, request):
        all_carmodels = CarBrand.objects.all()
        lis = []
        for i in all_carmodels:
            data = {
                "id": i.id,
                "model_name": i.name,
                "model_initial": i.initial,
                "model_imagefilename": "http://52.80.194.137:8001/dxgm/car_logo/{0}".format(i.image_filename),
            }
            lis.append(data)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 根据某一车型获取该车型系列
class GetAllCarSeriseByBrand(APIView):
    def post(self, request):
        car_brand_id = request.data.get("car_brand_id")
        car_series_list = CarSeries.objects.filter(brand_id=car_brand_id)
        lis = []
        for i in car_series_list:
            data = {
                "id": i.id,
                "series_name": i.name
            }
            lis.append(data)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 根据某系列车获取该系列所有车型
class GetAllCarModelBySeries(APIView):
    def post(self, request):
        car_series_id = request.data.get("car_series_id")
        car_model_list = CarModel.objects.filter(series_id=car_series_id)
        lis = []
        for i in car_model_list:
            if i.price == '':
                price = ''
            else:
                price = i.price.split('-')[1]
            data = {
                "id": i.id,
                "model_name": i.name,
                "model_price": price,
            }
            lis.append(data)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 邀请他参与我的话题-获取话题列表
class InviteTopic(APIView):
    def post(self, request):
        # 获取我的主键id
        pid = request.data.get("pid")
        # user_obj = User.objects.filter(id=pid).first()
        # 获取我的话题列表
        topic_list = Topic.objects.filter(topic_user_id=pid)
        lis1 = []
        if len(topic_list) > 0:

            for i in topic_list:
                dic = {
                    "id": i.id,
                    "topic_name": i.topic_name
                }
                lis1.append(dic)
        return Response(Common.tureReturn(Common, data=lis1))


# # TODO: 邀请他参与我的活动-获取活动列表
# class InviteTopic(APIView):
#     def post(self, request):
#         # 获取我的主键id
#         pid = request.data.get("pid")
#         # user_obj = User.objects.filter(id=pid).first()
#         # 获取我的话题列表
#         topic_list = Topic.objects.filter(topic_user_id=pid)
#         lis1 = []
#         if len(topic_list) > 0:
#
#             for i in topic_list:
#                 dic = {
#                     "id": i.id,
#                     "topic_name": i.topic_name
#                 }
#                 lis1.append(dic)
#         return Response(Common.tureReturn(Common, data=lis1))


# TODO: 邀请他参与我的活动
class InviteActivity(APIView):
    def post(self, request):
        # 获取我的主键id
        pid = request.data.get("pid")
        p_obj = User.objects.filter(id=pid).first()
        # 获取对方主键id
        hid = request.data.get("hid")
        h_obj = User.objects.filter(id=hid).first()
        # 获取活动id
        activity_id = request.data.get("activity_id")
        ac_obj = Activity.objects.filter(id=activity_id).first()
        # 根据id对象
        tp_obj = Topic.objects.filter(id=ac_obj.topic_name_id).first()
        if p_obj.sex == '1':
            content = "{0}邀请你参加他的活动-{1}".format(p_obj.username, tp_obj.topic_name)
        else:
            content = "{0}邀请你参加她的活动-{1}".format(p_obj.username, tp_obj.topic_name)
        content = {'content': content, 'extra': ''}
        rep = rc.get_message().get_private().send(from_user_id='rc_id_{0}'.format(pid),
                                                  to_user_ids='rc_id_{0}'.format(hid),
                                                  object_name='RC:TxtMsg', content=content)
        return Response(Common.tureReturn(Common, data=rep))


# TODO: 判断信息是否已全部完善
class JudgeState(APIView):
    def get(self, request):
        # 用户id
        pid = request.GET.get("pid")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        # 判断状态
        if obj.state_info == "2":
            return Response(Common.tureReturn(Common, data=True))
        else:
            return Response(Common.tureReturn(Common, data=False))


# TODO: 点数查询
class ReduceCoin(APIView):
    def post(self, request):
        # 用户id
        pid = request.data.get("pid")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        # 判断点数是否充足
        return Response(Common.tureReturn(Common, data=obj.coin))


# TODO: 个人活动列表
class ActivityPaging(APIView):
    def post(self, request):
        # 用户id
        pid = request.data.get("pid")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        # 获取该用户相关活动
        all_activity_objects = Activity.objects.filter(activity_issue_id=obj.id)

        #
        # # 图片数量
        # pic_num = Image.objects.filter(activity_id=obj.id).count()
        # # 图片列表
        # pic_obj_list = Image.objects.filter(activity_id=obj.id)
        # pic_list = []
        # if len(pic_obj_list) > 0:
        #     for i in pic_obj_list:
        #         img_url = "http://52.80.194.137:8001/dxgm/picture/{0}".format(i.image),
        #         pic_list.append(img_url)


        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=all_activity_objects, request=request, view=self)
        # 实例化对象
        ser = ActivitySerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            # 活动时间日期
            i["activity_create_time"] = i["activity_create_time"].replace('T', ' ').split('.')[0]
            activity_create_time = i["activity_create_time"].split(' ')[0].replace('-', '/')
            # 活动图片
            # 图片数量
            pic_num = Image.objects.filter(activity_id=i["id"]).count()
            # 图片列表
            pic_obj_list = Image.objects.filter(activity_id=i["id"])
            pic_list = []
            if len(pic_obj_list) > 0:
                for i1 in pic_obj_list:
                    img_url = "http://52.80.194.137:8001/dxgm/picture/{0}".format(i1.image),
                    pic_list.append(img_url)


            # 活动话题
            topic_obj = Topic.objects.filter(id=i["topic_name"]).first()
            # datetime 转 str
            # 活动时间日期
            i["activity_time"] = i["activity_time"].replace('T', ' ').split('.')[0]
            activity_time = i["activity_time"].split(' ')[0]
            # # 日期str 转 datetime
            birthday = datetime.datetime.strptime(i["activity_time"], '%Y-%m-%d %H:%M:%S')
            # 格式化datetime为%Y-%m-%d %H:%M:%S （datetime==> str）
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # str ==> datetime
            now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
            # 距开始还有多少秒
            # print(birthday-now_time)
            a = time.mktime(birthday.timetuple())
            b = time.mktime(now_time.timetuple())
            seconds = int(a) - int(b)
            # seconds = (birthday-now_time).seconds
            # 如果差距大于一小时
            if seconds > 0:
                # 差值大于一天86400
                if seconds > 86400:
                    day = seconds//86400
                    if day > 30:
                        month = seconds//2592000
                        stime = "{0}个月".format(month)
                    elif day > 15:
                        stime = "半个月"
                    else:
                        stime = "{0}天".format(day)
                else:
                    # 一天之内
                    seconds = seconds%86400
                    if seconds > 3600:
                        hour = seconds//3600
                        stime = "{0}小时".format(hour)
                    else:
                        # 一小时之内
                        minute = seconds%3600
                        if minute > 60:
                            minute = minute//60
                            stime = "{0}分钟".format(minute)
                        else:
                            stime = "即将开始"
            else:
                seconds = int(b) - int(a)
                # 差值大于一天86400
                if seconds > 86400:
                    day = seconds//86400
                    if day > 30:
                        month = seconds//2592000
                        stime = "{0}个月前".format(month)
                    elif day > 15:
                        stime = "半个月前"
                    else:
                        stime = "{0}天前".format(day)
                else:
                    # 一天之内
                    seconds = seconds%86400
                    if seconds > 3600:
                        hour = seconds//3600
                        stime = "{0}小时前".format(hour)
                    else:
                        # 一小时之内
                        minute = seconds%3600
                        if minute > 60:
                            minute = minute//60
                            stime = "{0}分钟前".format(minute)
                        else:
                            stime = "已开始"
            # 获取车库中的车
            carbarn_obj = CarBarn.objects.filter(id=i["activity_car"]).first()
            # 获取车对象
            carmodel_obj = CarModel.objects.filter(id=carbarn_obj.car_model_id).first()
            # 活动名称
            like_obj = Like.objects.filter(id=i["activity_name"]).first()
            dic = {
                # 人头像
                "head_img": "http://52.80.194.137:8001/dxgm/image/{0}".format(obj.img_head),
                # 姓名
                "nikename": obj.username,
                # 职业
                "job": obj.job,
                # 性别
                "sex": obj.sex,
                # 图片数量
                "pic_num": pic_num,
                # 图片地址
                "pic_list": pic_list,
                # 开始距当前活动还剩多少时间
                "start_time": stime,
                # 车型
                "car_model_name": carmodel_obj.name,
                # 活动名称
                "activity_name": like_obj.likename,
                # 活动主键
                "id": i["id"],
                # 活动类型种类(单人/多人)
                "activity_kind": i["activity_kind"],
                # 活动出发地
                "activity_area_start": i["activity_area_start"],
                # 活动目的地
                "activity_area_end": i["activity_area_end"],
                # 活动时间
                "activity_time": activity_time,
                # 活动话题
                "topic_name": topic_obj.topic_name,
                # 活动参与人群性别
                "activity_person_sex": i["activity_person_sex"],
                # 活动内容-说说你的想法
                "activity_content": i["activity_content"],
                # 起始经度
                "longitude_start": i["longitude_start"],
                # 起始纬度
                "latitude_start": i["latitude_start"],
                # 终点经度
                "longitude_end": i["longitude_end"],
                # 终点纬度
                "latitude_end": i["latitude_end"],
                # 发布时间
                "activity_create_time": activity_create_time
            }
            lis.append(dic)
        if len(lis) > 0:
            lis[0]["number"] = all_activity_objects.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 活动首页列表(排除自己和未开始的活动)
class ActivityIndex(APIView):
    def post(self, request):
        pid = request.data.get("pid")
        # 获取现在的时间
        now = datetime.datetime.now()
        # 获取该用户相关活动
        # all_activity_objects = Activity.objects.exclude(activity_issue_id=pid).filter(activity_time__gt=now)
        all_activity_objects = Activity.objects.filter(activity_time__gt=now)
        lis = []
        if all_activity_objects:
            # all_activity_objects = Activity.objects.all()
            # 实例化分页对象, 获取数据库中的分页数据
            pagination_class = MyPageNumberPagination()
            page_list = pagination_class.paginate_queryset(queryset=all_activity_objects, request=request, view=self)
            # 实例化对象
            ser = ActivitySerializer(instance=page_list, many=True)  # 可允许多个

            for i in ser.data:
                # 获取用户对象
                obj = User.objects.filter(id=i["activity_issue"]).first()

                # datetime 转 str
                obj.born_time = obj.born_time.strftime('%Y-%m-%d')
                # 用-分割学生的出生日期，获取年月日
                if obj.born_time != '':
                    birth = datetime.datetime.strptime(obj.born_time, '%Y-%m-%d')
                    # 获取今天的日期
                    now = datetime.datetime.now().strftime('%Y-%m-%d')
                    # 分割今天的日期获取年月日
                    now = datetime.datetime.strptime(now, '%Y-%m-%d')
                    # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
                    if now.month < birth.month:
                        age = now.year - birth.year - 1
                    # 如果学生月份比今天小，他过生日了，则年份相减
                    if now.month > birth.month:
                        age = now.year - birth.year
                    # 如果月份相等，学生日比今天大，他没过生日
                    if now.month == birth.month and now.day < birth.day:
                        age = now.year - birth.year - 1
                    # 如果月份相等，学生日比今天小，他过生日了
                    if now.month == birth.month and now.day > birth.day:
                        age = now.year - birth.year
                else:
                    age = ''

                # 图片列表
                pic_obj_list = Image.objects.filter(activity_id=i["id"])
                pic_list = []
                if len(pic_obj_list) > 0:
                    for j in pic_obj_list:
                        img_url = "http://52.80.194.137:8001/dxgm/picture/{0}".format(j.image)
                        pic_list.append(img_url)
                # 图片数量
                pic_num = len(pic_obj_list)
                # 活动话题
                topic_obj = Topic.objects.filter(id=i["topic_name"]).first()
                # datetime 转 str
                # 活动时间日期
                i["activity_time"] = i["activity_time"].replace('T', ' ').split('.')[0]
                activity_time = i["activity_time"].split(' ')[0]
                # # 日期str 转 datetime
                birthday = datetime.datetime.strptime(i["activity_time"], '%Y-%m-%d %H:%M:%S')
                # 格式化datetime为%Y-%m-%d %H:%M:%S （datetime==> str）
                now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # str ==> datetime
                now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
                # 距开始还有多少秒
                # print(birthday-now_time)
                a = time.mktime(birthday.timetuple())
                b = time.mktime(now_time.timetuple())
                seconds = int(a) - int(b)
                # 如果差距大于一小时
                # 差值大于一天86400
                if seconds > 86400:
                    day = seconds//86400
                    if day > 30:
                        month = seconds//2592000
                        stime = "{0}个月".format(month)
                    elif day > 15:
                        stime = "半个月"
                    else:
                        stime = "{0}天".format(day)
                else:
                    # 一天之内
                    seconds = seconds%86400
                    if seconds > 3600:
                        hour = seconds//3600
                        stime = "{0}小时".format(hour)
                    else:
                        # 一小时之内
                        minute = seconds%3600
                        if minute > 60:
                            minute = minute//60
                            stime = "{0}分钟".format(minute)
                        else:
                            stime = "即将开始"
                # 获取车库中的车
                carbarn_obj = CarBarn.objects.filter(id=i["activity_car"]).first()
                # 获取车对象
                carmodel_obj = CarModel.objects.filter(id=carbarn_obj.car_model_id).first()
                # 活动名称
                like_obj = Like.objects.filter(id=i["activity_name"]).first()
                dic = {
                    "pid": obj.id,
                    # 人头像
                    "head_img": "http://52.80.194.137:8001/dxgm/image/{0}".format(obj.img_head),
                    # 姓名
                    "nikename": obj.username,
                    # 职业
                    "job": obj.job,
                    # 性别
                    "sex": obj.sex,
                    # 图片数量
                    "pic_num": pic_num,
                    # 图片地址
                    "pic_list": pic_list,
                    # 开始距当前活动还剩多少时间
                    "start_time": stime,
                    # 车型
                    "car_model_name": carmodel_obj.name,
                    # 活动名称
                    "activity_name": like_obj.likename,
                    # 活动主键
                    "id": i["id"],
                    # 活动类型种类(单人/多人)
                    "activity_kind": i["activity_kind"],
                    # 活动出发地
                    "activity_area_start": i["activity_area_start"],
                    # 活动目的地
                    "activity_area_end": i["activity_area_end"],
                    # 活动时间
                    "activity_time": activity_time,
                    # 活动话题
                    "topic_name": topic_obj.topic_name,
                    # 活动参与人群性别
                    "activity_person_sex": i["activity_person_sex"],
                    # 活动内容-说说你的想法
                    "activity_content": i["activity_content"],
                    # 起始经度
                    "longitude_start": i["longitude_start"],
                    # 起始纬度
                    "latitude_start": i["latitude_start"],
                    # 终点经度
                    "longitude_end": i["longitude_end"],
                    # 终点纬度
                    "latitude_end": i["latitude_end"],
                    # 年龄
                    "age": age
                }
                lis.append(dic)
        if len(lis) > 0:
            lis[0]["number"] = all_activity_objects.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 条件筛选
class ConditionFilter(APIView):

    def cal_dis(self, lat1, lon1, lat2, lon2):
        latitude1 = (math.pi / 180) * lat1
        latitude2 = (math.pi / 180) * lat2
        longitude1 = (math.pi / 180) * lon1
        longitude2 = (math.pi / 180) * lon2
        # 因此AB两点的球面距离为:{arccos[sinb*siny+cosb*cosy*cos(a-x)]}*R
        # 地球半径
        R = 6378.137;
        d = math.acos(math.sin(latitude1) * math.sin(latitude2) + math.cos(latitude1) * math.cos(latitude2) * math.cos(
            longitude2 - longitude1)) * R
        return d

    def post(self, request):
        cf = ConditionFilter()
        # pid = request.data.get("pid")
        jindu = request.data.get("jindu")
        weidu = request.data.get("weidu")
        like_lis = request.data.get("like_lis")
        sex = request.data.get("sex")
        num = request.data.get("num")
        start = request.data.get("start")
        age_lis = request.data.get("age_lis")
        facescore_lis = request.data.get("facescore_lis")
        time_lis = request.data.get("time_lis")
        distance_lis = request.data.get("distance_lis")
        # str 转 datetime
        time_less = datetime.datetime.strptime(time_lis[0], '%Y-%m-%d %H:%M:%S')
        time_than = datetime.datetime.strptime(time_lis[1], '%Y-%m-%d %H:%M:%S')

        # 筛选兴趣
        like_list1 = []
        list1 = []
        for z in like_lis:
            like_obj_lis = Activity.objects.filter(activity_name_id=z)
            for ii in like_obj_lis:
                like_list1.append(ii)
        for i in like_list1:
            # 根据兴趣匹配活动发布人
            user_obj = User.objects.filter(id=i.activity_issue_id).first()
            # 计算年龄
            # datetime 转 str
            user_obj.born_time = user_obj.born_time.strftime('%Y-%m-%d')
            # 用-分割学生的出生日期，获取年月日
            birth = datetime.datetime.strptime(user_obj.born_time, '%Y-%m-%d')
            # 获取今天的日期
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            # 分割今天的日期获取年月日
            now = datetime.datetime.strptime(now, '%Y-%m-%d')
            # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
            if now.month < birth.month:
                age = now.year - birth.year - 1
            # 如果学生月份比今天小，他过生日了，则年份相减
            if now.month > birth.month:
                age = now.year - birth.year
            # 如果月份相等，学生日比今天大，他没过生日
            if now.month == birth.month and now.day < birth.day:
                age = now.year - birth.year - 1
            # 如果月份相等，学生日比今天小，他过生日了
            if now.month == birth.month and now.day > birth.day:
                age = now.year - birth.year
            # 首先判断发布人的星座、年龄和颜值是否符合
            if user_obj.sign == start or start == '不限' and int(user_obj.face_score) >= int(facescore_lis[
                0]) and int(user_obj.face_score) < int(facescore_lis[1]) and int(age) >= int(age_lis[0]) and int(age) <= int(age_lis[1]):
                # 符合后筛选活动条件
                ac_obj_lis = Activity.objects.filter(activity_person_sex=sex, activity_kind=num,
                                                     activity_time__gt=time_less,
                                                     activity_time__lt=time_than)
        for j in ac_obj_lis:
            dis = cf.cal_dis(float(j.latitude_start), float(j.longitude_start), float(jindu), float(weidu))
            if dis*1000 >= float(distance_lis[0]) and dis*1000 <= float(distance_lis[1]):
                list1.append(j)
        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=list1, request=request,
                                                       view=self)
        # 实例化对象
        ser = ActivitySerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            # 获取用户对象
            obj = User.objects.filter(id=i["activity_issue"]).first()
            # datetime 转 str
            obj.born_time = obj.born_time.strftime('%Y-%m-%d')
            # 用-分割学生的出生日期，获取年月日
            if obj.born_time != '':
                birth = datetime.datetime.strptime(obj.born_time, '%Y-%m-%d')
                # 获取今天的日期
                now = datetime.datetime.now().strftime('%Y-%m-%d')
                # 分割今天的日期获取年月日
                now = datetime.datetime.strptime(now, '%Y-%m-%d')
                # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
                if now.month < birth.month:
                    age = now.year - birth.year - 1
                # 如果学生月份比今天小，他过生日了，则年份相减
                if now.month > birth.month:
                    age = now.year - birth.year
                # 如果月份相等，学生日比今天大，他没过生日
                if now.month == birth.month and now.day < birth.day:
                    age = now.year - birth.year - 1
                # 如果月份相等，学生日比今天小，他过生日了
                if now.month == birth.month and now.day > birth.day:
                    age = now.year - birth.year
            else:
                age = ''
            # 图片列表
            pic_obj_list = Image.objects.filter(activity_id=i["id"])
            pic_list = []
            if len(pic_obj_list) > 0:
                for j in pic_obj_list:
                    img_url = "http://52.80.194.137:8001/dxgm/picture/{0}".format(j.image)
                    pic_list.append(img_url)
            # 图片数量
            pic_num = len(pic_obj_list)
            # 活动话题
            topic_obj = Topic.objects.filter(id=i["topic_name"]).first()
            # datetime 转 str
            # 活动时间日期
            i["activity_time"] = i["activity_time"].replace('T', ' ').split('.')[0]
            activity_time = i["activity_time"].split(' ')[0]
            # # 日期str 转 datetime
            birthday = datetime.datetime.strptime(i["activity_time"], '%Y-%m-%d %H:%M:%S')
            # 格式化datetime为%Y-%m-%d %H:%M:%S （datetime==> str）
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # str ==> datetime
            now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
            # 距开始还有多少秒
            # print(birthday-now_time)
            a = time.mktime(birthday.timetuple())
            b = time.mktime(now_time.timetuple())
            seconds = int(a) - int(b)
            # 如果差距大于一小时
            # 差值大于一天86400
            if seconds > 86400:
                day = seconds // 86400
                if day > 30:
                    month = seconds // 2592000
                    stime = "{0}个月".format(month)
                elif day > 15:
                    stime = "半个月"
                else:
                    stime = "{0}天".format(day)
            else:
                # 一天之内
                seconds = seconds % 86400
                if seconds > 3600:
                    hour = seconds // 3600
                    stime = "{0}小时".format(hour)
                else:
                    # 一小时之内
                    minute = seconds % 3600
                    if minute > 60:
                        minute = minute // 60
                        stime = "{0}分钟".format(minute)
                    else:
                        stime = "即将开始"
            # 获取车库中的车
            carbarn_obj = CarBarn.objects.filter(id=i["activity_car"]).first()
            # 获取车对象
            carmodel_obj = CarModel.objects.filter(id=carbarn_obj.car_model_id).first()
            # 活动名称
            like_obj = Like.objects.filter(id=i["activity_name"]).first()
            dic = {
                # 人头像
                "head_img": "http://52.80.194.137:8001/dxgm/image/{0}".format(obj.img_head),
                # 姓名
                "nikename": obj.username,
                # 职业
                "job": obj.job,
                # 性别
                "sex": obj.sex,
                # 图片数量
                "pic_num": pic_num,
                # 图片地址
                "pic_list": pic_list,
                # 开始距当前活动还剩多少时间
                "start_time": stime,
                # 车型
                "car_model_name": carmodel_obj.name,
                # 活动名称
                "activity_name": like_obj.likename,
                # 活动主键
                "id": i["id"],
                # 活动类型种类(单人/多人)
                "activity_kind": i["activity_kind"],
                # 活动出发地
                "activity_area_start": i["activity_area_start"],
                # 活动目的地
                "activity_area_end": i["activity_area_end"],
                # 活动时间
                "activity_time": activity_time,
                # 活动话题
                "topic_name": topic_obj.topic_name,
                # 活动参与人群性别
                "activity_person_sex": i["activity_person_sex"],
                # 活动内容-说说你的想法
                "activity_content": i["activity_content"],
                # 起始经度
                "longitude_start": i["longitude_start"],
                # 起始纬度
                "latitude_start": i["latitude_start"],
                # 终点经度
                "longitude_end": i["longitude_end"],
                # 终点纬度
                "latitude_end": i["latitude_end"],
                # 年龄
                "age": age
            }
            lis.append(dic)
        if len(lis) > 0:
            lis[0]["number"] = len(list1)
        return Response(Common.tureReturn(Common, data=lis))

# TODO: 根据活动id查询
class QueryActivity(APIView):
    def post(self, request):
        # 用户id
        pid = request.data.get("pid")
        # 活动id
        ac_id = request.data.get("ac_id")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        # 获取该活动
        ac_obj = Activity.objects.filter(id=ac_id).first()
        # datetime 转 str
        obj.born_time = obj.born_time.strftime('%Y-%m-%d')
        # 用-分割学生的出生日期，获取年月日
        if obj.born_time != '':
            birth = datetime.datetime.strptime(obj.born_time, '%Y-%m-%d')
            # 获取今天的日期
            now = datetime.datetime.now().strftime('%Y-%m-%d')
            # 分割今天的日期获取年月日
            now = datetime.datetime.strptime(now, '%Y-%m-%d')
            # 如果学生月份比今天大，他肯定没过生日，则年份相减在减去1
            if now.month < birth.month:
                age = now.year - birth.year - 1
            # 如果学生月份比今天小，他过生日了，则年份相减
            if now.month > birth.month:
                age = now.year - birth.year
            # 如果月份相等，学生日比今天大，他没过生日
            if now.month == birth.month and now.day < birth.day:
                age = now.year - birth.year - 1
            # 如果月份相等，学生日比今天小，他过生日了
            if now.month == birth.month and now.day > birth.day:
                age = now.year - birth.year
        else:
            age = ''
        lis = []
        # 活动时间日期
        print("22")
        print(type(ac_obj.activity_create_time))
        # datetime 转 str
        ac_obj.activity_create_time = ac_obj.activity_create_time.strftime('%Y-%m-%d %H:%M:%S')
        # ac_obj.activity_create_time = ac_obj.activity_create_time.replace('T', ' ').split('.')[0]
        activity_create_time = ac_obj.activity_create_time.split(' ')[0].replace('-', '/')
        # 活动图片
        # 图片数量
        pic_num = Image.objects.filter(activity_id=ac_obj.id).count()
        # 图片列表
        pic_obj_list = Image.objects.filter(activity_id=ac_obj.id)
        pic_list = []
        if len(pic_obj_list) > 0:
            for i1 in pic_obj_list:
                img_url = "http://52.80.194.137:8001/dxgm/picture/{0}".format(i1.image),
                pic_list.append(img_url)
        # 活动话题
        topic_obj = Topic.objects.filter(id=ac_obj.topic_name_id).first()

        print(ac_obj.activity_time)
        # 活动时间日期
        ac_obj.activity_time = ac_obj.activity_time.strftime('%Y-%m-%d %H:%M:%S')
        # ac_obj.activity_time = ac_obj.activity_time.replace('T', ' ').split('.')[0]
        activity_time = ac_obj.activity_time.split(' ')[0]
        # # 日期str 转 datetime
        birthday = datetime.datetime.strptime(ac_obj.activity_time, '%Y-%m-%d %H:%M:%S')
        # 格式化datetime为%Y-%m-%d %H:%M:%S （datetime==> str）
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # str ==> datetime
        now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
        # 距开始还有多少秒
        # print(birthday-now_time)
        a = time.mktime(birthday.timetuple())
        b = time.mktime(now_time.timetuple())
        seconds = int(a) - int(b)
        # seconds = (birthday-now_time).seconds
        # 如果差距大于一小时
        if seconds > 0:
            # 差值大于一天86400
            if seconds > 86400:
                day = seconds//86400
                if day > 30:
                    month = seconds//2592000
                    stime = "{0}个月".format(month)
                elif day > 15:
                    stime = "半个月"
                else:
                    stime = "{0}天".format(day)
            else:
                # 一天之内
                seconds = seconds%86400
                if seconds > 3600:
                    hour = seconds//3600
                    stime = "{0}小时".format(hour)
                else:
                    # 一小时之内
                    minute = seconds%3600
                    if minute > 60:
                        minute = minute//60
                        stime = "{0}分钟".format(minute)
                    else:
                        stime = "即将开始"
        else:
            seconds = int(b) - int(a)
            # 差值大于一天86400
            if seconds > 86400:
                day = seconds//86400
                if day > 30:
                    month = seconds//2592000
                    stime = "{0}个月前".format(month)
                elif day > 15:
                    stime = "半个月前"
                else:
                    stime = "{0}天前".format(day)
            else:
                # 一天之内
                seconds = seconds%86400
                if seconds > 3600:
                    hour = seconds//3600
                    stime = "{0}小时前".format(hour)
                else:
                    # 一小时之内
                    minute = seconds%3600
                    if minute > 60:
                        minute = minute//60
                        stime = "{0}分钟前".format(minute)
                    else:
                        stime = "已开始"
        # 获取车库中的车
        carbarn_obj = CarBarn.objects.filter(id=ac_obj.activity_car_id).first()
        # 获取车对象
        carmodel_obj = CarModel.objects.filter(id=carbarn_obj.car_model_id).first()
        # 活动名称
        like_obj = Like.objects.filter(id=ac_obj.activity_name_id).first()
        dic = {
            # 人头像
            "head_img": "http://52.80.194.137:8001/dxgm/image/{0}".format(obj.img_head),
            # 姓名
            "nikename": obj.username,
            # 职业
            "job": obj.job,
            # 性别
            "sex": obj.sex,
            # 图片数量
            "pic_num": pic_num,
            # 图片地址
            "pic_list": pic_list,
            # 开始距当前活动还剩多少时间
            "start_time": stime,
            # 车型
            "car_model_name": carmodel_obj.name,
            # 活动名称
            "activity_name": like_obj.likename,
            # 活动主键
            "id": ac_obj.id,
            # 活动类型种类(单人/多人)
            "activity_kind": ac_obj.activity_kind,
            # 活动出发地
            "activity_area_start": ac_obj.activity_area_start,
            # 活动目的地
            "activity_area_end": ac_obj.activity_area_end,
            # 活动时间
            "activity_time": activity_time,
            # 活动话题
            "topic_name": topic_obj.topic_name,
            # 活动参与人群性别
            "activity_person_sex": ac_obj.activity_person_sex,
            # 活动内容-说说你的想法
            "activity_content": ac_obj.activity_content,
            # 起始经度
            "longitude_start": ac_obj.longitude_start,
            # 起始纬度
            "latitude_start": ac_obj.latitude_start,
            # 终点经度
            "longitude_end": ac_obj.longitude_end,
            # 终点纬度
            "latitude_end": ac_obj.latitude_end,
            # 发布时间
            "activity_create_time": activity_create_time,
            # 年龄
            "age": age
        }
        lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))


# 发布之前判断车库是否有通过审核且信息全部完善
class Check_ok(APIView):
    def get(self, request):
        # 用户手机号
        pid = request.GET.get("pid")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        print(user_obj)
        # 获取用户车库
        carbarn_list = CarBarn.objects.filter(car_person_id=user_obj.id)
        print(carbarn_list)
        list1 = []
        for i in carbarn_list:
            if i.check_status == '1':
                list1.append(i)
        # print(user_obj)
        if user_obj.state_info == '2':
            if len(list1) == 0:
                # return Response(Common.tureReturn(Common, data='车库无符合车辆'))
                return Response(Common.falseReturn(Common, data='1'))
            else:
                # return Response(Common.tureReturn(Common, data='可发布'))
                return Response(Common.falseReturn(Common, data='2'))
        else:
            # return Response(Common.tureReturn(Common, data='用户信息未完善'))
            return Response(Common.falseReturn(Common, data='0'))


# 获取审核通过的车
class Check_car_ok(APIView):
    def get(self, request):
        # 用户手机号
        pid = request.GET.get("pid")
        # 获取用户对象
        user_obj = User.objects.filter(id=pid).first()
        # 获取用户车库
        carbarn_list = CarBarn.objects.filter(car_person_id=user_obj.id)
        list1 = []
        for i in carbarn_list:
            if i.check_status == '1':
                list1.append(i)
        lis = []
        for i in list1:
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
                # 审核状态
                "check_status": i.check_status,
                # 行驶证
                "driver_licence": i.driver_licence,
                # 驾驶证
                "driver_license": i.driver_license
            }
            lis.append(dic)
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 活动--我感兴趣
class ActivityInterst(APIView):
    def post(self, request):
        # 获取自己id
        m_id = request.data.get("m_id")
        # 获取用户对象
        m_obj = User.objects.filter(id=m_id).first()
        # 获取活动发布者id
        h_id = request.data.get("h_id")
        # 获取用户对象
        h_obj = User.objects.filter(id=h_id).first()
        # 获取活动主页id
        ac_id = request.data.get("ac_id")
        # 获取活动对象
        ac_obj = Activity.objects.filter(id=ac_id).first()
        # 查询是否已加入活动
        all_join = ac_obj.activity_join.all()
        join_list = []
        for j in all_join:
            join_list.append(j.id)
        if m_id not in join_list:
            # 加入活动
            ac_obj.activity_join.add(m_id)
            try:
                # 获取群组
                # group_info = rc.get_group().query(group_id='group_id_{0}'.format(ac_id))
                user_list = []
                # for i in group_info["users"]:
                #     user_list.append(i["id"])
                # 加入聊天室
                user_list.append('rc_id_{0}'.format(m_id))
                # user_list.append('rc_id_33333')
                # print('user_list',user_list)
                # print('group_id_{0}'.format(ac_id))
                result = rc.get_group().join(user_ids=user_list,
                                          group_id='group_id_{0}'.format(ac_id),
                                          group_name='{0}'.format(h_obj.username))
                # print(1012)
                # print(result)
                # 发送群组消息
                txt = "大家好,我是{0}，我对这个活动非常感兴趣，希望进一步了解。".format(m_obj.username)
                content = {'content': txt, 'extra': ''}
                rc.get_message().get_group().send(from_user_id='rc_id_{0}'.format(m_id),
                                                          to_group_id='group_id_{0}'.format(ac_id),
                                                          object_name='RC:TxtMsg', content=content)
                return Response(Common.tureReturn(Common, data='ok'))
            except Exception as e:
                print(e)
                return Response(Common.tureReturn(Common, data='服务状态异常'))
        else:
            return Response(Common.tureReturn(Common, data='活动已存在'))


# TODO: 密码修改
class UpdatePwd(APIView):
    def post(self, request):
        # 获取用户id
        pid = request.data.get("pid")
        # 获取手机号
        pwd = request.data.get("pwd")
        user_obj = User.objects.filter(id=pid).first()
        # 密码加密
        password = make_password(pwd)
        # 更改密码
        user_obj.password = password
        return Response(Common.tureReturn(Common, data='密码修改成功'))


# TODO: 我参与的
class TakePart(APIView):
    def post(self, request):
        # 用户id
        pid = request.data.get("pid")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        print(obj)
        # 获取该用户相关活动
        all_activity_objects = obj.sample6.all()
        print(all_activity_objects)
        # for j in all_activity_objects:

        #
        # # 图片数量
        # pic_num = Image.objects.filter(activity_id=obj.id).count()
        # # 图片列表
        # pic_obj_list = Image.objects.filter(activity_id=obj.id)
        # pic_list = []
        # if len(pic_obj_list) > 0:
        #     for i in pic_obj_list:
        #         img_url = "http://52.80.194.137:8001/dxgm/picture/{0}".format(i.image),
        #         pic_list.append(img_url)

        # 实例化分页对象, 获取数据库中的分页数据
        pagination_class = MyPageNumberPagination()
        page_list = pagination_class.paginate_queryset(queryset=all_activity_objects, request=request, view=self)
        # 实例化对象
        ser = ActivitySerializer(instance=page_list, many=True)  # 可允许多个
        lis = []
        for i in ser.data:
            # 活动时间日期
            i["activity_create_time"] = i["activity_create_time"].replace('T', ' ').split('.')[0]
            activity_create_time = i["activity_create_time"].split(' ')[0].replace('-', '/')
            # 活动图片
            # 图片数量
            pic_num = Image.objects.filter(activity_id=i["id"]).count()
            # 图片列表
            pic_obj_list = Image.objects.filter(activity_id=i["id"])
            pic_list = []
            if len(pic_obj_list) > 0:
                for i1 in pic_obj_list:
                    img_url = "http://52.80.194.137:8001/dxgm/picture/{0}".format(i1.image),
                    pic_list.append(img_url)

            # 活动话题
            topic_obj = Topic.objects.filter(id=i["topic_name"]).first()
            # datetime 转 str
            # 活动时间日期
            i["activity_time"] = i["activity_time"].replace('T', ' ').split('.')[0]
            activity_time = i["activity_time"].split(' ')[0]
            # # 日期str 转 datetime
            birthday = datetime.datetime.strptime(i["activity_time"], '%Y-%m-%d %H:%M:%S')
            # 格式化datetime为%Y-%m-%d %H:%M:%S （datetime==> str）
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # str ==> datetime
            now_time = datetime.datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
            # 距开始还有多少秒
            # print(birthday-now_time)
            a = time.mktime(birthday.timetuple())
            b = time.mktime(now_time.timetuple())
            seconds = int(a) - int(b)
            # seconds = (birthday-now_time).seconds
            # 如果差距大于一小时
            if seconds > 0:
                # 差值大于一天86400
                if seconds > 86400:
                    day = seconds // 86400
                    if day > 30:
                        month = seconds // 2592000
                        stime = "{0}个月".format(month)
                    elif day > 15:
                        stime = "半个月"
                    else:
                        stime = "{0}天".format(day)
                else:
                    # 一天之内
                    seconds = seconds % 86400
                    if seconds > 3600:
                        hour = seconds // 3600
                        stime = "{0}小时".format(hour)
                    else:
                        # 一小时之内
                        minute = seconds % 3600
                        if minute > 60:
                            minute = minute // 60
                            stime = "{0}分钟".format(minute)
                        else:
                            stime = "即将开始"
            else:
                seconds = int(b) - int(a)
                # 差值大于一天86400
                if seconds > 86400:
                    day = seconds // 86400
                    if day > 30:
                        month = seconds // 2592000
                        stime = "{0}个月前".format(month)
                    elif day > 15:
                        stime = "半个月前"
                    else:
                        stime = "{0}天前".format(day)
                else:
                    # 一天之内
                    seconds = seconds % 86400
                    if seconds > 3600:
                        hour = seconds // 3600
                        stime = "{0}小时前".format(hour)
                    else:
                        # 一小时之内
                        minute = seconds % 3600
                        if minute > 60:
                            minute = minute // 60
                            stime = "{0}分钟前".format(minute)
                        else:
                            stime = "已开始"
            # 获取车库中的车
            carbarn_obj = CarBarn.objects.filter(id=i["activity_car"]).first()
            # 获取车对象
            carmodel_obj = CarModel.objects.filter(id=carbarn_obj.car_model_id).first()
            # 活动名称
            like_obj = Like.objects.filter(id=i["activity_name"]).first()
            dic = {
                # 人头像
                "head_img": "http://52.80.194.137:8001/dxgm/image/{0}".format(obj.img_head),
                # 姓名
                "nikename": obj.username,
                # 职业
                "job": obj.job,
                # 性别
                "sex": obj.sex,
                # 图片数量
                "pic_num": pic_num,
                # 图片地址
                "pic_list": pic_list,
                # 开始距当前活动还剩多少时间
                "start_time": stime,
                # 车型
                "car_model_name": carmodel_obj.name,
                # 活动名称
                "activity_name": like_obj.likename,
                # 活动主键
                "id": i["id"],
                # 活动类型种类(单人/多人)
                "activity_kind": i["activity_kind"],
                # 活动出发地
                "activity_area_start": i["activity_area_start"],
                # 活动目的地
                "activity_area_end": i["activity_area_end"],
                # 活动时间
                "activity_time": activity_time,
                # 活动话题
                "topic_name": topic_obj.topic_name,
                # 活动参与人群性别
                "activity_person_sex": i["activity_person_sex"],
                # 活动内容-说说你的想法
                "activity_content": i["activity_content"],
                # 起始经度
                "longitude_start": i["longitude_start"],
                # 起始纬度
                "latitude_start": i["latitude_start"],
                # 终点经度
                "longitude_end": i["longitude_end"],
                # 终点纬度
                "latitude_end": i["latitude_end"],
                # 发布时间
                "activity_create_time": activity_create_time
            }
            lis.append(dic)
        if len(lis) > 0:
            lis[0]["number"] = all_activity_objects.count()
        return Response(Common.tureReturn(Common, data=lis))


# TODO: 人
class PersonPic(APIView):
    def post(self, request):
        # 用户id
        pid = request.data.get("pid")
        # 获取用户对象
        obj = User.objects.filter(id=pid).first()
        if obj:
            # data
            dic = {
                "img": "http://52.80.194.137:8001/dxgm/image/{0}".format(obj.img_head),
                "name": obj.username
            }
        else:
            dic = {}
        return Response(Common.tureReturn(Common, data=dic))


# TODO: 活动
class ActivityPic(APIView):
    def post(self, request):
        # 用户id
        aid = request.data.get("aid")
        # 获取用户对象
        obj = Activity.objects.filter(id=aid).first()
        print(obj)
        if obj:
            topic_obj = Topic.objects.filter(id=obj.topic_name_id).first()

            image_obj = Image.objects.filter(activity_id=obj.id).first()
            # data
            dic = {
                "img": "http://52.80.194.137:8001/dxgm/picture/{0}".format(image_obj.image),
                "name": topic_obj.topic_name
            }
        else:
            dic = {}
        return Response(Common.tureReturn(Common, data=dic))
