block_weight = {
    1: 0.15,
    2: 0.1,
    3: 0.15,
    4: 0.05,
    5: 0.1,
    6: 0.15,
    7: 0.15,
    8: 0.1,
    9: 0.05
}
choice_score = {
    0: 0,
    1: 0,
    2: 0.33,
    3: 0.66,
    4: 1,
}


def calculate_block_score(choices_count):
    submission_count = 0
    total_score = 0
    for choice in choices_count:
        total_score += choice_score[choice] * choices_count[choice]
        submission_count += choices_count[choice]
    if submission_count != 0:
        return round(total_score / submission_count, 2)
    else:
        return 0


def calculate_total_score(block_score):
    total_score = 0
    for block in block_score:
        total_score += block_score[block] * block_weight[block]
    total_score = 100 * (1 - total_score)
    return round(total_score, 2)


