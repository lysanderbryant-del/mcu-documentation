"""
File Discovery Module - Locate all 7 required CSV files for any business date
"""

from pathlib import Path
from datetime import date
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class SourceFile:
    """Represents a discovered source file."""
    file_type: str
    file_path: Path
    exists: bool
    size_bytes: int
    modified_time: Optional[float]


class FileDiscoveryError(Exception):
    """Raised when required files cannot be found."""
    pass


class DailyFileDiscovery:
    """Discovers all 7 CSV files required for daily margin report."""

    # Network drive base paths
    BNP_BASE = Path(r'\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPFileStore')
    BNPCET_BASE = Path(r'\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\BNPCETFileStore')
    SOCGEN_BASE = Path(r'\\pgb1-p-e-evs012\ENDUR_PROD_01\endur_prod\Interface\SGSAFileStore\SocGenAAL')
    CSA_BASE = Path(r'\\app-nas-fsx-prod.uk.centricaplc.com\CRR_PROD_01\CreditRisk\Collateral')

    def __init__(self, business_date: date):
        """
        Initialize file discovery for a specific business date.

        Args:
            business_date: The date to find files for
        """
        self.business_date = business_date
        self._format_dates()
        self._build_paths()

    def _format_dates(self):
        """Generate all date format variations needed."""
        self.date_iso = self.business_date.strftime('%Y-%m-%d')        # 2026-07-22
        self.date_compact = self.business_date.strftime('%Y%m%d')      # 20260722
        self.date_underscore = self.business_date.strftime('%Y_%m_%d') # 2026_07_22
        self.month_folder = self.business_date.strftime('%Y-%b')       # 2026-Jul
        self.date_ddmmyyyy = self.business_date.strftime('%d%m%Y')     # 23072026

    def _build_paths(self):
        """Build directory paths for each file source."""
        self.bnp_processed = self.BNP_BASE / 'Processed' / self.month_folder
        self.bnpcet_processed = self.BNPCET_BASE / 'Processed' / self.month_folder
        self.socgen_dir = self.SOCGEN_BASE
        self.csa_dir = self.CSA_BASE

    def discover_all_files(self) -> Dict[str, SourceFile]:
        """
        Locate all 7 required CSV files.

        Returns:
            Dictionary mapping file type to SourceFile object

        Raises:
            FileDiscoveryError: If any critical files are missing
        """
        files = {
            'bnp_cel_mc': self._find_bnp_mc_statement('CEL'),
            'bnp_cel_ote': self._find_bnp_ote_detail('CEL'),
            'bnp_cel_jnls': self._find_bnp_journal_entries('CEL'),
            'bnp_cel_pns': self._find_bnp_pns('CEL'),
            'bnp_cet_mc': self._find_bnp_mc_statement('CET'),
            'socgen': self._find_socgen_margin(),
            'csa': self._find_csa_collateral(),
        }

        # Check for missing critical files
        missing_critical = []
        for file_type, source_file in files.items():
            if not source_file.exists:
                if file_type in ['bnp_cel_mc', 'csa']:  # Critical files
                    missing_critical.append(file_type)

        if missing_critical:
            raise FileDiscoveryError(
                f"Missing critical files for {self.business_date}: {missing_critical}"
            )

        return files

    def _find_latest_file(self, directory: Path, pattern: str, file_type: str) -> SourceFile:
        """
        Find the most recent file matching a glob pattern.

        Args:
            directory: Directory to search
            pattern: Glob pattern (e.g., "MC_Statement_CEL U_*.csv")
            file_type: Identifier for this file type

        Returns:
            SourceFile object (exists=False if not found)
        """
        if not directory.exists():
            return SourceFile(
                file_type=file_type,
                file_path=directory / pattern,
                exists=False,
                size_bytes=0,
                modified_time=None
            )

        matches = list(directory.glob(pattern))

        if not matches:
            return SourceFile(
                file_type=file_type,
                file_path=directory / pattern,
                exists=False,
                size_bytes=0,
                modified_time=None
            )

        # Find most recent file
        latest_file = max(matches, key=lambda p: p.stat().st_mtime)
        stat = latest_file.stat()

        return SourceFile(
            file_type=file_type,
            file_path=latest_file,
            exists=True,
            size_bytes=stat.st_size,
            modified_time=stat.st_mtime
        )

    def _find_bnp_mc_statement(self, entity: str) -> SourceFile:
        """Find MC_Statement file for BNP CEL or CET."""
        if entity == 'CEL':
            directory = self.bnp_processed
        else:
            directory = self.bnpcet_processed

        # Note: File timestamp may be different from business date (created next day)
        pattern = f'MC_Statement_{entity} U_{self.date_iso}_*.csv'
        return self._find_latest_file(directory, pattern, f'bnp_{entity.lower()}_mc')

    def _find_bnp_ote_detail(self, entity: str) -> SourceFile:
        """Find Detailed_Open_Pos file for BNP CEL."""
        directory = self.bnp_processed
        # Note: File timestamp may be different from business date
        pattern = f'Detailed_Open_Pos_{entity} U_{self.date_iso}_*.csv'
        return self._find_latest_file(directory, pattern, f'bnp_{entity.lower()}_ote')

    def _find_bnp_journal_entries(self, entity: str) -> SourceFile:
        """Find Journal_Entries file for BNP CEL."""
        directory = self.bnp_processed
        # Note: File timestamp may be different from business date
        pattern = f'Journal_Entries_{entity} U_{self.date_iso}_*.csv'
        return self._find_latest_file(directory, pattern, f'bnp_{entity.lower()}_jnls')

    def _find_bnp_pns(self, entity: str) -> SourceFile:
        """Find PnS file for BNP CEL."""
        directory = self.bnp_processed
        # Note: File timestamp may be different from business date
        pattern = f'PnS_{entity} U_{self.date_iso}_*.csv'
        return self._find_latest_file(directory, pattern, f'bnp_{entity.lower()}_pns')

    def _find_socgen_margin(self) -> SourceFile:
        """Find SocGen Global Margin Report."""
        directory = self.socgen_dir
        pattern = f'{self.date_compact}_GlobalMarginUnderlyingCurrencyReport.csv'

        # SocGen uses exact filename (no timestamp suffix)
        file_path = directory / pattern

        if file_path.exists():
            stat = file_path.stat()
            return SourceFile(
                file_type='socgen',
                file_path=file_path,
                exists=True,
                size_bytes=stat.st_size,
                modified_time=stat.st_mtime
            )
        else:
            return SourceFile(
                file_type='socgen',
                file_path=file_path,
                exists=False,
                size_bytes=0,
                modified_time=None
            )

    def _find_csa_collateral(self) -> SourceFile:
        """Find CSA Collateral Summary file."""
        directory = self.csa_dir
        pattern = f'Collateral_Summary_{self.date_underscore}_*.csv'
        return self._find_latest_file(directory, pattern, 'csa')

    def get_file_summary(self, files: Dict[str, SourceFile]) -> str:
        """
        Generate a human-readable summary of discovered files.

        Args:
            files: Dictionary of discovered files

        Returns:
            Formatted summary string
        """
        lines = [f"\nFile Discovery for {self.business_date}"]
        lines.append("=" * 60)

        for file_type, source_file in files.items():
            status = "FOUND" if source_file.exists else "MISSING"
            size_mb = source_file.size_bytes / (1024 * 1024) if source_file.exists else 0

            lines.append(f"\n{file_type.upper()}: {status}")
            if source_file.exists:
                lines.append(f"  Path: {source_file.file_path}")
                lines.append(f"  Size: {size_mb:.2f} MB")
            else:
                lines.append(f"  Expected: {source_file.file_path.name}")

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


if __name__ == "__main__":
    # Demo usage
    from datetime import date

    test_date = date(2026, 7, 22)
    discovery = DailyFileDiscovery(test_date)

    try:
        files = discovery.discover_all_files()
        print(discovery.get_file_summary(files))
    except FileDiscoveryError as e:
        print(f"ERROR: {e}")
