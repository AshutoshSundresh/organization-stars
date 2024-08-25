# GitHub Organization Stars Counter

Welcome to the GitHub Org Star Counter, a tool that helps you show off the total star count for any GitHub organization. 

## What's This All About? 

This FastAPI-powered app generates a badge displaying the total star count across all repositories for any GitHub organization. It's perfect for READMEs, websites, or anywhere else you want to show this stat off.

## Features 

- Fetches star counts for all repos in a GitHub org
- Generates a SVG badge with the total star count, using Google's PyBadges so that it looks uniform with all your other badges
- Fast responses thanks to caching with TTLCache (we remember your star count for an hour)
- Includes a JSON API 

## How to Use It 

Just use this URL format:

` https://your-deployed-app-url/?org=YOUR_GITHUB_ORG_NAME `

For example, if your app is deployed at `https://organization-stars.vercel.app` and you want to show stars for the "ShapeShiftOS" organization, you'd use:

` https://organization-stars.vercel.app/?org=ShapeShiftOS `

Stick that in an image tag, and you've got yourself a shiny star count badge! Here's an example use case:

   <br>
    <img height="22.5em" src="https://organization-stars.vercel.app/?org=ShapeShiftOS" />
   </br>

## API

If you're more into raw data, hit up the `/api/stars` endpoint:

` https://your-deployed-app-url/api/stars?org=YOUR_GITHUB_ORG_NAME`

## Deploy Your Own 
Note: You can use this project as is with the organization-stars.vercel.app domain. Be warned that you may run into rate limits as I'm using the public GitHub API with no authentication.

1. Clone this repo
2. Make sure you have Python 3.7+ installed
3. Install the requirements: `pip install -r requirements.txt`
4. Run it locally: `uvicorn main:app --reload`
5. Deploy to your favorite platform (Vercel recommended)

