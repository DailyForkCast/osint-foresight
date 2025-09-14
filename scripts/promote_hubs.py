#!/usr/bin/env python3
"""
Hub promotion script with transaction support and rollback capability.
Ensures atomic updates to hub configuration files.
"""

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class HubPromotionError(Exception):
    """Custom exception for hub promotion failures."""
    pass


class HubPromoter:
    """Manages hub promotion with transaction support."""

    def __init__(self, country: str, config_file: str):
        self.country = country
        self.config_file = Path(config_file)
        self.backup_file = None
        self.temp_file = None
        self.transaction_log = []

    def start_transaction(self):
        """Begin a transaction by creating backups."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create backup of existing config
        if self.config_file.exists():
            self.backup_file = self.config_file.with_suffix(f'.bak.{timestamp}')
            shutil.copy2(self.config_file, self.backup_file)
            self.transaction_log.append(f"Created backup: {self.backup_file}")
            logger.info(f"Backed up existing config to {self.backup_file}")

        # Create temp file for new config
        fd, self.temp_file = tempfile.mkstemp(suffix='.tmp', prefix='hubs_',
                                              dir=self.config_file.parent)
        os.close(fd)
        self.transaction_log.append(f"Created temp file: {self.temp_file}")

    def rollback(self, error_msg: str = None):
        """Rollback the transaction on error."""
        logger.error(f"Rolling back transaction: {error_msg}")

        # Remove temp file
        if self.temp_file and os.path.exists(self.temp_file):
            os.remove(self.temp_file)
            logger.info(f"Removed temp file: {self.temp_file}")

        # Restore backup if it exists
        if self.backup_file and self.backup_file.exists():
            if self.config_file.exists():
                os.remove(self.config_file)
            shutil.move(str(self.backup_file), str(self.config_file))
            logger.info(f"Restored config from backup: {self.backup_file}")

        # Log transaction history
        logger.info("Transaction log:")
        for entry in self.transaction_log:
            logger.info(f"  {entry}")

    def commit(self):
        """Commit the transaction by moving temp file to final location."""
        try:
            # Validate temp file exists and is valid
            if not self.temp_file or not os.path.exists(self.temp_file):
                raise HubPromotionError("No temp file to commit")

            # Atomic move (on same filesystem)
            shutil.move(self.temp_file, str(self.config_file))
            logger.info(f"Committed new config to {self.config_file}")

            # Clean up old backups (keep last 5)
            self._cleanup_old_backups()

            # Log success
            self.transaction_log.append(f"Transaction committed successfully")
            logger.info("Transaction completed successfully")

        except Exception as e:
            self.rollback(f"Commit failed: {str(e)}")
            raise

    def _cleanup_old_backups(self):
        """Keep only the 5 most recent backups."""
        backup_pattern = f"{self.config_file.stem}.bak.*"
        backups = sorted(self.config_file.parent.glob(backup_pattern))

        if len(backups) > 5:
            for old_backup in backups[:-5]:
                old_backup.unlink()
                logger.debug(f"Removed old backup: {old_backup}")

    def load_existing_config(self) -> Dict[str, Any]:
        """Load existing hub configuration."""
        if not self.config_file.exists():
            logger.info("No existing config file, starting fresh")
            return {
                'COUNTRY': self.country,
                'HUBS': [],
                'AUTO_HUBS': [],
                'PROMOTION_HISTORY': []
            }

        try:
            # Handle both Makefile format and JSON format
            if self.config_file.suffix == '.conf':
                return self._parse_makefile_config()
            else:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            raise HubPromotionError(f"Failed to load existing config: {str(e)}")

    def _parse_makefile_config(self) -> Dict[str, Any]:
        """Parse Makefile-style config file."""
        config = {
            'COUNTRY': self.country,
            'HUBS': [],
            'AUTO_HUBS': [],
            'PROMOTION_HISTORY': []
        }

        with open(self.config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('HUBS'):
                    # Parse: HUBS ?= hub1 hub2 hub3
                    parts = line.split('?=', 1)
                    if len(parts) == 2:
                        config['HUBS'] = parts[1].strip().split()
                elif line.startswith('AUTO_HUBS'):
                    # Parse: AUTO_HUBS ?= hub4 hub5
                    parts = line.split('?=', 1)
                    if len(parts) == 2:
                        config['AUTO_HUBS'] = parts[1].strip().split()

        return config

    def validate_proposals(self, proposals: List[Dict]) -> List[Dict]:
        """Validate hub proposals meet promotion criteria."""
        valid_proposals = []

        for proposal in proposals:
            errors = []

            # Check required fields
            required_fields = ['name', 'domains', 'scores', 'recommendation']
            for field in required_fields:
                if field not in proposal:
                    errors.append(f"Missing required field: {field}")

            # Check recommendation
            if proposal.get('recommendation') != 'promote':
                logger.info(f"Skipping {proposal.get('name')}: recommendation is {proposal.get('recommendation')}")
                continue

            # Check decision
            if proposal.get('decision') == 'rejected':
                logger.info(f"Skipping {proposal.get('name')}: already rejected")
                continue

            # Check QA criteria
            qa = proposal.get('qa', {})
            if not qa.get('alias_clean', False):
                errors.append("Alias not clean")
            if qa.get('governance_risk') == 'High':
                errors.append("Governance risk too high")

            # Check evidence sources
            if proposal.get('evidence_sources', 0) < 2:
                errors.append("Insufficient evidence sources")

            # Check z-scores
            scores = proposal.get('scores', {})
            high_scores = sum(1 for v in scores.values() if v and v >= 2.0)
            if high_scores < 2:
                errors.append("Insufficient high z-scores")

            if errors:
                logger.warning(f"Validation failed for {proposal.get('name')}: {', '.join(errors)}")
            else:
                valid_proposals.append(proposal)
                logger.info(f"Validated proposal: {proposal.get('name')}")

        return valid_proposals

    def write_config(self, config: Dict[str, Any]):
        """Write configuration to temp file."""
        try:
            if self.config_file.suffix == '.conf':
                self._write_makefile_config(config)
            else:
                with open(self.temp_file, 'w') as f:
                    json.dump(config, f, indent=2)
        except Exception as e:
            raise HubPromotionError(f"Failed to write config: {str(e)}")

    def _write_makefile_config(self, config: Dict[str, Any]):
        """Write Makefile-style config file."""
        with open(self.temp_file, 'w') as f:
            f.write(f"# Hub configuration for {config['COUNTRY']}\n")
            f.write(f"# Generated: {datetime.now().isoformat()}\n\n")

            # Write main hubs
            if config['HUBS']:
                f.write(f"HUBS ?= {' '.join(config['HUBS'])}\n")

            # Write auto-promoted hubs
            if config['AUTO_HUBS']:
                f.write(f"AUTO_HUBS ?= {' '.join(config['AUTO_HUBS'])}\n")

            # Write promotion history as comments
            if config.get('PROMOTION_HISTORY'):
                f.write("\n# Promotion History:\n")
                for entry in config['PROMOTION_HISTORY']:
                    f.write(f"# {entry}\n")

    def promote_hubs(self, auto_hubs_file: str, policy: Dict[str, Any]) -> bool:
        """Main promotion workflow with transaction support."""
        try:
            # Start transaction
            self.start_transaction()

            # Load auto-hub proposals
            with open(auto_hubs_file, 'r') as f:
                data = json.load(f)
                proposals = data.get('proposals', [])

            if not proposals:
                logger.info("No proposals to promote")
                return True

            # Load existing config
            config = self.load_existing_config()

            # Validate proposals
            valid_proposals = self.validate_proposals(proposals)

            if not valid_proposals:
                logger.info("No valid proposals to promote")
                return True

            # Apply policy filters
            promoted = []
            for proposal in valid_proposals:
                scores = proposal.get('scores', {})

                # Check policy criteria
                min_evidence = policy.get('min_evidence', 2)
                min_z = policy.get('min_z', 2.0)
                require_reviewer = policy.get('require_reviewer', True)

                if proposal.get('evidence_sources', 0) < min_evidence:
                    continue

                high_scores = sum(1 for v in scores.values() if v and v >= min_z)
                if high_scores < 2:
                    continue

                if require_reviewer and not proposal.get('reviewer'):
                    logger.warning(f"Skipping {proposal['name']}: no reviewer assigned")
                    continue

                # Add to promoted list
                hub_name = proposal['name']
                if hub_name not in config['AUTO_HUBS']:
                    config['AUTO_HUBS'].append(hub_name)
                    promoted.append(hub_name)

                    # Add to history
                    history_entry = f"{datetime.now().isoformat()}: Promoted {hub_name}"
                    config.setdefault('PROMOTION_HISTORY', []).append(history_entry)

            # Write updated config
            if promoted:
                self.write_config(config)
                logger.info(f"Promoted {len(promoted)} hubs: {', '.join(promoted)}")

                # Validate written file
                if not self._validate_written_file():
                    raise HubPromotionError("Written file validation failed")

                # Commit transaction
                self.commit()
                return True
            else:
                logger.info("No hubs promoted")
                return True

        except Exception as e:
            self.rollback(str(e))
            return False

    def _validate_written_file(self) -> bool:
        """Validate the written configuration file."""
        try:
            if not os.path.exists(self.temp_file):
                return False

            # Check file is not empty
            if os.path.getsize(self.temp_file) == 0:
                return False

            # Try to parse it
            if self.config_file.suffix == '.conf':
                with open(self.temp_file, 'r') as f:
                    content = f.read()
                    return 'HUBS' in content or 'AUTO_HUBS' in content
            else:
                with open(self.temp_file, 'r') as f:
                    json.load(f)
                return True

        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return False


def main():
    parser = argparse.ArgumentParser(description='Promote auto-discovered hubs with transaction support')
    parser.add_argument('--country', required=True, help='Country code')
    parser.add_argument('--auto', required=True, help='Path to auto-hubs JSON file')
    parser.add_argument('--conf', required=True, help='Path to hub config file')
    parser.add_argument('--policy', help='JSON string with promotion policy')
    parser.add_argument('--validate', action='store_true', help='Validate only, no changes')
    parser.add_argument('--force', action='store_true', help='Force promotion even with warnings')

    args = parser.parse_args()

    # Parse policy
    policy = {'min_evidence': 2, 'min_z': 2.0, 'require_reviewer': True}
    if args.policy:
        try:
            policy.update(json.loads(args.policy))
        except json.JSONDecodeError:
            logger.error(f"Invalid policy JSON: {args.policy}")
            sys.exit(1)

    # Create promoter
    promoter = HubPromoter(args.country, args.conf)

    # Run promotion
    if args.validate:
        logger.info("Running in validation mode only")
        # Just validate proposals
        with open(args.auto, 'r') as f:
            data = json.load(f)
            proposals = data.get('proposals', [])
        valid = promoter.validate_proposals(proposals)
        logger.info(f"Valid proposals: {len(valid)}")
        sys.exit(0 if valid else 1)
    else:
        success = promoter.promote_hubs(args.auto, policy)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
