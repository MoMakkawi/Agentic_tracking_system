from utils import *

class GroupAnalyzer:
    """
    Grouping fetched data based on UID sets and configuration.
    """

    def __init__(self):
        load_config()
        self.groups_count = get_config().GROUPS_COUNTS.to_dict()
        self.allowed_lengths = set(self.groups_count.values())
        logger.info(f"GroupingTool initialized. Allowed lengths: {self.allowed_lengths}")

    def run(self, data):
        """Run full grouping pipeline on provided data."""
        filtered = self._filter_by_count(data)
        uid_groups = self._extract_uid_sets(filtered)
        counter = self._count_uid_groups(uid_groups)
        top_named_groups = self._assign_group_names(counter)
        return top_named_groups

    # ---------- Internal helper methods ----------
    def _filter_by_count(self, data):
        filtered = [item for item in data if item.get("count") in self.allowed_lengths]
        logger.info(f"Filtered {len(filtered)} records from {len(data)}")
        return filtered

    def _extract_uid_sets(self, data):
        uid_sets = [set(log["uid"] for log in item["logs"]) for item in data]
        logger.info(f"Extracted {len(uid_sets)} UID sets")
        return uid_sets

    def _count_uid_groups(self, uid_groups):
        from collections import Counter
        counter = Counter(frozenset(group) for group in uid_groups)
        logger.info(f"Counted {len(counter)} unique UID groups")
        return counter

    def _assign_group_names(self, counter):
        from collections import defaultdict
        length_to_names = defaultdict(list)
        for name, length in self.groups_count.items():
            length_to_names[length].append(name)
        
        groups_by_length = defaultdict(list)
        for group, full_count in counter.items():
            groups_by_length[len(group)].append((group, full_count))
        
        result = []
        for length, names in length_to_names.items():
            sorted_groups = sorted(groups_by_length[length], key=lambda x: -x[1])
            for name, (group, full_count) in zip(names, sorted_groups):
                result.append({
                    "name": name,
                    "full_count": full_count,
                    "uids": list(group)
                })
                logger.info(f"Assigned group '{name}' with count {full_count}")
        return result

    # ---------- Optional save/load ----------
    def save(self, groups, file_path):
        save_json(groups, file_path)
        logger.info(f"Groups saved to {file_path}")

    def load(self, file_path):
        groups = load_json(file_path)
        logger.info(f"Groups loaded from {file_path}")
        return groups
