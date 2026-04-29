module.exports = {
  apps: [{
    name: 'fitness-tracker',
    script: '/Users/christopherbrown/4m/02-projects/fourm-fitness/fourm-fitness-tracker/venv/bin/streamlit',
    interpreter: 'none',
    args: 'run app.py --server.port 5012 --server.address 0.0.0.0 --server.headless true',
    cwd: '/Users/christopherbrown/4m/02-projects/fourm-fitness/fourm-fitness-tracker',
    restart_delay: 5000,
    max_restarts: 10,
    env: {
    "PORT": "5012"
}
  }]
}
