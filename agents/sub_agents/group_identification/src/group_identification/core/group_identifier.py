from typing import Dict, List, Optional
from utils import logger, get_config
from utils import JsonRepository, CsvRepository
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.cluster import DBSCAN
from sklearn.metrics import pairwise_distances
import numpy as np

class GroupIdentifier:
    """
    Performs identification and clustering of student attendance groups.

    Workflow:
        1. Load preprocessed session attendance data from storage.
        2. Group student IDs (UIDs) by event names, splitting multi-event entries if necessary.
        3. Cluster students based on session attendance similarity.
        4. Save the resulting groups to a JSON file.

    Methods:
        - mapping_students_by_sessions_names() -> dict[str, List[str]]:
            Returns a mapping of event names to lists of valid student UIDs.
        - cluster_students() -> dict[str, List[str]]:
            Clusters students based on session attendance using DBSCAN with Jaccard similarity.
        - save_groups(groups: dict[str, List[str]]) -> str:
            Saves the given group mapping to a JSON file at the configured output path.
    """
    
    def __init__(self):
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
        self.id_alerts = csv_repo.read_all()
        logger.info(f"Loaded {len(self.id_alerts)} invalid uids successfully!")

        # load output path
        self.output_path = config.PATHS.GROUPS

    def mapping_students_by_sessions_names(self) -> dict[str, List[str]]:
        groups: dict[str, set] = {}
        
        for session in self.sessions:
            event_context = session.get("event_context", "")
            logs = session.get("logs", [])
            
            # Extract UIDs from this session
            uids = {log.get("uid") for log in logs if log.get("uid") and self._is_valid_id(log.get("uid"))}
            
            if not event_context:
                continue
                
            # Split event names (assuming comma separation as per processor.py)
            # "Coaching professionnel, Communications et Réseaux pour l’IoT" -> ["Coaching professionnel", "Communications et Réseaux pour l’IoT"]
            events = [e.strip() for e in event_context.split(",")]
            
            for event in events:
                if not event:
                    continue
                
                if event not in groups:
                    groups[event] = set()
                
                groups[event].update(uids)
        
        # Convert sets to sorted lists for JSON serialization and consistency
        return {event: sorted(list(uids)) for event, uids in groups.items()}
    
    def save_groups(self, groups: dict[str, List[str]]) -> str:
        logger.info(f"Saving groups {groups} to: {self.output_path}")
        json_repo = JsonRepository(self.output_path)
        json_repo.save_all(groups)
        logger.info(f"Saved successfully groups to: {self.output_path}")
        return self.output_path

    def cluster_students(self) -> dict[str, List[str]]:
        """
        Cluster students based on session attendance using DBSCAN and Jaccard similarity.
        Automatically calculates a suitable eps from the data.
        
        Returns:
            Dict of cluster label -> list of student UIDs
        """

           # Step 1: Build mapping {event: [uids]}
        event_to_uids = self.mapping_students_by_sessions_names()

        # Step 2: Build set of all students
        all_students = set()
        for uids in event_to_uids.values():
            all_students.update(uids)
        all_students = sorted(all_students)

        if not all_students:
            return {}

        # Step 3: Transform into student-session matrix
        sessions_list = list(event_to_uids.values())
        mlb = MultiLabelBinarizer(classes=all_students)
        matrix = mlb.fit_transform(sessions_list).T  # rows = students, columns = sessions

        # Step 4: Compute pairwise Jaccard distances
        distances = pairwise_distances(matrix, metric="jaccard")

        # Step 5: Calculate eps automatically
        np.fill_diagonal(distances, np.inf)  # ignore self-distance
        nearest_distances = distances.min(axis=1)
        eps = np.median(nearest_distances)

        # Step 5b: Ensure eps > 0
        if eps <= 0.0:
            eps = 0.01  # small positive value to avoid DBSCAN error

        # Step 6: Run DBSCAN with calculated eps
        clustering = DBSCAN(metric="precomputed", eps=float(eps), min_samples=1)
        labels = clustering.fit_predict(distances)

        # Step 7: Map students to clusters
        student_clusters = {}
        for student, label in zip(all_students, labels):
            cluster_key = str(label)
            if cluster_key not in student_clusters:
                student_clusters[cluster_key] = []
            student_clusters[cluster_key].append(student)

        return student_clusters

    def _is_valid_id(self, uid: str) -> bool:
        invalid_uids = [row["uid"] for row in self.id_alerts if "uid" in row]
        return uid not in invalid_uids