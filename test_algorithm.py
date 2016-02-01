'''
Unit test for algorithms.

I don't feel like getting python unittest working so f it
'''
from algorithm import simulate_problems, simulate_users, adjust_distribution

users = simulate_users()
problems = simulate_problems()

def test_noninformative_presequence():
  '''
  Solving easier problems prior to solving difficult problems should
  not change the user rating too much
  '''
  u1 = users[0]
  u2 = users[1]
  # user 1 solves all problems, except last one
  for p in problems[:-1]:
    u1, p2 = adjust_distribution(u1, p, True)
  u1, p2 = adjust_distribution(u1, problems[-1], False)
  # user 2 solves some prev problems, except last one
  for p in problems[5:-1]:
    u2, p2 = adjust_distribution(u2, p, True)
  u2, p2 = adjust_distribution(u1, problems[-1], False)
  assert u1[0] > u2[0] # make sense for the first person to score little higher
  assert abs(u1[0] - u2[0]) < 50 # but not too much

if __name__ == '__main__':
  test_noninformative_presequence()
