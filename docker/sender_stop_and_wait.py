import socket
import time

# total packet size
PACKET_SIZE = 1024
# bytes reserved for sequence id
SEQ_ID_SIZE = 4
# bytes available for message
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE

# read data
with open('file.mp3', 'rb') as f:
    data = f.read()

def finack(udp_socket, sid):
        # send final closing message
    udp_socket.sendto(int.to_bytes(sid, SEQ_ID_SIZE, signed=True, byteorder='big'), ('localhost', 5001))

    empty_message = int.to_bytes(sid, SEQ_ID_SIZE, signed=True, byteorder='big') + b''
    udp_socket.sendto(empty_message, ('localhost', 5001))

    # Wait for acknowledgment and fin message from the receiver
    ack, _ = udp_socket.recvfrom(PACKET_SIZE)
    fin, _ = udp_socket.recvfrom(PACKET_SIZE)

    # Sender sends '==FINACK' to notify the receiver to exit
    finack_message = int.to_bytes(sid + 1, SEQ_ID_SIZE, signed=True, byteorder='big') + b'==FINACK=='
    udp_socket.sendto(finack_message, ('localhost', 5001))
 
# create a udp socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
    startTime = time.time()
    
    # bind the socket to a OS port
    udp_socket.bind(('localhost', 5000))
    udp_socket.settimeout(1)

    delays = {}
    
    
    # start sending data from 0th sequence
    seq_id = 0
    totalPackets = 0


    while seq_id < len(data):
        try:
            # construct message
            # sequence id of length SEQ_ID_SIZE + message of remaining PACKET_SIZE - SEQ_ID_SIZE bytes
            message = int.to_bytes(seq_id, SEQ_ID_SIZE, byteorder='big', signed=True) + data[seq_id : seq_id + MESSAGE_SIZE]

            packetStartTime = time.time()
        
            # send message out
            udp_socket.sendto(message, ('localhost', 5001))

            # wait for ack
            ack, _ = udp_socket.recvfrom(PACKET_SIZE)

            packetEndTime = time.time()

            packetDelay = (packetEndTime - packetStartTime)
            

            delays[seq_id] = packetDelay

                
            # extract ack id
            ack_id = int.from_bytes(ack[:SEQ_ID_SIZE], byteorder='big')
            # print(ack_id, ack[SEQ_ID_SIZE:], f"Delay: {packetDelay} seconds")
            
            totalPackets += 1
            
            # move sequence id forward
            seq_id += MESSAGE_SIZE
                
            # ack id == sequence id, move on
            if ack_id == seq_id + MESSAGE_SIZE:
                break
        except socket.timeout:
            # no ack, resend message
            packetStartTime = time.time()
            udp_socket.sendto(message, ('localhost', 5001))


    finack(udp_socket, seq_id)


# calculate throughput
endTime = time.time()
timeTaken = (endTime - startTime)
throughput = totalPackets * MESSAGE_SIZE / timeTaken

# compute average delay per packet
avgDelay = sum(delays.values()) / totalPackets

# compute and print the desired metric
metric = throughput / avgDelay

# Print the results in the specified format
print(f"{throughput:.2f}, {avgDelay:.2f}, {metric:.2f}")
