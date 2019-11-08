from rest_framework import serializers
from ..user import models


# 车品牌序列化
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CarBrand
        fields = "__all__"


# 车系列序列化
class SeriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CarSeries
        fields = "__all__"


# 车型号序列化
class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CarModel
        fields = "__all__"


# 用户序列化
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = "__all__"


# 车库序列化
class CarBarnSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CarBarn
        fields = "__all__"


# 活动序列化
class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Activity
        fields = "__all__"