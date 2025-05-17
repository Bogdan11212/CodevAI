"""
Cloudflare Gateway API
This module provides a clean interface for interacting with Cloudflare AI services.
"""

import os
import requests
import json
import logging
import base64
import time
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

# Available models from Cloudflare
CLOUDFLARE_MODELS = {
    # Text models
    "llama3-8b": "@cf/meta/llama-3-8b-instruct",
    "llama3-70b": "@cf/meta/llama-3-70b-instruct",
    
    # Image models
    "stable-diffusion": "@cf/stabilityai/stable-diffusion-xl-base-1.0",
    
    # Utility models
    "moderation": "@cf/cloudflare/moderation", 
    "classify-image": "@cf/microsoft/resnet-50",
    "embeddings": "@cf/baai/bge-base-en-v1.5",
}

class CloudflareGateway:
    """Gateway for Cloudflare AI services"""
    
    def __init__(self):
        """Initialize with environment variables"""
        self.token = os.environ.get("CLOUDFLARE_AI_TOKEN", "")
        self.account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
        self.base_url = "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/"
        
        if not self.token or not self.account_id:
            logger.warning("Cloudflare credentials missing. Set CLOUDFLARE_AI_TOKEN and CLOUDFLARE_ACCOUNT_ID.")
    
    def has_credentials(self) -> bool:
        """Check if credentials are available"""
        return bool(self.token and self.account_id)
    
    def call_model(self, model_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a Cloudflare AI model
        
        Args:
            model_key: Key from CLOUDFLARE_MODELS or direct model path
            data: Request data specific to the model
            
        Returns:
            Response dictionary with success status and result/error
        """
        if not self.has_credentials():
            return {"success": False, "error": "Cloudflare credentials not configured"}
        
        try:
            # Get the model path
            model_path = CLOUDFLARE_MODELS.get(model_key, model_key)
            
            # Build the URL
            url = self.base_url.format(account_id=self.account_id) + model_path
            
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # Make the request
            start_time = time.time()
            response = requests.post(url, headers=headers, json=data, timeout=60)
            
            # Log request duration for performance monitoring
            duration = time.time() - start_time
            logger.debug(f"Cloudflare AI request to {model_key} took {duration:.2f}s")
            
            # Handle response
            if response.status_code != 200:
                logger.error(f"Cloudflare API error: {response.status_code} - {response.text}")
                return {
                    "success": False, 
                    "error": f"API error: HTTP {response.status_code}",
                    "details": response.text
                }
            
            return {"success": True, "result": response.json()}
            
        except Exception as e:
            logger.error(f"Error calling Cloudflare AI: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def chat_completion(self, 
                        prompt: str, 
                        system_message: Optional[str] = None,
                        model: str = "llama3-8b") -> Dict[str, Any]:
        """
        Get a completion from an AI chat model
        
        Args:
            prompt: User's prompt
            system_message: Optional system instructions
            model: Model to use (default: llama3-8b)
            
        Returns:
            Dictionary with generated text or error
        """
        # Build messages array
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Prepare request data
        data = {
            "messages": messages,
            "stream": False
        }
        
        # Call the model
        response = self.call_model(model, data)
        
        if response.get("success"):
            try:
                # Extract just the text response
                result = response["result"]["result"]["response"]
                return {"success": True, "text": result}
            except (KeyError, TypeError):
                return {
                    "success": False,
                    "error": "Unexpected response format",
                    "raw": response.get("result")
                }
        
        return response
    
    def generate_image(self, prompt: str) -> Dict[str, Any]:
        """
        Generate an image from text prompt
        
        Args:
            prompt: Text description of the image
            
        Returns:
            Dictionary with base64 image data or error
        """
        data = {"prompt": prompt}
        
        response = self.call_model("stable-diffusion", data)
        
        if response.get("success"):
            try:
                # Extract base64 image data
                image_data = response["result"]["result"]["images"][0]
                return {"success": True, "image_data": image_data}
            except (KeyError, IndexError):
                return {
                    "success": False,
                    "error": "Could not extract image from response",
                    "raw": response.get("result")
                }
        
        return response
    
    def moderate_content(self, text: str) -> Dict[str, Any]:
        """
        Check if text contains harmful content
        
        Args:
            text: Text to moderate
            
        Returns:
            Dictionary with moderation results
        """
        data = {"text": text}
        
        return self.call_model("moderation", data)
    
    def classify_image(self, image_data: str) -> Dict[str, Any]:
        """
        Classify an image
        
        Args:
            image_data: Base64 encoded image
            
        Returns:
            Dictionary with classification results
        """
        data = {"image": image_data}
        
        return self.call_model("classify-image", data)
    
    def get_embeddings(self, text: str) -> Dict[str, Any]:
        """
        Get vector embeddings for text
        
        Args:
            text: Text to get embeddings for
            
        Returns:
            Dictionary with embedding vectors
        """
        data = {"text": text}
        
        return self.call_model("embeddings", data)
    
    def analyze_code(self, 
                     code: str, 
                     language: Optional[str] = None,
                     task: str = "review") -> Dict[str, Any]:
        """
        Analyze code for errors, improvements, or explanation
        
        Args:
            code: Code to analyze
            language: Programming language (optional)
            task: Analysis type: review, debug, explain, or optimize
            
        Returns:
            Dictionary with analysis results
        """
        lang_part = f" {language}" if language else ""
        
        # Define system prompts for different tasks
        prompts = {
            "review": f"You are an expert{lang_part} programmer. Review the following code for bugs, errors, " +
                      "and style issues. Provide specific line references and suggestions for improvement.",
            
            "debug": f"You are an expert{lang_part} programmer. Debug the following code. " +
                     "Identify errors, explain why they occur, and provide fixed code.",
            
            "explain": f"You are an expert{lang_part} programmer. Explain the following code in simple terms. " +
                       "Describe what it does, how it works, and any important concepts.",
            
            "optimize": f"You are an expert{lang_part} programmer. Optimize the following code. " +
                        "Suggest improvements for better performance, readability, or maintainability."
        }
        
        system_prompt = prompts.get(task, prompts["review"])
        
        return self.chat_completion(code, system_message=system_prompt)
    
    def learn_from_text(self, text: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract structured knowledge from text
        
        Args:
            text: Text to analyze
            topic: Optional topic category
            
        Returns:
            Dictionary with extracted knowledge
        """
        topic_part = f" about {topic}" if topic else ""
        
        system_message = (
            f"Extract useful programming knowledge{topic_part} from the following text. "
            "Return a JSON object with these keys: "
            "'key_concepts': [list of important concepts], "
            "'code_examples': [list of any code examples found], "
            "'best_practices': [list of best practices mentioned], "
            "'common_problems': [list of problems or pitfalls mentioned]"
        )
        
        response = self.chat_completion(text, system_message=system_message)
        
        if response.get("success"):
            # Try to parse JSON from the response
            try:
                text = response.get("text", "")
                
                # Look for JSON in the response
                if "```json" in text:
                    json_text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    json_text = text.split("```")[1].split("```")[0].strip()
                else:
                    json_text = text
                
                # Parse the JSON
                knowledge = json.loads(json_text)
                return {"success": True, "knowledge": knowledge}
            except Exception as e:
                logger.error(f"Error parsing knowledge extraction: {str(e)}")
                return {
                    "success": False,
                    "error": "Failed to parse knowledge data",
                    "text": response.get("text", "")
                }
        
        return response

# Create a global instance
cloudflare = CloudflareGateway()