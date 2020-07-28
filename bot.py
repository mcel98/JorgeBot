import utils as u
import discord
import datetime
from discord.ext import commands


class JorgeBot:

    def __init__(self, token):
        self.client = commands.Bot(command_prefix="!",description='')
        self.cola = u.pqueue()
        self.token = token
        self.dicAlumnos = {}
        self.Membersize = 1



    def activardiscord(self):

        @self.client.event
        async def on_message(message):
            message.content = message.content.lower().replace(' ', '')
            await self.client.process_commands(message)

        @self.client.event
        async def on_member_join(member):
            self.dicAlumnos[member.id] = 'activo'


        @self.client.event
        async def on_member_remove(member):
            self.cola.delete(member.id)

        @self.client.event
        async def on_voice_state_update(member,before, after):
            channelDM = await member.create_dm()
            if before.channel == None and after.channel is not None:
                self.dicAlumnos[member.id] = 'activo'
                await channelDM.send('bienvenido a la clase')
            elif after.channel == None and before.channel is not None:
                await channelDM.send('saliste de la clase, tus consultas fueron borradas')
                del self.dicAlumnos[member.id]
                self.cola.delete(member.id)


        @self.client.command()

        async def pregunta(ctx):
            if ctx.message.author == self.client.user:
                await ctx.send(ctx.message.channel, 'bot no puede unirse a la cola')
            else:

                timestamp = (ctx.message.id >> 22) + 1420070400000
                date = datetime.datetime.fromtimestamp(timestamp / 1e3)
                time = date.time()
                time = time.hour + time.minute / 60.0
                mensaje = ctx.message.content
                voiceChannel = ctx.message.author.voice.channel
                id = ctx.message.author.id
                status = self.dicAlumnos[id]
                consulta = u.consulta(time, id, mensaje, status)
                channelDM = await ctx.message.author.create_dm()
                if status == 'denegado':
                    await channelDM.send("Ya estas en la cola de espera, espere a ser atendido antes de "
                                         "iniciar "
                                         "otra consulta")
                else:
                    self.cola.insertar_consulta(consulta)
                    self.dicAlumnos[id] = 'denegado'
                    await channelDM.send('El profesor lo atendera pronto')
                    print(self.cola.queue[0].id)

        @self.client.command()
        @commands.has_permissions(administrator = True)
        async def atender(ctx):
            size = self.cola.size()
            if size > 0:
                alumno = self.cola.atender()
                print(alumno)
                self.dicAlumnos[alumno] = 'activo'
                alumno = ctx.guild.get_member(alumno)
                canal_del_profesor = discord.utils.get(ctx.guild.voice_channels, name='Profesor')
                await alumno.move_to(canal_del_profesor)

        @self.client.command(pass_context=True)
        @commands.has_permissions(administrator=True)
        async def pausa(ctx, *, nombre: discord.user):
            canal_del_profesor = discord.utils.get(ctx.guild.voice_channels, name='Profesor')
            canal_de_espera = discord.utils.get(ctx.guild.voice_channels, name='Pausa')
            miembros = canal_del_profesor.members
            for member in miembros:
                if member == nombre:
                    self.dicAlumnos[member.id] = 'pausa'
                    await member.move_to(canal_de_espera)

        self.client.run(str(self.token))


Jorge = JorgeBot('#')
Jorge.activardiscord()
