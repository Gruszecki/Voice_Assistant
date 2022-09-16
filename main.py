import commands

commands.greetings()

while True:
    if not commands.listen():       # Return 0 when command for closing app is called
        break
