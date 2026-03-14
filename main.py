import logging
from app.bot.container import Container
from app.bot.manager import BotManager

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


def main():
    container = Container()
    bot = BotManager(container)
    logger.info("Bot iniciado.")
    bot.run()


if __name__ == "__main__":
    main()
