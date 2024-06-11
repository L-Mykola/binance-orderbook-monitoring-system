import mysql.connector


def create_database(conn, database_name):
    with mysql.connector.connect(**conn) as mydb:
        my_cursor = mydb.cursor()
        my_cursor.execute(f"CREATE DATABASE {database_name}")


def create_table(conn, database_name, table_name):
    with mysql.connector.connect(database=database_name, **conn) as mydb:
        my_cursor = mydb.cursor()
        my_cursor.execute(f'''CREATE TABLE {table_name} 
        (id INT AUTO_INCREMENT PRIMARY KEY, 
        coin_name VARCHAR(255) NOT NULL, 
        avg_price DECIMAL(20, 10) NOT NULL, 
        volumes_plus DECIMAL(20, 10) NOT NULL, 
        volumes_minus DECIMAL(20, 10) NOT NULL, 
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')


def insert_into_table(conn, database_name, table_name, val):
    try:
        with mysql.connector.connect(database=database_name, **conn) as mydb:
            my_cursor = mydb.cursor()
            sql = f"INSERT INTO {table_name} (coin_name, avg_price, volumes_plus, volumes_minus) VALUES (%s, %s, %s, %s)"
            my_cursor.execute(sql, val)

            mydb.commit()
    except mysql.connector.Error as err:
        if err.errno == 1146:
            create_table(conn, database_name, table_name)
            insert_into_table(conn, database_name, table_name)
        elif err.errno == 1049:
            create_database(conn, database_name)
            create_table(conn, database_name, table_name)
            insert_into_table(conn, database_name, table_name)
        else:
            raise


def get_values(conn, database_name, table_name, intrvl):
    with mysql.connector.connect(database=database_name, **conn) as mydb:
        my_cursor = mydb.cursor()
        my_cursor.execute(f'''SELECT volumes_plus, volumes_minus, date 
        FROM {table_name} 
        where date >= DATE_SUB(NOW(), INTERVAL {intrvl} MINUTE)
        ORDER BY date DESC''')

        values = my_cursor.fetchall()
        return values


