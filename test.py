import requests

url = "http://127.0.0.1:8000/vote/"

payload={'csrfmiddlewaretoken': '3HcsvArx5DgGYjiv7zroql8XZscbup0xjoLGT6lenFwAiKYVNkkfzW9tTE9FsHPH',
'votes': [2, 3]}
files=[

]
headers = {
  'Cookie': 'csrf-token=3HcsvArx5DgGYjiv7zroql8XZscbup0xjoLGT6lenFwAiKYVNkkfzW9tTE9FsHPH; csrftoken=qRJoyG4Rscq4uBQAQV31jLbG4m7E8sZk; sessionid=unuc1spxh4dy4h5eltp136y9melv7b1y'
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)

print(response.text)