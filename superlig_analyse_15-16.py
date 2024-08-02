import json
import pandas as pd
import matplotlib.pyplot as plt

# JSON dosyasını açma
file_path = r'C:\Users\Asus\Desktop\spyder\superlig_15-16.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# İşlenmiş maç verilerini saklamak için bir liste oluştur
processed_matches = []

for week_data in data:
    week = week_data['week']
    for match in week_data['matches']:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        score = match['match']['score']
        home_score, away_score = map(int, score.split(' - '))
        
        processed_matches.append({
            'week': week,
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score
        })

# Verileri bir DataFrame'e dönüştür
df = pd.DataFrame(processed_matches)

# Ev sahibi takımların attığı goller
home_goals = df.groupby('home_team')['home_score'].sum().reset_index()
home_goals.columns = ['team', 'home_goals']

print("home_goals :",home_goals)

# Misafir takımların attığı goller
away_goals = df.groupby('away_team')['away_score'].sum().reset_index()
away_goals.columns = ['team', 'away_goals']

print("away_goals :",away_goals)


# Toplam goller
total_goals = pd.merge(home_goals, away_goals, on='team')
total_goals['total_goals'] = total_goals['home_goals'] + total_goals['away_goals']
total_goals = total_goals.sort_values(by='total_goals', ascending=False)

print("total_goals :", total_goals)


# Ev sahibi takımların yediği goller
home_conceded = df.groupby('home_team')['away_score'].sum().reset_index()
home_conceded.columns = ['team', 'home_conceded']


print("home_conceded:",home_conceded)


# Misafir takımların yediği goller
away_conceded = df.groupby('away_team')['home_score'].sum().reset_index()
away_conceded.columns = ['team', 'away_conceded']


print("away_conceded :",away_conceded)

# Toplam yenen goller
total_conceded = pd.merge(home_conceded, away_conceded, on='team')
total_conceded['total_conceded'] = total_conceded['home_conceded'] + total_conceded['away_conceded']
total_conceded = total_conceded.sort_values(by='total_conceded', ascending=False)

print("total_conceded :",total_conceded)

# Takım bazlı performansları hesaplama
teams = set(df['home_team']).union(set(df['away_team']))
print("teams :", teams)

performance = []

for team in teams:
    home_wins = len(df[(df['home_team'] == team) & (df['home_score'] > df['away_score'])])
    home_draws = len(df[(df['home_team'] == team) & (df['home_score'] == df['away_score'])])
    home_losses = len(df[(df['home_team'] == team) & (df['home_score'] < df['away_score'])])
    
    away_wins = len(df[(df['away_team'] == team) & (df['away_score'] > df['home_score'])])
    away_draws = len(df[(df['away_team'] == team) & (df['away_score'] == df['home_score'])])
    away_losses = len(df[(df['away_team'] == team) & (df['away_score'] < df['home_score'])])
    
    total_wins = home_wins + away_wins
    total_draws = home_draws + away_draws
    total_losses = home_losses + away_losses
    
    performance.append({
        'team': team,
        'home_wins': home_wins,
        'home_draws': home_draws,
        'home_losses': home_losses,
        'away_wins': away_wins,
        'away_draws': away_draws,
        'away_losses': away_losses,
        'total_wins': total_wins,
        'total_draws': total_draws,
        'total_losses': total_losses
    })

performance_df = pd.DataFrame(performance)
print("performance_df :",performance_df)

# Haftalık maç sonuçları ve toplam skorlar
weekly_results = df.groupby('week').agg({
    'home_score': 'sum',
    'away_score': 'sum'
}).reset_index()

weekly_results['total_goals'] = weekly_results['home_score'] + weekly_results['away_score']
print("weekly_results .",weekly_results)


# Her takımın genel performansını ve gol istatistiklerini birleştir
team_stats = pd.merge(total_goals, total_conceded, on='team')
team_stats = pd.merge(team_stats, performance_df, on='team')
print("team_stats :",team_stats)

# Maç başına ortalama gol sayısı
average_goals_per_match = df[['home_score', 'away_score']].mean().sum()
print("average_goals_per_match:",average_goals_per_match)



# Tüm takımların isimlerini bir liste içinde topluyoruz
teams = set()
for week in data:
    for match in week['matches']:
        teams.add(match['homeTeam']['name'])
        teams.add(match['awayTeam']['name'])

teams = list(teams)  # Set'i listeye dönüştürüyoruz

# Tüm haftaları ve takımları içeren boş bir DataFrame oluşturuyoruz
rankings = pd.DataFrame(index=teams, columns=[week['week'] for week in data])

# Başlangıç puanları
points = {team: 0 for team in teams}

# Puanları hesaplama
for week in data:
    for match in week['matches']:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        home_score, away_score = map(int, match['match']['score'].split(' - '))
        
        if home_score > away_score:
            points[home_team] += 3
        elif home_score < away_score:
            points[away_team] += 3
        else:
            points[home_team] += 1
            points[away_team] += 1
        
    # Haftalık sıralamaları hesaplayıp DataFrame'e ekleme
    sorted_teams = sorted(points.items(), key=lambda x: x[1], reverse=True)
    for rank, (team, point) in enumerate(sorted_teams, start=1):
        rankings.at[team, week['week']] = rank

# Eksik değerleri 0 ile doldur
rankings = rankings.fillna(0).astype(int)

# Grafik çizimi
plt.figure(figsize=(14, 10))
for team in teams:
    plt.plot(rankings.columns, rankings.loc[team], marker='o', label=team)
    
plt.gca().invert_yaxis()
plt.xticks(rotation=90)
plt.xlabel('Haftalar')
plt.ylabel('Sıralama')
plt.title('Her Hafta Takımların Sıralamaları')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()





