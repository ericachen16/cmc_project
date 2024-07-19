import plotly.express as px
import pandas as pd
from django.shortcuts import render
from .models import UnknownMolecule, Molecule
from .forms import SelectionForm

def getSelectedSamples(request):
    if request.method == 'POST':
        form = SelectionForm(request.POST)
        if form.is_valid():
            # sample selected
            requestedSample = form.cleaned_data['selected']

            # dataframe with just type and percent
            unkRes = getUnknownMoleculeData(requestedSample)
            globRes = getMoleculeData(requestedSample)

            # boxplot in html
            plot1 = generateBoxplot(globRes,'GlobalView',len(requestedSample))
            plot2 = generateBoxplot(unkRes, 'UNKOnly',len(requestedSample))

            return render(request, 'boxplots/sampleForm.html', {'form': form, 'plot1':plot1, 'plot2':plot2})
    else:
        form = SelectionForm()
    return render(request, 'boxplots/sampleForm.html', {'form': form})


def getUnknownMoleculeData(sampleNames):
    df_list = []
    
    # dataframe for each dataset chosen
    for n in sampleNames:
        df = pd.DataFrame(UnknownMolecule.objects.all().filter(sampleSource__icontains=n).values('levDistance','type','numOfReads'))
        
        # shorten and combine description
        df['levDistance'] = df['levDistance'].replace({'Levenshtein': 'LV'}, regex=True)
        df['lev_type'] = df['levDistance'] + ' | ' + df['type']

        # handle multiclass
        df['isMulti'] = df['type'].str.contains('/')
        justMulti = df[df['isMulti']].groupby('levDistance', as_index=False)['numOfReads'].sum()
        justMulti['lev_type'] = justMulti['levDistance'] + ' | multiclass'
        df.drop(df[df['isMulti']].index, inplace=True)
        df = pd.concat([df,justMulti])
    
        df['percent of reads (unnormalized)'] = (df['numOfReads']/df['numOfReads'].sum())*100  

        df_list.append(df)
 
    return readyDataFramesForPlot(df_list, 'unknown')


def getMoleculeData(sampleNames):
    df_list = []
    
    for n in sampleNames: 
        df = pd.DataFrame(Molecule.objects.filter(sampleSource__icontains=n).values('description','numOfReads'))
        
        # handle multiclass
        df['isMulti'] = df['description'].str.contains('/')
        justMulti = df[df['isMulti']]
        justMulti['description'] = 'multiclass'
        justMulti = justMulti.groupby('description', as_index=False)['numOfReads'].sum()
        df.drop(df[df['isMulti']].index, inplace=True)
        df = pd.concat([df,justMulti])
        
        df['percent of reads (unnormalized)'] = (df['numOfReads']/df['numOfReads'].sum())*100

        df_list.append(df)
   
    return readyDataFramesForPlot(df_list,'global')

def generateBoxplot(df, plotName, numOfSamples):
    t = 'SummaryTable:' + plotName + ' (n=' + str(numOfSamples) + ' samples)'
    return px.box(df, y=df['percent of reads (unnormalized)'], x=df['type'], width=1100, height=500,color = 'type',title=t, range_y=[0,None]).to_html()

def readyDataFramesForPlot(df_list, type):
    d = {
        'unknown': 'lev_type',
        'global': 'description'
    }
    dfMain = pd.concat(df_list, ignore_index=True)
    dfMain = dfMain[[d[type], 'percent of reads (unnormalized)']].copy()
    dfMain.rename(columns={d[type]:'type'}, inplace=True)
    return dfMain.sort_values('type')