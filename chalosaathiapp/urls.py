

from django.urls import path
from chalosaathiapp import admin
from . import views
from .views import feedback_view
from django.conf import settings
from django.conf.urls.static import static
from .views import send_email_view

urlpatterns = [
    path("", views.index, name="index"),
    path("profile/", views.profile, name="profile"),        
    path("signup/", views.signup, name="signup"), 
    path("login/", views.login, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("aboutus/", views.aboutus, name="aboutus"),
    path('feedback/', views.feedback_view, name='feedback'),
    path('feedback-data/', views.feedback_list, name='feedback-data'),
    path("forgot_password/", views.forgot_password, name="forgot_password"),  
    path("feedback-data/", views.feedback_data, name="feedback_data"),
    path('send-email/', send_email_view, name='send_email'),

   

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)