from utils import logger, get_config
from utils.file_helpers import load_json, save_json
import os


class GroupAnalyzer:
    """
    Categorize students into groups Based on the preprocessed data.
    """

    def __init__(self, input_path: str = None):
        self.input_path = input_path or get_config().PREPROCESSED_DATA_PATH

        if not self.input_path or not os.path.exists(self.input_path):
            raise FileNotFoundError(f"GroupAnalyzer input file not found: {self.input_path}")

        self.raw_sessions = load_json(self.input_path)
        self.last_result = None
        self.groups_count = get_config().GROUPS_COUNTS.to_dict()
        self.allowed_lengths = set(self.groups_count.values())
        logger.info(f"GroupAnalyzer initialized with data: {len(self.raw_sessions)} sessions")

    # ------------------------------------------------------------------
    def run(self):
        """Execute full grouping pipeline."""
        logger.info("Running grouping on preprocessed sessions")

        filtered = self._filter_by_count(self.raw_sessions)
        uid_sets = self._extract_uid_sets(filtered)
        counter = self._count_uid_groups(uid_sets)
        top_named_groups = self._assign_group_names(counter)

        self.last_result = top_named_groups
        logger.info("Grouping pipeline completed")

        return top_named_groups

    # ---------- Internal Helpers ----------
    def _filter_by_count(self, data):
        return [
            item for item in data
            if item.get("unique_count") in self.allowed_lengths
        ]

    def _extract_uid_sets(self, data):
        return [set(log["uid"] for log in item["logs"]) for item in data]

    def _count_uid_groups(self, uid_groups):
        from collections import Counter
        return Counter(frozenset(group) for group in uid_groups)

    def _assign_group_names(self, counter):
        from collections import defaultdict
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
                    "uids": list(group)
                })

        return result

    # ------------------------------------------------------------------
    def save(self, groups=None, output_path: str = None):
        """Save grouping results."""
        if groups is None:
            if self.last_result is None:
                raise ValueError("No grouping results available")
            groups = self.last_result

        output_path = output_path or get_config().GROUPS_OUTPUT_PATH
        save_json(groups, output_path)
        logger.info(f"Groups saved to {output_path}")
        return output_path
