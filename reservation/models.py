from django.db import models
from django.contrib.auth.models import User


SLOT_CHOICES = [
    ('lunch',        'Lunch  ·  12:00 – 14:00'),
    ('afternoon',    'Afternoon  ·  14:30 – 16:30'),
    ('early_dinner', 'Early Dinner  ·  17:00 – 19:00'),
    ('dinner',       'Dinner  ·  19:30 – 21:30'),
    ('late_night',   'Late Night  ·  22:00 – 23:30'),
]

# Human-readable start times used in emails / templates
SLOT_START = {
    'lunch':        '12:00',
    'afternoon':    '14:30',
    'early_dinner': '17:00',
    'dinner':       '19:30',
    'late_night':   '22:00',
}


class Profile(models.Model):
    ROLE_CHOICES = (
        ("admin",    "Admin"),
        ("staff",    "Staff"),
        ("customer", "Customer"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="customer")

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class MenuItem(models.Model):
    name        = models.CharField(max_length=100)
    description = models.TextField()
    price       = models.DecimalField(max_digits=6, decimal_places=2)
    available   = models.BooleanField(default=True)
    image       = models.ImageField(upload_to="images/", blank=False)

    def __str__(self):
        return self.name


class Table(models.Model):
    number = models.PositiveBigIntegerField(unique=True)
    seats  = models.PositiveBigIntegerField()

    def __str__(self):
        return f"Table {self.number} — {self.seats} seats"


class Reservation(models.Model):
    STATUS = [
        ('confirmed', 'Confirmed'),
        ('cancelled',  'Cancelled'),
    ]

    user             = models.ForeignKey(User, on_delete=models.CASCADE)
    name             = models.CharField(max_length=50, null=True, blank=True)
    table            = models.ForeignKey(Table, on_delete=models.CASCADE)
    reservation_date = models.DateField()
    slot             = models.CharField(max_length=20, choices=SLOT_CHOICES)
    guests           = models.PositiveBigIntegerField()
    status           = models.CharField(max_length=10, choices=STATUS, default='confirmed')
    special_requests = models.TextField(blank=True, null=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-reservation_date', 'slot']
        constraints = [
            # A table can only have one confirmed booking per slot per day.
            # Cancelled reservations are excluded so the slot can be rebooked.
            models.UniqueConstraint(
                fields=['table', 'reservation_date', 'slot'],
                condition=models.Q(status='confirmed'),
                name='unique_confirmed_table_slot',
            )
        ]

    def get_slot_label(self):
        return dict(SLOT_CHOICES).get(self.slot, self.slot)

    def get_slot_start(self):
        return SLOT_START.get(self.slot, '')

    def __str__(self):
        return f"{self.user.username} — Table {self.table.number} | {self.get_slot_label()} on {self.reservation_date}"
