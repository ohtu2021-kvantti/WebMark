from flask import Flask, request, jsonify
import docker
import time
import os

app = Flask(__name__)
client = docker.from_env()


@app.route("/benchmark", methods=["POST"])
def benchmark():
    # create an unique file
    timestamp = time.time_ns()
    file_path = f"/tmp/{timestamp}.py"

    # write the algorithm to file
    file = open(file_path, "w")
    file.write(request.json["algorithm"])
    file.close()

    # run the algorithm in a container
    try:
        output = client.containers.run(
            image="python:3.8",
            command="timeout -s SIGKILL 3 python /mnt/code.py",
            volumes={file_path: {'bind': '/mnt/code.py', 'ro': True}},
        )
        output = str(output, 'utf-8')
    except docker.errors.ContainerError:
        output = "something went wrong"

    os.remove(file_path)

    # TODO: proper response
    return jsonify(
        output=output
    )
