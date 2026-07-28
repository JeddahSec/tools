# HTTP Forward Shell

An HTTP-based forward shell that communicates with a remote PHP endpoint.  
Commands are base64-encoded and piped through a named FIFO for persistent shell interaction.

---

## Project Structure

```
http-forward-shell/
├── main.py           # Entry point — argument parsing & signal handling
├── forwardshell.py   # ForwardShell class — core shell logic
├── index.php         # Vulnerable PHP endpoint (runs on the target)
├── Dockerfile        # Builds a lightweight web server for testing
└── README.md
```

---

## Setup with Docker

### 1 — Build the image

```bash
docker build . -t web_server
```

### 2 — Run the container

```bash
docker run --rm -dit -p 80:80 web_server
```

### 3 — Verify the container is running

```bash
docker ps
```

### 4 — Get the exposed port

```bash
docker port <NAMES>
```

### 5 — Open a shell inside the container

```bash
docker exec -it <NAMES> bash
```

> Replace `<NAMES>` with the container name shown in `docker ps`.

---

## Usage

```bash
# Default target (localhost)
python3 main.py

# Custom target
python3 main.py -u http://10.10.10.1/index.php

# Help
python3 main.py --help
```

### Built-in commands

| Command     | Description                            |
|-------------|----------------------------------------|
| `help`      | Show the built-in command panel        |
| `enum suid` | Enumerate binaries with SUID bit set   |
| `exit`      | Exit the current pseudo-terminal       |

### Upgrade to a pseudo-terminal

```bash
fwd> script /dev/null -c bash
```

---

## Requirements

```bash
pip install requests termcolor
```
