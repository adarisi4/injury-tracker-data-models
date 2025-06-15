{{ config(
    materialized='view'
) }}

SELECT
    INJURY_ID,
    INJURY_DESCRIPTION,
    BODY_PART,
    STATUS,
    DATE_OF_INJURY,
    TODAY_DATE,
    PLAYER_ID,
    SPORTS_INJURY_ID,
    PLAYER_NAME
FROM {{ source('INJURY_SCHEMA', 'INJURIES') }}
