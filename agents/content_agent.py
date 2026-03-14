
class ContentAgent:

    def generate_scripts(self, summary, analysis):

        scripts = []

        scripts.append(
            f"今天海南新增企业{summary['enterprise_count']}家，其中{analysis.get('top_industry','未知')}行业最多。"
        )

        scripts.append(
            f"今日发布政策{summary['policy_count']}条，建议关注政策红利带来的商业机会。"
        )

        scripts.append(
            f"今日新增招商项目{summary['project_count']}个，可能带来新的投资机会。"
        )

        return scripts
