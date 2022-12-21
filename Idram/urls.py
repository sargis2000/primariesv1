from django.urls import path
from .views import PayForEvaluate, PayForVoting


urlpatterns = [
    # path("i-pay/", )
    path("pay_evaluate/", PayForEvaluate.as_view()),
    path("pay_voting/", PayForVoting.as_view()),
]
