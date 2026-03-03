from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("courses/", views.CourseListView.as_view(), name="course-list"),
    path("courses/new/", views.CourseCreateView.as_view(), name="course-create"),
    path("courses/<int:pk>/", views.CourseDetailView.as_view(), name="course-detail"),
    path(
        "courses/<int:pk>/edit/", views.CourseUpdateView.as_view(), name="course-update"
    ),
    path(
        "courses/<int:pk>/delete/",
        views.CourseDeleteView.as_view(),
        name="course-delete",
    ),
]
