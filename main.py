from flask import Flask, request, make_response
from github import Github
import svgwrite
import requests
import pybadges

app = Flask(__name__)

def get_total_stars(org_name):
    # Create a GitHub instance
    g = Github()

    # Get the organization from the link
    org = g.get_organization(org_name)

    # Initialize the total number of stars to zero
    total_stars = 0

    # Loop through all repositories in the organization
    for repo in org.get_repos():
        # Add the number of stars for the repository to the total number of stars
        total_stars += repo.stargazers_count
    return total_stars
        
@app.route("/")
def generate_svg():
    org_name = request.args.get("org")
    if not org_name:
        return svgwrite.Drawing(size=(0, 0)).tostring()
    
    # Get the total number of stars for the given organization
    try:
        total_stars = get_total_stars(org_name)
    except ValueError as e:
        return svgwrite.Drawing(size=(0, 0)).tostring()
        
    badge = pybadges.badge(left_text='stars', right_text=str(total_stars), right_color='green')

    # Create an HTTP response with the SVG content type
    response = make_response(badge)
    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Content-Disposition"] = "inline"

    return response

if __name__ == "__main__":
    app.run(debug=True)
