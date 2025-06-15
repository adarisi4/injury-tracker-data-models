
{{ config(
    materialized='view'
) }}

WITH distinct_statuses AS (
    SELECT DISTINCT STATUS
    FROM {{ ref('stg_injuries') }}
    WHERE STATUS IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (ORDER BY STATUS) AS STATUS_ID,
    STATUS
FROM distinct_statuses
    
