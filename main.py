from VKbot import Vkinder
from config import token



if __name__ == '__main__':
    vkbot = Vkinder(token=token)
    vkbot.start_bot()