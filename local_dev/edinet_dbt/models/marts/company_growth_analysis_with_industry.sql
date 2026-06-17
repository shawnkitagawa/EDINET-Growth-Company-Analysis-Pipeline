-- depends_on: {{ ref('int_company_growth_analysis') }}
{{ config(materialized='table') }}

SELECT
    g.edinetCode,
    g.filerName,
    m.industry,
    m.secCode,
    m.fiscal_year_end,
    m.listing_status,
    m.has_consolidated,

    g.docID,
    g.periodStart,
    g.periodEnd,

    g.sales_5_years_ago,
    g.sales_4_years_ago,
    g.sales_3_years_ago,
    g.sales_2_years_ago,
    g.previous_sales,
    g.current_sales,

    g.one_year_growth_rate,
    g.four_year_total_growth_rate,
    g.four_year_cagr,
    g.five_year_growth_rate,
    g.two_year_consecutive_growth,
    g.four_year_consecutive_growth

FROM {{ ref('int_company_growth_analysis') }} g
LEFT JOIN edinet_company_master m
    ON g.edinetCode = m.edinetCode