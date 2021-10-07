import sqlalchemy
from psycopg2 import OperationalError
from config import sql_name

engine = sqlalchemy.create_engine(sql_name)
engine
connection = engine.connect()

class sql:

    def create_table(self):
        connection.execute("""CREATE TABLE IF NOT EXISTS USER_(
                Id INTEGER NOT NULL UNIQUE,
                LastName VARCHAR(60) NOT NULL,
                FirstName VARCHAR(60) NOT NULL,
                Age INTEGER NOT NULL,
                Sex INTEGER NOT NULL,
                City_id INTEGER NOT NULL,
                City VARCHAR(60) NOT NULL
            ); """)

        connection.execute("""CREATE TABLE IF NOT EXISTS VARIANT(
                Id INTEGER NOT NULL UNIQUE,
                LastName VARCHAR(60) NOT NULL,
                FirstName VARCHAR(60) NOT NULL,
                PersonUrl VARCHAR(60) NOT NULL,
                Age INTEGER NOT NULL,
                Sex INTEGER NOT NULL,
                City_id INTEGER NOT NULL,
                City VARCHAR(60) NOT NULL,
                Relation INTEGER NOT NULL,
                User_id INTEGER references user_(Id) NOT NULL
            ); """)

        connection.execute("""CREATE TABLE IF NOT EXISTS PHOTOS(
                PhotosUrl TEXT NOT null,
                Likes INTEGER NOT NULL,
                Var_id INTEGER references VARIANT(Id) NOT NULL,
                Id SERIAL PRIMARY KEY
            ); """)

    def insert_user(self, table_name, value_insert):
        connection.execute(f"""insert into {table_name} values({value_insert}); """)

    def get_city_(self):
        citi_id_bd = connection.execute(f"""select city_id from user_ where city_id = 0; """).fetchone()
        return citi_id_bd

    def get_age_(self):
        age_bd = connection.execute(f"""select age from user_ where age = 0; """).fetchone()
        return age_bd

    def update_user(self, city_i, city_t):
        connection.execute(f"""UPDATE user_ SET City_id = {city_i}, City = {f"'{city_t}'"}; """)

    def update_user_a(self, age_):
        connection.execute(f"""UPDATE user_ SET age = {age_}; """)

    def user(self):
        user_data = connection.execute(f"""select * from user_; """).fetchone()
        return user_data

    def itog_msg(self):
        mes = ''
        count_v = len(connection.execute(f"""select Id from variant  """).fetchall())
        for i in range(1, (count_v+1 if count_v <= 3 else 4)):
            v = connection.execute(f"""select Id, LastName , FirstName, PersonUrl, Age, City 
                    from variant limit 1 OFFSET {i-1} """).fetchall()
            p = connection.execute(f"""select PhotosUrl from photos p
                    where var_id =(select Id from variant LIMIT 1  OFFSET {i-1} ) """).fetchall()
            m = f'{v[0][1]} {v[0][2]}  {v[0][3]}\n' \
                f'Возраст: {v[0][4]}\n' \
                f'Cамые попумярные фото {p[0] if len(p)>=1 else ""} \n ' \
                f'        {p[1]  if len(p)>=2 else ""} \n ' \
                f'        {p[2]  if len(p)>=3 else ""} \n '
            mes = mes + f'{m}\n'
        return(mes)

    def clean_table(self):
        connection.execute(f"""delete from photos; """)
        connection.execute(f"""delete from variant; """)
        connection.execute(f"""delete from user_; """)
