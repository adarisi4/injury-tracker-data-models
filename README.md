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

## 📊 Injury Data Visualizations (April–July)

This section highlights key trends in sports injuries across multiple dimensions—body part, sport, player, and injury status—using data from April 18–19, June 13–15, and July 9–11. Visualizations were built using pandas and matplotlib.

🦴 Most Injured Body Parts

Across all three timeframes, the knee was by far the most frequently injured body part, peaking at 5,800+ injuries in July. The shoulder, elbow, ankle, and back followed behind in every cycle, typically ranging from 900 to 1,300 injuries. This reflects high lower-body strain in most sports, especially football and basketball.

🏟️ Injuries by Sport

April: Baseball narrowly edged out football in injury count (~300 each).

June: Baseball and football both surpassed 4,000 injuries, with baseball still leading.

July: Baseball remained highest at 5,600+, but football showed a sharp increase to 4,700+.

📌 Explanation: The jump in football injuries during July is linked to the start of NFL training camps, where players return to high-contact practice after the offseason, increasing soft tissue and joint injuries.

👤 Most Injured Players

Top injured players across all datasets include:

Landon Dickerson, Foster Moreau, L’Jarius Sneed, Chris Godwin, Nacho Alvarez Jr., and others.

By July, many had 30+ injuries, which may reflect chronic issues or detailed tracking of ongoing recovery.

🩺 Injury Status by Sport

The most frequent status across all periods was Football – Questionable, reaching 4,200+ in July.

Baseball contributed several status types: 60-Day IL, 15-Day IL, Day-to-Day, and Out, each consistently appearing in the top 10.

Basketball and Hockey had notable entries like Injured Reserve and Day-to-Day.

Statuses like “Questionable” and “Day-to-Day” are often used for precautionary or recovery-phase listings, not always indicating severe injuries.

## ✅ Summary

Knee injuries remain the most prevalent across all sports.

Baseball consistently reports the most injuries, likely due to longer seasons and more granular tracking.

Football injury counts surged in July as training camp began.

A small group of players repeatedly show up in the top injury list and may be worth analyzing for long-term trends.
- Implemented **CI/CD with GitHub Actions** to auto-run `dbt build` on push, ensuring models pass tests before deployment
- Wrote complex **SQL using window functions, CTEs, and macros** to streamline joins, deduplication, and historical logic
- Added **data documentation and dbt exposures** for transparency across downstream dashboards and metrics
- Final models support **Matplotlib dashboards** surfacing weekly trends, player injury breakdowns, and body part frequency


---
