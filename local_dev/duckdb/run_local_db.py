from pathlib import Path 
import duckdb
from tabulate import tabulate

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT/'LOCAL_DEV'/ 'data'/'processed'/'edinet.duckdb'
SAMPLE_DATA = ROOT/'LOCAL_DEV'/'data'/'raw'


conn = duckdb.connect(DB_PATH)

# result = conn.execute(f"""
#                 SELECT'document_metadata_raw' AS table_name, COUNT(*) AS row_count FROM document_metadata_raw 
#                       UNION ALL
#                 SELECT 'edinet_company_master_raw', COUNT(*) FROM edinet_company_master_raw
#                       UNION ALL 

#                 SELECT 'raw_annual_report_values', COUNT(*) FROM raw_annual_report_values
#                 ORDER BY row_count DESC     
#                       """).fetchdf()


# print(result)

result = conn.execute(f"""

            SELECT * FROM raw_annual_report_values
            LIMIT 10
                      
                      """).fetchdf()


result = conn.execute(f"""
            SELECT docID, COUNT(*) AS row_count 
            FROM raw_annual_report_values
            GROUP BY docID 
            ORDER BY row_count DESC
            LIMIT 10
                      
                      """).df()


result = conn.execute(f"""
            SELECT docID, COUNT(*) AS row_count
            FROM document_metadata_raw
            GROUP BY docID HAVING COUNT(*) > 1 
            ORDER BY row_count DESC;
                      """).fetchdf()

result = conn.execute(f"""
            SELECT docID, item_name, context_id , value_text, element_id,  COUNT(*) AS row_count
            FROM raw_annual_report_values
            GROUP BY docID, item_name, context_id, value_text, element_id
            HAVING COUNT(*) > 1 
            ORDER BY row_count DESC
                      
                      """).fetchdf()



result = conn.execute(f"""

                SELECT * FROM document_metadata_raw
                LIMIT 10
                      """).fetchdf()


result = conn.execute(f"""
                SELECT docID, COUNT(*) AS row_count
                FROM document_metadata_raw 
                GROUP BY docID
                HAVING COUNT(*) > 1 
                ORDER BY row_count DESC
                LIMIT 20 
                      """).fetchdf()

result = conn.execute(f"""
            SELECT * FROM raw_annual_report_values
            LIMIT 10
                      """).fetchdf()

result = conn.execute("""
    SELECT
        docID,
        item_name , 
        value_text, 
        COUNT(*) AS row_count
    FROM raw_annual_report_values
    GROUP BY
        docID,
        item_name,
        value_text
    HAVING COUNT(*) > 1
    ORDER BY row_count DESC
    LIMIT 10
""").fetch_df()


result = conn.execute(f"""
        SELECT docID, element_id ,item_name, context_id, relative_year, consolidated_type, period_type,value_text, COUNT(*) AS row_count 
        FROM raw_annual_report_values
        GROUP BY docID, element_id , item_name, context_id, relative_year, consolidated_type, period_type, value_text
        HAVING  COUNT(*) > 1 
        ORDER BY row_count DESC 
        LIMIT 10 
                      """).fetchdf()

result = conn.execute(f"""
        SELECT docID, element_id ,item_name, context_id, relative_year, consolidated_type, period_type,value_text, COUNT(*) AS row_count 
        FROM stg_annual_report_values_cleaned
        GROUP BY docID, element_id , item_name, context_id, relative_year, consolidated_type, period_type, value_text
        HAVING  COUNT(*) > 1 
        ORDER BY row_count DESC 
        LIMIT 10 
                      """).fetchdf()


# result = conn.execute(f"""

#         SELECT *
#         FROM raw_annual_report_values 
#         WHERE docID = 'S100XTNW' AND item_name is NULL 
#         ORDER BY context_id, relative_year, consolidated_type, period_type
#         LIMIT 10; 
#                       """).fetchdf()

result = conn.execute(f"""
            SELECT 
                    COUNT(*) AS total_rows, 
                    COUNT(*) FILTER(WHERE docID is NULL) AS docID, 
                    COUNT(*) FILTER(WHERE item_name is NULL) AS null_item_name, 
                    COUNT(*) FILTER(WHERE element_id is NULL) AS null_element_id, 
                    COUNT(*) FILTER(WHERE value_text is NULL) AS null_value_text, 
                      
                 
            FROM stg_annual_report_values_cleaned
            
                      """).fetchdf()

result = conn.execute(f"""
            SELECT
                COUNT(*) AS total_rows, 
                SUM(CASE WHEN docID is NULL THEN 1 ELSE 0 END) AS null_doc_id, 
                SUM(CASE WHEN item_name is NULL THEN 1 ELSE 0 END) AS null_item_name, 
                SUM(CASE WHEN element_id is NULL THEN 1 ELSE 0 END) AS null_element_id, 
                SUM(CASE WHEN value_text is NULL THEN 1 ElSE 0 END) AS null_value_text
                      
                FROM stg_annual_report_values_cleaned
                      
                      """).fetchdf()


result = conn.execute(f"""
        SELECT value_text , COUNT(*) as count_row
        FROM stg_annual_report_values_cleaned
        WHERE value_text IS NOT NULL AND TRY_CAST(value_text AS DOUBLE) IS NULL 
        GROUP BY value_text 
        ORDER BY count_row DESC
        LIMIT 20; 
                      """).fetchdf()





print(result) 
conn.close()