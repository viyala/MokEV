from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUS"),
    path("contact/", views.contact, name="ContactUS"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>", views.productView, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path("category/<str:cat>", views.category, name="Category"),
    path("orders/", views.orders, name="Orders"),
    path("track-order/<int:odId>", views.trackorder, name="TrackOrder"),
    path("cancel-order/<int:odId>", views.cancelOrder, name="CancelOrder"),
    # path("handlerequest/", views.handlerequest, name="handlerequest"),
    # Authentication
    path('signup/', views.handleSignup, name='handleSignup'),
    path('login/', views.handleLogin, name='handleLogin'),
    path('logout/', views.handleLogout, name='handleLogout'),
]