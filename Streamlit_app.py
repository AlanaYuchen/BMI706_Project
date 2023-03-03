#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 09:47:14 2023

@author: chenghui
"""

import pandas as pd
import numpy as np
import altair as alt

clinical_df = pd.read_csv("clinical.tsv", delimiter = "\t")
family_df = pd.read_csv("family_history.tsv", delimiter = "\t")

# ================ clean clinical_df data ===============
# replace '-- with empty space and collapse columns with cancer stage to one
clinical_df = clinical_df.replace("'--","")
clinical_df = clinical_df.fillna('')

stage_columns = clinical_df.filter(regex=("stage.*"))
stage_columns.drop(axis = 1, columns = ["ajcc_clinical_stage", "ann_arbor_clinical_stage"])
agg_df = stage_columns.agg(lambda x: ''.join(x.astype(str)), axis=1)
clinical_df['stage'] = agg_df

# select columns of interest
clinical_df_filtered = clinical_df[['project_id', 'case_id','primary_diagnosis', 'ethnicity', 'gender', 'race', 'vital_status',
'stage', 'year_of_diagnosis', 'age_at_diagnosis', 'year_of_birth', 'year_of_death', 'site_of_resection_or_biopsy', 
'tissue_or_organ_of_origin', 'tumor_grade', 'days_to_death']]

# ================ clean family history data ================
family_df = family_df.replace("'--","")
family_df_filtered = family_df[['case_id', 'project_id', 
'relationship_gender', 'relationship_primary_diagnosis', 
'relationship_type', 'relative_with_cancer_history']]

# ================ merge both datasets ================
full_df = pd.merge(clinical_df_filtered, family_df_filtered, on = "case_id", how = "left")
full_df = full_df.replace("",np.nan)
full_df


# Visualization 1
## Part 1 and 2
# select columns of interest and drop NAs
Q1 = full_df[['tissue_or_organ_of_origin', 'gender', 'ethnicity', 
              'relative_with_cancer_history', 'relationship_type', 
              'relationship_primary_diagnosis', 'relationship_gender']]
Q1["relative_with_cancer_history"] = np.where(Q1["relative_with_cancer_history"] == "yes", 1, 0)
Q1 = Q1.dropna() 

# === bar chart 1: number of cases per cancer type with relatives who also have a history of cancer ===
 
# add selector 
select_cancer = alt.selection_single(encodings=["x"])

num_relatives_cancer_base = alt.Chart(Q1).properties(width = 400, height = 200)
num_relatives_cancer = num_relatives_cancer_base.mark_bar().encode(
  x = "tissue_or_organ_of_origin:N", 
  y = alt.Y("relative_with_cancer_history", aggregate = "sum"), 
  color = "tissue_or_organ_of_origin:N",
  tooltip = ["sum(relative_with_cancer_history)","tissue_or_organ_of_origin"],
  opacity=alt.condition(select_cancer, alt.value(1), alt.value(0.2))
).add_selection(
    select_cancer
)

# === bar chart 2 === 
num_relatives_cancer2 = num_relatives_cancer_base.mark_bar().encode(
    x = alt.X("relationship_primary_diagnosis:N", sort = '-y'),
    y = alt.Y(aggregate = "count"),
    color = alt.Color("relationship_type"),
    tooltip = ["relationship_primary_diagnosis", "relationship_type","count(relationship_type)"]
).transform_filter(
    select_cancer
)

num_relatives_cancer & num_relatives_cancer2

# Visualization 2
# Part1
alt.data_transformers.enable('default', max_rows=None)

# select columns of interest and drop NAs
Q2 = full_df[['year_of_diagnosis','primary_diagnosis','case_id', 'tissue_or_organ_of_origin','gender']]
Q2 = Q2.dropna()

# =================== visualization for task 2 ===================

# line chart
num_diagnosis_cancer_year = alt.Chart(Q2).mark_line(point=alt.OverlayMarkDef()).encode(
  x = "year_of_diagnosis:O", 
  y = alt.Y(aggregate = "count"), 
  color = "tissue_or_organ_of_origin:N",
  tooltip = [alt.Tooltip("tissue_or_organ_of_origin",title='Tissue or organ of origin'),alt.Tooltip("year_of_diagnosis:O",title='Year of diagnosis'), alt.Tooltip("count(year_of_diagnosis)",title='Count')]
)
num_diagnosis_cancer_year

# Part2
# bar chart 
num_diagnosis_cancer = alt.Chart(Q2).mark_bar().encode(
  x = alt.X("tissue_or_organ_of_origin:N", sort='-y'), 
  y = alt.Y(aggregate = "count"),
  color = 'gender', 
  tooltip = ["tissue_or_organ_of_origin","gender", "count(tissue_or_organ_of_origin)"]
)
num_diagnosis_cancer

#Visualization 3
## Part 1 & part 2
pd.to_numeric(Q3['age_at_diagnosis'])/365
Q3['age_at_diagnosis_year'] = pd.to_numeric(Q3['age_at_diagnosis'])/365
Q3 = full_df[['year_of_diagnosis','age_at_diagnosis','tissue_or_organ_of_origin','gender']]
Q3['age_at_diagnosis_year'] = pd.to_numeric(Q3['age_at_diagnosis'])/365
Q3 = Q3.dropna()

# add selector 
single = alt.selection_single(encodings=["color"])

# line chart
base = alt.Chart(Q3)
num_diagnosis_age_cancer = base.mark_line(point=alt.OverlayMarkDef()).encode(
  x = "year_of_diagnosis:O", 
  y = alt.Y("age_at_diagnosis_year:Q", aggregate = "mean"), 
  color = "tissue_or_organ_of_origin:N",
  tooltip = ["year_of_diagnosis","mean(age_at_diagnosis_year)","tissue_or_organ_of_origin"],
  opacity=alt.condition(single, alt.value(1), alt.value(0.2))
).add_selection(
    single
)

num_diagnosis_age_cancer2 = base.mark_boxplot().encode(
    x = "year_of_diagnosis:O",
    y = "age_at_diagnosis_year:Q"
).transform_filter(
    single
)
num_diagnosis_age_cancer & num_diagnosis_age_cancer2

# Visualization 4
## Part 1
# scatter plot between average age of death and diagnosis for each cancer type
Q4 = full_df[['year_of_diagnosis','age_at_diagnosis','tissue_or_organ_of_origin','year_of_death', 'year_of_birth']]
Q4['age_of_death'] = pd.to_numeric(Q4['year_of_death']) - pd.to_numeric(Q4['year_of_birth'])
Q4['age_at_diagnosis_year'] = pd.to_numeric(Q4['age_at_diagnosis'])/365
Q4 = Q4.dropna()

# line chart
diagnosis_death_age = alt.Chart(Q4).mark_circle(size=60, opacity = 0.7).encode(
  y = alt.Y("age_of_death:Q", aggregate = "mean"), 
  x = alt.X("age_at_diagnosis_year:Q", aggregate = "mean"), 
  color = "tissue_or_organ_of_origin:N",
  tooltip = ["mean(age_of_death)","mean(age_at_diagnosis_year)","tissue_or_organ_of_origin"]
)

diagnosis_death_age

## Part3
diagnosis_age_distribution = alt.Chart(Q4).mark_boxplot(opacity = 0.8).encode(
    x = "tissue_or_organ_of_origin:N",
    y = "age_at_diagnosis_year:Q",
    color = "tissue_or_organ_of_origin:N"
)
death_age_distribution = alt.Chart(Q4).mark_boxplot(opacity = 0.8).encode(
    x = "tissue_or_organ_of_origin:N",
    y = "age_of_death:Q",
    color = "tissue_or_organ_of_origin:N"
)

diagnosis_age_distribution & death_age_distribution

# Visualization 6
#subset one cancer type
Q6 = full_df[full_df["tissue_or_organ_of_origin"] == "Lung, NOS"]
Q6 = full_df[['stage', 'ethnicity', 'gender', 'age_at_diagnosis']]
Q6['age_at_diagnosis_year'] = pd.to_numeric(Q6['age_at_diagnosis'])/365
Q6 = Q6.dropna()

# bar chart 
cancerstage_gender = alt.Chart(Q6).mark_bar().encode(
  x = alt.X("stage:O", sort='-y'), 
  y = alt.Y(aggregate = "count"),
  color = 'gender', 
  tooltip = ["stage","gender", "count()"]
)
cancerstage_gender

diagnosisage_gender = alt.Chart(Q6).mark_bar(opacity = 0.8).encode(
  x = alt.X("age_at_diagnosis_year:Q"), 
  y = alt.Y(aggregate = "count"),
  color = 'gender', 
  tooltip = ["age_at_diagnosis_year","gender", "count()"]
)
cancerstage_gender & diagnosisage_gender



