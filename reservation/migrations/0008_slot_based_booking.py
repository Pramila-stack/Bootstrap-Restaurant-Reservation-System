"""
Replace free-time booking with time-slot booking.

Changes:
  - Remove old UniqueConstraint (unique_active_table_booking)
  - Add `slot` CharField with predefined choices (default to 'dinner' for existing rows)
  - Add `created_at` DateTimeField
  - Remove `reservation_time` TimeField
  - Alter `status` field default from 'pending' → 'confirmed'
  - Add new UniqueConstraint (unique_confirmed_table_slot)
"""
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservation', '0007_fix_unique_constraint_allow_cancelled_rebooking'),
    ]

    operations = [
        # 1. Drop the old constraint so we can safely alter the table
        migrations.RemoveConstraint(
            model_name='reservation',
            name='unique_active_table_booking',
        ),

        # 2. Add the slot field (existing rows get 'dinner' as a sensible default)
        migrations.AddField(
            model_name='reservation',
            name='slot',
            field=models.CharField(
                choices=[
                    ('lunch',        'Lunch  ·  12:00 – 14:00'),
                    ('afternoon',    'Afternoon  ·  14:30 – 16:30'),
                    ('early_dinner', 'Early Dinner  ·  17:00 – 19:00'),
                    ('dinner',       'Dinner  ·  19:30 – 21:30'),
                    ('late_night',   'Late Night  ·  22:00 – 23:30'),
                ],
                max_length=20,
                default='dinner',
            ),
            preserve_default=False,
        ),

        # 3. Add created_at timestamp
        migrations.AddField(
            model_name='reservation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),

        # 4. Remove the old reservation_time field
        migrations.RemoveField(
            model_name='reservation',
            name='reservation_time',
        ),

        # 5. Change status default from 'pending' to 'confirmed'
        migrations.AlterField(
            model_name='reservation',
            name='status',
            field=models.CharField(
                choices=[('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')],
                default='confirmed',
                max_length=10,
            ),
        ),

        # 6. Update ordering via AlterModelOptions
        migrations.AlterModelOptions(
            name='reservation',
            options={'ordering': ['-reservation_date', 'slot']},
        ),

        # 7. Add new slot-based unique constraint (confirmed bookings only)
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.UniqueConstraint(
                condition=models.Q(status='confirmed'),
                fields=['table', 'reservation_date', 'slot'],
                name='unique_confirmed_table_slot',
            ),
        ),
    ]
