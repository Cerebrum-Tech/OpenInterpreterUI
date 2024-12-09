import os
import requests
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

base_auth_url = "https://api.reengen.com/api/do/"
username = os.getenv("API_USERNAME")
password = os.getenv("API_PASSWORD")

if not username or not password:
    st.error("API kullanıcı adı veya şifre çevre değişkeni eksik.")

def handle_response(response):
    try:
        response_data = response.json()
    except ValueError as e:
        st.error(f"JSON decoding hatası: {e}")
        return None
    
    if response.status_code == 200 and response_data.get("succeeded"):
        return response_data
    else:
        st.error(response_data.get('message', 'Bilinmeyen hata'))
        st.error(f"Kimlik doğrulama isteği başarısız oldu. Durum kodu: {response.status_code}")
        return None

def authenticate():
    auth_data = {
        "$": "Authenticate",
        "properties": {
            "tenant": "game4seen",
            "user": username,
            "password": password
        }
    }

    response = requests.post(base_auth_url, json=auth_data)
    return handle_response(response).get("properties", {}).get("connectionId")

def get_data(connection_id):
    data_payload = {
        "$": "GetData",
        "properties": {
            "series": [
                {
                    "definition": "activeEnergy",
                    "variant": "import",
                    "type": "actual",
                    "xFunction": "sum",
                    "unit": "kWh",
                    "decimalPoints": 2
                }
            ],
            "point": ["game4seen_konut_10"],
            "start": "2023-01-01T00:00:00",
            "end": "2023-01-31T23:59:59",
            "resolution": "week"
        },
        "connectionId": connection_id
    }
    
    response = requests.post(base_auth_url, json=data_payload)
    return handle_response(response).get("properties", {}).get("data")

def get_data_breakdown(connection_id):
    data_payload = {
        "$": "GetData",
        "properties": {
            "series": [
                {
                    "definition": "activeEnergy",
                    "variant": "import",
                    "type": "actual",
                    "xFunction": "sum",
                    "unit": "kWh",
                    "decimalPoints": 2
                }
            ],
            "point": ["game4seen_konut_10"],
            "start": "2023-01-01T00:00:00",
            "end": "2023-01-31T23:59:59",
            "break": {
                "type": "timeGroup",
                "breakdown": "game4seen_peakHours",
                "filter": True,
                "filterValue": ["peakHours"]
            },
            "resolution": "week"
        },
        "connectionId": connection_id
    }
    
    response = requests.post(base_auth_url, json=data_payload)
    return handle_response(response).get("properties", {}).get("data")

def list_data(connection_id):
    data_payload = {
        "$": "ListDataEx",
        "properties": {
            "requestType": "code",
            "point": ["game4seen_konut_8","game4seen_konut_10"],
            "definition": ["activeEnergy"],
            "variant": ["import"],
            "type": ["actual"],
            "unit": "kWh",
            "properties": [ "point.code", "definition.code", "variant.code", "type.code", "date", "definition.unit.code", "value"],
            "start": "2022-09-21T00:00:00",
            "end": "2023-02-19T23:59:59",
            "resolution": "hour"
        }
    }
    
    headers = {
        "XConnectionId": connection_id,
        "Content-Type": "application/json"
    }
    
    response = requests.post(base_auth_url, json=data_payload, headers=headers)
    return handle_response(response).get("properties", {}).get("data")

def list_point_full_data(connection_id):
    data_payload = {
        "$": "ListPointForV2",
        "properties": {
            "properties": [
                "id", "tenant.name", "code", "name", "enabled", "type.name", 
                "lat", "lng", "totalArea", "parent.name", 
                {"function": "concat", "separator": "", "rename": "age", "properties": ["hddBaseTemperature", ""]}, 
                {"function": "concat", "separator": "", "rename": "hhm", "properties": ["cddBaseTemperature", ""]}
            ],
            "criteria": [
                {
                    "property" :"hddBaseTemperature",
                    "function" : "ge",
                    "value" : "40"
                }
            ]
        }
    }
    
    headers = {
        "XConnectionId": connection_id,
        "Content-Type": "application/json"
    }
    
    response = requests.post(base_auth_url, json=data_payload, headers=headers)
    return handle_response(response).get("properties", {}).get("data")