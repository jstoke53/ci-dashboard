from flask import Flask, request, redirect, render_template, url_for, Response, session
import argparse, json, requests, os, uuid
from datetime import timedelta
from lib.tools import Tools
from lib.dashboard import Dashboard
from lib.repositories import Repositories
from lib.clients.travis import Travis

app = Flask(__name__)
app.secret_key = uuid.uuid4().hex
tools = Tools()

@app.context_processor
def context_processor():
    config = tools.read_config(protected=True)
    return dict(config=config)

@app.route("/")
@app.route("/master")
def master():
    return render_template("dashboard.html", branch = "master")
    
@app.route("/next")
def next():
    return render_template("dashboard.html", branch = "next")

@app.route("/dashboard", methods=["POST"])
def build_actions():
    slug = request.form.get('repo')
    if 'trigger-build' in request.form:
        branch = request.form.get('branch')
        env_vars = {}
        for key, value in request.form.items():
            if 'env_var@' in key and value != '[hidden-secret-var]':
                key = key.split('@')[-1]
                env_vars[key] = value

        Repositories().repo(slug).trigger_build(branch, env_vars)

    elif 'restart-build' in request.form:
        buildid = request.form.get('buildid')
        Repositories().repo(slug).restart_build(buildid)
    
    elif 'cancel-build' in request.form:
        buildid = request.form.get('buildid')
        Repositories().repo(slug).cancel_build(buildid)

    return redirect(url_for('dashboard'), code=302)


@app.route("/dashboard/fetch")
def fetch_dashboard(): 
    params = request.args.to_dict()
    headers, repos = Dashboard().fetch(** params)
    html = render_template("repos.html", repos=repos)
    return Response(html, headers=headers)

@app.route("/dashboard/modal")
def repo_modal():
    slug = request.args.get('slug')
    repo = Repositories().repo(slug)
    repo = {
        "info": repo.info(),  
        "branches":repo.branches(),
        "last_build": repo.last_build(),
        "env_vars": repo.env_vars()
    }
    html = render_template("modal.html", repo=repo)
    return html

@app.route("/settings", methods=['GET', 'POST'])
def settings():
    success = None
    if request.method == 'POST':    
        if 'configration' in request.form:  
            travis_token = request.form.get('travis_token')
            github_token = request.form.get('github_token')
            threads = int(request.form.get('threads'))
            grid_size = int(request.form.get('grid_size'))
            interval = int(request.form.get('interval'))
            view_mode = request.form.get('view_mode')
            tools.save_config(threads=threads, 
                              grid_size=grid_size, 
                              interval=interval, 
                              travis_token=travis_token, 
                              github_token=github_token,
                              view_mode=view_mode)

        elif 'repositories' in request.form:
            selected_repos = request.form.getlist("repos")
            tools.save_config(repos=selected_repos)

        success = True

    repos = Repositories().list()
    return render_template('settings.html', repos=repos, success=success) 


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default='127.0.0.1', help="the hostname to listen on")
    parser.add_argument("--port", type=int, default=5000, help="the port of the webserver")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=True, threaded=True)