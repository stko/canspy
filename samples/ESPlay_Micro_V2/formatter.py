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

class BitArray:
    '''
    This is just an empty class to emulate the real Bitstring Library https://pypi.org/project/bitstring/
    which hast too much dependencies and too much overloads as to be senseful used here in Micropython
    '''
    def __init__(self, data):
        if data is str: # we simply assume the string has the format '0b....' and represents a binay number
            self.data=data[2:]
        elif data is bytearray:
            self.data=""
            for b in data:
                self.data+=bin(b)[2:]
        else:
            print("unknown data type ")
    
    def to_bytes(self): # https://stackoverflow.com/a/32676625
        return int(self.data, 2).to_bytes((len(self.data) + 7) // 8, byteorder='big')

class Formatter(dict):

    def __init__(self,bus_name):
        super().__init__()
        self.module=''
        self.bus_name=bus_name
        self.header=bus_name
        self.internal_hash={}
        ## just for test
        self.known_messages={
            "Modul A1" : {
                0x6A8 : {
                    "title": "Voltage",
                    "format": "f:0:16:1:10:0:V"
                },
                0x0195 : {
                    "title": "Speed",
                    "format": "f:0:16:1:10:0:V"
                },
                0x02BD: {
                    "title": "#",
                    "format": ""
                }
            },
            "Modul A88" : {
                0x751 : {
                    "title": "Loaded",
                    "format": "f:0:16:1:10:0:V"
                },
                0x0032 : {
                    "title": "Range",
                    "format": "f:0:16:1:10:0:V"
                },
                0x0FD: {
                    "title": "#",
                    "format": ""
                }
            },
            "#" : {
                0x425 : {
                    "title": "foo",
                    "format": "foo"
                },
                0x036 : {
                    "title": "foo",
                    "format": "foo"
                }
            }
        }
        
    def format(self,id,data_bytes,format_str=""):
        # reformat the id input to be compatible with the  format_msgs function copied from labdash 
        return self.format_msgs(data_bytes,"{:04x} ::".format(id).upper()+format_str)

    # routine taken from LabDash: https://github.com/stko/labdash/blob/master/labdash/ldmclass.py#L112
    def format_msgs(self,data_bytes, id):
        [can_id_string, timeout, format_str] =id.split(':',2)
        if not data_bytes:
            return '-', None
        if not format_str:
            return can_id_string + "".join(["{:02x}".format(x) for x in data_bytes]).upper() ,None
        [data_type, bit_pos, bit_len, mult, div, offset,unit] = format_str.split(':')
        bit_pos=int(bit_pos)
        bit_len=int(bit_len)
        mult=float(mult)
        div=float(div)
        offset=float(offset)
        # length check
        if data_type != 'a':
            if bit_pos//8+bit_len//8 > len(data_bytes):
                return 'message data too short', None
        # test, if we can use faster byte oriented methods or bit-wise, but slower bitstring operations
        if bit_pos % 8 == 0  and bit_len % 8 == 0:
            message_data_bytes=data_bytes[bit_pos//8:bit_pos//8+bit_len//8]
        else:
            message_data_bytes=BitArray(data_bytes)
            message_data_bytes=message_data_bytes[bit_pos:bit_pos+bit_len]
            if bit_len % 8 != 0 : # we need to do padding :-(
                # first we need the numpber of leading padding bits
                padding_string="0b"+"0"*(8 - (bit_len % 8))
                padding_bits=BitArray(padding_string)
                padding_bits.append(message_data_bytes)
                message_data_bytes=padding_bits.tobytes()
            else:
                message_data_bytes=message_data_bytes.tobytes()

        if data_type=='f':
            raw =int.from_bytes(message_data_bytes, 'big')*mult/div+offset
            return str(raw)+unit , raw 
        if data_type=='a':
            bytearray_message=bytearray(message_data_bytes)
            return bytearray_message.decode("utf-8"), bytearray_message
        else:
            return 'unknown data type in format_str' ,None

    def clear_all(self):
        self.clear()
        self.internal_hash.clear()
        
    def get_module(self,id):
        for module_name,module_telegrams in self.known_messages.items():
            for telegram_id in module_telegrams:
                if telegram_id==id:
                    if module_name == "#": # supress ids which do belong to the dummy module '#'
                        return None
                    else:
                        return module_name
        return "{:04x}".format(id).upper()

    def new_content(self,telegrams):
        ids=list(telegrams.keys())
        ids.sort()
        for id in ids:
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
            print("module:",self.module)
            if self.module not in self.known_messages: # the user has selected a undescripted id
                id =int(self.module,16) # we need to convert the id string back to its int value to adress the array with it
                text, _ =self.format(id,self.internal_hash[id].data)
                self[self.module]=FormatTelegram(self.internal_hash[id].new,text)
            else:
                for id, data in self.known_messages[self.module].items():
                    if data["title"]=="#": # we ignore this id in the output
                        continue
                    if id not in self.internal_hash: # we did not received that known id yet
                        continue
                    text, _ =self.format(id,self.internal_hash[id].data,data["format"])
                    self[id]=FormatTelegram(self.internal_hash[id].new,data["title"]+": "+text)
        else:
            self.header=self.bus_name
            for id in ids: # create new sorted output
                module_name=self.get_module(id)
                if not module_name: # its None when we want to supress that id
                    continue
                if module_name in self: # the module is already in the list
                    continue 
                self[module_name]=FormatTelegram(self.internal_hash[id].new,module_name)

