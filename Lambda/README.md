# injury-tracker-data-models

This dbt project models sports injury data for analytics using Snowflake.

## Project Overview

This project builds a data mart that includes staging, intermediate, and mart layers for sports injury data. The models transform raw CSV data from S3 into clean, query-ready Snowflake tables and views for downstream analytics.

## Running the Project

Try running the following commands:

```bash
dbt run
dbt test
