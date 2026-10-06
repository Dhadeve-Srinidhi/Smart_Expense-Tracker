
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("sqlite:///expenses.db")

Base = declarative_base()


# =========================================================
# USER
# =========================================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    username = Column(
        String,
        unique=True,
        nullable=False
    )

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )


# =========================================================
# EXPENSE
# =========================================================

class Expense(Base):

    __tablename__ = "expenses"

    id = Column(
        Integer,
        primary_key=True
    )

    date = Column(
        Date
    )

    category = Column(
        String
    )

    description = Column(
        String
    )

    amount = Column(
        Float
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )


# =========================================================
# SAVINGS GOAL
# =========================================================

class SavingsGoal(Base):

    __tablename__ = "savings_goals"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String,
        nullable=False
    )

    target_amount = Column(
        Float,
        nullable=False
    )

    saved_amount = Column(
        Float,
        default=0.0
    )

    target_date = Column(
        Date
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )


# =========================================================
# BUDGET
# =========================================================

class Budget(Base):

    __tablename__ = "budgets"

    id = Column(
        Integer,
        primary_key=True
    )

    month = Column(
        Integer,
        nullable=False
    )

    year = Column(
        Integer,
        nullable=False
    )

    amount = Column(
        Float,
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )


# =========================================================
# CREATE TABLES
# =========================================================

Base.metadata.create_all(
    engine
)


# =========================================================
# DATABASE SESSION
# =========================================================

Session = sessionmaker(
    bind=engine
)

session = Session()