from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import (
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView,
)
from django.urls import reverse_lazy
from datetime import date, timedelta
from .models import Course, Assignment, StudyResource
from .forms import AssignmentForm, CourseForm


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


class SignUpView(FormView):
    template_name = "registration/signup.html"
    form_class = UserCreationForm

    def get_next_url(self):
        return self.request.POST.get("next") or self.request.GET.get("next")

    def get_success_url(self):
        next_url = self.get_next_url()
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={self.request.get_host()}
        ):
            return next_url
        return reverse_lazy("course-list")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.get_next_url()
        context["error_message"] = ""
        if self.request.method == "POST" and context["form"].errors:
            context["error_message"] = "Invalid sign up - please try again."
        return context


class CourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = "courses/index.html"
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user).order_by("name")


class CourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = "courses/detail.html"
    context_object_name = "course"

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        soon = today + timedelta(days=2)

        assignments = self.object.assignments.all().order_by("due_date")

        for assignment in assignments:
            assignment.is_due_soon = (
                assignment.status != "done" and today <= assignment.due_date <= soon
            )

        context["assignments"] = assignments
        context["total_assignments_count"] = assignments.count()
        context["completed_assignments_count"] = assignments.filter(
            status="done"
        ).count()

        return context


class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/form.html"

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Course created successfully.")
        return super().form_valid(form)


class CourseUpdateView(LoginRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/form.html"

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Course updated successfully.")
        return super().form_valid(form)


class CourseDeleteView(LoginRequiredMixin, DeleteView):
    model = Course
    template_name = "courses/confirm_delete.html"
    success_url = reverse_lazy("course-list")

    def get_queryset(self):
        return Course.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Course deleted successfully.")
        return super().form_valid(form)


class AssignmentDetailView(LoginRequiredMixin, DetailView):
    model = Assignment
    template_name = "assignments/detail.html"
    context_object_name = "assignment"

    def get_queryset(self):
        return Assignment.objects.filter(course__user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        soon = today + timedelta(days=2)
        assignment = context["assignment"]

        assignment.is_due_soon = (
            assignment.status != "done" and today <= assignment.due_date <= soon
        )

        return context


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
        messages.success(self.request, "Assignment created successfully.")
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

    def form_valid(self, form):
        messages.success(self.request, "Assignment updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.course.get_absolute_url()


class AssignmentDeleteView(LoginRequiredMixin, DeleteView):
    model = Assignment
    template_name = "assignments/confirm_delete.html"

    def get_queryset(self):
        return Assignment.objects.filter(course__user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "Assignment deleted successfully.")
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
        messages.success(self.request, "Resource created successfully.")
        return super().form_valid(form)


class StudyResourceUpdateView(LoginRequiredMixin, UpdateView):
    model = StudyResource
    fields = ["title", "url", "resource_type", "description"]
    template_name = "resources/form.html"

    def get_queryset(self):
        return StudyResource.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Resource updated successfully.")
        return super().form_valid(form)


class StudyResourceDeleteView(LoginRequiredMixin, DeleteView):
    model = StudyResource
    template_name = "resources/confirm_delete.html"
    success_url = reverse_lazy("resource-list")

    def get_queryset(self):
        return StudyResource.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Resource deleted successfully.")
        return super().form_valid(form)


class AssignmentListView(LoginRequiredMixin, ListView):
    model = Assignment
    template_name = "assignments/index.html"
    context_object_name = "assignments"

    def get_queryset(self):
        queryset = Assignment.objects.filter(course__user=self.request.user).order_by(
            "due_date"
        )

        search_query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status")
        priority = self.request.GET.get("priority")

        if search_query:
            queryset = queryset.filter(title__icontains=search_query)

        if status:
            queryset = queryset.filter(status=status)

        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["selected_status"] = self.request.GET.get("status", "")
        context["selected_priority"] = self.request.GET.get("priority", "")

        today = date.today()
        soon = today + timedelta(days=2)

        for assignment in context["assignments"]:
            assignment.is_due_soon = (
                assignment.status != "done" and today <= assignment.due_date <= soon
            )

        return context


class AssignmentCompleteView(LoginRequiredMixin, View):
    status = "done"
    success_message = "Assignment marked as complete."

    def get_object(self, pk):
        return get_object_or_404(
            Assignment,
            pk=pk,
            course__user=self.request.user,
        )

    def post(self, request, pk):
        assignment = self.get_object(pk)
        assignment.status = self.status
        assignment.save(update_fields=["status"])
        messages.success(request, self.success_message)
        if request.POST.get("redirect_to") == "course":
            return redirect(assignment.course.get_absolute_url())
        return redirect("assignment-detail", pk=pk)


class AssignmentIncompleteView(AssignmentCompleteView):
    status = "todo"
    success_message = "Assignment marked as incomplete."
