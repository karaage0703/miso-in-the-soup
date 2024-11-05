# miso-in-the-soup
LLM Brain in the soup

## Usage

### X86

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

### Jetson Setup

```sh
$ jetson-containers run --name ollama $(autotag ollama)
```

参考:[Seeed reComputer J4012(Jetson Orin NX 16GB)セットアップ情報まとめ](https://zenn.dev/karaage0703/articles/04ca258a89a50e)
