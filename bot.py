import discord
from discord.ext import commands
from discord.ext.commands import Context
import config
from utils.logger import BotLogger
import os
import platform

class DnDSpawner(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=config.PREFIX,
            intents=discord.Intents.all(),
            help_command=None
        )
        self.logger = BotLogger.get_logger()

    async def load_extensions(self) -> None:
        """
        Load all cogs on start
        """
        extensions = os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "cogs"))
        if not extensions:
            self.logger.warning("No extensions found!")
            return

        for file in extensions:
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    await self.load_extension(f"cogs.{name}")
                    self.logger.info(f"Loaded extension {name}")
                except Exception as e:
                    self.logger.error(
                        f"Failed to load extension {name} due to {type(e).__name__}: {e}"
                    )

    async def setup_hook(self) -> None:
        """
        Setup bot on launch
        """
        self.logger.info(f"Logged in as {self.user.name}")
        self.logger.info(f"discord.py API version: {discord.__version__}")
        self.logger.info(f"Python version: {platform.python_version()}")
        self.logger.info(
            f"Running on: {platform.system()} {platform.release()} ({os.name})"
        )
        self.logger.info("-------------------")
        await self.load_extensions()
        self.logger.info("-------------------")
        self.logger.info("Bot is up and running")

    async def on_message(self, message: discord.Message) -> None:
        """
        Prevent bot running own or other bot commands
        """
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

    async def on_command_completion(self, context: Context) -> None:
        """
        Report successful command completion
        """
        full_command_name = context.command.qualified_name
        split = full_command_name.split(" ")
        executed_command = str(split[0])
        if context.guild is not None:
            self.logger.info(
                f"Executed {executed_command} command in {context.guild.name} (ID: {context.guild.id}) by {context.author} (ID: {context.author.id})"
            )
        else:
            self.logger.info(
                f"Executed {executed_command} command by {context.author} (ID: {context.author.id}) in DMs"
            )

    async def on_command_error(self, context: Context, error) -> None:
        """
        Report unsuccessful command failure
        """
        match type(error).__name__:
            case "CommandOnCooldown":
                minutes, seconds = divmod(error.retry_after, 60)
                hours, minutes = divmod(minutes, 60)
                hours = hours % 24
                embed = discord.Embed(
                    description=f"**Please slow down** - You can use this command again in {f'{round(hours)} hours' if round(hours) > 0 else ''} {f'{round(minutes)} minutes' if round(minutes) > 0 else ''} {f'{round(seconds)} seconds' if round(seconds) > 0 else ''}.",
                    color=0xE02B2B,
                )
            case "NotOwner":
                embed = discord.Embed(
                    description="You are not the owner of the bot!", color=0xE02B2B
                )
                if context.guild:
                    self.logger.warning(
                        f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the guild {context.guild.name} (ID: {context.guild.id}), but the user is not an owner of the bot."
                    )
                else:
                    self.logger.warning(
                        f"{context.author} (ID: {context.author.id}) tried to execute an owner only command in the bot's DMs, but the user is not an owner of the bot."
                    )
            case "MissingPermissions":
                embed = discord.Embed(
                    description="You are missing the permission(s) `"
                                + ", ".join(error.missing_permissions)
                                + "` to execute this command!",
                    color=0xE02B2B,
                )
            case "BotMissingPermissions":
                embed = discord.Embed(
                    description="I am missing the permission(s) `"
                                + ", ".join(error.missing_permissions)
                                + "` to fully perform this command!",
                    color=0xE02B2B,
                )
            case "MissingRequiredArgument":
                embed = discord.Embed(
                    title="Error!",
                    description=str(error).capitalize(),
                    color=0xE02B2B,
                )
            case _:
                raise error

        await context.send(embed=embed)
