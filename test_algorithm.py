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
  print u1[0]
  print u2[0]
  assert u1[0] >= u2[0] # make sense for the first person to score little higher
  assert abs(u1[0] - u2[0]) < 50 # but not too much

def test_convergence():
  '''
  Have the same user and problem win and lose over and over again, 
  and they should "converge" or ocillate around the same value.
  '''
  user = users[0]
  problem = problems[0]
  for i in xrange(15):
    user, problem = adjust_distribution(user, problem, True)
    user, problem = adjust_distribution(user, problem, False)
  user1, problem1 = adjust_distribution(user, problem, True)
  user2, problem2 = adjust_distribution(user1, problem1, False)
  print user, user1, user2
  print problem, problem1, problem2
  assert abs(user[0] - user2[0]) < 10
  assert abs(user1[0] - user2[0]) < 50
  assert abs(problem[0] - problem2[0]) < 10
  assert abs(problem1[0] - problem2[0]) < 50

if __name__ == '__main__':
  test_noninformative_presequence()
  test_convergence()
