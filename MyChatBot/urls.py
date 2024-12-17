from django.urls import path

from . import views

urlpatterns = [path("index.html", views.MyChatBot, name="MyChatBot"),
	       path("User.html", views.User, name="User"),
	       path("index.html", views.Logout, name="Logout"),
	       path("Register.html", views.Register, name="Register"),
	       path("test.html", views.test, name="test"),
	       path("UserLogin", views.UserLogin, name="UserLogin"),
	       path("Signup", views.Signup, name="Signup"),
	       path("ChatData", views.ChatData, name="ChatData"),
]