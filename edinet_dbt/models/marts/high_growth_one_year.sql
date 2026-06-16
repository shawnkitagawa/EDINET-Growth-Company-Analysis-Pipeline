-- depends_on: {{ ref('company_growth_analysis_with_industry') }}
{{ config(materialized='table') }}

SELECT *
FROM {{ ref('company_growth_analysis_with_industry') }}
WHERE one_year_growth_rate IS NOT NULL
  AND one_year_growth_rate >= 0.40
ORDER BY one_year_growth_rate DESC