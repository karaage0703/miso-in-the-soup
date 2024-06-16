# miso-in-the-soup
LLM Brain in the soup

## Usage

```sh
$ docker stop $(docker ps -q)
$ docker rm $(docker ps -q -a)
```

```sh
$ docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

```sh
$ python3 miso.py
```
