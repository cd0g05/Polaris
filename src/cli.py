import argparse
import logging
import sys
import dotenv
dotenv.load_dotenv()

from anyio import sleep

from src.data_retriever import StockItToMe, StockPriceRetriever, StubStockPriceRetriever, AlphavantageStockRetriever
from src.endpoints import DiscordEndpoint
from src.llm import AiService, StubAiService, OpenaiAiService, Api

logger: logging.Logger = logging.getLogger(__package__)

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,  # Set the logging level
        format='%(asctime)s [%(levelname)s] - %(message)s',  # Define the log message format
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    logger.info("Starting...")
    parser = argparse.ArgumentParser(description='scrAIbe launcher')
    parser.add_argument('--working_dir', type=str, default='working',
                        help='Path to parent location of working directories')
    parser.add_argument('-u', '--user_name', type=str, default=None,
                        help='Name of the project working directory (only needed if drafting without first generating)')
    parser.add_argument('-s', '--stock_stub', action="store_true",
                        help='Use stock stub')
    parser.add_argument('-a', '--ai_stub', action="store_true",
                        help='Use AI stub')

    args = parser.parse_args()

    if args.stock_stub:
        logger.debug("creating stub stock service")
        service:StockPriceRetriever = StubStockPriceRetriever()
    else:
        logger.debug("creating Alpha stock service")
        service:StockPriceRetriever = AlphavantageStockRetriever()

    if args.ai_stub:
        aiservice:AiService = StubAiService()
    else:
        aiservice:AiService = OpenaiAiService()

    endpoint: DiscordEndpoint = DiscordEndpoint(service, aiservice)
    # runner = StockItToMe(service)
    # runner.service_user(args.user_name)
    # airunner = Api(aiservice)
    # airunner.get_response("/Users/cartercripe/dev/code/projects/stockittome/working/output.txt")
