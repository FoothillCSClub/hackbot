import os
import json

import discord
from discord.ext.commands import Bot, Context, BadArgument, check

import settings
from database import db

PREFIX = ('hacks ', 'Hacks ', 'hack ', 'Hacks ')
DISCORD_API_KEY = os.environ.get('DISCORD_API_KEY')

CS_BLUE = discord.Color.from_rgb(1, 130, 180)
CS_GREEN = discord.Color.from_rgb(1, 153, 1)

bot = Bot(command_prefix=PREFIX)


@bot.event
async def on_ready():
    print(f'Logged on as {bot.user.name}')

    game = discord.Game(f'"{PREFIX[0]}help" for usage!')
    await bot.change_presence(activity=game)


async def is_mod(ctx: Context):
    if ctx.guild:
        hack_guild = db.get_guild(ctx.guild.id)

        if hack_guild and ctx.author.id in hack_guild['mods']:
            return True

    return False


def id_to_mention(user_id):
    return f'<@{user_id}>'


def format_hack(hack):
    parts = ''

    for person in hack['people']:
        parts += f"<@{person}> "

    parts += f" - {hack['description']}"

    return parts


def format_hacks(add_index=False):
    parts = ''

    for i, hack in enumerate(db.get_hacks()):
        if add_index:
            parts += f'`{i}` '
        parts += f'{format_hack(hack)}\n'

    return parts


async def send_hackathon_info(channel: discord.TextChannel, edit=None, send=True):
    embed = discord.Embed(
        title=settings.TITLE,
        description=settings.MAIN_TEXT,
        color=CS_BLUE
    )

    if edit:
        try:
            message = await channel.fetch_message(edit)
            if message:
                await message.edit(embed=embed)
                return message
        except discord.NotFound:
            pass

    if send:
        return await channel.send(embed=embed)

    return None


async def send_hacks_list(channel: discord.TextChannel, edit=None, send=True):
    description = format_hacks(add_index=True)
    embed = discord.Embed(
        title='Hacks',
        description=description,
        color=CS_GREEN,
    )

    if edit:
        try:
            message = await channel.fetch_message(edit)
            if message:
                await message.edit(embed=embed)
                return message
        except discord.NotFound:
            pass

    if send:
        return await channel.send(embed=embed)

    return None


async def edit_sent(ctx: Context):
    hack_guild = db.get_guild(ctx.guild.id)

    if hack_guild:
        for channel_id, info in hack_guild['channels'].items():
            if info:
                channel = ctx.guild.get_channel(int(channel_id))

                if info.get('info_id'):
                    info_msg = await send_hackathon_info(channel, edit=info['info_id'], send=False)
                if info.get('list_id'):
                    list_msg = await send_hacks_list(channel, edit=info['list_id'], send=False)


@bot.command('list', brief='List all hacks')
async def list_(ctx: Context):
    await send_hacks_list(ctx.channel)


@bot.command('send', brief='Send hackathon info and hacks list msgs')
@check(is_mod)
async def send(ctx: Context, channel: discord.TextChannel = None):
    hack_guild = db.get_guild(ctx.guild.id)

    if hack_guild:
        channel = channel or ctx.channel
        channel_id = str(channel.id)

        prev_info = hack_guild['channels'].get(channel_id)

        if prev_info:
            info_msg = await send_hackathon_info(channel, edit=prev_info['info_id'])
            list_msg = await send_hacks_list(channel, edit=prev_info['list_id'])
        else:
            info_msg = await send_hackathon_info(channel)
            list_msg = await send_hacks_list(channel)

        hack_guild['channels'][channel_id] = {'info_id': info_msg.id, 'list_id': list_msg.id}
        db.set_guild(ctx.guild.id, hack_guild)


@bot.command('delete', brief='Delete hackathon info messages')
@check(is_mod)
async def delete(ctx: Context, channel: discord.TextChannel = None):
    hack_guild = db.get_guild(ctx.guild.id)

    if hack_guild:
        channel = channel or ctx.channel
        channel_id = str(channel.id)

        prev_info = hack_guild['channels'].get(channel_id)

        if prev_info:
            try:
                info_msg = await channel.fetch_message(prev_info['info_id'])
                list_msg = await channel.fetch_message(prev_info['list_id'])

                await info_msg.delete()
                await list_msg.delete()

                del hack_guild['channels'][channel_id]
                db.set_guild(ctx.guild.id, hack_guild)

            except discord.NotFound:
                pass


@send.error
async def send_error(ctx, error):
    if isinstance(error, BadArgument):
        await ctx.send('Usage: `hacks add "description" @hacker1 [@hacker2]`')
    else:
        raise error


@bot.command('add', brief='Add a hack')
async def add(ctx: Context, description: str = None):
    mentions = ctx.message.mentions

    if not description or len(mentions) == 0:
        embed = discord.Embed(
            title="Error: Can't add the hack",
            description=f'Project description and user(s) have to be specified!'
        )
        await ctx.send(embed=embed)

    else:
        hack = {'people': [user.id for user in mentions], 'description': description}
        hacks = db.get_hacks()
        hacks.append(hack)
        db.set_hacks(hacks)

        await ctx.send(f'Added hack "{format_hack(hack)}"')
        await send_hacks_list(ctx.channel)
        await edit_sent(ctx)


@add.error
async def add_error(ctx, error):
    if isinstance(error, BadArgument):
        await ctx.send('Usage: `hacks add "description" @hacker1 [@hacker2]`')
    else:
        raise error


@bot.command('update', brief='Update a hack')
async def update(ctx: Context, index: int = None, description: str = None):
    mentions = ctx.message.mentions
    hacks = db.get_hacks()

    if index == None or index >= len(hacks):
        await send_hacks_list(ctx.channel)

    elif not description:
        embed = discord.Embed(
            title="Error: Can't update the hack",
            description=f'Project description and possibly updated user(s) have to be specified!'
        )
        await ctx.send(embed=embed)

    else:
        previous = hacks[index]

        if not (ctx.author.id in previous['people'] or await is_mod(ctx)):
            await ctx.send(f'Error: You do not have permission to modify "{format_hack(previous)}"')
            return

        people = [user.id for user in mentions] if len(mentions) > 0 else previous['people']
        hack = {'people': people, 'description': description}
        hacks[index] = hack
        db.set_hacks(hacks)

        await ctx.send(f'Updated hack "{format_hack(hack)}"')
        await send_hacks_list(ctx.channel)
        await edit_sent(ctx)


@update.error
async def update_error(ctx, error):
    if isinstance(error, BadArgument):
        await ctx.send('Usage: `hacks update # "description" [@hacker1] [@hacker2]`')
    else:
        raise error


@bot.command('remove', brief='Remove a hack')
async def remove(ctx: Context, index: int = None):
    hacks = db.get_hacks()

    if index == None or index >= len(hacks):
        await send_hacks_list(ctx.channel)

    else:
        hack = hacks[index]

        if not (ctx.author.id in hack['people'] or await is_mod(ctx)):
            await ctx.send(f'Error: You do not have permission to remove "{format_hack(hack)}"')
            return

        hacks.pop(index)
        db.set_hacks(hacks)

        await ctx.send(f'Removed hack "{format_hack(hack)}"')
        await send_hacks_list(ctx.channel)
        await edit_sent(ctx)


@remove.error
async def remove_error(ctx, error):
    if isinstance(error, BadArgument):
        await ctx.send(f'Usage: `hacks remove #`\n\nUse `{ctx.prefix}list` to list all hacks.')
    else:
        raise error


if __name__ == '__main__':
    if not DISCORD_API_KEY:
        logger.error("ERROR: Set the env variable 'DISCORD_API_KEY'")
        exit(1)

    bot.run(DISCORD_API_KEY)
