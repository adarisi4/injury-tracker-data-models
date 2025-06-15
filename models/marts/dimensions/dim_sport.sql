{{ config(
    materialized='view'
) }}

SELECT DISTINCT
    SPORTS_INJURY_ID AS SPORT_ID,
    CASE 
        WHEN SPORTS_INJURY_ID = 1 THEN 'Football'
        WHEN SPORTS_INJURY_ID = 2 THEN 'Basketball'
        WHEN SPORTS_INJURY_ID = 3 THEN 'Baseball'
        WHEN SPORTS_INJURY_ID = 4 THEN 'Hockey'
        ELSE NULL
    END AS SPORT
FROM {{ ref('stg_injuries') }}
WHERE SPORTS_INJURY_ID IS NOT NULL

