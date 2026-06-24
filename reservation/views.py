import datetime

from django.contrib import messages
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login

from reservation.emails import (
    send_booking_confirmed_guest,
    send_booking_cancelled_by_guest_guest,
)
from reservation.forms import ReservationForm, SignupForm
from reservation.models import MenuItem, Profile, Reservation, Table


class SignupView(CreateView):
    template_name = "registration/signup.html"
    form_class    = SignupForm
    success_url   = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.email = form.cleaned_data['email']
        self.object.save()
        Profile.objects.create(user=self.object, role="customer")
        login(self.request, self.object)
        messages.success(self.request, f"Welcome to Maison Rouge, {self.object.username}!")
        return response


class HomeView(ListView):
    model                = MenuItem
    template_name        = "home.html"
    context_object_name  = "menu_items"

    def get_queryset(self):
        return MenuItem.objects.filter(available=True).order_by("-id")


class ReserveTableView(LoginRequiredMixin, CreateView):
    model         = Reservation
    form_class    = ReservationForm
    template_name = "reserve_table.html"
    success_url   = reverse_lazy("my-reservations")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        date = self.request.GET.get('date')
        slot = self.request.GET.get('slot')
        if date and slot:
            kwargs['date'] = date
            kwargs['slot'] = slot
        return kwargs

    def get_context_data(self, **kwargs):
        ctx  = super().get_context_data(**kwargs)
        date = self.request.GET.get('date')
        slot = self.request.GET.get('slot')
        # Only show step-2 form when both params are present
        if not (date and slot):
            ctx['form'] = None
        return ctx

    def form_valid(self, form):
        form.instance.user   = self.request.user
        form.instance.status = 'confirmed'           # auto-confirm immediately
        try:
            response = super().form_valid(form)
        except IntegrityError:
            form.add_error(
                None,
                "This table slot was just taken by another guest. "
                "Please go back and choose a different table or time slot."
            )
            return self.form_invalid(form)

        send_booking_confirmed_guest(form.instance)

        messages.success(
            self.request,
            "Your table is confirmed! A confirmation email has been sent to you."
        )
        return response


class MyReservationView(LoginRequiredMixin, ListView):
    model               = Reservation
    template_name       = "my_reservations.html"
    context_object_name = "reservations"

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).order_by("-reservation_date")


class CustomerCancelReservationView(LoginRequiredMixin, View):
    """Allow a guest to cancel their own confirmed upcoming reservation."""

    def post(self, request, pk, *args, **kwargs):
        res = get_object_or_404(Reservation, pk=pk, user=request.user)

        if res.status != 'confirmed':
            messages.error(request, "Only confirmed reservations can be cancelled.")
            return redirect('my-reservations')

        if res.reservation_date < datetime.date.today():
            messages.error(request, "Past reservations cannot be cancelled.")
            return redirect('my-reservations')

        res.status = 'cancelled'
        res.save()
        send_booking_cancelled_by_guest_guest(res)
        messages.success(request, "Your reservation has been cancelled. A confirmation email has been sent.")
        return redirect('my-reservations')


# ── Staff read-only dashboard ──────────────────────────────────────────────

@method_decorator(staff_member_required, name='dispatch')
class ManageReservationsView(ListView):
    model               = Reservation
    template_name       = 'manage_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        return Reservation.objects.select_related('user', 'table').order_by('-reservation_date', 'slot')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs  = Reservation.objects.all()
        today = datetime.date.today()
        ctx['total']           = qs.count()
        ctx['confirmed_count'] = qs.filter(status='confirmed').count()
        ctx['cancelled_count'] = qs.filter(status='cancelled').count()
        ctx['today_count']     = qs.filter(
            reservation_date=today, status='confirmed'
        ).count()
        return ctx
