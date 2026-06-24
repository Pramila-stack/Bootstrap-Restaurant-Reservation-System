"""
Maison Rouge — centralised email helpers (customer-only notifications).

Sends HTML + plain-text fallback. Never raises — email failure must never
break the booking flow.
"""
from django.core.mail import EmailMultiAlternatives


def booking_ref(reservation):
    return f"MR-{reservation.pk:05d}"


def send_reservation_email(subject, to, text_body, html_body):
    try:
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            to=[to] if isinstance(to, str) else to,
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=True)
    except Exception:
        pass


# ── Shared HTML components ─────────────────────────────────────────────────

def _html_shell(title, content_html):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#0D0D0D;
             font-family:'Helvetica Neue',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0"
       style="background:#0D0D0D;padding:40px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0"
           style="max-width:600px;width:100%;background:#161616;
                  border-radius:16px;overflow:hidden;border:1px solid #2a2a2a;">

      <!-- Header -->
      <tr>
        <td style="background:linear-gradient(135deg,#1a1a1a,#141414);
                   padding:36px 40px;border-bottom:1px solid #2a2a2a;
                   text-align:center;">
          <div style="display:inline-block;width:48px;height:48px;
                      background:linear-gradient(135deg,#C99542,#E8B95C);
                      border-radius:12px;line-height:48px;font-size:24px;
                      margin-bottom:14px;">🍷</div>
          <h1 style="margin:0;font-family:Georgia,serif;font-size:22px;
                     font-weight:600;color:#EDE4D4;letter-spacing:0.02em;">
            Maison Rouge
          </h1>
          <p style="margin:4px 0 0;font-size:11px;letter-spacing:0.2em;
                    text-transform:uppercase;color:#C99542;">
            Fine Dining · Est. 2018
          </p>
        </td>
      </tr>

      <!-- Body -->
      <tr>
        <td style="padding:36px 40px;">{content_html}</td>
      </tr>

      <!-- Footer -->
      <tr>
        <td style="padding:24px 40px;border-top:1px solid #2a2a2a;
                   text-align:center;background:#111111;">
          <p style="margin:0 0 6px;font-size:12px;color:#555;">
            Lazimpat, Kathmandu &nbsp;·&nbsp;
            <a href="tel:+97714111111"
               style="color:#C99542;text-decoration:none;">+977 1-411-1111</a>
            &nbsp;·&nbsp;
            <a href="mailto:info@maisonrouge.com"
               style="color:#C99542;text-decoration:none;">info@maisonrouge.com</a>
          </p>
          <p style="margin:0;font-size:11px;color:#333;">
            &copy; 2024 Maison Rouge. All rights reserved.
          </p>
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


def _detail_row(label, value):
    return (
        f'<tr>'
        f'<td style="padding:10px 16px;font-size:13px;color:#888;width:140px;'
        f'border-bottom:1px solid #222;vertical-align:top;">{label}</td>'
        f'<td style="padding:10px 16px;font-size:13px;color:#EDE4D4;font-weight:500;'
        f'border-bottom:1px solid #222;vertical-align:top;">{value}</td>'
        f'</tr>'
    )


def _booking_table(res):
    ref  = booking_ref(res)
    rows = _detail_row("Reference",   f"<strong style='color:#C99542;'>{ref}</strong>")
    rows += _detail_row("Date",       res.reservation_date.strftime("%A, %d %B %Y"))
    rows += _detail_row("Time Slot",  res.get_slot_label())
    rows += _detail_row("Party size", f"{res.guests} guest{'s' if res.guests != 1 else ''}")
    rows += _detail_row("Table",      f"Table #{res.table.number} ({res.table.seats} seats)")
    if res.name:
        rows += _detail_row("Occasion", res.name)
    if res.special_requests:
        rows += _detail_row("Special requests", res.special_requests)
    return (
        f'<table width="100%" cellpadding="0" cellspacing="0"'
        f' style="background:#1C1C1C;border-radius:10px;border:1px solid #2a2a2a;'
        f'margin:20px 0;overflow:hidden;">{rows}</table>'
    )


def _heading(text):
    return (f'<h2 style="margin:0 0 8px;font-family:Georgia,serif;'
            f'font-size:20px;color:#EDE4D4;">{text}</h2>')


def _subtext(text):
    return (f'<p style="margin:0 0 20px;font-size:14px;color:#888;'
            f'line-height:1.65;">{text}</p>')


def _badge(text, color="#C99542", bg="rgba(201,149,66,0.12)",
           border="rgba(201,149,66,0.3)"):
    return (
        f'<span style="display:inline-block;padding:4px 14px;background:{bg};'
        f'border:1px solid {border};border-radius:100px;font-size:11px;'
        f'font-weight:700;letter-spacing:0.1em;text-transform:uppercase;'
        f'color:{color};">{text}</span>'
    )


# ══════════════════════════════════════════════════════════════════════════
# 1. BOOKING CONFIRMED — to guest
# ══════════════════════════════════════════════════════════════════════════

def send_booking_confirmed_guest(reservation):
    if not reservation.user.email:
        return

    ref     = booking_ref(reservation)
    user    = reservation.user
    subject = f"Reservation Confirmed [{ref}] — Maison Rouge"

    text = (
        f"Hi {user.username},\n\n"
        f"Your table at Maison Rouge is confirmed — we look forward to welcoming you!\n\n"
        f"BOOKING DETAILS\n"
        f"  Reference  : {ref}\n"
        f"  Date       : {reservation.reservation_date.strftime('%A, %d %B %Y')}\n"
        f"  Time Slot  : {reservation.get_slot_label()}\n"
        f"  Party size : {reservation.guests} guest(s)\n"
        f"  Table      : #{reservation.table.number} ({reservation.table.seats} seats)\n"
        f"  Occasion   : {reservation.name or '—'}\n"
        f"  Requests   : {reservation.special_requests or 'None'}\n\n"
        f"Please arrive a few minutes before the start of your slot.\n"
        f"Tables are held for 15 minutes past the slot start time.\n\n"
        f"To cancel, log in to your account or call us on +977 1-411-1111.\n\n"
        f"— Maison Rouge Team"
    )

    content = (
        f'<p style="margin:0 0 12px;">'
        f'{_badge("✓ Confirmed", "#4ade80", "rgba(74,222,128,0.1)", "rgba(74,222,128,0.25)")}'
        f'</p>'
        + _heading("Your Table is Confirmed!")
        + _subtext(
            f"Hi <strong style='color:#EDE4D4;'>{user.username}</strong>, "
            f"your reservation is all set. We look forward to welcoming you."
        )
        + _booking_table(reservation)
        + f"""
        <div style="background:#1C1C1C;border:1px solid #2a2a2a;border-radius:10px;
                    padding:18px 20px;margin:4px 0 0;">
          <p style="margin:0 0 8px;font-size:12px;font-weight:700;color:#888;
                    letter-spacing:0.1em;text-transform:uppercase;">Good to Know</p>
          <ul style="margin:0;padding-left:18px;color:#888;font-size:13px;line-height:1.9;">
            <li>Please arrive a <strong style="color:#EDE4D4;">few minutes early</strong>
                before your slot begins.</li>
            <li>Tables are held for <strong style="color:#EDE4D4;">15 minutes</strong>
                past the slot start time.</li>
            <li>To cancel, log in to
                <strong style="color:#EDE4D4;">My Reservations</strong>
                or call
                <a href="tel:+97714111111" style="color:#C99542;">+977 1-411-1111</a>.</li>
          </ul>
        </div>"""
    )

    send_reservation_email(subject, user.email, text, _html_shell(subject, content))


# ══════════════════════════════════════════════════════════════════════════
# 2. BOOKING CANCELLED BY GUEST — to guest only
# ══════════════════════════════════════════════════════════════════════════

def send_booking_cancelled_by_guest_guest(reservation):
    if not reservation.user.email:
        return

    ref     = booking_ref(reservation)
    user    = reservation.user
    subject = f"Cancellation Confirmed [{ref}] — Maison Rouge"

    text = (
        f"Hi {user.username},\n\n"
        f"Your cancellation for reservation {ref} has been confirmed.\n\n"
        f"  Date      : {reservation.reservation_date.strftime('%A, %d %B %Y')}\n"
        f"  Time Slot : {reservation.get_slot_label()}\n"
        f"  Guests    : {reservation.guests}\n\n"
        f"We hope to welcome you at Maison Rouge again soon.\n\n"
        f"— Maison Rouge Team"
    )

    content = (
        _heading("Cancellation Confirmed")
        + _subtext(
            f"Hi <strong style='color:#EDE4D4;'>{user.username}</strong>, "
            f"your reservation has been cancelled as requested. "
            f"We hope to see you at Maison Rouge again soon."
        )
        + _booking_table(reservation)
    )

    send_reservation_email(subject, user.email, text, _html_shell(subject, content))
