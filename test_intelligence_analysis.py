import requests

# Replace with your actual OpenAlex data
openalex_data = [
    {
        "id": "https://openalex.org/W2151103935",
        "title": "Distinctive Image Features from Scale-Invariant Keypoints",
        "authorships": [
            {
                "author": {"display_name": "David Lowe"},
                "institutions": [{"display_name": "University of British Columbia"}]
            }
        ],
        "topics": [
            {"display_name": "Robotics and Sensor-Based Localization"},
            {"display_name": "Advanced Image and Video Retrieval Techniques"}
        ],
        "cited_by_count": 53384
    }
]

# Example patent database
patent_db = [
    {
        "title": "Scale-Invariant Feature Transform Patent",
        "inventors": ["David Lowe"],
        "classifications": ["G06N"]
    }
]

response = requests.post(
    "http://127.0.0.1:8000/intelligence_analysis",
    json={"data": openalex_data, "patent_db": patent_db}
)
print(response.json())
