# Bobby Discord Bot

Bobby is a small discord bot for personal use. Runs in a docker container.

# How to run
1. [Create a discord bot account and invite it to a test discord server](https://discordpy.readthedocs.io/en/stable/discord.html)
2. Once you've copied the token, save it and add it as an environment variable (named `API_TOKEN`) in your terminal session:
```
$ export API_TOKEN=<YOUR_API_TOKEN_HERE>
```
**If you don't want to run it in Docker**: 

1. Change directory to `src`
2. Run the discord bot 
```
$ python main.py
```

**If you do want to run it in Docker**:

1. Ensure you have [docker installed](https://www.docker.com/get-started/)
2. Ensure you are the root of the project directory
3. Build the docker image, labelling the image with a tag of your choice
```
$ docker build --tag <YOUR_TAG_NAME_OF_CHOICE> .
```
4. Run the container with tagged image
```
$ docker run <THE_NAME_OF_THE_TAG>
```

# Contributing

### If you want to contribute a new feature
1. Refer to the [discord.py documentation](https://discordpy.readthedocs.io/en/latest/index.html) and [Github repo](https://github.com/Rapptz/discord.py)
1. Look at `src/commands/ping.py` on how to write a basic discord command
1. I don't have a testing pipeline set up and I don't think I ever will so you'll have to [test your changes yourself](#how-to-run)
1. Submit a pull request