# Draw Steel Ability Data Visualizer
Live app: (https://app-ap-gmzobyyngzknbbhhquzczm.streamlit.app/)

## Purpose
An interactive Streamlit app for exploring abilities from the tabletop RPG Draw Steel.

## Dataset
`draw_steel_ability_data.csv` contains 497 abilities from classes and kits in
*Draw Steel* by MCDM Productions. I compiled it manually from the game's
rulebook (<exact title, edition/version, year>) into a spreadsheet, one row per
ability. It does not include classes or content released after that version.
Data cleaning in the app handles blank subclasses, a few typos, and numeric
conversion of costs.

## How to use
1. Use the sidebar to pick classes and subclasses.
2. Data tab: browse class and kit tables, choose columns.
3. Charts tab: pick an attribute for the bar chart; pick a class for the pie chart.
4. Insights tab: summary observations.

## Run locally
pip install -r requirements.txt
streamlit run draw_steel_data.py
