import pymysql
import pymysql.cursors
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

connection = pymysql.connect(host="localhost",
                             port=3306,
                             user="gogogoAquarius",
                             password="chenpengjiayou19",
                             db="gogogoAquarius$db_movies",
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

sql = "SELECT keywords from movie"
insert_sql = "INSERT INTO recommend (movieId, recId) VALUES (%s, %s) "

with connection.cursor() as cursor:
    cursor.execute(sql)
    movies = cursor.fetchall()
    for i, row in enumerate(movies):
        movies[i] = row['keywords']
    movies = TfidfVectorizer().fit_transform(movies)
    sims = cosine_similarity(movies)
    res = []
    for row in sims:
        most_sim = [i[0]+1 for i in sorted(enumerate(row), key=lambda x:x[1], reverse=True)[1:11]]
        res.append(most_sim)
    for index, row in enumerate(res):
        for rec in row:
            cursor.execute(insert_sql%(index+1, rec))
    connection.commit()

connection.close()

