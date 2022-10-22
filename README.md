# This is a GUI implementation to interface with a [DiscoArt](https://github.com/jina-ai/discoart) server.

# 

# Development Quickstart

## 1. Create virtualenv

```bash
pyenv virtualenv 3.10.4 disco-diffusion-ui
pyenv local disco-diffusion-ui
```

## 2. Install requirements

```bash
make install-dev
```

## 3. Setup Environment
Use direnv and .envrc.example file.

```bash
mv .envrc.example .envrc
direnv allow .envrc
```