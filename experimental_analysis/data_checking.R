library(ggplot2)
library(tidyverse)

pd_decision_data = read.csv("pd_decision_data.csv")
share_decision_data = read.csv("share_decision_data.csv")
update_decision_data = read.csv("update_decision_data.csv")

pd_check_data <- pd_decision_data %>%
  group_by(
    #treatment_ref,
    opponent_pre_pd_reputation,
    player_decision
  ) %>%
  summarise(n = n())

pd_check_data_low_count <- pd_check_data %>%
  filter(n <= 10)

if (nrow(pd_check_data_low_count) / nrow(pd_check_data) == 0) {
  print("Pass - dataset contains no counts below threshold")
} else {
  print("Fail - dataset contains counts below threshold")
}

share_check_data <- share_decision_data %>%
  filter(neighbour_share_decision != "Sharing Not Possible") %>%
  group_by(
    neighbour_post_pd_reputation,
    neighbour_share_decision
  ) %>%
  summarise(n = n(),
            n_0 = round(sum(neighbour_share_score_0_available, na.rm=T),0),
            n_1 = round(sum(neighbour_share_score_1_available, na.rm=T),0),
            n_2 = round(sum(neighbour_share_score_2_available, na.rm=T),0),
            n_3 = round(sum(neighbour_share_score_3_available, na.rm=T),0),
            n_4 = round(sum(neighbour_share_score_4_available, na.rm=T),0),
            n_5 = round(sum(neighbour_share_score_5_available, na.rm=T),0),
            n_6 = round(sum(neighbour_share_score_6_available, na.rm=T),0),
            n_7 = round(sum(neighbour_share_score_7_available, na.rm=T),0),
            n_8 = round(sum(neighbour_share_score_8_available, na.rm=T),0),
            n_9 = round(sum(neighbour_share_score_9_available, na.rm=T),0),
            n_10 = round(sum(neighbour_share_score_10_available, na.rm=T),0)
            )

share_check_data_low_count <- share_check_data %>%
  filter(neighbour_share_decision == "Share"
         & if_any(starts_with("n_"), ~ .x <= 10))

if (nrow(share_check_data_low_count) / nrow(share_check_data) == 0) {
  print("Pass - dataset contains no counts below threshold")
} else {
  print("Fail - dataset contains counts below threshold")
}

update_check_data <- update_decision_data %>%
  filter(
  gossip_available_different_values == 'True'
  & gossip_available == 1
  & neighbour_gossip != "NA"
  #& treatment_ref == "C"
  ) %>%
  group_by(
    neighbour_post_pd_reputation,
    post_pd_reputation,
    neighbour_gossip,
  ) %>%
  summarise(n = n())

update_check_data_low_count <- update_check_data %>%
  filter(n <= 10)

if (nrow(update_check_data_low_count) / nrow(update_check_data) == 0) {
  print("Pass - dataset contains no counts below threshold")
} else {
  print("Fail - dataset contains counts below threshold")
}

update_check_data <- update_decision_data %>%
  filter(
    gossip_available_different_values == 'True'
    & gossip_available == 1
    & neighbour_gossip != "NA"
    #& treatment_ref == "C"
  ) %>%
  group_by(
    neighbour_post_pd_reputation_group,
    post_pd_reputation_group,
    neighbour_gossip_group,
  ) %>%
  summarise(n = n())

update_check_data_low_count <- update_check_data %>%
  filter(n <= 10)

if (nrow(update_check_data_low_count) / nrow(update_check_data) == 0) {
  print("Pass - dataset contains no counts below threshold")
} else {
  print("Fail - dataset contains counts below threshold")
}
