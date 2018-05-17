import discord
from discord.ext import commands

class Events:

    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
        
        
    async def on_guild_join(self, guild):
        if guild.id != 329431036440084481:
            try:
                await guild.owner.send("Left your server, `{}`, as this bot should only be used on the Kurain Village server under this token.".format(guild.name))
            except discord.Forbidden:
                for channel in guild.channels:
                   if guild.me.permissions_in(channel).send_messages and isinstance(channel, discord.TextChannel):
                        await channel.send("Left your server, as this bot should only be used on the PKSM server under this token.")
                        break
            finally:
                await guild.leave()
                
    async def on_member_join(self, member):
        embed = discord.Embed(title="New member!")
        embed.description = "{} | {}#{} | {}".format(member.mention, member.name, member.discriminator, member.id)
        await self.bot.log_channel.send(embed=embed)
            
    async def on_member_remove(self, member):
        embed = discord.Embed(title="Member left.")
        embed.description = "{} | {}#{} | {}".format(member.mention, member.name, member.discriminator, member.id)
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
            
    async def on_message_delete(self, message):
        if isinstance(message.channel, discord.abc.GuildChannel) and message.author.id != self.bot.user.id and not message.author.bot:
            if message.channel not in self.bot.ignored_channels and not self.bot.message_purge:
                embed = discord.Embed(description=message.content)
                if message.attachments:
                        attachment_urls = []
                        for attachment in message.attachments:
                            attachment_urls.append('[{}]({})'.format(attachment.filename, attachment.url))
                        attachment_msg = '\N{BULLET} ' + '\n\N{BULLET} s '.join(attachment_urls)
                        embed.add_field(name='Attachments', value=attachment_msg, inline=False)
                await self.bot.message_log_channel.send("Message by {0} deleted in channel {1.mention}:".format(message.author, message.channel), embed=embed)

        
def setup(bot):
    bot.add_cog(Events(bot))