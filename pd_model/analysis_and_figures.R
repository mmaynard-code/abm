library(ggplot2)
library(tidyverse)
library(ggbeeswarm)


cols_to_select = c(
  "iteration",
  "Step",
  "network_groups",
  "total_networks",
  "treatment_ref",
  "game_type",
  "agent_id",
  "cooperation",
  "payoff_total",
  "payoff_mean",
  "cooperation_round",
  "session_consensus",
  "network_consensus",
  "neighbour_consensus",
  "session_cooperation",
  "network_cooperation",
  "neighbour_cooperation",
  "session_gossip",
  "network_gossip",
  "neighbour_gossip"
)

file_list = list.files(pattern = "(result)\\_.*")

is.martingale <- function(X) {
  for (n in 2:length(X)) {
    if (mean(X[1:(n-1)]) != X[n-1]) return(FALSE)
  }
  return(TRUE)
}

almost.sure.convergence <- function(X) {
  limit <- mean(X)
  for (n in 2:length(X)) {
    if (abs(mean(X[1:n]) - limit) > 0.01) return(FALSE)
  }
  return(TRUE)
}

for (i in seq(1, length(file_list), 1)) {
  print(file_list[i])
  input_df = read.csv(file_list[i]) %>%
    mutate(source_file = file_list[i],
           round_number = Step,)
  for (j in seq(min(input_df$iteration),max(input_df$iteration),1)) {
    iteration_df = input_df %>%
      filter(iteration == j)
    session_df = iteration_df %>%
      group_by(source_file, iteration, round_number) %>%
      summarise(session_consensus = mean(session_consensus),
                session_cooperation = mean(session_cooperation),
                session_gossip = mean(session_gossip)) %>%
      mutate(prev_session_consensus = lag(session_consensus, 1),
             prev_session_cooperation = lag(session_cooperation, 1),
             prev_session_gossip = mean(session_gossip, 1),
             session_consensus_convergence = (prev_session_consensus - session_consensus)^2,
             session_cooperation_convergence = (prev_session_cooperation - session_cooperation)^2,
             session_gossip_convergence = (session_gossip - prev_session_gossip)^2)
    if (j == 0) {
      df_to_bind = session_df
    } else {
      df_to_bind = bind_rows(df_to_bind, session_df)
    }
  }
  if (i == 1) {
    all_abm_ses_df = df_to_bind
  } else {
    all_abm_ses_df = bind_rows(all_abm_ses_df, df_to_bind)
  }
}

for (i in seq(1, length(file_list), 1)) {
  print(file_list[i])
  input_df = read.csv(file_list[i]) %>%
    mutate(source_file = file_list[i],
           round_number = Step,)
  for (j in seq(min(input_df$iteration),max(input_df$iteration),1)) {
      iteration_df = input_df %>%
      filter(iteration == j)
    for (k in seq(min(input_df$network_id), max(input_df$network_id), 1)) {
      network_df = iteration_df %>%
        filter(network_id == k) %>%
        group_by(source_file, iteration, round_number) %>%
        summarise(consensus = mean(network_consensus),
                  cooperation = mean(network_cooperation),
                  gossip = mean(network_gossip)) %>%
        mutate(prev_consensus = lag(consensus, 1),
               prev_cooperation = lag(cooperation, 1),
               prev_gossip = mean(gossip, 1),
               consensus_convergence = (prev_consensus - consensus)^2,
               cooperation_convergence = (prev_cooperation - cooperation)^2,
               gossip_convergence = (prev_gossip - gossip)^2)
      if (j == 0) {
        df_to_bind = network_df
      } else {
        df_to_bind = bind_rows(df_to_bind, network_df)
      }
    }
  }
  if (i == 1) {
    all_abm_net_df = df_to_bind
  } else {
    all_abm_net_df = bind_rows(all_abm_net_df, df_to_bind)
  }
}


for (i in seq(1, length(file_list), 1)) {
  print(file_list[i])
  input_df = read.csv(file_list[i]) %>%
    mutate(source_file = file_list[i],
           round_number = Step,)
  for (j in seq(min(input_df$iteration),max(input_df$iteration),1)) {
    iteration_df = input_df %>%
      filter(iteration == j)
    for (k in seq(min(input_df$AgentID), max(input_df$AgentID), 1)) {
      neighbour_df = iteration_df %>%
        filter(network_id == k) %>%
        group_by(source_file, iteration, round_number) %>%
        summarise(consensus = mean(neighbour_consensus),
                  cooperation = mean(neighbour_cooperation),
                  gossip = mean(neighbour_gossip)) %>%
        mutate(prev_consensus = lag(consensus, 1),
               prev_cooperation = lag(cooperation, 1),
               prev_gossip = mean(gossip, 1),
               consensus_convergence = (prev_consensus - consensus)^2,
               cooperation_convergence = (prev_cooperation - cooperation)^2,
               gossip_convergence = (prev_gossip - gossip)^2)
      if (j == 0) {
        df_to_bind = neighbour_df
      } else {
        df_to_bind = bind_rows(df_to_bind, neighbour_df)
      }
    }
  }
  if (i == 1) {
    all_abm_ngh_df = df_to_bind
  } else {
    all_abm_ngh_df = bind_rows(all_abm_ngh_df, df_to_bind)
  }
}

filter_df <- all_abm_ses_df %>%
  filter(source_file == all_abm_ses_df$source_file[1]
         & iteration == 1)

filter_df <- head(filter_df, 1001)

is.martingale(na.omit(filter_df$session_consensus_convergence))
almost.sure.convergence(na.omit(filter_df$session_consensus_convergence))

all_known_lookup <- all_abm_ses_df %>%
  group_by(source_file, iteration, round_number) %>%
  summarise(all_known = mean(all_known),
            all_played = mean(all_played)) %>%
  group_by(source_file, iteration) %>%
  summarise(all_known = min(all_known, na.rm=TRUE),
            all_played = min(all_played, na.rm = TRUE)) %>%
  group_by(source_file) %>%
  summarise(all_known = min(all_known),
            all_played = min(all_played)) %>%
  mutate(all_known_played_diff = abs(all_known - all_played))

str_split(str_sub(all_abm_ses_df$source_file[1],0,-5),"_")[[1]][5]

session_df <- all_abm_ses_df %>%
  #left_join(all_known_lookup, by="source_file") %>%
  select(-ends_with(".y")) %>%
  mutate(game_type = str_split(str_sub(source_file[1],0,-5),"_")[[1]][5],
         treatment_ref = str_split(str_sub(source_file[1],0,-5),"_")[[1]][4],
         network_size = as.numeric(str_split(str_sub(source_file[1],0,-5),"_")[[1]][2]) * 4,
         total_networks = str_split(str_sub(source_file[1],0,-5),"_")[[1]][3]) %>%
  group_by(game_type, network_size, total_networks, treatment_ref, round_number) %>%
  summarise(
    consensus_convergence = mean(session_consensus_convergence),
    cooperation_convergence = mean(session_cooperation_convergence),
    gossip_convergence = mean(session_gossip_convergence),
    #all_known = mean(all_known),
    #all_played = mean(all_played),
  )

network_df <- all_abm_net_df %>%
  left_join(all_known_lookup, by="source_file") %>%
  select(-ends_with(".y")) %>%
  mutate(game_type = str_split(str_sub(source_file[1],0,-5),"_")[[1]][5],
         treatment_ref = str_split(str_sub(source_file[1],0,-5),"_")[[1]][4],
         network_size = as.numeric(str_split(str_sub(source_file[1],0,-5),"_")[[1]][2]) * 4,
         total_networks = str_split(str_sub(source_file[1],0,-5),"_")[[1]][3]) %>%
  group_by(game_type, network_size, total_networks, treatment_ref, round_number) %>%
  summarise(
    consensus_convergence = mean(consensus_convergence),
    cooperation_convergence = mean(cooperation_convergence),
    gossip_convergence = mean(gossip_convergence),
    all_known = mean(all_known),
    all_played = mean(all_played),
  )

neighbour_df <- all_abm_ngh_df %>%
  left_join(all_known_lookup, by="source_file") %>%
  select(-ends_with(".y")) %>%
  mutate(game_type = str_split(str_sub(source_file[1],0,-5),"_")[[1]][5],
         treatment_ref = str_split(str_sub(source_file[1],0,-5),"_")[[1]][4],
         network_size = as.numeric(str_split(str_sub(source_file[1],0,-5),"_")[[1]][2]) * 4,
         total_networks = str_split(str_sub(source_file[1],0,-5),"_")[[1]][3]) %>%
  group_by(game_type, network_size, total_networks, treatment_ref, round_number) %>%
  summarise(
    consensus_convergence = mean(consensus_convergence),
    cooperation_convergence = mean(cooperation_convergence),
    gossip_convergence = mean(gossip_convergence),
    all_known = mean(all_known),
    all_played = mean(all_played),
  )

ses_abm_df <- all_abm_df %>%
  select(-all_known, -all_played) %>%
  left_join(all_known_lookup, by="source_file") %>%
  select(-ends_with(".y")) %>%
  group_by(game_type, network_size, total_networks, treatment_ref, round_number) %>%
  summarise(
    payoff_total = mean(payoff_total),
    payoff_mean = mean(payoff_mean),
    session_consensus = mean(session_consensus),
    network_consensus = mean(network_consensus),
    neighbour_consensus = mean(neighbour_consensus),
    session_cooperation = mean(session_cooperation),
    network_cooperation = mean(network_cooperation),
    neighbour_cooperation = mean(neighbour_cooperation),
    session_gossip = mean(session_gossip),
    network_gossip = mean(network_gossip),
    neighbour_gossip = mean(neighbour_gossip),
    diff_session_consensus = mean(diff_session_consensus),
    diff_network_consensus = mean(diff_session_consensus),
    diff_neighbour_consensus = mean(diff_neighbour_consensus),
    diff_session_cooperation = mean(diff_session_cooperation),
    diff_network_cooperation = mean(diff_network_cooperation),
    diff_neighbour_cooperation = mean(diff_neighbour_cooperation),
    all_known = mean(all_known),
    all_played = mean(all_played),
    all_known_played_diff = mean(all_known_played_diff),
    session_consensus_convergence = mean(session_consensus_convergence),
    network_consensus_convergence = mean(network_consensus_convergence),
    neighbour_consensus_convergence = mean(neighbour_consensus_convergence),
    session_cooperation_convergence = mean(session_cooperation_convergence),
    network_cooperation_convergence = mean(network_cooperation_convergence),
    neighbour_cooperation_convergence = mean(neighbour_cooperation_convergence)
  )

treat_a_df <- session_df %>% filter(treatment_ref == "A")
treat_b_df <- session_df %>% filter(treatment_ref == "B")
treat_c_df <- session_df %>% filter(treatment_ref == "C")

convergence_a <- ggplot(data = treat_a_df, aes(x = round_number)) +
  geom_line(aes(y = consensus_convergence, color = as_factor(total_networks))) +
  #geom_line(aes(y = network_consensus_convergence, color = as_factor(total_networks)), alpha=0.5) +
  #geom_line(aes(y = neighbour_consensus_convergence, color = as_factor(total_networks)), alpha=0.5) +
  #geom_vline(aes(xintercept = all_played, color = as_factor(total_networks))) +
  #geom_vline(aes(xintercept = all_known, color = as_factor(total_networks)), linetype = "dotdash") +
  #geom_hline(aes(yintercept = mean(session_consensus_convergence)), color = "red") +
  facet_wrap(facets = vars(game_type, network_size))

convergence_a

convergence_b <- ggplot(data = treat_b_df, aes(x = round_number)) +
  geom_line(aes(y = consensus_convergence, color = as_factor(total_networks))) +
  #geom_line(aes(y = network_consensus_convergence, color = as_factor(total_networks)), alpha=0.5) +
  #geom_line(aes(y = neighbour_consensus_convergence, color = as_factor(total_networks)), alpha=0.5) +
  #geom_vline(aes(xintercept = all_played, color = as_factor(total_networks))) +
  #geom_vline(aes(xintercept = all_known, color = as_factor(total_networks)), linetype = "dotdash") +
  #geom_hline(aes(yintercept = 0.0001), color = "red") +
  facet_wrap(facets = vars(game_type, network_size))

convergence_c <- ggplot(data = treat_c_df, aes(x = round_number)) +
  geom_line(aes(y = consensus_convergence, color = as_factor(total_networks))) +
  #geom_line(aes(y = network_consensus_convergence, color = as_factor(total_networks)), alpha=0.5) +
  #geom_line(aes(y = neighbour_consensus_convergence, color = as_factor(total_networks)), alpha=0.5) +
  #geom_vline(aes(xintercept = all_played, color = as_factor(total_networks))) +
  #geom_vline(aes(xintercept = all_known, color = as_factor(total_networks)), linetype = "dotdash") +
  #geom_hline(aes(yintercept = 0.0001), color = "red") +
  facet_wrap(facets = vars(game_type, network_size))

convergence_a
convergence_b
convergence_c

exp_equiv_df <- all_abm_df %>%
  group_by(game_type, treatment_ref, network_size, session_size, total_networks, neighbours, Step) %>%
  summarise(avg_prop_coop = mean(Cooperation),
            avg_prop_coop_rnd = mean(Cooperation_Round),
            avg_consensus_ses = mean(session_consensus),
            avg_consensus_net = mean(network_consensus),
            avg_consensus_nbr = mean(neighbour_consensus),
            avg_cooperation_ses = mean(session_cooperation),
            avg_cooperation_net = mean(network_cooperation),
            avg_cooperation_nbr = mean(neighbour_cooperation),
            avg_gossip_ses = mean(session_gossip / neighbours),
            avg_gossip_net = mean(network_gossip / neighbours),
            avg_gossip_nbr = mean(neighbour_gossip / neighbours))

unique(exp_equiv_df$neighbours)
ggplot(data = exp_equiv_df, aes(x = Step, y = avg_gossip_ses, color = treatment_ref)) +
  geom_line() +
  #geom_smooth() +
  facet_wrap(facets = vars(game_type, total_networks, session_size))

ggplot(data = exp_equiv_df, aes(x = avg_gossip, y = avg_consensus_nbr, color = treatment_ref)) +
  #geom_line() +
  geom_smooth() +
  facet_wrap(facets = vars(game_type, total_networks, session_size))

# Hypotheses

# G1 - the consensus is positively correlated with the frequency of gossip sharing within the group
g1_df = all_abm_df %>%
  filter(game_type == "gossip")

ggplot(data = g1_df) +
  geom_smooth(aes(x = neighbour_gossip, y = neighbour_consensus, color = "neighbour")) +
  geom_smooth(aes(x = network_gossip, y = network_consensus, color = "network")) +
  geom_smooth(aes(x = session_gossip, y = session_consensus, color = "session")) +
  facet_wrap(facets = vars(game_type, network_size))


# G2 - the consensus is greater within small world networks than circle networks

g2_df = all_abm_df %>%
  filter(game_type == "gossip")

ggplot(data = g2_df, aes(x = treatment_ref)) +
  geom_boxplot(aes(y = neighbour_consensus, color = "neighbour"), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

ggplot(data = g2_df, aes(x = treatment_ref)) +
  geom_boxplot(aes(y = network_consensus, color = "network"), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

ggplot(data = g2_df, aes(x = treatment_ref)) +
  geom_boxplot(aes(y = session_consensus, color = "session"), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))


# G3 - the mean group payoff is positively correlated with higher frequencies of gossip sharing within the group

g3_df = all_abm_df %>%
  filter(game_type == "gossip")

ggplot(data = g3_df) +
  geom_point(aes(x = neighbour_gossip, y = payoff_mean, color = "neighbour")) +
  geom_point(aes(x = network_gossip, y = payoff_mean, color = "network")) +
  geom_point(aes(x = session_gossip, y = payoff_mean, color = "session")) +
  facet_wrap(facets = vars(game_type, network_size))

ggplot(data = g3_df, aes(x = payoff_mean)) +
  geom_point(aes(y = neighbour_gossip, color = "neighbour"), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

ggplot(data = g3_df, aes(x = payoff_mean)) +
  geom_boxplot(aes(y = network_gossip, color = "network"), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

ggplot(data = g3_df, aes(x = payoff_mean)) +
  geom_boxplot(aes(y = session_gossip, color = "session"), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

# G4 - the mean payoff is positively correlated with increased consensus within the group

g4_df = all_abm_df %>%
  filter(game_type == "gossip")

ggplot(data = g4_df) +
  geom_point(aes(x = neighbour_consensus, y = payoff_mean, color = "neighbour")) +
  geom_smooth(aes(x = network_consensus, y = payoff_mean, color = "network")) +
  geom_smooth(aes(x = session_consensus, y = payoff_mean, color = "session")) +
  facet_wrap(facets = vars(game_type, network_size))

ggplot(data = g4_df, aes(x = payoff_mean)) +
  geom_boxplot(aes(y = neighbour_consensus, color = "neighbour"), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

ggplot(data = g4_df, aes(x = payoff_mean)) +
  geom_boxplot(aes(y = network_consensus, color = "network"), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

ggplot(data = g4_df, aes(x = payoff_mean)) +
  geom_boxplot(aes(y = session_consensus, color = "session"), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

# G5 - the level of cooperative interactions in the group is greater within small world networks than circle networks

g5_df = all_abm_df

ggplot(data = g5_df, aes(x = treatment_ref)) +
  geom_boxplot(aes(y = neighbour_cooperation), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

ggplot(data = g5_df, aes(x = treatment_ref)) +
  geom_boxplot(aes(y = network_cooperation), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

ggplot(data = g5_df, aes(x = treatment_ref)) +
  geom_boxplot(aes(y = session_cooperation), notch = TRUE, outlier.alpha = 0.1) +
  facet_wrap(facets = vars(game_type, network_size))

# G6 - the level of cooperative interactions between individuals in the neighbour group is greater than between the network or session

g6_df = all_abm_df %>%
  mutate(nbr_net_diff = neighbour_cooperation / network_cooperation - 1,
         nbr_ses_diff = neighbour_cooperation / session_cooperation - 1,
         net_ses_diff = network_cooperation / session_cooperation - 1)

ggplot(data = g6_df, aes(x = nbr_net_diff, y = factor(treatment_ref), color = treatment_ref)) +
  geom_boxplot() +
  facet_wrap(facets = vars(game_type, network_size)) +
  xlim(-0.10, 0.10)

ggplot(data = g6_df, aes(x = nbr_ses_diff, y = factor(treatment_ref), color = treatment_ref)) +
  geom_boxplot() +
  facet_wrap(facets = vars(game_type, network_size)) +
  xlim(-0.10, 0.10)

# G7 - the level of cooperative interactions between individuals in the network is greater than between the session

g7_df = g6_df %>%
  group_by(game_type, treatment_ref, network_size, session_size, total_networks, neighbours, Step) %>%
  summarise(avg_net_ses_diff = mean(net_ses_diff))

ggplot(data = g6_df, aes(x = net_ses_diff, y = factor(treatment_ref), color = treatment_ref)) +
  geom_boxplot() +
  geom_vline(xintercept=0, color="red") +
  facet_wrap(facets = vars(game_type, network_size)) +
  xlim(-0.15, 0.15)

# A1 -
