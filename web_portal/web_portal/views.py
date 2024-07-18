from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import UnknownMolecule, Molecule
from .forms import SelectionForm
# import plotly.express as px


def getSelectedSamples(request):
    if request.method == 'POST':
        form = SelectionForm(request.POST)
        if form.is_valid():
            requestedSample = form.cleaned_data["selected"]
            res = getUnknownMoleculeData(requestedSample)
            print(res)
    else:
        form = SelectionForm()
        print("get")

    plot = 'box' #make the plot
    return render(request, 'boxplots/sampleForm.html', {'form': form})

def getUnknownMoleculeData(sampleNames):
    result = []
    for n in sampleNames:
        result.append(UnknownMolecule.objects.all().filter(sampleSource__icontains=n).values())

    return result

def getMoleculeData(sampleNames):
    result = []
    for n in sampleNames:
        result.append(Molecule.objects.all().filter(sampleSource__icontains=n).values())

    return result
