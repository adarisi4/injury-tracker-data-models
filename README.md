# 🏥 injury-tracker-data-models

This **dbt project models sports injury data** for advanced analytics, powering dashboards that help stakeholders understand injury trends across major professional leagues (NBA, NFL, MLB, NHL).

---

## 📈 Business Goal

**How can we identify which player positions, teams, or body parts are most frequently affected by injuries over time — and surface trends to inform training load, roster management, or fan engagement?**

To answer this, I designed a robust data mart using dbt on Snowflake that cleans, structures, and models injury data from multiple sources into analytics-ready tables for daily use.

---

## 🛠 Project Overview

This project builds a modular data pipeline with:

- ✅ **Staging layer**: Cleans raw injury CSVs from S3, standardizes column names and types, and handles NULLs or invalid entries.
- ✅ **Intermediate layer**: Joins injury records with player and sport metadata, deduplicates rows, and creates time-based metrics.
- ✅ **Mart layer**: Creates fact and dimension tables (e.g. `fact_injuries`, `dim_players`, `dim_sports`) optimized for analytics and dashboarding.

---

## 🔍 Example Insights Enabled

- Injury trends by body part (e.g. hamstring, shoulder)
- Injury by position or team
- Severity of injuries

---

## 👨‍💻 What I Did

- Built a full dbt project with **staging → intermediate → mart** layers using modular, testable models in Snowflake
- Created **custom schema tests and `dbt test` assertions** to enforce data quality (nulls, uniqueness, accepted values)
- Developed **Python ETL scripts** to scrape and preprocess sports injury data from ESPN, storing cleaned datasets in S3
- Automated daily ingestion using **AWS EventBridge to trigger Lambda**, loading raw injury CSVs into S3 for processing
- Integrated dbt with **Snowflake external stages** to transform raw S3 data into clean, analytics-ready models
- Implemented **CI/CD with GitHub Actions** to auto-run `dbt build` on push, ensuring models pass tests before deployment
- Wrote complex **SQL using window functions, CTEs, and macros** to streamline joins, deduplication, and historical logic
- Added **data documentation and dbt exposures** for transparency across downstream dashboards and metrics
- Final models support **Matplotlib dashboards** surfacing weekly trends, player injury breakdowns, and body part frequency


---

## 🧪 How to Run

To execute the project:

```bash
dbt build         # Runs models + tests
dbt run           # Only runs models
dbt test          # Runs tests only
