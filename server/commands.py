import argparse
import subprocess

parser = argparse.ArgumentParser(description='Run docker-compose')
parser.add_argument('action', choices=['up', 'down'], help='docker-compose up/down')
parser.add_argument('--spark-workers', action="store_true", help='Spark worker 사용', default=False)
parser.add_argument('--hadoop', action="store_true", help='Hadoop cluster 사용', default=False)
parser.add_argument('--build', action="store_true", help='Build 유무', default=False)

args = parser.parse_args()
print(args)

compose_files = {
    "hadoop":"docker-compose.hadoop.yaml",
    "spark-workers":"docker-compose.spark.worker.yaml",
}

command_args = ["docker-compose"]

if args.action == "down" or args.spark_workers:
    command_args.append(f'-f {compose_files["spark_workers"]}')
if args.action == "down" or args.hadoop:
    command_args.append(f'-f {compose_files["hadoop"]}')

if args.action == "down":
    command_args.append("down")
else:
    command_args.append("up -d")

if args.build:
    command_args.append("--build")

print(command_args)
subprocess.run(" ".join(command_args), shell=True)