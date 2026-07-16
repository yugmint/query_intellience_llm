from time import perf_counter

from src.ingestion.config import IngestionConfig

from src.ingestion.loaders.factory import LoaderFactory
from src.ingestion.cleaners.factory import CleanerFactory
from src.ingestion.chunkers.hybrid_chunker import HybridChunker
from src.ingestion.metadata.generator import MetadataGenerator
from src.ingestion.indexers.faiss_indexer import FAISSIndexer

from src.retrieval.embeddings import EmbeddingFactory

from src.utils.logger import logger


class IngestionPipeline:
    """
    End-to-end document ingestion pipeline.
    """

    def __init__(self):

        self.config = IngestionConfig()

        # Long-lived shared components
        self.cleaner = CleanerFactory.build()

        self.chunker = HybridChunker(
            self.config,
        )

        self.metadata = MetadataGenerator()

        self.embeddings = EmbeddingFactory.get()

        self.indexer = FAISSIndexer()

    def ingest(
        self,
        file_path: str,
    ):

        start = perf_counter()

        logger.info("=" * 80)
        logger.info(f"Ingesting : {file_path}")

        # Loader is document-specific
        loader = LoaderFactory.build(file_path)

        documents = loader.load(file_path)

        documents = self.cleaner.clean(documents)

        chunks = self.chunker.chunk(documents)

        chunks = self.metadata.generate(
            chunks,
            file_path,
        )

        vectorstore = self.indexer.build(
            chunks,
            self.embeddings,
        )

        self.indexer.save(
            vectorstore,
            self.config.index_path,
        )

        elapsed = perf_counter() - start

        logger.info("=" * 80)
        logger.info(
            f"Ingestion completed in {elapsed:.2f}s"
        )

        return chunks