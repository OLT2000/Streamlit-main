import requests
import json

objPpttc = [
    {
        "template": "https://storage.googleapis.com/example_bucekt/BarChart.pptx",
        "data": [
            {
                "name": "BarChart",
                "table": [
                    [
                        {
                            "string": "1. Your Gender"
                        },
                        {
                            "string": "Female"
                        },
                        {
                            "string": "Male"
                        }
                    ],
                    [],
                    [
                        {
                            "string": "Daily"
                        },
                        {
                            "number": 0.0,
                            "fill": "#333333"
                        },
                        {
                            "number": 2.0,
                            "fill": "#333333"
                        }
                    ],
                    [
                        {
                            "string": "Monthly"
                        },
                        {
                            "number": 10.0,
                            "fill": "#5c5c5c"
                        },
                        {
                            "number": 16.0,
                            "fill": "#5c5c5c"
                        }
                    ],
                    [
                        {
                            "string": "Never"
                        },
                        {
                            "number": 6.0,
                            "fill": "#858585"
                        },
                        {
                            "number": 3.0,
                            "fill": "#858585"
                        }
                    ],
                    [
                        {
                            "string": "Rarely"
                        },
                        {
                            "number": 45.0,
                            "fill": "#2c475a"
                        },
                        {
                            "number": 31.0,
                            "fill": "#2c475a"
                        }
                    ],
                    [
                        {
                            "string": "Weekly"
                        },
                        {
                            "number": 4.0,
                            "fill": "#cc0000"
                        },
                        {
                            "number": 5.0,
                            "fill": "#cc0000"
                        }
                    ]
                ]
            }
        ]
    }
]

# objPpttc = [
#     {
#         "template": "https://storage.googleapis.com/example_bucekt/BainBarTemplate.pptx",
#         "data": [
#             {
#                 "name": "Chart1",
#                 "table": [
#                     [
#                         {
#                             "string": "1. Your Gender"
#                         },
#                         {
#                             "string": "Female"
#                         },
#                         {
#                             "string": "Male"
#                         }
#                     ],
#                     [],
#                     [
#                         {
#                             "string": "count"
#                         },
#                         {
#                             "number": 65,
#                             "fill": "#333333"
#                         },
#                         {
#                             "number": 57,
#                             "fill": "#333333"
#                         }
#                     ]
#                 ]
#             }
#         ]
#     }
# ]

headers = {
    'Content-Type': 'application/vnd.think-cell.ppttc+json'
}

response = requests.post('https://eeb8569744781e.lhr.life', headers=headers, data=json.dumps(objPpttc))

if response.status_code == 200:
    with open('sample.pptx', 'wb') as f:
        f.write(response.content)
    print("Success.")

else:
    print(f"Failed with status code: {response.status_code}")
    # print(response)
    print(response.text)
