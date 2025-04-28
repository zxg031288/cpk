import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from dotenv import load_dotenv

class CPKAnalyzer:
    def __init__(self):
        self.data = None
        self.results = {}
        
    def load_data(self, file_path=None):
        """加载数据，如果没有文件，创建示例数据"""
        if file_path and os.path.exists(file_path):
            self.data = pd.read_csv(file_path)
        else:
            # 创建示例数据
            np.random.seed(42)
            measurements = np.random.normal(100, 2, 1000)
            self.data = pd.DataFrame({
                'measurement': measurements,
                'timestamp': pd.date_range(start='2024-01-01', periods=1000, freq='H')
            })
    
    def calculate_cpk(self, lsl, usl, target=None):
        """计算CPK值"""
        data = self.data['measurement'].values
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        
        if target is None:
            target = (usl + lsl) / 2
            
        cpu = (usl - mean) / (3 * std)
        cpl = (mean - lsl) / (3 * std)
        cpk = min(cpu, cpl)
        
        self.results = {
            'cpk': cpk,
            'mean': mean,
            'std': std,
            'cpu': cpu,
            'cpl': cpl
        }
        return self.results
    
    def plot_results(self, output_dir='results'):
        """生成分析图表"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 创建直方图
        plt.figure(figsize=(10, 6))
        plt.hist(self.data['measurement'], bins=50, density=True)
        plt.title(f'数据分布 (CPK = {self.results["cpk"]:.3f})')
        plt.xlabel('测量值')
        plt.ylabel('频率')
        
        # 添加正态分布曲线
        x = np.linspace(
            min(self.data['measurement']), 
            max(self.data['measurement']), 
            100
        )
        plt.plot(x, 
                 1/(self.results['std'] * np.sqrt(2*np.pi)) * 
                 np.exp(-(x - self.results['mean'])**2 / (2*self.results['std']**2)),
                 'r-', lw=2)
        
        plt.savefig(os.path.join(output_dir, 'distribution.png'))
        plt.close()
        
        # 保存结果
        results_df = pd.DataFrame([self.results])
        results_df['timestamp'] = datetime.now()
        results_df.to_csv(os.path.join(output_dir, 'cpk_results.csv'), 
                         index=False, mode='a', header=not os.path.exists(os.path.join(output_dir, 'cpk_results.csv')))

def main():
    # 初始化分析器
    analyzer = CPKAnalyzer()
    
    # 加载数据
    analyzer.load_data()
    
    # 计算CPK（示例规格限）
    results = analyzer.calculate_cpk(lsl=94, usl=106)
    
    # 生成图表和保存结果
    analyzer.plot_results()
    
    print(f"分析完成！CPK值: {results['cpk']:.3f}")

if __name__ == "__main__":
    main() 