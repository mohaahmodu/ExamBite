from functools import wraps

from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

from .models import Subscription


def subscription_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        try:
            subscription = Subscription.objects.get(
                user=request.user
            )

            if (
                subscription.is_active
                and subscription.expiry_date
                and subscription.expiry_date > timezone.now()
            ):
                return view_func(request, *args, **kwargs)

        except Subscription.DoesNotExist:
            pass

        messages.warning(
            request,
            "This feature requires an active Premium subscription."
        )

        return redirect("subscribe")

    return wrapper