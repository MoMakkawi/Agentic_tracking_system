from collections import defaultdict
from typing import List, Dict, Any, Optional

import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
import community as community_louvain

from utils import logger, get_config
from utils import JsonRepository, CsvRepository

class LouvainGroupIdentifier:
    """
    Pipeline to analyze student behavioral patterns and detect communities.

    Output format (strict):
    {
        "group_0": ["uid1", "uid2", "uid3"],
        "group_1": ["uid4", "uid5"]
    }
    """

    def __init__(self):
        # -----------------------------
        # Configuration
        # -----------------------------
        config = get_config()

        # load sessions data
        clean_data_path = config.PATHS.PREPROCESSED
        logger.info(f"Loading session data from: {clean_data_path}")
        json_repo = JsonRepository(clean_data_path)
        json_repo.ensure_exists()
        self.sessions = json_repo.read_all()
        logger.info(f"Loaded {len(self.sessions)} sessions successfully!")

        # load alerts to detect invalid uids
        id_alerts_path = config.PATHS.ALERTS.VALIDATION.IDENTITY
        logger.info(f"Loading invalid uids from: {id_alerts_path}")
        csv_repo = CsvRepository(id_alerts_path)
        csv_repo.ensure_exists()
        alerts = csv_repo.read_all()
        self.disallowed_uids = {
            row["uid"]
            for row in alerts
            if int(row["allow_clustering"]) == 0
        }

        logger.info(f"Loaded {len(self.disallowed_uids)} disallowed uids successfully!")

        # Louvain
        louvain_config = config.LLM_MODULES.GROUP_IDENTIFIER.LOUVAIN
        self.similarity_threshold = louvain_config.SIMILARITY_THRESHOLD
        self.random_state = louvain_config.RANDOM_STATE

        # -----------------------------
        # Data containers
        # -----------------------------

        self.all_students: set[str] = set()
        self.student_sessions: Dict[str, List[str]] = defaultdict(list)
        self.session_info: Dict[str, Dict[str, Any]] = {}

        self.features: Dict[str, Dict[str, float]] = {}
        self.student_list: List[str] = []
        self.feature_names: List[str] = []
        self.feature_matrix: np.ndarray = np.empty((0, 0))

        self.G: nx.Graph = nx.Graph()

        self.communities: Dict[str, int] = {}
        self.groups: Dict[int, List[str]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _valid_uid(self, uid: Optional[str]) -> bool:
        return bool(uid) and uid not in self.disallowed_uids

    # ------------------------------------------------------------------
    # Pipeline steps
    # ------------------------------------------------------------------

    def _explore_data(self) -> None:
        for session in self.sessions:
            sid = session.get("session_id")
            logs = session.get("logs", [])

            if not sid:
                continue

            valid_uids = [
                log.get("uid")
                for log in logs
                if self._valid_uid(log.get("uid"))
            ]

            self.session_info[sid] = {
                "name": session.get("session_context"),
            }

            for uid in valid_uids:
                self.all_students.add(uid)
                self.student_sessions[uid].append(sid)

        self.student_list = sorted(self.all_students)
        logger.info(f"Unique students: {len(self.student_list)}")

    def _extract_features(self) -> None:
        """
        Extract per-student features using ONLY session_context.
        Each unique session_context is treated as ONE atomic categorical feature.
        """

        # 1. Collect unique session_context values (no splitting)
        session_contexts = sorted({
            info["name"]
            for info in self.session_info.values()
            if info.get("name")
        })

        self.feature_names = session_contexts

        # 2. Build binary feature vectors per student
        for student in self.student_list:
            attended_sessions = self.student_sessions[student]

            attended_contexts = {
                self.session_info[sid]["name"]
                for sid in attended_sessions
                if self.session_info[sid].get("name")
            }

            self.features[student] = {
                ctx: 1.0 if ctx in attended_contexts else 0.0
                for ctx in session_contexts
            }

        # 3. Build feature matrix (students × session_contexts)
        self.feature_matrix = np.array([
            [self.features[s][f] for f in self.feature_names]
            for s in self.student_list
        ], dtype=float)

        logger.info(f"Feature matrix shape: {self.feature_matrix.shape}")

    def _build_network(self) -> None:
        self.G.add_nodes_from(self.student_list)

        # Co-attendance edges (normalized)
        for session in self.sessions:
            uids = [
                log.get("uid")
                for log in session.get("logs", [])
                if self._valid_uid(log.get("uid"))
            ]

            n = len(uids)
            if n < 2:
                continue

            weight = 1.0 / (n - 1)

            for i, u1 in enumerate(uids):
                for u2 in uids[i + 1:]:
                    if self.G.has_edge(u1, u2):
                        self.G[u1][u2]["weight"] += weight
                    else:
                        self.G.add_edge(u1, u2, weight=weight)

        # Behavioral similarity edges
        sim = cosine_similarity(self.feature_matrix)

        for i in range(len(self.student_list)):
            for j in np.where(sim[i] > self.similarity_threshold)[0]:
                if i >= j:
                    continue

                s1, s2 = self.student_list[i], self.student_list[j]
                if not self.G.has_edge(s1, s2):
                    self.G.add_edge(s1, s2, weight=0.5 * sim[i, j])

        logger.info(f"Graph edges: {self.G.number_of_edges()}")

    def _detect_communities(self) -> None:
        self.communities = community_louvain.best_partition(
            self.G,
            weight="weight",
            random_state=self.random_state,
        )

        for student, gid in self.communities.items():
            self.groups[gid].append(student)

        logger.info(f"Detected {len(self.groups)} groups")

    def _export_results(self) -> Dict[str, List[str]]:
        return {
            f"group {gid + 1}": members
            for gid, members in self.groups.items()
        }

    def run(self) -> Dict[str, List[str]]:
        self._explore_data()
        self._extract_features()
        self._build_network()
        self._detect_communities()
        return self._export_results()
