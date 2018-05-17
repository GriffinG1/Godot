# import dependencies
import os
from discord.ext import commands
import discord
import datetime
import json, asyncio
import copy
import configparser
import traceback
import sys
import os
import re
import ast

import config

# sets working directory to bot's folder
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

token = config.token
prefix = config.prefix
description = config.description

bot = commands.Bot(command_prefix=prefix, description=description)

bot.dir_path = os.path.dirname(os.path.realpath(__file__))

# mostly taken from https://github.com/Rapptz/discord.py/blob/async/discord/ext/commands/bot.py
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        pass  # ...don't need to know if commands don't exist
    elif isinstance(error, discord.ext.commands.errors.CheckFailure):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        formatter = commands.formatter.HelpFormatter()
        await ctx.send("You are missing required arguments.\n{}".format(formatter.format_help_for(ctx, ctx.command)[0]))
    else:
        if ctx.command:
            await ctx.send("An error occurred while processing the `{}` command.".format(ctx.command.name))
        print('Ignoring exception in command {0.command} in {0.message.channel}'.format(ctx))
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        error_trace = "".join(tb)
        print(error_trace)

@bot.event
async def on_error(event_method, *args, **kwargs):
    if isinstance(args[0], commands.errors.CommandNotFound):
        return
    print("Ignoring exception in {}".format(event_method))
    tb = traceback.format_exc()
    error_trace = "".join(tb)
    print(error_trace)


@bot.event
async def on_ready():
    # this bot should only ever be in one server anyway
    for guild in bot.guilds:
        try:
            if guild.id == 329431036440084481:
                    
                bot.guild = guild
                
                try:
                    with open("restart.txt") as f:
                        channel = bot.get_channel(int(f.readline()))
                        f.close()
                    await channel.send("Restarted!")
                    os.remove("restart.txt")
                except:
                    pass
                    
                bot.creator = discord.utils.get(guild.members, id=177939404243992578)
                
                bot.log_channel = discord.utils.get(guild.channels, id=config.log_channel)
                bot.message_log_channel = discord.utils.get(guild.channels, id=config.message_log_channel)
                bot.ignored_channels = {bot.message_log_channel, bot.log_channel}
                for id in config.ignored_chans:
                    bot.ignored_channels.add(discord.utils.get(guild.channels, id=id))
                    
                if config.nsfw_role != "":
                    bot.nsfw_role = discord.utils.get(guild.roles, name=config.nsfw_role)
                if config.news_role != "":
                    bot.news_role = discord.utils.get(guild.roles, name=config.news_role)
                if config.restrict_role != "":
                    bot.restrict_role = discord.utils.get(guild.roles, name=config.restrict_role)
                bot.staff_roles = set()
                for role in config.staff_roles:
                    bot.staff_roles.add(discord.utils.get(guild.roles, name=role))
                    
                bot.blocked_users = set()
                for id in config.blocked_users:
                    bot.blocked_users.add(discord.utils.get(guild.members, id=id))
                    
                bot.message_purge = False
                
                
                if guild.me.nick != None:
                    old_nick = guild.me.nick
                    await bot.user.edit(nick=None)
                    await bot.log_channel.send("Someone changed my name to {} while I was offline 😡".format(old_nick))
                    
            else:
                try:
                    await guild.owner.send("Left your server, `{}`, as this bot should only be used on the Kurain Village server under this token.".format(guild.name))
                except discord.Forbidden:
                    for channel in guild.channels:
                       if guild.me.permissions_in(channel).send_messages and isinstance(channel, discord.TextChannel):
                            await channel.send("Left your server, as this bot should only be used on the PKSM server under this token.")
                            break
                finally:
                    await guild.leave()
                
            print("Initialized on {}.".format(guild.name))
        except Exception as e:
            print("Failed to initialize on {}".format(guild.name))
            print("\t{}".format(e))

    
# loads extensions
addons = [
    'addons.info',
    'addons.events',
    'addons.utility',
    'addons.mod',
]

failed_addons = []

for extension in addons:
    try:
        bot.load_extension(extension)
    except Exception as e:
        print('{} failed to load.\n{}: {}'.format(extension, type(e).__name__, e))
        failed_addons.append([extension, type(e).__name__, e])
if not failed_addons:
    print('All addons loaded!')
    
@bot.check
def check_author_is_blocked(ctx):
    return ctx.author not in bot.blocked_users

        
@bot.command()
async def reload(ctx):
    """Reloads an addon."""
    if ctx.author != ctx.guild.owner and ctx.author != bot.creator:
        return await ctx.send("You can't use this!")
    errors = ""
    for addon in os.listdir("addons"):
        if ".py" in addon:
            addon = addon.replace('.py', '')
            try:
                bot.unload_extension("addons.{}".format(addon))
                bot.load_extension("addons.{}".format(addon))
            except Exception as e:
                errors += 'Failed to load addon: `{}.py` due to `{}: {}`\n'.format(addon, type(e).__name__, e)
    if not errors:
        await ctx.send(':white_check_mark: Extensions reloaded.')
    else:
        await ctx.send(errors)
        
@bot.command(hidden=True)
async def load(ctx, *, module):
    """Loads an addon"""
    if ctx.author != ctx.guild.owner and ctx.author != bot.creator:
        return await ctx.send("You can't use this!")
    try:
        bot.load_extension("addons.{}".format(module))
    except Exception as e:
        await ctx.send(':anger: Failed!\n```\n{}: {}\n```'.format(type(e).__name__, e))
    else:
        await ctx.send(':white_check_mark: Extension loaded.')
        
@bot.command(hidden=True)
async def botedit(ctx, name=""):
    """Edits the bot profile. Takes name only, at the moment. Bot owner only"""
    await ctx.message.delete()
    if ctx.author != bot.creator:
        return
    if not name:
        name = bot.user.name
    return await bot.user.edit(username=name)
        
# Execute
print('Bot directory: ', dir_path)
bot.run(token)
