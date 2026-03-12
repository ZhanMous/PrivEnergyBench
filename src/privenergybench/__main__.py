from .cli import parse_args, run_benchmark


if __name__ == "__main__":
    args = parse_args()
    run_benchmark(args.config)
