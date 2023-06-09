# Import packages
library(ggplot2)
library(tidyverse)
library(ggbeeswarm)
library(foreach)
library(doParallel)
library(glue)

# Setup project parameters and functions
numCores <- detectCores() - 1
registerDoParallel(numCores)

# Prepares the abm output for further analytical processing
prepare_abm_output = function(file_path, group_type) {
  input_df = read.csv(file_path)
  if (any(grepl("gossip", colnames(input_df)))) {
    df = input_df
  } else {
    df = input_df %>% mutate(session_absolute_gossip = NA,
                       network_absolute_gossip = NA,
                       neighbour_absolute_gossip = NA,
                       session_mean_gossip = NA,
                       network_mean_gossip = NA,
                       neighbour_mean_gossip = NA)
  }
  df = df %>%
    mutate(source_file = file_list[i],
           round_number = Step,
           game_type = ifelse(grepl("gossip_mod", source_file),"gossip_mod",str_split(str_sub(source_file[1],0,-5),"_")[[1]][5]),
           treatment_ref = str_split(str_sub(source_file[1],0,-5),"_")[[1]][4],
           network_size = as.numeric(str_split(str_sub(source_file[1],0,-5),"_")[[1]][2]) * 4,
           total_networks = as.numeric(str_split(str_sub(source_file[1],0,-5),"_")[[1]][3]),
           neighbours = ifelse(treatment_ref == "A", 2, 3),
           normalise = case_when(group_type == "session" ~ total_networks * network_size,
                                 group_type == "network" ~ network_size,
                                 group_type == "neighbour" ~ neighbours + 1),
           normalise_change = ifelse(grepl("gossip|gossip_mod", game_type),
                                     normalise * neighbours,
                                     normalise),
           treatment_ref_long = case_when(treatment_ref == "A" ~ "Circle",
                                          treatment_ref == "B" ~ "Transitive",
                                          treatment_ref == "C" ~ "Small World"))
  return(df)
}

# Takes the prepared output and transforms key analytical variables
transform_abm_variables = function(dataframe, group_type) {
  lookup = c(consensus = glue('{group_type}_consensus'),
             consensus_grouped = glue('{group_type}_consensus_grouped'),
             consensus_diff_mean = glue('{group_type}_consensus_diff_mean'),
             consensus_diff_mode = glue('{group_type}_consensus_diff_mode'),
             consensus_grouped_diff_mean = glue('{group_type}_consensus_grouped_diff_mean'),
             consensus_grouped_diff_mode = glue('{group_type}_consensus_grouped_diff_mode'),
             cooperation = glue('{group_type}_absolute_cooperation'),
             interaction = glue('{group_type}_absolute_interaction'),
             gossip = glue('{group_type}_absolute_gossip'),
             mean_gossip = glue('{group_type}_mean_gossip'))
  if (group_type != "session") {
    lookup = c(lookup,
               consensus_in = glue('in_{group_type}_consensus'),
               consensus_out = glue('out_{group_type}_consensus'),
               consensus_diff_mean_in = glue('in_{group_type}_consensus_diff_mean'),
               consensus_diff_mean_out = glue('out_{group_type}_consensus_diff_mean'),
               consensus_diff_mode_in = glue('in_{group_type}_consensus_diff_mode'),
               consensus_diff_mode_out = glue('out_{group_type}_consensus_diff_mode'),
               consensus_grouped_in = glue('in_{group_type}_consensus_grouped'),
               consensus_grouped_out = glue('out_{group_type}_consensus_grouped'),
               consensus_grouped_diff_mean_in = glue('in_{group_type}_consensus_grouped_diff_mean'),
               consensus_grouped_diff_mean_out = glue('out_{group_type}_consensus_grouped_diff_mean'),
               consensus_grouped_diff_mode_in = glue('in_{group_type}_consensus_grouped_diff_mode'),
               consensus_grouped_diff_mode_out = glue('out_{group_type}_consensus_grouped_diff_mode'),
               cooperation_in = glue('in_{group_type}_absolute_cooperation'),
               cooperation_out = glue('out_{group_type}_absolute_cooperation'),
               interaction_in = glue('in_{group_type}_absolute_interaction'),
               interaction_out = glue('out_{group_type}_absolute_interaction')
               )
  }
  df = dataframe %>%
    rename(any_of(lookup)) %>%
    group_by(source_file, round_number) %>%
    summarise(across(starts_with("consensus"), mean),
              across(starts_with("cooperation"), sum),
              across(starts_with("interaction"), sum),
              gossip = ifelse(group_type == "neighbour", sum(gossip / max(normalise_change)), sum(gossip / max(normalise_change)) / max(normalise_change)),
              mean_gossip = mean(mean_gossip, na.rm=TRUE) / max(normalise_change),
              change_count = ifelse(group_type == "neighbour", sum(reputation_change_count), sum(reputation_change_count) / max(normalise_change)),
              change_count_grouped = ifelse(group_type == "neighbour", sum(reputation_change_count), sum(reputation_change_count_grouped) / max(normalise_change)),
              payoff_mean = mean(payoff_mean),
              played = mean(agents_played),
              known = mean(agents_known),
              normalise = max(normalise),
              normalise_change = max(normalise_change)
              ) %>%
    mutate(normalised_cooperation = ifelse(group_type == "neighbour", cooperation, cooperation / normalise),
           normalised_interaction = ifelse(group_type == "neighbour", interaction, interaction / normalise),
           cooperation_level = cooperation / interaction,
           # Previous values for convergence testing
           prev_consensus = lag(consensus, 1),
           prev_cooperation_level = lag(cooperation_level, 1),
           prev_change_count = lag(change_count, 1),
           prev_change_count_grouped = lag(change_count_grouped, 1),
           # Convergence variables
           consensus_convergence = (prev_consensus - consensus)^2,
           cooperation_level_convergence = (prev_cooperation_level - cooperation_level)^2,
           change_convergence = (prev_change_count - change_count)^2,
           change_grouped_convergence = (prev_change_count_grouped - change_count_grouped)^2,
           # Metadata from source_file
           game_type = ifelse(grepl("gossip_mod", source_file),"gossip_mod",str_split(str_sub(source_file[1],0,-5),"_")[[1]][5]),
           treatment_ref = str_split(str_sub(source_file[1],0,-5),"_")[[1]][4],
           network_size = as.numeric(str_split(str_sub(source_file[1],0,-5),"_")[[1]][2]) * 4,
           total_networks = as.numeric(str_split(str_sub(source_file[1],0,-5),"_")[[1]][3]),
           neighbours = ifelse(treatment_ref == "A", 2, 3),
           treatment_ref = case_when(treatment_ref == "A" ~ "Circle",
                                     treatment_ref == "B" ~ "Transitive",
                                     treatment_ref == "C" ~ "Small World"),
           treatment_ref = factor(treatment_ref, levels = c("Circle", "Transitive", "Small World")),
           game_type = case_when(game_type == "random" ~ "Random",
                                 game_type == "reputation" ~ "Reputation",
                                 game_type == "gossip" ~ "Gossip",
                                 game_type == "gossip_mod" ~ "Gossip Prefer Self"),
           group = group_type,
           # Set all played / round limit prerequisites
           all_played = ifelse(played == total_networks * network_size - 1, round_number, NA),
           all_known = ifelse(known == total_networks * network_size - 1, round_number, NA),
           all_played_min = min(all_played, na.rm=T),
           all_known_min = min(all_known, na.rm=T)
    ) %>%
    select(-consensus_type)

  if (group_type != "session") {
    df = df %>%
      mutate(consensus_grouped_diff_mean_in_out = consensus_grouped_diff_mean_in - consensus_grouped_diff_mean_out,
             consensus_grouped_diff_mode_in_out = consensus_grouped_diff_mode_in - consensus_grouped_diff_mode_out,
             normalised_cooperation_in = ifelse(group_type == "neighbour", cooperation_in, cooperation_in / normalise),
             normalised_cooperation_out = ifelse(group_type == "neighbour", cooperation_out, cooperation_out / normalise),
             normalised_interaction_in = ifelse(group_type == "neighbour", interaction_in, interaction_in / normalise),
             normalised_interaction_out = ifelse(group_type == "neighbour", interaction_out, interaction_out / normalise),
             cooperation_level_in = cooperation_in / interaction_in,
             cooperation_level_out = cooperation_out / interaction_out,
             )
  }

  return(df)
}

# Get the list of output files from the ABM to read in
# file_list = list.files(pattern = "(result)\\_.*")
#
# # Produces session-level analytical variable outputs
# all_session_df = foreach(i=1:length(file_list), .combine=rbind, .packages=c("dplyr", "stringr", "foreach", "doParallel", "glue")) %dopar% {
#   input_df = prepare_abm_output(file_list[i], "session")
#   output_df = foreach(j= seq(min(input_df$iteration),max(input_df$iteration),1), .combine=rbind, .packages=c("dplyr", "stringr", "glue")) %dopar% {
#     iteration_df = input_df %>%
#       filter(iteration == j)
#     session_df = transform_abm_variables(iteration_df, "session")
#   }
# }
#
# # Produces network-level analytical variable outputs
# all_network_df = foreach(i=1:length(file_list), .combine=rbind, .packages=c("dplyr", "stringr", "foreach", "doParallel")) %dopar% {
#   input_df = prepare_abm_output(file_list[i], "network")
#   output_df = foreach(j=min(input_df$iteration):max(input_df$iteration), .combine=rbind, .packages=c("dplyr", "foreach", "doParallel")) %dopar% {
#     iteration_df = input_df %>%
#       filter(iteration == j)
#     network_output_df = foreach(k=min(iteration_df$network_id):max(iteration_df$network_id), .combine=rbind, .packages=c("dplyr")) %dopar% {
#       iteration_network_df = iteration_df %>%
#         filter(network_id == k)
#       network_df = transform_abm_variables(iteration_network_df, "network")
#     }
#   }
# }
#
# # # Produces neighbour-level analytical variable outputs
# all_neighbour_df = foreach(i=1:length(file_list), .combine=rbind, .packages=c("dplyr", "stringr", "foreach", "doParallel")) %dopar% {
#   input_df = prepare_abm_output(file_list[i], "neighbour")
#   output_df = foreach(j=min(input_df$iteration):max(input_df$iteration), .combine=rbind, .packages=c("dplyr", "foreach", "doParallel")) %dopar% {
#     iteration_df = input_df %>%
#       filter(iteration == j)
#     neighbour_output_df = foreach(k=min(iteration_df$AgentID):max(iteration_df$AgentID), .combine=rbind, .packages=c("dplyr")) %dopar% {
#       iteration_neighbour_df = iteration_df %>%
#         filter(AgentID == k)
#       neighbour_df = transform_abm_variables(iteration_neighbour_df, "neighbour")
#     }
#   }
# }

# saveRDS(all_session_df, "all_session_df.rds")
# saveRDS(all_network_df, "all_network_df.rds")
# saveRDS(all_neighbour_df, "all_neighbour_df.rds")

all_session_df <- readRDS("all_session_df.rds")
all_network_df <- readRDS("all_network_df.rds")
all_neighbour_df <- readRDS("all_neighbour_df.rds")
all_df <- bind_rows(all_session_df, all_network_df, all_neighbour_df)

all_neighbour_df <- all_neighbour_df %>% distinct()
all_network_df <- all_network_df %>% distinct()
all_session_df <- all_session_df %>% distinct()

all_known_lookup_by_file <- all_session_df %>%
  group_by(source_file) %>%
  summarise(all_known = min(all_known_min, na.rm=T),
            all_played = min(all_played_min, na.rm=T),
            round_limit = ceiling(all_known*2)) %>%
  group_by(source_file) %>%
  summarise(all_known = mean(all_known),
            all_played = mean(all_played),
            round_limit = ceiling(mean(round_limit))) %>%
  mutate(all_known_played_diff = abs(all_known - all_played))

all_known_lookup_by_game_type <- all_session_df %>%
  group_by(source_file, game_type, total_networks, network_size) %>%
  summarise(all_known = min(all_known_min, na.rm=T),
            all_played = min(all_played_min, na.rm=T),
            round_limit = ceiling(all_known*2)) %>%
  group_by(game_type, total_networks, network_size) %>%
  summarise(all_known = mean(all_known),
            all_played = mean(all_played),
            round_limit = ceiling(mean(round_limit))) %>%
  mutate(all_known_played_diff = abs(all_known - all_played))

all_known_lookup_by_size <- all_session_df %>%
  group_by(source_file, total_networks, network_size) %>%
  summarise(all_known = min(all_known_min, na.rm=T),
            all_played = min(all_played_min, na.rm=T),
            round_limit = ceiling(all_known*2)) %>%
  group_by(total_networks, network_size) %>%
  summarise(all_known = mean(all_known),
            all_played = mean(all_played),
            round_limit = ceiling(mean(round_limit))) %>%
  mutate(all_known_played_diff = abs(all_known - all_played))

# Takes the transformed dataset and prepares it for visualisation
prepare_convergence_df = function(dataframe) {
  df <- dataframe %>%
    select(-all_played, -all_known) %>%
    left_join(all_known_lookup_by_game_type, by=c("game_type", "total_networks", "network_size")) %>%
    select(-ends_with(".y")) %>%
    mutate(# Previous values for convergence testing
           prev_consensus_grouped = lag(consensus_grouped, 1),
           prev_consensus_diff_mean = lag(consensus_diff_mean, 1),
           prev_consensus_grouped_diff_mean = lag(consensus_grouped_diff_mean, 1),
           prev_consensus_diff_mode = lag(consensus_diff_mode, 1),
           prev_consensus_grouped_diff_mode = lag(consensus_grouped_diff_mode, 1),
           # Convergence variables
           consensus_grouped_convergence = (prev_consensus_grouped - consensus_grouped)^2,
           consensus_diff_mean_convergence = (prev_consensus_diff_mean - consensus_diff_mean)^2,
           consensus_grouped_diff_mean_convergence = (prev_consensus_grouped_diff_mean - consensus_grouped_diff_mean)^2,
           consensus_diff_mode_convergence = (prev_consensus_diff_mode - consensus_diff_mode)^2,
           consensus_grouped_diff_mode_convergence = (prev_consensus_grouped_diff_mode - consensus_grouped_diff_mode)^2,) %>%
    group_by(game_type, network_size, total_networks, treatment_ref, round_number) %>%
    summarise(
      consensus_convergence = mean(consensus_convergence),
      cooperation_level_convergence = mean(cooperation_level_convergence),
      change_convergence = mean(change_convergence),
      change_grouped_convergence = mean(change_grouped_convergence),
      consensus_grouped_convergence = mean(consensus_grouped_convergence),
      consensus_diff_mean_convergence = mean(consensus_diff_mean_convergence),
      consensus_grouped_diff_mean_convergence = mean(consensus_grouped_diff_mean_convergence),
      consensus_diff_mode_convergence = mean(consensus_diff_mode_convergence),
      consensus_grouped_diff_mode_convergence = mean(consensus_grouped_diff_mode_convergence),
      total_size = network_size * total_networks,
      known = mean(known),
      played = mean(played),
      all_known = mean(all_known),
      all_played = mean(all_played),
    )
}

# Produces session-level Convergence df
convergence_df <- prepare_convergence_df(all_session_df)

# convergence_1 <- ggplot(data = convergence_df, aes(x = round_number)) +
#   geom_line(aes(y = consensus_grouped_diff_mode_convergence, color=treatment_ref), alpha = 0.66) +
#   #geom_smooth(aes(y = consensus_convergence, color=treatment_ref)) +
#   geom_vline(aes(xintercept=all_known), color="red", alpha=0.66) +
#   facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
#   theme_minimal() +
#   labs(x = "Round number",
#        y = "Convergence - Session Mean Reputation Variance",
#        color = "Treatment",
#        caption = "Guide line indicates round at which all agents knew all other agents") +
#   scale_x_continuous(breaks=c(0, 400, 800)) +
#   theme(axis.text.x = element_text(angle = 45))
#
# convergence_1

convergence_2 <- ggplot(data = convergence_df, aes(x = round_number)) +
  geom_line(aes(y = change_convergence, color=treatment_ref), alpha = 0.66) +
  #geom_smooth(aes(y = consensus_convergence, color=treatment_ref)) +
  geom_vline(aes(xintercept=all_known), color="red", alpha=0.66) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(x = "Round number",
       y = "Convergence - Reputation Change Count",
       color = "Treatment",
       caption = "Guide line indicates round at which all agents knew all other agents") +
  scale_x_continuous(breaks=c(0, 400, 800)) +
  theme(axis.text.x = element_text(angle = 45))

convergence_2

convergence_3 <- ggplot(data = convergence_df, aes(x = round_number)) +
  geom_line(aes(y = change_grouped_convergence, color=treatment_ref), alpha = 0.66) +
  #geom_smooth(aes(y = consensus_convergence, color=treatment_ref)) +
  geom_vline(aes(xintercept=all_known), color="red", alpha=0.66) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(x = "Round number",
       y = "Convergence - Reputation Change Count Grouped",
       color = "Treatment",
       caption = "Guide line indicates round at which all agents knew all other agents") +
  scale_x_continuous(breaks=c(0, 400, 800)) +
  theme(axis.text.x = element_text(angle = 45))

convergence_3

range = c(0, 400)
convergence_4 <- ggplot(data = convergence_df, aes(x = round_number)) +
  geom_line(aes(y = change_convergence, color=treatment_ref), alpha = 0.66) +
  #geom_smooth(aes(y = consensus_convergence, color=treatment_ref)) +
  geom_vline(aes(xintercept=all_known), color="red", alpha=0.66) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(x = "Round number",
       y = "Convergence - Reputation Change Count",
       color = "Treatment",
       caption = "Guide line indicates round at which all agents knew all other agents") +
  scale_x_continuous(breaks=range, limits = range) +
  theme(axis.text.x = element_text(angle = 45))

convergence_4

convergence_5 <- ggplot(data = convergence_df, aes(x = round_number)) +
  geom_line(aes(y = change_grouped_convergence, color=treatment_ref), alpha = 0.66) +
  #geom_smooth(aes(y = consensus_convergence, color=treatment_ref)) +
  geom_vline(aes(xintercept=all_known), color="red", alpha=0.66) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(x = "Round number",
       y = "Convergence - Reputation Change Count Grouped",
       color = "Treatment",
       caption = "Guide line indicates round at which all agents knew all other agents") +
  scale_x_continuous(breaks=range, limits = range) +
  theme(axis.text.x = element_text(angle = 45))

convergence_5

# range = c(0, 50)
# convergence_consensus_50 <- ggplot(data = convergence_df, aes(x = round_number)) +
#   geom_line(aes(y = consensus_convergence, color=treatment_ref), alpha = 0.66) +
#   #geom_smooth(aes(y = consensus_convergence, color=treatment_ref)) +
#   #geom_vline(aes(xintercept=all_known), color="red", alpha=0.66) +
#   facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
#   theme_minimal() +
#   labs(x = "Round number",
#        y = "Convergence - Session Mean Reputation Variance",
#        color = "Treatment",
#        caption = "Guide line indicates round at which all agents knew all other agents") +
#   scale_x_continuous(breaks=range, limits = range) +
#   theme(axis.text.x = element_text(angle = 45))
#
# convergence_consensus_50

# Hypotheses
range = c(0, 400)
played_known <- ggplot(data = convergence_df, aes(x = round_number)) +
  geom_line(aes(y=known / (total_networks * network_size - 1), color = treatment_ref), alpha=0.66, linetype = "dashed") +
  geom_line(aes(y=played / (total_networks * network_size - 1), color = treatment_ref), alpha=0.66) +
  geom_vline(aes(xintercept=all_known), color="red", alpha=0.66) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(x = "Round number",
       y = "Proportion of agents known",
       color = "Treatment",
       caption = "Guide line indicates round at which all agents knew all other agents") +
  scale_x_continuous(breaks=range, limits = range) +
  theme(axis.text.x = element_text(angle = 45))

played_known

hypothesis_session_df <- all_session_df %>%
  select(-all_played, -all_known) %>%
  left_join(all_known_lookup_by_size, by=c("total_networks", "network_size")) %>%
  select(-ends_with(".y")) %>%
  filter(game_type == "Gossip") %>%
  group_by(game_type, network_size, total_networks, treatment_ref, round_number) %>%
  summarise(
    consensus = mean(consensus),
    gossip = mean(gossip),
    mean_gossip = mean(mean_gossip),
    h1a = gossip / consensus,
    h1m = mean_gossip / consensus,
    played = mean(played),
    known = mean(known),
    all_played = mean(all_played),
    all_known = mean(all_known),
    round_limit = mean(round_limit)
  ) %>%
  mutate(known_proportion = known / (total_networks * network_size - 1)) %>%
  filter(round_number <= round_limit)


hypothesis_all_df <- all_df %>%
  select(-all_played, -all_known) %>%
  left_join(all_known_lookup_by_game_type, by=c("game_type", "total_networks", "network_size")) %>%
  select(-ends_with(".y")) %>%
  mutate(gossip = ifelse(group == "neighbour", gossip / (neighbours + 1), gossip),
         group = factor(group, levels = c("session", "network", "neighbour"))) %>%
  group_by(game_type, treatment_ref, network_size, total_networks, round_number, group) %>%
  summarise(consensus_diff_mode = mean(consensus_diff_mode, na.rm=T),
            cooperation = mean(cooperation, na.rm=T),
            gossip = mean(gossip, na.rm=T),
            cooperation_level = mean(cooperation_level, na.rm=T),
            round_limit = mean(round_limit),
            ) %>%
  filter(round_number <= round_limit)

in_group_df <- all_df %>%
  select(source_file, game_type, group, treatment_ref, network_size, total_networks, round_number, group, ends_with("in"), -ends_with("min"), known, played, gossip, mean_gossip, neighbours) %>%
  left_join(all_known_lookup_by_game_type, by=c("game_type", "total_networks", "network_size")) %>%
  select(-ends_with(".y")) %>%
  filter(round_number <= round_limit & group != "session") %>%
  mutate(group = paste0('in_',group)) %>%
  rename_all(~ stringr::str_remove(.x, "_in")) %>%
  rename(normalised_interaction = normalisedteraction_in)

out_group_df <- all_df %>%
  select(source_file, game_type, group, treatment_ref, network_size, total_networks, round_number, group, ends_with("out"), -ends_with("in_out"), known, played, gossip, mean_gossip, neighbours) %>%
  left_join(all_known_lookup_by_game_type, by=c("game_type", "total_networks", "network_size")) %>%
  select(-ends_with(".y")) %>%
  filter(round_number <= round_limit & group != "session") %>%
  mutate(group = paste0('out_',group)) %>%
  rename_all(~ stringr::str_remove(.x, "_out"))

group_session_df <- all_session_df %>%
  select(-all_played, -all_known) %>%
  left_join(all_known_lookup_by_game_type, by=c("game_type", "total_networks", "network_size")) %>%
  select(-ends_with(".y"), names(out_group_df)) %>%
  filter(round_number <= round_limit)

group_network_df <- all_network_df %>%
  select(-all_played, -all_known) %>%
  left_join(all_known_lookup_by_game_type, by=c("game_type", "total_networks", "network_size")) %>%
  select(-ends_with(".y"), names(out_group_df)) %>%
  filter(round_number <= round_limit)

group_neighbour_df <- all_neighbour_df %>%
  select(-all_played, -all_known) %>%
  left_join(all_known_lookup_by_game_type, by=c("game_type", "total_networks", "network_size")) %>%
  select(-ends_with(".y"), names(out_group_df)) %>%
  filter(round_number <= round_limit)

hypothesis_group_df <- bind_rows(in_group_df, out_group_df, group_session_df, group_network_df, group_neighbour_df)  %>%
  mutate(
    gossip = ifelse(group %in% c("in_neighbour", "out_neighbour"), gossip / (neighbours + 1), gossip),
    group = factor(group, levels = c("session", "network", "out_network", "in_network", "neighbour", "out_neighbour", "in_neighbour"))) %>%
  group_by(game_type, treatment_ref, network_size, total_networks, round_number, group) %>%
  summarise(consensus = mean(consensus, na.rm=T),
            consensus_grouped = mean(consensus_grouped, na.rm=T),
            consensus_diff_mean = mean(consensus_diff_mean, na.rm=T),
            consensus_diff_mode = mean(consensus_diff_mode, na.rm=T),
            consensus_grouped_diff_mean = mean(consensus_grouped_diff_mean, na.rm=T),
            consensus_grouped_diff_mode = mean(consensus_grouped_diff_mode, na.rm=T),
            cooperation = mean(cooperation, na.rm=T),
            cooperation_level = mean(cooperation_level, na.rm=T),
            gossip = mean(gossip, na.rm=T),
            mean_gossip = mean(mean_gossip, na.rm=T),
            known = mean(known),
            played = mean(played),
  )

max(hypothesis_group_df$gossip, na.rm=T)

hypothesis_group_session_df <- hypothesis_group_df %>%
  filter(game_type == "Gossip")

hypothesis_session_df <- hypothesis_all_df %>%
  filter(game_type == "Gossip")

# H1 - the consensus is positively correlated with the frequency of gossip sharing within the group

h1_fig_df <- hypothesis_group_df %>%
  filter(game_type == "Gossip" )

h1_fig_a_df <- h1_fig_df %>%
  filter(group %in% c("session", "network", "neighbour"))

range = c(0, 800)
h1_fig_a <- ggplot(data = h1_fig_a_df, aes(x = gossip)) +
  geom_point(aes(y = consensus, color = group), alpha = 0.33) +
  #geom_smooth(aes(y = consensus_diff_mode, color = group)) +
  #geom_vline(aes(xintercept=all_known), colour= "red") +
  #geom_vline(aes(xintercept=all_played), colour = "red") +
  facet_wrap(facets = vars(game_type, network_size, total_networks, treatment_ref), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Reputation Variance Within Group",
       x = "Normalised Absolute Gossip Per Agent",
       color = "Treatment") +
  theme(axis.text.x = element_text(angle = 45))

h1_fig_a

h1_fig_bc_df <- h1_fig_df %>%
  filter(!group %in% c("network", "neighbour")) %>%
  mutate(group = recode(group, "in_network" = "network", "in_neighbour" = "neighbour"))%>%
  filter(group %in% c("session", "network", "neighbour"))

unique(h1_fig_bc_df$group)

h1_fig_b <- ggplot(data = h1_fig_bc_df, aes(x = gossip)) +
  geom_point(aes(y = consensus_diff_mean, color = group), alpha = 0.33) +
  #geom_smooth(aes(y = consensus_diff_mode, color = group)) +
  #geom_vline(aes(xintercept=all_known), colour= "red") +
  #geom_vline(aes(xintercept=all_played), colour = "red") +
  facet_wrap(facets = vars(game_type, network_size, total_networks, treatment_ref), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mean",
       x = "Normalised Absolute Gossip Per Agent",
       color = "Treatment") +
  theme(axis.text.x = element_text(angle = 45))

h1_fig_b

h1_fig_c <- ggplot(data = h1_fig_bc_df, aes(x = gossip)) +
  geom_point(aes(y = consensus_diff_mode, color = group), alpha = 0.33) +
  #geom_smooth(aes(y = consensus_diff_mode, color = group)) +
  #geom_vline(aes(xintercept=all_known), colour= "red") +
  #geom_vline(aes(xintercept=all_played), colour = "red") +
  facet_wrap(facets = vars(game_type, network_size, total_networks, treatment_ref), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance Within Group",
       x = "Normalised Absolute Gossip Per Agent",
       color = "Treatment") +
  theme(axis.text.x = element_text(angle = 45))

h1_fig_c

h1_fig_d <- ggplot(data = h1_fig_bc_df, aes(x = gossip / played)) +
  geom_point(aes(y = consensus, color = group), alpha = 0.33) +
  geom_smooth(aes(y = consensus, color = group)) +
  #geom_vline(aes(xintercept=all_known), colour= "red") +
  #geom_vline(aes(xintercept=all_played), colour = "red") +
  facet_wrap(facets = vars(game_type, network_size, total_networks, treatment_ref), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mean",
       x = "Absolute Gossip / Players Known",
       color = "Treatment") +
  theme(axis.text.x = element_text(angle = 45))

h1_fig_d

h1_fig_e <- ggplot(data = h1_fig_bc_df, aes(x = gossip / played)) +
  geom_point(aes(y = consensus_diff_mean, color = group), alpha = 0.33) +
  geom_smooth(aes(y = consensus_diff_mean, color = group)) +
  #geom_vline(aes(xintercept=all_known), colour= "red") +
  #geom_vline(aes(xintercept=all_played), colour = "red") +
  facet_wrap(facets = vars(game_type, network_size, total_networks, treatment_ref), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mode",
       x = "Absolute Gossip / Players Known",
       color = "Treatment") +
  theme(axis.text.x = element_text(angle = 45))

h1_fig_e

h1_fig_f <- ggplot(data = h1_fig_bc_df, aes(x = gossip / played)) +
  geom_point(aes(y = consensus_diff_mode, color = group), alpha = 0.33) +
  geom_smooth(aes(y = consensus_diff_mode, color = group)) +
  #geom_vline(aes(xintercept=all_known), colour= "red") +
  #geom_vline(aes(xintercept=all_played), colour = "red") +
  facet_wrap(facets = vars(game_type, network_size, total_networks, treatment_ref), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mode",
       x = "Absolute Gossip / Players Known",
       color = "Treatment") +
  theme(axis.text.x = element_text(angle = 45))

h1_fig_f

h2_fig_df <- hypothesis_group_df %>%
  filter(group == "session")

h2_fig_a <- ggplot(data=h2_fig_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus, colour = treatment_ref), outlier.alpha = 0.1) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Reputation Variance Within Group",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45)) +
  ylim(0, 20)

h2_fig_a

h2_fig_b <- ggplot(data=h2_fig_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus_diff_mean, colour = treatment_ref), outlier.alpha = 0.1) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mean",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45)) +
  ylim(1.5, 2.3)

h2_fig_b

h2_fig_c <- ggplot(data=h2_fig_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus_diff_mode, colour = treatment_ref), outlier.alpha = 0.1) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mode",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45))

h2_fig_c

h3_df <- hypothesis_group_df %>%
  filter(group %in% c("in_neighbour", "out_neighbour"))

h3_fig_a<- ggplot(data=h3_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus, colour = group), outlier.alpha = 0.1) +
  #geom_boxplot(aes(y=consensus), alpha = 0.01, outlier.alpha = 0) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Reputation Variance Within Group",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45))

h3_fig_a

h3_fig_b <- ggplot(data=h3_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus_diff_mean, colour = group), outlier.alpha = 0.1) +
  #geom_boxplot(aes(y=consensus_diff_mean), alpha = 0.01, outlier.alpha = 0) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mean",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45))

h3_fig_b

h3_fig_c <- ggplot(data=h3_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus_diff_mode, colour = group), outlier.alpha = 0.1) +
  #geom_boxplot(aes(y=consensus_diff_mode), alpha = 0.01, outlier.alpha = 0) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mode",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45))

h3_fig_c

h4_df <- hypothesis_group_df %>%
  filter(group %in% c("in_network", "out_network"))

h4_fig_a<- ggplot(data=h4_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus, colour = group), outlier.alpha = 0.1) +
  #geom_boxplot(aes(y=consensus), alpha = 0.01, outlier.alpha = 0) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Reputation Variance Within Group",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45))

h4_fig_a

h4_fig_b <- ggplot(data=h4_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus_diff_mean, colour = group), outlier.alpha = 0.1) +
  #geom_boxplot(aes(y=consensus_diff_mean), alpha = 0.01, outlier.alpha = 0) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mean",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45))

h4_fig_b

h4_fig_c <- ggplot(data=h4_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus_diff_mode, colour = group), outlier.alpha = 0.1) +
  #geom_boxplot(aes(y=consensus_diff_mode), alpha = 0.01, outlier.alpha = 0) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mode",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45))

h4_fig_c

h3_h4_fig_a <- ggplot(data=h3_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus, colour = group), outlier.alpha = 0.1) +
  #geom_boxplot(aes(y=consensus), alpha = 0.01, outlier.alpha = 0) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Reputation Variance Within Group",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45))

h3_h4_fig_a

h3_h4_fig_b <- ggplot(data=hypothesis_group_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus_diff_mean, colour = group), outlier.alpha = 0.1) +
  #geom_boxplot(aes(y=consensus_diff_mean), alpha = 0.01, outlier.alpha = 0) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mean",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45))

h3_h4_fig_b

h3_h4_fig_c <- ggplot(data=hypothesis_group_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=consensus_diff_mode, colour = group), outlier.alpha = 0.1) +
  #geom_boxplot(aes(y=consensus_diff_mode), alpha = 0.01, outlier.alpha = 0) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Mean Agent Reputation Variance From Group Mode",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45))

h3_h4_fig_c

h5_fig_df = hypothesis_group_df %>%
  filter(as.character(group) %in% c("out_neighbour", "in_neighbour"))

h5_fig <- ggplot(data=h5_fig_df, aes(x=treatment_ref)) +
  #geom_boxplot(aes(y=cooperation_level), alpha = 0.01, outlier.alpha = 0) +
  geom_boxplot(aes(y=cooperation_level, colour = group), alpha = 0.01, outlier.alpha = 0.1) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Absolute Cooperative Interactions\nNormalised by Number of Agents in Group",
       x = "Treatment Ref",
       color = element_blank()) +
  ylim(0.2, 0.6) +
  theme(axis.text.x = element_text(angle = 45))

h5_fig

h6_fig_df = hypothesis_group_df %>%
  filter(as.character(group) %in% c("in_network", "out_network"))

h6_fig <- ggplot(data=h6_fig_df, aes(x=treatment_ref)) +
  #geom_boxplot(aes(y=cooperation_level), alpha = 0.01, outlier.alpha = 0) +
  geom_boxplot(aes(y=cooperation_level, colour = group), alpha = 0.01, outlier.alpha = 0.1) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Absolute Cooperative Interactions\nNormalised by Number of Agents in Group",
       x = "Treatment Ref",
       color = element_blank()) +
  ylim(0.2, 0.6) +
  theme(axis.text.x = element_text(angle = 45))

h6_fig

h5_6_fig_a <- ggplot(data=hypothesis_group_df, aes(x=treatment_ref)) +
  #geom_boxplot(aes(y=cooperation_level), alpha = 0.01, outlier.alpha = 0) +
  geom_boxplot(aes(y=cooperation_level, colour = group), alpha = 0.01, outlier.alpha = 0.1) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Absolute Cooperative Interactions\nNormalised by Agents in Group",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45)) +
  ylim(0.45, 0.6)

h5_6_fig_a

h5_6_fig_b_df <- hypothesis_group_df %>%
  filter(game_type != "Random")

h5_6_fig_b <- ggplot(data=h5_6_fig_b_df, aes(x=treatment_ref)) +
  geom_boxplot(aes(y=cooperation_level), alpha = 0.01, outlier.alpha = 0) +
  geom_boxplot(aes(y=cooperation_level, colour = group), alpha = 0.01, outlier.alpha = 0.1) +
  #geom_smooth(aes(y=cooperation, colour=group)) +
  facet_wrap(facets = vars(game_type, network_size, total_networks), ncol=9) +
  theme_minimal() +
  labs(y = "Absolute Cooperative Interactions\nNormalised by Agents in Group",
       x = "Treatment Ref",
       color = element_blank()) +
  theme(axis.text.x = element_text(angle = 45)) +
  ylim(0.45, 0.6)

h5_6_fig_b
