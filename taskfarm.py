"""
task farm

Run example with:

   mpiexec -n 4 python taskfarm.py

replacing 4 with however many processors you have/want to use
"""
from mpi4py import MPI

MANAGER_ID = 0  # Manager is always worker (rank) zero under mpiexec
VERBOSE = False
STOP = -1


def worker(comm, worker_id, f, verbose=VERBOSE):
    """
    Worker process for taskfarm. (Run only on the workers.)
    Processes jobs using the function f until it receives STOP
    as the task_id.

    Args:
        comm: the MPI comm object
        worker_id: this worker's ID (rank, as returned by comm.Get_rank())
        f: the function to use to process jobs

    Returns:
        None (after all work is done!)
    """
    msg = comm.recv(source=MANAGER_ID)  # blocking

    (task_id, args, kw) = msg
    while task_id != STOP:
        result = f(*args, **kw)
        comm.send((worker_id, task_id, result), dest=MANAGER_ID)
        (task_id, args, kw) = comm.recv(source=MANAGER_ID)
    if verbose:
        print(f'Worker {worker_id} received STOP; stopping.')


class TaskFarm:
    """
    MPI-based Task Farm, Manager Process (run only on PID 0)

    Args:
        comm: the MPI comm object
        tasks: the list of tasks. Each task is a tuple, (f, args, kwargs)
               where f is a function to perform the task,
               args is the list of positional arguments for the function
               and kwargs is the list of keyword arguments for the function
        verbose: Optional boolean to control verbosity
                 Defaults to VERBOSE.
    """
    def __init__(self, comm, tasks, verbose=VERBOSE):
        self.comm = comm
        self.tasks = tasks or []
        self.verbose = verbose

        self.n_procs = comm.Get_size()
        self.n_results_outstanding = 0
        self.n_tasks = len(self.tasks)
        self.requests = [None] * self.n_procs  # holds request handles
        self.results = {}   # holds results, keyed on task_id

    def allot(self, task_id, worker):
        """
        Allot task n to the worker specified.
          - Picks the task with task_id
          - sends to a the nominated worker
          - Stores the request, keyed on worker, so it can be
            called after receipt.

        Args:
            task_id: the number of the task to be allocated
            worker: the ID of the task to be allocated
        """
        args, kw = self.tasks[task_id]
        task = (task_id, args, kw)
        req = self.comm.isend(task, dest=worker)  # non-blocking
        if self.verbose:
            print(f'Allotted task {task_id} to worker {worker}.')
        self.n_results_outstanding += 1
        self.requests[worker] = req  # store request handle for later await

    def collect_result(self):
        """
        Collects the next result from any worker then:
          - Records the result in self.results (keyed on task_id)
          - Waits on the initial request (which should be complete)

        Args:
            None

        Returns:
            - The ID of the worker that returned a result.
        """
        (worker, task_id, result) = self.comm.recv()  # receive
        self.results[task_id] = result
        if self.verbose:
            print(f'Received result of task {task_id} from worker {worker}.')

        req = self.requests[worker]
        self.n_results_outstanding -= 1
        self.requests[worker] = None
        if req:
            req.wait()  # must be done now: the result has been returned
        return worker

    def stop_workers(self):
        """
        Send stop task for all workers
        """
        # Wait for all the workers to have stopped
        for worker_id in range(1, self.n_procs):
            self.stop_worker(worker_id)

    def stop_worker(self, worker_id):
        """
        Send stop task to nominated worker
        """
        self.comm.send((STOP, (), {}), worker_id)

    def go(self):
        """
        Run the task farm with the tasks already specified.

        Return:
            Results, keyed on task_id, which is the index of the
            task in the task list.
        """
        # Send each worker an initial task, assuming there are enough
        n_initial = self.send_initial_tasks()

        # Collect each result and send a replacement task until all sent
        for task_id in range(n_initial, self.n_tasks):
            worker = self.collect_result()
            self.allot(task_id, worker)

        # Collect remaining results
        while self.n_results_outstanding > 0:
            worker = self.collect_result()

        return self.results

    def send_initial_tasks(self):
        """
        Send initial task to each worker

        Args:
            report (bool): If set to True, this will report the
                           initial allocation of tasks

        Returns:
            Number of tasks allocated (int)
        """
        n_workers = self.n_procs - 1
        n_initial = min(n_workers, self.n_tasks)
        for task_id in range(0, n_initial):
            self.allot(task_id, worker=task_id + 1)

        if self.verbose:
            print(f'{n_initial} tasks allocated.')

        return n_initial


if __name__ == '__main__':

    def cube(n):
        return n * n * n

    def report(tasks, results):
        for task_id, task in sorted(results.items()):
            (n,), _ = tasks[task_id][:2]
            print(f'{n}^3 = {results[task_id]}')

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    if rank == 0:  # Task Farm Manager; always ID 0
        tasks = [((i,), {}) for i in range(100)]
        tf = TaskFarm(comm, tasks)
        results = tf.go()
        tf.stop_workers()
        report(tasks, results)

    else:  # Task Worker
        f = cube
        worker(comm, rank, f, verbose=VERBOSE)
