-- depends_on: {{ ref('int_annual_reports_latest_version') }}
{{ config(materialized='table') }}

SELECT * EXCLUDE(row_num)
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY edinetCode
            ORDER BY periodEnd DESC, submitDateTime DESC
        ) AS row_num
    FROM {{ ref('int_annual_reports_latest_version') }}
)
WHERE row_num = 1