"""
0-send-receive.py

Run with:

   mpiexec -n 2 python 0-send-receive.py

"""
from mpi4py import MPI

comm = MPI.COMM_WORLD              # The communication channel ("Intercom")

rank = comm.Get_rank()             # The process(or) ID

if rank == 0:
    msg = 'Dear 1, Hi! Love 0.'    # (not in scope in other branch)
    comm.send(msg, dest=1)
    print(f'Processor {rank} sent message to processor 1: {repr(msg)}')
elif rank == 1:
    msg = comm.recv(source=0)      # Can omit the source to receive from anyone
    print(f'Processor {rank} received message from 0: {repr(msg)}')

