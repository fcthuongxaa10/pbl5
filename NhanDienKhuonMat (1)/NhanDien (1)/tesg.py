import pymysql

connectionn = pymysql.connect(host='localhost',
                              user='root',
                              password='',
                              db='pbl5_ktmt',
                              )
id = str("1")
conn=connectionn
cursor = conn.cursor()
cursor.execute("select * from people")
cursor.execute("SELECT * FROM people WHERE id_tv=" + id)
for row in cursor:
 ad = row[1]
print(ad)
conn.commit()
conn.close()

