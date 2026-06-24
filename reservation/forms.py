import datetime

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from reservation.models import Reservation, Table, SLOT_CHOICES


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email Address")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email


class ReservationForm(forms.ModelForm):
    class Meta:
        model  = Reservation
        fields = ['name', 'table', 'slot', 'guests', 'reservation_date', 'special_requests']
        widgets = {
            'reservation_date': forms.DateInput(attrs={'type': 'date'}),
            'special_requests': forms.Textarea(attrs={'rows': 3}),
            'name':             forms.TextInput(),
        }
        labels = {
            'name':             'Occasion / Booking Name (optional)',
            'slot':             'Dining Slot',
            'special_requests': 'Special Requests (optional)',
        }

    def __init__(self, *args, **kwargs):
        date = kwargs.pop('date', None)
        slot = kwargs.pop('slot', None)
        super().__init__(*args, **kwargs)

        # Pre-select slot if coming from step 1
        if slot:
            self.fields['slot'].initial = slot

        # Filter out fully-booked tables for the chosen date+slot
        if date and slot:
            booked = Reservation.objects.filter(
                reservation_date=date,
                slot=slot,
                status='confirmed',
            ).values_list('table_id', flat=True)
            self.fields['table'].queryset = Table.objects.exclude(id__in=booked)

    # ── Field validators ───────────────────────────────────────────────────

    def clean_reservation_date(self):
        date = self.cleaned_data.get('reservation_date')
        if date is None:
            return date
        today = datetime.date.today()
        if date < today:
            raise forms.ValidationError(
                "Reservation date cannot be in the past. Please choose today or a future date."
            )
        if date > today + datetime.timedelta(days=90):
            raise forms.ValidationError(
                "Reservations can only be made up to 90 days in advance. "
                "Please contact us directly for special arrangements."
            )
        return date

    def clean_guests(self):
        guests = self.cleaned_data.get('guests')
        if guests is not None:
            if guests < 1:
                raise forms.ValidationError("Party size must be at least 1.")
            if guests > 20:
                raise forms.ValidationError(
                    "We accommodate a maximum of 20 guests per booking. "
                    "For larger groups please contact us directly."
                )
        return guests

    # ── Cross-field validation ─────────────────────────────────────────────

    def clean(self):
        cleaned = super().clean()
        table  = cleaned.get('table')
        date   = cleaned.get('reservation_date')
        slot   = cleaned.get('slot')
        guests = cleaned.get('guests')

        # Guest count must not exceed the table's capacity
        if table and guests and guests > table.seats:
            self.add_error(
                'guests',
                f"Table #{table.number} seats {table.seats} "
                f"but you requested {guests}. "
                f"Please choose a larger table or reduce your party size."
            )

        # Defence-in-depth: re-check slot availability at clean time to catch
        # the narrow race where two users submit simultaneously.
        if table and date and slot:
            conflict = Reservation.objects.filter(
                table=table,
                reservation_date=date,
                slot=slot,
                status='confirmed',
            )
            if self.instance and self.instance.pk:
                conflict = conflict.exclude(pk=self.instance.pk)
            if conflict.exists():
                raise forms.ValidationError(
                    "This table was just booked for that slot while you were completing the form. "
                    "Please go back and select a different table or slot."
                )

        return cleaned
