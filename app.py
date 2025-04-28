from flask import Flask, render_template, request, jsonify, send_file
from flask_bootstrap import Bootstrap
import os
from main import CPKAnalyzer
import base64
from io import BytesIO
import matplotlib.pyplot as plt

app = Flask(__name__)
Bootstrap(app)

# 确保结果目录存在
if not os.path.exists('results'):
    os.makedirs('results')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        lsl = float(data.get('lsl', 94))
        usl = float(data.get('usl', 106))
        
        # 初始化分析器
        analyzer = CPKAnalyzer()
        analyzer.load_data()
        
        # 计算CPK
        results = analyzer.calculate_cpk(lsl=lsl, usl=usl)
        
        # 生成图表
        plt.figure(figsize=(10, 6))
        plt.hist(analyzer.data['measurement'], bins=50, density=True)
        plt.title(f'数据分布 (CPK = {results["cpk"]:.3f})')
        plt.xlabel('测量值')
        plt.ylabel('频率')
        
        # 添加正态分布曲线
        x = analyzer.data['measurement']
        x_line = plt.linspace(min(x), max(x), 100)
        plt.plot(x_line, 
                1/(results['std'] * (2*3.14159)**0.5) * 
                plt.exp(-(x_line - results['mean'])**2 / (2*results['std']**2)),
                'r-', lw=2)
        
        # 将图表转换为base64字符串
        img_buf = BytesIO()
        plt.savefig(img_buf, format='png')
        plt.close()
        img_buf.seek(0)
        img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'results': {
                'cpk': f"{results['cpk']:.3f}",
                'mean': f"{results['mean']:.3f}",
                'std': f"{results['std']:.3f}",
                'cpu': f"{results['cpu']:.3f}",
                'cpl': f"{results['cpl']:.3f}",
            },
            'plot': img_base64
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 