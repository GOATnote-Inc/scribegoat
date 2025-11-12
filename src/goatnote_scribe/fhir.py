"""GCP FHIR R4 export integration"""

import subprocess
from typing import Dict, Optional

import requests

from .config import ScribeConfig


class FHIRExporter:
    """
    GCP Healthcare API FHIR R4 exporter.
    
    Handles uploading FHIR bundles to GCP Healthcare API and retrieving
    patient resources. Uses gcloud CLI for authentication.
    
    Example:
        >>> from goatnote_scribe import FHIRExporter
        >>> exporter = FHIRExporter()
        >>> bundle = {...}  # FHIR R4 bundle
        >>> response = exporter.upload_bundle(bundle)
        >>> print(response['id'])
    """
    
    def __init__(self, config: Optional[ScribeConfig] = None):
        """
        Initialize FHIR exporter.
        
        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or ScribeConfig.from_env()
        
        self.project_id = self.config.gcp_project_id
        self.location = self.config.gcp_location
        self.dataset = self.config.gcp_dataset
        self.fhir_store = self.config.gcp_fhir_store
        
        self.base_url = (
            f"https://healthcare.googleapis.com/v1/"
            f"projects/{self.project_id}/"
            f"locations/{self.location}/"
            f"datasets/{self.dataset}/"
            f"fhirStores/{self.fhir_store}/fhir"
        )
    
    def get_token(self) -> str:
        """
        Get GCP access token via gcloud CLI.
        
        Returns:
            GCP OAuth2 access token
            
        Raises:
            RuntimeError: If gcloud auth fails
        """
        result = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to get GCP auth token: {result.stderr}. "
                "Run: gcloud auth application-default login"
            )
        
        return result.stdout.strip()
    
    def upload_bundle(self, bundle: Dict) -> Dict:
        """
        Upload FHIR R4 bundle to GCP Healthcare API.
        
        Args:
            bundle: FHIR R4 Bundle resource
            
        Returns:
            Response from GCP Healthcare API
            
        Raises:
            requests.HTTPError: If upload fails
            ValueError: If bundle is invalid
        """
        if not bundle or bundle.get("resourceType") != "Bundle":
            raise ValueError("Invalid FHIR Bundle: must have resourceType='Bundle'")
        
        headers = {
            "Authorization": f"Bearer {self.get_token()}",
            "Content-Type": "application/fhir+json"
        }
        
        response = requests.post(
            self.base_url,
            json=bundle,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def get_patient(self, patient_id: str) -> Dict:
        """
        Retrieve patient resource from FHIR store.
        
        Args:
            patient_id: Patient identifier
            
        Returns:
            FHIR Patient resource
            
        Raises:
            requests.HTTPError: If patient not found or retrieval fails
        """
        headers = {
            "Authorization": f"Bearer {self.get_token()}"
        }
        
        response = requests.get(
            f"{self.base_url}/Patient/{patient_id}",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def search_documents(
        self,
        patient_id: Optional[str] = None,
        limit: int = 10
    ) -> Dict:
        """
        Search for DocumentReference resources.
        
        Args:
            patient_id: Optional patient ID to filter by
            limit: Maximum number of results
            
        Returns:
            FHIR Bundle of search results
        """
        params = {"_count": limit}
        if patient_id:
            params["subject"] = f"Patient/{patient_id}"
        
        headers = {
            "Authorization": f"Bearer {self.get_token()}"
        }
        
        response = requests.get(
            f"{self.base_url}/DocumentReference",
            params=params,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()

