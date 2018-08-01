import discord
from discord.ext import commands
import asyncio
import git
from datetime import datetime

git = git.cmd.Git(".")

class Events:

    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
                
    async def on_member_join(self, member):
        embed = discord.Embed(title="New member!", colour=discord.Color.green())
        embed.description = "{0.mention} | {0.name}#{0.discriminator} | {0.id} | {1} Pacific".format(member, datetime.now().strftime('%H:%M:%S'))
        await self.bot.log_channel.send(embed=embed)
        
        if self.bot.approval:
            asyncio.sleep(10)
            members = 0
            for user in self.bot.guild.members:
                if not user.bot:
                    members += 1
            await self.bot.approval_channel.send("Welcome to {0} {1}! This server is owned by {2.name}#{2.discriminator} and currently has {3} members. Please make sure to read the rules channel, and check out the channel description in this channel for further instructions.".format(self.bot.guild, member.mention, self.bot.guild.owner, members))
            
    async def on_member_remove(self, member):
        embed = discord.Embed(title="Member left.", colour=discord.Color.blue())
        embed.description = "{0.mention} | {0.name}#{0.discriminator} | {0.id} | {1} Pacific".format(member, datetime.now().strftime('%H:%M:%S'))
        await self.bot.log_channel.send(embed=embed)
        if member == self.bot.creator:
            try:
                await member.unban()
            except:
                pass
                
    async def on_member_update(self, before, after):
        if before == self.bot.user and after.nick != None:
            await after.edit(nick=None)
            await self.bot.log_channel.send("Someone tried to change my name to {} 😡".format(after.nick))
                
                
    async def on_message(self, message):
        # auto ban on 15+ pings
        if len(message.mentions) > 15:
            embed = discord.Embed(description=message.content)
            await message.delete()
            await message.author.ban()
            await message.channel.send("{} was banned for attempting to spam user mentions.".format(message.author))
            await self.bot.log_channel.send("{} was banned for attempting to spam user mentions.".format(message.author))
            
        if self.bot.user.mention in message.content:
            if message.author == self.bot.creator:
                await message.channel.send("Yes {}?".format(self.bot.creator.mention))
            else:
                await message.channel.send("Fuck off {}.".format(message.author.mention))
        
        if isinstance(message.channel, discord.abc.GuildChannel) and 'git' in message.channel.name and message.author.name == 'GitHub':
            print('Pulling changes')
            git.pull()
            print('Changes pulled!')
            
    async def on_message_delete(self, message):
        if isinstance(message.channel, discord.abc.GuildChannel) and message.author.id != self.bot.user.id and not message.author.bot:
            if message.channel not in self.bot.ignored_channels and not self.bot.message_purge:
                embed = discord.Embed(description=message.content)
                if message.attachments: # attachments code doesn't work, will fix later.
                        attachment_urls = []
                        for attachment in message.attachments:
                            attachment_urls.append('[{}]({})'.format(attachment.filename, attachment.url))
                        attachment_msg = '\N{BULLET} ' + '\n\N{BULLET} s '.join(attachment_urls)
                        embed.add_field(name='Attachments', value=attachment_msg, inline=False)
                await self.bot.message_log_channel.send("Message by {0} deleted in channel {1.mention}:".format(message.author, message.channel), embed=embed)

        
def setup(bot):
    bot.add_cog(Events(bot))