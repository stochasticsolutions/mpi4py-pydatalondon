"""
1-deadlock-risk.py

Run with:

   mpiexec -n 2 python 1-deadlock-risk.py

"""
from mpi4py import MPI

comm = MPI.COMM_WORLD            # The communication channel ("Intercom")

me = comm.Get_rank()             # The process(or) ID
other = 1 - me

sent_msg = f'Dear {other}, Hi! Love {me}.'
comm.send(sent_msg, dest=other)
received_msg = comm.recv(source=other)
print(f'Processor {me} sent message to processor {other}: {repr(sent_msg)}')
print(f'Processor {me} received message from {other}: {repr(received_msg)}')
