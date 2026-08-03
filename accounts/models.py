from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.username} - {self.code}"


class Subscription(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="subscription"
    )

    is_active = models.BooleanField(default=False)

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=600.00
    )

    paystack_reference = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    start_date = models.DateTimeField(
        blank=True,
        null=True
    )

    expiry_date = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def activate(self):
        self.is_active = True
        self.start_date = timezone.now()
        self.expiry_date = timezone.now() + timedelta(days=30)
        self.save()

    @property
    def expired(self):
        if not self.expiry_date:
            return True
        return timezone.now() > self.expiry_date

    def __str__(self):
        return f"{self.user.username} Subscription"