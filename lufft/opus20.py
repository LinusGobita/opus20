#!/usr/bin/env python

import socket
import pdb
import struct
import time
import logging

logger = logging.getLogger(__name__)

class Opus20(object):

    def __init__(self, host, port=52015, timeout=0.25):

        self.host = host
        self.port = port

        self.s = socket.create_connection((self.host, self.port), timeout)

        self.request_supported_channels()

    def request_supported_channels(self):
        frame = Frame.from_cmd_and_payload(0x31, b"\x16")
        answer = self.query_frame(frame)
        self.available_channels = answer.available_channels()

    def channel_value(self, channel: int):
        query_frame = Frame.from_cmd_and_payload(0x23, struct.pack('<H', channel))
        answer_frame = self.query_frame(query_frame)
        return answer_frame.online_data_request_single()

    def query_frame(self, frame):
        assert type(frame) == Frame
        return self.query_bytes(frame.data)

    def query_bytes(self, data : bytes):
        logger.info("Sending the following {} bytes now: {}".format(len(data), hex_formatter(data)))
        frame = None
        num_tries = 3
        while num_tries:
            try:
                self.s.sendall(data)
                answer = self.s.recv(1024)
                frame = Frame(answer)
                frame.validate()
                break
            except IncompleteDataException:
                logger.info("received incomplete data; trying to get the remaining bytes.")
                answer += self.s.recv(1024)
                frame = Frame(answer)
                frame.validate()
                break
            except FrameValidationException as e:
                logger.warning("The frame couldn't be validated: " + str(e))
            num_tries -= 1
            logger.warning("remaining tries: {}".format(num_tries))
        if not frame: raise NameError("Couldn't get a valid answer.")
        logger.info("Received the following {} bytes as answer: {}".format(len(frame.data), hex_formatter(frame.data)))
        return frame

    def close(self):
        self.s.close()

class Opus20Exception(NameError):
    """ An exception concerning Opu20 """

class FrameValidationException(Opus20Exception):
    """ received invalid data """

class IncompleteDataException(FrameValidationException):
    """ received incomplete data """

class Frame(object):

    HEADER_SHORT = b"\x01\x10\x00\x00\x00\x00"
    HEADER_LONG = b"\x01\x20\x00\x00\x00\x00"

    STX = b"\x02"
    ETX = b"\x03"
    EOT = b"\x04"
    SHORT_FRAME = 0x10
    LONG_FRAME  = 0x20

    def __init__(self, data=bytes()):
        self.data = data

    @classmethod
    def from_cmd_and_payload(cls, cmd, payload, verc=0x10):
        data = cls.HEADER_SHORT
        data += bytes([2+len(payload)])
        data += cls.STX
        data += bytes([cmd, verc]) + payload
        data += cls.ETX
        crc = crc16(data)
        # The byte order is LO HI
        data += bytes([crc & 0xFF, crc >> 8])
        data += cls.EOT

        frame = Frame()
        frame.data = data
        return frame

    def validate(self):

        data = self.data

        if len(data) < 12:
            logger.info("message incomplete? Expected at least 12 bytes, got {}. ".format(len(data)))
            raise IncompleteDataException()

        frame_style = None
        offset = 0
        # check header
        if data[0:6] == self.HEADER_SHORT:
            frame_style = self.SHORT_FRAME
        elif data[0:6] == self.HEADER_LONG:
            frame_style = self.LONG_FRAME
        else:
            raise FrameValidationException("l2p-header incorrect: " + str(data[0:6]))

        # length of payload
        length = 0
        if frame_style == self.SHORT_FRAME:
            length = data[6]
        elif frame_style == self.LONG_FRAME:
            length = struct.unpack('<H', data[6:8])[0]
            offset += 1
        logger.debug("length of payload={}".format(length))
        if len(data) < 12 + offset + length:
            # This 'problem' can occur regularly, thus we don't use .warning() but .info()
            logger.info("message incomplete? Expected {} bytes, got {}. ".format(12+length, len(data)) + str(data))
            raise IncompleteDataException()

        # stx ok?
        if data[7+offset] != 0x02: raise FrameValidationException("l2p-stx incorrect")

        # cmd/verc
        cmd = data[8+offset]
        verc = data[9+offset]
        logger.debug("CMD=[0x{:02X}] VERC=[0x{:02X}]".format(cmd, verc))

        # payload
        payload = data[10+offset:10+offset+length-2]
        logger.debug("Payload=[" + hex_formatter(payload) + "]")

        # etx ok?
        if data[8+offset+length] != 0x03: raise FrameValidationException("l2p-etx incorrect")

        # chksum ok?
        frame = data[0:9+offset+length]
        chksum_calc = crc16(frame)
        # The byte order is LO HI
        chksum_calc = bytes([chksum_calc & 0xFF, chksum_calc >> 8])
        chksum_found = data[9+offset+length:9+offset+length+2]
        if chksum_calc != chksum_found:
            logger.warning("Checksum: WRONG!")
            raise FrameValidationException("l2p chksum incorrect: {} vs. {}".format(chksum_calc, chksum_found))
        else:
            logger.debug("Checksum: OK")

        # eot ok?
        if data[11+offset+length] != 0x04: raise FrameValidationException("l2p-eot incorrect")

        props = Object()
        props.cmd = cmd
        props.verc = verc
        props.length = length
        props.payload = payload
        props.frame_style = frame_style
        props.chksum_found = chksum_found
        self._props = props

        return True

    @property
    def status(self):
        return self.props.payload[0]

    def assert_status(self):
        # check the status byte
        status = self.status
        if status == 0x0:
            logger.debug("Status: {}".format(STATUS_WORDS[status]))
            return True
        else:
            logger.warning("Status: {}".format(STATUS_WORDS[status]))
            msg = 'status not ok: 0x{:02X}'.format(status)
            if status in STATUS_WORDS: msg += ' error code: {}'.format(STATUS_WORDS[status]['name'])
            else: msg += ' error code: unknown'
            raise NameError(msg)

    @property
    def props(self):
        """ returns an object containing the basic properties of the Frame.
            This object is created when calling Frame.validate() . """
        try:
            return self._props
        except:
            raise NameError('Props not available yet. Check Frame.validate() first.')


    @property
    def kind(self):
        FRAME_KINDS = [
          #
          Object(cmd=0x1E, payload_check=[],            payload_length=   0, name='network discovery request'),
          Object(cmd=0x1E, payload_check=[],            payload_length=  35, name='network discovery answer'),
          #
          Object(cmd=0x23, payload_check=[],            payload_length=   2, name='online single channel request'),
          Object(cmd=0x23, payload_check=[0x00,],       payload_length=   8, name='online single channel answer',               func=self.online_data_request_single),
          #
          Object(cmd=0x24, payload_check=[0x10,],       payload_length=  10, name='initiate log download request'),
          Object(cmd=0x24, payload_check=[0x00, 0x10],  payload_length=  10, name='initiate log download answer'),
          #
          Object(cmd=0x24, payload_check=[0x20, 0x01],  payload_length=   2, name='log download data request'),
          Object(cmd=0x24, payload_check=[0x00, 0x20],  payload_length=None, name='log download data answer'),
          #
          Object(cmd=0x27, payload_check=[],            payload_length=   8, name='update time request'),
          Object(cmd=0x27, payload_check=[0x00,],       payload_length=   1, name='update time answer'),
          #
          Object(cmd=0x2F, payload_check=[],            payload_length=   2, name='online multiple channel request'),
          Object(cmd=0x2F, payload_check=[0x00,],       payload_length=None, name='online multiple channel answer',             func=self.online_data_request_multiple),
          #
          Object(cmd=0x31, payload_check=[0x16,],       payload_length=   1, name='channel list request'),
          Object(cmd=0x31, payload_check=[0x00, 0x16,], payload_length=None, name='channel list answer',                        func=self.available_channels),
          #
          Object(cmd=0x31, payload_check=[0x17,],       payload_length=   1, name='channel group list request'),
          Object(cmd=0x31, payload_check=[0x00, 0x17,], payload_length=None, name='channel group list answer'),
          #
          Object(cmd=0x31, payload_check=[0x30,],       payload_length=   3, name='information on specific channel request'),
          Object(cmd=0x31, payload_check=[0x00, 0x30,], payload_length=  85, name='information on specific channel answer'),
          #
          Object(cmd=0x31, payload_check=[0x10,],       payload_length=   1, name='advanced status request 0x10 (?)'),
          Object(cmd=0x31, payload_check=[0x00, 0x10,], payload_length=None, name='advanced status answer 0x10 (?)'),
          #
          Object(cmd=0x31, payload_check=[0x13,],       payload_length=   1, name='advanced status request 0x13 (?)'),
          Object(cmd=0x31, payload_check=[0x00, 0x13,], payload_length=None, name='advanced status answer 0x13 (?)'),
          #
          Object(cmd=0x31, payload_check=[0x60,],       payload_length=   1, name='device status request'),
          Object(cmd=0x31, payload_check=[0x00, 0x60,], payload_length=  10, name='device status answer'),
          #
          Object(cmd=0x44, payload_check=[0x12,],       payload_length=   2, name='[r] value range of channel group request'),
          Object(cmd=0x44, payload_check=[0x00, 0x12],  payload_length=  18, name='[r] value range of channel group answer'),
          #
          Object(cmd=0x44, payload_check=[0x22,],       payload_length=   3, name='[r] enable/disable logging of specific channel request'),
          Object(cmd=0x44, payload_check=[0x00, 0x22],  payload_length=   5, name='[r] enable/disable logging of specific channel answer'),
          Object(cmd=0x45, payload_check=[0x22,],       payload_length=   4, name='[w] enable/disable logging of specific channel request'),
          Object(cmd=0x45, payload_check=[0x00, 0x22],  payload_length=   6, name='[w] enable/disable logging of specific channel answer'),
          #
          Object(cmd=0x44, payload_check=[0x41,],       payload_length=   1, name='[r] measuring/logging interval request'),
          Object(cmd=0x44, payload_check=[0x00, 0x41],  payload_length=  14, name='[r] measuring/logging interval answer'),
          Object(cmd=0x45, payload_check=[0x41,],       payload_length=   9, name='[w] measuring/logging interval request'),
          Object(cmd=0x45, payload_check=[0x00, 0x41],  payload_length=   8, name='[w] measuring/logging interval answer'),
          #
          Object(cmd=0x44, payload_check=[0x43,],       payload_length=   1, name='[r] enable/disable logging request'),
          Object(cmd=0x44, payload_check=[0x00, 0x43],  payload_length=   3, name='[r] enable/disable logging answer'),
          Object(cmd=0x45, payload_check=[0x43,],       payload_length=   2, name='[w] enable/disable logging request'),
          Object(cmd=0x45, payload_check=[0x00,],       payload_length=   1, name='[w] enable/disable logging answer'),
          #
          Object(cmd=0x46, payload_check=[],            payload_length=   0, name='clear log request'),
          Object(cmd=0x46, payload_check=[0x00,],       payload_length=   1, name='clear log answer'),
          #
          ## Commands I don't understand right now:
          # 31/31 : channel group specific, a 2+1+1+n-byte answer, the n-bytes are counting upwards
          # 44/11 : channel group specific, a 2+1+1-byte answer (single flat?)
          # 44/13 : channel group specific, a 2+1+1+4-byte answer with a float value of 0.0
          # 44/21 : channel group specific, 2+81-byte answer with mostly 0x00 values
          # 44/31 : global, 2+80-byte answer with mostly 0x00 values
          # 44/61 : global, a 2+1-byte answer with 0x00 (single flag?)
          # 44/62 : global, a 2+1-byte answer with 0x00 (single flag?)
          # 44/70 : global, a 2+2-byte answer with 0x00 0x00
          # 44/81 : global, contains the device ID like 31/60
        ]

        props = self.props

        # all frames I have seen so far use verc = 0x10
        if props.verc != 0x10: return None

        for knd in FRAME_KINDS:
            if knd.cmd != props.cmd: continue
            if knd.payload_length != None and knd.payload_length != len(props.payload):
                continue
            if len(knd.payload_check) > len(props.payload): continue
            payload_matches = True
            for i in range(len(knd.payload_check)):
                ref_byte = knd.payload_check[i]
                check_byte = props.payload[i]
                if ref_byte != None and ref_byte != check_byte:
                    payload_matches = False
                    break
            if payload_matches: return knd
        return None

    def available_channels(self):
        # cmd="31 10" (which channels are available in device?)

        props = self.props

        assert props.length >= 3, 'message too short for an answer containing the available channels'
        assert props.cmd == 0x31 and props.verc == 0x10 and  props.payload[1] == 0x16
        self.assert_status()

        logger.debug("Channel Query (31 10 16)")
        num_channels = props.payload[2]
        logger.debug("Number of available channels: {}".format(num_channels))
        channels = []
        for i in range(num_channels):
            # Little Endian 16 bit:
            channel = props.payload[3+2*i:3+2*i+2]
            channel = channel[0] + (channel[1] << 8 )
            if channel not in CHANNEL_SPEC:
                # This is the case for channel 150 = 0x0096
                continue
            channels.append(channel)
        return channels

    def online_data_request_single(self):
        # cmd="23 10" (online data request, one channel)

        props = self.props

        assert props.length >= 3, 'message too short for an online data request with a single channel'
        assert props.cmd == 0x23 and props.verc == 0x10
        self.assert_status()
        logger.debug("Online Data Request (single channel) (23 10)")
        channel = props.payload[1] + (props.payload[2] << 8)
        logger.debug("Channel={}: {}".format(channel, CHANNEL_SPEC[channel]))

        dtype = props.payload[3]
        logger.debug("DataType=[0x{:02X}]".format(dtype))
        if dtype == 0x16:
            value = struct.unpack('<f', props.payload[4:4+4])[0]
        else:
            raise NameError("Data type 0x{:02X} not implemented".format(dtype))
        logger.info("Returned Value: " + str(value))


        return value

    def online_data_request_multiple(self):
        # cmd="2F 10" (online data request, multiple channels)

        props = self.props

        assert props.length >= 3, 'message too short for an online data request with multiple channels'
        assert props.cmd == 0x2F and props.verc == 0x10
        self.assert_status()
        logger.debug("Online Data Request (multiple channels) (2F 10)")

        offset = 1
        num_channels = props.payload[offset]
        logger.debug("Number of Channels={}".format(num_channels))
        offset += 1

        values = []

        for i in range(num_channels):
            sub_length = props.payload[offset]
            logger.debug("SubLen={} ({})".format(sub_length, offset))
            sub_payload = props.payload[offset:offset+1+sub_length]
            logger.debug("SubPayload: " + hex_formatter(sub_payload))
            offset += 1

            sub_status = props.payload[offset]
            logger.debug("SubStatus={}: ({})".format(sub_status, offset))
            offset += 1
            if sub_status != 0: continue

            channel = props.payload[offset] + (props.payload[offset+1] << 8)
            logger.info("channel: {} ({:04X}) {}".format(channel, channel, CHANNEL_SPEC[channel]))
            offset += 2

            dtype = props.payload[offset]
            logger.debug("DataType=[0x{:02X}]".format(dtype))
            offset += 1
            if dtype == 0x16:
                value = struct.unpack('<f', props.payload[offset:offset+4])[0]
                offset += 4
            else:
                raise NameError("Data type 0x{:02X} not implemented".format(dtype))
            logger.info("Returned Value: " + str(value))

            values.append(value)

        return values


def hex_formatter(raw: bytes):
    return ' '.join('{:02X}'.format(byte) for byte in raw)


def crc16(data : bytes):
    """ Calculates a CRC-16 CCITT checksum. data should be of type bytes() """
    # https://en.wikipedia.org/wiki/Cyclic_redundancy_check
    crc16_table = [
        0x0000, 0x1189, 0x2312, 0x329B, 0x4624, 0x57AD, 0x6536, 0x74BF,
        0x8C48, 0x9DC1, 0xAF5A, 0xBED3, 0xCA6C, 0xDBE5, 0xE97E, 0xF8F7,
        0x1081, 0x0108, 0x3393, 0x221A, 0x56A5, 0x472C, 0x75B7, 0x643E,
        0x9CC9, 0x8D40, 0xBFDB, 0xAE52, 0xDAED, 0xCB64, 0xF9FF, 0xE876,
        0x2102, 0x308B, 0x0210, 0x1399, 0x6726, 0x76AF, 0x4434, 0x55BD,
        0xAD4A, 0xBCC3, 0x8E58, 0x9FD1, 0xEB6E, 0xFAE7, 0xC87C, 0xD9F5,
        0x3183, 0x200A, 0x1291, 0x0318, 0x77A7, 0x662E, 0x54B5, 0x453C,
        0xBDCB, 0xAC42, 0x9ED9, 0x8F50, 0xFBEF, 0xEA66, 0xD8FD, 0xC974,
        0x4204, 0x538D, 0x6116, 0x709F, 0x0420, 0x15A9, 0x2732, 0x36BB,
        0xCE4C, 0xDFC5, 0xED5E, 0xFCD7, 0x8868, 0x99E1, 0xAB7A, 0xBAF3,
        0x5285, 0x430C, 0x7197, 0x601E, 0x14A1, 0x0528, 0x37B3, 0x263A,
        0xDECD, 0xCF44, 0xFDDF, 0xEC56, 0x98E9, 0x8960, 0xBBFB, 0xAA72,
        0x6306, 0x728F, 0x4014, 0x519D, 0x2522, 0x34AB, 0x0630, 0x17B9,
        0xEF4E, 0xFEC7, 0xCC5C, 0xDDD5, 0xA96A, 0xB8E3, 0x8A78, 0x9BF1,
        0x7387, 0x620E, 0x5095, 0x411C, 0x35A3, 0x242A, 0x16B1, 0x0738,
        0xFFCF, 0xEE46, 0xDCDD, 0xCD54, 0xB9EB, 0xA862, 0x9AF9, 0x8B70,
        0x8408, 0x9581, 0xA71A, 0xB693, 0xC22C, 0xD3A5, 0xE13E, 0xF0B7,
        0x0840, 0x19C9, 0x2B52, 0x3ADB, 0x4E64, 0x5FED, 0x6D76, 0x7CFF,
        0x9489, 0x8500, 0xB79B, 0xA612, 0xD2AD, 0xC324, 0xF1BF, 0xE036,
        0x18C1, 0x0948, 0x3BD3, 0x2A5A, 0x5EE5, 0x4F6C, 0x7DF7, 0x6C7E,
        0xA50A, 0xB483, 0x8618, 0x9791, 0xE32E, 0xF2A7, 0xC03C, 0xD1B5,
        0x2942, 0x38CB, 0x0A50, 0x1BD9, 0x6F66, 0x7EEF, 0x4C74, 0x5DFD,
        0xB58B, 0xA402, 0x9699, 0x8710, 0xF3AF, 0xE226, 0xD0BD, 0xC134,
        0x39C3, 0x284A, 0x1AD1, 0x0B58, 0x7FE7, 0x6E6E, 0x5CF5, 0x4D7C,
        0xC60C, 0xD785, 0xE51E, 0xF497, 0x8028, 0x91A1, 0xA33A, 0xB2B3,
        0x4A44, 0x5BCD, 0x6956, 0x78DF, 0x0C60, 0x1DE9, 0x2F72, 0x3EFB,
        0xD68D, 0xC704, 0xF59F, 0xE416, 0x90A9, 0x8120, 0xB3BB, 0xA232,
        0x5AC5, 0x4B4C, 0x79D7, 0x685E, 0x1CE1, 0x0D68, 0x3FF3, 0x2E7A,
        0xE70E, 0xF687, 0xC41C, 0xD595, 0xA12A, 0xB0A3, 0x8238, 0x93B1,
        0x6B46, 0x7ACF, 0x4854, 0x59DD, 0x2D62, 0x3CEB, 0x0E70, 0x1FF9,
        0xF78F, 0xE606, 0xD49D, 0xC514, 0xB1AB, 0xA022, 0x92B9, 0x8330,
        0x7BC7, 0x6A4E, 0x58D5, 0x495C, 0x3DE3, 0x2C6A, 0x1EF1, 0x0F78,
    ]
    crc_buff = 0xffff
    for i in range(len(data)):
        c = data[i]
        crc_buff = (crc_buff >> 8) ^ crc16_table[ (c ^ ( crc_buff & 0xFF )) ]
    return crc_buff

CHANNEL_SPEC = {
  100:   "CUR temperature       min=-20.0  max=50.0   unit=°C   type=FLOAT offset=±10.0",
  120:   "MIN temperature       min=-20.0  max=50.0   unit=°C   type=FLOAT offset=±10.0",
  140:   "MAX temperature       min=-20.0  max=50.0   unit=°C   type=FLOAT offset=±10.0",
  160:   "AVG temperature       min=-20.0  max=50.0   unit=°C   type=FLOAT offset=±10.0",
  105:   "CUR temperature       min=-4.0   max=122.0  unit=°F   type=FLOAT offset=0.0",
  125:   "MIN temperature       min=-4.0   max=122.0  unit=°F   type=FLOAT offset=0.0",
  145:   "MAX temperature       min=-4.0   max=122.0  unit=°F   type=FLOAT offset=0.0",
  165:   "AVG temperature       min=-4.0   max=122.0  unit=°F   type=FLOAT offset=0.0",
  110:   "CUR dewpoint          min=-85.0  max=50.0   unit=°C   type=FLOAT offset=0.0",
  130:   "MIN dewpoint          min=-85.0  max=50.0   unit=°C   type=FLOAT offset=0.0",
  150:   "MAX dewpoint          min=-85.0  max=50.0   unit=°C   type=FLOAT offset=0.0",
  170:   "AVG dewpoint          min=-85.0  max=50.0   unit=°C   type=FLOAT offset=0.0",
  115:   "CUR dewpoint          min=-121.0 max=122.0  unit=°F   type=FLOAT offset=0.0",
  135:   "MIN dewpoint          min=-121.0 max=122.0  unit=°F   type=FLOAT offset=0.0",
  155:   "MAX dewpoint          min=-121.0 max=122.0  unit=°F   type=FLOAT offset=0.0",
  175:   "AVG dewpoint          min=-121.0 max=122.0  unit=°F   type=FLOAT offset=0.0",
  200:   "CUR relative_humidity min=0.0    max=100.0  unit=%    type=FLOAT offset=±30.0",
  220:   "MIN relative_humidity min=0.0    max=100.0  unit=%    type=FLOAT offset=±30.0",
  240:   "MAX relative_humidity min=0.0    max=100.0  unit=%    type=FLOAT offset=±30.0",
  260:   "AVG relative_humidity min=0.0    max=100.0  unit=%    type=FLOAT offset=±30.0",
  205:   "CUR absolute_humidity min=0.0    max=85.0   unit=g/m³ type=FLOAT offset=0.0",
  225:   "MIN absolute_humidity min=0.0    max=85.0   unit=g/m³ type=FLOAT offset=0.0",
  245:   "MAX absolute_humidity min=0.0    max=85.0   unit=g/m³ type=FLOAT offset=0.0",
  265:   "AVG absolute_humidity min=0.0    max=85.0   unit=g/m³ type=FLOAT offset=0.0",
  300:   "CUR abs. air pressure min=300.0  max=1200.0 unit=hPa  type=FLOAT offset=±10.0",
  320:   "MIN abs. air pressure min=300.0  max=1200.0 unit=hPa  type=FLOAT offset=±10.0",
  340:   "MAX abs. air pressure min=300.0  max=1200.0 unit=hPa  type=FLOAT offset=±10.0",
  360:   "AVG abs. air pressure min=300.0  max=1200.0 unit=hPa  type=FLOAT offset=±10.0",
  305:   "CUR abs. air pressure min=300.0  max=1200.0 unit=hPa  type=FLOAT offset=0.0",
  325:   "MIN abs. air pressure min=300.0  max=1200.0 unit=hPa  type=FLOAT offset=0.0",
  345:   "MAX abs. air pressure min=300.0  max=1200.0 unit=hPa  type=FLOAT offset=0.0",
  365:   "AVG abs. air pressure min=300.0  max=1200.0 unit=hPa  type=FLOAT offset=0.0",
  10020: "CUR battery voltage   min=0.0    max=6.5    unit=V    type=FLOAT offset=0.0",
  10040: "MIN battery voltage   min=0.0    max=6.5    unit=V    type=FLOAT offset=0.0",
  10060: "MAX battery voltage   min=0.0    max=6.5    unit=V    type=FLOAT offset=0.0",
  10080: "AVG battery voltage   min=0.0    max=6.5    unit=V    type=FLOAT offset=0.0",
}
STATUS_WORDS = {
  0x00: {'name': "OK",                 'descr': "command successful"},
  0x10: {'name': "UNKNOWN_CMD",        'descr': "unknown command"},
  0x11: {'name': "INVALID_PARAM",      'descr': "invalid parameter"},
  0x12: {'name': "INVALID_HEADER",     'descr': "invalid header version"},
  0x13: {'name': "INVALID_VERC",       'descr': "invalid verion of the command"},
  0x14: {'name': "INVALID_PW",         'descr': "invalid password for command"},
  0x20: {'name': "READ_ERR",           'descr': "read error"},
  0x21: {'name': "WRITE_ERR",          'descr': "write error"},
  0x22: {'name': "TOO_LONG",           'descr': "too long"},
  0x23: {'name': "INVALID_ADDRESS",    'descr': "invalid address"},
  0x24: {'name': "INVALID_CHANNEL",    'descr': "invalid channel"},
  0x25: {'name': "INVALID_CMD",        'descr': "command not possible in this mode"},
  0x26: {'name': "UNKNOWN_CAL_CMD",    'descr': "unknown calibration command"},
  0x27: {'name': "CAL_ERROR",          'descr': "calibration error"},
  0x28: {'name': "BUSY",               'descr': "busy"},
  0x29: {'name': "LOW_VOLTAGE",        'descr': "low voltage"},
  0x2A: {'name': "HW_ERROR",           'descr': "hardware error"},
  0x2B: {'name': "MEAS_ERROR",         'descr': "measurement error"},
  0x2C: {'name': "INIT_ERROR",         'descr': "device initialization error"},
  0x2D: {'name': "OS_ERROR",           'descr': "operating system error"},
  0x30: {'name': "E2_DEFAULT_CONF",    'descr': "error. loading the default configuration."},
  0x31: {'name': "E2_CAL_ERROR",       'descr': "calibration invalid - measurement impossible"},
  0x32: {'name': "E2_CRC_CONF_ERR",    'descr': "CRC error. loading the default configuration."},
  0x33: {'name': "E2_CRC_CAL_ERR",     'descr': "CRC error. calibration invalid - measurement impossible"},
  0x34: {'name': "ADJ_STEP1",          'descr': "adjustment step 1"},
  0x35: {'name': "ADJ_OK",             'descr': "adjustment OK"},
  0x36: {'name': "CHANNEL_OFF",        'descr': "channel deactivated"},
  0x50: {'name': "VALUE_OVERFLOW",     'descr': "measured value (+offset) is above the set value limit"},
  0x51: {'name': "VALUE_UNDERFLOW",    'descr': ""},
  0x52: {'name': "CHANNEL_OVERRANGE",  'descr': "measured value (physical) is above the measurable range (e.g. ADC saturation)"},
  0x53: {'name': "CHANNEL_UNDERRANGE", 'descr': ""},
  0x54: {'name': "DATA_ERROR",         'descr': "measurement data is invalid or doesn't exist"},
  0x55: {'name': "MEAS_UNABLE",        'descr': "measurement impossible - check the environment conditions!"},
  0x60: {'name': "FLASH_CRC_ERR",      'descr': "CRC error in the values stored in flash memory"},
  0x61: {'name': "FLASH_WRITE_ERR",    'descr': "error on writing to flash memory"},
  0x62: {'name': "FLASH_FLOAT_ERR",    'descr': "flash memory contains invalid float values"},
  0x80: {'name': "FW_RECEIVE_ERR",     'descr': "Error activating firmware flash mode"},
  0x81: {'name': "CRC_ERR",            'descr': "CRC error"},
  0x82: {'name': "TIMEOUT_ERR",        'descr': "timeout occured"},
  0xF0: {'name': "RESERVED",           'descr': "reserved"},
  0xFF: {'name': "UNKNOWN_ERR",        'descr': "unknown error"},
}

class Object(object):
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return "Object.from_dict({})".format(self.__dict__)
    def __str__(self):
        return repr(self)

    @classmethod
    def from_dict(cls, d):
        o = Object()
        for key, val in d:
            setattr(o, key, val)
        return o

