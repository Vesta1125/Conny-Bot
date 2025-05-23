import discord
from discord.ext import commands

def setup(bot, record, save_record):

    @bot.command(name="승패추가")
    async def add_result(ctx, result: str, count: int = 1):
        user = str(ctx.author.id)
        if user not in record:
            record[user] = {"승": 0, "패": 0, "티어": "5티어", "등수": len(record) + 1}
        if result == "승":
            record[user]["승"] += count
        elif result == "패":
            record[user]["패"] += count
        else:
            await ctx.send("승 또는 패 중 하나를 입력해주세요.")
            return
        save_record(record)
        await ctx.send(f"{ctx.author.name}님의 기록이 추가되었습니다.")
