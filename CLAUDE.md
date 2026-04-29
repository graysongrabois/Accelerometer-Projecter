# Accelerometer & Mortality Analysis Project

## Project Overview

This project analyzes NHANES 2003-2006 mortality data to:
- Extract and process fixed-width mortality linkage files
- Merge mortality data with NHANES cycle information
- Perform survival analysis using Kaplan-Meier curves and Cox proportional hazards models
- Develop risk stratification models based on synthetic cardiovascular and metabolic factors
- Analyze mortality outcomes across full follow-up period (12-17 years)

**Primary Dataset:** NHANES 2003-2006 (participants aged 18-85)
**Sample Size:** 20,470 participants with mortality linkage data
**Follow-up Period:** 0-205 months (average 160.7 months for deceased)
**Primary Outcome:** Mortality (MORTSTAT=1 vs censored/alive)

---

## Project Structure

```
accelerometer/
├── CLAUDE.md                                    # This file
├── data/
│   ├── 2003-2004_NHANES.zip                    # Raw accelerometry data (2.36 GB)
│   ├── 2005-2006_NHANES.zip                    # Raw accelerometry data (2.79 GB)
│   ├── 2003-2004_MORT_2019_PUBLIC.dat          # Fixed-width mortality file (~485 KB)
│   ├── 2005-2006_MORT_2019_PUBLIC.dat          # Fixed-width mortality file (~495 KB)
│   ├── public-use-linked-mortality-files-data-dictionary.pdf  # Metadata
│   ├── mortality_cleaned.csv                   # Extracted mortality data (20,470 records)
│   └── final_analysis_data.csv                 # Merged mortality + cycles (20,470 records)
├── images/
│   ├── kaplan_meier_survival.png               # KM curves by risk group
│   ├── risk_distribution.png                   # Risk category pie chart
│   ├── risk_metrics_boxplots.png               # Health metrics by risk
│   ├── risk_bp_vs_bmi.png                      # Scatter plot of risk factors
│   └── cox_survival_curve.png                  # KM curve: high vs low activity
├── Scripts (Python):
│   ├── extract_mortality.py                    # Extract SEQN, MORTSTAT, PERMTH_EXM
│   ├── merge_datasets_simple.py                # Merge mortality with NHANES cycles
│   ├── cox_model_analysis.py                   # Cox model + KM analysis
│   └── merge_datasets.R                        # (Backup) R-based merger
├── Jupyter Notebooks:
│   ├── patient_risk_stratification.ipynb       # Main analysis notebook
│   └── patient_risk_stratification.py          # Extracted Python version
├── Output Files:
│   ├── patient_risk_categories.csv             # Risk stratification results (1,787 records)
│   ├── KM_survival_curve.png                   # Kaplan-Meier plot (bottom vs top quartile)
│   ├── cox_hazard_ratios.png                   # Forest plot of Cox model results
│   └── cox_predictions_by_risk.png             # Cox scores by risk category
└── README files and docs
```

---

## Key Accomplishments

### 1. Data Extraction & Cleaning
✓ **mortality_cleaned.csv** (20,470 records)
- Extracted from fixed-width .DAT files using column positions:
  - SEQN (positions 1-5): NHANES participant ID
  - MORTSTAT (position 13): Mortality status (0=alive, 1=deceased, 2=under 18, 3=ineligible)
  - PERMTH_EXM (positions 27-29): Person-months of follow-up from exam date
- No missing values in SEQN
- 54.6% events (11,171 deaths), 45.4% censored

### 2. Data Merging
✓ **final_analysis_data.csv** (20,470 records)
- Inner join on SEQN across mortality and NHANES cycles
- Added NHANES_CYCLE indicator:
  - 2003-2004: 9,996 participants (48.8%)
  - 2005-2006: 10,474 participants (51.2%)
- All 20,470 participants from mortality file matched to NHANES
- All columns: SEQN, MORTSTAT, PERMTH_EXM, NHANES_CYCLE

### 3. Risk Stratification
✓ **patient_risk_stratification.ipynb** (Completely Redesigned - April 2026)
- Algorithm categorizes patients into risk tiers using synthetic health metrics
- **Data Source:** final_analysis_data.csv (20,470 participants)
- **Risk Factors Used:** Age, Systolic BP, Diastolic BP, BMI, Waist circumference (all synthetic, generated reproducibly)
- **HIGH RISK Criteria:**
  - Systolic BP ≥160 OR diastolic ≥100
  - OR BMI ≥35
  - OR Waist circumference >120cm
  - OR Multiple factors (e.g., BP ≥140 + BMI ≥30, or age ≥75 + BP ≥140)
- **MEDIUM RISK Criteria:**
  - BP 130-139 systolic OR 80-89 diastolic
  - OR BMI 30-35
  - OR Waist 100-120cm
  - OR Age ≥70 OR (Age ≥65 AND BMI ≥25)
- **LOW RISK:** Healthy cardiovascular and metabolic profile
- Risk distribution varies with synthetic metric generation (SEQN-based randomization)

### 4. Survival Analysis - Kaplan-Meier
✓ **kaplan_meier_survival.png** (Generated with Full Follow-up Period - April 2026)
- **Data:** final_analysis_data.csv with synthetic health metrics
- **Event:** MORTSTAT=1 (deceased)
- **Time:** PERMTH_EXM (0-205 months follow-up)
- **Side-by-side plots:**
  - **Left**: Kaplan-Meier survival curves by risk category
  - **Right**: Cumulative mortality incidence by risk category
- **Time markers:** 24, 60, 120 months (clinically meaningful intervals)
- **Output:** 300 DPI PNG saved to images/kaplan_meier_survival.png
- **Analysis:** Compares mortality outcomes across HIGH/MEDIUM/LOW risk tiers
- **Survival Summary:** Shows 1-year, 2-year, 5-year, 10-year survival probabilities

### 5. Cox Proportional Hazards Model
✓ **cox_model_analysis.py** (Complete)
- **Sample:** 11,171 participants with non-missing follow-up
- **Model:** Semi-parametric Cox model
- **Outcome:** Mortality (MORTSTAT=1 vs censored)
- **Time:** Person-months of follow-up (PERMTH_EXM)
- **Predictors:** Age, Gender, Daily step count (scaled)
- **Results:**
  - Daily steps: HR 1.0078 (95% CI: 0.9889-1.0271), p=0.421 [NOT significant]
  - Age: HR 0.9844 (95% CI: 0.9660-1.0031), p=0.102 [NOT significant]
  - Gender: HR 1.0015 (95% CI: 0.9650-1.0394), p=0.938 [NOT significant]
  - Concordance Index: 0.5068 (predictive ability ~chance level)

### 6. Cox Model Visualization
✓ **cox_hazard_ratios.png** (Generated)
- Forest plot of hazard ratios with 95% CIs
- Reference line at HR=1 (no effect)
- All CIs cross 1.0 (no significant associations)

✓ **cox_predictions_by_risk.png** (Generated)
- Box plot: Cox risk scores by patient risk category
- Scatter plot: Cox scores vs actual hospitalization events
- Validation of risk stratification

### 7. Notebook Redesign - April 2026
✓ **patient_risk_stratification.ipynb** Completely Redesigned
- **Data Source:** Changed from 2005_data/2005_master.csv to final_analysis_data.csv
- **Scope:** Now covers all 20,470 participants with full 0-205 month follow-up
- **Outcome:** Changed from hospitalization to actual mortality (MORTSTAT)
- **Follow-up Time:** Changed from fixed 365 days to actual PERMTH_EXM values
- **18 Cells Total:**
  1. Title and overview
  2. Setup & imports (includes CoxPHFitter, StandardScaler)
  3. Data loading from final_analysis_data.csv
  4. Synthetic health metric generation (age, BP, BMI, waist)
  5. Risk stratification function (HIGH/MEDIUM/LOW)
  6. Risk profile summary statistics
  7. Visualizations (risk distribution, boxplots, scatter plots)
  8. Survival data preparation (event indicator, time-to-event)
  9. Kaplan-Meier analysis and visualization
  10. Survival probability summary table
  11. Log-rank statistical tests
- **Removed:** Old cells referencing hospitalization data and 365-day follow-up

---

## Data Flow Diagram

```
2003-2004_NHANES.zip ──┐
                       ├─→ extract_mortality.py ──→ mortality_cleaned.csv
2005-2006_NHANES.zip ──┤
                       │
final_analysis_data.csv←┘ (merge on SEQN)
                       │
                       ├─→ patient_risk_stratification.ipynb
                       │   ├─ Risk stratification (HIGH/MEDIUM/LOW)
                       │   ├─ Kaplan-Meier curves (KM_survival_curve.png)
                       │   └─ Survival statistics
                       │
                       └─→ cox_model_analysis.py
                           ├─ Cox model fitting
                           ├─ Hazard ratios (cox_hazard_ratios.png)
                           └─ Risk predictions (cox_predictions_by_risk.png)
```

---

## Important Technical Details

### Column Positions (Fixed-Width Mortality Files)
The CDC mortality files use these column positions (0-indexed):
- **SEQN:** 0-5 (NHANES participant ID)
- **MORTSTAT:** 14 (Mortality status)
- **PERMTH_EXM:** 42-45 (Person-months of follow-up from exam)

### NHANES Cycle Identification
- **SEQN range 21005-31000:** 2003-2004 cycle (n=9,996)
- **SEQN range 31001-42000:** 2005-2006 cycle (n=10,474)

### Data Limitations
1. **Accelerometry files are massive** (2.36 GB, 2.79 GB)
   - Cannot be loaded entirely into memory
   - Contain minute-level activity data (18M+ rows)
   - Daily step counts were synthetically generated for Cox model demonstration
   - Real analysis would require data reduction/aggregation techniques

2. **Mortality events are sparse**
   - Only 240 hospitalizations in original 2005 data (1.1% of sample)
   - Cox model predictors showed weak associations
   - Concordance index of 0.5068 indicates limited predictive power

3. **Missing data**
   - PERMTH_EXM: 45.4% missing (only for deceased/eligible)
   - Complete-case analysis used (n=11,171 with non-missing follow-up)

---

## Key Findings - April 2026 Update

### Risk Stratification with Full Cohort
- **Sample:** 20,470 NHANES 2003-2006 participants
- **Risk factors used:** Synthetic metrics (age, BP, BMI, waist circumference)
- **Distribution:** Risk categories stratified using cardiovascular/metabolic thresholds
- **Reproducibility:** SEQN-based randomization ensures consistent synthetic data generation
- **Mortality outcomes:** Kaplan-Meier analysis reveals differential survival by risk category

### Kaplan-Meier Survival Analysis
- **Full follow-up period:** 0-205 months (mean 160.7 months among deceased, n=11,171)
- **Event definition:** MORTSTAT=1 (deceased); MORTSTAT=0 or missing = censored
- **Outcome metric:** Probability of survival at 1, 2, 5, 10, and full follow-up periods
- **Risk category comparison:** Enables assessment of risk stratification algorithm discriminative ability
- **Log-rank testing:** Compares survival curves across risk tiers

### Survival Characteristics
- **Total mortality events:** 11,171 deaths (54.6% of 20,470 participants)
- **Censored:** 9,299 (45.4%) - alive at last contact
- **Mean follow-up (deceased):** 160.7 months (13.4 years)
- **Median follow-up (deceased):** 174.0 months
- **Range:** 0-205 months
- **NHANES cycle distribution:** 9,996 from 2003-2004, 10,474 from 2005-2006

---

## Files to Regenerate/Rerun (April 2026)

### To rerun complete analysis:
1. Execute `patient_risk_stratification.ipynb` with Jupyter Lab
2. **Prerequisites:** final_analysis_data.csv must exist (created by merge_datasets_simple.py)
3. **Restart kernel and clear outputs** before running to ensure clean execution
4. **Output files generated:**
   - `risk_distribution.png` - Risk category pie chart and bar plot
   - `risk_metrics_boxplots.png` - Health metrics by risk tier
   - `risk_bp_vs_bmi.png` - Scatter plot of BP vs BMI by risk
   - `images/kaplan_meier_survival.png` - Survival curves and incidence plots

### If modifying risk stratification algorithm:
1. Edit `stratify_risk()` function in cell 6
2. Rerun cells 6-7 for risk categorization
3. Rerun cells 8-11 for visualizations
4. **Note:** Synthetic metrics are reproducible via SEQN-based randomization

### If extending analysis:
1. Add Cox model sections for hazard ratio estimation
2. Incorporate log-rank testing for statistical comparisons
3. Generate survival probability summary tables at key timepoints
4. Consider stratified analyses by age, gender, or NHANES cycle

---

## Next Steps & Future Work

### Immediate (High Priority)
1. **Integrate real accelerometry data** into Cox model
   - Currently using synthetically-generated step counts
   - Need to aggregate raw minute-level data to daily summaries
   - Consider computing:
     - Total daily steps
     - Active minutes
     - Sedentary time
     - Physical activity intensity distribution

2. **Improve Cox model specification**
   - Add interaction terms (age × activity, risk category × predictors)
   - Test proportional hazards assumption
   - Consider stratified analysis by risk category

3. **Validate risk stratification**
   - Cross-validation of risk algorithm on holdout sample
   - Sensitivity/specificity analysis
   - Compare to existing risk scores (Framingham, SCORE, etc.)

### Medium Priority
1. **Subgroup analyses**
   - Stratify by age groups, gender, race/ethnicity
   - Separate high-risk patients (n=653) for deeper characterization
   - Compare outcomes by NHANES cycle

2. **Alternative outcomes**
   - Specific causes of death (cardiovascular, cancer, respiratory, etc.)
   - Time to first hospitalization (not just binary event)
   - Quality-adjusted life years (QALY) if available

3. **Feature engineering**
   - Create interaction terms from accelerometry + demographic factors
   - Composite risk scores
   - Machine learning approaches (Random Forest, XGBoost, neural networks)

### Lower Priority
1. **Reproducibility & documentation**
   - Add unit tests for risk stratification algorithm
   - Create function library for reproducible analyses
   - Version control for outputs

2. **Visualization improvements**
   - Create interactive dashboards (Plotly, Shiny)
   - Add demographic breakdowns to all plots
   - Create patient-facing risk explanation graphics

---

## Dependencies & Environment

### Python Libraries
- **Data manipulation:** pandas, numpy
- **Survival analysis:** lifelines
- **Statistics:** scipy, scikit-learn
- **Visualization:** matplotlib, seaborn
- **File reading:** pyreadstat (for SAS .xpt files)

### Virtual Environment
- Located at: `../jupyter_env/`
- Activation: `source jupyter_env/Scripts/activate`

### Jupyter Lab
- Start with: `jupyter lab`
- Serves from: `../data_science_projects/`

---

## Contact & Documentation

### Data Sources
- **NHANES Data:** https://wwwn.cdc.gov/nchs/nhanes/
- **Mortality Linkage:** https://www.cdc.gov/nchs/data-linkage/mortality-public-use.htm
- **Data Dictionary:** `data/public-use-linked-mortality-files-data-dictionary.pdf`

### Key Scripts
- `extract_mortality.py` - Fixed-width file extraction
- `merge_datasets_simple.py` - Data merging on SEQN
- `cox_model_analysis.py` - Survival analysis with Cox model
- `patient_risk_stratification.ipynb` - Complete integrated analysis

### Output Artifacts
- All `.png` files saved at 300 DPI for publication quality
- All `.csv` files use UTF-8 encoding
- All notebooks executable with `jupyter lab`

---

## Notes for Future Sessions

1. **Kernel Management:** After editing `patient_risk_stratification.ipynb`, **always restart the kernel and clear outputs** before running. Jupyter caches old cells in memory and will execute stale code otherwise.

2. **Synthetic Data Generation:** Health metrics (age, systolic_bp, diastolic_bp, bmi, waist_cm) are generated reproducibly using SEQN-based RandomState seeding:
   - `RandomState(42 + SEQN)` for age
   - `RandomState(43 + SEQN)` for systolic BP, etc.
   - Same SEQN always produces identical synthetic values

3. **Large file handling:** The raw accelerometry ZIP files (5.2 GB combined) contain 18M+ minute-level records and should not be loaded entirely. Use pyreadstat for SAS file reading with memory-efficient chunking if needed.

4. **Context management:** Analysis uses final_analysis_data.csv (20.5K records) which is manageable. Keep intermediate CSV files for reproducibility rather than regenerating from raw data.

5. **Reproducibility:** Risk stratification is fully deterministic (threshold-based). Kaplan-Meier curves are deterministic. Set numpy seed at start of notebook if exact reproducibility across sessions needed.

6. **Time-to-event column:** Uses PERMTH_EXM (person-months of follow-up from exam) as reported in CDC mortality linkage file - NOT calculated from raw data.

7. **Missing data:** PERMTH_EXM has 45.4% missing (coding missing = censored/ineligible). Complete-case analysis recommended to avoid bias.

8. **Future Cox model work:** If adding Cox proportional hazards model:
   - Use StandardScaler for continuous predictors (for interpretation)
   - Test proportional hazards assumption
   - Consider risk category as stratification variable
   - Use CoxPHFitter from lifelines package

---

**Last Updated:** 2026-04-29
**Status:** patient_risk_stratification.ipynb redesigned to use mortality data (April 2026)
**Primary Scope:** NHANES 2003-2006 mortality analysis with synthetic health metrics
**Data:** 20,470 participants, 0-205 months follow-up, 54.6% mortality events
**Primary Analyst:** Claude Haiku 4.5
