from django.urls import path
from .views import UserRegistrationAPI, UserLoginAPI, LoanAPI, PaymentAPI, GetStatementAPI

urlpatterns = [
    path('api/register-user/',UserRegistrationAPI.as_view(), name='registration'),
    path('api/login-user/',UserLoginAPI.as_view(), name='login'),
    path('api/apply-loan/',LoanAPI.as_view(), name='apply-loan'),
    path('api/make-payment/',PaymentAPI.as_view(), name='make-payment'),
    path('api/get-statement/',GetStatementAPI.as_view(), name='get-statement'),
]