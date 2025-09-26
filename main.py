#!/usr/bin/env python3
"""
Adam Sandler News Agent
Ponto de entrada principal do aplicativo.
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(__file__))

# Importar e executar a CLI
from src.interfaces.cli.main import main

if __name__ == "__main__":
    main()