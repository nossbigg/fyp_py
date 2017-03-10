from django.shortcuts import render


def index(request):
    test_var = "This is a test var"

    context = {"test_var": test_var}
    return render(request, 'index.html', context)
