from __future__ import annotations

import requests
from pdpyras import APISession


class PagerDutyManager:
    BASE_URL = "https://api.pagerduty.com"
    INCIDENTS_URI = "/incidents"

    def __init__(self, api_key):
        """Initializes PagerDutyManager with params as set in connector config"""
        self.api_key = api_key
        self.session = APISession(self.api_key)

    def acknowledge_incident(self, incident_id):
        """Acknowledges an incident in PagerDuty
        API Reference: https://developer.pagerduty.com/api-reference/8a0e1aa2ec666-update-an-incident
        """
        url = self.BASE_URL + self.INCIDENTS_URI + f"/{incident_id}"
        data = {"statuses[]": "acknowledged"}
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": f"Token token={self.api_key}",
        }
        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=data,
            timeout=10,
        )
        return response

    def list_oncalls(self):
        users = self.session.list_all("oncalls")
        return users

    def get_all_incidents(self):
        session = requests.Session()
        session.headers.update(
            {"Authorization": f"Token token={self.api_key}", "From": "none"},
        )
        parameters = {"user_ids[]": 0}
        url = self.BASE_URL + "/incidents"
        response = session.get(url=url, json=parameters, timeout=10)
        incident_data = response.json().get("incidents")
        return incident_data

    def list_incidents(self):
        incidents = self.session.list_all("incidents")
        if incidents:
            return incidents
        return "No Incidents Found"

    def list_users(self):
        users = self.session.list_all("users")
        users.raise_for_status()
        if users:
            return users
        return "No Users Found"

    def create_incident(self, email_from, title, service, urgency, body):
        session = requests.Session()
        session.headers.update(
            {"Authorization": f"Token token={self.api_key}", "From": f"{email_from}"},
        )
        payload = {
            "incident": {
                "type": "incident",
                "title": f"{title}",
                "service": {"id": f"{service}", "type": "service_reference"},
                "urgency": f"{urgency}",
                "body": {"type": "incident_body", "details": f"{body}"},
            },
        }
        url = self.BASE_URL + "/incidents"

        response = session.post(url=url, json=payload, timeout=10)
        response.raise_for_status()
        if response.json().get("incident_number") != 0:
            return response.json()
        return {"message": "No Incident Found"}

    def get_incident_ID(self, incidentID, email_from):
        session = requests.Session()
        session.headers.update(
            {"Authorization": f"Token token={self.api_key}", "From": f"{email_from}"},
        )
        parameters = {"user_ids[]": incidentID}
        url = self.BASE_URL + self.INCIDENTS_URI
        response = session.get(url=url, json=parameters, timeout=10)
        response.raise_for_status()
        incident_data = {}
        info_got = response.json().get("incidents")

        for incident in info_got:
            if incident.get(incident_key) == incidentID:
                incident_data = info_got[incident]

        return incident_data

    def get_user_by_email(self, email):
        user = self.session.find("users", email, attribute="email")
        if user is not None:
            return user
        return "No User Found"

    def get_user_by_ID(self, userID):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": f"Token token={self.api_key}",
        }
        url = self.BASE_URL + "/users/" + userID
        response = requests.request("GET", url, headers=headers, timeout=10)
        response.raise_for_status()
        if response.json()["user"]:
            return response.json()["user"]
        return "No User Found"

    def list_filtered_incidents(self, filter_params_dic: dict):
        url = self.BASE_URL + "/incidents"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "Authorization": f"Token token={self.api_key}",
        }
        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=filter_params_dic,
            timeout=10,
        )
        if response.json().get("incidents"):
            return response.json()
        return {"message": "No incident found with the filters entered"}

    def snooze_incident(self, email_from, incident_id):
        session = requests.Session()
        session.headers.update(
            {"Authorization": f"Token token={self.api_key}", "From": f"{email_from}"},
        )
        payload = {"duration": 3600}
        url = self.BASE_URL + self.INCIDENTS_URI + f"/{incident_id}" + "/snooze"
        response = session.post(url=url, json=payload, timeout=10)
        if response.ok:
            return response.json()
        return {"message": "No Incident found"}

    def run_response_play(self, email, response_plays_id, user_id):
        payload = {"incident": {"id": f"{user_id}", "type": "incident_reference"}}

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.pagerduty+json;version=2",
            "From": f"{email}",
            "Authorization": f"Token token={self.api_key}",
        }

        full_url = self.BASE_URL + "/response_plays/" + response_plays_id + "/run"
        response = requests.request(
            "POST",
            full_url,
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        return {"message": response}
