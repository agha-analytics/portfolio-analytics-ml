# Validation Checks

This folder contains validation evidence for the cleaned `retail_sales` dataset.

---

## 1. sales_validation.xlsx
- **What it checks:**  
  - Row counts in SQL vs Excel  
  - Duplicate check on (Store, Dept, Date)  
  - Spot checks of random rows  
  - Summary statistics (MIN/AVG/MAX) for Weekly_Sales  
- **Result:**  
  - Duplicates found and removed in SQL.  
  - Excel confirms 0 duplicates remain.  
  - Row counts and summary statistics match SQL outputs.

---

## 2. stores_validation.xlsx
- **What it checks:**  
  - Duplicate check on Store column.  
- **Result:**  
  - No duplicates found.  
  - Primary Key enforced in SQL.

---

## 3. features_validation.xlsx
- **What it checks:**  
  - Duplicate check on (Store, Date).  
- **Result:**  
  - No duplicates found.  
  - Unique constraint enforced in SQL.

