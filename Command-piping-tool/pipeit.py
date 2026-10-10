#!/usr/bin/env python3
"""A small interactive command-line shell for an OSSP project."""

from __future__ import annotations

import os
import shlex
import subprocess
import sys
from collections.abc import Sequence


class ParseError(ValueError):
    pass


def parse_pipeline(text: str) -> list[list[str]]:
    """Split a command line into pipe stages and shell-like arguments."""
    try:
        parts = shlex.split(text, punctuation_chars="|")
    except ValueError as exc:
        raise ParseError(str(exc)) from exc

    stages: list[list[str]] = []
    stage: list[str] = []
    for part in parts:
        if part and set(part) == {"|"}:
            if len(part) != 1 or not stage:
                raise ParseError("empty command in pipeline")
            stages.append(stage)
            stage = []
        else:
            stage.append(part)
    if not stage:
        raise ParseError("empty command in pipeline")
    stages.append(stage)
    return stages


def run_pipeline(stages: Sequence[Sequence[str]]) -> int:
    """Execute a pipeline and return the final command's exit status."""
    processes: list[subprocess.Popen[bytes]] = []
    previous_stdout = None
    try:
        for index, stage in enumerate(stages):
            process = subprocess.Popen(
                stage,
                stdin=previous_stdout,
                stdout=subprocess.PIPE if index < len(stages) - 1 else None,
            )
            if previous_stdout is not None:
                previous_stdout.close()
            previous_stdout = process.stdout
            processes.append(process)
        return processes[-1].wait()
    except FileNotFoundError as exc:
        print(f"minish: command not found: {exc.filename}", file=sys.stderr)
        for process in processes:
            process.kill()
        for process in processes:
            process.wait()
        return 127
    except OSError as exc:
        print(f"minish: {exc}", file=sys.stderr)
        for process in processes:
            process.kill()
        for process in processes:
            process.wait()
        return 1


def run_command(line: str) -> int:
    """Handle built-ins or run an external command/pipeline."""
    if not line.strip():
        return 0
    try:
        stages = parse_pipeline(line)
    except ParseError as exc:
        print(f"minish: {exc}", file=sys.stderr)
        return 2

    # Built-ins run in this process so `cd` changes the shell's directory.
    if len(stages) == 1:
        command = stages[0]
        if command[0] == "exit":
            if len(command) > 2:
                print("minish: exit: expected at most one status", file=sys.stderr)
                return 2
            try:
                status = int(command[1]) % 256 if len(command) == 2 else 0
            except ValueError:
                print("minish: exit: status must be an integer", file=sys.stderr)
                return 2
            raise SystemExit(status)
        if command[0] == "cd":
            if len(command) > 2:
                print("minish: cd: expected zero or one path", file=sys.stderr)
                return 1
            path = command[1] if len(command) == 2 else os.path.expanduser("~")
            try:
                os.chdir(os.path.expanduser(path))
            except OSError as exc:
                print(f"minish: cd: {exc}", file=sys.stderr)
                return 1
            return 0
        if command[0] == "help":
            print("Built-ins: cd [DIR], help, exit [STATUS]")
            print("Run external programs directly; connect commands with |.")
            return 0

    return run_pipeline(stages)


def main() -> int:
    """Start an interactive prompt or execute a single supplied command."""
    if len(sys.argv) > 1:
        return run_command(" ".join(sys.argv[1:]))

    while True:
        try:
            line = input(f"{os.getcwd()} $ ")
        except EOFError:
            print()
            return 0
        except KeyboardInterrupt:
            print()
            continue
        try:
            run_command(line)
        except SystemExit as exc:
            return int(exc.code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
