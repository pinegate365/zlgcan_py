# ZLGCAN Python API

## 使用指南
- 在ZLG官网搜索：CAN接口卡二次开发接口函数库，即可下载zlgcan二次开发库。官网地址：https://www.zlg.cn/can/can/index.html
- 将zlgcan二次开发库中的zlgcan.dll和kerneldlls文件夹拷贝到当前目录下即可。
- 下载的zlgcan接口库和当前运行python版本位数(32/64bits)一致。
- 当前zlgcan.py中示例DEMO使用设备为usbcanfd-100u/200u/mini。

## 作为python-can的backend driver使用
- 在项目根目录下，执行`pip install .`来安装zlgcan。会注册为python-can的backeng driver，驱动名称为“zlgcan”。
- 然后可以在你自己的项目中先导入周立功can卡的类型，如下所示：

        from zlg_can.zlgcan import (
            ZCAN_USBCAN1,
            ZCAN_USBCAN_E_U,
            ZCAN_USBCAN_2E_U,
            ZCAN_USBCAN_2E_U,
            ZCAN_PCI9820I
        )
- 然后调用python-can的接口，使用zlgcan作为backend driver，使用方式如下所示：

        import can
        bus = can.Bus(channel=0, bustype='zlgcan', device_type=ZCAN_USBCAN1, bitrate=500000)
  
  注意：需要额外设置device_type来指定can卡类型。  
