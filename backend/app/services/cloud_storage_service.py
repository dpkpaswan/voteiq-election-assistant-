"""
Google Cloud Storage integration for VoteIQ
Manages knowledge base files and election data in GCS buckets
"""

import json
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CloudStorageService:
    """
    Google Cloud Storage for managing election knowledge base.

    Uses GCS to store and retrieve:
    - Election knowledge base JSON
    - Timeline data
    - Regional election configurations

    Falls back to local filesystem when GCS is unavailable.
    """

    def __init__(self, bucket_name: Optional[str] = None):
        self._client = None
        self._bucket = None
        self._available: bool = False
        self._bucket_name: str = bucket_name or os.getenv(
            "GCS_KNOWLEDGE_BUCKET", "voteiq-knowledge-base"
        )
        self._init_client()

    def _init_client(self) -> None:
        """Initialize GCS client and bucket reference"""
        try:
            from google.cloud import storage

            self._client = storage.Client()
            self._bucket = self._client.bucket(self._bucket_name)
            self._available = True
            logger.info(f"☁️ Google Cloud Storage initialized (bucket: {self._bucket_name})")

        except ImportError:
            logger.info("google-cloud-storage not installed, using local files")
        except Exception as e:
            logger.warning(f"GCS init failed ({e}), using local files")

    @property
    def is_available(self) -> bool:
        """Check if GCS is connected"""
        return self._available and self._bucket is not None

    def load_knowledge_base(self, blob_name: str = "election_knowledge.json") -> Dict[str, Any]:
        """
        Load election knowledge base from GCS or local fallback.

        Priority:
        1. Google Cloud Storage (production)
        2. Local data/ directory (development)

        Args:
            blob_name: Object name in the GCS bucket

        Returns:
            Knowledge base dictionary
        """
        # Try GCS first
        if self.is_available:
            try:
                blob = self._bucket.blob(blob_name)
                if blob.exists():
                    content = blob.download_as_text()
                    data = json.loads(content)
                    logger.info(f"Knowledge base loaded from GCS: {blob_name}")
                    return data
            except Exception as e:
                logger.warning(f"GCS load failed ({e}), falling back to local")

        # Fallback to local file
        return self._load_local_knowledge(blob_name)

    def _load_local_knowledge(self, filename: str) -> Dict[str, Any]:
        """Load knowledge base from local filesystem"""
        local_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            filename
        )

        try:
            with open(local_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Knowledge base loaded from local: {local_path}")
                return data
        except FileNotFoundError:
            logger.warning(f"Local knowledge file not found: {local_path}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load local knowledge: {e}")
            return {}

    def save_knowledge_base(
        self,
        data: Dict[str, Any],
        blob_name: str = "election_knowledge.json"
    ) -> bool:
        """
        Upload updated knowledge base to GCS.

        Args:
            data: Knowledge base dictionary
            blob_name: Target object name in GCS

        Returns:
            True if upload successful
        """
        if not self.is_available:
            logger.info("GCS not available, skipping cloud upload")
            return False

        try:
            blob = self._bucket.blob(blob_name)
            content = json.dumps(data, indent=2, ensure_ascii=False)
            blob.upload_from_string(content, content_type="application/json")
            logger.info(f"Knowledge base uploaded to GCS: {blob_name}")
            return True

        except Exception as e:
            logger.error(f"GCS upload failed: {e}")
            return False

    def list_available_data(self) -> list:
        """List all available data files in the GCS bucket"""
        if not self.is_available:
            return []

        try:
            blobs = self._bucket.list_blobs(prefix="", max_results=50)
            return [blob.name for blob in blobs]
        except Exception as e:
            logger.error(f"GCS list failed: {e}")
            return []
