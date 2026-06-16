
{{ config(materialized='table') }}

SELECT * EXCLUDE(row_num)
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY edinetCode, periodStart, periodEnd
            ORDER BY submitDateTime DESC
        ) AS row_num
    FROM {{ ref('stg_annual_reports_cleaned') }}
)
WHERE row_num = 1