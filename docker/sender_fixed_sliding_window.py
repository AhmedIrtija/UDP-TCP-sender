import socket
import time

# total packet size
PACKET_SIZE = 1024
# bytes reserved for sequence id
SEQ_ID_SIZE = 4
# bytes available for message
MESSAGE_SIZE = PACKET_SIZE - SEQ_ID_SIZE
# total packets to send
WINDOW_SIZE = 100


# read data
with open('file.mp3', 'rb') as f:
    data = f.read()
    
    
def resend(udp_socket, id):
    message = int.to_bytes(id, SEQ_ID_SIZE, byteorder='big', signed=True) + data[id: id + MESSAGE_SIZE]
    udp_socket.sendto(message, ('localhost', 5001))
    return time.time()
    

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
    
    udp_socket.bind(('localhost', 5000))
    udp_socket.settimeout(1)
    
    packet_sent = {}
    totalDelay = 0
    totalPackets = 0

    seq_id = 0

    windowStart = 0
    windowEndCurr = WINDOW_SIZE * MESSAGE_SIZE
    windowEndPrev = windowStart
    dupCount = 0
    prevAck = -1

    while seq_id < len(data):

        for seq_id in range(windowEndPrev, windowEndCurr, MESSAGE_SIZE):
            if(seq_id < len(data)):
                packet_sent[seq_id] = resend(udp_socket, seq_id)
                totalPackets += 1

        try:
            ack, _ = udp_socket.recvfrom(PACKET_SIZE)
            ack_id = int.from_bytes(ack[:SEQ_ID_SIZE], byteorder='big')
            
    
            # print(ack_id, ack[SEQ_ID_SIZE:])

            seq_id = ack_id

            windowStart = seq_id
            windowEndPrev = windowEndCurr
            windowEndCurr = windowStart + WINDOW_SIZE * MESSAGE_SIZE

            
            for i in list(packet_sent.keys()):
               if i < ack_id:
                   totalDelay += time.time() - packet_sent[i]
                   del packet_sent[i]


            if prevAck == ack_id:
                dupCount += 1
                if dupCount == 2:
                    packet_sent[seq_id] = resend(udp_socket, seq_id)
                    totalPackets += 1
                    prevAck = -1
                    dupCount = 0

            else:
                prevAck = ack_id
             

        except socket.timeout:
            packet_sent[seq_id] = resend(udp_socket, seq_id)
            totalPackets += 1



    # send final closing message
    finack(udp_socket, seq_id)

# calculate throughput
endTime = time.time()
timeTaken = endTime - startTime
throughput = totalPackets * MESSAGE_SIZE / timeTaken
print(f"Throughput: {throughput} bytes/second")

# compute average delay per packet
avgDelay = totalDelay / totalPackets
print(f"Average Delay/Packet: {avgDelay} seconds")

# compute and print the desired metric
metric = throughput / avgDelay
print(f"Throughput/Average Delay: {metric}")
