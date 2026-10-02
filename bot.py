import os
import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# =========================
# SETTINGS
# =========================

BOT_TOKEN = "8718827494:AAG6DmnQuypW9fyFxfDOwqwg0_AUULFN09E"

CHANNEL_1 = "@idhshbsj"
CHANNEL_2 = "@nxnskskbe"

# আপনার বটের নিজস্ব ভিডিও File ID বসানো হলো
VIDEO_FILE_ID = "BAACAgEAAxkBAAMJar-dWA8z-D_VC0iYAAFwZp0fS9HzAALxCAAC7avoRVJYF7diXIcoPQQ"

DELETE_AFTER_SECONDS = 10 * 60


# =========================
# JOIN BUTTONS
# =========================

def join_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(
                "📢 Join Channel 1",
                url=f"https://t.me/{CHANNEL_1.lstrip('@')}"
            )
        ],
        [
            InlineKeyboardButton(
                "📢 Join Channel 2",
                url=f"https://t.me/{CHANNEL_2.lstrip('@')}"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Verify",
                callback_data="verify"
            )
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = (
        "👋 স্বাগতম!\n\n"
        "ভিডিওটি পেতে প্রথমে নিচের দুইটি চ্যানেলে Join করুন।\n\n"
        "তারপর নিচের ✅ Verify বাটনে চাপুন।"
    )

    await update.message.reply_text(
        text,
        reply_markup=join_keyboard()
    )


# =========================
# GET FILE ID AUTOMATICALLY
# =========================

async def get_video_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file_id = update.message.video.file_id
    print("\n" + "="*40)
    print("🎬 আপনার ভিডিওর File ID:")
    print(file_id)
    print("="*40 + "\n")
    await update.message.reply_text(f"✅ আপনার ভিডিওর File ID পাওয়া গেছে!\n\n`{file_id}`", parse_mode="Markdown")


# =========================
# CHECK MEMBERSHIP
# =========================

async def is_member(bot, channel, user_id):

    try:
        member = await bot.get_chat_member(
            chat_id=channel,
            user_id=user_id
        )

        return member.status in (
            "member",
            "administrator",
            "creator",
        )

    except Exception as e:
        print(f"Membership check error for {channel}: {e}")
        return False


# =========================
# DELETE VIDEO
# =========================

async def delete_video(context: ContextTypes.DEFAULT_TYPE):

    job_data = context.job.data

    chat_id = job_data["chat_id"]
    message_id = job_data["message_id"]

    try:
        await context.bot.delete_message(
            chat_id=chat_id,
            message_id=message_id
        )

        print("ভিডিও ১০ মিনিট পরে মুছে ফেলা হয়েছে।")

    except Exception as e:
        print(f"Delete error: {e}")


# =========================
# VERIFY BUTTON
# =========================

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    channel1_ok = await is_member(
        context.bot,
        CHANNEL_1,
        user_id
    )

    channel2_ok = await is_member(
        context.bot,
        CHANNEL_2,
        user_id
    )

    # -------------------------
    # NOT JOINED
    # -------------------------

    if not channel1_ok or not channel2_ok:

        await query.edit_message_text(
            "❌ Verification failed.\n\n"
            "দয়া করে দুইটি চ্যানেলেই Join করুন।\n"
            "তারপর আবার নিচের Verify বাটনে চাপুন।",
            reply_markup=join_keyboard()
        )

        return

    # -------------------------
    # BOTH JOINED
    # -------------------------

    await query.edit_message_text(
        "✅ Verification successful!\n\n"
        "🎬 ভিডিও পাঠানো হচ্ছে..."
    )

    # Send video
    video_message = await context.bot.send_video(
        chat_id=query.message.chat_id,
        video=VIDEO_FILE_ID,
        caption="🎬 আপনার ভিডিও\n\n⏳ এই ভিডিওটি ১০ মিনিট পরে মুছে যাবে।"
    )

    # Schedule deletion
    context.job_queue.run_once(
        delete_video,
        when=DELETE_AFTER_SECONDS,
        data={
            "chat_id": video_message.chat_id,
            "message_id": video_message.message_id,
        },
        name=f"delete_{video_message.chat_id}_{video_message.message_id}"
    )


# =========================
# MAIN
# =========================

def main():

    if not BOT_TOKEN:
        print("❌ BOT_TOKEN পাওয়া যায়নি।")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, get_video_id))
    app.add_handler(
        CallbackQueryHandler(
            verify,
            pattern="^verify$"
        )
    )

    print("🤖 Bot চলছে...")

    app.run_polling()


if __name__ == "__main__":
    main()
