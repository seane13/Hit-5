# combo_filters.py

def valid_even_odd(combo, even_required=(2, 3)):
    """
    Checks if combo has valid number of even numbers (usually 2 or 3 out of 5).
    Returns True if combo meets the requirement.
    """
    evens = sum(n % 2 == 0 for n in combo)
    return evens in even_required


def has_3_consecutive(combo):
    """
    Checks if combo has any run of 3 consecutive numbers.
    Returns True if such a run exists.
    """
    sorted_combo = sorted(combo)
    for i in range(len(sorted_combo) - 2):
        if sorted_combo[i] + 1 == sorted_combo[i+1] and sorted_combo[i] + 2 == sorted_combo[i+2]:
            return True
    return False


def in_recent_hits(combo, recent_hits):
    """
    Returns True if any number in combo appears in the recent_hits set.
    """
    return any(n in recent_hits for n in combo)


def in_past_draws(combo, draws_set):
    """
    Returns True if combo (sorted) has been drawn before (in draws_set).
    """
    return tuple(sorted(combo)) in draws_set


def in_sum_range(combo, sum_range):
    """
    Returns True if sum(combo) falls within the supplied (min, max) range.
    """
    s = sum(combo)
    return sum_range[0] <= s <= sum_range[1]


def must_include(combo, must_nums):
    """
    Returns True if all numbers in must_nums are present in combo.
    """
    return all(n in combo for n in must_nums)
