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
    dwg = svgwrite.Drawing(size=(240, 200))

    # Draw the pill-shaped background
    # Create a gradient that goes from dark gray to light gray
    gradient = dwg.linearGradient((0, 0), (0, 1))
    gradient.add_stop_color(offset='0%', color='#ffce00', opacity='1').add_stop_color(offset='50%', color='#ffce00', opacity='1').add_stop_color(offset='50%', color='#282828', opacity='1').add_stop_color(offset='100%', color='#282828', opacity='1')
    dwg.defs.add(gradient)

    # Create the rectangle
    rect = dwg.rect((0, 0), (240, 200), rx=10, ry=10)
    rect.fill(gradient.get_paint_server())
    dwg.add(rect)

    # Draw the "Star(s)" label
    star_label_bg = dwg.rect((15, 15), (110, 80), rx=10, ry=10, fill='#ffce00', stroke='none')
    dwg.add(star_label_bg)
    dwg.add(dwg.text("Star" + ("s" if total_stars != 1 else ""), insert=(10, 70), font_family="Helvetica", font_size="50px", fill='#282828'))

    # Draw the star count
    star_count_bg = dwg.rect((135, 15), (330, 80), rx=10, ry=10, fill='#282828', stroke='none')
    dwg.add(star_count_bg)
    dwg.add(dwg.text(total_stars, insert=(190, 70), font_family="Helvetica", font_size="50px", fill='#ffce00'))

    # Save the SVG drawing to a string
    svg_str = dwg.tostring()

    # Create an HTTP response with the SVG content type
    response = make_response(svg_str)
    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Content-Disposition"] = "inline"

    return response

if __name__ == "__main__":
    app.run(debug=True)
