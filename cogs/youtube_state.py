import discord
from discord import app_commands
from discord.ext import commands,tasks
import configparser
import youtubeAPI

class youtubestate(commands.GroupCog, name="state"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.init_config()
        
    def init_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('data/config.ini')

        self.request_loop.change_interval(minutes=self.config['Youtube_state'].getint('intervals'))
        
        self.subs_show = self.config['Youtube_state'].getboolean('show_subscriber')
        self.view_show = self.config['Youtube_state'].getboolean('show_view')
        self.lastlive_show = self.config['Youtube_state'].getboolean('show_lastlive')
        self.subs_channel = self.bot.get_channel(self.config['Youtube_state'].getint('subscriber_channel_ID'))
        self.view_channel = self.bot.get_channel(self.config['Youtube_state'].getint('view_channel_ID'))
        self.lastlive_channel = self.bot.get_channel(self.config['Youtube_state'].getint('lastlive_channel_ID'))
        self.subs_channel_text = self.config['Youtube_state'].get('subscriber_channel_text')
        self.view_channel_text = self.config['Youtube_state'].get('view_channel_text')
        self.lastlive_channel_text = self.config['Youtube_state'].get('lastlive_channel_text')
        self.living_text = self.config['Youtube_state'].get('living_text')
        
    @tasks.loop(minutes=30)
    async def request_loop(self):
        request = youtubeAPI.subs_view_request()
        subs ,view = request[0] ,request[1]
        if self.subs_show :
            await self.subs_channel.edit(name=self.subs_channel_text.replace('&',str(subs)))
        if self.view_show :
            await self.view_channel.edit(name=self.view_channel_text.replace('&',str(view)))
        if self.lastlive_show :
            lastlive = youtubeAPI.lastlive_request()
            await self.lastlive_channel.edit(name= lastlive if lastlive == self.living_text else self.lastlive_channel_text.replace('&',str(lastlive)))

        
    @app_commands.command(name="開始更新youyube狀態")
    async def start_request(self,interaction: discord.Interaction):
        self.request_loop.start()
        await interaction.response.send_message("Start!",ephemeral = True)
        
    @app_commands.command(name="停止更新youtube狀態")
    async def end_request(self,interaction: discord.Interaction): 
        self.request_loop.stop()
        await interaction.response.send_message("Stop!",ephemeral = True)
        
    @app_commands.command(description="重新加載ini檔")
    async def setup(self,interaction: discord.Interaction):
        self.init_config()
        await interaction.response.send_message("Setup setting!",ephemeral = True)
    
async def setup(bot):
    await bot.add_cog(youtubestate(bot))
