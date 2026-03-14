
import random

def crawl_enterprises():

    industries = ["跨境贸易","旅游","科技","电商","物流"]
    data = []

    for i in range(30):
        data.append({
            "name": f"海南企业{i}",
            "industry": random.choice(industries),
            "capital": random.randint(100,1000)
        })

    return data
