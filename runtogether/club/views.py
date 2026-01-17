from django.shortcuts import render

from core.tasks import email_users, addition_lente


def list_clubs(request):
    result = email_users.delay(
        emails=["user@example.com"],
        subject="You have a message",
        message="Hello there!",
    )

    print(result.status)

    # from core.tasks import addition_lente

    # result = addition_lente.delay(10, 20)
    # print(result.status)  # Devrait être 'PENDING' ou 'SUCCESS'

    return render(request, "club/clubs.html")
