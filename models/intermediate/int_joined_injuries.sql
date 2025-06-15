{{ config(
    materialized='view'
) }}

SELECT
    i.INJURY_ID,
    i.PLAYER_ID,
    s.STATUS_ID,
    b.BODY_PART_ID,
    sp.SPORT_ID,
    i.INJURY_DESCRIPTION,
    i.DATE_OF_INJURY,
    i.TODAY_DATE,
    i.INJURY_SEVERITY

FROM {{ ref('int_injury_severity') }} i
LEFT JOIN {{ ref('dim_status') }} s
    ON i.STATUS = s.STATUS
LEFT JOIN {{ ref('dim_body_part') }} b
    ON i.BODY_PART = b.BODY_PART
LEFT JOIN {{ ref('dim_sport') }} sp
    ON i.SPORTS_INJURY_ID = sp.SPORT_ID

