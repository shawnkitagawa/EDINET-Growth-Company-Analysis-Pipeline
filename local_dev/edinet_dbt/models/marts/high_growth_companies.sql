-- depends_on: {{ ref('high_growth_four_year_cagr') }}
{{ config(materialized='table') }}

SELECT *
FROM {{ ref('high_growth_four_year_cagr') }}