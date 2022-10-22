library(ggplot2)
library(tidyverse)
library(igraph)
library(ggbeeswarm)
library(stringr)
library(glue)

df <- read.csv("game_data.csv") %>%
  mutate(treatment_ref = case_when(
    subsession_treatment_id == 2 ~ "A",
    subsession_treatment_id == 4 ~ "B",
    subsession_treatment_id == 3 ~ "C",
  ))

opponent_1_data <- df %>%
  select(
    unique_id,
    opponent_1_unique_id,
    player_decision1,
    opponent_1_pre_pd_reputation,
    player_payoffs,
    opponent_1_post_pd_reputation,
    treatment_ref,
    subsession_round_number) %>%
  rename(
    player_decision = player_decision1,
    opponent_unique_id = opponent_1_unique_id,
    opponent_pre_pd_reputation = opponent_1_pre_pd_reputation,
    opponent_post_pd_reputation = opponent_1_post_pd_reputation,
    ) %>%
  separate(player_payoffs, c("player_payoff",NA)) %>%
  mutate(player_payoff = strtoi(gsub("cu","",player_payoff)))

opponent_2_data <- df %>%
  select(
    unique_id,
    opponent_2_unique_id,
    player_decision2,
    opponent_2_pre_pd_reputation,
    player_payoffs,
    opponent_2_post_pd_reputation,
    treatment_ref,
    subsession_round_number) %>%
  rename(
    player_decision = player_decision2,
    opponent_unique_id = opponent_2_unique_id,
    opponent_pre_pd_reputation = opponent_2_pre_pd_reputation,
    opponent_post_pd_reputation = opponent_2_post_pd_reputation,
    ) %>%
  separate(player_payoffs, c("player_payoff",NA)) %>%
  mutate(player_payoff = strtoi(gsub("cu","",player_payoff)))

pd_decision_data <- bind_rows(
  opponent_1_data,
  opponent_2_data
  ) %>%
  mutate(
    player_decision = case_when(
      player_decision == "X" ~ "Cooperate",
      player_decision == "Y" ~ "Defect",
    ),
  ) %>%
  rename(
    player_unique_id = unique_id) %>%
  filter(!(player_payoff == 0 & player_decision == "Defect"))
length(unique(df$unique_id))
for (i in seq(1,3,1)) {
  df_to_bind <- df %>%
    select(
      starts_with(glue("neighbour_{i}")),
      unique_id,
      treatment_ref)  %>%
    rename_all(
      ~str_replace(.x,glue("neighbour_{i}_"),"neighbour_")) %>%
    rename(
      player_unique_id = unique_id) %>%
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
unique(df_to_bind$neighbour_unique_id)
for (i in seq(1,16,1)) {
  update_df <- df %>%
    select(
      starts_with(glue("other_player_{i}_")),
      unique_id) %>%
    rename(player_unique_id = unique_id) %>%
    rename_all(
      ~str_replace(.x,glue("other_player_{i}_"),"")) %>%
    rename(target_unique_id = unique_id)

  rep_df <- df %>%
    select(
      starts_with("neighbour_"),
      -!ends_with(c("reputation","unique_id")),
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

abm_pd_decision_distributions_by_score <- pd_decision_data %>%
  group_by(
    #treatment_ref,
    opponent_pre_pd_reputation,
    player_decision
    ) %>%
  summarise(n = n()) %>%
  mutate(freq = n / sum(n)) %>%
  select(-n)

abm_pd_scoring_distributions_by_payoff_result <- pd_decision_data %>%
  group_by(
    #treatment_ref,
    player_payoff,
    opponent_post_pd_reputation,
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2)) %>%
  select(-n) %>%
  arrange(desc(player_payoff))

#share_decision_data_for_abm <- share_decision_data %>%
#  filter(neighbour_share_decision != "Sharing Not Possible") %>%
#  group_by(
#    #treatment_ref,
#    neighbour_post_pd_reputation,
#    neighbour_share_decision
#    ) %>%
#  summarise(n = n()) %>%
#  mutate(freq = n / sum(n)) %>%
#  select(-n)

abm_gossip_value_distribution_by_gossip_value <- share_decision_data %>%
  filter(neighbour_share_decision != "Sharing Not Possible") %>%
  group_by(
    #treatment_ref,
    #neighbour_post_pd_reputation,
    neighbour_share_decision
  ) %>%
  summarise(
    n = n(),
    n_0 = round(mean(neighbour_share_score_0, na.rm=T),2),
    n_1 = round(mean(neighbour_share_score_1, na.rm=T),2),
    n_2 = round(mean(neighbour_share_score_2, na.rm=T),2),
    n_3 = round(mean(neighbour_share_score_3, na.rm=T),2),
    n_4 = round(mean(neighbour_share_score_4, na.rm=T),2),
    n_5 = round(mean(neighbour_share_score_5, na.rm=T),2),
    n_6 = round(mean(neighbour_share_score_6, na.rm=T),2),
    n_7 = round(mean(neighbour_share_score_7, na.rm=T),2),
    n_8 = round(mean(neighbour_share_score_8, na.rm=T),2),
    n_9 = round(mean(neighbour_share_score_9, na.rm=T),2),
    n_10 = round(mean(neighbour_share_score_10, na.rm=T),2)) %>%
  mutate(
    freq = n / sum(n)) %>%
  select(-n) %>%
  relocate("freq", .after = "neighbour_share_decision") %>%
  filter(neighbour_share_decision == "Share")

abm_gossip_value_distribution_by_neighbour_score <- share_decision_data %>%
  filter(neighbour_share_decision != "Sharing Not Possible") %>%
  group_by(
    #treatment_ref,
    neighbour_post_pd_reputation,
    neighbour_share_decision
  ) %>%
  summarise(
    n = n(),
    n_0 = round(mean(neighbour_share_score_0, na.rm=T),2),
    n_1 = round(mean(neighbour_share_score_1, na.rm=T),2),
    n_2 = round(mean(neighbour_share_score_2, na.rm=T),2),
    n_3 = round(mean(neighbour_share_score_3, na.rm=T),2),
    n_4 = round(mean(neighbour_share_score_4, na.rm=T),2),
    n_5 = round(mean(neighbour_share_score_5, na.rm=T),2),
    n_6 = round(mean(neighbour_share_score_6, na.rm=T),2),
    n_7 = round(mean(neighbour_share_score_7, na.rm=T),2),
    n_8 = round(mean(neighbour_share_score_8, na.rm=T),2),
    n_9 = round(mean(neighbour_share_score_9, na.rm=T),2),
    n_10 = round(mean(neighbour_share_score_10, na.rm=T),2)) %>%
  mutate(
    freq = n / sum(n)) %>%
  select(-n) %>%
  relocate("freq", .after = "neighbour_share_decision") %>%
  filter(neighbour_share_decision == "Share") %>%
  arrange(desc(neighbour_post_pd_reputation))

#update_decision_data_neighbour_rep_for_abm <- update_decision_data %>%
#  filter(gossip_available >= 1 & neighbour_gossip_new_flag == "True") %>%
#  group_by(
#    treatment_ref,
#    neighbour_post_pd_reputation,
#    gossip_change_flag
#    ) %>%
#  summarise(n = n()) %>%
#  mutate(freq = n / sum(n)) %>%
#  select(-n)

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

abm_update_decision_distribution_by_gossip_value <- update_decision_data_filtered %>%
  group_by(
    #treatment_ref,
    neighbour_gossip,
    gossip_change_flag
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2)) %>%
  select(-n) %>%
  arrange(desc(neighbour_gossip))

abm_update_decision_distribution_by_neighbour_score <- update_decision_data_filtered %>%
  group_by(
    #treatment_ref,
    neighbour_post_pd_reputation,
    #neighbour_gossip,
    gossip_change_flag
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2)) %>%
  select(-n) %>%
  arrange(desc(neighbour_post_pd_reputation)) %>%
  filter(gossip_change_flag == "True")

abm_update_value_distribution_by_neighbour_score <- update_decision_data_filtered %>%
  group_by(
    #treatment_ref,
    neighbour_post_pd_reputation,
    neighbour_gossip,
    gossip_change_flag
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2)) %>%
  select(-n) %>%
  arrange(desc(neighbour_post_pd_reputation)) %>%
  filter(gossip_change_flag == "True")

#update_decision_data_neighbour_rep_for_abm <- update_decision_data_filtered %>%
#  group_by(
#    treatment_ref,
#    neighbour_post_pd_reputation,
#    gossip_change_flag
#  ) %>%
#  summarise(n = n()) %>%
#  mutate(freq = n / sum(n)) %>%
#  select(-n)

write.csv(pd_decision_data, "pd_decision_data.csv")
write.csv(share_decision_data, "share_decision_data.csv")
write.csv(update_decision_data, "update_decision_data.csv")
write.csv(update_decision_data_filtered, "update_decision_data_filtered.csv")

write.csv(abm_pd_decision_distributions_by_score, "abm_pd_decision_distributions_by_score.csv")
write.csv(abm_pd_scoring_distributions_by_payoff_result, "abm_pd_scoring_distributions_by_payoff_result.csv")
write.csv(abm_gossip_value_distribution_by_gossip_value, "abm_gossip_value_distribution_by_gossip_value.csv")
write.csv(abm_gossip_value_distribution_by_neighbour_score, "abm_gossip_value_distribution_by_neighbour_score.csv")
write.csv(abm_update_decision_distribution_by_gossip_value, "abm_update_decision_distribution_by_gossip_value.csv")
write.csv(abm_update_decision_distribution_by_neighbour_score, "abm_update_decision_distribution_by_neighbour_score.csv")
write.csv(abm_update_value_distribution_by_neighbour_score, "abm_update_value_distribution_by_neighbour_score.csv")
