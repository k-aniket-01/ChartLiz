# """
# URL configuration for chartliz project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.2/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path, include

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('accounts/', include('allauth.urls')),
# ]



from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def homepage(request):
    return HttpResponse("<h1>ChartLiz works!</h1><a href='/accounts/login/'>Login</a>")

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('accounts/',   include('allauth.urls')),
    path('users/',      include('users.urls')),   
    path('stocks/',     include('stocks.urls')),
    path('trading/',    include('trading.urls')),
    path('patterns/',   include('patterns.urls',    namespace='patterns')),
    path('alerts/',     include('alerts.urls',      namespace='alerts')),
    path('',            homepage),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
