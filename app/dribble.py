from flask import Blueprint, render_template, request, flash, url_for, jsonify,redirect, current_app, send_from_directory
import os

dribble = Blueprint("dribble", __name__,static_folder='dribble.tf/build')


@dribble.route('/', defaults={'path': ''})
def serve(path):
    return send_from_directory(dribble.static_folder, "index.html")


@dribble.route("/<path:path>")
def static_proxy(path):
    """serve static files"""
    file_name = path.split("/")[-1]
    primary_path = path.split("/")[0]
    paths  = path.split("/")
    print(paths)
    #Need to get tricky with static folder structure because flask was not properly handeling files outside of the default static folder
    #There is likely a better solution than this.
    if primary_path in ['js','css','media']:
        dir_name = os.path.join(dribble.static_folder,'../static', "/".join(path.split("/")[1:-1]))
    else:
        dir_name = os.path.join(dribble.static_folder, "/".join(path.split("/")[1:-1]))
    
    
    return send_from_directory(dir_name, file_name)