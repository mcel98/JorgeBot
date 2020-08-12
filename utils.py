class consulta:
    def __init__(self, tiempo, id ,status):
        self.id = id
        self.tiempo = tiempo
        self.status = status

    def cambiar_status(self,status):
        if self.status == 'activo':
            self.status = status

    def status(self):
        return self.status


class pqueue:
    def __init__(self):
        self.queue = []
        self.pausa = []
        self.size = 0

    def size(self):
        return self.size

    def p(self,i):
        return (i-1)/2

    def left(self, i):
        return 2 * i + 1

    def right(self, i):
        return 2 * i + 2

    def insertar_consulta(self,consulta):

        if consulta.status == 'activo':
            self.size += 1
            i = self.size - 1
            self.queue.append(consulta)
            consulta.cambiar_status('denegado')
            while i != 0 and self.queue[self.p(i)].tiempo > self.queue[i].tiempo and self.queue[self.p(i)].status != 'pausa':
                self.queue[i],self.queue[self.p(i)] = self.queue[self.p(i)],self.queue[i]
                i = self.p(i)
            return

        elif consulta.status == 'pausa':
            self.size += 1
            i = self.size - 1
            consulta.tiempo = self.queue[0].tiempo
            consulta.cambiar_status('denegado')
            self.queue.append(consulta)
            while i != 0 and self.queue[self.p(i)].tiempo > self.queue[0].tiempo:
                self.queue[i], self.queue[self.p(i)] = self.queue[self.p(i)], self.queue[i]
                i = self.p(i)
            return
        else:
            return

    def decKey(self,id,val):
        k = 0
        for i in self.queue:
            if i.id != id:
                k += 1
        if k == self.size:
            return
        else:
            self.queue[k].tiempo = val
            while(self.queue[self.p(k)].tiempo > self.queue[k].tiempo):
                self.queue[k], self.queue[self.p(k)] = self.queue[self.p(k)], self.queue[k]
                k = self.p(k)

    def delete(self, id):
        self.decKey(id,float("-inf"))
        self.atender()


    def alcostado(self):
        if self.size <= 0:
            return
        if self.size == 1:
            self.size -= 1
            self.queue[0].cambiar_status('denegado')
            res = self.queue[0]
            self.queue.pop()
            return res
        else:
            res = self.queue[0]
            self.pausa.append(res)
            self.queue[0] = self.queue[self.size -1]
            self.queue.pop()
            self.size -=1
            self.Heapify(0)
            return res

    def atender(self):
        if self.size == 0:
            return 0
        if self.size == 1:
            self.size -= 1
            self.queue[0].cambiar_status('denegado')
            res = self.queue[0].id
            self.queue.pop()
            return res
        else:
            res = self.queue[0].id
            self.queue[0] = self.queue[self.size -1]
            self.queue.pop()
            self.size -=1
            self.Heapify(0)
            return res

    def Heapify(self,i):
        l = self.left(i)
        r = self.right(i)
        s = i

        if l < self.size and self.queue[l].tiempo < self.queue[i]:
            s = l
        if r < self.size and self.queue[r].tiempo < self.queue[i]:
            s = r
        if s != i:
            self.queue[i], self.queue[s] = self.queue[s],self.queue[i]
            self.Heapify(s)
