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
df$neighbour
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
        ~str_replace(.x, glue("neighbour_{j}_"),"neighbour_")
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

update_decision_data <- update_decision_data %>%
  mutate(
    neighbour_post_pd_reputation_group = case_when(neighbour_post_pd_reputation >= 7 ~ 1,
                                                   neighbour_post_pd_reputation <= 3 ~ -1,
                                                   TRUE ~ 0),
    post_pd_reputation_group = case_when(post_pd_reputation >= 7 ~ 1,
                                         post_pd_reputation <= 3 ~ -1,
                                         TRUE ~ 0),
    neighbour_gossip_group = case_when(neighbour_gossip >= 7 ~ 1,
                                       neighbour_gossip <= 3 ~ -1,
                                       TRUE ~ 0),
    final_reputation_group = case_when(final_reputation >= 7 ~ 1,
                                       final_reputation <= 3 ~ -1,
                                       TRUE ~ 0),
  )

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

abm_gossip_decision_distribution_by_gossip_value <- share_decision_data %>%
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
    freq = round((n / sum(n)),2)) %>%
  select(-n) %>%
  relocate("freq", .after = "neighbour_share_decision") %>%
  filter(neighbour_share_decision == "Share") %>%
  arrange(desc(neighbour_post_pd_reputation))

update_decision_data_simple_gossip <- update_decision_data %>%
  filter(
    gossip_available_different_values == 'True'
    & gossip_available == 1
    & neighbour_gossip != "NA"
  )

update_decision_data_complex_gossip <- update_decision_data %>%
  filter(
    gossip_available_different_values == 'True'
    & gossip_available > 1
    & neighbour_gossip != "NA"
  )

table_neighbour_reputation_import_for_gossip_update <- update_decision_data_complex_gossip %>%
  mutate(gossip_consensus_5_group = case_when(gossip_consensus == 0 ~ 0,
                                              gossip_consensus > 0 & gossip_consensus <= 4 ~ 1,
                                              gossip_consensus > 4 & gossip_consensus <= 10 ~ 2,
                                              gossip_consensus > 10 & gossip_consensus <= 20 ~ 3,
                                              gossip_consensus > 20 ~ 4),
         gossip_consensus_2_group = case_when(gossip_consensus == 0 ~ 0,
                                              TRUE ~ 1),
         neighbour_gossip_consensus_flag = neighbour_pre_gossip_consensus > neighbour_post_gossip_consensus) %>%
  group_by(
    neighbour_post_pd_reputation_group,
    gossip_consensus_2_group,
    #gossip_consensus,
    neighbour_gossip_consensus_flag
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2),) %>%
  filter(neighbour_gossip_consensus_flag == TRUE) %>%
  #select(-neighbour_gossip_consensus_flag) %>%
  arrange(desc(neighbour_post_pd_reputation_group))

table_agent_reputation_import_for_gossip_update <- update_decision_data_complex_gossip %>%
  mutate(gossip_consensus_5_group = case_when(gossip_consensus == 0 ~ 0,
                                              gossip_consensus > 0 & gossip_consensus <= 4 ~ 1,
                                              gossip_consensus > 4 & gossip_consensus <= 10 ~ 2,
                                              gossip_consensus > 10 & gossip_consensus <= 20 ~ 3,
                                              gossip_consensus > 20 ~ 4),
         gossip_consensus_2_group = case_when(gossip_consensus == 0 ~ 0,
                                              TRUE ~ 1),
         neighbour_gossip_consensus_flag = neighbour_pre_gossip_consensus > neighbour_post_gossip_consensus,
         match_neighbour_gossip_flag = neighbour_post_gossip_consensus == 0,) %>%
  filter(gossip_consensus_2_group == 1) %>%
  group_by(
    post_pd_reputation_group,
    final_reputation_group,
    #gossip_consensus_2_group,
    #gossip_consensus,
    neighbour_gossip_consensus_flag,
    match_neighbour_gossip_flag,
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2),) %>%
  filter(neighbour_gossip_consensus_flag == TRUE) %>%
  #select(-neighbour_gossip_consensus_flag) %>%
  arrange(desc(final_reputation_group), desc(post_pd_reputation_group))

abm_update_decision_distribution_for_simple_gossip <- update_decision_data_simple_gossip %>%
  group_by(
    neighbour_post_pd_reputation,
    post_pd_reputation,
    neighbour_gossip,
    gossip_change_flag
  ) %>%
  summarise(n = n()) %>%
  #mutate(freq = round(n / sum(n),2)) %>%
  #select(-n) %>%
  arrange(desc(neighbour_post_pd_reputation), desc(neighbour_gossip), desc(post_pd_reputation)) %>%
  filter(gossip_change_flag != "False")

abm_update_decision_distribution_for_simple_gossip_grouped_neighbour_scores <- update_decision_data_simple_gossip %>%
  group_by(
    neighbour_post_pd_reputation_group,
    post_pd_reputation_group,
    neighbour_gossip_group,
    gossip_change_flag
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2),) %>%
  arrange(desc(neighbour_post_pd_reputation_group), desc(post_pd_reputation_group), desc(neighbour_gossip_group)) %>%
  filter(gossip_change_flag != "False") %>%
  select(-gossip_change_flag)

abm_update_decision_distribution_for_complex_gossip_grouped_scores <- update_decision_data_complex_gossip %>%
  group_by(
    neighbour_post_pd_reputation_group,
    post_pd_reputation_group,
    neighbour_gossip_group,
    gossip_change_flag
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2),) %>%
  arrange(desc(neighbour_post_pd_reputation_group), desc(post_pd_reputation_group), desc(neighbour_gossip_group)) #%>%
filter(gossip_change_flag != "False") %>%
  select(-gossip_change_flag)

abm_neighbour_reputation_for_gossip_update <- update_decision_data_complex_gossip %>%
  mutate(gossip_consensus_5_group = case_when(gossip_consensus == 0 ~ 0,
                                              gossip_consensus > 0 & gossip_consensus <= 4 ~ 1,
                                              gossip_consensus > 4 & gossip_consensus <= 10 ~ 2,
                                              gossip_consensus > 10 & gossip_consensus <= 20 ~ 3,
                                              gossip_consensus > 20 ~ 4),
         gossip_consensus_2_group = case_when(gossip_consensus == 0 ~ 0,
                                              TRUE ~ 1),
         neighbour_gossip_consensus_flag = neighbour_pre_gossip_consensus > neighbour_post_gossip_consensus,
         match_neighbour_gossip_flag = neighbour_post_gossip_consensus == 0,) %>%
  filter(gossip_consensus_2_group == 1) %>%
  group_by(
    post_pd_reputation_group,
    final_reputation_group,
    #gossip_consensus_2_group,
    #gossip_consensus,
    neighbour_gossip_consensus_flag,
    match_neighbour_gossip_flag,
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2),) %>%
  filter(neighbour_gossip_consensus_flag == TRUE) %>%
  #select(-neighbour_gossip_consensus_flag) %>%
  arrange(desc(final_reputation_group), desc(post_pd_reputation_group))

write.csv(pd_decision_data, "pd_decision_data.csv")
write.csv(share_decision_data, "share_decision_data.csv")
write.csv(update_decision_data, "update_decision_data.csv")
write.csv(update_decision_data_simple_gossip, "update_decision_data_filtered_simple_gossip.csv")
write.csv(update_decision_data_complex_gossip, "update_decision_data_filtered_complex_gossip.csv")

write.csv(abm_pd_decision_distributions_by_score, "abm_pd_decision_distributions_by_score.csv")
write.csv(abm_pd_scoring_distributions_by_payoff_result, "abm_pd_scoring_distributions_by_payoff_result.csv")
write.csv(abm_gossip_decision_distribution_by_gossip_value, "abm_gossip_decision_distribution_by_gossip_value.csv")
write.csv(abm_update_decision_distribution_for_simple_gossip, "abm_update_decision_distribution_for_simple_gossip.csv")
write.csv(abm_neighbour_reputation_for_gossip_update, "abm_neighbour_reputation_for_gossip_update.csv")
