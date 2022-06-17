"""
2-deadlock.py

Run with:

   mpiexec -n 2 python 2-deadlock.py

"""
from mpi4py import MPI

comm = MPI.COMM_WORLD            # The communication channel ("Intercom")

me = comm.Get_rank()             # The process(or) ID
other = 1 - me

sent_msg = f'Dear {other}, Hi! Love {me}.'
L = len(sent_msg)

for n in range(1, 16):
    comm.send(sent_msg * (2 ** n), dest=other)
    received_msg = comm.recv(source=other)
    print(f'Processor {me} sent message of length {len(sent_msg)} '
          f'to processor {other}, starting starting{repr(sent_msg)}')
    print(f'Processor {me} received message of length {len(received_msg)} '
          f'from {other}, starting: {repr(received_msg[:L])}')
