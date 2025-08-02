import csv
import os
import pandas as pd

class Peers_Retriever:
    
    def __init__(self, path) -> None:
        self.path = path
        self.companies_by_industry = dict()
        self.companies_by_sector = dict()
        self.init_company_dataframe()
        
    def init_company_dataframe(self):
        df = pd.read_csv(self.path)
        df_filtered = df[['Sector', 'Industry', 'Symbol', 'Shortname', 'Marketcap', 'Currentprice']]
        
        # Group by Industry
        industry_groups = dict(tuple(df_filtered.groupby('Industry')))
        self.companies_by_industry = {k: v for k, v in industry_groups.items()}
        
        # Group by Sector
        sector_groups = dict(tuple(df_filtered.groupby('Sector')))
        self.companies_by_sector = {k: v for k, v in sector_groups.items()}
    
    def top_five_peers_by_industry(self, industry):
        if industry not in self.companies_by_industry:
            return []
        return self.companies_by_industry[industry].iloc[:5]['Symbol'].unique().tolist()
    
    def top_five_peers_by_sector(self, sector):
        if sector not in self.companies_by_sector:
            return []
        return self.companies_by_sector[sector].iloc[:5]['Symbol'].unique().tolist()

        

        
        
# sp_path = os.path.join(os.path.dirname(__file__), r"data\sp500_companies.csv")
# peers = Peers_Retriever(sp_path)
# print(peers.topFivePeers('Semiconductors'))
# Semiconductors