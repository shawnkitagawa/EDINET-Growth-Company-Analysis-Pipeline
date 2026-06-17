{{ config(materialized='table') }}

SELECT
    docID,

    MAX(CASE
        WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
         AND context_id = 'Prior5YearDuration'
        THEN TRY_CAST(value_text AS BIGINT)
    END) AS sales_5_years_ago,

    MAX(CASE
        WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
         AND context_id = 'Prior4YearDuration'
        THEN TRY_CAST(value_text AS BIGINT)
    END) AS sales_4_years_ago,

    MAX(CASE
        WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
         AND context_id = 'Prior3YearDuration'
        THEN TRY_CAST(value_text AS BIGINT)
    END) AS sales_3_years_ago,

    MAX(CASE
        WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
         AND context_id = 'Prior2YearDuration'
        THEN TRY_CAST(value_text AS BIGINT)
    END) AS sales_2_years_ago,

    MAX(CASE
        WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
         AND context_id = 'Prior1YearDuration'
        THEN TRY_CAST(value_text AS BIGINT)
    END) AS previous_sales,

    MAX(CASE
        WHEN element_id = 'jpcrp_cor:NetSalesSummaryOfBusinessResults'
         AND context_id = 'CurrentYearDuration'
        THEN TRY_CAST(value_text AS BIGINT)
    END) AS current_sales

FROM raw_annual_report_values
GROUP BY docID