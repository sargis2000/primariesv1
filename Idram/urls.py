from django.urls import path
from .views import IdramPayForEvaluate

urlpatterns =[
    # path("i-pay/", )
    path("get_idram_data/", IdramPayForEvaluate.as_view())

]