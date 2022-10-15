library(ggplot2)
library(tidyverse)
library(igraph)
library(ggbeeswarm)
library(stringr)
library(glue)

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

pd_decision_data <- bind_rows(
  opponent_1_data,
  opponent_2_data
  ) %>%
  mutate(
    player_decision = case_when(
      player_decision == "X" ~ "Cooperate",
      player_decision == "Y" ~ "Defect",
    )
  )

for (i in seq(1,3,1)) {
  df_to_bind <- df %>%
    select(
      starts_with(glue("neighbour_{i}")),
      treatment_ref)  %>%
    rename_all(
      ~str_replace(.x,glue("neighbour_{i}_"),"neighbour_")) %>%
    mutate(
      neighbour_share_decision = case_when(
        neighbour_share_decision == "Yes" ~ "Share",
        neighbour_share_decision == "No" ~ "Won't share",
        neighbour_share_decision == "Sharing Not Possible" ~ "Can't share",
      )
    )
  if (i == 1) {
    share_decision_data <- df_to_bind
  } else {
    share_decision_data <- bind_rows(share_decision_data, df_to_bind)
  }
}

for (i in seq(1,16,1)) {
  update_df <- df %>%
    select(
      starts_with(glue("other_player_{i}_"))) %>%
    rename_all(
      ~str_replace(.x,glue("other_player_{i}_"),"")
    )
  rep_df <- df %>%
    select(
      starts_with("neighbour_"),
      -!ends_with("reputation"),
      treatment_ref
    )
  combined_df <- bind_cols(update_df, rep_df)
  for (j in seq(1,3,1)) {
    neighbour_df <- combined_df %>%
      select(
        starts_with(glue("neighbour_{j}_"))) %>%
      rename_all(
        ~str_replace(.x,glue("neighbour_{j}_"),"neighbour_")
      )
    other_df <- combined_df %>%
      select(
        -starts_with(glue("neighbour_")))
    recombined_df <- bind_cols(neighbour_df, other_df)
    if (j == 1) {
      df_to_bind <- recombined_df
    } else {
      df_to_bind <- bind_rows(df_to_bind, recombined_df)
    }
  }
  if (i == 1) {
    update_decision_data <- df_to_bind
  } else {
    update_decision_data <- bind_rows(update_decision_data, df_to_bind)
  }
}

pd_decision_data_for_abm <- pd_decision_data %>%
  group_by(
    treatment_ref,
    opponent_pre_pd_reputation,
    player_decision
    ) %>%
  summarise(n = n()) %>%
  mutate(freq = n / sum(n)) %>%
  select(-n)

share_decision_data_for_abm <- share_decision_data %>%
  filter(neighbour_share_decision != "Sharing Not Possible") %>%
  group_by(
    treatment_ref,
    neighbour_post_pd_reputation,
    neighbour_share_decision
    ) %>%
  summarise(n = n()) %>%
  mutate(freq = n / sum(n)) %>%
  select(-n)

update_decision_data_neighbour_rep_for_abm <- update_decision_data %>%
  filter(gossip_available >= 1 & neighbour_gossip_new_flag == "True") %>%
  group_by(
    treatment_ref,
    neighbour_post_pd_reputation,
    gossip_change_flag
    ) %>%
  summarise(n = n()) %>%
  mutate(freq = n / sum(n)) %>%
  select(-n)

update_decision_data_filtered <- update_decision_data %>%
  mutate(
    gossip_difference = abs(neighbour_gossip - pre_pd_reputation)
  ) %>%
  filter(
    gossip_available >= 1
    & !is.na(gossip_difference)
    & gossip_difference > 0
    & (neighbour_pre_gossip_consensus > 0 | neighbour_gossip_new_flag == 'True')
    )

update_decision_data_gossip_rep_for_abm <- update_decision_data_filtered %>%
  group_by(
    treatment_ref,
    neighbour_gossip,
    gossip_change_flag
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = n / sum(n)) %>%
  select(-n)

update_decision_data_neighbour_rep_for_abm <- update_decision_data_filtered %>%
  group_by(
    treatment_ref,
    neighbour_post_pd_reputation,
    gossip_change_flag
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = n / sum(n)) %>%
  select(-n)

write.csv(pd_decision_data, "pd_decision_data.csv")
write.csv(share_decision_data, "share_decision_data.csv")
write.csv(update_decision_data, "update_decision_data.csv")
write.csv(update_decision_data_filtered, "update_decision_data_filtered.csv")
write.csv(update_decision_data_neighbour_rep_for_abm, "update_decision_data_neighbour_rep.csv")
write.csv(update_decision_data_gossip_rep_for_abm, "update_decision_data_gossip_rep.csv")
