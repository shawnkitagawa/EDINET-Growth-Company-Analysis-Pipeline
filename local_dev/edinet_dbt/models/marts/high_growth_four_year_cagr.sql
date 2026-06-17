-- depends_on: {{ ref('company_growth_analysis_with_industry') }}
{{ config(materialized='table') }}

SELECT *
FROM {{ ref('company_growth_analysis_with_industry') }}
WHERE four_year_cagr IS NOT NULL
  AND four_year_cagr >= 0.40
  AND sales_4_years_ago >= 100000000
ORDER BY four_year_cagr DESC