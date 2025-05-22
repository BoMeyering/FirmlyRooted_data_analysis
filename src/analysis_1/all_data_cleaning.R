#############################################
# Prop Excavation Data Cleaning and Export #
#############################################

# Library Imports ---------------------------------------------------------

library(tidyverse)
library(factoextra)
library(emmeans)
library(lme4)
library(lmerTest)
library(factoextra)
library(GGally)
library(plotly)
library(multcomp)
library(multcompView)
library(data.table)
library(readxl)


# Raw Data Imports --------------------------------------------------------

# Tree growth data
pa_growth_raw <- fread("../../data/raw/tree_growth/prop_adair_tree_growth_data.csv")
pp_growth_raw <- fread("../../data/raw/tree_growth/prop_picos_tree_growth_data.csv")

# Root measurement data
pa_roots_raw <- fread("../../data/raw/root_measurements/prop_adair_root_measurement.csv")
pp_roots_raw <- fread("../../data/raw/root_measurements/prop_picos_root_measurement.csv")

# Root system measurement data
pa_systems_raw <- fread("../../data/raw/whole_root_system_measurements/prop_adair_root_system_measurement.csv")
pp_systems_raw <- fread("../../data/raw/whole_root_system_measurements/prop_picos_root_system_measurement.csv")

# LAI data
pa_lai_raw <- fread("../../data/processed/lai/prop_adair_processed_lai")
pp_lai_raw <- fread("../../data/processed/lai/prop_picos_processed_lai")

# Phytophthora data only for Prop-ADAIR
pa_phyt_raw <- fread("../../data/raw/phytophthora_analysis/prop_adair_phytophthora_elisa.csv")

# PCR data
pa_qpcr_raw <- fread("../../data/raw/pcr/prop_adair_pcr_202111.csv")
pp_qpcr_raw <- fread("../../data/raw/pcr/prop_picos_pcr_202110.csv")

# Nutrient data
pa_leaf_raw <- fread("../../data/raw/nutrient_analysis/prop_adair_20211102_leaf_nutrient_analysis.csv")
pa_soil_raw <- fread("../../data/raw/nutrient_analysis/prop_adair_20211102_soil_nutrient_analysis.csv")
pp_leaf_raw <- fread("../../data/raw/nutrient_analysis/prop_picos_20211019_leaf_nutrient_analysis.csv")
pp_soil_raw <- fread("../../data/raw/nutrient_analysis/prop_picos_20211019_soil_nutrient_analysis.csv")

# Read in join tables
# PROP-ADAIR join table
# May need to remove 17W_28 - US1516 ct died in year 1, replaced with US1516 mpg in year 2
pa_join <- fread("../../metadata/join_tables/prop_adair_join_table.csv") %>% 
        dplyr::select(sys_id:plant_date) %>% 
        filter(!is.na(block)) # Get rid of border trees

pp_join <- fread("../../metadata/join_tables/prop_picos_join_table.csv") %>% 
        dplyr::select(sys_id:plant_date) %>%
        filter(!is.na(block)) # Get rid of border trees


# Prop Adair Data Cleaning-------------------------------------------------

# Create a pa plot table with tree counts
pa_plots <- pa_join %>% 
        group_by(plot_id, row, plot, block, rs, prop_type) %>% 
        count() %>% 
        arrange(row, plot, block)

# Aggregate the qPCR data for Prop-Adair
pa_qpcr <- pa_qpcr_raw %>% 
        left_join(pa_plots, 'plot_id' ) %>% 
        dplyr::select(plot_id, block, row.x, plot.x, rs, prop_type, hlb_ct, cox_ct) %>% 
        mutate(mean_cox = mean(cox_ct),
               hlb_ct_adj = hlb_ct/(cox_ct/mean(cox_ct)))

# Cleaning and joining all tree level data with single obs per tree
pa_tree_data <- pa_join %>% 
        left_join(
                pa_growth_raw %>% 
                        filter(
                                measurement_date=="2021-11-02", 
                                plot_id!="pa_00") %>% # get rid of null plots
                        dplyr::select(-c(plot_id:plant_date, comment)),
                by='sys_id'
        ) %>% 
        left_join(
                pa_systems_raw %>% 
                        dplyr::select(-c(plot_id:block)),
                by='sys_id'
        ) %>% 
        left_join(
                pa_lai_raw %>% 
                        separate(LAI_File, into = c("row", "tree")) %>% 
                        mutate(tree = str_pad(string=tree, width=2, side="left", pad="0"),
                               sys_id = paste(row, tree, sep="_")) %>% 
                        dplyr::select(sys_id, LAI),
                by='sys_id'
        ) %>%
        left_join(
                pa_phyt_raw %>%
                        rename("phyt_pos" = "result") %>%
                        dplyr::select(sys_id, phyt_pos),
                by='sys_id'
        ) %>% 
        dplyr::filter(sys_id != "17W_28")


# Cleaning and joining all plot level data with single obs per plot
pa_plot_data <- pa_plots %>% 
        left_join(
                pa_leaf_raw %>% 
                        dplyr::select(plot_id, n_per:cu_ppm),
                by='plot_id'
        ) %>% 
        left_join(
                pa_qpcr %>% 
                        dplyr::select(plot_id, hlb_ct_adj),
                by='plot_id'
        )

# Aggregate and clean all of the raw root data and clean up some of the inconsistencies in the data
pa_root_data <- pa_roots_raw %>% 
        mutate(n_branch_seg = str_remove_all(n_branch_seg, ' '),
               n_branch_seg = str_replace(n_branch_seg, '\\(<', '\\(all<'),
               n_branch = as.numeric(as.vector(str_match(n_branch_seg, pattern = '^(\\d+)\\(*')[,2])),
               branch_sub5mm = as.vector(str_match(n_branch_seg, "(\\d+)<")[,2]),
               all_branch_sub5mm = as.vector(str_match(n_branch_seg, 'all')),
               branch_sub5mm = ifelse(is.na(branch_sub5mm), 0, branch_sub5mm),
               n_branch_lt5mm = as.numeric(ifelse(is.na(all_branch_sub5mm), branch_sub5mm, n_branch))) %>% 
        dplyr::select(-c(branch_sub5mm, all_branch_sub5mm, n_branch_seg))


# Prop Picos Data Cleaning ------------------------------------------------

# Create a pp plot table with tree counts
pp_plots <- pp_join %>% 
        group_by(plot_id, row, plot, block, rs, prop_type) %>% 
        count() %>% 
        arrange(row, plot, block)

# Aggregate the qPCR data for Prop-Picos
pp_qpcr <- pp_qpcr_raw %>% 
        left_join(pp_plots, 'plot_id' ) %>% 
        dplyr::select(plot_id, block, row.x, plot.x, rs, prop_type, hlb_ct, cox_ct) %>% 
        mutate(mean_cox = mean(cox_ct),
               hlb_ct_adj = hlb_ct/(cox_ct/mean(cox_ct)))

# Cleaning and joining all tree level data with single obs per tree
pp_tree_data <- pp_join %>% 
        left_join(
                pp_growth_raw %>% 
                        dplyr::filter(plot_id!="pp_00") %>% # get rid of null plots
                        dplyr::select(-c(plot_id:plant_date, comment)),
                by='sys_id'
        ) %>% 
        left_join(
                pp_systems_raw %>%
                        dplyr::select(-c(plot_id:block)),
                by='sys_id'
        ) %>%
        left_join(
                pp_lai_raw %>%
                        mutate(tree = str_pad(string=tree, width=2, side="left", pad="0"),
                               sys_id = paste(row, tree, sep="_")) %>%
                        dplyr::select(sys_id, LAI),
                by='sys_id'
        )

# Cleaning and joining all plot level data with single obs per plot
pp_plot_data <- pp_plots %>% 
        left_join(
                pp_leaf_raw %>% 
                        dplyr::select(plot_id, n_per:cu_ppm),
                by='plot_id'
        ) %>% 
        left_join(
                pp_qpcr %>% 
                        dplyr::select(plot_id, hlb_ct_adj),
                by='plot_id'
        )

# Aggregate and clean all of the raw root data and clean up some of the inconsistencies in the data
pp_root_data <- pp_roots_raw %>% 
        mutate(n_branch_seg = str_remove_all(n_branch_seg, ' '),
               n_branch_seg = str_replace(n_branch_seg, '\\(<', '\\(all<'),
               n_branch = as.numeric(as.vector(str_match(n_branch_seg, pattern = '^(\\d+)\\(*')[,2])),
               branch_sub5mm = as.vector(str_match(n_branch_seg, "(\\d+)<")[,2]),
               all_branch_sub5mm = as.vector(str_match(n_branch_seg, 'all')),
               branch_sub5mm = ifelse(is.na(branch_sub5mm), 0, branch_sub5mm),
               n_branch_lt5mm = as.numeric(ifelse(is.na(all_branch_sub5mm), branch_sub5mm, n_branch))) %>% 
        dplyr::select(-c(branch_sub5mm, all_branch_sub5mm, n_branch_seg))

# Root Measurement Aggregation --------------------------------------------

# Aggregate measurements for each root system, summing or averaging as necessary
# Prop Adair
pa_root_aggregated <- pa_root_data %>% 
        group_by(sys_id) %>% 
        summarize(seg_depth_cm = mean(seg_depth_cm, na.rm=TRUE),
                  em_depth_cm = mean(em_depth_cm, na.rm=TRUE),
                  seg_angle = mean(seg_angle, na.rm=TRUE),
                  seg_b_dia = mean(seg_b_dia, na.rm=TRUE),
                  seg_d_dia = mean(seg_d_dia, na.rm=TRUE),
                  lateral_e = sum(lateral_e, na.rm=TRUE),
                  vertical_e = sum(vertical_e, na.rm=TRUE),
                  straight = sum(straight, na.rm=TRUE),
                  curved = sum(curved, na.rm=TRUE),
                  root_bound = sum(root_bound, na.rm=TRUE),
                  knotted = sum(knotted, na.rm=TRUE), 
                  broken = sum(broken, na.rm=TRUE),
                  branched = sum(branched, na.rm=TRUE), 
                  n_branch = sum(n_branch, na.rm=TRUE),
                  n_branch_lt5mm = sum(n_branch_lt5mm, na.rm=TRUE),
                  n_seg = n()) %>% 
        full_join(pa_join) %>% 
        dplyr::select(sys_id, plot_id:plant_date, everything()) %>% 
        dplyr::filter(sys_id != "17W_28") # Remove the replacement tree data

# Prop Picos
pp_root_aggregated <- pp_root_data %>% 
        group_by(sys_id) %>% 
        summarize(seg_depth_cm = mean(seg_depth_cm, na.rm=TRUE),
                  em_depth_cm = mean(em_depth_cm, na.rm=TRUE),
                  seg_angle = mean(seg_angle, na.rm=TRUE),
                  seg_b_dia = mean(seg_b_dia, na.rm=TRUE),
                  seg_d_dia = mean(seg_d_dia, na.rm=TRUE),
                  lateral_e = sum(lateral_e, na.rm=TRUE),
                  vertical_e = sum(vertical_e, na.rm=TRUE),
                  straight = sum(straight, na.rm=TRUE),
                  curved = sum(curved, na.rm=TRUE),
                  root_bound = sum(root_bound, na.rm=TRUE),
                  knotted = sum(knotted, na.rm=TRUE), 
                  broken = sum(broken, na.rm=TRUE),
                  branched = sum(branched, na.rm=TRUE), 
                  n_branch = sum(n_branch, na.rm=TRUE),
                  n_branch_lt5mm = sum(n_branch_lt5mm, na.rm=TRUE),
                  n_seg = n()) %>% 
        left_join(pp_join) %>% 
        dplyr::select(sys_id, plot_id:plant_date, everything())

# Join the individual root data back to plot metadata
pa_root_data <- pa_root_data %>% 
        left_join(pa_join) %>% 
        dplyr::select(sys_id, plot_id:plant_date, everything()) %>% 
        dplyr::filter(sys_id != "17W_28")

pp_root_data <- pp_root_data %>% 
        left_join(pp_join) %>% 
        dplyr::select(sys_id, plot_id:plant_date, everything())


# Export Data Files -------------------------------------------------------

# Plot level data
write.csv(pa_plot_data, file="../../data/processed/cleaned_data/prop_adair_plot_level.csv")
write.csv(pp_plot_data, file="../../data/processed/cleaned_data/prop_picos_plot_level.csv")

# Tree level data
write.csv(pa_tree_data, file="../../data/processed/cleaned_data/prop_adair_tree_level.csv")
write.csv(pp_tree_data, file="../../data/processed/cleaned_data/prop_picos_tree_level.csv")

# Tree aggregated root data
write.csv(pa_root_aggregated, file="../../data/processed/root_measurements/prop_adair_root_measurement_aggregated.csv")
write.csv(pp_root_aggregated, file = "../../data/processed/root_measurements/prop_picos_root_measurement_aggregated.csv")

# Root level data (non aggregated)
write.csv(pa_root_data, file="../../data/processed/cleaned_data/prop_adair_root_level.csv")
write.csv(pp_root_data, file="../../data/processed/cleaned_data/prop_picos_root_level.csv")


# Clean Up Environment ----------------------------------------------------

rm(list=ls())
