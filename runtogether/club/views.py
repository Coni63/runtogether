from django.shortcuts import render

# from core.tasks import email_users


def list_clubs(request):
    # result = email_users.enqueue(
    #     emails=["user@example.com"],
    #     subject="You have a message",
    #     message="Hello there!",
    # )

    # print(result)

    return render(request, "club/clubs.html")
