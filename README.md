This was designed during the Spring '24 semester for an Applications of Embedded Systems class. It is a modified NEC standard based on code by Peter Hinch. https://github.com/peterhinch/micropython_ir/

By default, the NEC protocol uses 80ms of transit time. As any overlap of two transmissions will corrupt both of them, two competitors will each need 120ms of clear air every time they want to transmit. Since they must transmit multiple times a second, this will quickly lead to collisions and corrupted/rejected transmission blocks.

SLAM attempts to address this by reducing the transmission time and by restricting the number of transmissions per second.

Features
  Transmission time of about 15ms
  Ability to change carrier frequency
  Transmission time is scaled to the carrier frequency. TSOPs designed for higher frequencies have a quicker response and so require shorter transmission bursts
  Error detection. Since we expect multiple transmitters to be operating simultaneously, we are concerned about errant IR bursts.
  Addresses and commands are 4 bits long. 
  
