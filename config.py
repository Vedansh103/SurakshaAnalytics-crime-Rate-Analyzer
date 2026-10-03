# config.py
# Configuration and constants for crime analysis tool

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import sys
import os
from pathlib import Path

# Import plotly and scipy (required packages)
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from scipy.stats import pearsonr

# Seaborn defaults
sns.set(style="whitegrid", palette="deep")

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.absolute()
DATASET_DIR = SCRIPT_DIR / "Dataset"

# Crime Categories Definition
CRIME_CATEGORIES = {
    'Violent Crimes': [
        'murder', 'culpable homicide not amounting to murder', 'attempt to murder',
        'causing death by negligence', 'rape', 'attempt to commit rape', 'custodial rape',
        'other rape', 'kidnapping and abduction', 'kidnapping and abduction of women and girls',
        'kidnapping and abduction of others', 'dacoity', 'preparation and assembly for dacoity',
        'robbery', 'riots', 'criminal intimidation', 'assault on women with intent to outrage her modesty',
        'insult to modesty of women', 'cruelty by husband or his relatives', 'importation of girls from foreign countries',
        'causing hurt', 'grievous hurt', 'dowry deaths', 'assault on public servant to deter him from duty',
        'voluntarily causing hurt to deter public servant from duty'
    ],
    'Property Crimes': [
        'theft', 'auto theft', 'burglary', 'criminal breach of trust', 'cheating',
        'counterfeiting', 'arson', 'mischief', 'criminal trespass', 'house-breaking',
        'house trespass', 'theft by servant', 'dishonest misappropriation of property',
        'receiving stolen property', 'criminal misappropriation', 'breach of trust by public servant',
        'breach of trust by banker, merchant or agent'
    ],
    'Economic Crimes': [
        'criminal breach of trust', 'cheating', 'counterfeiting', 'forgery',
        'forgery of valuable security, will, etc', 'forgery for purpose of cheating',
        'using as genuine a forged document', 'currency offences', 'breach of trust by public servant',
        'breach of trust by banker, merchant or agent', 'dishonest misappropriation of property',
        'criminal misappropriation', 'preparing false evidence'
    ],
    'Public Order Crimes': [
        'riots', 'unlawful assembly', 'promoting enmity between different groups',
        'imputations, assertions prejudicial to national-integration', 'public nuisance',
        'negligent conduct with respect to machinery', 'negligent conduct with respect to fire or combustible matter',
        'disobedience to order duly promulgated by public servant', 'threat of injury to public servant',
        'public servant disobeying direction of law', 'public servant framing an incorrect document'
    ],
    'Cyber Crimes': [
        'cyber crimes', 'cybercrime', 'online fraud', 'identity theft', 'hacking',
        'cyber stalking', 'cyber bullying', 'online harassment', 'data theft',
        'credit card fraud', 'internet fraud', 'phishing', 'malware'
    ],
    'Women & Children Crimes': [
        'rape', 'attempt to commit rape', 'custodial rape', 'other rape',
        'assault on women with intent to outrage her modesty', 'insult to modesty of women',
        'cruelty by husband or his relatives', 'dowry deaths', 'importation of girls from foreign countries',
        'kidnapping and abduction of women and girls', 'selling of girls for prostitution',
        'buying of girls for prostitution', 'trafficking', 'immoral traffic (prevention) act',
        'protection of children from sexual offences act', 'child marriage', 'juvenile crimes'
    ]
}

# Risk Score Weights for different crime categories
RISK_WEIGHTS = {
    'Violent Crimes': 3.0,      # Highest weight - most serious
    'Women & Children Crimes': 2.8,
    'Cyber Crimes': 2.0,
    'Property Crimes': 1.5,
    'Economic Crimes': 1.3,
    'Public Order Crimes': 1.2,
    'Drug & Substance': 1.8,
    'Traffic & Vehicle': 1.0    # Lowest weight
}