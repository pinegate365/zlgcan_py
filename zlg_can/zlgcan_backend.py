# -*- coding:utf-8 -*-
# zlgcan_backend.py
#
# ~~~~~~~~~~~~
#
# ZLGCAN Backend for python-can
#
# ~~~~~~~~~~~~
#
# ------------------------------------------------------------------
# Author : guochuangjian, modified by [Your Name]
# Last change: [Current Date]
#
# Language: Python 3.6+
# ------------------------------------------------------------------

from can import BusABC, Message
from can.bus import BusState
from zlg_can.zlgcan import ZCAN, ZCAN_USBCANFD_MINI, ZCAN_TYPE_CAN, ZCAN_TYPE_CANFD, ZCAN_Transmit_Data, ZCAN_TransmitFD_Data, ZCAN_STATUS_OK, ZCAN_CHANNEL_INIT_CONFIG
from ctypes import byref, c_int, c_ubyte

class ZLGCANBus(BusABC):
    def __init__(self, channel, bitrate=500000, fd=False, device_type=ZCAN_USBCANFD_MINI, **kwargs):
        super().__init__(channel, can_filters=None, **kwargs)
        self.zcanlib = ZCAN()
        self.device_handle = self.zcanlib.OpenDevice(device_type, 0, 0)
        if self.device_handle == 0:
            raise IOError("Failed to open ZLGCAN device")
        
        self.chn_handle = self._init_channel(bitrate, fd)
        if self.chn_handle is None:
            raise IOError("Failed to initialize ZLGCAN channel")
        
        self.zcanlib.StartCAN(self.chn_handle)
        self.state = BusState.ACTIVE

    def _init_channel(self, bitrate, fd):
        ip = self.zcanlib.GetIProperty(self.device_handle)
        self.zcanlib.SetValue(ip, f"{self.channel_info}/clock", "60000000")
        self.zcanlib.SetValue(ip, f"{self.channel_info}/canfd_standard", "0")
        self.zcanlib.SetValue(ip, f"{self.channel_info}/initenal_resistance", "1")
        self.zcanlib.ReleaseIProperty(ip)

        chn_init_cfg = ZCAN_CHANNEL_INIT_CONFIG()
        chn_init_cfg.can_type = ZCAN_TYPE_CANFD if fd else ZCAN_TYPE_CAN
        if fd:
            chn_init_cfg.config.canfd.abit_timing = 101166  # 1Mbps
            chn_init_cfg.config.canfd.dbit_timing = 101166  # 1Mbps
        else:
            chn_init_cfg.config.can.timing0 = 0x00  # Set according to bitrate
            chn_init_cfg.config.can.timing1 = 0x1C  # Set according to bitrate
        chn_init_cfg.config.canfd.mode = 0

        return self.zcanlib.InitCAN(self.device_handle, self.channel_info, chn_init_cfg)

    def send(self, msg, timeout=None):
        if msg.is_fd:
            fd_msg = ZCAN_TransmitFD_Data()
            fd_msg.frame.can_id = msg.arbitration_id
            fd_msg.frame.len = msg.dlc
            fd_msg.frame.brs = 1 if msg.bitrate_switch else 0
            fd_msg.frame.esi = 0
            fd_msg.frame.data = (c_ubyte * 64)(*msg.data)
            fd_msg.transmit_type = 2  # Send Self
            ret = self.zcanlib.TransmitFD(self.chn_handle, fd_msg, 1)
        else:
            std_msg = ZCAN_Transmit_Data()
            std_msg.frame.can_id = msg.arbitration_id
            std_msg.frame.can_dlc = msg.dlc
            std_msg.frame.data = (c_ubyte * 8)(*msg.data)
            std_msg.transmit_type = 2  # Send Self
            ret = self.zcanlib.Transmit(self.chn_handle, std_msg, 1)

        if ret != ZCAN_STATUS_OK:
            raise IOError("Failed to send message")

    def recv(self, timeout=None):
        rcv_num = self.zcanlib.GetReceiveNum(self.chn_handle, ZCAN_TYPE_CANFD if msg.is_fd else ZCAN_TYPE_CAN)
        if rcv_num == 0:
            return None

        if msg.is_fd:
            rcv_canfd_msgs, rcv_canfd_num = self.zcanlib.ReceiveFD(self.chn_handle, rcv_num, timeout)
            if rcv_canfd_num == 0:
                return None
            rcv_msg = rcv_canfd_msgs[0]
            msg = Message(
                arbitration_id=rcv_msg.frame.can_id,
                dlc=rcv_msg.frame.len,
                data=rcv_msg.frame.data[:rcv_msg.frame.len],
                is_extended_id=rcv_msg.frame.eff,
                is_remote_frame=rcv_msg.frame.rtr,
                bitrate_switch=rcv_msg.frame.brs,
                error_state_indicator=rcv_msg.frame.esi,
                # Convert timestamp from macroseconds to seconds
                timestamp=rcv_msg.timestamp / 1000000.0
            )
        else:
            rcv_msgs, rcv_num = self.zcanlib.Receive(self.chn_handle, rcv_num, timeout)
            if rcv_num == 0:
                return None
            rcv_msg = rcv_msgs[0]
            msg = Message(
                arbitration_id=rcv_msg.frame.can_id,
                dlc=rcv_msg.frame.can_dlc,
                data=rcv_msg.frame.data[:rcv_msg.frame.can_dlc],
                is_extended_id=rcv_msg.frame.eff,
                is_remote_frame=rcv_msg.frame.rtr,
                # Convert timestamp from macroseconds to seconds
                timestamp=rcv_msg.timestamp / 1000000.0
            )

        return msg

    def flush_tx_buffer(self):
        self.zcanlib.ClearBuffer(self.chn_handle)

    def shutdown(self):
        self.zcanlib.ResetCAN(self.chn_handle)
        self.zcanlib.CloseDevice(self.device_handle)
        self.state = BusState.SHUTDOWN