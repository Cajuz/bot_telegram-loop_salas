from app.database.engine import AsyncSessionLocal
from app.api_clients.freefire_client import FreeFireClient
from app.payments.wallet_client import WalletClient
from app.repositories.key_repository import KeyRepository
from app.repositories.user_repository import UserRepository
from app.repositories.room_repository import RoomRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.blacklist_repository import BlacklistRepository
from app.services.room_service import RoomService
from app.services.key_service import KeyService
from app.services.payment_service import PaymentService
from app.services.user_service import UserService
from app.services.admin_service import AdminService
from app.services.analytics_service import AnalyticsService
from app.utils.rate_limiter import RateLimiter
from app.commands.user_commands import UserCommands
from app.commands.admin_commands import AdminCommands
from app.handlers.key_handler import KeyHandler
from app.handlers.payment_handler import PaymentHandler
from app.handlers.room_handler import RoomHandler


def _make_session():
    return AsyncSessionLocal()


class Container:
    def __init__(self):
        # API Clients
        self.ff_client = FreeFireClient()
        self.wallet_client = WalletClient()

        # Rate Limiter
        self.rate_limiter = RateLimiter()

        # Session
        self._session = _make_session()

        # Repositories
        self.key_repo = KeyRepository(self._session)
        self.user_repo = UserRepository(self._session)
        self.room_repo = RoomRepository(self._session)
        self.payment_repo = PaymentRepository(self._session)
        self.blacklist_repo = BlacklistRepository(self._session)

        # Services
        self.room_service = RoomService(self.ff_client, self.key_repo, self.room_repo)
        self.key_service = KeyService(self.key_repo, self.blacklist_repo)
        self.payment_service = PaymentService(
            self.wallet_client, self.payment_repo, self.key_repo
        )
        self.user_service = UserService(self.user_repo)
        self.admin_service = AdminService(
            self.key_repo, self.blacklist_repo, self.room_repo
        )
        self.analytics_service = AnalyticsService(self.room_repo)

        # Commands & Handlers  ← isso estava faltando
        self.user_commands = UserCommands(self)
        self.admin_commands = AdminCommands(self)
        self.key_handler = KeyHandler(self)
        self.payment_handler = PaymentHandler(self)
        self.room_handler = RoomHandler(self)
