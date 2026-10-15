import getpass
import mysql.connector
from mysql.connector import Error


def main():
    password = getpass.getpass("Enter MySQL root password: ")

    try:
        connection = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password=password,
            database="high_performance_db",
            connection_timeout=10,
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE(), VERSION()")
            database, version = cursor.fetchone()

            print("Connection successful!")
            print(f"Database: {database}")
            print(f"MySQL version: {version}")

            cursor.close()
            connection.close()

    except Error as error:
        print(f"Connection failed: {error}")


if __name__ == "__main__":
    main()
