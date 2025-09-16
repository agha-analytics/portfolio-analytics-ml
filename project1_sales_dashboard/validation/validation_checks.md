# Validation Checks

This folder contains validation evidence for the cleaned `retail_sales` dataset.

---

## 1. sales_validation.xlsx
- **What it checks:**  
  - Row counts in SQL   
  - Duplicate check on (Store, Dept, Date)  
  - Spot checks of random rows  
  - Summary statistics (MIN/AVG/MAX) for Weekly_Sales  
- **Result:**  
  - No duplicates found in SQL.    
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
 
    ## 📊 Data Validation

Validation was performed to ensure the cleaned dataset is correct.

- SQL validation queries are in [`sql/validation_checks.sql`](sql/validation_checks.sql)  
- Validation results are documented in [`validation/validation_checks.md`](validation/validation_checks.md)  


