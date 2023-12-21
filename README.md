#  ECS 152A Programming Assignment 3 (Fall 2023)

## Note: This README, the receiver.py, training_profile.sh, start-simulator.sh, Dockerfile, file.mp3, docker-script.sh were received from the TA's code in the link below 
Check the `How to use` section of the README for instructions on indicating the end of sending data.

## Congestion Control
Derived from https://github.com/Haroon96/ecs152a-fall-2023/tree/main/week7
### Docker Installation
* [Linux](https://docs.docker.com/engine/install/ubuntu/)
* [Mac](https://docs.docker.com/desktop/install/mac-install/)
* [Windows](https://docs.docker.com/desktop/install/windows-install/)

### How to use
(From the `docker` directory).
1. Run `./start-simulator.sh` to start running our receiver with the emulated network profile. Once it's running successfully, you will see a message saying `Receiver running`. 
2. The receiver has already been programmed to send acknowledgements to the sender similar to the receiver in the [discussion](https://github.com/Haroon96/ecs152a-fall-2023/blob/main/week7/docker/receiver.py).
3. Implement your own sender code and bind it to any port other than `5001`. Invoke your sender to send packets to `localhost`, port `5001` to communicate with the receiver.
4. Finally, on sending all the data, sender should send an empty message with the correct sequence id.
5. Receiver will then send an ack and fin message for the sender to know it's been acknowledged. (Lines 55 to 59 in receiver.py)
6. The sender should then send a message with body '==FINACK' to let the receiver know to exit (see line 31 and 32 in receiver.py)
7. Both sender and receiver will then exit.


### How to run code
1. Run ```python receiver.py```
2. Then on a different terminal run any of the sender file
    * ```python sender_stop_and_wait.py```
    * ```python sender_fixed_sliding_window.py```
    * ```python sender_tahoe.py```
    * ```python sender_reno.py```
    * ```python sender_custom.py```
3. Once all the packages has been received it will show the throughput, average delay per packet, and the metrics of throughput per average delay