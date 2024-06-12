import discord
from discord.ext import commands, tasks
import random
import aiohttp
import asyncio
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable the member intents

bot = commands.Bot(command_prefix="!", intents=intents)
guild_id = 1248055571249369228  # Replace with your guild ID

# Task to make the bot appear as typing continuously


#@tasks.loop(seconds=5)
#async def typing_task():
   # channel_id = 1248055571249369232  # Replace with your channel ID
   # channel = bot.get_channel(channel_id)
    #if channel:
      #  async with channel.typing():
       #     await asyncio.sleep(5)


#@typing_task.before_loop
#async def before_typing_task():
    #await bot.wait_until_ready()

# Task to update the bot's status with the member count


@tasks.loop(minutes=1)  # Update every minute
async def update_status():
    guild = bot.get_guild(guild_id)
    if guild:
        member_count = guild.member_count
        status = f"{member_count} Brat's"
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status))


@update_status.before_loop
async def before_update_status():
    await bot.wait_until_ready()

# Event handler for when the bot is ready


@bot.event
async def on_ready():
    typing_task.start()
    update_status.start()
    print(f'Logged in as {bot.user}')

# Command to change the bot's status dynamically


@bot.command()
@commands.has_permissions(administrator=True)
async def setstatus(ctx, *, status: str):
    await bot.change_presence(activity=discord.Game(name=status))
    await ctx.send(f'Status changed to: {status}')

# Event handler for welcoming new members


@bot.event
async def on_member_join(member):
    # Replace 'welcome' with your welcome channel name
    channel = discord.utils.get(member.guild.channels, name='welcome')
    if channel:
        await channel.send(f'Welcome to the server, {member.mention}!')

# Command to respond with "Hello!"


@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

# Command to check the bot's latency


@bot.command()
async def ping(ctx):
    latency = round(bot.latency * 1000)  # Convert latency to milliseconds
    await ctx.send(f'Pong! {latency}ms')

# Command to provide information about the server


@bot.command()
async def info(ctx):
    guild = ctx.guild
    num_channels = len(guild.channels)
    num_members = guild.member_count
    server_info = (
        f'Server Name: {guild.name}\n'
        f'Total Channels: {num_channels}\n'
        f'Total Members: {num_members}'
    )
    await ctx.send(server_info)

# Event handler to log messages


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignore messages sent by the bot itself

    if "angal" in message.content.lower() or "انگل" in message.content:
        await message.channel.send(f"<@1152837005366001764> بخورش")
    elif "rat" in message.content.lower() or "موش" in message.content:
        await message.channel.send(f"<@1199449822348968057> برات")
    elif "hi" in message.content.lower() or "hello" in message.content or "سلام" in message.content:
        await message.channel.send("سلام عزیزم خوبی")

    await bot.process_commands(message)  # Ensure commands are still processed

# Moderation command to kick a user


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    try:
        await member.kick(reason=reason)
        await ctx.send(f'Kicked {member.mention} for reason: {reason}')
    except discord.Forbidden:
        await ctx.send('I do not have permission to kick members.')
    except discord.HTTPException:
        await ctx.send('An error occurred while trying to kick the member.')

# Moderation command to ban a user


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    try:
        await member.ban(reason=reason)
        await ctx.send(f'Banned {member.mention} for reason: {reason}')
    except discord.Forbidden:
        await ctx.send('I do not have permission to ban members.')
    except discord.HTTPException:
        await ctx.send('An error occurred while trying to ban the member.')

# Moderation command to unban a user


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member: str):
    try:
        banned_users = await ctx.guild.bans()
    except discord.Forbidden:
        await ctx.send('I do not have permission to view the ban list.')
        return
    except discord.HTTPException:
        await ctx.send('An error occurred while retrieving the ban list.')
        return

    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            try:
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return
            except discord.Forbidden:
                await ctx.send('I do not have permission to unban members.')
            except discord.HTTPException:
                await ctx.send('An error occurred while trying to unban the member.')

    await ctx.send(f'User {member} not found in the ban list.')


@unban.error
async def unban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have permission to use this command.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Invalid member format. Please use the format: name#discriminator.')
    else:
        await ctx.send('An error occurred while processing the command.')

# Moderation command to mute a user


@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")

        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False, read_message_history=True, read_messages=True)

    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f'Muted {member.mention} for reason: {reason}')

# Moderation command to unmute a user


@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f'Unmuted {member.mention}')
    else:
        await ctx.send(f'{member.mention} is not muted')

# Fun command to roll a dice


@bot.command()
async def roll(ctx, sides: int):
    if sides < 1:
        await ctx.send('The number of sides must be greater than 0.')
        return

    result = random.randint(1, sides)
    await ctx.send(f'Rolled a {result} on a {sides}-sided dice')

# Fun command to flip a coin


@bot.command()
async def flip(ctx):
    result = random.choice(['Heads', 'Tails'])
    await ctx.send(f'The coin landed on {result}')

# Fun command to get a random joke


@bot.command()
async def joke(ctx):
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "Why don't skeletons fight each other? They don't have the guts.",
        "What do you get when you cross a snowman and a vampire? Frostbite.",
        "What do you call fake spaghetti? An impasta!",
        "Why don't skeletons fight each other? They don't have the guts.",
        "What did the fish say when it hit the wall? Dam!",
        "Why did the math book look sad? Because it had too many problems.",
        "Why was the math lecture so long? The professor kept going off on a tangent.",
        "What do you call a belt made of watches? A waist of time.",
        "How do you organize a space party? You planet!",
        "Why did the bicycle fall over? Because it was two-tired.",
        "Why was the big cat disqualified from the race? Because it was a cheetah.",
        "What do you call a pile of cats? A meowtain.",
        "Why don't eggs tell jokes? Because they might crack up.",
    ]
    await ctx.send(random.choice(jokes))

# Fun command to get a random number in a specified range


@bot.command()
async def randomnumber(ctx, start: int, end: int):
    if start >= end:
        await ctx.send('The start number must be less than the end number.')
        return

    result = random.randint(start, end)
    await ctx.send(f'Random number between {start} and {end}: {result}')

# Command to get a random meme from an API


@bot.command()
async def meme(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://meme-api.herokuapp.com/gimme') as response:
            if response.status == 200:
                data = await response.json()
                await ctx.send(data['url'])
            else:
                await ctx.send('Could not fetch a meme at the moment. Try again later.')

# Command to get the current weather for a city


@bot.command()
async def weather(ctx, *, city: str):
    # Replace with your OpenWeatherMap API key
    api_key = 'YOUR_OPENWEATHERMAP_API_KEY'
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric') as response:
            if response.status == 200:
                data = await response.json()
                weather_description = data['weather'][0]['description']
                temperature = data['main']['temp']
                await ctx.send(f'The current weather in {city} is {weather_description} with a temperature of {temperature}°C.')
            else:
                await ctx.send(f'Could not fetch weather data for {city}. Please check the city name and try again.')

# Command to create a poll


@bot.command()
async def poll(ctx, *, question: str):
    message = await ctx.send(f'Poll: {question}')
    await message.add_reaction('👍')
    await message.add_reaction('👎')

# Command to set a reminder


@bot.command()
async def remind(ctx, time: int, *, task: str):
    await ctx.send(f'Reminder set for {time} seconds to: {task}')
    await asyncio.sleep(time)
    await ctx.send(f'{ctx.author.mention}, here is your reminder: {task}')

# Command to get a random trivia question from an API


@bot.command()
async def trivia(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://opentdb.com/api.php?amount=1&type=multiple') as response:
            if response.status == 200:
                data = await response.json()
                question = data['results'][0]['question']
                correct_answer = data['results'][0]['correct_answer']
                options = data['results'][0]['incorrect_answers']
                options.append(correct_answer)
                random.shuffle(options)

                trivia_message = f"**Question:** {question}\n"
                for i, option in enumerate(options):
                    trivia_message += f"{i + 1}. {option}\n"
                trivia_message += "Reply with the correct option number."

                await ctx.send(trivia_message)

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel and m.content.isdigit()

                try:
                    response = await bot.wait_for('message', check=check, timeout=30.0)
                except asyncio.TimeoutError:
                    await ctx.send(f'Sorry, you took too long. The correct answer was: {correct_answer}')
                else:
                    answer = options[int(response.content) - 1]
                    if answer == correct_answer:
                        await ctx.send('Correct!')
                    else:
                        await ctx.send(f'Incorrect. The correct answer was: {correct_answer}')
            else:
                await ctx.send('Could not fetch trivia question at the moment. Try again later.')

# Define your custom command


@bot.command()
async def custom_command(ctx):
    await ctx.send('This is a custom command!')

# Moderation command to clear messages


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    if amount < 1:
        await ctx.send("Please specify a number greater than 0.")
        return

    try:
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)
    except discord.Forbidden:
        await ctx.send('I do not have permission to delete messages.')
    except discord.HTTPException:
        await ctx.send('An error occurred while trying to delete messages.')


@clear.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('You do not have permission to use this command.')
    elif isinstance(error, commands.BadArgument):
        await ctx.send('Invalid argument. Please provide a number of messages to delete.')
    else:
        await ctx.send('An error occurred while processing the command.')

# Command to provide help information


@bot.command(name='commands_help')  # Renaming the command to avoid conflicts
async def help(ctx):
    help_message = (
        "**List of Commands**\n"
        "!hello - Responds with 'Hello!'\n"
        "!ping - Checks the bot's latency\n"
        "!info - Provides information about the server\n"
        "!kick <member> <reason> - Kicks a member from the server\n"
        "!ban <member> <reason> - Bans a member from the server\n"
        "!unban <member#1234> - Unbans a member from the server\n"
        "!mute <member> <reason> - Mutes a member in the server\n"
        "!unmute <member> - Unmutes a member in the server\n"
        "!roll <sides> - Rolls a dice with the specified number of sides\n"
        "!flip - Flips a coin\n"
        "!joke - Tells a random joke\n"
        "!randomnumber <start> <end> - Gets a random number between the specified range\n"
        "!meme - Fetches a random meme\n"
        "!weather <city> - Gets the current weather for the specified city\n"
        "!poll <question> - Creates a poll\n"
        "!remind <time> <task> - Sets a reminder for the specified time\n"
        "!trivia - Asks a random trivia question\n"
    )
    await ctx.send(help_message)

# Run the bot
bot.run('DISCORD_TOKEN')
