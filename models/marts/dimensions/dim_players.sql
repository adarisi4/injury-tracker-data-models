{{ config(
    materialized='view'
) }}

WITH ranked_players AS (
    SELECT
        PLAYER_ID,
        PLAYER_NAME,
        ROW_NUMBER() OVER (
            PARTITION BY PLAYER_ID
            ORDER BY DATE_OF_INJURY
        ) AS rn
    FROM {{ ref('stg_injuries') }}
    WHERE PLAYER_ID IS NOT NULL
)

SELECT
    PLAYER_ID,
    PLAYER_NAME
FROM ranked_players
WHERE rn = 1
ORDER BY PLAYER_ID ASC
