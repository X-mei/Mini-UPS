from django.shortcuts import render

# Create your views here.
def show_index(request):
    """
    Show the index for the web app
    """
    return render(request, 'ups/index.html')