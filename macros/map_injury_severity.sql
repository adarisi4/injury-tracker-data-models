{% macro map_injury_severity(status_col) %}
    CASE
        WHEN {{ status_col }} = 'Day-to-Day' THEN 5
        WHEN {{ status_col }} = 'Questionable' THEN 4
        WHEN {{ status_col }} = 'Out' THEN 3
        WHEN {{ status_col }} LIKE '%IL%' THEN 2
        WHEN {{ status_col }} = 'Injured Reserve' THEN 1
        ELSE 0
    END
{% endmacro %}
