from operator import and_

from sqlalchemy import create_engine, URL, Table, MetaData, insert, Column, Integer

from config import username, password, host, database


class Checker:

    def __init__(self):
        url_object = URL.create(
            "postgresql+psycopg2",
            username=username,
            password=password,
            host=host,
            database=database
        )
        engine = create_engine(url_object)
        self.connection = engine.connect()
        metadata = MetaData()
        self.already_processed = Table('already_processed', metadata,
                                       Column('user_id', Integer()),
                                       Column('profile_id', Integer())
                                       )

    def put_record(self, user_id, profile_id):
        if not self.exist(user_id, profile_id):
            query = insert(self.already_processed).values(user_id=user_id, profile_id=profile_id)
            self.connection.execute(query)
            self.connection.commit()

    def exist(self, user_id, profile_id):
        query = self.already_processed.select().where(and_(self.already_processed.columns.user_id == user_id,
                                                           self.already_processed.columns.profile_id == profile_id))
        output = self.connection.execute(query)
        return output.rowcount > 0

    def print_all(self):
        output = self.connection.execute(self.already_processed.select()).fetchall()
        print(output)


if __name__ == '__main__':
    checker = Checker()
    if checker.exist(100, 101):
        print('exist')
    else:
        print('is not exist')
    if checker.exist(101, 101):
        print('exist')
    else:
        print('is not exist')
    checker.print_all()
