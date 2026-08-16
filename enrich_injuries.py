import os
import json
import pandas as pd

from anthropic import Anthropic
from dotenv import load_dotenv


# -------------------------
# LOAD API KEY
# -------------------------

load_dotenv()

client = Anthropic(
    api_key=os.environ["ANTHROPIC_API_KEY"]
)


# -------------------------
# CLAUDE ENRICHMENT FUNCTION
# -------------------------

def enrich_injury(description):

    prompt = f"""
Extract structured information from the sports injury report below.

STRICT RULES:

1. Only use information explicitly supported by the report.

2. Do not infer a diagnosis from a body part.
   Example:
   "(knee)" means body_part = "knee",
   but injury_type = "unknown" unless an actual diagnosis is stated.

3. injury_type must describe an actual injury or diagnosis, such as:
   - torn ACL
   - fracture
   - sprain
   - torn labrum
   - hamstring strain

   Values such as "knee", "shoulder", "ankle", "Achilles",
   and "leg" are body parts and must NOT be used as injury_type.

4. surgery_status rules:
   - Use "yes" only when surgery is explicitly mentioned.
   - Use "no" only when the report explicitly states surgery
     is not required or will not occur.
   - Otherwise use "unknown".

5. season_ending rules:
   - Use "yes" only when the report explicitly states the player
     will miss the remainder of the season, is out for the season,
     or equivalent language.

   - Use "no" only when the report explicitly states the player
     is expected to return during the current season.

   - Otherwise use "unknown".

   Do NOT interpret phrases such as:
   - "miss the start of the season"
   - "limited participant"
   - "not yet cleared"
   - "unlikely to be ready"
   - absence of season-ending language

   as evidence for "no".

6. availability_status should summarize only the availability
   explicitly stated in the report.

7. mentioned_player should contain the player last name or player
   identifier explicitly mentioned in the injury description.
   If no player can be identified, use "unknown".

8. When information is unavailable, use "unknown".

Return ONLY valid JSON in exactly this format:

{{
    "injury_type": "",
    "body_part": "",
    "body_side": "",
    "surgery_status": "",
    "season_ending": "",
    "availability_status": "",
    "mentioned_player": ""
}}

Allowed body_side values:
left, right, bilateral, unknown

Allowed surgery_status values:
yes, no, unknown

Allowed season_ending values:
yes, no, unknown

Injury report:
{description}
"""

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=350,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response_text = message.content[0].text

    # Remove Markdown code fences if Claude adds them
    response_text = (
        response_text
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    injury_data = json.loads(response_text)

    return {
        "injury_type": injury_data["injury_type"],
        "body_part": injury_data["body_part"],
        "body_side": injury_data["body_side"],
        "surgery_status": injury_data["surgery_status"],
        "season_ending": injury_data["season_ending"],
        "availability_status": injury_data["availability_status"],
        "mentioned_player": injury_data["mentioned_player"],
        "input_tokens": message.usage.input_tokens,
        "output_tokens": message.usage.output_tokens
    }


# -------------------------
# READ ALL 50 ROWS
# -------------------------

df = pd.read_csv("severe_injuries_50.csv")

print("Rows to process:", len(df))


# -------------------------
# PROCESS ALL ROWS
# -------------------------

results = []

for index, row in df.iterrows():

    print(
        f"\nProcessing {index + 1}/{len(df)} "
        f"- Injury ID: {row['INJURY_ID']}"
    )

    print("Player:", row["PLAYER_NAME"])

    try:

        ai_result = enrich_injury(
            row["INJURY_DESCRIPTION"]
        )

        # -------------------------
        # PLAYER MATCH CHECK
        # -------------------------

        player_last_name = str(
            row["PLAYER_NAME"]
        ).split()[-1].lower()

        mentioned_player = str(
            ai_result["mentioned_player"]
        ).lower()

        if (
            mentioned_player != "unknown"
            and player_last_name in mentioned_player
        ):
            player_match_flag = "match"
        else:
            player_match_flag = "review"

        # -------------------------
        # SUCCESSFUL RESULT
        # -------------------------

        results.append({

            "injury_id": row["INJURY_ID"],
            "player_name": row["PLAYER_NAME"],
            "sport": row["SPORT"],
            "injury_description": row["INJURY_DESCRIPTION"],

            "injury_type": ai_result["injury_type"],
            "body_part": ai_result["body_part"],
            "body_side": ai_result["body_side"],

            "surgery_status":
                ai_result["surgery_status"],

            "season_ending":
                ai_result["season_ending"],

            "availability_status":
                ai_result["availability_status"],

            "mentioned_player":
                ai_result["mentioned_player"],

            "player_match_flag":
                player_match_flag,

            "input_tokens":
                ai_result["input_tokens"],

            "output_tokens":
                ai_result["output_tokens"],

            "processing_status": "success",
            "error_message": ""
        })

        print("Claude result:", ai_result)
        print("Player match:", player_match_flag)

    except Exception as e:

        # -------------------------
        # FAILED RESULT
        # -------------------------

        print("ERROR:", str(e))

        results.append({

            "injury_id": row["INJURY_ID"],
            "player_name": row["PLAYER_NAME"],
            "sport": row["SPORT"],
            "injury_description": row["INJURY_DESCRIPTION"],

            "injury_type": "unknown",
            "body_part": "unknown",
            "body_side": "unknown",
            "surgery_status": "unknown",
            "season_ending": "unknown",
            "availability_status": "unknown",

            "mentioned_player": "unknown",
            "player_match_flag": "review",

            "input_tokens": 0,
            "output_tokens": 0,

            "processing_status": "failed",
            "error_message": str(e)
        })


# -------------------------
# CREATE FINAL DATAFRAME
# -------------------------

result_df = pd.DataFrame(results)


# -------------------------
# SAVE FINAL CSV
# -------------------------

result_df.to_csv(
    "ai_injury_enrichment.csv",
    index=False
)


# -------------------------
# RUN SUMMARY
# -------------------------

print("\n------------------------------")
print("PROCESSING COMPLETE")
print("------------------------------")

print("Rows processed:", len(result_df))

print(
    "Successful:",
    (result_df["processing_status"] == "success").sum()
)

print(
    "Failed:",
    (result_df["processing_status"] == "failed").sum()
)

print(
    "Player reviews:",
    (result_df["player_match_flag"] == "review").sum()
)

print("\nTOKEN USAGE")

print(
    "Total input tokens:",
    result_df["input_tokens"].sum()
)

print(
    "Total output tokens:",
    result_df["output_tokens"].sum()
)

print("\nSaved to:")
print("ai_injury_enrichment.csv")