import csv
import os
import pandas as pd

class Peers_Retriever:
    
    ticker_dict = None
    companies_by_industry = dict()
    
    def __init__(self, path) -> None:
        self.path = path
        self.init_company_dataframe()
        
    def init_company_dataframe(self):
        df = pd.read_csv(self.path)
        df1 = df.iloc[:, 1:8]

        names = df1['Industry'].unique().tolist()
        dfs = dict(tuple(df1.groupby('Industry')))
        dct = dict()
        for industry in names:
            dct[industry] = dfs[industry]
        self.companies_by_industry = dct
    
    def topFivePeers(self, industry):
        return self.companies_by_industry[industry].iloc[:5]['Symbol'].unique().tolist()
        

        
        
# sp_path = os.path.join(os.path.dirname(__file__), r"data\sp500_companies.csv")
# peers = Peers_Retriever(sp_path)
# print(peers.topFivePeers('Semiconductors'))
# Semiconductors