'''formats the texts to show out of the received telegrams and the previous texts'''

class Telegram:
    def __init__(self, id, data):
        self.id=id
        self.update(data)

    def update(self, data):
        self.new=True
        self.data = data

class FormatTelegram:
    def __init__(self,new,text) -> None:
        self.new=new
        self.text=text



class Formatter(dict):

    def __init__(self,bus_name):
        super().__init__()
        self.module=''
        self.bus_name=bus_name
        self.header=bus_name
        self.internal_hash={}
        self.ignored_ids=[]



    def format(self, id, data):
        return "{:04x}".format(id).upper() + " " + "".join(["{:02x}".format(x) for x in data[:6]]).upper()

    def clear_all(self):
        self.clear()
        self.internal_hash.clear()
        
    def is_id_of_module(self, module, id): # true if id belongs to module
        return True

    def get_title(self,id):
        return "bla"

    def get_module(self,id):
        return id

    def new_content(self,telegrams):
        ids=list(telegrams.keys())
        ids.sort()
        for id in ids:
            if id in self.ignored_ids: # we don't want this id to be shown
                continue
            if id in self.internal_hash:
                self.internal_hash[id].update(telegrams[id])
            else:
                self.internal_hash[id]=Telegram(id,telegrams[id])
        # now we re-create ourself
        ids=list(self.internal_hash.keys())
        ids.sort()
        self.clear()
        if self.module: # we'll create a list of the signals of a single module
            self.header=self.module
            for id in ids: # create new sorted output
                if not self.is_id_of_module(self.module,id):
                    continue
                title=self.gettitle(id)
                self[title]=FormatTelegram(self.internal_hash[id].new,self.format(id,self.internal_hash[id].data))

        else:
            self.header=self.bus_name
            for id in ids: # create new sorted output
                module_name=self.get_module(id)
                if module_name in self: # the module is already in the list
                    continue 
                self[module_name]=FormatTelegram(self.internal_hash[id].new,"")

