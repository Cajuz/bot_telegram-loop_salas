import logging
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters,
)
from app.bot.container import Container
from app.config.settings import settings

logger = logging.getLogger(__name__)


class BotManager:
    def __init__(self, container: Container):
        self._c = container
        self._app = (
            Application.builder()
            .token(settings.TELEGRAM_TOKEN)
            .build()
        )
        self._register_handlers()

    def _register_handlers(self):
        app = self._app
        uc = self._c.user_commands
        ac = self._c.admin_commands
        kh = self._c.key_handler
        ph = self._c.payment_handler
        rh = self._c.room_handler

        app.add_handler(CommandHandler("start", uc.start))
        app.add_handler(CommandHandler("menu", uc.menu))
        app.add_handler(CommandHandler("criar", uc.criar))
        app.add_handler(CommandHandler("historico", uc.historico))
        app.add_handler(CommandHandler("comprar", uc.comprar))
        app.add_handler(CommandHandler("ajuda", uc.ajuda))
        app.add_handler(CommandHandler("suporte", uc.suporte))

        app.add_handler(CommandHandler("gerarkey", ac.gerar_key))
        app.add_handler(CommandHandler("darkey", ac.dar_key))
        app.add_handler(CommandHandler("listarkeys", ac.listar_keys))
        app.add_handler(CommandHandler("analytics", ac.analytics))
        app.add_handler(CommandHandler("broadcast", ac.broadcast))
        app.add_handler(CommandHandler("blacklist", ac.blacklist))
        app.add_handler(CommandHandler("rankadm", ac.rankadm))
        app.add_handler(CommandHandler("deletekeys", ac.delete_keys))

        app.add_handler(ConversationHandler(
            entry_points=[
                CommandHandler("ativar", kh.iniciar),
                CallbackQueryHandler(kh.iniciar, pattern="^menu:ativar$"),
            ],
            states={
                kh.AGUARDANDO_KEY: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, kh.receber_key)
                ],
            },
            fallbacks=[CommandHandler("cancelar", kh.cancelar)],
            per_message=False,
        ))

        app.add_handler(ConversationHandler(
            entry_points=[
                CallbackQueryHandler(ph.iniciar, pattern="^pay:comprar$"),
            ],
            states={
                1: [CallbackQueryHandler(ph.selecionar_qtd, pattern="^pay:qtd:")],
                2: [MessageHandler(filters.TEXT & ~filters.COMMAND, ph.receber_cpf)],
            },
            fallbacks=[CommandHandler("cancelar", ph.cancelar)],
            per_message=False,
        ))

        app.add_handler(CallbackQueryHandler(rh.handle, pattern="^room:"))
        app.add_handler(CallbackQueryHandler(uc.handle_menu_callback, pattern="^menu:"))

        logger.info("Handlers registrados.")

    def run(self):
        logger.info("Iniciando polling...")
        self._app.run_polling(drop_pending_updates=True)
