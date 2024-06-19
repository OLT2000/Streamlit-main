import requests
from streamlit import secrets
import json


def call_thinkcell_server(thinkcell_json: list):
    try:
        response = requests.post(
            secrets.get("LHR_SERVER"),
            headers={
                'Content-Type': 'application/vnd.think-cell.ppttc+json'
            },
            data=json.dumps(thinkcell_json)
        )

    except Exception as e:
        print(f"An unexpected error occurred when generating the powerpoint: {e}")

    else:
        if response.status_code == 200:
            return response.content
            # with open('sample.pptx', 'wb') as f:
            #     f.write(response.content)
            # print("Success.")

        else:
            raise ConnectionError(f"Failed with status code: {response.status_code}\n{response.text}")
            