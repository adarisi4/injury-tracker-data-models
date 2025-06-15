{{ config(
    materialized='table'
) }}

SELECT
    i.INJURY_ID,
    i.PLAYER_ID,
    i.SPORT_ID,
    i.BODY_PART_ID,
    i.STATUS_ID,
    i.INJURY_DESCRIPTION,
    i.DATE_OF_INJURY,
    i.TODAY_DATE,
    i.INJURY_SEVERITY
FROM {{ ref('int_joined_injuries') }} i
