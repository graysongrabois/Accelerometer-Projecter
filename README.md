# Accelerometer-Projecter

Project 11: Activity-based readmission risk from accelerometry
#BACKGROUND
Accelerometers in wrist-worn devices measure movement in 3 axes at high frequency, from which
activity intensity, sedentary time, step counts, and sleep duration can be derived. Physical activity
trajectories are strong predictors of chronic disease outcomes.

#WHY IT MATTERS
Functional decline — reduction in physical activity over time — often precedes hospitalization in older
adults and patients with chronic disease. Accelerometry provides an objective, continuous measure of
decline that self-reported activity data cannot capture.
#PROJECT GOAL
Using NHANES accelerometry linked to hospitalization records, build activity-decline trajectories for
adults 50+ and predict hospitalization risk within 12 months. Compare trajectory-feature approaches
against a Cox proportional hazards survival model.
DATA SOURCE
#NHANES 2003-2006 accelerometry waves (hip-worn ActiGraph, 7-day wear). Linked to NHANES
public-use mortality and hospitalization files via NCHS linked data files. Freely available from the CDC
NHANES website.
#FINAL OUTCOMES

• Activity trajectory features: Weekly step count, percent sedentary time, and sleep efficiency
derived from raw accelerometry.
• Cox proportional hazards model: Time-to-hospitalization model with activity features as time-
varying covariates.

• Risk stratification: High, medium, and low risk groups with Kaplan-Meier survival curves by
group.

• Clinical translation: What step count threshold or trajectory change best separates high-risk
from low-risk patients?

#QUESTIONS TO THINK ABOUT AS THE PROJECT EVOLVES
---------------------------------------------------------------------
52. NHANES accelerometry is a 7-day snapshot, not a continuous longitudinal record. What
assumptions must you make to treat this as a 'trajectory' rather than a cross-sectional measure?
---------------------------------------------------------------------
53. How do you distinguish non-wear periods from true sedentary behavior in accelerometry data?
54. Cox regression assumes proportional hazards — the risk ratio between groups is constant over
time. How do you test this assumption, and what happens if it is violated?
---------------------------------------------------------------------
56. Patients who are frequently hospitalized may show lower activity simply because they are often
in the hospital. How does this reverse causality affect your model?
---------------------------------------------------------------------
58. What data pipeline would be required to deploy a wearable-derived readmission risk score
operationally in a home monitoring setting?
