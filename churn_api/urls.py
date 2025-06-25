from django.urls import path
from .views import PredictChurnAPIView

urlpatterns = [
    path('predict/', PredictChurnAPIView.as_view(), name='predict-churn'),
]
