"""
数据源管理系统
支持从多个可靠来源获取数据：
1. 真实网站爬虫（优先）
2. 本地JSON文件（可靠备选）
3. 数据库历史记录（未来）
4. 空列表（当所有来源都失败时）
"""

import json
import os
from typing import List, Dict, Optional

class DataSourceManager:
    """管理多个数据源的统一接口"""
    
    def __init__(self, config_path: str = "crawler_config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.data_dir = "data"
    
    def _load_config(self) -> dict:
        """加载爬虫配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_enterprises(self, source: str = "auto", verbose: bool = True) -> List[Dict]:
        """获取企业数据
        
        Args:
            source: 数据源 ("auto", "web", "file", "database", "empty")
            verbose: 是否打印信息
        
        Returns:
            企业数据列表
        """
        return self._get_data(
            data_type="enterprises",
            source=source,
            verbose=verbose
        )
    
    def get_policies(self, source: str = "auto", verbose: bool = True) -> List[Dict]:
        """获取政策数据"""
        return self._get_data(
            data_type="policies",
            source=source,
            verbose=verbose
        )
    
    def get_projects(self, source: str = "auto", verbose: bool = True) -> List[Dict]:
        """获取项目数据"""
        return self._get_data(
            data_type="projects",
            source=source,
            verbose=verbose
        )
    
    def _get_data(self, data_type: str, source: str = "auto", verbose: bool = True) -> List[Dict]:
        """从指定来源获取数据"""
        
        if source == "auto":
            # 自动尝试按优先级获取
            sources_to_try = ["web", "file"]
        elif source == "empty":
            return []
        else:
            sources_to_try = [source]
        
        for src in sources_to_try:
            if src == "web":
                if verbose:
                    print(f"[{data_type}] 尝试从网站爬虫获取数据...")
                data = self._get_from_web(data_type, verbose)
                if data:
                    if verbose:
                        print(f"[{data_type}] ✓ 从网站成功获取 {len(data)} 条数据")
                    return data
            
            elif src == "file":
                if verbose:
                    print(f"[{data_type}] 尝试从本地文件获取数据...")
                data = self._get_from_file(data_type, verbose)
                if data:
                    if verbose:
                        print(f"[{data_type}] ✓ 从文件成功获取 {len(data)} 条数据")
                    return data
            
            elif src == "database":
                if verbose:
                    print(f"[{data_type}] 尝试从数据库获取历史记录...")
                data = self._get_from_database(data_type, verbose)
                if data:
                    if verbose:
                        print(f"[{data_type}] ✓ 从数据库成功获取 {len(data)} 条历史记录")
                    return data
        
        # 所有源都失败
        if verbose:
            print(f"[{data_type}] ✗ 所有数据源都不可用，返回空列表")
        return []
    
    def _get_from_web(self, data_type: str, verbose: bool = True) -> Optional[List[Dict]]:
        """从网站爬虫获取数据"""
        try:
            if data_type == "enterprises":
                from crawlers.enterprise import crawl_enterprises
                return crawl_enterprises()
            elif data_type == "policies":
                from crawlers.policy import crawl_policies
                return crawl_policies()
            elif data_type == "projects":
                from crawlers.projects import crawl_projects
                return crawl_projects()
        except Exception as e:
            if verbose:
                print(f"[{data_type}] ✗ 网站爬虫失败：{e}")
            return None
    
    def _get_from_file(self, data_type: str, verbose: bool = True) -> Optional[List[Dict]]:
        """从本地JSON文件获取数据"""
        try:
            file_mapping = {
                "enterprises": "data/enterprises.json",
                "policies": "data/policies.json",
                "projects": "data/projects.json"
            }
            
            file_path = file_mapping.get(data_type)
            if not file_path or not os.path.exists(file_path):
                if verbose:
                    print(f"[{data_type}] ✗ 本地文件不存在：{file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 标记数据来源
                for item in data:
                    if "data_source" not in item:
                        item["data_source"] = "本地JSON文件"
                return data
        
        except Exception as e:
            if verbose:
                print(f"[{data_type}] ✗ 读取文件失败：{e}")
            return None
    
    def _get_from_database(self, data_type: str, verbose: bool = True) -> Optional[List[Dict]]:
        """从数据库获取历史记录"""
        # 暂未实现
        return None
    
    def list_available_sources(self) -> Dict[str, List[str]]:
        """列出所有可用的数据源"""
        available = {}
        
        # 检查网站爬虫
        web_available = ['enterprises', 'policies', 'projects']
        available['web'] = web_available
        
        # 检查本地文件
        file_available = []
        for dtype in ['enterprises', 'policies', 'projects']:
            file_path = f"data/{dtype}.json"
            if os.path.exists(file_path):
                file_available.append(dtype)
        available['file'] = file_available
        
        return available
    
    def print_data_summary(self, data_type: str, data: List[Dict]):
        """打印数据摘要"""
        if not data:
            print(f"\n{data_type}: 无数据")
            return
        
        print(f"\n{data_type} 摘要 (共 {len(data)} 条):")
        for i, item in enumerate(data[:3], 1):
            if data_type == "enterprises":
                print(f"  {i}. {item.get('name')} ({item.get('industry')}) - {item.get('region')}")
            elif data_type == "policies":
                print(f"  {i}. {item.get('title')} - {item.get('issuing_department')}")
            elif data_type == "projects":
                print(f"  {i}. {item.get('name')} ({item.get('investment')}万元)")


# 全局实例
_manager = None

def get_manager() -> DataSourceManager:
    """获取全局数据源管理器实例"""
    global _manager
    if _manager is None:
        _manager = DataSourceManager()
    return _manager


if __name__ == "__main__":
    # 使用示例
    manager = get_manager()
    
    print("=" * 100)
    print("数据源管理系统示例")
    print("=" * 100)
    
    # 查看可用数据源
    print("\n可用的数据源：")
    available = manager.list_available_sources()
    for source, dtypes in available.items():
        print(f"  {source}: {dtypes}")
    
    # 自动获取数据
    print("\n【自动模式】按优先级尝试获取数据...")
    enterprises = manager.get_enterprises(verbose=True)
    policies = manager.get_policies(verbose=True)
    projects = manager.get_projects(verbose=True)
    
    # 打印摘要
    manager.print_data_summary("enterprises", enterprises)
    manager.print_data_summary("policies", policies)
    manager.print_data_summary("projects", projects)
    
    # 指定来源
    print("\n【文件模式】从本地JSON文件获取数据...")
    file_enterprises = manager.get_enterprises(source="file", verbose=True)
    print(f"企业数据：{len(file_enterprises)} 条")
    
    print("\n=" * 100)
