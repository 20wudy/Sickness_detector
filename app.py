from flask import Flask, render_template, request, redirect, url_for
from main import HealthMonitor
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'models'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    user_id = request.form.get('user_id', 'default_user') if request.method == 'POST' else request.args.get('user_id', 'default_user')
    monitor = HealthMonitor(user_id)

    if request.method == 'POST':
        try:
            avg_hr = float(request.form['avg_hr'])
            min_hr = float(request.form['min_hr'])
            max_hr = float(request.form.get('max_hr'))
            sleep_hours = float(request.form.get('sleep_hours', 9))
            sleep_quality = float(request.form.get('sleep_quality', 80))

            monitor.add_record({
                'avg_hr': avg_hr,
                'min_hr': min_hr,
                'max_hr': max_hr,
                'sleep_hours': sleep_hours,
                'sleep_quality': sleep_quality
            })
        except (ValueError, KeyError) as e:
            return f"Invalid input: {str(e)}", 400

        return redirect(url_for('dashboard', user_id=user_id))

    analysis = monitor.get_analysis()
    return render_template('dashboard.html', analysis=analysis)

if __name__ == '__main__':
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    app.run(debug=True)


