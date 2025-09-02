@echo off
setlocal enabledelayedexpansion

REM Initialize portfolio folders after cloning the repo
echo Creating folders...
mkdir project1_sales_dashboard
mkdir project2_forecasting
mkdir project3_churn_prediction
mkdir assets
mkdir data

echo Creating project subfolders and placeholder READMEs...
for %%d in (project1_sales_dashboard project2_forecasting project3_churn_prediction) do (
  mkdir %%d\data
  mkdir %%d\notebooks
  mkdir %%d\src
  echo # %%d> %%d\README.md
)

echo Done. Now add files, commit, and push!
