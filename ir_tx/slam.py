# SumoBot Little Asynchronous Messaging - SLAM 
# Encoder for IR transmission of SumoBots
# Written by Team Electric Muffin
# Cam Chalmers, Melissa Clark, Anusha Venkateswaran
# For ECEN 2440 - Applications of Embedded Systems, Spring '24
# Modified from NEC code by Peter Hinch

#DONE Reduce data and address size from 8 to 4 bits
#DONE Reduce burst length 
#DONE Reduce long/short space ratio
#DONE Make burst time based on tx frequency, so that higher frequencies reduce tx time
#DONE Reduce Start block size 
# First and second burst are both one DASH in length. A properly coded transmission will not have any other sequential DASH'es

from ir_tx import IR
import time

class SLAM(IR):
    valid = (0xf, 0xf, 0)  # Max addr, data, toggle

    _DASH_Ratio = 2 #Number of times we multiply _DOT to get the length of _DASH
    _CYCLES_PER_DOT = 10 #Number of IR cycles in a DOT. Determined by the IR Reciever, check the datasheet for information
    _edges = 36 #Number of rising/falling edges in a valid transmission block 

    _TX_DELAY = 3 #Length of time between transmissions; measured in transmission block sizes
    _Next_TX_time = time.ticks_ms()
    _TX_Block_Length = 0
    _TX_Delay_ms = 0
    
    #TX per second... How do we calculate TX_DELAY from TX per second?
    #If we assume 4 times a second, 


    #DONE change asize argument passed to super().__init__() to new size
    # asize = on/off times (μs)
    # 2 on/off times per bit. 
    # 8*4 + 2 = 34 bits
    # NEC asize is 68 for 32 bits of data + start and end blocks

    # SLAM has 4 bit addr and data sizes. Additional 4 bits each of error detection, and Start and End bloc
    # 4*4 + 2 = 18 bits
    # SLAM asize = 36

    def __init__(self, pin, freq=38_000, verbose=False):  # 38kHz is the standard frequency
        
        self._setBurstLength(freq)
        self._setStartBlock()
        self._TX_Block_Length = self._calculate_txBlock()
        self._TX_DELAY = 160-(2*self._TX_Block_Length) # Transmit 6 times a second. This comes out to be roughly 20% of the time 
        self._TX_Delay_ms = self._TX_Block_Length * self._TX_DELAY
        super().__init__(pin, freq, self._edges, 33, verbose)  # Measured duty ratio 33% 

    def _bit(self, b):
        self.append(self._DOT, self._DASH if b else self._DOT) # If bit =1, long space, else short space

    def _setBurstLength(self, freq):
        """Set's the length of the bursts based on the tx frequency"""
        cycles_per_us = freq/(1_000_000)
        period = 1/cycles_per_us
        burst_cycles = self._CYCLES_PER_DOT #Number of cycles in a burst
        self._DOT = int(burst_cycles * period)
        self._DASH = int(self._DASH_Ratio * self._DOT)

    def _setStartBlock(self):
        self.StartBlock_leader = self._DASH # Length of Start Block
        self.StartBlock_follower = self._DASH

    def tx(self, addr, data, _):  # Ignore toggle
        if time.ticks_diff(self._Next_TX_time, time.ticks_ms()) > 0:
            print("TX too early. Must wait {%i} ms between TX attempts",self._TX_Delay_ms)
            return
        self.append(self.StartBlock_leader, self.StartBlock_follower)
        addr |= ((addr ^ 0xf) << 4)
        for _ in range(8):
            self._bit(addr & 1)
            addr >>= 1
        data |= ((data ^ 0xf) << 4)
        for _ in range(8):
            self._bit(data & 1)
            data >>= 1
        self.append(self._DOT)

    def _calculate_txBlock(self):
        """Returns the expected txBlock size, based on the freq and data size"""
        #From the freq we get TBURST
        #The tx block has 2 edges for each bit, so we use _edges to find the data size of the block
        # Each bit is proceded by a TBURST, then a pause w/ length based on the value of the bit
        # 0b0 = 1 TBURST + 1 TBURST
        # 0b1 = 1 TBURST + n * TBURST, where n is the size ratio
        # Due to error correction, each tx block is half 1's and half 0's
        # thus, tx block length = bits/2 * (2 TBURST) + bits/2 * (1 TBURST = n * TBURST)
        bits = self._edges/2
        zero_length = (bits * self._DOT)
        ones_length = (bits/2 * (self._DOT + self._DASH_Ratio*self._DOT))
        data_length = zero_length + ones_length

        #Include header information.
        txBlock_us = data_length + self.StartBlock_leader*2 + self.StartBlock_follower*2
        txBlock_ms = int(txBlock_us / 1000) # convert us to ms
        return txBlock_ms