library(ggplot2)
library(tidyverse)
library(igraph)
library(ggbeeswarm)
library(stringr)

df <- read.csv("experimental_data.csv") %>%
  mutate(treatment_ref = case_when(
    subsession_treatment_id == 2 ~ "Circle Network",
    subsession_treatment_id == 4 ~ "Transitive",
    subsession_treatment_id == 3 ~ "Small World",
  ))

opponent_1_data <- df %>%
  select(
    player_decision1,
    opponent_1_pre_pd_reputation,
    treatment_ref,
    subsession_round_number) %>%
  rename(
    player_decision = player_decision1,
    opponent_pre_pd_reputation = opponent_1_pre_pd_reputation)

opponent_2_data <- df %>%
  select(
    player_decision2,
    opponent_2_pre_pd_reputation,
    treatment_ref,
    subsession_round_number) %>%
  rename(
    player_decision = player_decision2,
    opponent_pre_pd_reputation = opponent_2_pre_pd_reputation)

neighbour_1_data <- df %>%
  select(
    starts_with("neighbour_1"),
    treatment_ref) %>%
  rename_all(
    ~str_replace(.x,"neighbour_1_","neighbour_"))
neighbour_2_data <- df %>%
  select(
    starts_with("neighbour_2"),
    treatment_ref) %>%
  rename_all(
    ~str_replace(.x,"neighbour_2_","neighbour_"))
neighbour_3_data <- df %>%
  select(
    starts_with("neighbour_3"),
    treatment_ref) %>%
  rename_all(
    ~str_replace(.x,"neighbour_3_","neighbour_"))



share_decision_data <- bind_rows(
  neighbour_1_data,
  neighbour_2_data,
  neighbour_3_data
  )

pd_decision_data <- bind_rows(
  opponent_1_data,
  opponent_2_data
  )


pd_decision_data_for_abm <- pd_decision_data %>%
  group_by(treatment_ref, opponent_pre_pd_reputation, player_decision) %>%
  summarise(n = n()) %>%
  mutate(freq = n / sum(n)) %>%
  select(-n)

share_decision_data_for_abm <- share_decision_data %>%
  filter(neighbour_share_decision != "Sharing Not Possible") %>%
  group_by(treatment_ref, neighbour_post_pd_reputation, neighbour_share_decision) %>%
  summarise(n = n()) %>%
  mutate(freq = n / sum(n)) %>%
  select(-n)
