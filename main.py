from flask import Flask, request, make_response
from github import Github
import svgwrite
import requests

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
        
    # Determine whether to use plural or singular "star"
    star_label = "stars" if total_stars != 1 else "star"

    # Create the SVG drawing
    dwg = svgwrite.Drawing(size=(120, 20))

    # Draw the badge background
    dwg.add(dwg.rect((0, 0), (len(star_label) * 7 + 5, 20), rx=5, ry=5, fill='#4c1'))

    # Draw the "Star(s)" label background
    dwg.add(dwg.rect((0, 0), (len(star_label) * 7 + 5, 20), rx=5, ry=5, fill='#999'))

    # Draw the "Star(s)" label
    dwg.add(dwg.text(star_label, insert=(6, 14), font_family="Helvetica", font_size="11px", font_weight="bold", fill="#fff", text_anchor="start"))

    # Draw the star count background
    dwg.add(dwg.rect((len(star_label) * 7 + 5, 0), (len(str(total_stars)) * 7 + 5, 20), rx=5, ry=5, fill='#4c1'))

    # Draw the star count
    dwg.add(dwg.text(str(total_stars), insert=(44, 14), font_family="Helvetica", font_size="11px", font_weight="bold", fill="#fff", text_anchor="start"))

    # Save the SVG drawing to a string
    svg_str = dwg.tostring()

    # Create an HTTP response with the SVG content type
    response = make_response(svg_str)
    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Content-Disposition"] = "inline"

    return response

if __name__ == "__main__":
    app.run(debug=True)
