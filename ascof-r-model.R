# title: "R ASCOF Model"
# output: csv files
  
# install.packages("tidyverse")
library(tidyverse)
library(dplyr)
library(readr)

file_list <- list.files(path = "C:/Users/Craig/Dropbox/R/ascof-r-model/data/ascof_raw",
                        pattern = "*.csv", full.names = TRUE)

ascof_df <- map_df(file_list, ~read.csv(.x) %>%
                     mutate(File = basename(.x))) %>%
  mutate(LaCode = coalesce(LaCode,cassr)) %>%
  mutate(Year = as.numeric(str_extract(File, "[0-9]+"))) %>%
  select(LaCode, Year, File, everything()) %>%
  select(-c(cassr)) # drop cassr

# Filter Response/Non-response = 1
# Filter Support Setting: Residential Care or Nursing Care = [2, 3]
#ascof_df <- ascof_df %>% 
  #filter(resp == 1) %>%
  #filter(SupportSetting == 2 | SupportSetting == 3)

# Multiple conditions when adding new column to dataframe:
ascof_df <- ascof_df %>% mutate(Q3a_w =               
                                  case_when(Q3a == 1 ~ 1, 
                                            Q3a == 2 ~ 0.919,
                                            Q3a == 3 ~ 0.541,
                                            Q3a == 4 ~ 0))  %>%
  mutate(Q4a_w =
           case_when(Q4a == 1 ~ 0.911, 
                     Q4a == 2 ~ 0.789,
                     Q4a == 3 ~ 0.265,
                     Q4a == 4 ~ 0.195)) %>%
  mutate(Q5a_w =
           case_when(Q5a == 1 ~ 0.879, 
                     Q5a == 2 ~ 0.775,
                     Q5a == 3 ~ 0.294,
                     Q5a == 4 ~ 0.184)) %>%
  mutate(Q6a_w =
           case_when(Q6a == 1 ~ 0.863, 
                     Q6a == 2 ~ 0.78,
                     Q6a == 3 ~ 0.374,
                     Q6a == 4 ~ 0.288)) %>%
  mutate(Q7a_w =
           case_when(Q7a == 1 ~ 0.88, 
                     Q7a == 2 ~ 0.452,
                     Q7a == 3 ~ 0.298,
                     Q7a == 4 ~ 0.114)) %>%
  mutate(Q8a_w =
           case_when(Q8a == 1 ~ 0.873, 
                     Q8a == 2 ~ 0.748,
                     Q8a == 3 ~ 0.497,
                     Q8a == 4 ~ 0.241)) %>%
  mutate(Q9a_w =
           case_when(Q9a == 1 ~ 0.962, 
                     Q9a == 2 ~ 0.927,
                     Q9a == 3 ~ 0.567,
                     Q9a == 4 ~ 0.17)) %>%
  mutate(Q10_w =
           case_when(Q10 == 1 ~ 0, 
                     Q10 == 2 ~ 0,
                     Q10 == 3 ~ 0,
                     Q10 == 4 ~ 0)) %>%
  mutate(Q11_w =
           case_when(Q11 == 1 ~ 0.847, 
                     Q11 == 2 ~ 0.637,
                     Q11 == 3 ~ 0.295,
                     Q11 == 4 ~ 0.263))

# Calculate current utility weighted care-related quality of life (c_utility)
cols = c('Q3a_w','Q4a_w','Q5a_w','Q6a_w','Q7a_w','Q8a_w','Q9a_w','Q10_w','Q11_w')
ascof_df$c_util <- ascof_df %>% 
  select(cols) %>% 
  transmute(x=rowSums(.)) %>% 
  pull()

ascof_df$c_util <- sapply(ascof_df$c_util, function(x) (x*0.203)-0.466)

# Count of I/ADLs with difficulty or unable to do by self without help
ascof_df <- ascof_df %>% 
  mutate(Q15a_w = ifelse(Q15a > 1, Q15a-1, 0)) %>%
  mutate(Q15b_w = ifelse(Q15b > 1, Q15b-1, 0)) %>%
  mutate(Q15c_w = ifelse(Q15c > 1, Q15c-1, 0)) %>%
  mutate(Q15d_w = ifelse(Q15d > 1, Q15d-1, 0)) %>%
  mutate(Q16a_w = ifelse(Q16a > 1, Q16a-1, 0)) %>%
  mutate(Q16b_w = ifelse(Q16b > 1, Q16b-1, 0)) %>%
  mutate(Q16c_w = ifelse(Q16c > 1, Q16c-1, 0))

cols = c('Q15a_w','Q15b_w','Q15c_w','Q15d_w','Q16a_w','Q16b_w','Q16c_w')
ascof_df$difficulty_count <- ascof_df %>% 
  select(cols) %>% 
  transmute(x=rowSums(.)) %>% 
  pull()

ascof_df$difficulty_count <- ascof_df$difficulty_count * 0.0202 * -1

# IIASC adjustment factors
ascof_df <- ascof_df %>% mutate(agegrp_w = ifelse(agegrp == 2, 0.0473, 0)) %>%
  mutate(Q13a_w = ifelse(Q13 == 3, -0.0148, 0)) %>%
  mutate(Q13b_w = ifelse(Q13 == 4 | Q13 == 5, -0.109, 0)) %>%
  mutate(Q17a_w = ifelse(Q17 == 2, -0.0308, 0)) %>%
  mutate(Q17b_w = ifelse(Q17 == 3 | Q17 == 4, -0.125, 0)) %>%
  mutate(Q18a_w = ifelse(Q18 == 2, -0.0603, 0)) %>%
  mutate(Q18b_w = ifelse(Q18 == 3 | Q18 == 4, -0.11, 0))

cols = c('agegrp_w','Q13a_w','Q13b_w','Q17a_w','Q17b_w','Q18a_w','Q18b_w','difficulty_count')
ascof_df$adj_fac <- ascof_df %>% 
  select(cols) %>% 
  transmute(x=rowSums(.)) %>% 
  pull()

ascof_df$adj_fac <- ascof_df$adj_fac + 0.5798
ascof_df$a_util <- ascof_df$c_util-ascof_df$adj_fac

# filters
#ascof_df <- ascof_df %>% 
  #filter(!is.na(c_util) & (!is.na(a_util)))

# export to .csv
require(data.table)
setDT(ascof_df)
ascof_df[, write.csv(.SD, paste0("data/outputs/ascof_df_", .BY, ".csv")), by = Year]