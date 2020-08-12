import utils as u
import discord
import csv
from discord.ext import commands
import smtplib


class JorgeBot:

    def __init__(self, token, mail, mailProfesor):
        self.client = commands.Bot(command_prefix="!", description='')
        self.cola = u.pqueue()
        self.token = token
        self.mailBot = mail
        self.mailProfesor = mailProfesor
        self.dicAlumnos = {}
        self.Membersize = 1
        self.form = 0

    def enviarMail(self, id, texto):
        SUBJECT = 'Consulta'
        gmail_sender = self.mailBot[0] + '@gmail.com'
        gmail_passwd = self.mailBot[1]
        profesor = self.mailProfesor
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_sender, gmail_passwd)
        mail = ''
        with open('mails.csv', 'r', newline='') as mails:
            rd = csv.DictReader(mails)
            for row in rd:
                if row['member_id'] == id:
                    mail = row['mails']
        mails.close()

        BODY = '\r\n'.join(['To: %s' % profesor,
                           'From: %s' % mail,
                           'Subject: %s' % SUBJECT,
                           '', texto])
        try:
            server.sendmail(gmail_sender, [profesor], BODY)
            print('email sent')
        except:
            print('error sending mail')
        server.quit()

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
            with open('mails.csv', 'w', newline='') as mails:
                fieldnames = ['alumno_id','mail']
                wr = csv.DictWriter(mails, fieldnames=fieldnames)
                wr.writerow({'alumno_id': str(member.id), 'mails':respuesta.content})
            mails.close()

        @self.client.event
        async def on_member_remove(member):
            self.cola.delete(member.id)

        @self.client.event
        async def on_voice_state_update(member, before, after):
            channelDM = await member.create_dm()
            if before.channel is None and after.channel is not None:
                self.dicAlumnos[member.id] = 'activo'
                await channelDM.send('bienvenido a la clase')
            elif after.channel is None and before.channel is not None:
                def check(message, channel):
                    return message.author == member and message.channel == channelDM

                await channelDM.send('Saliste de la clase, consultas borradas. ¿Desea que enviar un mail de consulta al profesor? si/no')
                respuesta = await self.client.wait_for('message', check=check, timeout=60)
                resString = respuesta.content.lower()
                if resString == 'si':
                    await channelDM.send('Ingrese Consulta:')
                    consulta = await self.client.wait_for('message', check=check, timeout=60)
                    texto = consulta.content.lower()
                    id = consulta.author.id
                    self.enviarMail(id,texto)
                elif resString != 'no':
                    await channelDM.send('respuesta invalida. Vuelva a intentar')
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
            num = await reaction.count()
            id = user.id
            if id != self.client.user.id:
                status = self.dicAlumnos[id]
                channelDM = await user.create_dm()
                consulta = u.consulta(num, id, status)
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
