from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    # Course routes
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
    # Assignment routes
    path(
        "courses/<int:course_id>/assignments/new",
        views.AssignmentCreateView.as_view(),
        name="assignment-create",
    ),
    path(
        "assignments/<int:pk>/",
        views.AssignmentDetailView.as_view(),
        name="assignment-detail",
    ),
    path(
        "assignments/<int:pk>/edit/",
        views.AssignmentUpdateView.as_view(),
        name="assignment-update",
    ),
    path(
        "assignments/<int:pk>/delete/",
        views.AssignmentDeleteView.as_view(),
        name="assignment-delete",
    ),
]
