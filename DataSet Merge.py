import pandas as pd

df1 = pd.read_csv("Dataset\districtwise-missing-persons-2021-onwards-cleaned.csv")

df2 = pd.read_csv("Dataset\districtwise-missing-persons-20172020-cleaned.csv")


common_cols = list(set(df1.columns) & set(df2.columns))

# Keep only common columns from both DataFrames
df1_common = df1[common_cols]
df2_common = df2[common_cols]

# Merge (stack vertically)
merged_df = pd.concat([df1_common, df2_common], ignore_index=True)

print("Shape of the merged DataFrame:", merged_df.shape)
print("Common columns:", common_cols)
print(merged_df.head())