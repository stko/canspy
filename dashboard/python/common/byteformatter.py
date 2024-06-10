    # some convience methods


# just a copy, original is on https://github.com/stko/labdash/blob/master/labdash/utils/byteformatter.py

from bitstring import BitArray  # nice module for bit wise operations

def format_msgs(data_bytes, format_str):
    """
    format types:
    a: ASCII
    f: float
    e: enum : The calculated value is used as index for the different texts which are stored in the Unit field, seperated by &
    b: binary

    all formats are also exist as j.. (ja, jf..), where the leading j indicates that the data type is j1939, which has special
    formats, ranges and error indications

    """
    if not data_bytes:
        return "-"
    [data_type, bit_pos, bit_len, mult, div, offset, unit] = format_str.split(":",6)
    bit_pos = int(bit_pos)
    bit_len = int(bit_len)
    mult = float(mult)
    div = float(div)
    offset = float(offset)
    # length check
    if data_type != "a":
        if bit_pos // 8 + bit_len // 8 > len(data_bytes):
            return "message data too short",0
    # test, if we can use faster byte oriented methods or bit-wise, but slower bitstring operations
    if bit_pos % 8 == 0 and bit_len % 8 == 0:
        message_data_bytes = data_bytes[bit_pos // 8 : bit_pos // 8 + bit_len // 8]
    else:
        message_data_bytes = BitArray(data_bytes)
        print(str(message_data_bytes.b))
        message_data_bytes = message_data_bytes[bit_pos : bit_pos + bit_len]
        if bit_len % 8 != 0:  # we need to do padding :-(
            # first we need the numpber of leading padding bits
            padding_string = "0b" + "0" * (8 - (bit_len % 8))
            padding_bits = BitArray(padding_string)
            padding_bits.append(message_data_bytes)
            message_data_bytes = padding_bits.tobytes()
        else:
            message_data_bytes = message_data_bytes.tobytes()

    if data_type == "fb":
        raw = (
            int.from_bytes(message_data_bytes, byteorder="big", signed=False)
            * mult
            / div
            + offset
        )
        return str(raw) + unit, raw
    if data_type == "fl":
        raw = (
            int.from_bytes(message_data_bytes, byteorder="little", signed=False)
            * mult
            / div
            + offset
        )
        return str(raw) + unit, raw
    if data_type == "b":
        raw = message_data_bytes !=  b'\x00'
        values = unit.split("&")
        if raw:
            value = values[1]
        else:
            value = values[0]
        return value, raw
    if data_type == "a":
        bytearray_message = bytearray(message_data_bytes)
        return bytearray_message.decode("utf-8"), bytearray_message
    return "unknown data type in format_str", None
