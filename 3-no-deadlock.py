"""
3-no-deadlock.py

Run with:

   mpiexec -n 2 python 3-deadlock.py

"""
from mpi4py import MPI

comm = MPI.COMM_WORLD            # The communication channel ("Intercom")
BUF_SIZE = 1 << 20               # 1MB receive buffer

me = comm.Get_rank()             # The process(or) ID
other = 1 - me

sent_msg = f'Dear {other}, Hi! Love {me}.'
L = len(sent_msg)

buf = bytearray(BUF_SIZE)
for n in range(1, 16):
    rreq = comm.irecv(buf, source=other)  # re-used buffer
    sreq = comm.isend(sent_msg * (2 ** n), dest=other)
    received_msg = rreq.wait()
    print(f'Processor {me} sent message of length {len(sent_msg)} '
          f'to processor {other}, starting starting{repr(sent_msg)}')
    print(f'Processor {me} received message of length {len(received_msg)} '
          f'from {other}, starting: {repr(received_msg[:L])}')
    sreq.wait()

