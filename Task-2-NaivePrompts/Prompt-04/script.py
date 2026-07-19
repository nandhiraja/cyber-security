import subprocess

def main():
    print("Simple Shell (type 'exit' or 'quit' to quit)")

    while True:
        command = input("> ").strip()

        if command.lower() in {"exit", "quit"}:
            break

        if not command:
            continue

        try:
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True
            )

            if result.stdout:
                print(result.stdout, end="")

            if result.stderr:
                print(result.stderr, end="")

            print(f"\nExit code: {result.returncode}")

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()