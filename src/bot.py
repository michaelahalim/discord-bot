import discord

from discord.ext import commands
from database import *
from dotenv import dotenv_values

database = connect_to_database()
staff_df = create_pandas_table("SELECT * FROM staff", database)
student_df = create_pandas_table("SELECT * FROM student", database)
database_dict = {'staff': staff_df,
                 'student': student_df}
database.close()

config = dotenv_values()

intents = discord.Intents().all()

client = discord.Client(intents=intents)

# Shows that the bot is ready
@client.event
async def on_ready():
    print('{0.user} is ready'.format(client))
    
# Sends message to the new member.        
@client.event
async def on_member_join(member):
    await member.send(
        f'Hi {member.name}, welcome to the Upward Bound server! You must verify yourself' +
        ' by entering in `!verify` in the `#verification` channell of the UBMS Discord Server. ' +
        'Only then you will be able to access rest of the channels. Thanks!'
    )

# Verification System
@client.event
async def on_message(message):
    if message.content == '!verify' and message.channel.id == 829809966017282128:
        await message.channel.send('Are you a staff or student?')
        staff_student = ['staff', 'student']
        staff_or_student = await client.wait_for('message')
        if staff_or_student.content.lower() not in staff_student:
            while True:
                await message.channel.send('Please answer with either student or staff')
                staff_or_student = await client.wait_for('message')
                if staff_or_student.content.lower() == 'staff' or staff_or_student.content.lower() == 'student':
                    break
        data = database_dict[staff_or_student.content.lower()]
        # await message.channel.send('Please enter your first name and last name with capitalized first letter. ' +
        #                            'For example: John Smith')
        # msg = await client.wait_for('message')
        # msg = msg.content.split(' ')
        # first_name, last_name = msg[0], msg[1]
        while True:
            try:
                await message.channel.send('Please enter your first name and last name with capitalized first letter. ' +
                                   'For example: John Smith')
                msg = await client.wait_for('message')
                msg = msg.content.split(' ')
                first_name, last_name = msg[0], msg[1]
                verification = data[(data['first_name'] == first_name) & (data['last_name'] == last_name)]
                if verification.empty:
                    raise Exception('Database is empty.') 
                break
            except:
                await message.channel.send('Your name could not be found in the UBMS database. Please make sure that your name is capitalized. ' + 
                                        'If the problem persists please >>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print(staff_or_student.content.lower())
        if staff_or_student.content.lower() == 'staff':
            await message.channel.send('Please enter your berkeley email. For example: john.smith@berkeley.edu')
            email = await client.wait_for('message')
            while verification.iloc[0]['email'] != email.content:
                await message.channel.send('You entered the wrong email. Please enter your berkeley email.')
                email = await client.wait_for('message')
            role = discord.utils.get(message.guild.roles, name=verification.iloc[0]['role'])
            await message.author.add_roles(role)  
            await message.channel.send('Thank you! You have been verified. You can now access the server')
        else:
            await message.channel.send('Please enter your email. For example: john.smith@gmail.com')
            email = await client.wait_for('message')
            while verification.iloc[0]['email'] != email.content:
                await message.channel.send('You entered the wrong email. Please enter your email.')
                email = await client.wait_for('message')
            role = discord.utils.get(message.guild.roles, name='Student')
            await message.author.add_roles(role)  
            await message.channel.send('Thank you! You have been verified. You can now access the server')

client.run(config['TOKEN'])