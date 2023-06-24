import socket
import asyncio

FROM_IP, FROM_PORT = "0.0.0.0", 5005
TO_IP, TO_PORT = "192.168.1.30", 9999

#MESSAGE = b"\x00"
PING_MESSAGE = bytearray([0])

print("UDP target IP: %s" % TO_IP)
print("UDP target port: %s" % TO_PORT)
print("message: %s" % PING_MESSAGE)
sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
sock.bind((FROM_IP, FROM_PORT))

def send_message(message):
  sock.sendto(message, (TO_IP, TO_PORT))

def ping():
  print('ping')
  send_message(PING_MESSAGE)

async def periodic():
  while True:
    ping()
    await asyncio.sleep(1)

def stop():
  ping_task.cancel()
  check_messages_task.cancel()
  
async def check_messages():
  while True:
    print("recvfrom")
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print("received message: %s" % data)
    await asyncio.sleep(1)

loop = asyncio.get_event_loop()
ping_task = loop.create_task(periodic())
check_messages_task = loop.create_task(check_messages())
loop.call_later(5, stop)

loop.create_datagram_endpoint

try:
    loop.run_until_complete(ping_task)
    loop.run_until_complete(check_messages_task)
except asyncio.CancelledError:
    pass