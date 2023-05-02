# GitHub Organization Stars SVG
- This project is a simple Flask web application that generates an SVG image showing the total number of stars for a given GitHub organization. It uses the GitHub API to fetch the total number of stars for each repository in the organization, and then generates an SVG image with a "pill-shaped" background that displays the total number of stars.
- The SVG image is generated dynamically in response to HTTP requests made to the Flask web server. The user can specify the name of the GitHub organization for which they want to see the total number of stars by passing it as a query parameter in the URL.
- This project can be useful for individuals or organizations who want to keep track of the popularity of their GitHub repositories or those of others.
## Dependencies
- Flask
- github
- svgwrite
- requests
## Setup
- Install dependencies by running pip install -r requirements.txt.
## Usage
- Run the application by running python app.py or deploy it on Vercel.
- Access the application at http://localhost:5000/ with a query parameter org specifying the name of the organization whose stars you want to see, e.g. http://localhost:5000/?org=ShapeShiftOS.

## Example use case
   <br>
    <img height="60em" src="https://organization-stars.vercel.app/?org=ShapeShiftOS" />
   </br>
