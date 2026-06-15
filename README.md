\# WorldCupAI



WorldCupAI is a football match prediction API built with FastAPI.



The project predicts match outcomes using team data, multi-agent analysis, Monte Carlo simulation, odds value detection, Kelly staking, risk control, stadium data, and weather impact modeling.



\## Features



\* Team database prediction

\* Multi-agent match analysis



&#x20; \* Odds Agent

&#x20; \* Lineup Agent

&#x20; \* Injury Agent

&#x20; \* Tactics Agent

&#x20; \* Weather Agent

\* Stadium database for 2026 World Cup venues

\* Manual and automatic weather mode

\* Weather API integration using Open-Meteo

\* Expected goals adjustment

\* Monte Carlo score simulation

\* Top 3 likely scores

\* Home / Draw / Away probability

\* BTTS and Over 2.5 markets

\* Implied probability and edge calculation

\* Three-way Kelly staking

\* Risk control cap

\* Summary and report generation



\## Project Structure



```text

WorldCupAI/

│

├── main.py

├── schemas.py

├── simulation.py

├── kelly.py

├── risk.py

├── market.py

├── report.py

├── weather\_service.py

├── stadium\_loader.py

├── data\_loader.py

├── requirements.txt

│

├── agents/

│   ├── odds\_agent.py

│   ├── lineup\_agent.py

│   ├── injury\_agent.py

│   ├── tactics\_agent.py

│   ├── ensemble\_agent.py

│   ├── team\_agent.py

│   └── weather\_agent.py

│

└── data/

&#x20;   ├── teams.json

&#x20;   └── stadiums.json

```



\## How to Run



Activate the virtual environment:



```powershell

.\\venv\\Scripts\\activate

```



Install dependencies:



```powershell

pip install -r requirements.txt

```



Start the API server:



```powershell

uvicorn main:app --reload

```



Open Swagger:



```text

http://127.0.0.1:8000/docs

```



\## Example Request



Endpoint:



```text

POST /predict\_team

```



Example JSON:



```json

{

&#x20; "home\_team": "Argentina",

&#x20; "away\_team": "Japan",



&#x20; "stadium\_key": "Mexico City",

&#x20; "weather\_mode": "auto",



&#x20; "open\_home\_odds": 1.9,

&#x20; "current\_home\_odds": 1.75,



&#x20; "open\_draw\_odds": 3.6,

&#x20; "current\_draw\_odds": 3.8,



&#x20; "open\_away\_odds": 4.8,

&#x20; "current\_away\_odds": 5.2,



&#x20; "missing\_starters": 2,

&#x20; "star\_player\_out": 1,

&#x20; "injury\_level": 2,



&#x20; "bankroll": 10000,



&#x20; "max\_bet\_percent": 3,

&#x20; "high\_risk\_bet\_percent": 1,



&#x20; "temperature": 22,

&#x20; "humidity": 50,

&#x20; "wind\_speed": 10,

&#x20; "rain": 0,

&#x20; "altitude": 0

}

```



\## Important Note



This project is for football prediction research and software development practice.



The model output is not a guarantee of profit. Sports betting involves risk. Any staking suggestion should be treated as a simulated model signal, not financial advice.



## Local Demo

Activate the virtual environment:

```powershell
.\venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the backend:

```powershell
uvicorn main:app --reload
```

Start the frontend static server in another terminal:

```powershell
python -m http.server 5173 -d frontend
```

Open the frontend:

```text
http://127.0.0.1:5173
```

Check the backend health endpoint:

```text
http://127.0.0.1:8000/health
```

### Common Issues

1. If the page says the backend is not connected, confirm that `uvicorn main:app --reload` is running and that `http://127.0.0.1:8000/health` returns `status: ok`.

2. To change the frontend Backend API URL, edit the `Backend API URL` field at the top of the page and click the save button.

3. If the API URL is wrong, change it back to `http://127.0.0.1:8000` and save again. The page will reload health, teams, and stadiums from the corrected backend.


## GitHub Pages Frontend Deployment

The static frontend can be published from the `docs/` folder.

If `frontend/index.html` changes later, copy it again to `docs/index.html` before publishing.

GitHub Pages uses HTTPS, so the frontend Backend API URL must also use HTTPS.

### GitHub Pages Settings

1. Open the GitHub repository.
2. Go to `Settings`.
3. Go to `Pages`.
4. Set `Source` to `Deploy from a branch`.
5. Set `Branch` to `main`.
6. Set `Folder` to `/docs`.
7. Save.
8. Wait for GitHub Pages to publish.

Open:

```text
https://simonli2669574-li.github.io/WorldCupAI/
```

In the frontend `Backend API URL` field, enter:

```text
https://worldcupai-api.onrender.com
```

Click save.


## Online Demo

Frontend Demo URL:

```text
https://simonli2669574-li.github.io/WorldCupAI/
```

Backend API URL:

```text
https://worldcupai-api.onrender.com
```

Health Check:

```text
https://worldcupai-api.onrender.com/health
```

Usage:

打开前端 Demo 后，在 Backend API URL 输入 Render 后端地址，然后点击保存。

Render Free 实例可能冷启动，第一次请求可能需要 30-60 秒。

免责声明：

本工具仅用于足球数据分析和模型演示，不构成投注或投资建议。预测结果不保证准确，请理性判断并遵守当地法律法规。


