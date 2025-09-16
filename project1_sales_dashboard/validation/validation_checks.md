# 🧾 Data Validation

This folder contains validation queries and evidence for the **`retail_sales`** dataset after cleaning.  
The goal is to confirm data integrity, enforce constraints, and document results in a reproducible way.

---

## 🔹 Files

- **[`../sql/validation_checks.sql`](../sql/validation_checks.sql)**  
  SQL script with all validation queries (row counts, duplicate checks, nulls, referential integrity, summary stats, and constraint checks).

- **[`validation_checks.md`](validation_checks.md)**  
  Documentation of validation outcomes (summary of results from running the SQL queries).

- *evidence file*  
  - CSV exports of duplicate checks .  

---

## 🔹 Validation Steps

1. **Row Counts**  
   - Compare counts across `sales`, `stores`, and `features`.  
   - ✅ Confirmed expected number of rows.

2. **Duplicate Checks**  
   - `sales`: `(Store, Dept, Date)` must be unique.  
   - `stores`: `(Store)` must be unique.  
   - `features`: `(Store, Date)` must be unique.  
   - ✅ No duplicates found after cleaning.

3. **Null / Invalid Checks**  
   - Keys (`Store`, `Dept`, `Date`) must not be NULL.  
   - `Weekly_Sales` must not be NULL or negative.  
   - `IsHoliday` must be 0 or 1.  
   - ✅ All conditions satisfied.

4. **Referential Integrity**  
   - All `sales.Store` values exist in `stores`.  
   - All `(Store, Date)` in `sales` exist in `features`.  
   - ✅ No orphan records.

5. **Summary Statistics**  
   - Min/Avg/Max of `Weekly_Sales` calculated for benchmarking with Excel validation.  
   - ✅ Excel results matched SQL outputs.

6. **Constraint Validation**  
   - Verified unique keys and primary keys exist:  
     - `sales` → `uq_sales_store_dept_date`  
     - `features` → `uq_features_store_date`  
     - `stores` → primary key on `Store`  
   - ✅ Constraints enforced.

7. **Spot Checks (Optional)**  
   - Random rows sampled with `ORDER BY RAND() LIMIT 10`.  
   - ✅ Manual checks aligned with expectations.

---

## ✅ Conclusion

The `retail_sales` dataset is now:
- Free of duplicates  
- Protected by **unique constraints**  
- Free of null/invalid keys  
- Referentially consistent across tables  
- Verified with both **SQL queries** 

This dataset now is ready for reliable analysis and reporting.
