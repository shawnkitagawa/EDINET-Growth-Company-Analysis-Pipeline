-- depends_on: {{ ref('int_company_latest_annual_report') }}
{{ config(materialized='table') }}

SELECT
    f.edinetCode,
    f.filerName,
    f.docID,
    f.periodStart,
    f.periodEnd,

    r.sales_5_years_ago,
    r.sales_4_years_ago,
    r.sales_3_years_ago,
    r.sales_2_years_ago,
    r.previous_sales,
    r.current_sales,

    CASE
        WHEN r.current_sales IS NULL THEN NULL
        WHEN r.previous_sales IS NULL THEN NULL
        WHEN r.previous_sales = 0 THEN NULL
        ELSE (r.current_sales - r.previous_sales) * 1.0 / r.previous_sales
    END AS one_year_growth_rate,

    CASE
        WHEN r.current_sales IS NULL THEN NULL
        WHEN r.sales_4_years_ago IS NULL THEN NULL
        WHEN r.sales_4_years_ago = 0 THEN NULL
        ELSE (r.current_sales - r.sales_4_years_ago) * 1.0 / r.sales_4_years_ago
    END AS four_year_total_growth_rate,

    CASE
        WHEN r.current_sales IS NULL THEN NULL
        WHEN r.sales_4_years_ago IS NULL THEN NULL
        WHEN r.sales_4_years_ago <= 0 THEN NULL
        WHEN r.current_sales <= 0 THEN NULL
        ELSE POWER(r.current_sales * 1.0 / r.sales_4_years_ago, 1.0 / 4) - 1
    END AS four_year_cagr,

    CASE
        WHEN r.current_sales IS NULL THEN NULL
        WHEN r.sales_5_years_ago IS NULL THEN NULL
        WHEN r.sales_5_years_ago = 0 THEN NULL
        ELSE (r.current_sales - r.sales_5_years_ago) * 1.0 / r.sales_5_years_ago
    END AS five_year_growth_rate,

    CASE
        WHEN r.sales_2_years_ago IS NOT NULL
         AND r.previous_sales IS NOT NULL
         AND r.current_sales IS NOT NULL
         AND r.sales_2_years_ago > 0
         AND r.previous_sales > r.sales_2_years_ago
         AND r.current_sales > r.previous_sales
        THEN TRUE
        ELSE FALSE
    END AS two_year_consecutive_growth,

    CASE
        WHEN r.sales_4_years_ago IS NOT NULL
         AND r.sales_3_years_ago IS NOT NULL
         AND r.sales_2_years_ago IS NOT NULL
         AND r.previous_sales IS NOT NULL
         AND r.current_sales IS NOT NULL
         AND r.sales_4_years_ago > 0
         AND r.sales_3_years_ago > r.sales_4_years_ago
         AND r.sales_2_years_ago > r.sales_3_years_ago
         AND r.previous_sales > r.sales_2_years_ago
         AND r.current_sales > r.previous_sales
        THEN TRUE
        ELSE FALSE
    END AS four_year_consecutive_growth

FROM {{ ref('int_company_latest_annual_report') }} f
LEFT JOIN {{ ref('int_annual_report_revenue') }} r
    ON f.docID = r.docID