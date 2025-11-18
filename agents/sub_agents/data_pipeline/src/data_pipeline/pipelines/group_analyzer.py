from collections import Counter, defaultdict
from utils import logger, get_config
from utils.files_helper import FilesHelper

class GroupAnalyzer:
    """
    Group Analyzer for preprocessed session data.

    Features:
        - Filter sessions by valid unique counts
        - Identify recurring UID groups
        - Assign group names by size and frequency
        - Export final student group mappings
    """

    def __init__(self, input_path: str = None):
        self.input_path = input_path or get_config().PATHS.PREPROCESSED
        FilesHelper.ensure_exists(self.input_path)

        self.logs_sessions = FilesHelper.load(self.input_path)
        self.groups_count = get_config().GROUPS_COUNTS.to_dict()
        self.allowed_lengths = set(self.groups_count.values())
        self.last_result = None

        logger.info(f"Loaded {len(self.logs_sessions)} sessions for grouping")

    # -------------------------------------------------------------------------
    def run(self):
        """Run full grouping pipeline."""
        logger.info("Running GroupAnalyzer pipeline...")

        filtered = self._filter_by_count(self.logs_sessions)
        uid_sets = self._extract_uid_sets(filtered)
        counter = self._count_uid_groups(uid_sets)
        named_groups = self._assign_group_names(counter)

        self.last_result = named_groups
        logger.info(f"Grouping completed with {len(named_groups)} groups generated")
        return named_groups

    # -------------------------------------------------------------------------
    def _filter_by_count(self, data):
        """Filter sessions with valid unique UID counts."""
        return [item for item in data if item.get("unique_count") in self.allowed_lengths]

    # -------------------------------------------------------------------------
    def _extract_uid_sets(self, data):
        """Extract UID sets from filtered sessions."""
        return [set(log["uid"] for log in item.get("logs", [])) for item in data]

    # -------------------------------------------------------------------------
    def _count_uid_groups(self, uid_groups):
        """Count frequency of identical UID group combinations."""
        return Counter(frozenset(group) for group in uid_groups)

    # -------------------------------------------------------------------------
    def _assign_group_names(self, counter):
        """Assign readable group names based on size and frequency."""
        length_to_names = defaultdict(list)
        for name, length in self.groups_count.items():
            length_to_names[length].append(name)

        groups_by_length = defaultdict(list)
        for group, count in counter.items():
            groups_by_length[len(group)].append((group, count))

        result = []
        for length, names in length_to_names.items():
            sorted_groups = sorted(groups_by_length[length], key=lambda x: -x[1])
            for name, (group, count) in zip(names, sorted_groups):
                result.append({
                    "name": name,
                    "full_count": count,
                    "uids": list(group),
                })

        return result

    # -------------------------------------------------------------------------
    def save(self, groups=None, output_path: str = None):
        """Save final group results to JSON."""
        if groups is None:
            if self.last_result is None:
                logger.error("No grouping results found. Run `.run()` first.")
                raise ValueError("No group data to save.")
            groups = self.last_result

        output_path = output_path or get_config().PATHS.GROUPED
        FilesHelper.save(groups, output_path)
        logger.info(f"Group data saved to: {output_path}")
        return output_path