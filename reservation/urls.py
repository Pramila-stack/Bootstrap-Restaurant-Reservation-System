from django.urls import path
from reservation import views

urlpatterns = [
    path("",                                        views.HomeView.as_view(),                    name="home"),
    path("signup/",                                 views.SignupView.as_view(),                   name="signup"),
    path("reserve-table/",                          views.ReserveTableView.as_view(),             name="reserve-table"),
    path("my-reservations/",                        views.MyReservationView.as_view(),            name="my-reservations"),
    path("manage-reservations/",                    views.ManageReservationsView.as_view(),       name="manage-reservations"),
    path("reservation/<int:pk>/cancel-own/",        views.CustomerCancelReservationView.as_view(), name="cancel-own-reservation"),
]
