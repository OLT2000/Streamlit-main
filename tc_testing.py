import requests
import json

objPpttc = [
    {
        "template": "https://static.think-cell.com/ppttc/template3.pptx",
        "data": [
            {
                "name": "Chart1",
                "table": [
                    [
                        {
                            "string": "Category"
                        },
                        {
                            "string": "1"
                        },
                        {
                            "string": "0"
                        }
                    ],
                    [
                        None,
                        None,
                        None
                    ],
                    [
                        {
                            "string": "0"
                        },
                        {
                            "number": 27,
                            "fill": "#d0d0d0"
                        },
                        {
                            "number": 38,
                            "fill": "#d0d0d0"
                        }
                    ],
                    [
                        {
                            "string": "1"
                        },
                        {
                            "number": 9,
                            "fill": "#aae6f0"
                        },
                        {
                            "number": 14,
                            "fill": "#aae6f0"
                        }
                    ],
                    [
                        {
                            "string": "2"
                        },
                        {
                            "number": 10,
                            "fill": "#00a9f4"
                        },
                        {
                            "number": 7,
                            "fill": "#00a9f4"
                        }
                    ],
                    [
                        {
                            "string": "3"
                        },
                        {
                            "number": 3,
                            "fill": "#027ab1"
                        },
                        {
                            "number": 0,
                            "fill": "#027ab1"
                        }
                    ],
                    [
                        {
                            "string": "4"
                        },
                        {
                            "number": 5,
                            "fill": "#034b6f"
                        },
                        {
                            "number": 0,
                            "fill": "#034b6f"
                        }
                    ]
                ]
            }
        ]
    }
]

headers = {
    'Content-Type': 'application/vnd.think-cell.ppttc+json'
}

tc_server_url = 'http://20.68.169.15:8080/'

response = requests.post(tc_server_url, headers=headers, data=json.dumps(objPpttc))

if response.status_code == 200:
    with open('sample.pptx', 'wb') as f:
        f.write(response.content)
    print("Success.")

else:
    print(f"Failed with status code: {response.status_code}")
    print(response.cookies)
    print(response.text)
