import json
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.evaluation.models import EvaluationResult
from src.services.rag_service import RAGService
from src.utils.logger import logger


class EvaluationRunner:
    """
    Runs a batch evaluation against the RAG workflow and
    exports the results as a CSV report.
    """

    def __init__(self):

        self.rag = RAGService()

        self.dataset_path = (
            Path(__file__).parent
            / "datasets"
            / "test_queries.json"
        )

        self.results_dir = (
            Path(__file__).parent
            / "results"
        )

        self.results_dir.mkdir(
            exist_ok=True,
            parents=True,
        )

    def load_dataset(self):

        with open(
            self.dataset_path,
            "r",
            encoding="utf-8",
        ) as f:

            return json.load(f)

    def run(self):

        dataset = self.load_dataset()

        logger.info("=" * 100)
        logger.info(
            f"Starting Evaluation ({len(dataset)} test cases)"
        )
        logger.info("=" * 100)

        results = []

        for idx, sample in enumerate(dataset, start=1):

            query = sample["query"]
            category = sample["category"]

            logger.info("")
            logger.info("-" * 100)
            logger.info(
                f"[{idx}/{len(dataset)}] {category.upper()}"
            )
            logger.info(f"Query : {query}")

            start = time.perf_counter()

            try:

                # Return complete workflow state
                state = self.rag.ask(
                    query=query,
                    return_state=True,
                )

                latency = time.perf_counter() - start

                logger.info(
                    f"Completed in {latency:.3f}s"
                )

                results.append(

                    EvaluationResult(

                        query=query,

                        category=category,

                        response=state["answer"],

                        latency=latency,

                        success=True,

                        metadata=state.get(
                            "metadata",
                            {},
                        ),

                    )

                )

            except Exception as e:

                latency = time.perf_counter() - start

                logger.exception(e)

                results.append(

                    EvaluationResult(

                        query=query,

                        category=category,

                        response=str(e),

                        latency=latency,

                        success=False,

                        metadata={},

                    )

                )

        self.save_results(results)

    def save_results(self, results):

        dataframe = pd.DataFrame(

            [
                result.to_dict()
                for result in results
            ]

        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output_file = (
            self.results_dir
            / f"evaluation_{timestamp}.csv"
        )

        dataframe.to_csv(
            output_file,
            index=False,
        )

        logger.info("")
        logger.info("=" * 100)
        logger.info("Evaluation Complete")
        logger.info(f"Results saved to : {output_file}")
        logger.info("=" * 100)


def main():

    runner = EvaluationRunner()

    runner.run()


if __name__ == "__main__":

    main()