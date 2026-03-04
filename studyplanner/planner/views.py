from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from .models import Course, Assignment


# Create your views here.
class HomeView(TemplateView):
    template_name = "home.html"


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "courses/index.html"
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user).order_by("name")


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = "courses/detail.html"

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    fields = ["name", "instructor", "color"]
    template_name = "courses/form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    fields = ["name", "instructor", "color"]
    template_name = "courses/form.html"

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)


class CourseDeleteView(LoginRequiredMixin, DeleteView):
    model = Course
    template_name = "courses/confirm_delete.html"
    success_url = reverse_lazy("course-list")

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)


class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = "assignments/detail.html"

    def get_queryset(self):
        return Assignment.objects.filter(course__user=self.request.user)


class AssignmentCreateView(LoginRequiredMixin, CreateView):
    model = Assignment
    fields = ["title", "due_date", "status", "priority", "notes"]
    template_name = "assignments/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.course = Course.objects.get(id=kwargs["course_id"], user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.course = self.course
        return super().form_valid(form)

    def get_success_url(self):
        return self.course.get_absolute_url()


class AssignmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Assignment
    fields = ["title", "due_date", "status", "priority", "notes"]
    template_name = "assignments/form.html"

    def get_queryset(self):
        return Assignment.objects.filter(course_user=self.request.user)

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class AssignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Assignment
    template_name = "assignments/confirm_delete.html"

    def get_queryset(self):
        return Assignment.objects.filter(course_user=self.request.user)

    def get_success_url(self):
        return self.object.course.get_absolute_url()
