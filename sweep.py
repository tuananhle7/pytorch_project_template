import subprocess
import argparse
from pathlib import Path
import shutil
import socket
import util
import run


def get_sweep_argss():
    for seed in range(3):
        for num_hidden_units_1 in [10, 20]:
            for num_hidden_units_2 in [10, 20]:
                args = run.get_args_parser().parse_args([])
                args.seed = seed
                args.num_hidden_units_1 = num_hidden_units_1
                args.num_hidden_units_2 = num_hidden_units_2
                yield args


def args_to_str(args):
    result = ""
    for k, v in vars(args).items():
        k_str = k.replace("_", "-")
        if v is None:
            pass
        elif isinstance(v, bool):
            if v:
                result += " --{}".format(k_str)
        else:
            if isinstance(v, list):
                v_str = " ".join(map(str, v))
            else:
                v_str = v
            result += " --{} {}".format(k_str, v_str)
    return result


def main(args):
    if args.cluster:
        hostname = socket.gethostname()

    if args.rm:
        dir_ = "save/"
        if Path(dir_).exists():
            shutil.rmtree(dir_, ignore_errors=True)

    print("-------------------------------")
    print("-------------------------------")
    print("-------------------------------")
    util.logging.info(
        "Launching {} runs on {}".format(
            len(list(get_sweep_argss())), f"cluster ({hostname})" if args.cluster else "local",
        )
    )
    print("-------------------------------")
    print("-------------------------------")
    print("-------------------------------")

    for sweep_args in get_sweep_argss():
        if args.cluster:
            # SBATCH AND PYTHON CMD
            args_str = args_to_str(sweep_args)
            if args.no_repeat:
                sbatch_cmd = "sbatch"
                time_option = "12:0:0"
                python_cmd = f'--wrap="MKL_THREADING_LAYER=INTEL=1 python -u run.py {args_str}""'
            else:
                sbatch_cmd = "om-repeat sbatch"
                time_option = "2:0:0"
                python_cmd = f"MKL_THREADING_LAYER=INTEL=1 python -u run.py {args_str}"

            # SBATCH OPTIONS
            logs_dir = f"{util.get_save_dir(sweep_args)}/logs"
            Path(logs_dir).mkdir(parents=True, exist_ok=True)

            job_name = util.get_save_job_name_from_args(sweep_args)

            if args.priority:
                partition_option = "--partition=tenenbaum "
            else:
                partition_option = ""

            if args.titan_x:
                gpu_option = ":titan-x"
            else:
                gpu_option = ""

            gpu_memory_gb = 22
            cpu_memory_gb = 16
            if "openmind" in hostname:
                gpu_memory_option = f"--constraint={gpu_memory_gb}GB "
            else:
                gpu_memory_option = ""

            sbatch_options = (
                f"--time={time_option} "
                + "--ntasks=1 "
                + f"--gres=gpu{gpu_option}:1 "
                + gpu_memory_option
                + f"--mem={cpu_memory_gb}G "
                + partition_option
                + f'-J "{job_name}" '
                + f'-o "{logs_dir}/%j.out" '
                + f'-e "{logs_dir}/%j.err" '
            )
            cmd = " ".join([sbatch_cmd, sbatch_options, python_cmd])
            util.logging.info(cmd)
            subprocess.call(cmd, shell=True)
        else:
            run.main(sweep_args)


def get_parser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--cluster", action="store_true", help="")
    parser.add_argument("--titan-x", action="store_true", help="")
    parser.add_argument("--rm", action="store_true", help="")
    parser.add_argument("--priority", action="store_true", help="runs on lab partition")
    parser.add_argument(
        "--no-repeat",
        action="store_true",
        help="run the jobs using standard sbatch."
        "if False, queues 2h jobs with dependencies "
        "until the script finishes",
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
