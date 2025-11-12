#!/usr/bin/env python3
"""
GOAT Scribe CLI

Usage:
    python -m goatnote_scribe.cli "Patient presents with..."
    python -m goatnote_scribe.cli --help
"""

import argparse
import sys
from . import GOATScribe


def main():
    parser = argparse.ArgumentParser(
        description="GOAT Scribe - Emergency Medicine Documentation"
    )
    parser.add_argument(
        "clinical_text",
        nargs="?",
        help="Clinical encounter text"
    )
    parser.add_argument(
        "--patient-id",
        default="anon-001",
        help="Patient identifier (default: anon-001)"
    )
    parser.add_argument(
        "--show-guardrails",
        action="store_true",
        help="Show detailed guardrail report"
    )
    parser.add_argument(
        "--export-fhir",
        action="store_true",
        help="Export FHIR bundle to GCP"
    )
    
    args = parser.parse_args()
    
    # Read from stdin if no text provided
    if not args.clinical_text:
        if sys.stdin.isatty():
            parser.print_help()
            return 1
        args.clinical_text = sys.stdin.read().strip()
    
    try:
        # Initialize scribe
        scribe = GOATScribe()
        
        # Generate note
        result = scribe(args.clinical_text, patient_id=args.patient_id)
        
        # Print note
        print(result['note'])
        print()
        
        # Print stats
        print(f"✅ Generated {len(result['note'])} characters")
        print(f"🔒 Removed {result['phi_removed']} PHI entities")
        
        # Guardrails
        if result['guardrail_safe']:
            print("✅ All safety checks passed")
        else:
            print(f"⚠️  {result['guardrail_violations']} guardrail violation(s)")
            if args.show_guardrails:
                print()
                print(result['guardrail_report'])
        
        # FHIR export
        if args.export_fhir:
            from . import FHIRExporter
            exporter = FHIRExporter()
            response = exporter.upload_bundle(result['fhir_bundle'])
            print(f"📤 Uploaded to FHIR store: {response.get('id', 'N/A')}")
        
        # Cleanup
        scribe.wipe()
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

