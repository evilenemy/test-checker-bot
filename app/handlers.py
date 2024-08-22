from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from datetime import datetime

import database.requests as requests

router = Router()


@router.message(CommandStart())
async def start_command(message: Message):
    user = await requests.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await requests.create_user(message.from_user.id)
    await message.reply(
        f"*Salom, *[{message.from_user.full_name}](tg://user?id={message.from_user.id})!\n\n*Botdan foydalanish yo'riqnomasi:* 📝\n*Test tekshirish uchun test kodi va javoblaringizni quyidagi formatda yuboring:*\ntest kodi\*abcd...\n\n1. 15\*abcdef...\n2. 15\*1a2b3c4d...\n\n*Agar test yaratmoqchi bo'lsangiz ushbu formatda xabar yuboring:*\n+test\*abcd+test davom etish vaqti\n\n1. +test\*abcde+2\n2. +test\*1a2b3c4d5e+2",
        parse_mode="markdown",
    )


@router.message()
async def main(message: Message):
    if message.text.startswith("+test"):
        test_params = message.text.replace("+test*", "").split("+")
        try:
            test_params[1] = int(test_params[1])
        except:
            test_params.append(2)
        try:
            test = await requests.create_test(list(test_params[0]), test_params[1])
            if test:
                await message.answer(f"Sizning testingiz muvaffaqiyatli qo'shildi! ✅\n\n*Sizning testingiz kodi:* {test.id}\n*Test tugash vaqti:* {datetime.strptime(str(test.end_time), "%Y-%m-%d %H:%M:%S.%f").strftime("%d.%m.%Y %H:%M")} \({test_params[1]} soat davomida\)", parse_mode="markdown")
        except Exception as e:
            await message.answer("❗️ Test yaratishda xatolik, iltimos tekshirib qayta urinib ko'ring!")
            print(e)

    check_test = message.text.split("*")
    check_test_keys = list(check_test[1])
    user_id = await requests.get_user_by_telegram_id(message.from_user.id)
    test = await requests.get_test(int(check_test[0]))
    try:
        if not datetime.now() > datetime.strptime(test.end_time, "%Y-%m-%d %H:%M:%S.%f"):
            if not await requests.status_user_of_test(test.id, user_id):
                test_keys = test.test_keys.split(",")
                if len(test_keys) != len(check_test_keys):
                    return await message.answer("Sizning test javoblaringiz soni test javoblariga to'g'ri kelmayapti, iltimos tekshirib qayta urinib ko'ring!")
                score = 0
                score_ball = float(100 / len(test_keys))
                for i in range(len(test_keys)):
                    if test_keys[i] == check_test_keys[i]:
                        score += score_ball
                score = round(score, 1)
                try:
                    await requests.create_test_result(user_id, score, test.id)
                    await message.reply(f"Siz muvaffaqiyatli test topshirdingiz ✅\n\nSiz {len(test_keys)} ta savoldan {int(score / score_ball)} tasiga to'g'ri javob berdingiz.\nO'rta foizda: {score}%")
                except Exception as e:
                    await message.answer("Test javoblarini saqlashda xatolik, qayta urinib ko'ring!\n\nAgarda yana shu xato chiqsa, test adminiga murojaat qiling")
                    print(e)
            else:
                await message.answer("Siz avval ushbu testda qatnashgansiz, siz boshqa qatnasha olmaysiz!")
        else:
            await message.answer("Ushbu test topshirish vaqti tugagan!")
    except Exception as e:
        await message.reply("❗️Nimadir xato ketdi, iltimos tekshirib qayta urinib ko'ring")
        print(e)
