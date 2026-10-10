# minish — simple terminal shell

`minish` is a small interactive command-line shell written in Python for an OSSP (Operating Systems and System Programming) project. It demonstrates a prompt loop, built-in commands, process creation, and Unix-style pipelines.

## Requirements

- Python 3.10 or newer
- A POSIX-like operating system is recommended

## Run

```sh
python3 pipeit.py
```

Or use the Makefile:

```sh
make run
```

At the prompt, try commands such as:

```text
help
pwd
ls -la
printf 'hello\\n' | tr a-z A-Z
cd ..
exit
```

You can also run one command without entering the prompt:

```sh
python3 pipeit.py 'echo hello | tr a-z A-Z'
```

## Built-ins

- `cd [DIR]` changes the shell's current directory; with no argument it goes to the home directory.
- `help` prints a short help message.
- `exit [STATUS]` exits the shell with an optional status code.

Other commands are started as external programs. Pipeline stages are connected using `|`. Arguments support shell-style quoting. This learning shell does not implement variables, redirection, glob expansion, job control, or shell scripting.

## Project files

- `pipeit.py` — shell loop, built-ins, parsing, and process pipeline execution
- `Makefile` — convenient launch target
- `.gitignore` — ignores Python caches, environments, and editor files

## License

Provided as-is for learning and experimentation.
