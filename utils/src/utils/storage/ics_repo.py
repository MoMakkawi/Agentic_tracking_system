import os
from typing import List, Dict, Any, Union
from datetime import datetime
from .base import FileRepository
from utils import TimestampHelper

try:
    from icalendar import Calendar, Event
    ICALENDAR_AVAILABLE = True
except ImportError:
    ICALENDAR_AVAILABLE = False

class IcsRepository(FileRepository):
    def __init__(self, file_path: str):
        super().__init__(file_path)
        if not ICALENDAR_AVAILABLE:
            raise ImportError("The 'icalendar' library is required for ICS support. Please install it via 'pip install icalendar'.")

    def read_all(self) -> List[Dict[str, Any]]:
        self.ensure_exists()
        
        with open(self.file_path, 'rb') as f:
            cal = Calendar.from_ical(f.read())
            sessions = []
            for component in cal.walk():
                if component.name == "VEVENT":
                    session_dict = {
                        "id": str(component.get("UID")),
                        "summary": str(component.get("SUMMARY")),
                        "start": component.get("DTSTART").dt if component.get("DTSTART") else None,
                        "end": component.get("DTEND").dt if component.get("DTEND") else None,
                        "description": str(component.get("DESCRIPTION")) if component.get("DESCRIPTION") else "",
                    }
                    # Convert datetimes to desired format using TimestampHelper
                    if session_dict["start"]:
                        # safe_parse expects a string, so we convert datetime/date to string first
                        session_dict["start"] = TimestampHelper.safe_parse(str(session_dict["start"]))
                    if session_dict["end"]:
                        session_dict["end"] = TimestampHelper.safe_parse(str(session_dict["end"]))
                        
                    sessions.append(session_dict)
            return sessions

    def save_all(self, data: List[Dict[str, Any]]):
        self._save(data)

    def _save(self, data: List[Dict[str, Any]]):
        cal = Calendar()
        cal.add('prodid', '-//My Calendar Product//mxm.dk//')
        cal.add('version', '2.0')

        for item in data:
            session = Event()
            session.add('uid', item.get('id'))
            session.add('summary', item.get('summary'))
            session.add('description', item.get('description', ''))
            
            # Basic datetime handling - assumes ISO strings or datetime objects
            start = item.get('start')
            if isinstance(start, str):
                try:
                    start = datetime.fromisoformat(start)
                except ValueError:
                    pass # Handle or log error
            if start:
                session.add('dtstart', start)

            end = item.get('end')
            if isinstance(end, str):
                try:
                    end = datetime.fromisoformat(end)
                except ValueError:
                    pass
            if end:
                session.add('dtend', end)

            cal.add_component(session)

        self.ensure_directory_exists()
        with open(self.file_path, 'wb') as f:
            f.write(cal.to_ical())

    def add(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> None:
        current_data = self.read_all()
        if isinstance(data, list):
            current_data.extend(data)
        else:
            current_data.append(data)
        self._save(current_data)

    def update(self, record_id: str, updates: Dict[str, Any]) -> bool:
        data = self.read_all()
        updated = False
        for i, record in enumerate(data):
            if str(record.get('id')) == str(record_id):
                data[i].update(updates)
                updated = True
                break
        
        if updated:
            self._save(data)
        return updated

    def delete(self, record_id: str) -> bool:
        data = self.read_all()
        initial_len = len(data)
        data = [r for r in data if str(r.get('id')) != str(record_id)]
        
        if len(data) < initial_len:
            self._save(data)
            return True
        return False

    def save_from_bytes(self, content: Union[bytes, str]) -> str:
        """
        Save raw ICS data (bytes or string) exactly as-is.
        """
        self.ensure_directory_exists()
            
        try:
            # Decode bytes to string if needed
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="ignore")

            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(content)

            return self.file_path
        except Exception as e:
            # logger is not imported in this file, so we might need to import it or just raise
            # For now, let's just raise as the caller handles logging
            raise
