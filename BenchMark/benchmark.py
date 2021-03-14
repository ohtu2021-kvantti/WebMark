from celery import Celery
import os
import requests

app = Celery('benchmark', broker=os.getenv("BROKER_URL", 'pyamqp://guest@localhost//'))


@app.task(ignore_result=True)
def benchmark_task(params):
    # TODO: this is just an example showing how params passed from WebMark end up here
    print(params)

    # TODO: validate params!
    result = run_benchmark(params)
    requests.post(
        os.getenv("DJANGO_API_URL", "http://localhost:8000/handleResult"),
        data={'result': result}
    )


def run_benchmark(params):
    # everything explodes if these imports are at the top level
    import quantmark as qm
    import tequila as tq

    # Define optimizer
    # TODO: use params!
    optimizer = qm.QMOptimizer(module="scipy", method="BFGS")

    # Define backend
    backend = qm.QMBackend(backend='qulacs')

    # TODO: use params!
    active_orbitals = {'A1': [1], 'B1': [0]}
    molecule = tq.chemistry.Molecule(
        geometry='H 0.0 0.0 0.0\nLi 0.0 0.0 1.6',
        basis_set='sto-3g',
        active_orbitals=active_orbitals
    )

    # TODO: use params!
    circuit = tq.gates.Ry(angle='a', target=0) + tq.gates.X(target=[2, 3])
    circuit += tq.gates.X(target=1, control=0)
    circuit += tq.gates.X(target=2, control=0)
    circuit += tq.gates.X(target=3, control=1)

    # Run the benchmark
    result = qm.vqe_benchmark(
        molecule=molecule,
        circuit=circuit,
        optimizer=optimizer,
        backend=backend,
        repetitions=100
    )

    return result
