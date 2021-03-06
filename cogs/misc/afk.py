from typing import Union
from nextcord.channel import TextChannel
from nextcord.ext import commands
import asyncio

from nextcord.ext.commands.flags import Flag


class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_afk_users(self):
        return [
            i[0]
            for i in await (await self.bot.db.execute("SELECT id FROM afk")).fetchall()
        ]

    async def get_afk_message(self, id):
        return (
            await (
                await self.bot.db.execute(f"SELECT msg FROM afk WHERE id = ?", (id,))
            ).fetchone()
        )[0]

    async def write_afk(self, id, message):
        await self.bot.db.execute(
            "INSERT INTO afk (id, msg) VALUES(?, ?)", (id, message)
        )
        await self.bot.db.commit()

    async def remove_afk(self, id):
        await self.bot.db.execute("DELTE FROM afk WHERE id = ?", (id,))
        await self.bot.db.commit()

    async def go_afk(self, ctx, message):
        if id in await self.get_afk_users():
            await self.remove_afk(ctx.author.id)
        await self.write_afk(ctx.author.id, message)
        await ctx.send(f"{ctx.author.mention} set afk with: {message}")

    @commands.group(invoke_without_command=True)
    async def afk(self, ctx, msg="kk"):
        await self.go_afk(ctx, msg)

    @afk.command(name="ignore")
    async def afk_ignore(self, ctx, channel: TextChannel):
        self.bot.afk_ignored_channels.append(channel.id)
        await ctx.send("Ignored.")

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return
        if not msg.mentions:
            return
        if msg.channel.id in self.bot.afk_ignored_channels:
            return

        afk_users = await self.get_afk_users()
        temp_message = ""
        for user in msg.mentions:
            if user.id in afk_users:
                temp_message += f"{user.name} is afk with reason: {await self.get_afk_message(user.id)}\n"

        await msg.reply(temp_message)


def setup(bot):
    bot.add_cog(AFK(bot))
