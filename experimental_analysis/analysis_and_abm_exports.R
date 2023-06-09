### Setup
# Imports the required packages
library(ggplot2)
library(tidyverse)
library(igraph)
library(ggbeeswarm)
library(stringr)
library(glue)
library(RColorBrewer)
library(ggrepel)
library(ggpattern)

my_palette <- RColorBrewer::brewer.pal(11, "Set3")
my_palette_3 <- c(my_palette[0:1], my_palette[6:6], my_palette[11:11])
my_palette_emphasis_3 <- c(my_palette[2:2], my_palette[7:7], my_palette[10:10])

# Loads in the raw data
df <- read.csv("game_data.csv") %>%
  mutate(treatment_ref = case_when(
    subsession_treatment_id == 2 ~ "Circle",
    subsession_treatment_id == 4 ~ "Transitive",
    subsession_treatment_id == 3 ~ "Small World",
  ))

### Analytical datasets
# Creates a dataset containing all opponent 1 relevant columns from raw data
opponent_1_data <- df %>%
  select(
    unique_id,
    opponent_1_unique_id,
    player_decision1,
    opponent_1_pre_pd_reputation,
    player_payoffs,
    opponent_1_post_pd_reputation,
    treatment_ref,
    subsession_round_number,
    player_timed_out) %>%
  rename(
    player_decision = player_decision1,
    opponent_unique_id = opponent_1_unique_id,
    opponent_pre_pd_reputation = opponent_1_pre_pd_reputation,
    opponent_post_pd_reputation = opponent_1_post_pd_reputation,
  ) %>%
  separate(player_payoffs, c("player_payoff",NA)) %>%
  mutate(player_payoff = strtoi(gsub("cu","",player_payoff)))

# Creates a dataset containing all opponent 2 relevant columns from raw data
opponent_2_data <- df %>%
  select(
    unique_id,
    opponent_2_unique_id,
    player_decision2,
    opponent_2_pre_pd_reputation,
    player_payoffs,
    opponent_2_post_pd_reputation,
    treatment_ref,
    subsession_round_number,
    player_timed_out) %>%
  rename(
    player_decision = player_decision2,
    opponent_unique_id = opponent_2_unique_id,
    opponent_pre_pd_reputation = opponent_2_pre_pd_reputation,
    opponent_post_pd_reputation = opponent_2_post_pd_reputation,
  ) %>%
  separate(player_payoffs, c("player_payoff",NA)) %>%
  mutate(player_payoff = strtoi(gsub("cu","",player_payoff)))

# Builds the pd_decision_data analytical dataset from opponent 1 and 2 data
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
  #filter(!(player_payoff == 0 & player_decision == "Defect"))
  filter(substr(player_timed_out, 1, 1) == "a")

# Loops through raw data and builds the share_decision_data analytical dataset
for (i in seq(1,3,1)) {
  df_to_bind <- df %>%
    select(
      starts_with(glue("neighbour_{i}")),
      unique_id,
      treatment_ref,
      player_timed_out)  %>%
    rename_all(
      ~str_replace(.x,glue("neighbour_{i}_"),"neighbour_")) %>%
    rename(
      player_unique_id = unique_id) %>%
    mutate(
      neighbour_share_decision = case_when(
        neighbour_share_decision == "Yes" ~ "Share",
        neighbour_share_decision == "No" ~ "Won't share",
        neighbour_share_decision == "Sharing Not Possible" ~ "Can't share",
      )) %>%
    filter(as.numeric(substr(player_timed_out,2,max(nchar(player_timed_out)))) == 0)
  if (i == 1) {
    share_decision_data <- df_to_bind
  } else {
    share_decision_data <- bind_rows(share_decision_data, df_to_bind)
  }
}

# Loops through the raw data and builds the update_decision_data analytical dataset
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
      treatment_ref,
      player_timed_out
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

# Filters and transforms the update_decision_data to include grouped_reputations
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
  ) %>%
  filter(as.numeric(substr(player_timed_out,2,max(nchar(player_timed_out)))) == 0)


### ABM input datasets
# Creates the pd_decision_distribution_by_score from pd_decision_data
abm_pd_decision_distributions_by_score <- pd_decision_data %>%
  group_by(
    #treatment_ref,
    opponent_pre_pd_reputation,
    player_decision
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = n / sum(n)) %>%
  #select(-n) %>%
  #filter(player_decision == "Cooperate") %>%
  arrange(desc(opponent_pre_pd_reputation))

pd_figure_1_df <- abm_pd_decision_distributions_by_score %>%
  mutate(opponent_pre_pd_reputation = factor(opponent_pre_pd_reputation, levels=c(NA,0,1,2,3,4,5,6,7,8,9,10)),
         player_decision = factor(player_decision, levels=c("Defect", "Cooperate")))

# pd_figure_1_category_df <- pd_figure_1_df %>%
#   mutate(sum = n) %>%
#   group_by(player_decision) %>%
#   summarize(sum_value = sum(sum))
#
# pd_figure_1_all_df <- merge(pd_figure_1_df, pd_figure_1_category_df, by="player_decision", all.x = TRUE) %>%
#   mutate(sum = n,
#          freq = round(sum / sum_value,2))

pd_figure_1 <- ggplot(data = pd_figure_1_df, aes(x = opponent_pre_pd_reputation)) +
  geom_col(aes(y = n, fill = player_decision), position="fill") +
  geom_text(aes(y = n/2, label = paste0("n:", n, "\n", round(freq,2) * 100, "%")), position=position_fill(vjust=0.5), size=4) +
  #geom_smooth(aes(y = consensus_convergence, color=treatment_ref)) +
  #geom_vline(aes(xintercept=all_known), color="red", alpha=0.66) +
  #facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(x = "Opponent Pre-Game Reputation",
       y = "PD Game Interactions",
       fill = "Decision") +
  scale_x_discrete(limits = c(NA,"0","1","2","3","4","5","6","7","8","9","10")) +
  theme(axis.text.x = element_text(angle = 45))

pd_figure_1

# Creates the pd_scoring_distribution_by_payoff from pd_decision_data
abm_pd_scoring_distributions_by_payoff_result <- pd_decision_data %>%
  group_by(
    #treatment_ref,
    player_payoff,
    opponent_post_pd_reputation,
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2)) %>%
  #select(-n) %>%
  arrange(desc(player_payoff))

pd_figure_2_df <- abm_pd_scoring_distributions_by_payoff_result %>%
  filter(!is.na(opponent_post_pd_reputation)) %>%
  mutate(player_payoff = factor(player_payoff, levels=c("0","2","5","6")),
         player_payoff = fct_recode(player_payoff, "Player betrayed"="0", "Both defected"="2", "Cooperation"="5", "Player defected"="6"),
         opponent_post_pd_reputation_group = case_when(opponent_post_pd_reputation >= 7 ~ "Positive",
                                                              opponent_post_pd_reputation <= 3 ~ "Negative",
                                                              TRUE ~ "Neutral"),
         opponent_post_pd_reputation = factor(opponent_post_pd_reputation, levels=rev(c(0,1,2,3,4,5,6,7,8,9,10))),
         sum = n,
         opponent_post_pd_reputation_group = factor(opponent_post_pd_reputation_group, levels=c("Positive","Neutral","Negative")))

# pd_figure_2_category_df <- pd_figure_2_df %>%
#   mutate(sum = n) %>%
#   group_by(player_payoff) %>%
#   summarize(sum_value = sum(sum))
#
# pd_figure_2_all_df <- merge(pd_figure_2_df, pd_figure_2_category_df, by="player_payoff", all.x = TRUE) %>%
#   mutate(sum = n,
#          freq = round(sum / sum_value,2))

pd_figure_2 <- ggplot(data = pd_figure_2_df, aes(x = player_payoff)) +
  geom_col(aes(y = n, fill = opponent_post_pd_reputation), position="fill") +
  #geom_col(data=pd_figure_3_df, aes(y=sum, colour = opponent_post_pd_reputation_group), position="fill", fill=NA, size=1.5) +
  #geom_col_pattern(data=pd_figure_3_df, aes(y=sum, colour = opponent_post_pd_reputation_group, pattern_fill = opponent_post_pd_reputation_group), position="fill", fill=NA, pattern="circle", pattern_colour=NA) +
  geom_text(aes(y = n/2, label = paste0("n:", n, " - ", freq * 100, "%")), position=position_fill(vjust=0.5), size=4) +
  theme_minimal() +
  labs(x = element_blank(),
       y = "Count of Scoring Interactions",
       fill = "Reputation\nScore\nAssigned") +
  scale_x_discrete(limits = c("Player betrayed","Both defected","Cooperation","Player defected")) +
  scale_fill_manual(values=my_palette) +
  scale_colour_manual(values=my_palette_emphasis_3)
  #scale_pattern_colour_manual(values=my_emphasis_palette_3)

pd_figure_2

pd_figure_3_df <- abm_pd_scoring_distributions_by_payoff_result %>%
  filter(!is.na(opponent_post_pd_reputation)) %>%
  mutate(player_payoff = factor(player_payoff, levels=c("0","2","5","6")),
         opponent_post_pd_reputation_group = case_when(opponent_post_pd_reputation >= 7 ~ "Positive",
                                                 opponent_post_pd_reputation <= 3 ~ "Negative",
                                                 TRUE ~ "Neutral"),
         sum = n,
         opponent_post_pd_reputation_group = factor(opponent_post_pd_reputation_group, levels=c("Positive","Neutral","Negative")),
         player_payoff = fct_recode(player_payoff, "Player betrayed"="0", "Both defected"="2", "Cooperation"="5", "Player defected"="6")) %>%
  group_by(player_payoff, opponent_post_pd_reputation_group) %>%
  summarise(total = sum(sum),
            freq = sum(freq)) %>%
  arrange(player_payoff, desc(opponent_post_pd_reputation_group))

pd_figure_3_category_df <- pd_figure_3_df %>%
  group_by(player_payoff) %>%
  summarize(sum_value = sum(total))

pd_figure_3_all_df <- merge(pd_figure_3_df, pd_figure_3_category_df, by="player_payoff", all.x = TRUE) %>%
  mutate(freq = round(total / sum_value,2))

my_palette_3 <- c(my_palette[0:1], my_palette[6:6], my_palette[11:11])

pd_figure_3 <- ggplot(data = pd_figure_3_all_df, aes(x = player_payoff)) +
  geom_col(aes(y = total, fill = opponent_post_pd_reputation_group), position="fill") +
  #geom_col(aes(y = sum, colour = opponent_post_pd_reputation_group), fill=NA, position="fill") +
  geom_text(aes(y = total, label = paste0("n:", total, "\n", freq*100, "%")), position=position_fill(vjust=0.5), size=4) +
  theme_minimal() +
  labs(x = element_blank(),
       y = "Count of Scoring Interactions",
       fill = "Reputation\nScore\nAssigned") +
  scale_x_discrete(limits = c("Player betrayed","Both defected","Cooperation","Player defected")) +
  scale_fill_manual(values=my_palette_3)

pd_figure_3

# Creates hte gossip_distribution output from share_decision_data
abm_gossip_decision_distribution_by_subject_score_and_target_score <- share_decision_data %>%
  filter(neighbour_share_decision != "Sharing Not Possible") %>%
  mutate(neighbour_post_pd_reputation = factor(neighbour_post_pd_reputation, levels=c(NA,0,1,2,3,4,5,6,7,8,9,10))) %>%
  group_by(
    #treatment_ref,
    neighbour_post_pd_reputation,
    neighbour_share_decision
  ) %>%
  summarise(
    n = n(),
    n_0 = round(sum(neighbour_share_score_0_num, na.rm=T),2),
    n_1 = round(sum(neighbour_share_score_1_num, na.rm=T),2),
    n_2 = round(sum(neighbour_share_score_2_num, na.rm=T),2),
    n_3 = round(sum(neighbour_share_score_3_num, na.rm=T),2),
    n_4 = round(sum(neighbour_share_score_4_num, na.rm=T),2),
    n_5 = round(sum(neighbour_share_score_5_num, na.rm=T),2),
    n_6 = round(sum(neighbour_share_score_6_num, na.rm=T),2),
    n_7 = round(sum(neighbour_share_score_7_num, na.rm=T),2),
    n_8 = round(sum(neighbour_share_score_8_num, na.rm=T),2),
    n_9 = round(sum(neighbour_share_score_9_num, na.rm=T),2),
    n_10 = round(sum(neighbour_share_score_10_num, na.rm=T),2)) %>%
  mutate(
    freq = round((n / sum(n)),2)) %>%
  #select(-n) %>%
  relocate("freq", .after = "neighbour_share_decision") %>%
  #filter(neighbour_share_decision == "Share") %>%
  arrange(desc(neighbour_post_pd_reputation))

share_fig_1_df <- abm_gossip_decision_distribution_by_subject_score_and_target_score %>%
  mutate(neighbour_share_decision = factor(neighbour_share_decision, levels=c("Won't share", "Share")))

share_figure_1_category_df <- share_fig_1_df %>%
  mutate(sum = n) %>%
  group_by(neighbour_post_pd_reputation) %>%
  summarize(sum_value = sum(sum))

share_figure_1_all_df <- merge(share_fig_1_df, share_figure_1_category_df, by="neighbour_post_pd_reputation", all.x = TRUE) %>%
  mutate(sum = n,
         freq = round(sum / sum_value,2))

share_figure_1 <- ggplot(data = share_figure_1_all_df, aes(x = neighbour_post_pd_reputation)) +
  geom_col(aes(y = n, fill = neighbour_share_decision), position="fill") +
  geom_text(aes(y = n/2, label = paste0("n:", sum, "\n", freq * 100, "%")), position=position_fill(vjust=0.5), size=4) +
  #geom_smooth(aes(y = consensus_convergence, color=treatment_ref)) +
  #geom_vline(aes(xintercept=all_known), color="red", alpha=0.66) +
  #facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(x = "Gossip Target Reputation",
       y = "Gossip Interactions",
       fill = "Decision") +
  scale_x_discrete(limits = c(NA,"0","1","2","3","4","5","6","7","8","9","10")) +
  theme(axis.text.x = element_text(angle = 45))

share_figure_1

share_fig_2_df <- abm_gossip_decision_distribution_by_subject_score_and_target_score %>%
  #select(-n, -freq) %>%
  pivot_longer(cols = starts_with("n_"),
               names_to = "gossip_subject_reputation",
               values_to = "sum") %>%
  mutate(gossip_subject_reputation = factor(str_extract(gossip_subject_reputation, "\\d+"), levels=rev(c(0,1,2,3,4,5,6,7,8,9,10)))) %>%
  filter(neighbour_share_decision == "Share")

share_figure_2_category_df <- share_fig_2_df %>%
  group_by(neighbour_post_pd_reputation) %>%
  summarize(sum_value = sum(sum))

share_figure_2_all_df <- merge(share_fig_2_df, share_figure_2_category_df, by="neighbour_post_pd_reputation", all.x = TRUE) %>%
  mutate(freq = round(sum / sum_value,2))

share_figure_2 <- ggplot(data = share_figure_2_all_df, aes(x = neighbour_post_pd_reputation)) +
  geom_col(aes(y = sum, fill = gossip_subject_reputation), position="fill") +
  geom_text(aes(y = sum/2, label = paste0("n:",sum, " - ", freq * 100, "%")), position=position_fill(vjust=0.5), size=2) +
  theme_minimal() +
  labs(x = "Gossip Target Reputation",
       y = "Count of Sharing Interactions",
       fill = "Gossip\nSubject\nReputation") +
  scale_x_discrete(limits = c(NA,"0","1","2","3","4","5","6","7","8","9","10")) +
  scale_fill_manual(values=my_palette) +
  theme(axis.text.x = element_text(angle = 45))

share_figure_2

share_fig_3_df <- abm_gossip_decision_distribution_by_subject_score_and_target_score %>%
  #select(-n, -freq) %>%
  pivot_longer(cols = starts_with("n_"),
               names_to = "gossip_subject_reputation",
               values_to = "sum") %>%
  mutate(gossip_subject_reputation = as.numeric(str_extract(gossip_subject_reputation, "\\d+"))) %>%
  filter(neighbour_share_decision == "Share") %>%
  mutate(gossip_subject_reputation = case_when(gossip_subject_reputation >= 7 ~ "Positive",
                                               gossip_subject_reputation <= 3 ~ "Negative",
                                               TRUE ~ "Neutral"),
         gossip_subject_reputation = factor(gossip_subject_reputation, levels=c("Positive","Neutral","Negative"))) %>%
  group_by(neighbour_post_pd_reputation, gossip_subject_reputation) %>%
  summarise(sum = sum(sum)) %>%
  arrange(neighbour_post_pd_reputation, desc(gossip_subject_reputation))

share_figure_3_category_df <- share_fig_3_df %>%
  group_by(neighbour_post_pd_reputation) %>%
  summarize(sum_value = sum(sum))

share_figure_3_all_df <- merge(share_fig_3_df, share_figure_3_category_df, by="neighbour_post_pd_reputation", all.x = TRUE) %>%
  mutate(freq = round(sum / sum_value,2))

share_figure_3 <- ggplot(data = share_figure_3_all_df, aes(x = neighbour_post_pd_reputation)) +
  geom_col(aes(y = sum, fill = gossip_subject_reputation), position="fill") +
  geom_text(aes(y = sum/2, label = paste0("n:", sum, "\n", freq*100, "%")), position=position_fill(vjust=0.5), size=4) +
  theme_minimal() +
  labs(x = "Gossip Target Reputation",
       y = "Count of Sharing Interactions",
       fill = "Gossip\nSubject\nReputation") +
  scale_x_discrete(limits = c(NA,"0","1","2","3","4","5","6","7","8","9","10")) +
  scale_fill_manual(values=my_palette_3)

share_figure_3

update_decision_data_simple_gossip <- update_decision_data %>%
  filter(
    gossip_available_different_values == 'True'
    & gossip_available == 1
    & neighbour_gossip != "NA"
    #& treatment_ref == "C"
  )

update_decision_data_complex_gossip <- update_decision_data %>%
  filter(
    gossip_available_different_values == 'True'
    & gossip_available > 1
    & neighbour_gossip != "NA"
    #& treatment_ref == "A"
  )

abm_table_neighbour_reputation_import_for_gossip_update <- update_decision_data_complex_gossip %>%
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
    #gossip_change_flag
  ) %>%
  summarise(n = n()) %>%
  #mutate(freq = round(n / sum(n),2)) %>%
  #select(-n) %>%
  arrange(desc(neighbour_post_pd_reputation), desc(neighbour_gossip), desc(post_pd_reputation)) #%>%
  #filter(gossip_change_flag != "False")

abm_update_decision_distribution_for_simple_gossip_grouped_neighbour_scores <- update_decision_data_simple_gossip %>%
  group_by(
    neighbour_post_pd_reputation_group,
    post_pd_reputation_group,
    neighbour_gossip_group,
    gossip_change_flag
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2),) %>%
  arrange(desc(neighbour_post_pd_reputation_group), desc(post_pd_reputation_group), desc(neighbour_gossip_group))

update_figure_1_df <- abm_update_decision_distribution_for_simple_gossip_grouped_neighbour_scores %>%
  mutate(neighbour_post_pd_reputation_group = factor(neighbour_post_pd_reputation_group, levels=c("-1","0","1")),
         post_pd_reputation_group = factor(post_pd_reputation_group, levels=c("-1","0","1")),
         neighbour_gossip_group = factor(neighbour_gossip_group, levels=c("-1","0","1")),
         gossip_change_flag = factor(gossip_change_flag, levels=rev(c("True","False"))),
         neighbour_post_pd_reputation_group = fct_recode(neighbour_post_pd_reputation_group, "Negative"="-1", "Neutral"="0", "Positive"="1"),
         post_pd_reputation_group = fct_recode(post_pd_reputation_group, "Negative Current Reputation"="-1", "Neutral Current Reputation"="0", "Positive Current Reputation"="1"),
         neighbour_gossip_group = fct_recode(neighbour_gossip_group, "Negative Gossip Reputation"="-1", "Neutral Gossip Reputation"="0", "Positive Gossip Reputation"="1"))
         #neighbour_gossip_group = fct_recode(neighbour_gossip_group, "Negative"="-1", "Neutral"="0", "Positive"="1"))

update_figure_1_category_df <- update_figure_1_df %>%
  mutate(sum = n) %>%
  group_by(neighbour_post_pd_reputation_group, post_pd_reputation_group, neighbour_gossip_group) %>%
  summarize(sum_value = sum(sum))

update_figure_1_all_df <- merge(update_figure_1_df, update_figure_1_category_df, by=c("neighbour_post_pd_reputation_group", "post_pd_reputation_group", "neighbour_gossip_group"), all.x = TRUE) %>%
  mutate(sum = n,
         freq = round(sum / sum_value,2)) %>%
  arrange(post_pd_reputation_group, desc(neighbour_gossip_group), desc(gossip_change_flag))

update_figure_1 <- ggplot(data = update_figure_1_all_df, aes(x = neighbour_post_pd_reputation_group)) +
  geom_col(aes(y = n, fill = gossip_change_flag), position="fill") +
  geom_text(aes(y = n/2, label = paste0("n:", n, "\n", freq * 100, "%")), position=position_fill(vjust=0.5), size=4) +
  facet_wrap(facets = vars(post_pd_reputation_group, neighbour_gossip_group), ncol=3) +
  theme_minimal() +
  labs(x = "Gossip Sender Reputation",
       y = "Update Interactions",
       fill = "Decision") +
  #scale_x_discrete(limits = c("-1","0","1")) +
  #scale_fill_manual(values=rev(c("#619CFF", "#F8766D"))) +
  theme(axis.text.x = element_text(angle = 45))

update_figure_1

update_figure_2_df <- update_figure_1_df %>%
  filter(gossip_change_flag != "False") %>%
  mutate(neighbour_gossip_group = fct_recode(neighbour_gossip_group, "Positive"="Positive Gossip Reputation", "Neutral"="Neutral Gossip Reputation", "Negative"="Negative Gossip Reputation"),
         neighbour_gossip_group = factor(neighbour_gossip_group, levels = c("Positive", "Neutral", "Negative")),
         sum = n) %>%
  arrange(post_pd_reputation_group, desc(neighbour_gossip_group))

update_figure_2_category_df <- update_figure_2_df %>%
  group_by(neighbour_post_pd_reputation_group, post_pd_reputation_group) %>%
  summarize(sum_value = sum(sum))

update_figure_2_all_df <- merge(update_figure_2_df, update_figure_2_category_df, by=c("neighbour_post_pd_reputation_group", "post_pd_reputation_group"), all.x = TRUE) %>%
  mutate(freq = round(sum / sum_value,2)) %>%
  arrange(post_pd_reputation_group, desc(neighbour_gossip_group))

update_figure_2 <- ggplot(data = update_figure_2_all_df, aes(x = neighbour_post_pd_reputation_group)) +
  geom_col(aes(y = n, fill = neighbour_gossip_group), position="fill") +
  geom_text(aes(y = n/2, label = paste0("n:", sum, "\n", freq * 100, "%")), position=position_fill(vjust=0.5), size=4) +
  facet_wrap(facets = vars(post_pd_reputation_group), ncol=3) +
  theme_minimal() +
  labs(x = "Gossip Sender Reputation",
       y = "Update Interactions",
       fill = "Gossip\nReputation") +
  #scale_x_discrete(limits = c("-1","0","1")) +
  #scale_fill_manual(values=c("#619CFF", "#F8766D")) +
  scale_fill_manual(values=my_palette_3) +
  theme(axis.text.x = element_text(angle = 45))

update_figure_2

abm_update_decision_distribution_for_complex_gossip_grouped_scores <- update_decision_data_complex_gossip %>%
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
    neighbour_post_pd_reputation_group,
    neighbour_gossip_consensus_flag,
  ) %>%
  summarise(n = n()) %>%
  mutate(freq = round(n / sum(n),2),) %>%
  filter(neighbour_gossip_consensus_flag == TRUE) %>%
  select(-neighbour_gossip_consensus_flag) %>%
  arrange(desc(neighbour_post_pd_reputation_group))

update_figure_3_df <- abm_neighbour_reputation_for_gossip_update %>%
  mutate(neighbour_post_pd_reputation_group = factor(neighbour_post_pd_reputation_group, levels=c("-1","0","1")),
         neighbour_post_pd_reputation_group = fct_recode(neighbour_post_pd_reputation_group, "Negative"="-1", "Neutral"="0", "Positive"="1"),
         neighbour_post_pd_reputation_group = factor(neighbour_post_pd_reputation_group, levels=rev(c("Negative", "Neutral", "Positive"))),
         freq = round(n/sum(abm_neighbour_reputation_for_gossip_update$n),2) * 100) %>%
  arrange(desc(neighbour_post_pd_reputation_group))
update_figure_3_df$ypos <- c(4,16,62)

update_figure_3 <- ggplot(update_figure_3_df, aes(x="", y=n, fill = neighbour_post_pd_reputation_group)) +
  geom_bar(stat="identity", width=1, color="white") +
  coord_polar("y", start=0) +
  theme_void() +
  geom_text(aes(y = ypos, label = paste0("n:",n,"\n",freq,"%")), size=4) +
  labs(x = "Gossip Sender Reputation",
       y = element_blank(),
       fill = "Gossip\nSender\nReputation") +
  #scale_x_discrete(limits = c("-1","0","1")) +
  #scale_fill_manual(values=c("#619CFF", "#F8766D")) +
  scale_fill_manual(values=my_palette_3)

update_figure_3

write.csv(pd_decision_data, "pd_decision_data.csv")
write.csv(share_decision_data, "share_decision_data.csv")
write.csv(update_decision_data, "update_decision_data.csv")
write.csv(update_decision_data_simple_gossip, "update_decision_data_filtered_simple_gossip.csv")
write.csv(update_decision_data_complex_gossip, "update_decision_data_filtered_complex_gossip.csv")

write.csv(abm_pd_decision_distributions_by_score, "abm_pd_decision_distributions_by_score.csv")
write.csv(abm_pd_scoring_distributions_by_payoff_result, "abm_pd_scoring_distributions_by_payoff_result.csv")
write.csv(abm_gossip_decision_distribution_by_subject_score_and_target_score, "abm_gossip_decision_distribution_by_gossip_value.csv")
write.csv(abm_update_decision_distribution_for_simple_gossip, "abm_update_decision_distribution_for_simple_gossip.csv")
write.csv(abm_update_decision_distribution_for_simple_gossip_grouped_neighbour_scores, "abm_update_decision_distribution_for_simple_gossip_grouped_neighbour_scores.csv")
write.csv(abm_neighbour_reputation_for_gossip_update, "abm_neighbour_reputation_for_gossip_update.csv")
