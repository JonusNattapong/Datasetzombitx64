#!/usr/bin/env python3

import asyncio
from datasetzombitx64 import run

async def example_1_basic_text_processing():
    """Example 1: Basic text processing using local models."""
    print("\nExample 1: Basic Text Processing")
    print("--------------------------------")
    
    tasks = [
        {
            "query": "The food at this restaurant was amazing! Best service ever!",
            "task": "text_classification",
            "prompt": "Classify the sentiment"
        }
    ]
    
    await run(
        tasks,
        name="sentiment_analysis",
        deepseek_key="your_key",
        mistral_key="your_key",
        youtube_key="your_key",
        google_key="your_key",
        cse_id="your_cse_id"
    )

async def example_2_youtube_summarization():
    """Example 2: Summarize YouTube video content."""
    print("\nExample 2: YouTube Video Summarization")
    print("-------------------------------------")
    
    tasks = [
        {
            "source": "youtube",
            "query": "https://www.youtube.com/watch?v=example",
            "task": "summarization",
            "prompt": "Provide a concise summary of the video content",
            "use_api": "deepseek"
        }
    ]
    
    await run(
        tasks,
        name="youtube_summaries",
        deepseek_key="your_key",
        mistral_key="your_key",
        youtube_key="your_key",
        google_key="your_key",
        cse_id="your_cse_id"
    )

async def example_3_web_analysis():
    """Example 3: Analyze web content."""
    print("\nExample 3: Web Content Analysis")
    print("------------------------------")
    
    tasks = [
        {
            "source": "web",
            "query": "https://example.com/article",
            "task": "token_classification",
            "prompt": "Extract organization names and locations"
        },
        {
            "source": "web",
            "query": "https://example.com/article",
            "task": "summarization",
            "prompt": "Summarize the main points"
        }
    ]
    
    await run(
        tasks,
        name="web_analysis",
        deepseek_key="your_key",
        mistral_key="your_key",
        youtube_key="your_key",
        google_key="your_key",
        cse_id="your_cse_id"
    )

async def example_4_pdf_processing():
    """Example 4: Process PDF documents."""
    print("\nExample 4: PDF Document Processing")
    print("--------------------------------")
    
    tasks = [
        {
            "source": "pdf",
            "query": "path/to/document.pdf",
            "task": "summarization",
            "prompt": "Extract key findings and conclusions"
        }
    ]
    
    await run(
        tasks,
        name="pdf_summaries",
        deepseek_key="your_key",
        mistral_key="your_key",
        youtube_key="your_key",
        google_key="your_key",
        cse_id="your_cse_id"
    )

async def example_5_multi_source():
    """Example 5: Combine multiple sources and tasks."""
    print("\nExample 5: Multi-source Analysis")
    print("------------------------------")
    
    tasks = [
        # YouTube video analysis
        {
            "source": "youtube",
            "query": "https://www.youtube.com/watch?v=example1",
            "task": "summarization",
            "use_api": "deepseek"
        },
        # Google search results
        {
            "source": "google",
            "query": "latest AI developments",
            "task": "text_classification",
            "use_api": "mistral"
        },
        # Web page analysis
        {
            "source": "web",
            "query": "https://example.com/tech-news",
            "task": "token_classification"
        },
        # PDF document processing
        {
            "source": "pdf",
            "query": "report.pdf",
            "task": "summarization"
        }
    ]
    
    await run(
        tasks,
        name="multi_source_analysis",
        output_format="json",
        deepseek_key="your_key",
        mistral_key="your_key",
        youtube_key="your_key",
        google_key="your_key",
        cse_id="your_cse_id"
    )

def print_usage():
    """Print usage instructions."""
    print("\nDataset Collection and Processing Pipeline - Usage Examples")
    print("======================================================")
    print("\nBefore running examples:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Replace 'your_key' with actual API keys in each example")
    print("3. For PDF examples, update file paths to your documents")
    print("4. For YouTube examples, use actual video URLs")
    print("\nRun individual examples by commenting/uncommenting them in main()")

async def main():
    """Run the example scripts."""
    print_usage()
    
    # Uncomment examples you want to run
    await example_1_basic_text_processing()
    # await example_2_youtube_summarization()
    # await example_3_web_analysis()
    # await example_4_pdf_processing()
    # await example_5_multi_source()

if __name__ == "__main__":
    asyncio.run(main())
