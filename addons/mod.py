#!/usr/bin/env python3

import discord
from discord.ext import commands
import os
import sys
import json
import asyncio

class Moderation:
    """Bot commands for moderation."""
    def __init__(self, bot):
        self.bot = bot
        print('Addon "{}" loaded'.format(self.__class__.__name__))
        
    def find_user(self, user, ctx):
        found_member = self.bot.guild.get_member(user)
        if not found_member:
            found_member = self.bot.guild.get_member_named(user)
        if not found_member:
            try:
                found_member = ctx.message.mentions[0]
            except IndexError:
                pass
        if not found_member:
            return None
        else:
            return found_member
    
    @commands.has_permissions(kick_members=True)    
    @commands.command(pass_context=True)
    async def kick(self, ctx, member, *, reason="No reason was given."):
        """Kick a member."""
        found_member = self.find_user(member, ctx)
        for channel in ctx.guild.channels:
           if isinstance(channel, discord.TextChannel) and channel.position == 0:
                first_channel = channel
                pass
        invite = await first_channel.create_invite()
        if found_member == ctx.message.author:
            return await ctx.send("You can't kick yourself, obviously")
        elif not found_member:
            await ctx.send("That user could not be found.")
        else:
            embed = discord.Embed(title="{} kicked".format(found_member))
            embed.description = "{}#{} was kicked by {} for:\n\n{}".format(found_member.name, found_member.discriminator, ctx.message.author, reason)
            await self.bot.log_channel.send(embed=embed)
            try:
                await found_member.send("You were kicked from {} for:\n\n`{}`\n\nIf you believe this to be in error, you can rejoin here: {}".format(ctx.guild.name, reason, invite))
            except discord.Forbidden:
                pass # bot blocked or not accepting DMs
            await found_member.kick(reason=reason)
            await ctx.send("Successfully kicked user {0.name}#{0.discriminator}!".format(found_member))
     
    @commands.command(pass_context=True)
    async def ban(self, ctx, member, *, reason="No reason was given."):
        """Ban a member."""
        found_member = self.find_user(member, ctx)
        author_roles = ctx.message.author.roles[1:]
        if found_member == ctx.message.author:
            return await ctx.send("You can't ban yourself, obviously")
        elif found_member == ctx.guild.owner:
            return await ctx.send("{}#{} has been banned{}!".format(ctx.guild.owner.name, ctx.guild.owner.discriminator, " for reason: `{}`".format(reason) if reason != "No reason was given." else ""))
        elif not any(r in author_roles for r in self.bot.staff_roles):
            return await ctx.send("You're not a mod!")
        elif any(r in found_member.roles[1:] for r in self.bot.staff_roles):
            return await ctx.send("That member is protected!")
        elif not found_member:
            await ctx.send("That user could not be found.")
        else:
            embed = discord.Embed(title="{} banned".format(found_member))
            embed.description = "{}#{} was banned by {} for:\n\n{}".format(found_member.name, found_member.discriminator, ctx.message.author, reason)
            embed.set_footer(text="Member ID = {}".format(found_member.id))
            await self.bot.log_channel.send(embed=embed)
            if self.bot.private_logs:
                await self.bot.private_logs.send(embed=embed)
            if self.bot.public_logs:
                if reason != "No reason was given.":
                    embed.description = "Reason: {}".format(reason)
                    embed.set_footer(text=discord.Embed.Empty)
                    embed.title = "{}".format(found_member.name)
                    await self.bot.public_logs.send(embed=embed)
                else:
                    await self.bot.log_channel.send("Did not send a public log, as no reason was given. {} please fill in the public log manually, and provide a reason next time.".format(ctx.message.author.mention))
            try:
                await found_member.send("You were banned from {} for:\n\n`{}`\n\nIf you believe this to be in error, please contact a staff member.".format(ctx.guild.name, reason))
            except:
                pass # bot blocked or not accepting DMs
            await found_member.ban(reason=reason)
            await ctx.send("Successfully banned user {0.name}#{0.discriminator}!".format(found_member))
            
    @commands.has_permissions(kick_members=True)
    @commands.command(aliases=['p'])
    async def purge(self, ctx, amount=0, *, reason=""):
        """Purge x amount of messages"""
        await ctx.message.delete()
        asyncio.sleep(3)
        if amount > 0:
            self.bot.message_purge = True
            await ctx.channel.purge(limit=amount)
            asyncio.sleep(4)
            self.bot.message_purge = False
            message = "{} purged {} messages in {}".format(ctx.author, amount, ctx.channel.mention)
            if reason:
                message += " for `{}`".format(reason)
            await self.bot.log_channel.send(message)
        else:
            await ctx.send("Why would you wanna purge no messages?", delete_after=10)
            
    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def hide(self, ctx, member, reason="No reason was given."):
        """Hides a user from sight"""
        await ctx.message.delete()
        found_member = self.find_user(member, ctx)
        author_roles = ctx.message.author.roles[1:]
        if found_member == ctx.message.author:
            return await ctx.send("You can't hide yourself, obviously")
        elif any(r in found_member.roles[1:] for r in self.bot.staff_roles):
            return await ctx.send("That member is protected!")
        elif not found_member:
            await ctx.send("That user could not be found.")
        else:
            if not self.bot.restrict_role in found_member.roles[1:]:
                await found_member.add_roles(self.bot.restrict_role)
                if self.bot.approval:
                    await found_member.remove_roles(self.bot.default_role)
                try:
                    await found_member.send("You were hidden away from {} for:\n\n`{}`\n\nIf you believe this to be in error, please contact a staff member.".format(ctx.guild.name, reason))
                except:
                    pass # bot blocked or not accepting DMs
                embed = discord.Embed(title="{} hidden".format(found_member))
                embed.description = "{}#{} was hidden by {} for:\n\n{}".format(found_member.name, found_member.discriminator, ctx.message.author, reason)
                await self.bot.log_channel.send(embed=embed)
                await ctx.send("Successfully hid user {0.name}#{0.discriminator}!".format(found_member))
            else:
                return await ctx.send("{0.name}#{0.discriminator} is already restricted!".format(found_member))
            
    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def unhide(self, ctx, member):
        """Unhides a user from sight"""
        await ctx.message.delete()
        found_member = self.find_user(member, ctx)
        author_roles = ctx.message.author.roles[1:]
        if found_member == ctx.message.author:
            return await ctx.send("You can't unhide yourself, ask someone else")
        elif not found_member:
            await ctx.send("That user could not be found.")
        else:
            if self.bot.restrict_role in found_member.roles[1:]:
                await found_member.remove_roles(self.bot.restrict_role)
                if self.bot.approval:
                    await found_member.add_roles(self.bot.default_role)
                embed = discord.Embed(title="{} hidden".format(found_member))
                embed.description = "{}#{} was unhidden by {}".format(found_member.name, found_member.discriminator, ctx.message.author)
                await self.bot.log_channel.send(embed=embed)
                await ctx.send("Successfully unhid user {0.name}#{0.discriminator}!".format(found_member))
            else:
                return await ctx.send("{0.name}#{0.discriminator} isn't restricted!".format(found_member))
    
    def check_if_approval_system(self):
        return self.bot.approval
        
    @commands.command()
    @commands.check(check_if_approval_system)
    async def approve(self, ctx, member):
        """Approves a user, requires approval system to be on"""
        await ctx.message.delete()
        found_member = self.find_user(member, ctx)
        author_roles = ctx.message.author.roles[1:]
        if not any(r in author_roles[1:] for r in self.bot.staff_roles):
            return await ctx.send("You can't use this! You need a mod!", delete_after=5)
        elif not found_member:
            await ctx.send("That user could not be found.")
        else:
            if self.bot.default_role in found_member.roles[1:]:
                return await ctx.send("That user has already been approved!", delete_after=5)
            else:
                await found_member.add_roles(self.bot.default_role)
                embed = discord.Embed(title="{0.name}#{0.discriminator} Approved".format(found_member))
                embed.description = "{0.name}#{0.discriminator} was approved by {1.mention}".format(found_member, ctx.message.author)
                await self.bot.log_channel.send(embed=embed)
                try:
                    await found_member.send("You have been approved on {0.name}! Enjoy the server!".format(ctx.guild))
                except discord.Forbidden:
                    pass # Bot blocked
        
            
            
def setup(bot):
    bot.add_cog(Moderation(bot))
