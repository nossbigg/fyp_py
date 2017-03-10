from django.http import HttpResponse


def test(request):
    return HttpResponse("This is a test request.")


def get_test_results_list(request):
    return HttpResponse("This is a test POST request.")
