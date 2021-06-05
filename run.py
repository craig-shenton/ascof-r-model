import pandas as pd
import numpy as np

# NOMIS API - Population estimates - local authority based by five year age band
url = "https://www.nomisweb.co.uk/api/v01/dataset/NM_31_1.data.csv?geography=1820327937...1820328318&date=latest&sex=7&age=0,22,25&measures=20100,20301&signature=NPK-be81606366125733ff591b:0x040ed4bb17cc73b3e5e08779f332feb87f777ac1"

df_population = pd.read_csv(url)
df_population = df_population[
    [
        "DATE",
        "GEOGRAPHY_NAME",
        "GEOGRAPHY_CODE",
        "GEOGRAPHY_TYPE",
        "AGE_NAME",
        "MEASURES_NAME",
        "OBS_VALUE",
    ]
]
df_population = df_population[df_population["GEOGRAPHY_CODE"].str.contains("E")]
df_population_pivot = df_population.pivot_table(
    index=["GEOGRAPHY_CODE"], columns=["AGE_NAME", "MEASURES_NAME"], values="OBS_VALUE"
).reset_index()
df_population_pivot.columns = df_population_pivot.columns.map("|".join).str.strip("|")

# NOMIS - annual population survey
url = "https://www.nomisweb.co.uk/api/v01/dataset/NM_17_5.data.csv?geography=1820327937...1820328307&date=latestMINUS4&variable=248,249,111,1487,1488,1537,290,720...722,335,344,18,45,558,564,197,202,434...437,1558,72,74,84&measures=20599,21001,21002,21003&signature=NPK-be81606366125733ff591b:0x6f9c2f37c9dfe740d3b6bb526a225b04981a766e"

df_survey = pd.read_csv(url)
df_survey = df_survey[
    [
        "DATE",
        "GEOGRAPHY_NAME",
        "GEOGRAPHY_CODE",
        "GEOGRAPHY_TYPE",
        "MEASURES_NAME",
        "VARIABLE_NAME",
        "OBS_VALUE",
    ]
]
df_survey = df_survey[df_survey["GEOGRAPHY_CODE"].str.contains("E")]
df_survey_pivot = df_survey.pivot_table(
    index=["GEOGRAPHY_CODE"],
    columns=["VARIABLE_NAME", "MEASURES_NAME"],
    values="OBS_VALUE",
).reset_index()
df_survey_pivot.columns = df_survey_pivot.columns.map("|".join).str.strip("|")

# NOMIS - annual survey of hours and earnings - workplace analysis
url = "https://www.nomisweb.co.uk/api/v01/dataset/NM_99_1.data.csv?geography=1820327937...1820328307&date=latestMINUS1&sex=7...9&item=2&pay=1,7&measures=20100,20701&signature=NPK-be81606366125733ff591b:0xf7da857b959a5cb57353190fa7936dfcab634697"

df_workplace = pd.read_csv(url)
df_workplace = df_workplace[
    [
        "DATE",
        "GEOGRAPHY_NAME",
        "GEOGRAPHY_CODE",
        "GEOGRAPHY_TYPE",
        "SEX_NAME",
        "PAY_NAME",
        "MEASURES_NAME",
        "OBS_VALUE",
    ]
]
df_workplace = df_workplace[df_workplace["GEOGRAPHY_CODE"].str.contains("E")]
df_workplace_pivot = df_workplace.pivot_table(
    index=["GEOGRAPHY_CODE"],
    columns=["SEX_NAME", "PAY_NAME", "MEASURES_NAME"],
    values="OBS_VALUE",
).reset_index()
df_workplace_pivot.columns = df_workplace_pivot.columns.map("|".join).str.strip("|")

# NOMIS - jobs density
url = "https://www.nomisweb.co.uk/api/v01/dataset/NM_57_1.data.csv?geography=1820327937...1820328318&date=latest&item=1,3&measures=20100&signature=NPK-be81606366125733ff591b:0x70612ce5fbfa17433bcee945bf28f28a577360ea"

df_density = pd.read_csv(url)
df_density = df_density[
    [
        "DATE",
        "GEOGRAPHY_NAME",
        "GEOGRAPHY_CODE",
        "GEOGRAPHY_TYPE",
        "ITEM_NAME",
        "MEASURES_NAME",
        "OBS_VALUE",
    ]
]
df_density = df_density[df_density["GEOGRAPHY_CODE"].str.contains("E")]
df_density_pivot = df_density.pivot_table(
    index=["GEOGRAPHY_CODE"], columns=["ITEM_NAME", "MEASURES_NAME"], values="OBS_VALUE"
).reset_index()
df_density_pivot.columns = df_density_pivot.columns.map("|".join).str.strip("|")

# NOMIS - Claimant count
url = "https://www.nomisweb.co.uk/api/v01/dataset/NM_162_1.data.csv?geography=1820327937...1820328318&date=latestMINUS24&gender=0&age=0&measure=1...4&measures=20100&signature=NPK-be81606366125733ff591b:0x99686c2f446d8780bff53420853b01198f62baad"

df_claim = pd.read_csv(url)
df_claim = df_claim[
    [
        "DATE",
        "GEOGRAPHY_NAME",
        "GEOGRAPHY_CODE",
        "GEOGRAPHY_TYPE",
        "MEASURE_NAME",
        "OBS_VALUE",
    ]
]
df_claim = df_claim[df_claim["GEOGRAPHY_CODE"].str.contains("E")]
df_claim_pivot = df_claim.pivot_table(
    index=["GEOGRAPHY_CODE"], columns=["MEASURE_NAME"], values="OBS_VALUE"
).reset_index()

# London Min Wage
url = "https://opendata.arcgis.com/datasets/3ba3daf9278f47daba0f561889c3521a_0.csv"

df_london = pd.read_csv(url)
df_london["london_min_wage"] = np.where(df_london["RGN19NM"] == "London", True, False)
df_london.drop(list(df_london.filter(["FID", "LAD19NM"])), axis=1, inplace=True)

# ODS Code 2019 index file
url = "https://opendata.arcgis.com/datasets/c3ddcd23a15c4d7985d8b36f1344b1db_0.csv"

df_index = pd.read_csv(url)
df_index = df_index[df_index["LAD19CD"].str.contains("E")]

# Merge to master file
merged_master = pd.merge(df_index, df_london, on=["LAD19CD"], how="left")
merged_master = pd.merge(
    merged_master,
    df_survey_pivot,
    left_on=["LAD19CD"],
    right_on=["GEOGRAPHY_CODE"],
    how="left",
)
merged_master = pd.merge(
    merged_master,
    df_population_pivot,
    left_on=["LAD19CD"],
    right_on=["GEOGRAPHY_CODE"],
    how="left",
)
merged_master = pd.merge(
    merged_master,
    df_density_pivot,
    left_on=["LAD19CD"],
    right_on=["GEOGRAPHY_CODE"],
    how="left",
)
merged_master = pd.merge(
    merged_master,
    df_workplace_pivot,
    left_on=["LAD19CD"],
    right_on=["GEOGRAPHY_CODE"],
    how="left",
)
merged_master = pd.merge(
    merged_master,
    df_claim_pivot,
    left_on=["LAD19CD"],
    right_on=["GEOGRAPHY_CODE"],
    how="left",
)
merged_master.drop(
    list(merged_master.filter(regex="GEOGRAPHY_CODE")), axis=1, inplace=True
)
merged_master.reset_index().to_csv("data/master_file.csv", index=False)

col_list = list(merged_master.columns)
df = pd.DataFrame(col_list)

# saving the dataframe
df.to_csv("data/metrics.csv")
