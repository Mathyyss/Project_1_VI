=================================================
NSF GRANT CANCELLATIONS ANALYSIS
=================================================

AUTHORS: [VotreNom1], [VotreNom2]
COURSE: Data Visualization
DATE: November 2025

=================================================
INSTALLATION & EXECUTION
=================================================

1. Install required packages:
   
   pip install streamlit pandas altair vega-datasets scipy statsmodels

2. Place both files in the same directory:
   - app.py
   - merged_clean_ready.csv

3. Run the application:
   
   streamlit run app.py

4. Open your browser at:
   http://localhost:8501

=================================================
FILES DESCRIPTION
=================================================

- app.py: Main Streamlit application
- merged_clean_ready.csv: Cleaned dataset (1,970 grants)

=================================================
FEATURES
=================================================

The application answers 5 research questions:

Q1: How are cancellations distributed by states?
    → Interactive US map + Top 10 bar chart

Q2: Which institutions were most affected by number?
    → Lollipop chart (top 15)

Q3: Which institutions were most affected by budget?
    → Lollipop chart (top 15)

Q4: Correlation with flagged words?
    → 84.6% contain diversity/equity/climate keywords

Q5: Correlation with Cruz list and reinstatements?
    → Cruz grants 4× less likely to be reinstated

=================================================
DATA CLEANING PROCESS
=================================================

1. Merged nsf_terminations_airtable.csv with cruz_list.csv
2. Fixed in_cruz_list column (word boundary matching)
3. Created has_flagged_words column (54 keywords)
4. Removed false positives (e.g., "trans" in "transportation")
5. Final dataset: 1,970 grants, 20 columns

=================================================
TECHNICAL NOTES
=================================================

- All visualizations use Altair (declarative grammar)
- Colorblind-safe palettes (orangered, tableau10)
- Statistical tests: Chi-square, Fisher's exact
- Confidence intervals: Wilson method

=================================================
SUPPORT
=================================================

For questions or issues, contact:
[Your Email]

=================================================# Project_1_VI
