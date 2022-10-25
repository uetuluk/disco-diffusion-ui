![UI Image](images/ui.png)
# Disco Diffusion UI

This is a GUI implementation to interface with a [DiscoArt](https://github.com/jina-ai/discoart) server.

The following settings can be adjusted.
* Prompt - `text_prompts`
* Dimensions - `width_height`
* Skip Steps - `skip_steps`
* Steps - `steps`
* Clip Guidance Scale - `clip_guidance_scale`
* Diffusion Model - `diffusion_model`
* Secondary Model - `use_secondary_model`
* Seed - `seed`
* Maximum Clamp - `clamp_max`
* cut_ic_pow
* Clip Models - `clip_models`

# How to Setup

WIP

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