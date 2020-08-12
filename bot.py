import utils as u
import discord
import datetime
from discord.ext import commands


class JorgeBot:

    def __init__(self, token):
        self.client = commands.Bot(command_prefix="!", description='')
        self.cola = u.pqueue()
        self.token = token
        self.dicAlumnos = {}
        self.Membersize = 1
        self.form = 0

    def activardiscord(self):

        @self.client.event
        async def on_message(message):
            message.content = message.content.lower().replace(' ', '')
            await self.client.process_commands(message)

        @self.client.event
        async def on_member_join(member):
            channelDM = await member.create_dm()
            self.dicAlumnos[member.id] = 'activo'
            await channelDM.send('Bienvenido a la cursada, Por favor ingrese su mail:')

            def check(message, channel):
                return message.author == member and message.channel == channelDM

            respuesta = await self.client.wait_for('message', check=check)



        @self.client.event
        async def on_member_remove(member):
            self.cola.delete(member.id)

        @self.client.event
        async def on_voice_state_update(member, before, after):
            channelDM = await member.create_dm()
            if before.channel == None and after.channel is not None:
                self.dicAlumnos[member.id] = 'activo'
                await channelDM.send('bienvenido a la clase')
            elif after.channel == None and before.channel is not None:
                await channelDM.send('saliste de la clase, tus consultas fueron borradas')
                del self.dicAlumnos[member.id]
                self.cola.delete(member.id)

        @self.client.command()
        @commands.has_permissions(administrator=True)
        async def consultas(ctx):
            Anuncio = discord.Embed(
                title='Consultas abiertas',
                description='Hacer click en el icono de la mano para hacer una pregunta y espere ser atendido',
                colour=discord.Colour.orange()
            )
            channel = discord.utils.get(ctx.guild.text_channels, name="consultas")
            message = await channel.send(embed=Anuncio)
            self.form = message.id
            await message.add_reaction('\u270B')

        @self.client.event
        async def on_reaction_add(reaction, user):
            if(reaction.message.id == self.form):
                timestamp = (reaction.message.id >> 22) + 1420070400000
                date = datetime.datetime.fromtimestamp(timestamp / 1e3)
                time = date.time()
                time = time.hour + time.minute / 60.0
                id = user.id
                if(id != self.client.user.id):

                    status  = self.dicAlumnos[id]
                    channelDM = await user.create_dm()
                    consulta = u.consulta(time, id, status)
                    if status == 'denegado':
                        await channelDM.send("Ya estas en la cola de espera, espere a ser atendido antes de "
                                             "iniciar "
                                             "otra consulta")
                    else:
                        self.cola.insertar_consulta(consulta)
                        self.dicAlumnos[id] = 'denegado'
                        await channelDM.send('El profesor lo atendera pronto')


        @self.client.command()
        @commands.has_permissions(administrator=True)
        # problemas de concurrencia con más de un profesor TODO: asyncio lock() o await sleep
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

        self.client.run(self.token)

Jorge = JorgeBot('')
Jorge.activardiscord()
