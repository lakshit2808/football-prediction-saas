#!/bin/bash

ollama pull llama2
ollama serve
streamlit run main.py