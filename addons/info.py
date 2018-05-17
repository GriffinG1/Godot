import discord
from discord.ext import commands

class Info:

    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
        
    @commands.command()
    async def about(self, ctx):
        """Information about the bot"""
        await ctx.send("This is a bot coded in python for use in the {} server, made by {}#{}. You can view the source code here: CODE NOT UPLOADED YET.".format(ctx.guild.name, self.bot.creator.name, self.bot.creator.discriminator))
        
    @commands.command(aliases=['mc'])
    async def membercount(self, ctx):
        """Returns number of people in server"""
        members = 0
        for user in ctx.guild.members:
            if not user.bot:
                members += 1
        await ctx.send("There are {} members on this server!".format(members))
            
    @commands.command(aliases=['tc'])
    async def togglechannel(self, ctx, role=""):
        """Used for toggling roles.\nCurrently available roles: NSFW, NEWS"""
        await ctx.message.delete()
        found_member = ctx.message.author
        author_roles = found_member.roles[1:]
        role = role.lower()
        if role == "nsfw":
            if not self.bot.nsfw_role in author_roles:
                await found_member.add_roles(self.bot.nsfw_role)
                try:
                    await self.bot.log_channel.send("{}#{} accessed the nsfw channel".format(found_member.name, found_member.discriminator))
                except: # bot blocked
                    pass
                return await found_member.send("You now have access to the nsfw channel!")
            else:
                await found_member.remove_roles(self.bot.nsfw_role)
                await self.bot.log_channel.send("{}#{} left the nsfw channel".format(found_member.name, found_member.discriminator))
                try:
                    await self.bot.log_channel.send("{}#{} left the nsfw channel".format(found_member.name, found_member.discriminator))
                except:
                    pass
        elif role == "news":
            if not self.bot.news_role in author_roles:
                await found_member.add_roles(self.bot.news_role)
                await self.bot.log_channel.send("{}#{} opted to recieve news pings".format(found_member.name, found_member.discriminator))
                try:
                    return await found_member.send("You now will be pinged for news updates!")
                except: # bot blocked
                    pass 
            else:
                await found_member.remove_roles(self.bot.news_role)
                await self.bot.log_channel.send("{}#{} doesn't want to recieve news pings anymore".format(found_member.name, found_member.discriminator))
                try:
                    return await found_member.send("You won't be pinged for news updates anymore!")
                except: # bot blocked
                    pass
        else:
            return await ctx.send("Please input a choice!", delete_after=5)
        
def setup(bot):
    bot.add_cog(Info(bot))
