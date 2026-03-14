
class DataAgent:
    def summarize(self, enterprises, policies, projects):
        return {
            "enterprise_count": len(enterprises),
            "policy_count": len(policies),
            "project_count": len(projects)
        }
