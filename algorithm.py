# Each problem difficulty and user rating is represented by a distribution
# on the space [0, ~3000] that has some resemblance to the Elo system
# (and hopefully not diverge too much from it). For simplicity, we assume
# that the distribution is Gaussian, but unlike Elo we assume that both
# the mean and variance are _unknown_.

import matplotlib.pyplot as plt
import scipy.integrate
import scipy.stats
import math
import numpy
import random
import functools

MIN_VAL = -500
MAX_VAL = 3000


def simulate_problems():
  '''Simulate problems. Assume that problems are given an initial range
  of rating, e.g. [0-300], [600-800], [a, b] and that those initial ranges are 
  convertered to a Gaussian
  The ranges given are the ones that is easy to provide by an expert. We'll
  simulate ~10 problems per range.
  '''
  problems = []

  ranges = [(0,300), (300, 600), (600, 800), (800, 1000), (1000, 1200), 
            (1200, 1400), (1400, 1600), (1600, 1800), (1800, 2000)]
  for (a, b) in ranges:
    # Convert to gaussian. STD is chosen so that ~85% of the weight of the
    # distribution lies within [a, b]
    mean = (a + b) / 2
    std = (b - a) / 3
    var = std * std
    problems.append((mean, var),)
  return problems

def simulate_users():
  '''Simulate users. Hardcoded for now.'''
  #new_user_mean = 2000
  new_user_mean = 300
  new_user_var = 500*500
  new_users = [(new_user_mean, new_user_var), 
               (new_user_mean, new_user_var), 
               (new_user_mean, new_user_var)]
  #TODO: add established users?
  return new_users

def get_next_problem(user, problems, user_history=[]):
  '''
  Problem selection algorithm. We want to select problems that:
    1) have not been selected recently (not in user_history)
    2) best fit a user's level
    3) have low-variance if user is high-variance

  user     -- (mean, var) of the user
  problems -- list of (mean, var) of the problems
  history  -- array of problems indicies already displayed
  '''
  n = len(problems)
  i = None
  while i is None or i in user_history:
    i = random.randint(n-1)
  return i


def adjust_distribution(user, problem, solved):
  '''
  Adjust the distribution given the prior user and problem distribtuions,
  given the new outcome of a user-problem match
  '''
  def distr(x, m1, v1, m2, v2, winning):
    '''
    The distribution representing the numerator of
      `p(x | outcome) = (cdf(x, m1, v1) * pdf(x, m2, v2)) / C`
    Where cdf and pdf are the cumulative and probability distribution functions
    of normal distributions with the given mean and variance. The first part
    corresponds to `p(outcome | x, m1, v1)`, which is the probability that the
    user solves (or not solves) the problem. The second part is the prior
    `p(x)`, which we also assumed to be a normal distribution.

    x  -- input to the distribution function
    m1 -- mean of the item NOT to be updated
    v1 -- variance of the item NOT to be updated
    m2 -- prior mean of the item to be updated
    v2 -- prior variance of the item to be updated
    winning -- whether the item "won" against the other item

    Returns a probability mass function over domain [MIN_VAL, MAX_VAL]
    '''
    if winning:
      return scipy.stats.norm.cdf((x-m1)/math.sqrt(v1)) * \
        scipy.stats.norm.pdf((x-m2)/math.sqrt(v2))
    else:
      return (1-scipy.stats.norm.cdf((x-m1)/math.sqrt(v1))) * \
        scipy.stats.norm.pdf((x-m2)/math.sqrt(v2))

  def normal_approx(distr, interval=5):
    '''
    Approximate a given distribution with a normal distribution. Note that
    the input is typically expected to be created with the `distr` function
    above, so the distribution tends to look somewhat log-normal-like (or
    beta like?). This function works best for such input, not tested for
    general use.

    distr    -- unnormalized density function over domain [MIN_VAL, MAX_VAL]
    interval -- how finely to calculate the mean, etc...
    '''
    integral, error = scipy.integrate.quad(distr, MIN_VAL, MAX_VAL)
    distr_moment1 = 0
    distr_moment2 = 0
    distr_mode_val = 0
    distr_mode = 0
    for x in xrange(MIN_VAL, MAX_VAL, interval):
      y = distr(x)
      distr_moment1 += x  * y / integral * interval
      distr_moment2 += (x * x) * y / integral * interval
      if y > distr_mode_val:
        distr_mode_val = y
        distr_mode = x

    new_mean = distr_mode
    distr_moment2_left = 0
    distr_moment2_right = 0
    for x in xrange(MIN_VAL, MAX_VAL, interval):
      y = distr(x)
      if x < distr_mode:
        distr_moment2_left += (x - distr_mode) * (x - distr_mode) * y / integral * interval
      else:
        distr_moment2_right += (x - distr_mode) * (x - distr_mode) * y / integral * interval
    new_variance = 2 * max(distr_moment2_left, distr_moment2_right)
    return (new_mean, new_variance)

  user_mean, user_var = user
  problem_mean, problem_var = problem

  user_fn = functools.partial(distr,
                              m1=problem_mean,
                              v1=problem_var,
                              m2=user_mean,
                              v2=user_var,
                              winning=solved)
  problem_fn = functools.partial(distr,
                                 m1=user_mean,
                                 v1=user_var,
                                 m2=problem_mean,
                                 v2=problem_var,
                                 winning=not solved)

  plt.plot(range(MIN_VAL, MAX_VAL, 10),
           [user_fn(i) for i in xrange(MIN_VAL, MAX_VAL, 10)])
  #plt.show()

  new_user = normal_approx(user_fn)
  new_problem = normal_approx(problem_fn)

  '''
  print 'solved: ', solved
  print 'user: ', user, new_user
  print 'problem: ', problem, new_problem
  '''
  return (new_user, new_problem)

if __name__ == '__main__':
  problems = simulate_problems()
  users = simulate_users()

  #idx = get_next_problem(users[0], problems, [])
  # ASSUME users[0] - problems[0] and users[0] wins
  user = users[0]
  for p in problems[3:-1]:
    user, p2 = adjust_distribution(user, p, True)
  user, p2 = adjust_distribution(user, problems[-1], False)
