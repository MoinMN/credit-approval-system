"""
URL configuration for credit_approval_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from App import views

urlpatterns = [
    path('', views.index, name="home"),

    path('register', views.register, name="register"),
    path('check-eligibility', views.check_eligibility, name="check_eligibility"),
    path('create-loan', views.create_loan, name="create_loan"),
    path('view-loan/<int:loan_id>', views.view_loan, name="view_loan"),
    path('view-loans/<int:customer_id>', views.view_customer_loans, name="view_customer_loans"),
]
