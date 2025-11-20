from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database import Base

from sqlalchemy import Enum as PgEnum
import enum

class UserRole(enum.Enum):
    guest = "guest"
    trial = "trial"
    subscriber = "subscriber"
    expired = "expired"
    banned = "banned"
    admin = "admin"

# ==========================
# Users
# ==========================
class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, index=True)          # Telegram ID
    username = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    email = Column(String, nullable=True)

    lang = Column(String(5), default="ru")
    tz = Column(String(64), default="Europe/Berlin")
    role = Column(PgEnum(UserRole, name="user_role"), default=UserRole.guest)
                    # user / admin

    created_at = Column(DateTime, default=datetime.utcnow)

    profile = relationship("Profile", back_populates="user", uselist=False)
    subscriptions = relationship("Subscription", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    user_id = Column(
        BigInteger,
        ForeignKey("users.id"),
        primary_key=True,
    )

    exchange_uids = Column(JSONB, nullable=True)
    api_keys = Column(JSONB, nullable=True)          # хранить зашифрованно в будущем
    notifications = Column(JSONB, nullable=True)
    favorites = Column(JSONB, nullable=True)

    user = relationship("User", back_populates="profile")


# ==========================
# Plans (тарифы)
# ==========================
class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String, unique=True, index=True)   # basic / pro / trial
    name = Column(String)
    months = Column(Integer)                         # 1 / 3 / 0 (trial)
    price_cents = Column(Integer)                    # цена в центах
    trial = Column(Boolean, default=False)

    subscriptions = relationship("Subscription", back_populates="plan")


# ==========================
# Subscriptions
# ==========================
class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE")
    )

    plan_id = Column(
        Integer,
        ForeignKey("plans.id", ondelete="SET NULL")
    )

    status = Column(String(16), default="inactive")   # inactive / trial / active / expired / banned
    start_at = Column(DateTime, nullable=True)
    end_at = Column(DateTime, nullable=True)
    source = Column(String, nullable=True)            # telegram_wallet / manual / promo

    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan", back_populates="subscriptions")


# ==========================
# Payments (для будущих вебхуков)
# ==========================
class Payment(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    amount_cents = Column(Integer, nullable=False)
    currency = Column(String, nullable=False)  # TON / XTR / USD
    provider = Column(String, nullable=False)  # telegram_wallet / stars
    tx_id = Column(String, nullable=False)  # уникальный ID транзакции
    status = Column(String, default="pending")  # pending / success / failed / refunded

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("provider", "tx_id", name="uq_provider_txid"),
    )

    user = relationship("User", backref="payments")

# ==========================
# Signals (главная таблица по ТЗ)
# ==========================
class Signal(Base):
    __tablename__ = "signals"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    market = Column(String)                           # spot / futures
    symbol = Column(String)                           # SOLUSDT
    direction = Column(String)                        # long / short
    tf = Column(String)                               # M15/H1

    entry = Column(JSONB)                             # {"type":"zone","min":152.9,"max":153.4}
    sl = Column(Numeric)                              # стоп-лосс
    tps = Column(JSONB)                               # [155.2,156.0,157.4]

    risk_rr = Column(Numeric, nullable=True)          # R:R ≈ 2.3
    leverage = Column(Integer, nullable=True)         # макс. плечо
    risk_pct = Column(Numeric, nullable=True)         # риск %

    indicators = Column(JSONB, nullable=True)         # все фильтры (VWAP/EMA/RSI/SO/ATR/...)
    comment = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)         # PNG-график

    created_by = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    # admin_id (в будущем FK на users)
    created_at = Column(DateTime, default=datetime.utcnow)

    deliveries = relationship("SignalDelivery", back_populates="signal")


class SignalDelivery(Base):
    __tablename__ = "signal_deliveries"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    signal_id = Column(BigInteger, ForeignKey("signals.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))

    delivered_at = Column(DateTime, nullable=True)
    seen_at = Column(DateTime, nullable=True)

    signal = relationship("Signal", back_populates="deliveries")


# ==========================
# News (для фида новостей)
# ==========================
class News(Base):
    __tablename__ = "news"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)

    source = Column(String)                           # CryptoPanic / Binance RSS
    title = Column(Text)
    url = Column(Text)

    symbols = Column(ARRAY(String), nullable=True)    # ['BTC','ETH']
    tags = Column(ARRAY(String), nullable=True)       # ['macro','defi']

    published_at = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
