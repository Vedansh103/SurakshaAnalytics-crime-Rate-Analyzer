import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

class CrimeAnalyzer:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)
        self.setup_data()
        
    def setup_data(self):
        self.df['year'] = pd.to_numeric(self.df['year'])
        self.states = sorted(self.df['state_name'].unique())
        self.years = sorted(self.df['year'].unique())
        self.crime_columns = [col for col in self.df.columns if col not in 
                             ['id', 'year', 'state_name', 'state_code', 'district_name', 
                              'district_code', 'registration_circles']]
        
    def get_districts_by_state(self, state_name):
        state_data = self.df[self.df['state_name'].str.contains(state_name, case=False, na=False)]
        return sorted(state_data['district_name'].unique())
    
    def get_district_crime_data(self, state_name, district_name, crime_type):
        district_data = self.df[
            (self.df['state_name'].str.contains(state_name, case=False, na=False)) &
            (self.df['district_name'].str.contains(district_name, case=False, na=False))
        ]
        
        if district_data.empty:
            return None
            
        yearly_data = district_data.groupby('year')[crime_type].sum().reset_index()
        return yearly_data.sort_values('year')
    
    def line_chart(self, state_name, district_name, crime_type):
        data = self.get_district_crime_data(state_name, district_name, crime_type)
        if data is None or data.empty:
            print("No data available")
            return
            
        plt.figure(figsize=(12, 6))
        plt.plot(data['year'], data[crime_type], marker='o', linewidth=2, markersize=8)
        plt.title(f'{crime_type.title()} Cases in {district_name}, {state_name}')
        plt.xlabel('Year')
        plt.ylabel(f'Number of {crime_type.title()} Cases')
        plt.grid(True, alpha=0.3)
        plt.xticks(data['year'])
        
        for i, row in data.iterrows():
            plt.annotate(f'{int(row[crime_type])}', 
                        (row['year'], row[crime_type]), 
                        textcoords="offset points", 
                        xytext=(0,10), ha='center')
        
        plt.tight_layout()
        plt.show()
    
    def bar_chart(self, state_name, district_name, crime_type):
        data = self.get_district_crime_data(state_name, district_name, crime_type)
        if data is None or data.empty:
            print("No data available")
            return
            
        plt.figure(figsize=(10, 6))
        bars = plt.bar(data['year'], data[crime_type], color='steelblue', alpha=0.7)
        plt.title(f'{crime_type.title()} Cases in {district_name}, {state_name}')
        plt.xlabel('Year')
        plt.ylabel(f'Number of {crime_type.title()} Cases')
        plt.xticks(data['year'])
        
        for bar, value in zip(bars, data[crime_type]):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(data[crime_type])*0.01,
                    f'{int(value)}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()
    
    def interactive_chart(self, state_name, district_name, crime_type):
        data = self.get_district_crime_data(state_name, district_name, crime_type)
        if data is None or data.empty:
            print("No data available")
            return
            
        fig = px.line(data, x='year', y=crime_type, 
                     title=f'{crime_type.title()} Cases in {district_name}, {state_name}',
                     markers=True)
        
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title=f"Number of {crime_type.title()} Cases",
            template='plotly_white'
        )
        
        fig.show()
    
    def pie_chart(self, state_name, district_name, crime_type):
        data = self.get_district_crime_data(state_name, district_name, crime_type)
        if data is None or data.empty:
            print("No data available")
            return
            
        plt.figure(figsize=(8, 8))
        plt.pie(data[crime_type], labels=data['year'], autopct='%1.1f%%')
        plt.title(f'{crime_type.title()} Cases Distribution by Year\n{district_name}, {state_name}')
        plt.show()
    
    def area_chart(self, state_name, district_name, crime_type):
        data = self.get_district_crime_data(state_name, district_name, crime_type)
        if data is None or data.empty:
            print("No data available")
            return
            
        plt.figure(figsize=(12, 6))
        plt.fill_between(data['year'], data[crime_type], alpha=0.7, color='lightblue')
        plt.plot(data['year'], data[crime_type], marker='o', linewidth=2, color='blue')
        plt.title(f'{crime_type.title()} Cases in {district_name}, {state_name}')
        plt.xlabel('Year')
        plt.ylabel(f'Number of {crime_type.title()} Cases')
        plt.grid(True, alpha=0.3)
        plt.xticks(data['year'])
        plt.tight_layout()
        plt.show()