# About bot
This bot works in Lavalink with Wavelink wrapper. It could skip, play on youtube/soundcloud, have filters and some small futures.

# How to use?

1. Install python ^1.12 [Here](https://www.python.org/downloads/)

2. Clone repository (To desktop for example):
```shell
cd desktop
git clone https://github.com/IZomBiee/Wavelink-Discord-Bot
```

3. Install poetry and restart console (If you don't have):
```shell
pip install poetry
```

4. Select the project directory:
```shell
cd Wavelink-Discord-Bot
```

5. Install dependencies
```shell
poetry install
```

6. Download Lavalink [Here](https://github.com/lavalink-devs/Lavalink/releases) and place in lavalink folder

7. Run main file and change settings in .env:
```shell
poetry run python "wavelink discord bot\main.py"
```

8. Run main file again

9. Congratulations! You can see all commands write / in discord channel

### Note: Sometimes you may need to update the youtube plugin, it can be downloaded [Here](https://github.com/lavalink-devs/youtube-source/releases) and replaced in the lavalink/plugins folder. After that, in the lavalink folder you need to replace the last line in the application.yml ```dependency: "dev.lavalink.youtube:youtube-plugin:1.8.3"``` file with the correct version.