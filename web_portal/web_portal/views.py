from django.http import HttpResponseRedirect
from django.shortcuts import render
import plotly.express as px
from .models import UnknownMolecule, Molecule
from .forms import SelectionForm

import pandas as pd
pd.options.plotting.backend = "plotly"

# import plotly.express as px


def getSelectedSamples(request):
    if request.method == 'POST':
        form = SelectionForm(request.POST)
        if form.is_valid():
            requestedSample = form.cleaned_data["selected"]
            unkRes = getUnknownMoleculeData(requestedSample)
            globRes = getMoleculeData(requestedSample)

            plot1 = plotUnknown(unkRes)
            # plot2 = plotUnknown(unkRes)
            plot2 = plotGlobal(globRes)
            return render(request, 'boxplots/sampleForm.html', {'form': form, 'plot1':plot1, 'plot2':plot2})
    else:
        form = SelectionForm()
        print("get")

    plot = 'box' #make the plot
    return render(request, 'boxplots/sampleForm.html', {'form': form})

def getUnknownMoleculeData(sampleNames):
    # result = []
    df_list = []
    
    for n in sampleNames:
        i = UnknownMolecule.objects.all().filter(sampleSource__icontains=n).values()
        # result.append(i)
        df = pd.DataFrame(i.values('levDistance','type','numOfReads'))
        df['levDistance'] = df['levDistance'].replace({'Levenshtein': 'LV'}, regex=True)
        df["lev_type"] = df["levDistance"] + " | " + df["type"]
 
        df_list.append(df)
    
    # unMerged = df_list[0]
    # for df_ in df_list[1:]:
    #     unMerged = unMerged.merge(df_, on="lev_type", how='outer')
    #     dfMain = pd.concat(dfMain, df_, join='outer')
   
    dfMain = pd.concat(df_list, ignore_index=True)
    # dfMain = dfMain.groupby('lev_type', as_index=False)['numOfReads'].sum()
    # dfMain['percentage'] = (dfMain['numOfReads']/dfMain['numOfReads'].sum())*100
    # dfFinal = dfMain.groupby('lev_type')['numOfReads'].sum()
    # print(df)
    # for i in result:
    #     print(pd.DataFrame(i.values('levDistance','type','numOfReads')))
    dfMain.drop(df.columns[[0, 1]], axis=1, inplace=True)

    dfMain['percent of reads (unnormalized)'] = (dfMain['numOfReads']/dfMain['numOfReads'].sum())*100
    dfMain.rename(columns={'lev_type':'type'}, inplace=True)
    print(dfMain)
    return dfMain


def getMoleculeData(sampleNames):
    # result = []
    df_list = []
    
    for n in sampleNames:
        i = Molecule.objects.all().filter(sampleSource__icontains=n).values()
        # result.append(i)
        df = pd.DataFrame(i.values('description','numOfReads')) 
        df_list.append(df)
   
    dfMain = pd.concat(df_list, ignore_index=True)
    dfMain['percent of reads (unnormalized)'] = (dfMain['numOfReads']/dfMain['numOfReads'].sum())*100
    dfMain.rename(columns={'description':'type'}, inplace=True)
    print(dfMain)
    return dfMain

def getFormattedDataFrame(df):

    return df


# def getPlot(df, n):
#     df.

def plotUnknown(df):
    # px.box(df, y=df.iloc[0])
    return px.box(df, y=df['percent of reads (unnormalized)'], x=df['type'], width=1200, height=600,color = 'type',title="SummaryTable:UNKOnly").to_html()

def plotGlobal(df):
    return px.box(df, y=df['percent of reads (unnormalized)'], x=df['type'], width=1200, height=600,color = 'type', title="SummaryTable:GlobalView").to_html()

# def renameCol(df):
#     df.columns = ['percent of reads (unnormalized)', 'type','percent of reads (unnormalized)']
#     return df