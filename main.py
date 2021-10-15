from VKbot import Vkinder
from config import token, sql_name
import sqlalchemy
from sql_db import Users, Variants, Photos, create_db


if __name__ == '__main__':
    try:
        Session = create_db(sql_name)
    except sqlalchemy.exc.OperationalError as error_msg:
        print(error_msg)
        Session = False

    vkbot = Vkinder(token=token)
    vkbot.start_bot(Session)