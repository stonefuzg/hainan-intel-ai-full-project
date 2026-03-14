
class AnalysisAgent:

    def industry_analysis(self, enterprises):
        industry = {}
        for e in enterprises:
            industry[e["industry"]] = industry.get(e["industry"],0)+1

        if not industry:
            return {}

        top = max(industry, key=industry.get)
        return {
            "top_industry": top,
            "count": industry[top]
        }
