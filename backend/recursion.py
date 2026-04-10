from typing import List, Dict, Any, Optional
import time

try:
    import openai
    import google.generativeai as genai
except ImportError:
    pass

DEFAULT_SYSTEM_PROMPT = """You are an expert prompt engineer. Your task is to refine user prompts to be more clear, 
focused, and effective for Large Language Models. 

Guidelines for improvement:
- Make the prompt more specific and detailed
- Add necessary context and constraints
- Improve clarity and remove ambiguity
- Add structure when helpful (bullet points, numbered lists)
- Preserve the original intent and key elements

Respond ONLY with the improved prompt, no explanations."""


CRITIQUE_SYSTEM_PROMPT = """You are an expert prompt reviewer. Your task is to analyze a refined prompt and provide 
constructive criticism to further improve it.

For the given prompt, identify:
1. Remaining ambiguities or vague terms
2. Missing context that could help
3. Areas that could be more specific
4. Structural improvements possible

Provide specific, actionable feedback. If the prompt is already excellent, respond with "EXCELLENT" only."""


def create_provider_instance(provider_type: str, api_key: str, model: str, base_url: Optional[str] = None):
    """Factory function to create provider instances"""
    if provider_type == "openai":
        return OpenAIProviderWrapper(api_key, model, base_url)
    elif provider_type == "google":
        return GoogleProviderWrapper(api_key, model)
    elif provider_type == "xai":
        return xAIProviderWrapper(api_key, model)
    elif provider_type == "openrouter":
        return OpenRouterProviderWrapper(api_key, model, base_url)
    else:
        raise ValueError(f"Unknown provider: {provider_type}")


class OpenAIProviderWrapper:
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000)
        )
        return response.choices[0].message.content.strip()


class GoogleProviderWrapper:
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model
        genai.configure(api_key=api_key)
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        model = genai.GenerativeModel(self.model)
        response = model.generate_content(
            full_prompt,
            generation_config={
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 2000)
            }
        )
        return response.text.strip()


class xAIProviderWrapper:
    def __init__(self, api_key: str, model: str = "grok-2"):
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000)
        )
        return response.choices[0].message.content.strip()


class OpenRouterProviderWrapper:
    def __init__(self, api_key: str, model: str = "openai/gpt-4o", base_url: str = "https://openrouter.ai/api/v1"):
        self.api_key = api_key
        self.model = model
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 2000)
        )
        return response.choices[0].message.content.strip()


def self_refine_loop(
    prompt: str,
    provider,
    iterations: int = 3,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    critique_provider: Any = None
) -> Dict[str, Any]:
    """Self-Refine loop: generate → critique → refine → repeat"""
    history = []
    current = prompt
    
    for i in range(iterations):
        iteration_start = time.time()
        
        generation_prompt = f"""Original prompt: {prompt}

Current version: {current}

Please improve this prompt to be more clear, specific, and effective. 
Focus on making it produce better outputs when used with an LLM.

Improved prompt:"""
        
        generated = provider.generate(
            generation_prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        critique_p = critique_provider if critique_provider else provider
        
        if i < iterations - 1:
            critique_prompt = f"""Original: {prompt}
Previous: {current}
Generated: {generated}

Provide brief, actionable feedback to improve this prompt further.
If excellent, say "EXCELLENT":"""
            
            critique = critique_p.generate(
                critique_prompt,
                system_prompt=CRITIQUE_SYSTEM_PROMPT,
                temperature=0.3
            )
            
            if critique.strip() != "EXCELLENT":
                refine_prompt = f"""Original: {prompt}
Current version: {generated}
Critique: {critique}

Apply this critique to produce an improved version:"""
                
                refined = provider.generate(
                    refine_prompt,
                    system_prompt=system_prompt,
                    temperature=0.7
                )
            else:
                refined = generated
                critique = "EXCELLENT"
        else:
            refine_prompt = f"""Original: {prompt}
Previous version: {generated}
Critique: (Final iteration - no critique needed)

This is the final iteration. Polish and return the best version:"""
            
            refined = provider.generate(
                refine_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            critique = "Final iteration - polished"
        
        iteration_time = time.time() - iteration_start
        
        history.append({
            "iteration": i + 1,
            "generated": generated,
            "critique": critique,
            "refined": refined,
            "time_ms": int(iteration_time * 1000)
        })
        
        current = refined
    
    return {
        "original": prompt,
        "final": current,
        "history": history,
        "technique": "self-refine",
        "iterations": iterations
    }


def tree_of_thoughts(
    prompt: str,
    provider,
    n_versions: int = 3,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
) -> Dict[str, Any]:
    """Tree of Thoughts: generate multiple versions, evaluate, return best"""
    versions = []
    
    for i in range(n_versions):
        version_prompt = f"""Original prompt: {prompt}

Generate version {i+1} of this prompt, focusing on a different aspect or approach.
Try to make it more effective in a unique way.

Version {i+1}:"""
        
        version = provider.generate(
            version_prompt,
            system_prompt=system_prompt,
            temperature=0.9 + (i * 0.02)
        )
        
        versions.append(version)
    
    scored_versions = []
    for i, version in enumerate(versions):
        eval_prompt = f"""Original: {prompt}
Candidate: {version}

Rate this prompt from 0-100 on how effective it is for producing good LLM outputs.
Consider: clarity, specificity, structure, completeness.

Respond ONLY with a number:"""
        
        score_str = provider.generate(
            eval_prompt,
            system_prompt="You are a strict evaluator. Respond only with a number.",
            temperature=0.3
        )
        
        try:
            score = int(''.join(filter(str.isdigit, score_str.split()[0])))
        except:
            score = 50
        
        scored_versions.append({
            "version": i + 1,
            "text": version,
            "score": score
        })
    
    scored_versions.sort(key=lambda x: x["score"], reverse=True)
    
    return {
        "original": prompt,
        "final": scored_versions[0]["text"],
        "versions": scored_versions,
        "best_score": scored_versions[0]["score"],
        "technique": "toT",
        "n_versions": n_versions
    }


def basic_improve(
    prompt: str,
    provider,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
) -> Dict[str, Any]:
    """Basic single-pass improvement"""
    improvement_prompt = f"""Original prompt: {prompt}

Improve this prompt to be more clear, specific, and effective for LLM use.

Improved prompt:"""
    
    improved = provider.generate(
        improvement_prompt,
        system_prompt=system_prompt,
        temperature=0.7
    )
    
    return {
        "original": prompt,
        "final": improved,
        "technique": "none",
        "iterations": 1
    }