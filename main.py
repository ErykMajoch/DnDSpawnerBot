import config
from bot import DnDSpawner

def main():
    bot = DnDSpawner()
    bot.run(token=config.BOT_TOKEN, log_handler=None)

if __name__ == '__main__':
    main()
