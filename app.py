from flask import Flask, render_template, jsonify
import json
import pandas as pd

app = Flask(__name__)

#  JSON dosyalarını okuma
with open('users.json', 'r', encoding='utf-8') as f:
    users_data = json.load(f)["users"]

with open('simulations.json', 'r', encoding='utf-8') as f:
    simulations_data = json.load(f)["simulations"]

# User verilerinden pandas yardımıyla dataFrame
users_df = pd.DataFrame(users_data)

# DataFramelerin birleştirilmesi
simulations_df = pd.DataFrame(simulations_data)
merged_df = pd.merge(users_df, simulations_df, on='simulation_id')

# Şirketlerin gruplandırılması SQL
company_user_counts = merged_df.groupby('company_name').size().reset_index(name='user_count')

# Toplam günlük kullanıc sayısını hesaplama
users_df['signup_datetime'] = pd.to_datetime(users_df['signup_datetime'], unit='D', origin='1899-12-30')
daily_user_growth = users_df.resample('D', on='signup_datetime').size().cumsum().reset_index(name='total_users')
daily_user_growth['signup_datetime'] = daily_user_growth['signup_datetime'].dt.strftime('%Y-%m-%d')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/company_user_counts')
def get_company_user_counts():
    return jsonify(company_user_counts.to_dict(orient='records'))

@app.route('/api/daily_user_growth')
def get_daily_user_growth():
    return jsonify(daily_user_growth.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
