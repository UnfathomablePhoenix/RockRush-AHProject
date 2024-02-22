#https://www.bing.com/ck/a?!&&p=9672ed7458f4ce71JmltdHM9MTcwNzc4MjQwMCZpZ3VpZD0yMGZlZmQ0YS1jZjFjLTY1ZDUtMGY2Mi1lZTg3Y2VmYzY0YzImaW5zaWQ9NTQ5MQ&ptn=3&ver=2&hsh=3&fclid=20fefd4a-cf1c-65d5-0f62-ee87cefc64c2&psq=sqlite+fetch+format+&u=a1aHR0cHM6Ly9zdGFja292ZXJmbG93LmNvbS9xdWVzdGlvbnMvNTI4MTUzNzYvaG93LXRvLWZldGNoLWRhdGEtZnJvbS1zcWxpdGUtdXNpbmctcHl0aG9u&ntb=1

import sqlite3
#https://reintech.io/blog/connect-to-database-with-python

def putInDatabase(nameInput,score):
  #connects to, and inputs scores into the database
  conn = sqlite3.connect('score.db')
  cursor = conn.cursor()

  cursor.execute("CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, score INTEGER);")

  #cursor.execute("DELETE FROM scores")

  #cursor.execute("UPDATE `sqlite_sequence` SET `seq` = (SELECT MAX(`id`) FROM 'scores') WHERE `name` = 'scores'")

  cursor.execute("INSERT INTO scores(username,score) VALUES(?,?)",(nameInput, score))
  conn.commit()

  conn.close()

def takeOutDatabase():
  # connects to and reads the scores in the database
  conn = sqlite3.connect('score.db')
  cursor = conn.cursor()
  cursor.execute("CREATE TABLE IF NOT EXISTS scores (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, score INTEGER);")
  cursor = conn.execute("SELECT * FROM scores")
  rows = cursor.fetchall()
  rows = sortScores(rows)
  return(rows)

def sortScores(rows):
  # INSERTION SORT to sort the values into descending scores to return tho the main program. 
  n = len(rows)
  
  if n <= 1:
    return rows
  
  for i in range(1,n):
    value = rows[i]
    index = i
    while index > 0 and value[2] < rows[index - 1][2]:
      rows[index] = rows[index - 1]
      index -= 1
    rows[index] = value
  return rows