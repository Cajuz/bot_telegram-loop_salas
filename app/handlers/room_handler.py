from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.bot.container import Container

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from app.config.constants import MODOS
from app.services.room_service import (
    InsufficientBalanceError, RoomLimitError, RoomNotFoundError
)
from app.api_clients.base_client import APIUnavailableError


logger = logging.getLogger(__name__)


class RoomHandler:
    def __init__(self, container: Container):
        self._c = container

    async def handle(self, update: Update, context: CallbackContext):
        query = update.callback_query
        await query.answer()
        parts = query.data.split(":")
        action = parts[1] if len(parts) > 1 else ""
        uid = str(update.effective_user.id)

        if action == "modo":
            await self._criar(query, uid, int(parts[2]))
        elif action == "go":
            await self._go(query, uid, parts[2])
        elif action == "info":
            await self._info(query, uid, parts[2])
        elif action == "fechar":
            self._c.room_service.remover_sala(parts[2])
            await query.edit_message_text("Sala removida da memoria.")

    async def _criar(self, query, uid: str, modo: int):
        modo_info = MODOS.get(modo, {"nome": "Modo " + str(modo), "emoji": "🎮"})
        nome = modo_info["nome"]
        emoji = modo_info["emoji"]
        await query.edit_message_text(emoji + " Criando sala " + nome + "...\nAguarde.")
        try:
            room = await self._c.room_service.criar_sala(uid, modo)
            keyboard = [
                [
                    InlineKeyboardButton("GO!", callback_data="room:go:" + room.sshash),
                    InlineKeyboardButton("Players", callback_data="room:info:" + room.sshash),
                ],
                [InlineKeyboardButton("Fechar", callback_data="room:fechar:" + room.sshash)],
            ]
            texto = (
                "*Sala Criada!*\n\n"
                "ID: `" + room.room_id + "`\n"
                "Senha: `" + room.senha + "`\n"
                "Modo: " + emoji + " " + nome
            )
            await query.edit_message_text(texto, parse_mode="Markdown",
                                          reply_markup=InlineKeyboardMarkup(keyboard))
        except InsufficientBalanceError:
            await query.edit_message_text("Saldo insuficiente. Use /comprar.")
        except RoomLimitError as e:
            await query.edit_message_text(str(e))
        except APIUnavailableError:
            await query.edit_message_text("API indisponivel. Tente novamente.")
        except Exception as e:
            logger.error("[ROOM] erro: " + str(e))
            await query.edit_message_text("Erro ao criar sala. Contate o suporte.")

    async def _go(self, query, uid: str, sshash: str):
        try:
            await self._c.room_service.iniciar_sala(sshash, uid)
            await query.answer("Partida iniciada!", show_alert=True)
        except RoomNotFoundError:
            await query.answer("Sala nao encontrada.", show_alert=True)
        except Exception as e:
            await query.answer("Erro: " + str(e), show_alert=True)

    async def _info(self, query, uid: str, sshash: str):
        try:
            data = await self._c.room_service.info_sala(sshash, uid)
            players = data.get("players", [])
            lista = "\n".join("- " + str(p) for p in players) if players else "Nenhum ainda."
            await query.edit_message_text("*Jogadores na sala:*\n" + lista, parse_mode="Markdown")
        except Exception as e:
            await query.answer("Erro: " + str(e), show_alert=True)
