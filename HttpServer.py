import tornado.web
import tornado.ioloop
import os
import Procmon


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        p = Procmon.Procmon()
        p.getProcInfo(1)
        self.write(p.onRequest())

class PicHandler(tornado.web.RequestHandler):
    def get(self):
        p = Procmon.Procmon()
        for i in range(500):
           p.getCpuUsage()
           p.getCpuImage()
           f = open('cpu.png','rb')
           self.write(f.read())
           self.set_header("Content-type", "image/png")
           self.flush()


if __name__ == '__main__':
    app = tornado.web.Application([(r'/',IndexHandler),(r'/cpu.png',PicHandler)])
    app.listen(1080)
    tornado.ioloop.IOLoop.current().start()
