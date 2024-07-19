from django.shortcuts import render
import plotly.express as px
from .models import UnknownMolecule, Molecule
from .forms import SelectionForm

import pandas as pd
pd.options.plotting.backend = "plotly"



def getSelectedSamples(request):
    if request.method == 'POST':
        form = SelectionForm(request.POST)
        if form.is_valid():
            requestedSample = form.cleaned_data["selected"]
            unkRes = getUnknownMoleculeData(requestedSample)
            globRes = getMoleculeData(requestedSample)
            plot1 = generateBoxplot(unkRes, "UNKOnly",len(requestedSample))
            plot2 = generateBoxplot(globRes,"GlobalView",len(requestedSample))
            return render(request, 'boxplots/sampleForm.html', {'form': form, 'plot1':plot1, 'plot2':plot2})
    else:
        form = SelectionForm()
        print("get")
    return render(request, 'boxplots/sampleForm.html', {'form': form})

def getUnknownMoleculeData(sampleNames):
    df_list = []
    
    for n in sampleNames:
        df = pd.DataFrame(UnknownMolecule.objects.all().filter(sampleSource__icontains=n).values('levDistance','type','numOfReads'))
        
        df['levDistance'] = df['levDistance'].replace({'Levenshtein': 'LV'}, regex=True)
        df["lev_type"] = df["levDistance"] + " | " + df["type"]
        df['isMulti'] = df['type'].str.contains('/')
        justMulti = df[df['isMulti']].groupby('levDistance', as_index=False)['numOfReads'].sum()
        justMulti["lev_type"] = justMulti['levDistance'] + ' | Multiclass'
        
        df.drop(df[df['isMulti']].index, inplace=True)
        df = pd.concat([df,justMulti])
    
        
        df['percent of reads (unnormalized)'] = (df['numOfReads']/df['numOfReads'].sum())*100    
        df_list.append(df)
    dfMain = pd.concat(df_list, ignore_index=True)
    
    dfMain = dfMain[['lev_type', 'percent of reads (unnormalized)']].copy()

    dfMain.rename(columns={'lev_type':'type'}, inplace=True)
    
    return dfMain.sort_values('type')


def getMoleculeData(sampleNames):
    df_list = []
    
    for n in sampleNames: #speed
        df = pd.DataFrame(Molecule.objects.filter(sampleSource__icontains=n).values('description','numOfReads'))
        df['isMulti'] = df['description'].str.contains('/')
        justMulti = df[df['isMulti']]
        print(justMulti)
        justMulti['description'] = 'Multiclass'
        justMulti = justMulti.groupby('description', as_index=False)['numOfReads'].sum()
        df.drop(df[df['isMulti']].index, inplace=True)
        df = pd.concat([df,justMulti])
        
        df['percent of reads (unnormalized)'] = (df['numOfReads']/df['numOfReads'].sum())*100
        df_list.append(df)
   
    dfMain = pd.concat(df_list, ignore_index=True)
    dfMain = dfMain[['description', 'percent of reads (unnormalized)']].copy()
    dfMain.rename(columns={'description':'type'}, inplace=True)
    return dfMain.sort_values('type')

def getFormattedDataFrame(df):

    return df



def generateBoxplot(df, plotName, numOfSamples):
    t = "SummaryTable:" + plotName + " (n=" + str(numOfSamples) + " samples)"
    return px.box(df, y=df['percent of reads (unnormalized)'], x=df['type'], width=1200, height=600,color = 'type',title=t, range_y=[0,None]).to_html()


def trimTable(df, type):
    if type == "unknown":
        return df[['lev_type', 'numOfReads']]