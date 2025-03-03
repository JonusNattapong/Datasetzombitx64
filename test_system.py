#!/usr/bin/env python3

import asyncio
import json
from datasetzombitx64 import run

async def test_basic_functionality():
    """Test basic text processing without external API calls."""
    print("Running basic functionality test...")
    
    tasks = [
        {
            "query": "This movie was great! I really enjoyed it.",
            "task": "text_classification",
            "prompt": "Classify the sentiment of this text"
        },
        {
            "query": "John works at Microsoft in Seattle.",
            "task": "token_classification",
            "prompt": "Extract named entities"
        }
    ]
    
    output_path = await run(
        tasks,
        name="test_output",
        output_format="json",
        mistral_key="dummy",
        youtube_key="dummy",
        google_key="dummy",
        cse_id="dummy"
    )
    
    if output_path:
        print(f"\nTest output saved to: {output_path}")
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                results = json.load(f)
                print("\nTest Results:")
                for result in results:
                    print(f"\nTask: {result['task']}")
                    print(f"Input: {result['query']}")
                    print(f"Result: {result['result']}")
        except Exception as e:
            print(f"Error reading results: {str(e)}")
    else:
        print("\nTest failed - no output generated")

if __name__ == "__main__":
    print("Dataset Collection and Processing Pipeline - System Test")
    print("====================================================")
    
    # Run tests
    asyncio.run(test_basic_functionality())
