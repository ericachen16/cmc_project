import os
import pandas as pd
from sqlalchemy import create_engine

path = '' # directory of where your dataset files are located goes here

def loadFile(fileName):
    loc = path + fileName
    df = pd.read_csv(loc,sep='\t',skiprows=3,on_bad_lines='skip')

    # connect to db
    conn_string = 'postgresql://postgres:1234@localhost:5432/parsedSample'
    engine = create_engine(conn_string)
    unkTableName = 'web_portal_unknownmolecule'
    globalTableName = 'web_portal_molecule'

    # unknown molecule analysis data
    start_row = df[df['Description'] == '# Unknown (unk) molecule analysis'].index[0]
    end_row = df[df['Description'] == '# Other frequency statistics'].index[0]

    unkData = df.iloc[start_row+1:end_row,:3]
    unkData.columns=unkData.iloc[0]
    unkData = unkData[1:]

    unkData.insert(len(unkData.columns),'Sample Name', fileName)

    # global view data
    globalData = df.iloc[:1].transpose().rename_axis('id')
    globalData.columns = globalData.iloc[0]
    globalData = globalData[1:].rename_axis('Description').reset_index()

    globalData.insert(len(globalData.columns),'Sample Name', fileName)

    # save to db
    unkData.to_sql(unkTableName, engine, if_exists='append', index=False)
    globalData.to_sql(globalTableName, engine, if_exists='append', index=False)

loadFile('data.DRX012360-tool-v0.0.4_summary.tsv')
loadFile('data.DRX012036-tool-v0.0.4_summary.tsv')
loadFile('data.DRX012035-tool-v0.0.4_summary.tsv')



