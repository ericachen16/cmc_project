import os
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

path = "/Users/ericachen/Desktop/sampleData/"

def loadSamples():
    dir_list = os.listdir(path)
    print(dir_list)
    for f in dir_list:
        loadFile(f)

def loadFile(fileName):
    loc = "/Users/ericachen/Desktop/sampleData/" + fileName
    df = pd.read_csv(loc,sep='\t',skiprows=3,on_bad_lines='skip')

    conn_string = "postgresql://postgres:1234@localhost:5432/parsedSample"
    engine = create_engine(conn_string)
    unkTableName = "web_portal_unknownmolecule"
    globalTableName = "web_portal_molecule"

    start_row = df[df['Description'] == '# Unknown (unk) molecule analysis'].index[0]
    end_row = df[df['Description'] == '# Other frequency statistics'].index[0]

    unkData = df.iloc[start_row+1:end_row,:3]
    unkData.columns=unkData.iloc[0]
    unkData = unkData[1:]

    unkData.insert(len(unkData.columns),"Sample Name", fileName)

    globalData = df.iloc[:1].transpose().rename_axis("id")
    globalData.columns = globalData.iloc[0]
    globalData = globalData[1:].rename_axis("Description").reset_index()

    globalData.insert(len(globalData.columns),"Sample Name", fileName)

    unkData.to_sql(unkTableName, engine, if_exists='append', index=False)
    globalData.to_sql(globalTableName, engine, if_exists='append', index=False)

loadFile('data.DRX012360-tool-v0.0.4_summary.tsv')
loadFile('data.DRX012036-tool-v0.0.4_summary.tsv')
loadFile('data.DRX012035-tool-v0.0.4_summary.tsv')



