from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI

from base.config import get_postgres_url
from base.orm import Base
from chats.adapters.orm import ChatORM, MessageORM
from users.adapters.orm import UserORM, AccountORM, TransactionORM

DATABASE_URL = get_postgres_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Инициализация базы данных стандартными данными."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        demo_user = UserORM(email='user@example.com',
                            password='securepassword')
        demo_admin = UserORM(email='admin@example.com',
                             password='secureadminpassword')

        db.add(demo_user)
        db.add(demo_admin)
        db.commit()

        demo_user_account = AccountORM(user_id=demo_user.id)
        demo_admin_account = AccountORM(user_id=demo_admin.id)

        db.add(demo_user_account)
        db.add(demo_admin_account)
        db.commit()

        transaction1 = TransactionORM(amount=100.0, transaction_type=1,
                                      account_id=demo_user_account.id)
        transaction2 = TransactionORM(amount=-50.0, transaction_type=2,
                                      account_id=demo_admin_account.id)
        # TODO типы транзакций
        db.add(transaction1)
        db.add(transaction2)
        db.commit()

        chat = ChatORM(user_id=demo_user.id)
        db.add(chat)
        db.commit()

        message1 = MessageORM(chat_id=chat.id, role="user",
                              content="Привет! Как дела?")
        message2 = MessageORM(chat_id=chat.id, role="admin",
                              content="Здравствуйте! Всё хорошо, спасибо.")

        db.add(message1)
        db.add(message2)
        db.commit()

    finally:
        db.close()


app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()
