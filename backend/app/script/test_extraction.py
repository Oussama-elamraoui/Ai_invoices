import asyncio
import json

from app.agents.extraction_agent import extract_invoice


async def main():
    data = await extract_invoice("sample_invoice.pdf")
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())