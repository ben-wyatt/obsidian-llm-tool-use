"""
Ollama Connection Module

This module provides functions to initialize, manage, and connect to an Ollama server.
It handles server startup, health checking, and client creation.
(Written by Claude)
"""
import logging
import os
import psutil
import subprocess
import time
import requests
from contextlib import contextmanager
from typing import Optional, Union
from openai import OpenAI
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ollama")

# Default configuration
DEFAULT_OLLAMA_URL = "http://localhost:11434/v1"
DEFAULT_OLLAMA_MODEL = "qwen2.5"
HEALTH_CHECK_RETRIES = 5
HEALTH_CHECK_DELAY = 1  # seconds


def get_ollama_process() -> Optional[psutil.Process]:
    """
    Get the ollama process if it's running.
    
    Returns:
        Optional[psutil.Process]: Process object if Ollama is running, None otherwise.
    """
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'ollama':
            return proc
    return None


def check_ollama_health(base_url: str = DEFAULT_OLLAMA_URL) -> bool:
    """
    Check if Ollama server is healthy and responding.
    
    Args:
        base_url: The base URL of the Ollama server
        
    Returns:
        bool: True if the server is healthy, False otherwise
    """
    health_url = base_url.replace('/v1', '') + '/health'
    try:
        response = requests.get(health_url, timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False


def init_ollama() -> Optional[psutil.Process]:
    """
    Initialize the Ollama server if it's not already running.
    
    Returns:
        Optional[psutil.Process]: The Ollama process object
    
    Raises:
        RuntimeError: If Ollama fails to start or become healthy
    """
    ollama_proc = get_ollama_process()
    
    if ollama_proc:
        logger.info("Ollama process found (PID: %d)", ollama_proc.pid)
        return ollama_proc
    
    logger.info("Ollama process not found. Starting new instance.")
    
    # Start the Ollama server with proper resource management
    with open(os.devnull, 'w') as null_file:
        try:
            subprocess.Popen(
                ['ollama', 'serve'],
                stdout=null_file,
                stderr=null_file,
                start_new_session=True  # Detach from parent process
            )
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error("Failed to start Ollama: %s", str(e))
            raise RuntimeError(f"Failed to start Ollama: {str(e)}") from e
    
    # Wait for the process to start
    for _ in range(HEALTH_CHECK_RETRIES):
        time.sleep(HEALTH_CHECK_DELAY)
        ollama_proc = get_ollama_process()
        if ollama_proc:
            break
    else:
        logger.error("Ollama process failed to start within timeout")
        raise RuntimeError("Ollama process failed to start within timeout")
    
    # Wait for the server to become healthy
    for _ in range(HEALTH_CHECK_RETRIES):
        if check_ollama_health():
            logger.info("Ollama server started successfully (PID: %d)", ollama_proc.pid)
            return ollama_proc
        time.sleep(HEALTH_CHECK_DELAY)
    
    logger.error("Ollama server failed health check")
    raise RuntimeError("Ollama server failed health check")


def get_ollama_client() -> OpenAI:
    """
    Initialize the Ollama server and return an OpenAI-compatible client.
    
    Environment variables:
        OLLAMA_BASE_URL: Override the default Ollama server URL
        OLLAMA_API_KEY: Override the default API key
    
    Returns:
        OpenAI: An initialized OpenAI client connected to Ollama
        
    Raises:
        RuntimeError: If the Ollama server cannot be started or the client cannot be initialized
    """
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment or use defaults
    base_url = os.environ.get("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL)
    api_key = os.environ.get("OLLAMA_API_KEY", "ollama")
    
    # Initialize Ollama server
    try:
        init_ollama()
    except RuntimeError as e:
        logger.error("Failed to initialize Ollama: %s", str(e))
        raise
    
    # Create and return the client
    try:
        client = OpenAI(base_url=base_url, api_key=api_key)
        return client
    except Exception as e:
        logger.error("Failed to initialize OpenAI client: %s", str(e))
        raise RuntimeError(f"Failed to initialize OpenAI client: {str(e)}") from e


def stop_ollama() -> bool:
    """
    Stop the Ollama server if it's running.
    
    Returns:
        bool: True if Ollama was stopped, False if it wasn't running
    """
    ollama_proc = get_ollama_process()
    if ollama_proc:
        try:
            ollama_proc.terminate()
            ollama_proc.wait(timeout=5)
            logger.info("Ollama server stopped")
            return True
        except psutil.Error as e:
            logger.error("Failed to stop Ollama: %s", str(e))
            return False
    return False


@contextmanager
def ollama_session(auto_stop: bool = False):
    """
    Context manager for Ollama sessions.
    
    Args:
        auto_stop: If True, stop the Ollama server when exiting the context.
        
    Yields:
        OpenAI: An initialized OpenAI client connected to Ollama
    """
    client = get_ollama_client()
    try:
        yield client
    finally:
        if auto_stop:
            stop_ollama()