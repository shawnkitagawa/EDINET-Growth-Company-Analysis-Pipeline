{{ config(materialized='view') }}

SELECT
    docID,
    edinetCode,
    filerName,
    docDescription,

    COALESCE(
        periodStart,
        TRY_CAST(
            REPLACE(
                regexp_extract(docDescription, '\((\d{4}/\d{2}/\d{2})－', 1),
                '/',
                '-'
            ) AS DATE
        )
    ) AS periodStart,

    COALESCE(
        periodEnd,
        TRY_CAST(
            REPLACE(
                regexp_extract(docDescription, '－(\d{4}/\d{2}/\d{2})\)', 1),
                '/',
                '-'
            ) AS DATE
        )
    ) AS periodEnd,

    submitDateTime,
    formCode,
    docTypeCode,
    fetchDate

FROM document_metadata
WHERE docTypeCode IN ('120', '130')
  AND formCode IN ('030000', '030001')