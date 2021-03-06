"""The Game of Hog."""

from dice import four_sided, six_sided, make_test_dice
from ucb import main, trace, log_current_line, interact

# TODO remove my debugging
import pdb

GOAL_SCORE = 100 # The goal of Hog is to score 100 points.

#######################
# Phase 1: Simulator #
######################

# Taking turns

def roll_dice(num_rolls, dice=six_sided):
    """Roll DICE for NUM_ROLLS times.  Return either the sum of the outcomes,
    or 1 if a 1 is rolled (Pig out). This calls DICE exactly NUM_ROLLS times.

    num_rolls:  The number of dice rolls that will be made; at least 1.
    dice:       A zero-argument function that returns an integer outcome.
    """
    # These assert statements ensure that num_rolls is a positive integer.
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls > 0, 'Must roll at least once.'

    # could be nicer
    sum = 0
    had_one = False

    while ( num_rolls > 0 ):
        result = dice()
        
        if ( result == 1 ):
            had_one = True 

        else:
            sum = sum + result
 
        num_rolls = num_rolls - 1          
     
    if ( had_one is True ):
        return 1    
    else:
        return sum


def take_turn(num_rolls, opponent_score, dice=six_sided):
    """Simulate a turn rolling NUM_ROLLS dice, which may be 0 (Free bacon).

    num_rolls:       The number of dice rolls that will be made.
    opponent_score:  The total score of the opponent.
    dice:            A function of no args that returns an integer outcome.
    """
    assert type(num_rolls) == int, 'num_rolls must be an integer.'
    assert num_rolls >= 0, 'Cannot roll a negative number of dice.'
    assert num_rolls <= 10, 'Cannot roll more than 10 dice.'
    assert opponent_score < 100, 'The game should be over.'

    if (num_rolls == 0):   
        return get_free_bacon_score(opponent_score)

    return roll_dice(num_rolls, dice)


# Playing a game
def is_multiple_of_seven( a ):
    return a % 7 == 0 


def select_dice(score, opponent_score):
    """Select six-sided dice unless the sum of SCORE and OPPONENT_SCORE is a
    multiple of 7, in which case select four-sided dice (Hog wild).
    """

    if ( is_multiple_of_seven( score + opponent_score )):
        return four_sided

    return six_sided

def other(who):
    """Return the other player, for a player WHO numbered 0 or 1.

    >>> other(0)
    1
    >>> other(1)
    0
    """
    return 1 - who

def is_double_score(a, b):
    """Returns True if one score is double of the other

    >>> is_double_score(1,1)
    False
    >>> is_double_score(1,2)
    True
    >>> is_double_score(50, 20)
    False
    >>> is_double_score(22,11)
    True
    >>> is_double_score(22,0)
    False
    """
  
    # prevent division by zero
    if ( a == 0 or b == 0 ):
        return False
 
    return ( a / b == 2 or a / b == 0.5 )
    

def play(strategy0, strategy1, goal=GOAL_SCORE):
    """Simulate a game and return the final scores of both players, with
    Player 0's score first, and Player 1's score second.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    strategy0:  The strategy function for Player 0, who plays first.
    strategy1:  The strategy function for Player 1, who plays second.
    """

    who = 0  # Which player is about to take a turn, 0 (first) or 1 (second)
    score0, score1 = 0, 0

    while ( score0 < goal and score1 < goal ):
        dice = select_dice( score0, score1 )
        num_rolls = strategy0( score0, score1 )

        score0 = score0 + take_turn( num_rolls, score1, dice ) 

        if ( is_double_score( score0, score1 )):
            score0, score1 = score1, score0

        who = other(who)
        score0, score1 = score1, score0
        strategy0, strategy1 = strategy1, strategy0

    # if current player is "1" we swap a last time to come back
    # where we've started
    if ( who == 1 ):   
        score0, score1 = score1, score0

    return score0, score1  # You may wish to change this line.


def get_free_bacon_score(opponent_score):

    """ Returns the score using of the free bacon rule

    >>> get_free_bacon_score(1)
    2
    >>> get_free_bacon_score(10)
    2
    >>> get_free_bacon_score(17)
    8
    >>> get_free_bacon_score(94)
    10
    """
    assert opponent_score >= 0, 'Opponent score must be positive'
    assert opponent_score < 100, 'Opponent score must be less then 100'

    def get_list_of_single_numbers():    
        """Converts input number to a string which single chars
           are then converted back to integers (func int for
           each char). 
           The iterator returned by "map" is then converted to a list.
        """
        return list(map(int, str(opponent_score)))

    return max(get_list_of_single_numbers()) + 1


#######################
# Phase 2: Strategies #
#######################

# Basic Strategy


def always_roll(n):
    """Return a strategy that always rolls N dice.

    A strategy is a function that takes two total scores as arguments
    (the current player's score, and the opponent's score), and returns a
    number of dice that the current player will roll this turn.

    >>> strategy = always_roll(5)
    >>> strategy(0, 0)
    5
    >>> strategy(99, 99)
    5
    """
    def strategy(score, opponent_score):
        return n
    return strategy

# Experiments

def make_averaged(fn, num_samples=1000):
    """Return a function that returns the average_value of FN when called.

    To implement this function, you will have to use *args syntax, a new Python
    feature introduced in this project.  See the project description.

    >>> dice = make_test_dice(3, 1, 5, 6)
    >>> averaged_dice = make_averaged(dice, 1000)
    >>> averaged_dice()
    3.75
    >>> make_averaged(roll_dice, 1000)(2, dice)
    6.0

    In this last example, two different turn scenarios are averaged.
    - In the first, the player rolls a 3 then a 1, receiving a score of 1.
    - In the other, the player rolls a 5 and 6, scoring 11.
    Thus, the average value is 6.0.
    """
  
    def averaged_result(*args):
        result = 0
        cnt = num_samples

        while cnt > 0:
            result = result + fn(*args)
            cnt = cnt - 1    

        return result / num_samples 

    return averaged_result


def max_scoring_num_rolls(dice=six_sided):
    """Return the number of dice (1 to 10) that gives the highest average turn
    score by calling roll_dice with the provided DICE.  Print all averages as in
    the doctest below.  Assume that dice always returns positive outcomes.

    >>> dice = make_test_dice(3)
    >>> max_scoring_num_rolls(dice)
    1 dice scores 3.0 on average
    2 dice scores 6.0 on average
    3 dice scores 9.0 on average
    4 dice scores 12.0 on average
    5 dice scores 15.0 on average
    6 dice scores 18.0 on average
    7 dice scores 21.0 on average
    8 dice scores 24.0 on average
    9 dice scores 27.0 on average
    10 dice scores 30.0 on average
    10
    """
    "*** YOUR CODE HERE )***"

    max_avg_score = 0
    max_avg_rolls = 0
    current_score = 0

    for current_rolls in range(1,11):
        averaged_roll_dice = make_averaged(roll_dice, 1000)
        current_score = averaged_roll_dice(current_rolls, dice)

        print(str(current_rolls) + ' dice scores ' +  
              str(current_score) + ' on average')

        if ( current_score > max_avg_score ):
            max_avg_score = current_score
            max_avg_rolls = current_rolls

    return max_avg_rolls

def winner(strategy0, strategy1):
    """Return 0 if strategy0 wins against strategy1, and 1 otherwise."""
    score0, score1 = play(strategy0, strategy1)
    if score0 > score1:
        return 0
    else:
        return 1

def average_win_rate(strategy, baseline=always_roll(5)):
    """Return the average win rate (0 to 1) of STRATEGY against BASELINE."""
    win_rate_as_player_0 = 1 - make_averaged(winner)(strategy, baseline)
    win_rate_as_player_1 = make_averaged(winner)(baseline, strategy)
    return (win_rate_as_player_0 + win_rate_as_player_1) / 2 # Average results

def run_experiments():
    """Run a series of strategy experiments and report results."""
    if True: # Change to False when done finding max_scoring_num_rolls
        six_sided_max = max_scoring_num_rolls(six_sided)
        print('Max scoring num rolls for six-sided dice:', six_sided_max)
        four_sided_max = max_scoring_num_rolls(four_sided)
        print('Max scoring num rolls for four-sided dice:', four_sided_max)

    if True: # Change to True to test always_roll(8)
        print('always_roll(8) win rate:', average_win_rate(always_roll(8)))

    if True: # Change to True to test bacon_strategy
        print('bacon_strategy win rate:', average_win_rate(bacon_strategy))

    if True: # Change to True to test swap_strategy
        print('swap_strategy win rate:', average_win_rate(swap_strategy))

    if True: # Change to True to test final_strategy
        print('final_strategy win rate:', average_win_rate(final_strategy))

    "*** You may add additional experiments as you wish ***"

# Strategies

def bacon_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice if that gives at least MARGIN points,
    and rolls NUM_ROLLS otherwise.
    """
    "*** YOUR CODE HERE ***"

    if get_free_bacon_score(opponent_score) >= margin:
        return 0

    return num_rolls 

def swap_strategy(score, opponent_score, margin=8, num_rolls=5):
    """This strategy rolls 0 dice when it would result in a beneficial swap and
    rolls NUM_ROLLS if it would result in a harmful swap. It also rolls
    0 dice if that gives at least MARGIN points and rolls
    NUM_ROLLS otherwise.
    """
    "*** YOUR CODE HERE ***"
    
    def new_score():
        return score + get_free_bacon_score(opponent_score) 

    # benefical swap
    if ( new_score() * 2 == opponent_score ):
        return 0

    # harmful swap
    elif ( new_score() / 2  == opponent_score ):
        return num_rolls

    # explicitly call bacon_strategy with all arguments
    return bacon_strategy(score, opponent_score, margin, num_rolls)


def final_strategy(score, opponent_score, margin=8):
    """Write a brief description of your final strategy.

    Uses swap strategy as base. Mainly changes the num_rolls 
    supplied to swap.

    Exception is the first "if" which detects if using free bacon would
    give a four sided dice to the opponent.

    The average win rate is around 0.58 which is slightly better than the plain swap strategy.
    I didn't hit the 0.59 though :-(
    """
    "*** YOUR CODE HERE ***"

    def cautious_num_rolls():
        conservative_roll = 4
        standard_roll = 5
        progressive_roll = 6

        if ( score <= opponent_score or score < 25 ):
            return progressive_roll

        elif ( score > 85 ):
            return conservative_roll

        return standard_roll

    # translates average scores to required dice roles
    score_diff_to_rolls = { 7: 3,
                            8: 4,
                            9: 5 }

    diff_to_next_multiple_of_seven= get_diff_to_next_multiple_of_seven( score + opponent_score )
    free_bacon_score = get_free_bacon_score( opponent_score )

    # easy one, by applying the free bacon rule, the opponents next round is with a 
    # four sided dice
    if ( diff_to_next_multiple_of_seven == free_bacon_score ):
        return 0       

    elif ( diff_to_next_multiple_of_seven in score_diff_to_rolls):
        return swap_strategy(score, opponent_score, margin,
                             score_diff_to_rolls[ diff_to_next_multiple_of_seven ] )

    elif ( is_multiple_of_seven( score + margin + opponent_score + margin ) ):
        return swap_strategy(score, opponent_score, margin, 3)

    # default strategy
    return swap_strategy(score, opponent_score, margin, cautious_num_rolls())


def get_diff_to_next_multiple_of_seven( number ):
    """Calculates the score difference to the next multiple of seven
    
    >>> get_diff_to_next_multiple_of_seven( 1 )
    6
    >>> get_diff_to_next_multiple_of_seven( 23 )
    5
    """
    assert number >= 0 

    org_number = number

    while not is_multiple_of_seven( number ):
        number = number + 1

    return number - org_number

##########################
# Command Line Interface #
##########################

# Note: Functions in this section do not need to be changed.  They use features
#       of Python not yet covered in the course.


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions.

    This function uses Python syntax/techniques not yet covered in this course.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Play Hog")
    parser.add_argument('--run_experiments', '-r', action='store_true',
                        help='Runs strategy experiments')
    args = parser.parse_args()

    if args.run_experiments:
        run_experiments()
