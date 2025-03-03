#!/usr/bin/env python3

import os
import json
import csv
import requests
from dotenv import load_dotenv
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
import PyPDF2
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import traceback
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def print_ascii_art():
    ascii_art = """
███████╗ ██████╗ ███╗   ███╗██████╗ ██╗████████╗██╗  ██╗ ██████╗ ██╗  ██╗
╚══███╔╝██╔═══██╗████╗ ████║██╔══██╗██║╚══██╔══╝╚██╗██╔╝██╔════╝ ██║  ██║
  ███╔╝ ██║   ██║██╔████╔██║██████╔╝██║   ██║    ╚███╔╝ ███████╗ ███████║
 ███╔╝  ██║   ██║██║╚██╔╝██║██╔══██╗██║   ██║    ██╔██╗ ██╔═══██╗╚════██║
███████╗╚██████╔╝██║ ╚═╝ ██║██████╔╝██║   ██║   ██╔╝ ██╗╚██████╔╝     ██║
╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚═╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝      ╚═╝
    """
    print(ascii_art)
    os.makedirs("datasets", exist_ok=True)

def filter_text(text: str) -> str:
    """Removes non-ASCII characters from the text."""
    return ''.join(char for char in text if ord(char) < 128)

# Display utility class
class Display:
    """Utility class for displaying messages with emojis."""
    EMOJIS = {"loading": "⏳", "processing": "🔄", "done": "✅", "error": "❌", "info": "ℹ️", "warning": "⚠️"}
    
    @staticmethod
    def message(type_key: str, message: str, end: str = "\n") -> None:
        emoji = Display.EMOJIS.get(type_key, "ℹ️")
        print(f"{emoji} {message}", end=end)

# API Client class for Mistral
class APIClient:
    """Handles API requests to Mistral."""
    def __init__(self, mistral_key: str) -> None:
        self.mistral_key = mistral_key
        self.mistral_url = "https://api.mistral.ai/v1/chat/completions"
        Display.message("warning", "Ensure compliance with Mistral Terms of Service.")

    async def process_text(self, task: str, text: str, prompt: str) -> Optional[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {self.mistral_key}", 
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistral-large-latest",
            "messages": [{"role": "user", "content": f"Task: {task}\nPrompt: {prompt}\nText: {text}"}],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        text = filter_text(text)
        if len(text) > 500:
            text = text[:500]

        retries = 5
        delay = 3  # Initial delay in seconds
        timeout = aiohttp.ClientTimeout(total=60, connect=30)  # Increased timeout

        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(self.mistral_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            result = {"result": data["choices"][0]["message"]["content"]}
                            Display.message("done", f"Mistral processed {task}")
                            return result
                        elif response.status == 429:
                            Display.message("warning", f"Rate limit hit. Retrying in {delay} seconds...")
                            await asyncio.sleep(delay)
                            delay *= 2  # Exponential backoff
                            continue
                        else:
                            Display.message("error", f"Mistral API failed: {response.status}")
                            if attempt < retries - 1:  # If not the last attempt
                                await asyncio.sleep(delay)
                                delay *= 2
                                continue
                            return None
            except asyncio.TimeoutError:
                Display.message("error", f"Request timeout. Retrying... (Attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                Display.message("error", "All retry attempts failed due to timeout")
                return None
            except Exception as e:
                Display.message("error", f"Unexpected error: {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                    delay *= 2
                    continue
                return None
        
        Display.message("error", "All retry attempts failed")
        return None

# Data fetcher class
class DataFetcher:
    """Fetches data from various sources like YouTube, Google, Web, and PDF."""
    def __init__(self, youtube_key: str, google_key: str, cse_id: str) -> None:
        self.youtube_key = youtube_key
        self.google_key = google_key
        self.cse_id = cse_id
        self.youtube = build("youtube", "v3", developerKey=self.youtube_key)
        self.google_search = build("customsearch", "v1", developerKey=self.google_key)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})
        Display.message("warning", "Ensure API usage complies with YouTube and Google Terms of Service. Check quota limits.")

    def fetch_youtube_data(self, url: str) -> str:
        Display.message("processing", f"Fetching YouTube data: {url}", end="\r")
        try:
            video_id = url.split("v=")[1].split("&")[0] if "v=" in url else url.split("/")[-1]
            video_request = self.youtube.videos().list(part="snippet", id=video_id)
            video_response = video_request.execute()
            snippet = video_response["items"][0]["snippet"]
            content = f"Title: {snippet['title']}\nDescription: {snippet['description']}"
            Display.message("done", f"Fetched YouTube data: {url}")
            return content
        except HttpError as e:
            Display.message("error", f"YouTube API error: {str(e)}")
            return ""

    def search_google(self, query: str, num_results: int = 5) -> str:
        Display.message("processing", f"Searching Google: {query}", end="\r")
        try:
            response = self.google_search.cse().list(q=query, cx=self.cse_id, num=num_results).execute()
            search_results = ""
            for item in response["items"]:
                search_results += f"Title: {item['title']}\nLink: {item['link']}\nSnippet: {item['snippet']}\n\n"
            Display.message("done", f"Google search completed: Found {len(response['items'])} results")
            return search_results
        except HttpError as e:
            Display.message("error", f"Google API error: {str(e)}")
            return ""

    def can_scrape(self, url: str) -> bool:
        """Checks if scraping is allowed per Robots.txt."""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch("Mozilla/5.0", url)
        except Exception:
            Display.message("warning", f"Could not check Robots.txt for {url}. Proceed at your own risk.")
            return False

    async def fetch_web_content(self, url: str) -> str:
        Display.message("processing", f"Fetching web content from {url}", end="\r")
        if not self.can_scrape(url):
            Display.message("error", f"Scraping not allowed by {url} Robots.txt")
            return ""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        content = soup.get_text(separator="\n").strip()
                        Display.message("done", f"Fetched web content from {url}")
                        Display.message("warning", f"Ensure {url} Terms of Service allows scraping.")
                        return content
                    return ""
            except Exception as e:
                Display.message("error", f"Web fetch error: {str(e)}")
            return ""

    def read_pdf(self, url_or_path: str) -> str:
        Display.message("processing", f"Reading PDF: {url_or_path}", end="\r")
        Display.message("warning", f"Ensure {url_or_path} is public domain or you have permission to use.")
        try:
            if url_or_path.startswith("http"):
                local_path = "temp.pdf"
                response = self.session.get(url_or_path)
                response.raise_for_status()
                with open(local_path, "wb") as f:
                    f.write(response.content)
                pdf_path = local_path
            else:
                pdf_path = url_or_path.replace("[", "").replace("]", "")
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = "".join([page.extract_text() or "" for page in reader.pages])
            # Always remove temp.pdf after processing
            if url_or_path.startswith("http") and os.path.exists(pdf_path):
                try:
                    os.remove(pdf_path)
                except Exception as e:
                    Display.message("error", f"Failed to delete temp file: {e}")
            Display.message("done", f"Read PDF: {url_or_path}")
            return text
        except Exception as e:
            Display.message("error", f"PDF error: {str(e)}")
            return ""

    async def fetch_data(self, source: str, query: str) -> Dict[str, str]:
        if source == "youtube":
            content = self.fetch_youtube_data(query)
        elif source == "google":
            content = self.search_google(query)
        elif source == "web":
            content = await self.fetch_web_content(query)
        elif source == "pdf":
            content = self.read_pdf(query)
        else:
            Display.message("error", f"Unsupported source: {source}")
            return {"source": source, "query": query, "content": ""}
        return {"source": source, "query": query, "content": content}

# Dataset builder class
class DatasetBuilder:
    """Builds and saves datasets from fetched and processed data."""
    def __init__(self, mistral_key: str, youtube_key: str, google_key: str, cse_id: str) -> None:
        self.api_client = APIClient(mistral_key)
        self.data_fetcher = DataFetcher(youtube_key, google_key, cse_id)

    async def process_task(self, task_info: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Processes a single task with data fetching and processing."""
        source = task_info.get("source", "direct")
        query = task_info["query"]
        task = task_info["task"]
        prompt = task_info.get("prompt", "")

        if source != "direct":
            fetched = await self.data_fetcher.fetch_data(source, query)
            if not fetched["content"]:
                return None
            text = fetched["content"]
        else:
            text = query

        result = await self.api_client.process_text(task, text, prompt)
        if result:
            return {
                "source": source,
                "query": query,
                "task": task,
                "prompt": prompt,
                "content": text,
                "result": result,
                "processed_by": "mistral"
            }
        return None

    def save_dataset(self, data: List[Dict[str, Any]], name: str, output_format: str = "json") -> Optional[str]:
        """Saves the dataset."""
        os.makedirs("datasets", exist_ok=True)
        path = f"datasets/{name}.{output_format}"
        try:
            if output_format == "json":
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif output_format == "csv":
                with open(path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["source", "query", "task", "prompt", "content", "result", "processed_by"])
                    writer.writeheader()
                    writer.writerows(data)
            Display.message("done", f"Saved dataset at {path}")
            return path
        except Exception as e:
            Display.message("error", f"Failed to save dataset: {str(e)}")
            return None

# Main function
async def run(
    tasks: List[Dict[str, str]],
    name: str = "dataset",
    output_format: str = "json",
    mistral_key: str = "",
    youtube_key: str = "",
    google_key: str = "",
    cse_id: str = ""
) -> Optional[str]:
    """Main function to run the data collection and processing pipeline."""
    if not all([mistral_key]):
        Display.message("error", "Missing Mistral API key")
        return None
    
    builder = DatasetBuilder(mistral_key, youtube_key, google_key, cse_id)
    tasks_list = asyncio.gather(*[builder.process_task(task) for task in tasks])
    results = await tasks_list
    dataset = [r for r in results if r]
    return builder.save_dataset(dataset, name, output_format)

def get_user_tasks():
    """Get tasks interactively from the user."""
    tasks = []
    print("\nAvailable sources:")
    print("1. YouTube (requires YouTube API key)")
    print("2. Google Search (requires Google API key)")
    print("3. Web Page")
    print("4. PDF File")
    print("5. Direct Text")
    print("6. Done adding tasks")
    
    while True:
        try:
            # Strip whitespace and handle empty input
            choice_str = input("\nSelect source (1-6): ").strip()
            if not choice_str:
                print("Please enter a number between 1-6.")
                continue
                
            choice = int(choice_str)
            if choice == 6:
                break
            
            if choice not in [1, 2, 3, 4, 5]:
                print("Invalid choice. Please select 1-6.")
                continue
            
            task = {}
            
            # Set source based on choice
            sources = {1: "youtube", 2: "google", 3: "web", 4: "pdf"}
            if choice != 5:  # If not direct text
                task["source"] = sources[choice]
            
            # Get query based on source and validate
            while True:
                if choice == 1:
                    query = input("\nEnter YouTube video URL (must contain 'youtube.com/watch?v=' or 'youtu.be/'): ").strip()
                    if "youtube.com/watch?v=" in query or "youtu.be/" in query:
                        task["query"] = query
                        break
                    print("Invalid YouTube URL. Please try again.")
                elif choice == 2:
                    query = input("\nEnter search query: ").strip()
                    if query:
                        task["query"] = query
                        break
                    print("Search query cannot be empty. Please try again.")
                elif choice == 3:
                    query = input("\nEnter web page URL (must start with http:// or https://): ").strip()
                    if query.startswith(("http://", "https://")):
                        task["query"] = query
                        break
                    print("Invalid URL. Must start with http:// or https://")
                elif choice == 4:
                    query = input("\nEnter PDF file path or URL (if URL, must end with .pdf): ").strip()
                    if query.startswith(("http://", "https://")):
                        if not query.endswith(".pdf"):
                            print("URL must end with .pdf")
                            continue
                    task["query"] = query
                    break
                else:  # Direct text
                    query = input("\nEnter text to process: ").strip()
                    if query:
                        task["query"] = query
                        break
                    print("Text cannot be empty. Please try again.")
            
            print("\nAvailable tasks:")
            print("1. Summarize")
            print("2. Analyze")
            print("3. Extract key points")
            print("4. Classify")
            
            task_choice = int(input("Select task (1-4): "))
            task_types = {1: "summarize", 2: "analyze", 3: "extract", 4: "classify"}
            task["task"] = task_types.get(task_choice, "summarize")
            
            task["prompt"] = input("Enter prompt (or press Enter for default): ").strip()
            if not task["prompt"]:
                default_prompts = {
                    "summarize": "Summarize the content",
                    "analyze": "Analyze the main points and sentiment",
                    "extract": "Extract key information and findings",
                    "classify": "Classify the topic and sentiment"
                }
                task["prompt"] = default_prompts[task["task"]]
            
            tasks.append(task)
            print(f"\n✅ Task {len(tasks)} added successfully")
            
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            print(f"Error: {str(e)}")
    
    return tasks

if __name__ == "__main__":
    load_dotenv()
    print_ascii_art()

    # Load API keys from .env or config.json
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {"mistral_api_key": "", "youtube_api_key": "", "google_api_key": "", "cse_id": ""}

    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", config["mistral_api_key"])
    YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", config["youtube_api_key"])
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", config["google_api_key"])
    CSE_ID = os.getenv("CSE_ID", config["cse_id"])

    if not MISTRAL_API_KEY:
        Display.message("error", "Missing Mistral API key in .env or config.json")
        exit(1)

    Display.message("info", "Starting interactive task creation...")
    tasks = get_user_tasks()

    if not tasks:
        Display.message("error", "No tasks provided")
        exit(1)

    output_path = asyncio.run(run(
        tasks,
        name="multi_source_dataset",
        mistral_key=MISTRAL_API_KEY,
        youtube_key=YOUTUBE_API_KEY,
        google_key=GOOGLE_API_KEY,
        cse_id=CSE_ID
    ))

    if output_path:
        print(f"\nDataset saved at: {output_path}")
