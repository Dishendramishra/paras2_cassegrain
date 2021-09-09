class test:

    def __init__(self):

        self.var = "on"

    def change(self, var):
        var = "off"

    def run(self):
        print("before: ",self.var)
        self.change(self.var)
        print("after: ",self.var)

t = test()
t.run()