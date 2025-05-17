"""
Enhanced module for working with Cloudflare AI and other Cloudflare services

This module provides a clean interface for working with Cloudflare AI models and services.
"""

import os
import requests
import json
import logging
import time
import base64
import traceback
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

# Check for Cloudflare API credentials
CLOUDFLARE_AI_TOKEN = os.environ.get("CLOUDFLARE_AI_TOKEN")
CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")

# Base URLs for Cloudflare services
CF_AI_BASE_URL = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/"

# Available AI models
CF_MODELS = {
    # Text models
    "llama3-8b": "@cf/meta/llama-3-8b-instruct",
    "llama3-70b": "@cf/meta/llama-3-70b-instruct",
    "claude-instant": "@cf/anthropic/claude-instant-1",
    "claude-2": "@cf/anthropic/claude-2",
    
    # Image generation models
    "stable-diffusion": "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    
    # Utility models
    "moderation": "@cf/cloudflare/moderation", 
    "image-classification": "@cf/microsoft/resnet-50",
    "text-embeddings": "@cf/baai/bge-base-en-v1.5",
    "speech-recognition": "@cf/openai/whisper",
    "translation": "@cf/meta/m2m100-1.2b"
}

class CloudflareAI:
    """Main class for interacting with Cloudflare AI services"""
    
    def __init__(self):
        self.token = CLOUDFLARE_AI_TOKEN
        self.account_id = CLOUDFLARE_ACCOUNT_ID
        
        if not self.token or not self.account_id:
            logger.warning("Cloudflare credentials missing. Some features will not work.")
    
    def _make_request(self, model_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to Cloudflare AI API
        
        Args:
            model_key: The model identifier (from CF_MODELS or direct path)
            data: Request payload specific to the model
            
        Returns:
            Dict with response or error information
        """
        if not self.token or not self.account_id:
            return {"success": False, "error": "Missing Cloudflare credentials"}
        
        try:
            # Get model path from dictionary or use directly if not found
            model_path = CF_MODELS.get(model_key, model_key)
            
            # Construct URL with account ID
            if self.account_id:
                url = CF_AI_BASE_URL.replace("{account_id}", self.account_id) + model_path
            else:
                return {"success": False, "error": "Missing Cloudflare account ID"}
            
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # Make the request with a reasonable timeout
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Cloudflare API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "details": response.text
                }
            
            return {
                "success": True,
                "result": response.json()
            }
            
        except Exception as e:
            logger.error(f"Error making Cloudflare AI request: {str(e)}")
            logger.debug(traceback.format_exc())
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_text(self, prompt: str, system_message: Optional[str] = None, 
                      model: str = "llama3-8b") -> Dict[str, Any]:
        """
        Generate text using Cloudflare AI text models
        
        Args:
            prompt: User prompt or question
            system_message: Optional system message to guide model behavior
            model: Model to use (default: llama3-8b)
            
        Returns:
            Dict containing generated text or error
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
            
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "messages": messages,
            "stream": False
        }
        
        response = self._make_request(model, data)
        
        if response.get("success"):
            # Extract the actual text response from the Cloudflare response structure
            try:
                text = response["result"]["result"]["response"]
                return {
                    "success": True,
                    "text": text,
                    "model": model
                }
            except (KeyError, TypeError) as e:
                logger.error(f"Error extracting text from response: {str(e)}")
                return {
                    "success": False,
                    "error": "Invalid response format",
                    "raw_response": response.get("result")
                }
        
        return response
    
    def analyze_code(self, code: str, language: str = None, 
                    task: str = "review") -> Dict[str, Any]:
        """
        Analyze code for errors, improvements, or explanation
        
        Args:
            code: The code to analyze
            language: The programming language
            task: Type of analysis ("review", "explain", "optimize", "debug")
            
        Returns:
            Dict with analysis results
        """
        lang_str = f" {language}" if language else ""
        
        system_messages = {
            "review": f"You are an expert{lang_str} programmer. Review the following code for bugs, errors, and stylistic issues. Provide specific line references and suggestions for improvement.",
            "explain": f"You are an expert{lang_str} programmer. Explain the following code in detail, including what it does, how it works, and any important concepts it demonstrates.",
            "optimize": f"You are an expert{lang_str} programmer. Suggest ways to optimize the following code for better performance, readability, or maintainability.",
            "debug": f"You are an expert{lang_str} programmer. Debug the following code. Identify errors, explain why they occur, and provide fixed code."
        }
        
        system_message = system_messages.get(task, system_messages["review"])
        
        return self.generate_text(code, system_message=system_message, model="llama3-8b")
    
    def generate_image(self, prompt: str) -> Dict[str, Any]:
        """
        Generate an image from a text prompt using Stable Diffusion
        
        Args:
            prompt: Text description of the desired image
            
        Returns:
            Dict with image data (base64) or error
        """
        data = {
            "prompt": prompt
        }
        
        response = self._make_request("stable-diffusion", data)
        
        if response.get("success"):
            try:
                # Extract image data from response
                image_b64 = response["result"]["result"]["images"][0]
                return {
                    "success": True,
                    "image_b64": image_b64
                }
            except (KeyError, IndexError) as e:
                logger.error(f"Error extracting image from response: {str(e)}")
                return {
                    "success": False,
                    "error": "Invalid image response format",
                    "raw_response": response.get("result")
                }
        
        return response
    
    def moderate_content(self, text: str) -> Dict[str, Any]:
        """
        Check text for harmful or inappropriate content
        
        Args:
            text: Text to check
            
        Returns:
            Dict with moderation results
        """
        data = {
            "text": text
        }
        
        return self._make_request("moderation", data)
    
    def classify_image(self, image_b64: str) -> Dict[str, Any]:
        """
        Classify an image using ResNet-50
        
        Args:
            image_b64: Base64-encoded image data
            
        Returns:
            Dict with classification results
        """
        data = {
            "image": image_b64
        }
        
        return self._make_request("image-classification", data)
    
    def get_text_embedding(self, text: str) -> Dict[str, Any]:
        """
        Get vector embedding for text
        
        Args:
            text: Text to embed
            
        Returns:
            Dict with embedding vector
        """
        data = {
            "text": text
        }
        
        return self._make_request("text-embeddings", data)
    
    def translate_text(self, text: str, target_language: str) -> Dict[str, Any]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., "fr", "es", "de")
            
        Returns:
            Dict with translated text
        """
        data = {
            "text": text,
            "target_language": target_language
        }
        
        return self._make_request("translation", data)

# Create global instance
cf_ai = CloudflareAI()