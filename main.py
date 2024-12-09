from machine import Pin
from time import sleep

# For hardware testing
# if both are false, it will simulate tx/rx by directly injecting and extracting a tx block 
AUTOMATIC_TX = True
AUTOMATIC_RX = False

SLAM = False

pin_Tx_test = Pin(6,Pin.IN,Pin.PULL_UP)
txPin = Pin(19, Pin.OUT)
rxPin = Pin(18, Pin.IN)

if AUTOMATIC_TX:
    import ir_tx.test as tx_test
    from ir_tx.slam import SLAM as tx_SLAM
    TX = tx_SLAM(txPin)
    tx_test.printSummery(TX)


elif AUTOMATIC_RX:
    import ir_rx.test as rx_test
    from ir_rx.slam import SLAM as rx_SLAM
    from ir_rx.print_error import print_error
    RX = rx_SLAM(rxPin, rx_test.callback)
    rx_test.printSummery(RX)
    RX.error_function(print_error)

    while True:
        sleep(0.1)
else:
    import ir_tx.test as tx_test
    import ir_rx.test as rx_test
    from ir_tx.slam import SLAM as tx_SLAM
    from ir_rx.slam import SLAM as rx_SLAM
    from ir_rx.print_error import print_error

    TX = tx_SLAM(txPin)
    RX = rx_SLAM(rxPin, rx_test.callback)


    RX.error_function(print_error)
    tx_test.printSummery(TX)
    rx_test.printSummery(RX)
    print("\nRunning Software Test")

    print("-Good Data Test. Expect Address: 0x2, Cmd 0xF")
    TX.transmit(0x02,0xF)
    txBlock = TX._arr
    rx_test.runTest(txBlock, RX)