{{ config(
    materialized='view'
) }}

SELECT
    *,
    {{ map_injury_severity('STATUS') }} AS INJURY_SEVERITY
FROM {{ ref('stg_injuries') }}
WHERE STATUS IS NOT NULL

