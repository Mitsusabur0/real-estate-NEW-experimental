from django.shortcuts import render

# Create your views here.
def properties(request):
    return render(request, 'management_properties/m_properties.html')