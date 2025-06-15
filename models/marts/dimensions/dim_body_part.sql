{{ config(
    materialized='view'
) }}

WITH distinct_parts AS (
    SELECT DISTINCT BODY_PART
    FROM {{ ref('stg_injuries') }}
    WHERE BODY_PART IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (ORDER BY BODY_PART) AS BODY_PART_ID,
    BODY_PART
FROM distinct_parts

