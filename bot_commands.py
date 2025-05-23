import discord
from discord.ext import commands

def setup(bot, record, save_record):

    def ensure_user(user_id):
        if user_id not in record:
            record[user_id] = {"승": 0, "패": 0, "티어": "5티어", "등수": len(record) + 1}

    @bot.command(name="승패추가")
    async def add_result(ctx, result: str, count: int = 1):
        user = str(ctx.author.id)
        ensure_user(user)

        if result == "승":
            record[user]["승"] += count
        elif result == "패":
            record[user]["패"] += count
        else:
            await ctx.send("승 또는 패 중 하나를 입력해주세요. (!승패추가 승 3)")
            return

        save_record(record)
        await ctx.send(f"{ctx.author.name}님의 기록이 추가되었습니다. (승: {record[user]['승']}, 패: {record[user]['패']})")

    @bot.command(name="전적조회")
    async def view_record(ctx):
        user = str(ctx.author.id)
        if user not in record:
            await ctx.send(f"{ctx.author.name}님의 전적 기록이 없습니다.")
            return

        win = record[user]["승"]
        lose = record[user]["패"]
        total = win + lose
        win_rate = round(win / total * 100, 1) if total > 0 else 0
        tier = record[user].get("티어", "5티어")
        rank = record[user].get("등수", "?")

        await ctx.send(f"{ctx.author.name}님의 전적 - 승: {win} / 패: {lose} / 승률: {win_rate}% / 티어: {tier} / 등수: {rank}")

    @bot.command(name="전적수정")
    @commands.has_permissions(administrator=True)
    async def fix_result(ctx, member: discord.Member, result: str, new_value: int):
        user = str(member.id)
        ensure_user(user)

        if result == "승":
            record[user]["승"] = new_value
        elif result == "패":
            record[user]["패"] = new_value
        else:
            await ctx.send("승 또는 패 중 하나를 입력해주세요. (!전적수정 @유저 승 3)")
            return

        save_record(record)
        await ctx.send(f"{member.name}님의 전적이 수정되었습니다. (승: {record[user]['승']}, 패: {record[user]['패']})")

    @bot.command(name="티어설정")
    async def set_tier(ctx, tier: str):
        allowed_tiers = ["1티어", "2티어", "3티어", "4티어", "5티어"]
        if tier not in allowed_tiers:
            await ctx.send("올바른 티어를 입력해주세요. (1티어 ~ 5티어)")
            return

        user = str(ctx.author.id)
        ensure_user(user)
        record[user]["티어"] = tier
        save_record(record)
        await ctx.send(f"{ctx.author.name}님의 티어가 '{tier}'로 설정되었습니다.")

    @bot.command(name="등수설정")
    @commands.has_permissions(administrator=True)
    async def set_rank(ctx, member: discord.Member, rank: int):
        user = str(member.id)
        ensure_user(user)

        current_rank = record[user].get("등수", None)

        if current_rank is not None:
            for uid, stats in record.items():
                if uid != user and stats.get("등수", 9999) > current_rank:
                    stats["등수"] -= 1

        for uid, stats in record.items():
            if uid != user and stats.get("등수", 9999) >= rank:
                stats["등수"] += 1

        record[user]["등수"] = rank
        save_record(record)
        await ctx.send(f"{member.name}님의 등수가 {rank}등으로 설정되었습니다.")

    @bot.command(name="전적초기화")
    @commands.has_permissions(administrator=True)
    async def reset_records(ctx):
        record.clear()
        save_record(record)
        await ctx.send("모든 전적이 초기화되었습니다.")

    @bot.command(name="전체전적조회")
    async def view_all_records(ctx):
        if not record:
            await ctx.send("등록된 전적이 없습니다.")
            return

        sorted_records = sorted(record.items(), key=lambda x: x[1].get("등수", 9999))

        embed = discord.Embed(
            title="🏆 전체 유저 전적 목록 (등수순 + 티어 포함)",
            description="등수 기준으로 정렬된 유저 목록입니다.",
            color=discord.Color.gold()
        )

        for user_id, stats in sorted_records:
            try:
                user = await bot.fetch_user(int(user_id))
                name = user.name
            except:
                name = f"알 수 없는 사용자({user_id})"

            win = stats.get("승", 0)
            lose = stats.get("패", 0)
            total = win + lose
            win_rate = round(win / total * 100, 1) if total > 0 else 0
            tier = stats.get("티어", "5티어")
            rank = stats.get("등수", "?")

            embed.add_field(
                name=f"{rank}등 - {name}",
                value=f"승: {win} / 패: {lose} / 승률: {win_rate}% / 티어: {tier}",
                inline=False
            )

        await ctx.send(embed=embed)

    @bot.command(name="명령어")
    async def show_commands(ctx):
        embed = discord.Embed(
            title="📜 사용 가능한 명령어 목록",
            description="아래는 현재 사용 가능한 명령어들입니다.",
            color=discord.Color.blue()
        )

        embed.add_field(name="전적 관련", value=(
            "`!승패추가 승/패 (숫자)` : 내 전적 추가\n"
            "`!전적조회` : 내 전적 확인\n"
            "`!전적수정 @유저 승/패 숫자` : 관리자용 전적 수정\n"
            "`!티어설정 티어` : 본인 티어 설정\n"
            "`!등수설정 @유저 숫자` : 관리자용 등수 설정\n"
            "`!전적초기화` : 관리자용 전체 전적 초기화\n"
            "`!전체전적조회` : 전체 전적 보기"
        ), inline=False)

        await ctx.send(embed=embed)

