pd_decision_distributions_by_score = {
    10: (["Cooperate"] * 88) + (["Defect"] * 12),
    9: (["Cooperate"] * 73) + (["Defect"] * 27),
    8: (["Cooperate"] * 69) + (["Defect"] * 31),
    7: (["Cooperate"] * 71) + (["Defect"] * 29),
    6: (["Cooperate"] * 62) + (["Defect"] * 38),
    5: (["Cooperate"] * 67) + (["Defect"] * 33),
    4: (["Cooperate"] * 63) + (["Defect"] * 37),
    3: (["Cooperate"] * 53) + (["Defect"] * 47),
    2: (["Cooperate"] * 41) + (["Defect"] * 59),
    1: (["Cooperate"] * 32) + (["Defect"] * 68),
    0: (["Cooperate"] * 30) + (["Defect"] * 70),
    None: (["Cooperate"] * 77) + (["Defect"] * 23),
}

pd_scoring_distributions_by_payoff_result = {
    6: ([0] * 7)
    + ([1] * 2)
    + ([2] * 3)
    + ([3] * 3)
    + ([4] * 3)
    + ([5] * 17)
    + ([6] * 8)
    + ([7] * 9)
    + ([8] * 13)
    + ([9] * 12)
    + ([10] * 24),
    5: ([0] * 1)
    + ([1] * 2)
    + ([2] * 2)
    + ([3] * 2)
    + ([4] * 2)
    + ([5] * 8)
    + ([6] * 3)
    + ([7] * 5)
    + ([8] * 7)
    + ([9] * 10)
    + ([10] * 54),
    2: ([0] * 18)
    + ([1] * 5)
    + ([2] * 6)
    + ([3] * 5)
    + ([4] * 4)
    + ([5] * 2)
    + ([6] * 4)
    + ([7] * 7)
    + ([8] * 8)
    + ([9] * 8)
    + ([10] * 20),
    0: ([0] * 25)
    + ([1] * 5)
    + ([2] * 5)
    + ([3] * 5)
    + ([4] * 3)
    + ([5] * 9)
    + ([6] * 4)
    + ([7] * 6)
    + ([8] * 9)
    + ([9] * 7)
    + ([10] * 22),
}

gossip_value_distribution_by_gossip_value = {
    10: ([True] * 26) + ([False] * 74),
    9: ([True] * 17) + ([False] * 83),
    8: ([True] * 16) + ([False] * 84),
    7: ([True] * 16) + ([False] * 84),
    6: ([True] * 12) + ([False] * 88),
    5: ([True] * 6) + ([False] * 94),
    4: ([True] * 13) + ([False] * 87),
    3: ([True] * 19) + ([False] * 81),
    2: ([True] * 19) + ([False] * 81),
    1: ([True] * 22) + ([False] * 78),
    0: ([True] * 33) + ([False] * 67),
    None: ([False]) * 2,
}

gossip_decision_distribution_by_neighbour_score = {
    10: ([True] * 59) + ([False] * 41),
    9: ([True] * 42) + ([False] * 58),
    8: ([True] * 53) + ([False] * 47),
    7: ([True] * 50) + ([False] * 50),
    6: ([True] * 38) + ([False] * 62),
    5: ([True] * 26) + ([False] * 74),
    4: ([True] * 38) + ([False] * 62),
    3: ([True] * 44) + ([False] * 56),
    2: ([True] * 41) + ([False] * 59),
    1: ([True] * 62) + ([False] * 38),
    0: ([True] * 51) + ([False] * 49),
    None: ([True] * 51) + ([False] * 49),
}

update_decision_distribution_by_gossip_value = {
    10: ([True] * 23) + ([False] * 77),
    9: ([True] * 14) + ([False] * 86),
    8: ([True] * 17) + ([False] * 83),
    7: ([True] * 15) + ([False] * 85),
    6: ([True] * 13) + ([False] * 87),
    5: ([True] * 14) + ([False] * 86),
    4: ([True] * 12) + ([False] * 88),
    3: ([True] * 17) + ([False] * 83),
    2: ([True] * 17) + ([False] * 83),
    1: ([True] * 16) + ([False] * 84),
    0: ([True] * 19) + ([False] * 81),
}

update_decision_distribution_by_neighbour_score = {
    10: ([True] * 13) + ([False] * 87),
    9: ([True] * 41) + ([False] * 59),
    8: ([True] * 28) + ([False] * 72),
    7: ([True] * 40) + ([False] * 60),
    6: ([True] * 33) + ([False] * 67),
    5: ([True] * 15) + ([False] * 85),
    4: ([True] * 9) + ([False] * 91),
    3: ([True] * 27) + ([False] * 73),
    2: ([True] * 11) + ([False] * 89),
    1: ([True] * 18) + ([False] * 82),
    0: ([True] * 10) + ([False] * 90),
    None: ([True] * 20) + ([False] * 80),
}

gossip_value_distribution_neighbour_score_none = {
    10: ([True] * 34) + ([False] * 66),
    9: ([True] * 24) + ([False] * 76),
    8: ([True] * 17) + ([False] * 83),
    7: ([True] * 22) + ([False] * 78),
    6: ([True] * 10) + ([False] * 90),
    5: ([True] * 5) + ([False] * 95),
    4: ([True] * 13) + ([False] * 87),
    3: ([True] * 28) + ([False] * 72),
    2: ([True] * 17) + ([False] * 83),
    1: ([True] * 26) + ([False] * 74),
    0: ([True] * 38) + ([False] * 62),
}

gossip_value_distribution_neighbour_score_0 = {
    10: ([True] * 19) + ([False] * 81),
    9: ([True] * 17) + ([False] * 83),
    8: ([True] * 8) + ([False] * 92),
    7: ([True] * 18) + ([False] * 82),
    6: ([True] * 4) + ([False] * 96),
    5: ([True] * 7) + ([False] * 93),
    4: ([True] * 5) + ([False] * 95),
    3: ([True] * 12) + ([False] * 88),
    2: ([True] * 12) + ([False] * 88),
    1: ([True] * 16) + ([False] * 84),
    0: ([True] * 25) + ([False] * 75),
}

gossip_value_distribution_neighbour_score_1 = {
    10: ([True] * 36) + ([False] * 64),
    9: ([True] * 13) + ([False] * 87),
    8: ([True] * 5) + ([False] * 95),
    7: ([True] * 3) + ([False] * 97),
    6: ([True] * 7) + ([False] * 93),
    5: ([True] * 3) + ([False] * 97),
    4: ([True] * 5) + ([False] * 95),
    3: ([True] * 29) + ([False] * 71),
    2: ([True] * 12) + ([False] * 88),
    1: ([True] * 21) + ([False] * 79),
    0: ([True] * 29) + ([False] * 71),
}

gossip_value_distribution_neighbour_score_2 = {
    10: ([True] * 22) + ([False] * 78),
    9: ([True] * 6) + ([False] * 94),
    8: ([True] * 4) + ([False] * 96),
    7: ([True] * 7) + ([False] * 93),
    6: ([True] * 23) + ([False] * 77),
    5: ([True] * 16) + ([False] * 84),
    4: ([True] * 19) + ([False] * 81),
    3: ([True] * 16) + ([False] * 84),
    2: ([True] * 13) + ([False] * 87),
    1: ([True] * 4) + ([False] * 96),
    0: ([True] * 32) + ([False] * 68),
}

gossip_value_distribution_neighbour_score_3 = {
    10: ([True] * 37) + ([False] * 63),
    9: ([True] * 9) + ([False] * 91),
    8: ([True] * 16) + ([False] * 84),
    7: ([True] * 22) + ([False] * 78),
    6: ([True] * 15) + ([False] * 85),
    5: ([True] * 8) + ([False] * 92),
    4: ([True] * 14) + ([False] * 86),
    3: ([True] * 13) + ([False] * 87),
    2: ([True] * 20) + ([False] * 80),
    1: ([True] * 32) + ([False] * 68),
    0: ([True] * 42) + ([False] * 58),
}

gossip_value_distribution_neighbour_score_4 = {
    10: ([True] * 18) + ([False] * 82),
    9: ([True] * 17) + ([False] * 83),
    8: ([True] * 20) + ([False] * 80),
    7: ([True] * 16) + ([False] * 84),
    6: ([True] * 4) + ([False] * 96),
    5: ([True] * 7) + ([False] * 93),
    4: ([True] * 2) + ([False] * 98),
    3: ([True] * 12) + ([False] * 88),
    2: ([True] * 32) + ([False] * 68),
    1: ([True] * 4) + ([False] * 96),
    0: ([True] * 100) + ([False] * 0),
}

gossip_value_distribution_neighbour_score_5 = {
    10: ([True] * 26) + ([False] * 74),
    9: ([True] * 25) + ([False] * 75),
    8: ([True] * 18) + ([False] * 82),
    7: ([True] * 16) + ([False] * 84),
    6: ([True] * 11) + ([False] * 89),
    5: ([True] * 6) + ([False] * 94),
    4: ([True] * 17) + ([False] * 83),
    3: ([True] * 25) + ([False] * 75),
    2: ([True] * 26) + ([False] * 74),
    1: ([True] * 11) + ([False] * 89),
    0: ([True] * 33) + ([False] * 67),
}

gossip_value_distribution_neighbour_score_6 = {
    10: ([True] * 22) + ([False] * 78),
    9: ([True] * 18) + ([False] * 82),
    8: ([True] * 17) + ([False] * 83),
    7: ([True] * 6) + ([False] * 94),
    6: ([True] * 14) + ([False] * 86),
    5: ([True] * 5) + ([False] * 95),
    4: ([True] * 11) + ([False] * 89),
    3: ([True] * 20) + ([False] * 80),
    2: ([True] * 23) + ([False] * 73),
    1: ([True] * 48) + ([False] * 52),
    0: ([True] * 16) + ([False] * 84),
}

gossip_value_distribution_neighbour_score_7 = {
    10: ([True] * 25) + ([False] * 75),
    9: ([True] * 18) + ([False] * 82),
    8: ([True] * 22) + ([False] * 78),
    7: ([True] * 16) + ([False] * 84),
    6: ([True] * 12) + ([False] * 88),
    5: ([True] * 3) + ([False] * 97),
    4: ([True] * 23) + ([False] * 77),
    3: ([True] * 27) + ([False] * 73),
    2: ([True] * 33) + ([False] * 67),
    1: ([True] * 20) + ([False] * 80),
    0: ([True] * 26) + ([False] * 74),
}

gossip_value_distribution_neighbour_score_8 = {
    10: ([True] * 25) + ([False] * 75),
    9: ([True] * 16) + ([False] * 84),
    8: ([True] * 16) + ([False] * 84),
    7: ([True] * 15) + ([False] * 85),
    6: ([True] * 15) + ([False] * 85),
    5: ([True] * 8) + ([False] * 92),
    4: ([True] * 9) + ([False] * 91),
    3: ([True] * 11) + ([False] * 89),
    2: ([True] * 15) + ([False] * 85),
    1: ([True] * 17) + ([False] * 83),
    0: ([True] * 19) + ([False] * 81),
}

gossip_value_distribution_neighbour_score_9 = {
    10: ([True] * 16) + ([False] * 84),
    9: ([True] * 15) + ([False] * 85),
    8: ([True] * 17) + ([False] * 83),
    7: ([True] * 12) + ([False] * 88),
    6: ([True] * 8) + ([False] * 92),
    5: ([True] * 7) + ([False] * 93),
    4: ([True] * 11) + ([False] * 89),
    3: ([True] * 12) + ([False] * 88),
    2: ([True] * 19) + ([False] * 81),
    1: ([True] * 0) + ([False] * 100),
    0: ([True] * 52) + ([False] * 48),
}

gossip_value_distribution_neighbour_score_10 = {
    10: ([True] * 27) + ([False] * 73),
    9: ([True] * 14) + ([False] * 86),
    8: ([True] * 15) + ([False] * 85),
    7: ([True] * 15) + ([False] * 85),
    6: ([True] * 12) + ([False] * 88),
    5: ([True] * 5) + ([False] * 95),
    4: ([True] * 14) + ([False] * 86),
    3: ([True] * 18) + ([False] * 82),
    2: ([True] * 20) + ([False] * 80),
    1: ([True] * 26) + ([False] * 74),
    0: ([True] * 36) + ([False] * 64),
}

gossip_value_distribution_by_neighbour_score = {
    10: gossip_value_distribution_neighbour_score_10,
    9: gossip_value_distribution_neighbour_score_9,
    8: gossip_value_distribution_neighbour_score_8,
    7: gossip_value_distribution_neighbour_score_7,
    6: gossip_value_distribution_neighbour_score_6,
    5: gossip_value_distribution_neighbour_score_5,
    4: gossip_value_distribution_neighbour_score_4,
    3: gossip_value_distribution_neighbour_score_3,
    2: gossip_value_distribution_neighbour_score_2,
    1: gossip_value_distribution_neighbour_score_1,
    0: gossip_value_distribution_neighbour_score_0,
    None: gossip_value_distribution_neighbour_score_none,
}

update_value_distribution_neighbour_score_none = {
    10: ([True] * 27) + ([False] * 63),
    9: ([True] * 9) + ([False] * 91),
    8: ([True] * 10) + ([False] * 90),
    7: ([True] * 8) + ([False] * 92),
    6: ([True] * 18) + ([False] * 82),
    5: ([True] * 12) + ([False] * 88),
    4: ([True] * 10) + ([False] * 90),
    3: ([True] * 20) + ([False] * 80),
    2: ([True] * 19) + ([False] * 81),
    1: ([True] * 17) + ([False] * 83),
    0: ([True] * 24) + ([False] * 76),
}

update_value_distribution_neighbour_score_0 = {
    10: ([True] * 10) + ([False] * 90),
    9: ([True] * 8) + ([False] * 92),
    8: ([True] * 7) + ([False] * 93),
    7: ([True] * 5) + ([False] * 95),
    6: ([True] * 0) + ([False] * 100),
    5: ([True] * 13) + ([False] * 87),
    4: ([True] * 14) + ([False] * 86),
    3: ([True] * 16) + ([False] * 84),
    2: ([True] * 14) + ([False] * 86),
    1: ([True] * 14) + ([False] * 86),
    0: ([True] * 8) + ([False] * 92),
}

update_value_distribution_neighbour_score_1 = {
    10: ([True] * 18) + ([False] * 82),
    9: ([True] * 47) + ([False] * 53),
    8: ([True] * 21) + ([False] * 79),
    7: ([True] * 40) + ([False] * 60),
    6: ([True] * 25) + ([False] * 75),
    5: ([True] * 17) + ([False] * 83),
    4: ([True] * 0) + ([False] * 100),
    3: ([True] * 25) + ([False] * 75),
    2: ([True] * 11) + ([False] * 89),
    1: ([True] * 21) + ([False] * 79),
    0: ([True] * 6) + ([False] * 94),
}

update_value_distribution_neighbour_score_2 = {
    10: ([True] * 12) + ([False] * 88),
    9: ([True] * 38) + ([False] * 62),
    8: ([True] * 6) + ([False] * 94),
    7: ([True] * 0) + ([False] * 100),
    6: ([True] * 0) + ([False] * 100),
    5: ([True] * 0) + ([False] * 100),
    4: ([True] * 0) + ([False] * 100),
    3: ([True] * 0) + ([False] * 100),
    2: ([True] * 14) + ([False] * 86),
    1: ([True] * 0) + ([False] * 100),
    0: ([True] * 10) + ([False] * 90),
}

update_value_distribution_neighbour_score_3 = {
    10: ([True] * 34) + ([False] * 66),
    9: ([True] * 38) + ([False] * 62),
    8: ([True] * 33) + ([False] * 67),
    7: ([True] * 10) + ([False] * 90),
    6: ([True] * 12) + ([False] * 88),
    5: ([True] * 6) + ([False] * 94),
    4: ([True] * 67) + ([False] * 43),
    3: ([True] * 0) + ([False] * 100),
    2: ([True] * 50) + ([False] * 50),
    1: ([True] * 0) + ([False] * 100),
    0: ([True] * 24) + ([False] * 76),
}

update_value_distribution_neighbour_score_4 = {
    10: ([True] * 10) + ([False] * 90),
    9: ([True] * 12) + ([False] * 88),
    8: ([True] * 0) + ([False] * 100),
    7: ([True] * 0) + ([False] * 100),
    6: ([True] * 0) + ([False] * 100),
    5: ([True] * 14) + ([False] * 86),
    4: ([True] * 100) + ([False] * 0),
    3: ([True] * 0) + ([False] * 100),
    2: ([True] * 0) + ([False] * 100),
    1: ([True] * 0) + ([False] * 100),
    0: ([True] * 10) + ([False] * 90),
}

update_value_distribution_neighbour_score_5 = {
    10: ([True] * 13) + ([False] * 87),
    9: ([True] * 17) + ([False] * 83),
    8: ([True] * 19) + ([False] * 81),
    7: ([True] * 14) + ([False] * 86),
    6: ([True] * 12) + ([False] * 88),
    5: ([True] * 15) + ([False] * 85),
    4: ([True] * 12) + ([False] * 88),
    3: ([True] * 10) + ([False] * 90),
    2: ([True] * 11) + ([False] * 89),
    1: ([True] * 8) + ([False] * 82),
    0: ([True] * 21) + ([False] * 79),
}

update_value_distribution_neighbour_score_6 = {
    10: ([True] * 36) + ([False] * 64),
    9: ([True] * 16) + ([False] * 84),
    8: ([True] * 25) + ([False] * 75),
    7: ([True] * 17) + ([False] * 83),
    6: ([True] * 0) + ([False] * 100),
    5: ([True] * 0) + ([False] * 100),
    4: ([True] * 33) + ([False] * 67),
    3: ([True] * 0) + ([False] * 100),
    2: ([True] * 0) + ([False] * 100),
    1: ([True] * 38) + ([False] * 62),
    0: ([True] * 44) + ([False] * 56),
}

update_value_distribution_neighbour_score_7 = {
    10: ([True] * 39) + ([False] * 61),
    9: ([True] * 50) + ([False] * 50),
    8: ([True] * 24) + ([False] * 76),
    7: ([True] * 58) + ([False] * 42),
    6: ([True] * 50) + ([False] * 50),
    5: ([True] * 52) + ([False] * 48),
    4: ([True] * 50) + ([False] * 50),
    3: ([True] * 50) + ([False] * 50),
    2: ([True] * 8) + ([False] * 92),
    1: ([True] * 25) + ([False] * 75),
    0: ([True] * 41) + ([False] * 59),
}

update_value_distribution_neighbour_score_8 = {
    10: ([True] * 32) + ([False] * 68),
    9: ([True] * 20) + ([False] * 80),
    8: ([True] * 40) + ([False] * 60),
    7: ([True] * 29) + ([False] * 71),
    6: ([True] * 36) + ([False] * 64),
    5: ([True] * 18) + ([False] * 82),
    4: ([True] * 20) + ([False] * 80),
    3: ([True] * 29) + ([False] * 71),
    2: ([True] * 40) + ([False] * 60),
    1: ([True] * 23) + ([False] * 77),
    0: ([True] * 21) + ([False] * 79),
}

update_value_distribution_neighbour_score_9 = {
    10: ([True] * 44) + ([False] * 56),
    9: ([True] * 32) + ([False] * 68),
    8: ([True] * 53) + ([False] * 47),
    7: ([True] * 36) + ([False] * 64),
    6: ([True] * 10) + ([False] * 90),
    5: ([True] * 33) + ([False] * 67),
    4: ([True] * 17) + ([False] * 83),
    3: ([True] * 44) + ([False] * 56),
    2: ([True] * 50) + ([False] * 50),
    1: ([True] * 31) + ([False] * 69),
    0: ([True] * 41) + ([False] * 59),
}

update_value_distribution_neighbour_score_10 = {
    10: ([True] * 17) + ([False] * 83),
    9: ([True] * 6) + ([False] * 94),
    8: ([True] * 12) + ([False] * 88),
    7: ([True] * 13) + ([False] * 87),
    6: ([True] * 8) + ([False] * 92),
    5: ([True] * 6) + ([False] * 94),
    4: ([True] * 3) + ([False] * 97),
    3: ([True] * 9) + ([False] * 91),
    2: ([True] * 19) + ([False] * 81),
    1: ([True] * 16) + ([False] * 84),
    0: ([True] * 12) + ([False] * 88),
}

update_value_distribution_by_neighbour_score = {
    10: update_value_distribution_neighbour_score_10,
    9: update_value_distribution_neighbour_score_9,
    8: update_value_distribution_neighbour_score_8,
    7: update_value_distribution_neighbour_score_7,
    6: update_value_distribution_neighbour_score_6,
    5: update_value_distribution_neighbour_score_5,
    4: update_value_distribution_neighbour_score_4,
    3: update_value_distribution_neighbour_score_3,
    2: update_value_distribution_neighbour_score_2,
    1: update_value_distribution_neighbour_score_1,
    0: update_value_distribution_neighbour_score_0,
    None: update_value_distribution_neighbour_score_none,
}

# a_pd_decision_distributions_by_score = {
#     10: (["Cooperate"]*86) + (["Defect"]*14),
#     9: (["Cooperate"]*73) + (["Defect"]*27),
#     8: (["Cooperate"]*68) + (["Defect"]*32),
#     7: (["Cooperate"]*67) + (["Defect"]*33),
#     6: (["Cooperate"]*54) + (["Defect"]*46),
#     5: (["Cooperate"]*70) + (["Defect"]*30),
#     4: (["Cooperate"]*64) + (["Defect"]*36),
#     3: (["Cooperate"]*47) + (["Defect"]*53),
#     2: (["Cooperate"]*66) + (["Defect"]*34),
#     1: (["Cooperate"]*67) + (["Defect"]*33),
#     0: (["Cooperate"]*69) + (["Defect"]*31),
#     None: (["Cooperate"]*75) + (["Defect"]*25),
# }

# b_pd_decision_distributions_by_score = {
#     10: (["Cooperate"]*82) + (["Defect"]*18),
#     9: (["Cooperate"]*70) + (["Defect"]*30),
#     8: (["Cooperate"]*65) + (["Defect"]*35),
#     7: (["Cooperate"]*69) + (["Defect"]*31),
#     6: (["Cooperate"]*65) + (["Defect"]*35),
#     5: (["Cooperate"]*56) + (["Defect"]*44),
#     4: (["Cooperate"]*63) + (["Defect"]*37),
#     3: (["Cooperate"]*50) + (["Defect"]*50),
#     2: (["Cooperate"]*40) + (["Defect"]*60),
#     1: (["Cooperate"]*35) + (["Defect"]*65),
#     0: (["Cooperate"]*25) + (["Defect"]*75),
#     None: (["Cooperate"]*72) + (["Defect"]*28),
# }

# c_pd_decision_distributions_by_score = {
#     10: (["Cooperate"]*92) + (["Defect"]*8),
#     9: (["Cooperate"]*76) + (["Defect"]*24),
#     8: (["Cooperate"]*73) + (["Defect"]*27),
#     7: (["Cooperate"]*77) + (["Defect"]*23),
#     6: (["Cooperate"]*72) + (["Defect"]*28),
#     5: (["Cooperate"]*74) + (["Defect"]*26),
#     4: (["Cooperate"]*63) + (["Defect"]*37),
#     3: (["Cooperate"]*67) + (["Defect"]*33),
#     2: (["Cooperate"]*52) + (["Defect"]*48),
#     1: (["Cooperate"]*30) + (["Defect"]*70),
#     0: (["Cooperate"]*33) + (["Defect"]*67),
#     None: (["Cooperate"]*83) + (["Defect"]*17),
# }

# gossip_value_distribution_by_neighbour_score = {
#     10: ([0]*20) + ([1]*2) + ([2]*2) + ([3]*1) + ([4]*1) + ([5]*2) + ([6]*1) + ([7]*1) + ([8]*2) + ([9]*4) + ([10]*64),
#     9: ([0]*8) + ([1]*0) + ([2]*2) + ([3]*2) + ([4]*2) + ([5]*6) + ([6]*4) + ([7]*8) + ([8]*17) + ([9]*29) + ([10]*20),
#     8: ([0]*5) + ([1]*2) + ([2]*4) + ([3]*2) + ([4]*1) + ([5]*5) + ([6]*5) + ([7]*12) + ([8]*28) + ([9]*13) + ([10]*23),
#     7: ([0]*8) + ([1]*2) + ([2]*8) + ([3]*8) + ([4]*9) + ([5]*3) + ([6]*4) + ([7]*22) + ([8]*16) + ([9]*11) + ([10]*10),
#     6: ([0]*4) + ([1]*5) + ([2]*3) + ([3]*6) + ([4]*7) + ([5]*5) + ([6]*15) + ([7]*7) + ([8]*22) + ([9]*15) + ([10]*12),
#     5: ([0]*12) + ([1]*1) + ([2]*3) + ([3]*4) + ([4]*3) + ([5]*15) + ([6]*4) + ([7]*5) + ([8]*8) + ([9]*9) + ([10]*37),
#     4: ([0]*3) + ([1]*2) + ([2]*6) + ([3]*5) + ([4]*2) + ([5]*6) + ([6]*2) + ([7]*20) + ([8]*9) + ([9]*10) + ([10]*36),
#     3: ([0]*8) + ([1]*6) + ([2]*2) + ([3]*8) + ([4]*3) + ([5]*4) + ([6]*3) + ([7]*6) + ([8]*10) + ([9]*7) + ([10]*43),
#     2: ([0]*14) + ([1]*1) + ([2]*17) + ([3]*3) + ([4]*6) + ([5]*8) + ([6]*4) + ([7]*2) + ([8]*2) + ([9]*5) + ([10]*38),
#     1: ([0]*7) + ([1]*18) + ([2]*4) + ([3]*4) + ([4]*2) + ([5]*1) + ([6]*2) + ([7]*1) + ([8]*2) + ([9]*10) + ([10]*49),
#     0: ([0]*34) + ([1]*2) + ([2]*2) + ([3]*1) + ([4]*0) + ([5]*4) + ([6]*0) + ([7]*2) + ([8]*2) + ([9]*2) + ([10]*50),
#     None: ([0]*41) + ([1]*2) + ([2]*3) + ([3]*3) + ([4]*1) + ([5]*4) + ([6]*3) + ([7]*5) + ([8]*6) + ([9]*11) + ([10]*45),
# }
