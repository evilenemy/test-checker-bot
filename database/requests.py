from sqlalchemy import text
from datetime import datetime, timedelta

from database.models import Test, User, TestResult
from database.models import async_session


async def get_user_by_telegram_id(telegram_id: int):
    async with async_session() as session:
        return await session.scalar(
            text(f"SELECT * FROM users WHERE telegram_id={telegram_id}")
        )


async def create_user(telegram_id: int):
    async with async_session() as session:
        session.add(User(telegram_id=telegram_id))
        await session.commit()


async def create_test(keys: list, end_hour: int = 2):
    async with async_session() as session:
        test_keys = ""
        for key in keys:
            test_keys += f"{key}," if keys[-1] != key else key
        end_time = datetime.now() + timedelta(hours=end_hour)
        new_test = Test(test_keys=test_keys, end_time=end_time)
        session.add(new_test)
        await session.commit()
        await session.refresh(new_test)
        return new_test


async def get_test(id: int):
    async with async_session() as session:
        return (
            await session.execute(text(f"SELECT * FROM tests WHERE id = {id}"))
        ).fetchone()


async def create_test_result(user_id: int, result: float, test_id: int):
    async with async_session() as session:
        session.add(TestResult(user_id=user_id, user_score=result, test_id=test_id))
        await session.commit()


async def status_user_of_test(test_id: int, user_id: int):
    async with async_session() as session:
        return (
            False
            if not await session.scalar(
                text(
                    f"SELECT * FROM test_results WHERE test_id = {test_id} AND user_id = {user_id}"
                )
            )
            else True
        )
