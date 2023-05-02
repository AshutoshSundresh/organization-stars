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

    dwg = svgwrite.Drawing(size=(180, 80))
    dwg.add(dwg.rect((0, 0), (180, 80), rx=10, ry=10, fill='#001eff', stroke='none'))
    dwg.add(dwg.text(f"{total_stars} {star_label}", insert=(40, 50), font_family="Helvetica", font_size="30px", fill='#00ff9f'))
    dwg.add(dwg.path('M14.738 17.251c-.2 1.156.916 2.058 1.875 1.564l11.17-5.729 11.169 5.729c.96.493 2.04-.37 1.846-1.563l-2.047-11.695 8.651-8.252c.817-.776.393-2.77-.704-2.971l-12.013-1.706-5.034-10.063a1.01 1.01 0 0 0-1.815 0L17.305 3.06 5.292 4.766c-.907.202-1.524 1.196-1.305 2.166l2.745 15.617-11.662-6.001c-1.015-.524-2.274.389-2.062 1.655l2.752 15.688 13.317-6.85c.846-.438 1.224-1.74.577-2.478z', transform='scale(3) translate(-20,-12)', fill='#00ff9f', stroke='none'))

    # Save the SVG drawing to a string
    svg_str = dwg.tostring()

    # Create an HTTP response with the SVG content type
    response = make_response(svg_str)
    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Content-Disposition"] = "inline"

    return response

if __name__ == "__main__":
    app.run(debug=True)
