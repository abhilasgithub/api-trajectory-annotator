# Project 1: API Workflow Trajectory Annotator

## Overview
A Python tool that breaks down complex API workflows into structured, annotated step-by-step trajectories for LLM training data. Demonstrates skills in API handling, structured output, and reasoning documentation.

## Skills Demonstrated
- Python scripting
- API workflow decomposition
- Structured trajectory generation
- Reasoning documentation
- JSON schema design

## Setup
```bash
pip install requests python-dotenv
python annotator.py
```

## Usage
```bash
python annotator.py --task "fetch user data and update records" --api openai
python annotator.py --task "upload file and trigger processing pipeline" --api custom
```
