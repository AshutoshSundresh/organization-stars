from flask import Flask, request, make_response
import svgwrite
import requests

app = Flask(__name__)

def get_total_stars(org_name):
    api_url = f"https://api.github.com/orgs/{org_name}/repos?type=all"
    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        repos = response.json()
        total_stars = sum(repo["stargazers_count"] for repo in repos)
        return total_stars
    else:
        raise ValueError(f"Failed to get repositories for {org_name}: {response.text}")

@app.route("/")
def generate_svg():
    org_name = request.args.get("org")
    if not org_name:
        return "Error: Missing org parameter"

    # Get the total number of stars for the given organization
    total_stars = get_total_stars(org_name)

    # Determine whether to use plural or singular "star"
    star_label = "stars" if total_stars != 1 else "star"

    # Create an SVG drawing with a small rectangular box and a star icon
    dwg = svgwrite.Drawing(size=(140, 50))
    dwg.add(dwg.rect((0, 0), (140, 50), rx=5, ry=5, fill='#fff', stroke_width=1, stroke='#000'))
    dwg.add(dwg.text(f"{total_stars} {star_label}", insert=(10, 30), font_size="20px", font_family="Roboto", fill='#000'))
    dwg.add(dwg.polyline([(110, 20), (120, 30), (110, 40), (100, 30)], fill='#ffea00', stroke_width=1, stroke='#000'))

    # Save the SVG drawing to a string
    svg_str = dwg.tostring()

    # Create an HTTP response with the SVG content type
    response = make_response(svg_str)
    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Content-Disposition"] = "inline"

    return response

if __name__ == "__main__":
    app.run(debug=True)
