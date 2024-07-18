from django.http import HttpResponseRedirect
from django.shortcuts import render
import plotly.express as px
from .models import UnknownMolecule, Molecule
from .forms import SelectionForm

import pandas as pd

# import plotly.express as px


def getSelectedSamples(request):
    if request.method == 'POST':
        form = SelectionForm(request.POST)
        if form.is_valid():
            requestedSample = form.cleaned_data["selected"]
            res = getUnknownMoleculeData(requestedSample)
            plot = generatePlot(res)
            return render(request, 'boxplots/sampleForm.html', {'form': form, 'plot':plot})
    else:
        form = SelectionForm()
        print("get")

    plot = 'box' #make the plot
    return render(request, 'boxplots/sampleForm.html', {'form': form})

def getUnknownMoleculeData(sampleNames):
    result = []
    df_list = []
    
    for n in sampleNames:
        i = UnknownMolecule.objects.all().filter(sampleSource__icontains=n).values()
        result.append(i)
        df = pd.DataFrame(i.values('levDistance','type','numOfReads'))
        df['levDistance'] = df['levDistance'].replace({'Levenshtein': 'LV'}, regex=True)
        df["lev_type"] = df["levDistance"] + " | " + df["type"]
 
        df_list.append(df)
    
    unMerged = df_list[0]
    for df_ in df_list[1:]:
        unMerged = unMerged.merge(df_, on="lev_type", how='outer')
    #     dfMain = pd.concat(dfMain, df_, join='outer')
   
    dfMain = pd.concat(df_list, ignore_index=True)
    dfMain = dfMain.groupby('lev_type', as_index=False)['numOfReads'].sum()
    # dfFinal = dfMain.groupby('lev_type')['numOfReads'].sum()
    # print(df)
    # for i in result:
    #     print(pd.DataFrame(i.values('levDistance','type','numOfReads')))
    print(unMerged)
    print(dfMain)
    return


def getMoleculeData(sampleNames):
    result = []
    for n in sampleNames:
        result.append(Molecule.objects.all().filter(sampleSource__icontains=n).values())

    return result

def generatePlot(data):
    return px.box(data)
