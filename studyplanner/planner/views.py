from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from datetime import date, timedelta
from .models import Course, Assignment, StudyResource
from .forms import AssignmentForm


# Create your views here.
class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        week_from_today = today + timedelta(days=7)

        if not self.request.user.is_authenticated:
            context["overdue_assignments"] = Assignment.objects.none()
            context["due_today_assignments"] = Assignment.objects.none()
            context["due_this_week_assignments"] = Assignment.objects.none()
            context["high_priority_assignments"] = Assignment.objects.none()
            return context

        assignments = Assignment.objects.filter(
            course__user=self.request.user
        ).order_by("due_date")

        context["today"] = today
        context["overdue_assignments"] = assignments.filter(due_date__lt=today).exclude(
            status="done"
        )
        context["due_today_assignments"] = assignments.filter(due_date=today).exclude(
            status="done"
        )
        context["due_this_week_assignments"] = assignments.filter(
            due_date__gt=today, due_date__lte=week_from_today
        ).exclude(status="done")
        context["high_priority_assignments"] = assignments.filter(
            priority="high"
        ).exclude(status="done")

        return context


def signup(request):
    error_message = ""
    next_url = request.POST.get("next") or request.GET.get("next")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)
            return redirect("course-list")
        else:
            error_message = "Invalid sign up - please try again."
    else:
        form = UserCreationForm()

    context = {
        "form": form,
        "error_message": error_message,
        "next": next_url,
    }
    return render(request, "registration/signup.html", context)


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
    form_class = AssignmentForm
    template_name = "assignments/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(
            Course, id=kwargs["course_id"], user=request.user
        )
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.course = self.course
        return super().form_valid(form)

    def get_success_url(self):
        return self.course.get_absolute_url()


class AssignmentUpdateView(LoginRequiredMixin, UpdateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = "assignments/form.html"

    def get_queryset(self):
        return Assignment.objects.filter(course__user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class AssignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Assignment
    template_name = "assignments/confirm_delete.html"

    def get_queryset(self):
        return Assignment.objects.filter(course__user=self.request.user)

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class StudyResourceListView(LoginRequiredMixin, ListView):
    model = StudyResource
    template_name = "resources/index.html"
    context_object_name = "resources"

    def get_queryset(self):
        return StudyResource.objects.filter(user=self.request.user).order_by("title")


class StudyResourceDetailView(LoginRequiredMixin, DetailView):
    model = StudyResource
    template_name = "resources/detail.html"

    def get_queryset(self):
        return StudyResource.objects.filter(user=self.request.user)


class StudyResourceCreateView(LoginRequiredMixin, CreateView):
    model = StudyResource
    fields = ["title", "url", "resource_type", "description"]
    template_name = "resources/form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class StudyResourceUpdateView(LoginRequiredMixin, UpdateView):
    model = StudyResource
    fields = ["title", "url", "resource_type", "description"]
    template_name = "resources/form.html"

    def get_queryset(self):
        return StudyResource.objects.filter(user=self.request.user)


class StudyResourceDeleteView(LoginRequiredMixin, DeleteView):
    model = StudyResource
    template_name = "resources/confirm_delete.html"
    success_url = reverse_lazy("resource-list")

    def get_queryset(self):
        return StudyResource.objects.filter(user=self.request.user)
