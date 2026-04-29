# Merge NHANES accelerometry with mortality data on SEQN
# R approach for efficient SAS file reading

library(haven)  # For reading SAS files
library(dplyr)  # For data manipulation
library(tidyr)  # For data cleaning
library(readr)  # For reading CSV

cat("=",.Machine$integer.max,"==\n")
cat("NHANES Data Merge: Accelerometry + Mortality\n")
cat("=",.Machine$integer.max,"==\n")

# 1. Read mortality data
cat("\n[1/5] Reading mortality data...\n")
mortality_df <- read_csv("data/mortality_cleaned.csv",
                         col_types = cols(
                           SEQN = col_double(),
                           MORTSTAT = col_double(),
                           PERMTH_EXM = col_double()
                         ))

cat("  Mortality data:", nrow(mortality_df), "rows,", ncol(mortality_df), "columns\n")
cat("  SEQN range:", min(mortality_df$SEQN), "-", max(mortality_df$SEQN), "\n")
cat("  Unique SEQN:", n_distinct(mortality_df$SEQN), "\n")

# 2. Read 2003-2004 accelerometry (just SEQN)
cat("\n[2/5] Reading 2003-2004 NHANES accelerometry data...\n")
tryCatch({
  # First, try reading with Haven which is memory-efficient
  # Create a temporary directory to extract the ZIP
  temp_dir <- tempdir()
  unzip("data/2003-2004_NHANES.zip", exdir = temp_dir, overwrite = TRUE)
  xpt_path_2003 <- file.path(temp_dir, "paxraw_c.xpt")

  # Read only necessary columns to reduce memory usage
  cat("  Extracting from ZIP and reading...\n")
  accel_2003_full <- read_xpt(xpt_path_2003)

  cat("  Data loaded:", nrow(accel_2003_full), "rows,", ncol(accel_2003_full), "columns\n")

  # Extract unique SEQN values
  accel_2003 <- accel_2003_full %>%
    select(SEQN) %>%
    distinct() %>%
    mutate(NHANES_CYCLE = "2003-2004")

  cat("  Unique participants: ", nrow(accel_2003), "\n")
  cat("  SEQN range:", min(accel_2003$SEQN), "-", max(accel_2003$SEQN), "\n")

  # Clean up
  rm(accel_2003_full)
  gc()

}, error = function(e) {
  cat("  Error reading 2003-2004 data:", as.character(e), "\n")
})

# 3. Read 2005-2006 accelerometry (just SEQN)
cat("\n[3/5] Reading 2005-2006 NHANES accelerometry data...\n")
tryCatch({
  temp_dir <- tempdir()
  unzip("data/2005-2006_NHANES.zip", exdir = temp_dir, overwrite = TRUE)
  xpt_path_2006 <- file.path(temp_dir, "paxraw_d.xpt")

  cat("  Extracting from ZIP and reading...\n")
  accel_2006_full <- read_xpt(xpt_path_2006)

  cat("  Data loaded:", nrow(accel_2006_full), "rows,", ncol(accel_2006_full), "columns\n")

  # Extract unique SEQN values
  accel_2006 <- accel_2006_full %>%
    select(SEQN) %>%
    distinct() %>%
    mutate(NHANES_CYCLE = "2005-2006")

  cat("  Unique participants: ", nrow(accel_2006), "\n")
  cat("  SEQN range:", min(accel_2006$SEQN), "-", max(accel_2006$SEQN), "\n")

  # Clean up
  rm(accel_2006_full)
  gc()

}, error = function(e) {
  cat("  Error reading 2005-2006 data:", as.character(e), "\n")
})

# 4. Combine accelerometry SEQN lists
cat("\n[4/5] Combining accelerometry datasets...\n")
accel_combined <- bind_rows(accel_2003, accel_2006)
cat("  Combined accelerometry participants:", nrow(accel_combined), "\n")
cat("  Unique SEQN:", n_distinct(accel_combined$SEQN), "\n")

# 5. Perform inner join
cat("\n[5/5] Merging datasets on SEQN (inner join)...\n")

# Create a merged dataset with mortality data for participants with accelerometry
merged <- mortality_df %>%
  inner_join(select(accel_combined, SEQN, NHANES_CYCLE), by = "SEQN")

cat("  Merged dataset:", nrow(merged), "rows,", ncol(merged), "columns\n")
cat("  Unique participants:", n_distinct(merged$SEQN), "\n")

# Print summary statistics
cat("\n", paste(rep("=", 70), collapse=""), "\n")
cat("MERGED DATASET SUMMARY\n")
cat(paste(rep("=", 70), collapse=""), "\n")

cat("\nDataset Dimensions:\n")
cat("  Total rows:", nrow(merged), "\n")
cat("  Total columns:", ncol(merged), "\n")
cat("  Unique participants (SEQN):", n_distinct(merged$SEQN), "\n")

cat("\nNHANES Cycle Distribution:\n")
cycle_dist <- merged %>%
  group_by(NHANES_CYCLE) %>%
  summarise(count = n(), .groups = 'drop') %>%
  mutate(pct = 100 * count / sum(count))

for (i in 1:nrow(cycle_dist)) {
  cat(sprintf("  %s: %,d (%.1f%%)\n",
              cycle_dist$NHANES_CYCLE[i],
              cycle_dist$count[i],
              cycle_dist$pct[i]))
}

cat("\nMortality Status (MORTSTAT) Distribution:\n")
mort_labels <- list(
  "0" = "Assumed alive",
  "1" = "Assumed deceased",
  "2" = "Under age 18 / Not released",
  "3" = "Ineligible"
)

mort_dist <- merged %>%
  group_by(MORTSTAT) %>%
  summarise(count = n(), .groups = 'drop') %>%
  arrange(MORTSTAT) %>%
  mutate(pct = 100 * count / sum(count))

for (i in 1:nrow(mort_dist)) {
  status <- as.character(as.integer(mort_dist$MORTSTAT[i]))
  label <- mort_labels[[status]]
  cat(sprintf("  %s: %,d (%.1f%%) - %s\n",
              status,
              mort_dist$count[i],
              mort_dist$pct[i],
              label))
}

cat("\nFollow-up Time (PERMTH_EXM in months):\n")
valid_count <- sum(!is.na(merged$PERMTH_EXM))
missing_count <- sum(is.na(merged$PERMTH_EXM))

cat("  Non-missing:", valid_count, "\n")
cat("  Missing:", missing_count, "\n")

if (valid_count > 0) {
  cat("  Mean:", round(mean(merged$PERMTH_EXM, na.rm = TRUE), 1), "months\n")
  cat("  Median:", round(median(merged$PERMTH_EXM, na.rm = TRUE), 1), "months\n")
  cat("  Range:", round(min(merged$PERMTH_EXM, na.rm = TRUE), 0), "-",
      round(max(merged$PERMTH_EXM, na.rm = TRUE), 0), "months\n")
}

# Save merged dataset
output_file <- "data/final_analysis_data.csv"
cat("\nSaving merged dataset to:", output_file, "\n")

write_csv(merged, output_file)

# Verify output
if (file.exists(output_file)) {
  file_size <- file.size(output_file) / (1024^2)  # Convert to MB
  cat("\n[SUCCESS] Output file created!\n")
  cat("  File:", output_file, "\n")
  cat("  Size:", round(file_size, 2), "MB\n")
  cat("  Records:", nrow(merged), "\n")
  cat("  Columns:", ncol(merged), "\n")
} else {
  cat("\n[ERROR] Output file was not created\n")
}

cat("\n", paste(rep("=", 70), collapse=""), "\n")
cat("Merge completed successfully!\n")
cat(paste(rep("=", 70), collapse=""), "\n")
